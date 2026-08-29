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
- **Requirement IDs never break, from `0.1` on.** An ID is never reassigned and never renumbered;
  a withdrawn requirement stays in the text marked `withdrawn` with a pointer to its successor.
  This is deliberately the same rule the vocabulary applies to RDF terms, and for the same reason:
  an ID ends up in other people's test suites the way a term ends up in other people's data.
  Before the tag there are no such test suites, and §"Deleting and renumbering, before `0.1`" says
  what follows from that.
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
After the tag, none of the three ever again.** This is the same dated event as the switch from
descriptive to prescriptive, and it rests on the same fact. Permanence buys exactly one thing: an
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
rather than by memory: the relaxation holds only while the repository has no `0.1` tag **and** the
script still declares the pre-`0.1` specification version, matched exactly rather than by its `-dev`
suffix. `0.2-dev` is a later version, not a second window. Tagging ends it whether or not anyone
remembers this paragraph.

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
