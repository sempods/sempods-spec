# Governance

How this specification is versioned, when it starts binding implementations, and how a change to it
is made.

## Versioning

**The specification has its own version line** — `0.1`, `0.2`, … — independent of any
implementation. The reference implementation is on `0.2.0-SNAPSHOT` while this specification starts
at `0.1`, and locking the two together would mean every implementation release forced a
specification release and the reverse.

An implementation states which specification version it implements, and that statement is
machine-readable rather than prose in a README. The reference implementation carries it in
`gradle.properties`; every implementation exposes it to clients at the conformance discovery
endpoint. Without such a declaration "implements sempods 0.1" is a claim nobody can check.

**Modules version separately from core.** A pod may implement core `0.1` and media `0.2`. That is
the point of the split — a module that moves fast must not drag the core version with it, and an
implementation that skips a module entirely is still conformant.

### What a version number promises

- **`0.x`** — the contract may break between minors. Breaking changes are listed in the release
  notes and are never silent.
- **Requirement IDs never break.** An ID is never reassigned and never renumbered;
  a withdrawn requirement stays in the text marked `withdrawn` with a pointer to its successor.
  This is deliberately the same rule the vocabulary applies to RDF terms, and for the same reason:
  an ID ends up in other people's test suites the way a term ends up in other people's data.
  There are no such test suites yet, and §"Deleting and renumbering, before `0.1`" says what follows
  from that — including that the first one to appear closes the window without waiting for the tag.
- **Published IRIs never change.** Module IRIs and vocabulary terms under
  `https://schema.sempods.org/` are permanent identifiers, `0.x` included.

## The switch from descriptive to prescriptive

This is the one piece of process worth stating precisely, because it silently never happens
otherwise.

**Before the `0.1` release — descriptive.** The specification is extracted from the reference
implementation. Where the text and the code disagree, the code is right and the text is the bug.
A chapter is written by reading what the implementation does, deciding which parts of it are the
contract and which are one implementation's choice, and writing down only the first.

**From the `0.1` release on — prescriptive.** A behaviour change is decided here first, and an
implementation that disagrees with the specification is the bug — the reference implementation
included. It gets no standing it does not earn by being correct.

The switch happens **when `0.1` is tagged in this repository**, not when it feels ready. Until then
every chapter carries the fact that it is descriptive; after it, nothing does, because it is the
default.

### When `0.1` gets tagged

**The current version is `0.1-dev`, and it is not close to a tag.** That is a decision, not a
delay.

A tag is a promise to somebody. There is nobody yet: no second implementation, no client outside
this project whose build breaks when a requirement moves. Tagging before there is buys nothing and
spends the freedom to still be wrong about the shape — which the specification currently is in at
least one place it knows of, and probably more it does not.

So the trigger is not a date. **`0.1` is tagged when two things hold at once:** somebody is there
to promise to — a second implementation, or a client outside this project that depends on the
contract — **and** everything below is settled. Adoption is what makes the tag worth cutting; the
open questions are what makes it possible. Neither is sufficient alone, and adoption arriving first
is a reason to close the rest, not to tag around it.

Until then `0.1-dev` is what an implementation declares, what the conformance endpoint reports, and
what this document means wherever it says "before the tag". It is the honest answer to "which
version is this?" — more honest than a `0.1` that gets edited the week after it is cut.

### What has to be settled first

**The roadmap's open decisions are the gate, not a list kept here** — two copies of that list would
disagree within a week. What is written down there as required before `0.1` is required before
`0.1`, and one of those is a **known security defect**: `SPS-CORE-018` is a context-enumeration
oracle. Tagging over it makes it binding, which is the one outcome this whole switch exists to
prevent.

The heaviest of them, because it decides whether a version change is survivable at all:
[how a pod moves between versions](https://github.com/sempods/sempods-spec/issues/21) without changing
the IRIs it has already published. A pod's data is cited from elsewhere on the web, and the
citations are the point — so a version change cannot move the pod to a new address.

**That is a principle this specification does not yet require.** `SPS-CORE-009` looks like it says
so and does not: it makes minting independent of a request's `Host` header, which a pod could
satisfy while changing its publicly known address. Nothing else states it either — `Published IRIs
never change` above covers module IRIs and vocabulary terms, not a pod's resources. Issue #21
carries the gap; until it closes, the constraint is the project's intent rather than its
contract.

## How a change is made

1. **An issue first**, describing the change and the rationale. Specification changes need a written
   rationale because other implementations depend on them — this is the rule the reference
   implementation's `CONTRIBUTING.md` already states, and it is the reason this repository exists
   separately.
2. **A pull request** carrying the text change, the requirement-ID additions or withdrawals, and the
   OpenAPI change if the HTTP surface moved. The three are one change, never three.
3. **Running code beats a good argument.** A requirement that no implementation has ever satisfied is
   a proposal, not a specification. A change is adopted more readily when something already runs it —
   the same bar `NAMESPACE.md` sets for adopting a vocabulary term.
4. **Merge.** Squash, linear history, signed off.

### Withdrawing a requirement

A requirement is never deleted. It is marked `withdrawn`, keeps its ID, states the version it was
withdrawn in, and names what replaces it if anything does. The ID stays out of circulation forever.

### Deleting and renumbering, before `0.1`

**Until `0.1` is tagged a requirement may be deleted outright, identifiers may be renumbered, and a
requirement whose meaning changes may keep its identifier rather than be withdrawn for a successor.
After the tag, none of the three ever again.**

**The window closes earlier if adoption arrives first.** The tag now waits for the blockers above,
so a second implementation or an external client can appear while it is still open — and the moment
one does, the fact this rests on stops being true: there *is* somebody citing these identifiers, and
renumbering would retarget their tests silently. The relaxation ends when the first external
dependency appears or when `0.1` is tagged, whichever is sooner — which makes it a different event
from the switch to prescriptive above, resting on a different fact. That switch is a promise this
project makes about its own text and only the tag makes it; this one is about whether anybody is
citing the identifiers, and somebody outside can answer that first. Permanence buys exactly one thing: an
identifier stays safe to cite from a conformance report this project never sees. Nothing has been
published as binding yet, so no such report exists — and withdrawing pays the rule's full price,
a chapter carrying text that was wrong from the day it was written, for a promise nobody was given.

What the window is not is a licence to delete whatever is inconvenient. Deletion is for a statement
that should never have been written — one whose subject is not this specification's, or that the
thing this specification describes cannot satisfy on its own. Everything else is withdrawn, in the
window as after it.

A number freed by a deletion returns to the pool while the window is open — renumbering that could
not reuse a freed number would not be renumbering. The three permissions are one fact seen three
ways: an identifier does not yet stand for a fixed statement, because nothing has been told to rely
on it standing for one.

The consumer that holds identifiers today is the reference implementation, and re-vendoring
`requirements.json` there is not enough. It cites identifiers in prose and in code comments, and its
`checkDocLinks` validates them by *existence* against the vendored index — so a citation of a number
that was deleted and later reused goes on passing while pointing at a different obligation. That is
the one failure nothing downstream can see, and it is the reason reuse is bounded by this window
rather than merely inconvenient. A change that deletes, renumbers or reuses therefore carries the
downstream sweep with it: re-vendor the index, and read every citation of an affected identifier.
Both belong to the change that caused it, not to whoever finds the mismatch later.

`.github/scripts/check-requirements.py` carries the matching exception, and it closes on its own
rather than by memory. The relaxation holds only while the repository has no `0.1` tag **and** the
script still declares the pre-`0.1` specification version, matched exactly rather than by its `-dev`
suffix — `0.2-dev` is a later version, not a second window. A checkout that cannot establish whether
the tag exists, a shallow clone with no tag refs to read, counts as tagged: the permissive answer is
not the one to give a question that was never asked. Tagging ends the window whether or not anyone
remembers this paragraph, and a tag with a stale version is reported rather than absorbed.

What the script watches is not only whether an identifier disappeared. A requirement that keeps its
identifier and says something else is the same permission seen from the other side, and it is
reported while the window is open and refused after it closes — a withdrawal, which keeps the
original text and adds the preamble in front of it, being the one in-place edit the rule prescribes
and therefore the one it does not refuse.

## Who decides

One maintainer today (`@haed`). That is a fact, not a design: a specification governed by one person
is a specification that a second implementer has to trust rather than participate in, and the fix is
a second implementer, not a governance document written in advance for a body that does not exist.

Until then: the process above is followed publicly, the rationale is written down, and a disagreement
is settled in an issue where anyone can read it.

## What this repository will not do

- **No versioned namespace.** The vocabulary IRI does not carry a version. A versioned namespace
  would invalidate stored data on every revision, which is exactly what the stability guarantees
  exist to prevent.
- **No specification change without an implementation path.** If nobody can say how an
  implementation would satisfy a requirement, it is not ready to be one.
- **Nothing strategic, commercial or personal.** This repository is public. Technical milestones
  belong here; the business around them does not.
