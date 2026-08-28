#!/usr/bin/env python3
"""Assemble and render https://spec.sempods.org.

MkDocs refuses a `docs_dir` that contains its own configuration, and pointing it at the
repository root would publish the agent instructions along with the specification. So the
site is staged into a directory this script owns and `.gitignore` hides: the normative tree
is copied, never edited, and nothing under `spec/` has to know a website exists.

Run `python3 site/build.py` from anywhere; `--serve` rebuilds and watches instead.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
STAGE = SITE / "_stage"

# The public pod the try-it button talks to. THIS IS THE ONLY PLACE IT IS WRITTEN.
#
# It is deliberately not in the OpenAPI descriptions: those are normative, and a
# specification that names one operator's deployment has confused the contract with an
# instance of it. Their `servers` block stays on `example.org`/`alice`, and the staged copy
# rendered for the try-it page gets these values substituted in.
#
# Switching to a different demo pod is an edit to these two strings.
DEMO_ORIGIN = "https://sempods.org"
DEMO_POD = "aaltra"

# Every address a staged description is allowed to resolve a server to. A closed list rather
# than "anything on the demo origin": `{origin}/wrong` is on the origin too, and Scalar would
# send every request in that description to a base the pod does not serve.
#
# The second entry is the host-rooted well-known base `sempods-core.yaml` declares for protected
# resource metadata, which is not under a pod and cannot be.
#
# A chapter that introduces a genuinely new server shape fails the build until it is added here.
# That is the intent: this list decides where a reader's requests go, including authenticated
# ones, so a new destination should be a decision somebody made rather than one that arrived.
ALLOWED_ADDRESSES = {
    f"{DEMO_ORIGIN}/{DEMO_POD}",
    f"{DEMO_ORIGIN}/.well-known",
}

# Chapters, in reading order. The nav in `mkdocs.yml` repeats this order; a chapter added
# here and forgotten there is caught by `--check`.
SOURCES_MARKER = "/* SOURCES */"

# Where the repository is read when a staged document points at something the site does not
# publish. Only the staged copies get these; the files themselves stay ref-relative, so a
# reader on a tag follows links within that tag rather than being sent to whatever `main`
# holds — which for `requirements.json` would mean reading one revision's requirements
# alongside another revision's chapters.
REPOSITORY = "https://github.com/sempods/sempods-spec"

# The repository paths `stage()` copies. A link that lands inside one of these resolves on the
# site and stays relative; anything else has to leave.
STAGED = ("spec/", "vocabulary/", "GOVERNANCE.md")

RELATIVE_LINK = re.compile(r"\]\((?!https?://|mailto:|#)([^)]+)\)")

CORE = ["index", "contexts", "grants", "auth", "lod-crud", "sparql", "find"]
MODULES = ["oidc", "media", "mcp"]


def with_repository_links(text: str, source: Path) -> str:
    """Point a staged document's off-site links at the repository.

    A chapter may link to the roadmap, the authoring rules or `requirements.json`, and none of
    those is published. Rewritten here rather than written absolutely in the file, because the
    file is also read on GitHub at a tag or a branch, where a hard-coded `main` silently mixes
    one revision's text with another's.

    A link is left alone when it resolves to something `stage()` copies. A directory is not a
    page, so a link to one leaves too.
    """
    def rewrite(match: "re.Match[str]") -> str:
        target = match.group(1)
        path, _, fragment = target.partition("#")
        if not path:
            return match.group(0)
        resolved = (source.parent / path).resolve()
        try:
            relative = resolved.relative_to(ROOT).as_posix()
        except ValueError:
            return match.group(0)
        staged = any(relative == root.rstrip("/") or relative.startswith(root) for root in STAGED)
        if staged and resolved.is_file():
            return match.group(0)
        kind = "tree" if resolved.is_dir() else "blob"
        suffix = f"#{fragment}" if fragment else ""
        return f"]({REPOSITORY}/{kind}/main/{relative}{suffix})"

    return RELATIVE_LINK.sub(rewrite, text)


def configure() -> None:
    """Put the MkDocs configuration in place. Once per invocation, before the server starts.

    Kept apart from `stage()` because that one is called again under a running server, and a
    server whose configuration file is deleted and rewritten beneath it is a server that reloads
    into whatever state the filesystem happened to be in.
    """
    STAGE.mkdir(parents=True, exist_ok=True)
    shutil.copy(SITE / "mkdocs.yml", STAGE / "mkdocs.yml")


def stage() -> None:
    """Copy the sources into the directory MkDocs renders.

    Called again before every rebuild while serving, through `hooks.py`: MkDocs watches the
    directory it renders and that directory is a copy, so without re-staging an edit to a
    chapter changes nothing the server can see and the page keeps showing what was staged when
    it started.
    """
    docs = STAGE / "docs"
    if docs.exists():
        shutil.rmtree(docs)
    docs.mkdir(parents=True)

    shutil.copytree(ROOT / "spec", docs / "spec")
    shutil.copy(ROOT / "GOVERNANCE.md", docs / "GOVERNANCE.md")
    shutil.copytree(ROOT / "vocabulary", docs / "vocabulary")
    shutil.copy(SITE / "index.md", docs / "index.md")

    for staged in sorted(docs.rglob("*.md")):
        source = ROOT / staged.relative_to(docs)
        if source.is_file():
            staged.write_text(with_repository_links(staged.read_text(), source))

    api = docs / "api"
    api.mkdir()
    (api / "index.html").write_text(try_it_page())
    for src in sorted((ROOT / "openapi").glob("*.yaml")):
        (api / src.name).write_text(with_demo_pod(src.read_text()))

    (docs / "CNAME").write_text("spec.sempods.org\n")

    # Asserted on the staged file rather than on what `try_it_page()` returns. `check()` calls
    # that function and would have been satisfied by it while `stage()` copied the template
    # past it untouched — which is exactly what happened once. What ships is what gets checked.
    staged_page = (api / "index.html").read_text()
    if SOURCES_MARKER in staged_page:
        raise SystemExit(f"error: the staged try-it page still holds {SOURCES_MARKER!r}; its "
                         f"source list was never generated")
    for name, _ in descriptions():
        if f"url: '{name}'" not in staged_page:
            raise SystemExit(f"error: the staged try-it page does not offer {name!r}")


# The placeholders a normative description carries, and what the staged copy says instead.
# Matched on the `default:` key rather than on the value alone: `example.org` also appears in a
# `WWW-Authenticate` example in the MCP module, where it is illustrating a header and must stay.
# Quotes are optional on both sides because the four descriptions are hand-written and do not
# spell their scalars the same way — which is exactly how the first version of this missed
# `sempods-core.yaml`'s document-level server and pointed the core try-it at example.org.
ORIGIN_DEFAULT = re.compile(r"""(default:\s*)['"]?https://example\.org['"]?""")
POD_DEFAULT = re.compile(r"""(default:\s*)['"]?alice['"]?(?![\w-])""")


def with_demo_pod(yaml: str) -> str:
    """Point a staged description's server variables at the demo pod.

    Regex on the `default:` key rather than a YAML round-trip: parsing and re-emitting would
    reformat a hand-written file whose layout and comments are part of how it reads.
    """
    yaml = ORIGIN_DEFAULT.sub(lambda m: m.group(1) + f"'{DEMO_ORIGIN}'", yaml)
    yaml = POD_DEFAULT.sub(lambda m: m.group(1) + DEMO_POD, yaml)
    return yaml


def load(staged: str) -> object:
    try:
        import yaml
    except ImportError:  # pragma: no cover - the workflow installs it with the renderer
        raise SystemExit(
            "error: PyYAML is needed to read the staged descriptions.\n"
            "       pip install -r site/requirements.txt")
    return yaml.safe_load(staged)


def server_addresses(staged: str) -> list[tuple[str, str, dict]]:
    """Every server in a description as (template, resolved address, its variables).

    Walked recursively rather than read from `doc["servers"]`: a description may declare
    servers at the document, path or operation level, and `sempods-core.yaml` does — a pod base
    at the top and a `{origin}/.well-known` further down.

    Resolved, not just collected. Checking that the *defaults* are the demo values says nothing
    about what they are composed into: `{pod}/{origin}` and a literal `https://example.org/{pod}`
    both leave the defaults untouched and send the reader somewhere else. The address is what
    Scalar dials, so the address is what gets asserted.
    """
    found: list[tuple[str, str, dict]] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            servers = node.get("servers")
            if isinstance(servers, list):
                for server in servers:
                    if not isinstance(server, dict):
                        continue
                    template = str(server.get("url", ""))
                    variables = {
                        name: variable.get("default")
                        for name, variable in (server.get("variables") or {}).items()
                        if isinstance(variable, dict)
                    }
                    resolved = template
                    for name, value in variables.items():
                        resolved = resolved.replace("{" + name + "}", str(value))
                    found.append((template, resolved, variables))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(load(staged))
    return found


def descriptions() -> list[tuple[str, str]]:
    """The OpenAPI files as (filename, the title they give themselves), core first.

    Read from disk rather than listed anywhere, so the try-it page cannot name a description
    that was renamed away or miss one that was added — `stage()` copies whatever is in
    `openapi/`, and a hand-kept list beside it drifts silently into a 404.
    """
    found = []
    for path in sorted((ROOT / "openapi").glob("*.yaml")):
        document = load(path.read_text()) or {}
        title = ((document.get("info") or {}).get("title") or path.stem)
        found.append((path.name, str(title)))
    found.sort(key=lambda entry: (not entry[0].startswith("sempods-"), entry[0]))
    return found


def try_it_page() -> str:
    """`site/api/index.html` with its source list generated from the descriptions on disk."""
    sources = ",\n".join(
        "      { url: '%s', title: '%s', slug: '%s'%s }"
        % (name, title.replace("'", "\\'"), Path(name).stem,
           ", default: true" if index == 0 else "")
        for index, (name, title) in enumerate(descriptions()))
    page = (SITE / "api" / "index.html").read_text()
    if SOURCES_MARKER not in page:
        raise SystemExit(f"error: site/api/index.html no longer contains {SOURCES_MARKER!r}, "
                         f"so the try-it page would render an empty source list")
    return page.replace(SOURCES_MARKER, sources)


def check() -> int:
    """Everything this build assumes, asserted before it can ship a broken page."""
    problems = []

    for name in CORE:
        if not (ROOT / "spec" / "core" / f"{name}.md").is_file():
            problems.append(f"spec/core/{name}.md is listed in CORE but does not exist")
    for name in MODULES:
        if not (ROOT / "spec" / "modules" / f"{name}.md").is_file():
            problems.append(f"spec/modules/{name}.md is listed in MODULES but does not exist")

    # The reverse direction, which is the one that goes wrong quietly: a chapter written and
    # never added here renders nowhere and nobody notices, because the build still succeeds.
    for path in sorted((ROOT / "spec" / "core").glob("*.md")):
        if path.stem not in CORE and path.stem != "README":
            problems.append(f"{path.relative_to(ROOT)} exists but is in no nav list")
    for path in sorted((ROOT / "spec" / "modules").glob("*.md")):
        if path.stem not in MODULES and path.stem != "README":
            problems.append(f"{path.relative_to(ROOT)} exists but is in no nav list")

    descriptions = sorted((ROOT / "openapi").glob("*.yaml"))
    if not descriptions:
        problems.append("openapi/ holds no description; the try-it page would render nothing")
    # There is deliberately no check that the try-it page's source list matches these files.
    # The list is generated from them, so a comparison would be asking whether they equal
    # themselves — which passes for the same reason it means nothing. What can go wrong is the
    # generation failing to happen, and that is asserted in `stage()`, on the staged file.
    if SOURCES_MARKER not in (SITE / "api" / "index.html").read_text():
        problems.append("site/api/index.html no longer marks where its source list goes, so "
                        "the try-it page would render with none")
    for src in descriptions:
        text = src.read_text()
        if "servers:" not in text:
            problems.append(f"{src.relative_to(ROOT)} has no servers block to point at a pod")
        else:
            addresses = server_addresses(with_demo_pod(text))
            if not addresses:
                problems.append(
                    f"{src.relative_to(ROOT)} declares no server, so the try-it page has no "
                    f"address to send its requests to")
            for template, resolved, variables in addresses:
                where = f"{src.relative_to(ROOT)} server {template!r}"
                if "{" in resolved:
                    problems.append(
                        f"{where} still holds an unresolved variable after staging "
                        f"({resolved!r}); it declares one it does not give a default")
                elif resolved not in ALLOWED_ADDRESSES:
                    problems.append(
                        f"{where} resolves to {resolved!r}, which is not one of the addresses "
                        f"the demo pod serves ({', '.join(sorted(ALLOWED_ADDRESSES))}). "
                        f"Whatever a reader presses in that description goes there")
                for name, value in variables.items():
                    wanted = {"origin": DEMO_ORIGIN, "pod": DEMO_POD}.get(name)
                    if wanted is not None and value != wanted:
                        problems.append(
                            f"{where} sets {name!r} to {value!r} rather than {wanted!r}")

    nav = (SITE / "mkdocs.yml").read_text()
    for name in CORE:
        if f"spec/core/{name}.md" not in nav:
            problems.append(f"spec/core/{name}.md is in CORE but missing from the mkdocs nav")
    for name in MODULES:
        if f"spec/modules/{name}.md" not in nav:
            problems.append(f"spec/modules/{name}.md is in MODULES but missing from the nav")

    for problem in problems:
        print(f"error: {problem}", file=sys.stderr)
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="rebuild and watch on :8000")
    parser.add_argument("--check", action="store_true", help="verify inputs, render nothing")
    args = parser.parse_args()

    failed = check()
    if failed or args.check:
        return failed

    configure()
    stage()
    if not args.serve:
        return subprocess.call(["mkdocs", "build", "--strict"], cwd=STAGE)

    # `--watch` on each real source, so an edit to a chapter triggers a rebuild; the hook in
    # `mkdocs.yml` re-stages before that rebuild reads anything. Watching the staged copy alone
    # — which is all MkDocs does by default — reacts only to changes nobody makes by hand.
    watched = [ROOT / "spec", ROOT / "vocabulary", ROOT / "GOVERNANCE.md",
               ROOT / "openapi", SITE / "index.md", SITE / "api"]
    command = ["mkdocs", "serve"]
    for path in watched:
        command += ["--watch", str(path)]
    return subprocess.call(command, cwd=STAGE)


if __name__ == "__main__":
    raise SystemExit(main())
