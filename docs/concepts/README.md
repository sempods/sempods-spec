# Concepts

A concept document owns one topic. It says what the topic *is*, what the specification says about it
today, and what the target state is — and it links to the roadmap implementing that target and to
the chapters that already carry it.

## Why a concept matters more in a specification repository

In an implementation, the reasoning behind a decision can sit in a code comment beside the thing it
explains. Here there is no such place. The normative text must not carry the argument for itself, or
an implementer cannot tell the requirement from the justification — that is pitfall two in
[`../agents/spec-authoring.md`](../agents/spec-authoring.md).

So the argument lives here, and the chapter links to it. "The server MUST reject `SERVICE` anywhere
in a query" is the requirement; *why* — that federated queries are an SSRF surface and that the
sandbox has to be enforceable server-side — is a concept.

A concept outlives the roadmaps that implement it. Where a roadmap is dissolved by design, a
concept's SOLL section is rewritten as IST when it comes true, and the document stays. The one
exception is a concept with nothing left to say: if it is entirely IST and small enough, its
reasoning folds into the chapter's prose and it is deleted — see
[`../agents/roadmap-lifecycle.md`](../agents/roadmap-lifecycle.md) §2. It never folds into a
requirement.

## Here today

- [`access-control.md`](access-control.md) — at what granularity access is decided, and why
  [`contexts`](../../spec/core/contexts.md) and [`grants`](../../spec/core/grants.md) answer that
  question differently from [`lod-crud`](../../spec/core/lod-crud.md). Defines the target
  resource-first ACP profile, the optional multi-context constraint, and the closed matcher model
  for enterprise groups and audiences — and its load-bearing specification impact.

Reasoning that belongs to another document is not repeated here:
[`../../GOVERNANCE.md`](../../GOVERNANCE.md) owns versioning and the descriptive-to-prescriptive
switch, [`../../spec/README.md`](../../spec/README.md) the core/module split, and
[`../agents/spec-authoring.md`](../agents/spec-authoring.md) the requirement scheme. A concept
is written for the first chapter whose content needs one, not in advance.

## Template

```markdown
# <Topic> (Concept)

## Purpose

What this topic is, and why it exists in the shape it does. Two or three paragraphs. Sections below
are marked **IST** (specified today, verifiable against the chapters) or **SOLL** (target state).

## <Aspect> (IST)

What the specification says today. Present tense. Links to the chapters and requirement IDs that
carry the detail.

## <Aspect> (SOLL)

The target state, and the constraint or trade-off behind it. Not a plan — a plan is a roadmap.

## Rejected alternatives

What was considered and not chosen, and what it would have cost. This is the section that stops a
future reader reopening a settled question, and it is the reason a concept is worth keeping.

## Not in scope

What this concept deliberately does not cover, where a reader might expect it to.

## See also

- Chapter: `../../spec/core/<chapter>.md`
- Roadmap: `../roadmaps/<milestone>.md`   ← while one is running
```

## Rules

- **Never mix IST and SOLL in one section.** Mark each section, or the title if the whole document
  is one or the other.
- The concept carries the reasoning permanently. A roadmap links here rather than repeating it.
- Do not restate the chapters. Link to them, by requirement ID where the point is one requirement.
- No history and no decision log. Keep only the reasoning a future reader needs in order not to undo
  the decision — which, for a rejected alternative, includes what it would have cost.
