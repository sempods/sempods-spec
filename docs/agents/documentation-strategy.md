# Documentation strategy

How writing is organised in this repository, and — more importantly — when something should **not**
be written at all. Read this before writing or editing any `*.md`, which here means before writing
anything.

## The five types

The reference implementation has four. This repository has those four plus the one it exists for.

```
spec/**                     NORMATIVE TEXT. Prescriptive: it says what an implementation MUST do.
                            Neither IST nor SOLL — it does not describe a system, it constrains
                            every system claiming the name. Every normative statement carries a
                            requirement ID. See spec-authoring.md.

vision.md                   The vision. Why this exists and where it is going. Independent of what
                            is specified. Changes rarely.

concepts/<topic>.md         The high-level concept for one topic — the reasoning behind a chapter,
                            the trade-offs considered, what was rejected and why. It is what keeps
                            the normative text short: the chapter says what MUST happen, the
                            concept says why that shape and not another.

roadmaps/<milestone>.md     Temporary. The breakdown and status of one milestone. Links to its
                            concept instead of repeating it. Dissolved when the milestone ships.

<topic>.md, <area>/         IST documentation — about this repository itself, not about pods. The
                            governance process, the tooling. Rare here, and that is correct.
```

### Where the types differ from the implementation repository

**The source of truth is inverted.** There, the code is right and a document that disagrees is a
bug. Here the specification is right and an implementation that disagrees is the bug. What the
`0.1` tag still changes is whether the text may move, not who wins —
[`../../GOVERNANCE.md`](../../GOVERNANCE.md) is the authority.

**A concept is worth more here.** In an implementation, reasoning can hide in a code comment beside
the thing it explains. In a specification there is no such place: the normative text must not carry
the argument for itself, or an implementer cannot tell the requirement from the justification. So
the argument goes in `concepts/` and the chapter links to it.

### They nest

The same types may appear under any `docs/` directory. Today there is one. A document is written at
the **narrowest** level where it holds, and every document is reachable through at least one
`AGENTS.md` pointer.

## The writing rules

**1. Normative text is prescriptive; everything else is IST or SOLL, and never both in one
section.** Mark the section, or put the marker in the title. An aspiration written in the indicative
reads as a description, and a reader has no way to tell it apart.

**2. Name the standard; do not re-explain it.** A chapter states which RFC it profiles and describes
the deviation from it. Restating RFC 9110 in the specification's own words is how a specification
becomes both long and wrong — the copy drifts from the original and now two documents disagree about
something neither of them owns. The reference implementation's LOD-CRUD documentation already
follows this rule and is the model: *"Standards are named, not re-explained."*

**3. Short, direct, plain.** Take the shortest wording that is still correct.

- **Say what the thing is**, not what it is not, and drop the rhetorical shape. `Make context
  management a module, and let one area span both halves` — not `Stop forbidding an area from
  spanning core and a module`. Holds for headings, prose and commit subjects alike. What it targets
  is negation used as rhetoric; a real prohibition stays as it is, because `MUST NOT` in a
  requirement and the `never` in an invariant are already the shortest correct wording.
- **No history, no decision log**, no "this used to be X" — that is what the commit message is for.
  The one exception is a rationale a future reader genuinely needs in order not to undo it, and in
  this repository that rationale usually belongs in `concepts/` rather than inline.
- **Name the standard** instead of re-explaining it — rule 2, which is this rule applied to a
  document somebody else owns.

**4. Behaviour that follows the standard needs no requirement.** Do not write `SPS-CRUD-0nn: the
server MUST return 405 with an Allow header` when RFC 9110 already says so and the chapter has
already said it profiles RFC 9110. Write the requirement for the *deviation*, and for the place
where a reader would otherwise guess.

**5. When a deviation becomes ordinary, its text shrinks or goes.** A special case that folds into
the normal path takes its explanation with it, and deleting that explanation is a correct change.
*Replacing* it is the failure mode: a paragraph on why the thing is now ordinary is a longer way of
writing nothing. The requirement itself is **withdrawn**, never deleted, because its ID is cited
elsewhere. Until the `0.1` tag there is one exception, stated in
[`../../GOVERNANCE.md`](../../GOVERNANCE.md) and applied in
[`spec-authoring.md`](spec-authoring.md) §5.

**6. A normative statement without an ID is not normative.** It is background, and a reader is
entitled to treat it that way. If it matters, give it an ID; if it does not, say it in the concept
instead.

**7. No stub chapters.** A chapter exists when it is written. Until then it is a row with a status
in `spec/README.md`. An empty file that says "TBD" is a promise the repository cannot keep and a
link target that lies.

**8. This repository is public.** Nothing strategic, commercial or personal goes into it — roadmaps
included. Technical milestones are public; the business around them is not.

**9. Show the case.** Where a rule has a consequence a reader would otherwise have to derive, write
the consequence out instead of hedging the prose around it — one concrete case is shorter than the
hedging it replaces, and it is the half a reader remembers. It belongs in the chapter's prose, in a
`concepts/` document, or in access control best in a worked example under
[`../../examples/`](../../examples/README.md), the one place a case is machine-checked. What binds
stays in the requirement: the condition fixing where an obligation applies
([`SPS-MEDIA-002`](../../spec/modules/media.md#SPS-MEDIA-002)) and the case it reaches
([`SPS-CTX-030`](../../spec/core/contexts.md#SPS-CTX-030)) are the obligation itself. What a
requirement must not carry is its own argument — [`spec-authoring.md`](spec-authoring.md)
§"Pitfalls".

**10. Length is a budget, not an entitlement.** Add a paragraph, look for one to delete — usually
the one the new paragraph made redundant — and treat a section that has doubled since it was written
as one to cut rather than extend. The budget buys prose: an explanation, a rationale, an example
that no longer earns its place. It never buys a requirement. Rule 5 owns what becomes of one —
withdrawn, or deleted while the pre-`0.1` window is open — and neither is ever done because a
section got long.

## Roadmaps

A roadmap is a working document with a defined end. It exists to get one milestone specified in a
focused way, and it is dissolved afterwards.

**It stays thin.** The concept carries the target state and the reasoning permanently, so the roadmap
does not repeat them — it links. What belongs in a roadmap is the breakdown, the status, and the
open decisions.

**Progress is tracked in place.** Completed items stay in the file, marked done, until the whole
milestone is consolidated. They are not pruned one at a time — a reader has to be able to see what
has already been settled. Each roadmap repeats this rule in its own header so a reviewer who only
sees the diff reads it too.

The item is ticked **in the same commit as the text that finishes it**. A separate bookkeeping pass
is a pass that gets skipped.

**Lifecycle:** concept (SOLL) → derive a roadmap → write, ticking as you go → milestone done →
[`roadmap-lifecycle.md`](roadmap-lifecycle.md): rewrite the concept's SOLL section as IST, sweep
links, delete the roadmap.

**Tracking issues hold no state.** A milestone may have a GitHub issue announcing it, carrying a
title and a link to the roadmap file — never a copy of the checklist.

## Definition of done

A change to the specification is not finished until, **in the same change**:

- every new normative statement carries a requirement ID, and no ID was reused or renumbered —
  unless the pre-`0.1` window is open and the change says so out loud;
- a withdrawn requirement is marked withdrawn rather than removed, and names its successor;
- the OpenAPI description agrees with the chapter, where the change touched the HTTP surface;
- the corresponding roadmap item is ticked;
- `spec/README.md`'s chapter table still reflects reality;
- every relative link resolves, and any new document is reachable from an `AGENTS.md`.

[`documentation-sync.md`](documentation-sync.md) is the procedure that walks this list.

`lychee --offline --include-fragments --no-progress --exclude-path site .` checks the mechanical half. The rest is a judgement, which is why
it is written down here rather than automated.
