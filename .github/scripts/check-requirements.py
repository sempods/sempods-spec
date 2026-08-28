#!/usr/bin/env python3
"""Check the promises this repository makes about requirement identifiers.

Three of them, and none is checkable by a link checker:

1. An identifier's anchor matches it exactly. A mismatched anchor makes a citation resolve to the
   top of the page instead of failing, so the reader sees the wrong requirement and gets no sign
   of it.
2. No identifier is used twice — including twice inside one chapter, which is the shape a
   copy-paste produces and the one an identifier→body mapping used to swallow.
3. No identifier disappears. `SPS-CORE-003` says an identifier is never reassigned, never
   renumbered and never deleted — a retired requirement is marked withdrawn and keeps its text.
   That promise is what makes an identifier safe to cite from a conformance suite this project
   never sees, and it is exactly the kind of promise a reviewer stops noticing after the third
   pull request. Hence a check.

Run with no arguments to check the working tree. Pass a git ref to also compare against it:

    .github/scripts/check-requirements.py origin/main
"""
import json
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
INDEX = Path("requirements.json")

# Until `0.1` is tagged the index says so, so nothing downstream can pin a version that does not
# exist yet. GOVERNANCE.md §"The switch from descriptive to prescriptive" is what changes it.
SPEC_VERSION = "0.1-dev"


def requirements(text):
    """Every `(identifier, body)` a document opens, in order — a LIST, not a mapping.

    A mapping loses the case this guard exists for. Two paragraphs opening with the same
    identifier in one chapter — the shape a copy-paste produces — would collapse into one entry
    before anything counted them, and CI would report the identifiers as consistent while one of
    them silently addressed the wrong text.
    """
    return [
        (m.group(1), m.group(2))
        for m in re.finditer(r'^\*\*`(SPS-[A-Z]+-\d{3})`\*\*(.*?)(?=\n\n|\Z)', text, re.M | re.S)
    ]


def collect(read, paths=None):
    """Identifier → (path, body) across a set of documents, via a `read` that may hit git.

    Both the working tree and a git ref go through here. They used to unpack `requirements()`
    separately, which is how a change to its return type left one of the two broken while every
    local run stayed green — the base comparison only executes when a ref is passed.
    """
    found, problems = {}, []
    for path in sorted(paths if paths is not None else SPEC.rglob("*.md")):
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
        for ident, body in requirements(text):
            if ident in found:
                where = found[ident][0]
                problems.append(
                    f"{ident} appears twice in {path}" if where == path
                    else f"{ident} appears in both {where} and {path}"
                )
            found[ident] = (path, body)
    return found, problems


def self_test():
    """Prove the duplicate check before trusting it with a pull request.

    The same shape the DCO workflow uses on its own predicate, and for the same reason: the
    alternative is trusting a claim in a commit message, which protects nothing the next time this
    function is touched. Both cases earn their place — a duplicate inside one document is the one a
    mapping used to swallow, and the distinct pair is what must not be reported.
    """
    doc = (
        '<a id="SPS-X-001"></a>\n**`SPS-X-001`** — first.\n\n'
        '<a id="SPS-X-001"></a>\n**`SPS-X-001`** — a copy-paste of the same identifier.\n\n'
        '<a id="SPS-X-002"></a>\n**`SPS-X-002`** — distinct.\n'
    )
    found = requirements(doc)
    idents = [i for i, _ in found]
    if idents != ["SPS-X-001", "SPS-X-001", "SPS-X-002"]:
        print(f"error: self-test failed — requirements() returned {idents}", file=sys.stderr)
        return False
    return True


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


SUMMARY_END = re.compile(r'(?<=[.!?])\s')


def summarise(body):
    """The requirement's first sentence, flattened onto one line.

    A consumer of the index — the reference implementation's link checker, a conformance report —
    wants enough to recognise the requirement without fetching the chapter. The first sentence is
    where the obligation lives; everything after it is qualification.
    """
    text = " ".join(body.replace("\n", " ").split()).lstrip("— ").strip()
    parts = SUMMARY_END.split(text, 1)
    return parts[0].strip() if parts else text


def build_index(found):
    """The published index: identifier → where it lives and what it obliges.

    Deliberately carries no URL and no timestamp. A URL would pin a branch or a tag, and the
    consumer is the one who knows which it wants; a timestamp would make the file churn on every
    regeneration and turn a no-op into a diff.
    """
    return {
        "specVersion": SPEC_VERSION,
        "repository": "https://github.com/sempods/sempods-spec",
        "requirements": [
            {
                "id": ident,
                "chapter": str(path).replace("\\", "/"),
                "summary": summarise(body),
                "withdrawn": bool(WITHDRAWN.search(body)),
            }
            for ident, (path, body) in sorted(found.items())
        ],
    }


def main():
    if not self_test():
        return 3

    current, problems = collect(lambda p: p.read_text())

    # The OpenAPI description is hand-written and normative, so nothing regenerates it when a
    # chapter moves. A citation pointing at an identifier that no longer exists is the way that
    # goes wrong, and it is invisible to every other check here.
    cited = openapi_citations()
    for ident, path in cited:
        if ident not in current:
            problems.append(f"{path}: cites {ident}, which no chapter defines")

    refs = [a for a in sys.argv[1:] if not a.startswith("--")]
    base = refs[0] if refs else None
    if base:
        def at_base(path):
            done = subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True, text=True)
            return done.stdout if done.returncode == 0 else None

        # `git show` needs the paths that existed then, not the ones that exist now: a chapter that
        # was split would otherwise take its identifiers with it and read as a mass deletion.
        listing = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", base, "spec/"], capture_output=True, text=True
        )
        # A ref this repository does not have makes `ls-tree` fail with an empty stdout, which is
        # indistinguishable from "the base had no chapters" — so the disappearance check would be
        # skipped and the script would still exit 0, reporting consistency it never established.
        # A typo in a local invocation is exactly how that happens.
        if listing.returncode != 0:
            print(
                f"error: cannot read '{base}' — {listing.stderr.strip() or 'unknown ref'}.\n"
                f"The disappearance check needs a base that exists; refusing to report success "
                f"without running it.",
                file=sys.stderr,
            )
            return 2
        old_paths = [Path(line) for line in listing.stdout.splitlines() if line.endswith(".md")]
        before, _ = collect(at_base, old_paths)

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

    # The index is generated, committed, and checked rather than built on demand: the consumer is
    # another repository, which vendors it and must be able to see a specification upgrade as a
    # diff rather than discovering one at build time.
    index = json.dumps(build_index(current), indent=2, ensure_ascii=False) + "\n"
    if "--write-index" in sys.argv:
        INDEX.write_text(index)
        print(f"wrote {INDEX} — {len(current)} requirements")
    elif INDEX.exists() and INDEX.read_text() != index:
        print(
            f"error: {INDEX} is out of date. Regenerate it:\n"
            f"    .github/scripts/check-requirements.py --write-index",
            file=sys.stderr,
        )
        return 4

    print("\nrequirement identifiers are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
