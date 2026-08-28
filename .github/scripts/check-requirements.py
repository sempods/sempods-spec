#!/usr/bin/env python3
"""Check the promises this repository makes about requirement identifiers.

Three of them, and none is checkable by a link checker:

1. An identifier's anchor matches it exactly. A mismatched anchor makes a citation resolve to the
   top of the page instead of failing, so the reader sees the wrong requirement and gets no sign
   of it.
2. No identifier is used twice.
3. No identifier disappears. `SPS-CORE-003` says an identifier is never reassigned, never
   renumbered and never deleted — a retired requirement is marked withdrawn and keeps its text.
   That promise is what makes an identifier safe to cite from a conformance suite this project
   never sees, and it is exactly the kind of promise a reviewer stops noticing after the third
   pull request. Hence a check.

Run with no arguments to check the working tree. Pass a git ref to also compare against it:

    .github/scripts/check-requirements.py origin/main
"""
import re
import subprocess
import sys
from pathlib import Path

# The written form spec-authoring.md §"The written form" mandates: an explicit anchor line, then a
# paragraph opening with the identifier in bold code. Parsing the text rather than maintaining an
# index beside it is deliberate — an index maintained beside the text is an index that is wrong.
ANCHOR_THEN_ID = re.compile(r'<a id="(SPS-[A-Z]+-\d{3})"></a>\s*\n\*\*`(SPS-[A-Z]+-\d{3})`\*\*')
BOLD_ID_LINE = re.compile(r'^\*\*`(SPS-[A-Z]+-\d{3})`\*\*', re.M)
WITHDRAWN = re.compile(r'\*Withdrawn\b', re.I)

SPEC = Path("spec")


def requirements(text):
    """Identifier → the paragraph it opens, for one document."""
    out = {}
    for match in re.finditer(r'^\*\*`(SPS-[A-Z]+-\d{3})`\*\*(.*?)(?=\n\n|\Z)', text, re.M | re.S):
        out[match.group(1)] = match.group(2)
    return out


def collect(read):
    """Identifier → (path, body) across the spec tree, via a `read` that may hit git."""
    found, problems = {}, []
    for path in sorted(SPEC.rglob("*.md")):
        text = read(path)
        if text is None:
            continue
        for anchor, ident in ANCHOR_THEN_ID.findall(text):
            if anchor != ident:
                problems.append(f"{path}: anchor '{anchor}' does not match identifier '{ident}'")
        # A bold identifier with no anchor above it is a requirement nothing can cite.
        lines = text.splitlines()
        for match in BOLD_ID_LINE.finditer(text):
            no = text[: match.start()].count("\n")
            above = lines[no - 1] if no else ""
            if f'<a id="{match.group(1)}">' not in above:
                problems.append(f"{path}:{no + 1}: {match.group(1)} has no anchor line above it")
        for ident, body in requirements(text).items():
            if ident in found:
                problems.append(f"{ident} appears in both {found[ident][0]} and {path}")
            found[ident] = (path, body)
    return found, problems


def openapi_citations():
    """Every identifier cited from an `x-sps-requirements` list, with the file citing it.

    Parsed with a regex rather than a YAML library: this repository has no build system and no
    dependencies, and the citation form is one line of literal syntax that the OpenAPI files are
    written to keep. A citation that does not match this shape is not silently skipped — it would
    have to be malformed YAML too, which the workflow's own parse step catches.
    """
    out = []
    for path in sorted(Path("openapi").rglob("*.yaml")) if Path("openapi").is_dir() else []:
        text = path.read_text()
        for match in re.finditer(r"x-sps-requirements:\s*\[([^\]]*)\]", text):
            for ident in re.findall(r"SPS-[A-Z]+-\d{3}", match.group(1)):
                out.append((ident, path))
    return out


def main():
    current, problems = collect(lambda p: p.read_text())

    # The OpenAPI description is hand-written and normative, so nothing regenerates it when a
    # chapter moves. A citation pointing at an identifier that no longer exists is the way that
    # goes wrong, and it is invisible to every other check here.
    cited = openapi_citations()
    for ident, path in cited:
        if ident not in current:
            problems.append(f"{path}: cites {ident}, which no chapter defines")

    base = sys.argv[1] if len(sys.argv) > 1 else None
    if base:
        def at_base(path):
            done = subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True, text=True)
            return done.stdout if done.returncode == 0 else None

        # `git show` needs the paths that existed then, not the ones that exist now: a chapter that
        # was split would otherwise take its identifiers with it and read as a mass deletion.
        listing = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", base, "spec/"], capture_output=True, text=True
        )
        old_paths = [Path(line) for line in listing.stdout.splitlines() if line.endswith(".md")]
        before = {}
        for path in old_paths:
            text = at_base(path)
            if text:
                before.update({i: (path, b) for i, b in requirements(text).items()})

        for ident, (path, _) in sorted(before.items()):
            if ident not in current:
                problems.append(
                    f"{ident} was in {path} at {base} and is gone. An identifier is never deleted — "
                    f"mark it withdrawn and keep its text (SPS-CORE-003)."
                )

    by_area = {}
    for ident in current:
        by_area.setdefault(ident.split("-")[1], []).append(int(ident.split("-")[2]))
    for area, numbers in sorted(by_area.items()):
        withdrawn = sum(1 for i, (_, b) in current.items() if i.startswith(f"SPS-{area}-") and WITHDRAWN.search(b))
        note = f", {withdrawn} withdrawn" if withdrawn else ""
        print(f"{area:7s} {len(numbers):3d} requirements, highest {max(numbers):3d}{note}")

    if cited:
        print(f"openapi {len(cited):3d} citations over {len({p for _, p in cited})} file(s), "
              f"{len({i for i, _ in cited})} distinct requirements")

    if problems:
        print("\n" + "\n".join(problems), file=sys.stderr)
        return 1
    print("\nrequirement identifiers are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
