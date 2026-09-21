# Governance

How this specification is versioned and published, how its development text binds implementations,
and how a change is adopted.

## Versioning

**Core and each module have their own version lines**, independent of implementation releases.
An implementation declares the core and module versions it supports through the existing
conformance discovery contract; its own release number need not match any of them. Publication
records exact source revisions without adding a protocol negotiation mechanism.

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

### Publication identities and corrections

A core publication uses a tag such as `0.1`; a module publication uses
`module-<name>-<version>`, such as `module-media-0.2`. Each tag identifies one immutable repository
commit containing the matching chapters, OpenAPI, vocabulary and generated index. The release notes
record the complete core/module version map and which component is being published. Other components
in that snapshot keep their own status and version; their presence does not release a `-dev` version.
Publishing a module does not advance the core version.

While the version line is `0.x`, a contract change uses the next minor version, such as `0.2`.
Purely editorial corrections with no change to obligations, capabilities or observable behavior may
use `0.1.1`, then `0.1.2`. The first publication of a minor is `0.1`, not a separate `0.1.0` release.
A purported clarification that changes what passes or fails is a contract change. Patch publication
does not relax the existing requirement-identifier and withdrawal rules. The affected
component advances; the release notes state compatibility and any affected requirement IDs.
Shared vocabulary or cross-component changes identify every affected component and coordinate their
versions. This is publication policy, not a promise of wire-level backward compatibility.

Published tags are never moved or reused, including after a discovered error. Corrections require a
new reviewed commit and publication. A withdrawn distribution remains identifiable: mark its GitHub
Release as withdrawn, explain the reason and link a replacement when available. Preserve the tag,
commit, source artifacts and original notes; append a dated withdrawal notice rather than silently
replacing the contract. Requirement withdrawal remains the separate process below.

**GitHub Releases is the canonical release-note source.** Each published entry identifies its tag,
full commit, component versions, changes, affected requirements, compatibility/migration implications
and publication/check evidence. There is no parallel maintained changelog. Draft notes are reviewed
with the publication issue before the release is published.

`0.1-dev` and later `-dev` labels are mutable development labels, not immutable revisions. Cite the
full commit alongside a development label. The development website follows `main`; every build
identifies its source commit. A website deployment neither creates a release nor first makes the
normative text binding. Published versions and their source archives are reached through
[GitHub Releases](https://github.com/sempods/sempods-spec/releases).

### Reader publication boundary

The site renders normative chapters, vocabulary, governance and the informative vision. Proposals,
guides, example explanations and contributor instructions remain on GitHub, linked at the same
commit as the rendered source. They do not become normative through a link or a passing example.
[Repository checks](docs/guides/repository-checks.md) is the canonical explanation of check evidence.
Implementation release status and implementation conformance reports stay with implementations.

The [revision guide](docs/guides/specification-revisions.md) explains consumption; the
[publication procedure](docs/agents/publish-specification.md) applies this policy. Resource-IRI
continuity and protocol version negotiation remain
[#21](https://github.com/sempods/sempods-spec/issues/21)'s separate contract decisions.

## What the tag changes, and what it no longer does

This is the one piece of process worth stating precisely, because it silently never happens
otherwise.

**The text decides.** A behaviour change is settled here first. An implementation that disagrees
with the specification revision it claims to satisfy has a defect — the reference implementation
included. Its existing behavior does not decide the contract.

**Identifiers freeze at the tag, or at the first adopter, whichever comes first.** Until then a
requirement may be deleted, an identifier renumbered, and a requirement that changes meaning may
keep its identifier. That freedom rests on there being nobody outside this project to promise to,
which is why this half can end without a tag: somebody outside can end it.

### When `0.1` gets tagged

**The current version is `0.1-dev`, and it is not close to a tag.** That is a decision, not a
delay.

A tag is a promise to somebody. There is nobody yet: no second implementation, no client outside
this project whose build breaks when a requirement moves. Tagging before there is buys nothing and
spends the freedom to still be wrong about the shape.

So the trigger is not a date. **`0.1` is tagged when two things hold at once:** somebody is there
to promise to — a second implementation, or a client outside this project that depends on the
contract — **and** everything below is settled. Adoption is what makes the tag worth cutting; the
open questions are what makes it possible. Neither is sufficient alone, and adoption arriving first
is a reason to close the rest, not to tag around it.

Until then `0.1-dev` is what an implementation declares, what the conformance endpoint reports, and
what this document means wherever it says "before the tag". It is the honest answer to "which
version is this?" — more honest than a `0.1` that gets edited the week after it is cut.

### What has to be settled first

The [0.1 milestone](https://github.com/sempods/sempods-spec/milestone/1) is the sole maintained list
of release conditions. Every condition there needs its accepted deliverable and evidence before
the tag; completing a preparation issue does not adopt the contract it prepares. Deferring or
removing a condition requires an explicit reviewed governance decision and matching milestone
changes. Keeping one list prevents conflicting release gates.

The external-adopter trigger in §"When `0.1` gets tagged" also remains necessary. After-`0.1`
work and announcement planning do not become release conditions merely by being tracked in the
same repository.

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

## Contract sources

The normative development text already binds under the limits above. `spec/` owns the protocol
requirements and the standards profiles it incorporates.
[`SPS-CORE-021`](spec/core/index.md#SPS-CORE-021) bounds incorporation by the chapter's SPS
requirements; the reference supplies behavior within that scope. Selecting additional capabilities
or changing a deviation is a normative change under the adoption process below.
[`SPS-CORE-002`](spec/core/index.md#SPS-CORE-002) owns the identifier convention; informative
references create no obligations. [Spec authoring](docs/agents/spec-authoring.md#standards-incorporation)
defines how a profile is declared and reviewed.

`openapi/` is the normative HTTP view of those chapters; where it disagrees, the chapter wins and
the description needs correction. `vocabulary/` owns the RDF terms and their stability guarantees.
Resolve a conflict between a chapter and the vocabulary explicitly in an issue and a coordinated
normative PR; silently choosing one changes the other contract view. `requirements.json` is a
generated lookup index, not an independent source of obligations. Proposal and guide prose cannot
change any of these sources.

## How a change is made

1. **Establish the work record.** An issue states the problem, rationale, scope and verifiable
   acceptance. Use the [issue-planning rules](docs/agents/documentation-strategy.md#issue-planning),
   including their bounded bot-update and private-security exceptions, and the
   [issue-work procedure](docs/agents/issue-work.md).
2. **Propose where useful.** Substantial design may have a document under `docs/proposals/` linked
   to its issue. A proposal-document merge records a non-normative design; it adopts no protocol
   change. Evaluate proposed requirements against [the vision](docs/vision.md).
3. **Adopt normatively.** A reviewed PR changes the affected chapters, requirement IDs, standards
   profile and corresponding OpenAPI, vocabulary and index together. Record compatibility impact,
   applicable checks and per-PR documentation evidence. An implementation path is required; an
   implementation's delivery or conformance report does not determine adoption.
4. **Merge.** Squash, linear history, signed off. Record the proposal's disposition and adoption
   links, and update useful maintained guides. Close the work record only against its acceptance.
5. **Publish separately.** A version tag identifies the published revision, with release notes
   describing its changes. Publication follows the versioning and release conditions above;
   it is not what first makes the development text prescriptive.

### Implementation follow-up

The reference implementation may lag behind the specification. Opening or merging an implementation
PR, including one that refreshes its vendored requirement index, is not a prerequisite for
specification adoption. An implementation path is still required; conformance claims apply only to
the revisions the implementation actually satisfies.

Record known downstream effects and remaining work in the specification issue or PR. Normally open
or reuse a linked implementation issue for behavior, documentation, index and citation changes. If
there is no such issue, keep the remaining work visible in the specification record. A follow-up
issue tracks work; it does not establish implementation conformance or block completion of the
separately scoped specification change.

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
from who wins an argument, resting on a different fact. That one is a promise this project makes
about its own text and it holds now; this one is about whether anybody is
citing the identifiers, and somebody outside can answer that first. Permanence buys exactly one thing: an
identifier stays safe to cite from a conformance report this project never sees. Nobody outside is
citing these identifiers yet, so no such report exists — and withdrawing pays the rule's full price,
a chapter carrying text that was wrong from the day it was written, for a promise nobody was given.

What the window is not is a licence to delete whatever is inconvenient. Deletion is for a statement
that should never have been written — one whose subject is not this specification's, or that the
thing this specification describes cannot satisfy on its own — and for one a later requirement has
swallowed whole, where a withdrawal notice would preserve nothing but the contradiction. Everything
else is withdrawn, in the window as after it.

The third case arrives while a chapter is being written rather than years later: a general rule
lands, and the two requirements that each stated it for one case are left restating it. Keeping
those as withdrawn text leaves a reader reconciling three statements where one holds, and the
withdrawal preserves a promise nobody was given.

A number freed by a deletion returns to the pool while the window is open — renumbering that could
not reuse a freed number would not be renumbering. The three permissions are one fact seen three
ways: an identifier does not yet stand for a fixed statement, because nothing has been told to rely
on it standing for one.

The consumer that holds identifiers today is the reference implementation, and re-vendoring
`requirements.json` there is not enough. It cites identifiers in prose and in code comments, and its
`checkDocLinks` validates them by *existence* against the vendored index — so a citation of a number
that was deleted and later reused goes on passing while pointing at a different obligation. That is
the one failure nothing downstream can see, and it is the reason reuse is bounded by this window
rather than merely inconvenient. For deleted, renumbered, reused or redefined identifiers, identify
the affected downstream citations and track the index refresh and citation corrections under
[Implementation follow-up](#implementation-follow-up). Complete them when updating the implementation
to that specification revision; a stale index is not evidence of conformance to the newer contract.

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
