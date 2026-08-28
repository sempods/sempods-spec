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
- **Requirement IDs never break, at any version.** An ID is never reassigned and never renumbered;
  a withdrawn requirement stays in the text marked `withdrawn` with a pointer to its successor.
  This is deliberately the same rule the vocabulary applies to RDF terms, and for the same reason:
  an ID ends up in other people's test suites the way a term ends up in other people's data.
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
