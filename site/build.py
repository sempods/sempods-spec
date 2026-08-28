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

# Chapters, in reading order. The nav in `mkdocs.yml` repeats this order; a chapter added
# here and forgotten there is caught by `--check`.
CORE = ["index", "contexts", "grants", "auth", "lod-crud", "sparql", "find"]
MODULES = ["oidc", "media", "mcp"]


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

    api = docs / "api"
    api.mkdir()
    shutil.copy(SITE / "api" / "index.html", api / "index.html")
    for src in sorted((ROOT / "openapi").glob("*.yaml")):
        (api / src.name).write_text(with_demo_pod(src.read_text()))

    (docs / "CNAME").write_text("spec.sempods.org\n")


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


def server_defaults(staged: str) -> list[tuple[str, object]]:
    """Every server-variable default in a description, at whatever level it is declared.

    Walked recursively rather than reading `doc["servers"]`, because a description may set
    servers at the document, path or operation level, and `sempods-core.yaml` does exactly
    that — a document-level one and another further down.

    Parsed rather than pattern-matched. This is the post-condition, and the two versions of
    it that were written by pattern both passed while shipping a broken page: the first asked
    whether the input contained a spelling, which one occurrence satisfies for a whole file,
    and the second asked whether a known placeholder was left, which says nothing about a
    default that was changed to some third host. Asking the document what its servers
    actually point at is the only form that cannot be satisfied by the wrong thing.
    """
    try:
        import yaml
    except ImportError:  # pragma: no cover - the workflow installs it with the renderer
        raise SystemExit(
            "error: PyYAML is needed to verify the staged server URLs.\n"
            "       pip install -r site/requirements.txt")

    found: list[tuple[str, object]] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            servers = node.get("servers")
            if isinstance(servers, list):
                for server in servers:
                    variables = (server or {}).get("variables") if isinstance(server, dict) else None
                    for name, variable in (variables or {}).items():
                        if isinstance(variable, dict):
                            found.append((name, variable.get("default")))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(yaml.safe_load(staged))
    return found


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
    for src in descriptions:
        text = src.read_text()
        if "servers:" not in text:
            problems.append(f"{src.relative_to(ROOT)} has no servers block to point at a pod")
        else:
            expected = {DEMO_ORIGIN, DEMO_POD}
            defaults = server_defaults(with_demo_pod(text))
            if not defaults:
                problems.append(
                    f"{src.relative_to(ROOT)} declares servers with no variables to point at "
                    f"a pod, so the try-it button has no address to send anything to")
            for name, value in defaults:
                if value not in expected:
                    problems.append(
                        f"{src.relative_to(ROOT)} would stage with server variable {name!r} "
                        f"set to {value!r}. Every one of them has to end up at the demo pod; "
                        f"this description's requests would go somewhere nobody operates")

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
