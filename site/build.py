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
import copy
import json
import posixpath
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

# What the try-it page identifies as when a reader logs in. A `did:web:` client is its origin and
# registers nothing, so this is the site's own address and changes only if the site moves.
DEMO_CLIENT = "did:web:spec.sempods.org"

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
AUTH_MARKER = "/* AUTH */"

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


def with_repository_links(text: str, staged_at: str, published: set) -> str:
    """Point a staged document's off-site links at the repository.

    A chapter may link to the roadmap, the authoring rules or `requirements.json`, and none of
    those is published. Rewritten here rather than written absolutely in the file, because the
    file is also read on GitHub at a tag or a branch, where a hard-coded `main` silently mixes
    one revision's text with another's.

    Resolved against `staged_at` — where the file ends up — rather than against where it came
    from. Those differ for exactly one file and it is the important one: `site/index.md` is
    staged at the site root, so its `spec/core/auth.md` means the chapter, while resolving it
    beside the source would mean `site/spec/core/auth.md`, which is nothing. An earlier version
    did that and turned all ten of the landing page's links into repository URLs for paths that
    do not exist — invisibly, because a strict build does not follow absolute links.
    """
    def rewrite(match: "re.Match[str]") -> str:
        target = match.group(1)
        path, _, fragment = target.partition("#")
        if not path:
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(staged_at), path))
        if resolved in published:
            return match.group(0)
        kind = "tree" if (ROOT / resolved).is_dir() else "blob"
        suffix = f"#{fragment}" if fragment else ""
        return f"]({REPOSITORY}/{kind}/main/{resolved}{suffix})"

    return RELATIVE_LINK.sub(rewrite, text)


def configure() -> None:
    """Put the MkDocs configuration in place. Once per invocation, before the server starts.

    Kept apart from `stage()` because that one is called again under a running server, and a
    server whose configuration file is deleted and rewritten beneath it is a server that reloads
    into whatever state the filesystem happened to be in.
    """
    STAGE.mkdir(parents=True, exist_ok=True)
    shutil.copy(SITE / "mkdocs.yml", STAGE / "mkdocs.yml")


def write_if_changed(path: Path, content: bytes) -> None:
    """Write only when the bytes differ.

    MkDocs watches the directory this stages into, so every write it does not need is a file
    event, and every file event is another build that stages again. Rewriting the tree
    unconditionally turns one saved chapter into a rebuild loop — measured at thirty-six builds
    from a single edit before this existed.
    """
    if path.exists() and path.read_bytes() == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def staged_content() -> dict:
    """Everything the site is built from, as staged path -> bytes.

    Assembled before anything is written, so `stage()` can compare, and so a file that stopped
    having a source is recognised by its absence here rather than by deleting the tree.
    """
    copied = {}
    for root in ("spec", "vocabulary"):
        for source in sorted((ROOT / root).rglob("*")):
            if source.is_file():
                copied[f"{root}/{source.relative_to(ROOT / root).as_posix()}"] = source
    copied["GOVERNANCE.md"] = ROOT / "GOVERNANCE.md"
    copied["index.md"] = SITE / "index.md"

    generated = {"api/index.html": try_it_page().encode()}
    for source in sorted((ROOT / "openapi").glob("*.yaml")):
        generated[f"api/{source.name}"] = with_demo_pod(source.read_text()).encode()

    # The full set first: a link stays relative when it lands on something the site publishes,
    # and that cannot be decided one file at a time. The generated pages count — the landing
    # page links to the try-it page, which exists only here.
    published = set(copied) | set(generated)

    wanted = dict(generated)
    for relative, source in copied.items():
        if source.suffix == ".md":
            wanted[relative] = with_repository_links(
                source.read_text(), relative, published).encode()
        else:
            wanted[relative] = source.read_bytes()

    wanted["CNAME"] = b"spec.sempods.org\n"
    return wanted


def stage() -> None:
    """Bring the rendered directory in line with the sources.

    Called again before every rebuild while serving, through `hooks.py`: MkDocs watches the
    directory it renders and that directory is a copy, so without re-staging an edit to a
    chapter changes nothing the server can see. It writes only what differs, for the reason
    `write_if_changed` gives.
    """
    docs = STAGE / "docs"
    docs.mkdir(parents=True, exist_ok=True)

    wanted = staged_content()
    for relative, content in wanted.items():
        write_if_changed(docs / relative, content)

    for existing in sorted(docs.rglob("*"), reverse=True):
        if existing.is_file() and existing.relative_to(docs).as_posix() not in wanted:
            existing.unlink()
        elif existing.is_dir() and not any(existing.iterdir()):
            existing.rmdir()

    # Every repository URL this build wrote has to name something that is there. The rewriting
    # resolves paths, and a resolution that goes wrong produces a well-formed link to nothing —
    # which `--strict` cannot see, because it does not follow absolute URLs. Ten of them shipped
    # that way once: the entire navigation of the landing page.
    written = re.compile(re.escape(REPOSITORY) + r"/(?:blob|tree)/main/([^)#]+)")
    for relative, content in wanted.items():
        if relative.endswith(".md"):
            for target in written.findall(content.decode()):
                if not (ROOT / target).exists():
                    raise SystemExit(
                        f"error: {relative} was staged with a link to {target!r}, which this "
                        f"repository does not hold — the rewriting resolved it wrongly")

    # Asserted on the staged file rather than on what `try_it_page()` returns. `check()` calls
    # that function and would have been satisfied by it while `stage()` copied the template past
    # it untouched — which is exactly what happened once. What ships is what gets checked.
    staged_page = (docs / "api" / "index.html").read_text()
    if SOURCES_MARKER in staged_page:
        raise SystemExit(f"error: the staged try-it page still holds {SOURCES_MARKER!r}; its "
                         f"source list was never generated")
    for name, _ in descriptions():
        if f"url: {as_script_literal(name)}" not in staged_page:
            raise SystemExit(f"error: the staged try-it page does not offer {name!r}")


PLACEHOLDER_POD = "https://example.org/alice"

ORIGIN_DEFAULT = re.compile(r"""(default:\s*)['"]?https://example\.org['"]?""")
POD_DEFAULT = re.compile(r"""(default:\s*)['"]?alice['"]?(?![\w-])""")


# The only two values the substitution is allowed to change. Everything else in a description,
# a server variable's own `description` and `enum` included, has to survive staging untouched.
REWRITABLE = ("origin", "pod")


# Where OpenAPI 3.1 permits a `servers` field, and nowhere else: the document root, a Path
# Item Object, and an Operation Object. Path Items reach the document through `paths`, through
# `webhooks`, and through `components.pathItems`.
#
# Named here rather than found by searching for the key, because a `servers` key can also occur
# in a schema, an example or any other payload a description happens to document — and rewriting
# somebody's example data would publish a contract nobody wrote.
METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")
PATH_ITEM_CONTAINERS = ("paths", "webhooks")


def server_declarations(document, mapping_items, mapping_get):
    """Every `servers` value at a level OpenAPI allows one, as whatever `entry` returns.

    Written once against two shapes: a parsed document, where a mapping is a `dict`, and a
    composed node tree, where it is a `MappingNode`. The traversal is the same and only the two
    accessors differ, so there is one description of where a server may live rather than two
    that can drift apart.
    """
    found = []

    def at_level(node) -> None:
        servers = mapping_get(node, "servers")
        if servers is not None:
            found.append(servers)

    def at_path_item(item) -> None:
        at_level(item)
        for key, operation in mapping_items(item):
            if key in METHODS:
                at_level(operation)

    at_level(document)
    for container in PATH_ITEM_CONTAINERS:
        for _, item in mapping_items(mapping_get(document, container)):
            at_path_item(item)
    components = mapping_get(document, "components")
    for _, item in mapping_items(mapping_get(components, "pathItems")):
        at_path_item(item)
    return found


def _node_items(node):
    import yaml
    if not isinstance(node, yaml.MappingNode):
        return []
    return [(getattr(key, "value", None), value) for key, value in node.value]


def _node_get(node, key):
    for name, value in _node_items(node):
        if name == key:
            return value
    return None


def rewritable_default_lines(text: str) -> set:
    """The lines holding the `default:` values this build may change, and no others.

    Located node by node, at the levels a server may be declared. Earlier versions narrowed by
    indentation and then by the span of a `servers:` value; both were too coarse, because what
    has to be found is a node and lines know nothing of nodes. Searching the node tree for the
    key was too coarse in the other direction, because a `servers` key in an example is not a
    server declaration.

    What comes back is the position of two scalars per declared server — the defaults of
    `origin` and `pod` — so prose and payloads anywhere are left as they were written.
    """
    import yaml

    lines: set = set()
    for servers in server_declarations(yaml.compose(text), _node_items, _node_get):
        if not isinstance(servers, yaml.SequenceNode):
            continue
        for server in servers.value:
            variables = _node_get(server, "variables")
            for name, variable in _node_items(variables):
                if name not in REWRITABLE:
                    continue
                for field, content in _node_items(variable):
                    if field == "default":
                        lines.add(content.start_mark.line)
    return lines


def with_demo_pod(yaml_text: str) -> str:
    """Point a staged description's server variables at the demo pod.

    Confined to the exact lines the parser puts the two rewritable defaults on. Applied more
    widely it would rewrite a schema default, an example, or a server variable's own description
    that legitimately says `alice` — and the address check would not notice, because that only
    ever looks at what the servers resolve to.

    Substitution rather than a YAML round-trip: parsing and re-emitting would reformat
    hand-written files whose layout and comments are part of how they read. What guards the
    difference between the two is `unchanged_outside_servers` below, which compares the parsed
    documents and refuses any edit that reached something else.
    """
    lines = yaml_text.splitlines(keepends=True)
    for index in rewritable_default_lines(yaml_text):
        if index < len(lines):
            line = ORIGIN_DEFAULT.sub(lambda m: m.group(1) + f"'{DEMO_ORIGIN}'", lines[index])
            lines[index] = POD_DEFAULT.sub(lambda m: m.group(1) + DEMO_POD, line)

    # The OAuth flow URLs name the same placeholder pod the `servers` block defaults to, and have
    # to move with it — a staged description saying `sempods.org/aaltra` under `servers` and
    # `example.org/alice` under `securitySchemes` would send the try-it login somewhere the rest
    # of the page never talks to. They are plain strings rather than server variables, so they are
    # substituted by value here; `flow_url_lines` says which lines may be touched.
    for index in flow_url_lines(yaml_text):
        if index < len(lines):
            lines[index] = lines[index].replace(PLACEHOLDER_POD, f"{DEMO_ORIGIN}/{DEMO_POD}")
    return "".join(lines)


def flow_urls(staged: str) -> list:
    """Every OAuth flow endpoint in a staged description, as (scheme, flow, field, url)."""
    found = []
    document = load(staged)
    schemes = _dict_get(_dict_get(document, "components"), "securitySchemes")
    for scheme_name, scheme in _dict_items(schemes):
        for flow_name, flow in _dict_items(_dict_get(scheme, "flows")):
            for field, url in _dict_items(flow):
                if field in ("authorizationUrl", "tokenUrl", "refreshUrl"):
                    found.append((scheme_name, flow_name, field, str(url)))
    return found


def flow_url_lines(text: str) -> set:
    """The lines holding an OAuth flow's endpoint URLs, asked of the parser.

    Located by walking to `components.securitySchemes.*.flows.*` rather than by matching the
    placeholder anywhere, for the reason the server substitution has: a description may quote
    that URL in prose or in an example, and rewriting it there publishes a contract nobody wrote.
    """
    import yaml

    lines: set = set()
    root = yaml.compose(text)
    schemes = _node_get(_node_get(root, "components"), "securitySchemes")
    for _, scheme in _node_items(schemes):
        for _, flows in [(k, v) for k, v in _node_items(scheme) if k == "flows"]:
            for _, flow in _node_items(flows):
                for field, value in _node_items(flow):
                    if field in ("authorizationUrl", "tokenUrl", "refreshUrl"):
                        lines.add(value.start_mark.line)
    return lines


def _dict_items(value):
    return value.items() if isinstance(value, dict) else []


def _dict_get(value, key):
    return value.get(key) if isinstance(value, dict) else None


def without_rewritable_defaults(document):
    """A copy with `servers[].variables.{origin,pod}.default` blanked, and nothing else.

    Masking every `servers` the document contains would hide the case this exists to catch, in
    both directions: a variable's own `description` is a scalar like any other, and a `servers`
    key inside an example is not a server at all. So the same traversal that decides what may be
    rewritten decides what is excused from the comparison — one description of where a server
    lives, used by both halves.
    """
    pruned = copy.deepcopy(document)

    schemes = _dict_get(_dict_get(pruned, "components"), "securitySchemes")
    for _, scheme in _dict_items(schemes):
        for _, flow in _dict_items(_dict_get(scheme, "flows")):
            for field in ("authorizationUrl", "tokenUrl", "refreshUrl"):
                if isinstance(flow, dict) and field in flow:
                    flow[field] = None

    for servers in server_declarations(pruned, _dict_items, _dict_get):
        if not isinstance(servers, list):
            continue
        for server in servers:
            variables = _dict_get(server, "variables")
            for name in REWRITABLE:
                variable = _dict_get(variables, name)
                if isinstance(variable, dict) and "default" in variable:
                    variable["default"] = None
    return pruned


def unchanged_outside_servers(before: str, after: str) -> bool:
    """Whether substitution touched anything but a server variable.

    The post-condition for over-reach, and the reason the substitution is allowed to be textual
    at all. Every earlier version of this guard asked something about the *input* — whether a
    pattern was present, whether a placeholder was left — and each passed while shipping
    something wrong. This one compares the two documents and answers about the result.
    """
    return without_rewritable_defaults(load(before)) == without_rewritable_defaults(load(after))


def load(staged: str) -> object:
    try:
        import yaml
    except ImportError:  # pragma: no cover - the workflow installs it with the renderer
        raise SystemExit(
            "error: PyYAML is needed to read the staged descriptions.\n"
            "       pip install -r site/requirements.txt")
    return yaml.safe_load(staged)


def server_addresses(staged: str) -> list:
    """Every declared server as (template, resolved address, its variables).

    Uses the same traversal as the substitution and the comparison. It has to: a `servers` key
    inside an example is not a server, and a check that walked the whole document would refuse a
    description for pointing its own sample payload at `example.org` — which is exactly what a
    sample payload should say.

    Resolved, not just collected. Checking that the defaults are the demo values says nothing
    about what they are composed into: `{pod}/{origin}` and a literal `https://example.org/{pod}`
    both leave the defaults untouched and send the reader elsewhere. The address is what Scalar
    dials, so the address is what gets asserted.
    """
    found = []
    for servers in server_declarations(load(staged), _dict_items, _dict_get):
        if not isinstance(servers, list):
            continue
        for server in servers:
            if not isinstance(server, dict):
                continue
            template = str(server.get("url", ""))
            variables = {
                name: variable.get("default")
                for name, variable in _dict_items(server.get("variables"))
                if isinstance(variable, dict)
            }
            resolved = template
            for name, value in variables.items():
                resolved = resolved.replace("{" + name + "}", str(value))
            found.append((template, resolved, variables))
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


def as_script_literal(value: str) -> str:
    """One value, safe inside a `<script>` element in an HTML document.

    `json.dumps` handles what breaks a JavaScript string — a title is whatever the description
    calls itself, and YAML lets that be folded across lines or carry a backslash. It does not
    handle what breaks the surrounding *element*: an HTML parser ends a script at the first
    `</script>` in the text, string literal or not, so a title documenting markup would close
    the block and leave everything after it to be read as page content.

    `<`, `>` and `&` therefore leave as escapes. They mean the same to JavaScript and nothing at
    all to the HTML parser.
    """
    return (json.dumps(value)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def try_it_page() -> str:
    """`site/api/index.html` with its source list generated from the descriptions on disk."""
    # `json.dumps` per value rather than quoting by hand. A title is whatever the description
    # says it is — YAML allows it folded over several lines, and a newline or a backslash
    # written straight into a quoted JavaScript string breaks the whole initialiser, which no
    # check here would see because the page is never parsed.
    sources = ",\n".join(
        "      { url: %s, title: %s, slug: %s%s }"
        % (as_script_literal(name), as_script_literal(title),
           as_script_literal(Path(name).stem),
           ", default: true" if index == 0 else "")
        for index, (name, title) in enumerate(descriptions()))

    # Only the client identity. The endpoints come from the staged description, which names the
    # demo pod because `with_demo_pod` moved them there with everything else.
    authentication = """    authentication: {
      preferredSecurityScheme: 'oauth2',
      securitySchemes: {
        oauth2: {
          flows: {
            authorizationCode: { 'x-scalar-client-id': %s },
          },
        },
      },
    },""" % json.dumps(DEMO_CLIENT)

    page = (SITE / "api" / "index.html").read_text()
    for marker, what in ((SOURCES_MARKER, "source list"), (AUTH_MARKER, "authentication block")):
        if marker not in page:
            raise SystemExit(f"error: site/api/index.html no longer contains {marker!r}, so the "
                             f"try-it page would render without its {what}")
    return page.replace(SOURCES_MARKER, sources).replace(AUTH_MARKER, authentication)


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
            if not unchanged_outside_servers(text, with_demo_pod(text)):
                problems.append(
                    f"{src.relative_to(ROOT)} would stage with an edit somewhere other than the "
                    f"`origin` and `pod` defaults of a server. Nothing else may be rewritten; "
                    f"anything else means the try-it page shows a contract nobody wrote")
            # The flow URLs are excused from the comparison above, so this is what stands in
            # its place: after staging they must be on the demo pod, the way a server must.
            # Without it an endpoint edited to a foreign host would stage untouched — the
            # substitution replaces one exact string and silently does nothing to any other —
            # and the try-it login would carry a reader there.
            staged = with_demo_pod(text)
            pod_base = f"{DEMO_ORIGIN}/{DEMO_POD}/"
            for scheme, flow, field, url in flow_urls(staged):
                if not url.startswith(pod_base):
                    problems.append(
                        f"{src.relative_to(ROOT)} would stage {scheme}.{flow}.{field} as {url!r}, "
                        f"which is not on the demo pod. A reader logging in from the try-it page "
                        f"would be sent there")

            addresses = server_addresses(staged)
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
