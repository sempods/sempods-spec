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

   Until `0.1` is tagged the third one is a notice rather than a failure, because there is no
   conformance suite yet to protect — GOVERNANCE.md §"Deleting and renumbering, before `0.1`".
   The exception closes itself; see `window_open`.

Run with no arguments to check the working tree. Pass a git ref to also compare against it:

    .github/scripts/check-requirements.py origin/main

One rule runs through all of it, and it is the one this script kept getting wrong: **an expected
artefact that is missing is a failure, not a skip.** A guard that quietly does nothing when its
input is absent reports success at exactly the moment it had nothing to say — and the states that
make it absent (a deleted directory, a dropped file) are the ones worth catching. So a missing
`spec/`, a missing `openapi/` and a missing `requirements.json` each stop the run rather than
shrinking what it examines.
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

# The tag that ends the window in which a requirement may be deleted or an identifier renumbered,
# and the one version in which that window is open.
#
# `PRE_RELEASE_VERSION` is an exact string rather than a `-dev` suffix test, and the difference is
# the whole guard. After `0.1` ships, ordinary development sets `0.2-dev` — and a suffix test would
# read that as pre-release and reopen a window GOVERNANCE.md says never reopens. Every later
# version fails the comparison, which is the direction that has to be automatic.
RELEASE_TAG = "0.1"
PRE_RELEASE_VERSION = "0.1-dev"

# A module versions independently of core (`SPS-CORE-005`, GOVERNANCE.md §"Versioning"), so one
# number over the whole index would be a claim the model does not make: a consumer reading a MEDIA
# requirement could not tell which media version it belongs to. They are all equal today and that
# is exactly why the shape is fixed now — adding the field after somebody vendors the file is a
# change every consumer has to absorb.
#
# This is the *only* place a module is enumerated, and even here it is checked against the
# chapters rather than trusted. Two independent maps — one from area to module, one from module to
# version — is a pair that has to be kept in step by somebody remembering to, and the failure is
# silent: a module in one and not the other publishes a part with no version behind it. So the
# module set comes from `spec/modules/`, where a module actually comes into existence, and its
# area is that name upper-cased.
MODULE_VERSIONS = {
    "oidc": "0.1-dev",
    "media": "0.1-dev",
    "mcp": "0.1-dev",
}

# The core areas, from the registry in `docs/agents/spec-authoring.md`. Listed rather than derived
# because a core area is not a file — several share one chapter, and `index.md` carries `CORE`.
#
# An area in neither half is an error rather than a default. Defaulting to core is the dangerous
# direction: a mistyped area would publish an optional obligation as one every implementation must
# satisfy, and regenerating the index reproduces it, so nothing downstream would ever notice.
CORE_AREAS = {"CORE", "CTX", "GRANT", "AUTH", "CRUD", "SPARQL", "FIND"}


def modules():
    """Module name → area, derived from the chapters that define them."""
    return {p.stem: p.stem.upper() for p in sorted(Path("spec/modules").glob("*.md"))}


def module_areas():
    """Area → module name, the direction the index needs."""
    return {area: name for name, area in modules().items()}


def versions_cover_modules():
    """Every module a chapter defines has a version, and every version has a chapter."""
    declared = set(MODULE_VERSIONS)
    actual = set(modules())
    problems = [f"spec/modules/{m}.md has no version in MODULE_VERSIONS" for m in sorted(actual - declared)]
    problems += [f"MODULE_VERSIONS names '{m}', which no chapter defines" for m in sorted(declared - actual)]
    if problems:
        print("\n".join(f"error: {p}" for p in problems), file=sys.stderr)
        return False
    return True


def window_open(spec_version, is_tagged):
    """Whether a requirement may still be deleted or an identifier renumbered.

    GOVERNANCE.md §"Deleting and renumbering, before `0.1`" opens this until the tag and closes it
    forever after. Two conditions rather than one, because each alone fails in the permissive
    direction: a checkout without tags — a shallow clone, an archive export — reads as untagged,
    and a `SPEC_VERSION` nobody remembered to move reads as pre-release. Both have to say
    pre-release, so either one closes the window on its own.

    The version test is an equality against one string, not a `-dev` suffix. A suffix test reopens
    the window at `0.2-dev`, and it does so in exactly the environment the tag half cannot cover —
    a clone without tags. Two guards that fail together are one guard.

    Pure, so the self-test can prove the polarity. An inverted condition here does not fail — it
    permits, and permitting silently is the whole failure mode this file exists to prevent.
    """
    return spec_version == PRE_RELEASE_VERSION and not is_tagged


def tagged(name=RELEASE_TAG):
    """Whether this checkout carries the release tag."""
    done = subprocess.run(["git", "tag", "--list", name], capture_output=True, text=True)
    return done.returncode == 0 and bool(done.stdout.strip())


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

    # Every combination that decides something, because the case that matters never fails loudly:
    # a window wrongly open lets a deletion through with a note that reads like approval. The
    # `0.2-dev` rows are the ones a suffix test got wrong — a later development version in a clone
    # without tags is the shape that silently reopens this.
    cases = {("0.1-dev", False): True, ("0.1-dev", True): False,
             ("0.1", False): False, ("0.1", True): False,
             ("0.2-dev", False): False, ("0.2-dev", True): False,
             ("1.0-dev", False): False}
    for (version, is_tagged), wanted in cases.items():
        if window_open(version, is_tagged) is not wanted:
            print(
                f"error: self-test failed — window_open({version!r}, {is_tagged}) is not {wanted}",
                file=sys.stderr,
            )
            return False
    return True


def require(path, what, contains=None):
    """Fail rather than examine less. See the rule in the module docstring.

    `contains` is a glob the directory must still match something for. Requiring the container and
    not its contents is the same mistake one level up: `openapi/` keeps existing because it holds a
    README, so every description could be deleted and this would go on passing. A guard that
    watches the box rather than what is in it is a guard that survives the theft.
    """
    if not path.exists():
        print(
            f"error: {path} is missing — {what}. Refusing to report success on a smaller set than "
            f"this check exists to cover.",
            file=sys.stderr,
        )
        return False
    if contains is not None and not any(path.glob(contains)):
        print(
            f"error: {path} matches no {contains} — {what}. The directory surviving is not the "
            f"same as its contents surviving.",
            file=sys.stderr,
        )
        return False
    return True


def descriptions_match_chapters():
    """Every module chapter has a description, and every description has a chapter.

    Requiring the directory to hold *something* was still too loose: deleting one description left
    three and passed. The fix is not a list of four filenames — a list is a thing to forget when a
    module is added, and the check would then be enforcing yesterday's shape.

    So the expectation is derived from the chapters, which is where a module comes into existence.
    A module chapter without its description fails, and a description without a chapter fails too —
    the second is what catches a rename that only moved one of the pair.

    A module with no pod-side HTTP surface would make the first half wrong, and that is deliberate:
    all three have one today, and deciding otherwise should cost somebody a visit to this function
    rather than happening quietly.
    """
    modules = {p.stem for p in Path("spec/modules").glob("*.md")}
    described = {p.stem.removeprefix("module-") for p in Path("openapi").glob("module-*.yaml")}

    problems = [f"spec/modules/{m}.md has no openapi/module-{m}.yaml" for m in sorted(modules - described)]
    problems += [f"openapi/module-{d}.yaml describes no spec/modules/{d}.md" for d in sorted(described - modules)]
    if not Path("openapi/sempods-core.yaml").exists():
        problems.append("openapi/sempods-core.yaml is missing — the core surface has no description")

    if problems:
        print("\n".join(f"error: {p}" for p in problems), file=sys.stderr)
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
    for path in sorted(Path("openapi").rglob("*.yaml")):
        text = path.read_text()
        for match in re.finditer(r"x-sps-requirements:\s*\[([^\]]*)\]", text):
            for ident in re.findall(r"SPS-[A-Z]+-\d{3}", match.group(1)):
                out.append((ident, path))
    return out


SUMMARY_END = re.compile(r'(?<=[.!?])\s')

# The withdrawal preamble `spec-authoring.md` §"Withdraw, never delete" mandates, which sits in
# front of the retained obligation: *Withdrawn in 0.3. Superseded by `SPS-X-NNN`.*
PREAMBLE = re.compile(r'^\*Withdrawn\b(?P<note>[^*]*)\*\s*', re.I)
SUCCESSOR = re.compile(r'Superseded by \[?`(SPS-[A-Z]+-\d{3})`')


def summarise(body):
    """The requirement's obligation in one sentence, and its withdrawal note if it has one.

    A consumer of the index — the reference implementation's citation check, a conformance report —
    wants enough to recognise the requirement without fetching the chapter. The first sentence is
    where the obligation lives; everything after it is qualification.

    A withdrawn requirement needs the preamble stepped over rather than summarised. Taking the
    first sentence literally there yields `*Withdrawn in 0.3.` — no successor and no obligation,
    which is precisely the case where recognising the identifier matters most, because it is
    permanent and cited somewhere this project cannot see.
    """
    text = " ".join(body.replace("\n", " ").split()).lstrip("— ").strip()

    note = None
    match = PREAMBLE.match(text)
    if match:
        note = ("Withdrawn" + match.group("note")).strip()
        text = text[match.end():].strip()

    first = SUMMARY_END.split(text, 1)
    return (first[0].strip() if first else text), note


def entry(ident, path, body):
    """One requirement as the index publishes it."""
    summary, note = summarise(body)
    row = {
        "id": ident,
        "part": module_areas().get(ident.split("-")[1], "core"),
        "chapter": str(path).replace("\\", "/"),
        "summary": summary,
        "withdrawn": note is not None,
    }
    if note:
        row["withdrawnNote"] = note
        successor = SUCCESSOR.search(note)
        if successor:
            row["supersededBy"] = successor.group(1)
    return row


def build_index(found):
    """The published index: identifier → where it lives and what it obliges.

    Deliberately carries no URL and no timestamp. A URL would pin a branch or a tag, and the
    consumer is the one who knows which it wants; a timestamp would make the file churn on every
    regeneration and turn a no-op into a diff.
    """
    problems = []
    for ident in found:
        area = ident.split("-")[1]
        if area not in CORE_AREAS and area not in module_areas():
            problems.append(
                f"{ident} is in area '{area}', which is neither a core area nor a module. "
                f"Register it in check-requirements.py and in docs/agents/spec-authoring.md, or "
                f"fix the identifier."
            )
    if problems:
        print("\n".join(problems), file=sys.stderr)
        raise SystemExit(6)

    return {
        # Core's version. Kept under this name because it is what a consumer pins to say which
        # specification it implements, and core is the part that has no opt-out.
        "specVersion": SPEC_VERSION,
        # Every part with a version of its own, core included, so a consumer never has to know
        # which key holds which. A requirement names its part rather than repeating the number,
        # so the two cannot drift.
        "versions": {"core": SPEC_VERSION, **MODULE_VERSIONS},
        "repository": "https://github.com/sempods/sempods-spec",
        "requirements": [
            entry(ident, path, body)
            for ident, (path, body) in sorted(found.items())
        ],
    }


def main():
    if not self_test():
        return 3

    writing = "--write-index" in sys.argv
    checks = [
        require(SPEC, "the chapters are what everything else is checked against"),
        require(Path("openapi"), "its citations are half of what this checks", contains="*.yaml"),
        # Not required when this run is the one creating it.
        writing or require(INDEX, "downstream repositories vendor it"),
        descriptions_match_chapters(),
        versions_cover_modules(),
    ]
    if not all(checks):
        return 5

    current, problems = collect(lambda p: p.read_text())
    notices = []
    if not current:
        print(
            f"error: {SPEC} defines no requirements at all. That is either a parsing failure or a "
            f"deletion; neither is something to pass.",
            file=sys.stderr,
        )
        return 5

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

        # Reported either way. A deletion inside the window is still the kind of change that has to
        # be seen to be reviewed — the failure this guard was written for is a deletion that reads
        # as tidying, and silence is what makes it read that way.
        open_window = window_open(SPEC_VERSION, tagged())
        for ident, (path, _) in sorted(before.items()):
            if ident not in current:
                if open_window:
                    notices.append(
                        f"{ident} was in {path} at {base} and is gone. Deleting is allowed until "
                        f"{RELEASE_TAG} is tagged — GOVERNANCE.md §\"Deleting and renumbering, "
                        f"before `0.1`\". Say in the change which identifier went, and why."
                    )
                else:
                    problems.append(
                        f"{ident} was in {path} at {base} and is gone. An identifier is never "
                        f"deleted — mark it withdrawn and keep its text (SPS-CORE-003)."
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

    if notices:
        print("\n" + "\n".join(f"notice: {n}" for n in notices))

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
    elif INDEX.read_text() != index:
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
