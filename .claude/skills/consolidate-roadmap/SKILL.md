---
name: consolidate-roadmap
description: Use when a specification milestone has shipped and its roadmap should be retired into
  the permanent documentation. Audits the roadmap against the chapters, rewrites the linked
  concept's SOLL section as IST, deletes the roadmap file, and sweeps every reference to it in the
  docs, the AGENTS.md files and the chapter table. Invoke when the user says "let's consolidate",
  "audit the roadmap", "is this still open?", after a milestone ships, or before a new one starts.
  Do NOT use to tidy a roadmap that is still running — completed items stay in place until the whole
  milestone is done.
---

# consolidate-roadmap

The procedure is [`docs/agents/roadmap-lifecycle.md`](../../../docs/agents/roadmap-lifecycle.md).
**Read it and follow it** — it is written tool-neutrally so every agent in this repository runs the
same steps, and this file deliberately holds no copy of them.

Context you need alongside it:
[`docs/agents/documentation-strategy.md`](../../../docs/agents/documentation-strategy.md) for the
five document types and the writing rules.

Three things worth knowing before you start:

- **Run this only when the milestone is done.** A roadmap with open items keeps its completed
  entries; pruning them individually is the opposite of what this repository wants.
- **Evidence, not checkboxes.** A ticked item whose chapter carries no requirement IDs is not done —
  prose about a surface is not a specification of it.
- **Report, do not commit.** Stage the changes and propose a commit message.
