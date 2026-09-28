---
name: doc-review
description: Review the specification's text against its contract sources and the writing rules —
  your own change before review, a pull request, or a path (a chapter, guide or proposal). Checks
  requirement IDs and anchors, the chapter table, OpenAPI and the work record. Applies its findings
  to your own change; on a pull request or a path it reports them, and `--fix` applies them. Invoke
  on "doc review for spec/core/auth.md", "review the docs of PR 123", "sync the docs", "is the spec
  still right?", before requesting review, and after any change to a chapter, a requirement or the
  HTTP surface.
argument-hint: "[#PR | branch | path] [--fix]"
---

# doc-review

The procedure is [`docs/agents/doc-review.md`](../../../docs/agents/doc-review.md). **Read it and
follow it** for the target in `$ARGUMENTS`; with none, the target is your own branch. It is written
tool-neutrally so every agent in this repository runs the same steps, and this file deliberately
holds no copy of them.

The rules it applies are in
[`docs/agents/documentation-strategy.md`](../../../docs/agents/documentation-strategy.md), and for
anything under `spec/` also
[`docs/agents/spec-authoring.md`](../../../docs/agents/spec-authoring.md).
