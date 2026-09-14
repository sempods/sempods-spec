---
name: sync-docs
description: Use before proposing a commit in the sempods specification repository, to bring the
  text back into internal agreement. Verifies that no requirement ID was reused, renumbered or
  deleted, that anchors match their IDs, that the chapter table and the OpenAPI description moved
  with the chapter, and that the work record has check and documentation evidence. Invoke when the
  user says "sync the docs", "update the documentation", "is the spec still right?", or after any change to a chapter, a
  requirement, or the HTTP surface.
---

# sync-docs

The procedure is
[`docs/agents/documentation-sync.md`](../../../docs/agents/documentation-sync.md). **Read it and
follow it** — it is written tool-neutrally so every agent in this repository runs the same steps,
and this file deliberately holds no copy of them.

The rules it applies are in
[`docs/agents/documentation-strategy.md`](../../../docs/agents/documentation-strategy.md), and for
anything under `spec/` also
[`docs/agents/spec-authoring.md`](../../../docs/agents/spec-authoring.md).
