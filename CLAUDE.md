# Claude Code instructions (compatibility pointer)

The canonical guidance for this repository is the root [`AGENTS.md`](AGENTS.md), reached through the
shared hub [`docs/agents/ai-instructions.md`](docs/agents/ai-instructions.md). Read both before
making a change; the hub's self-check lists what else applies.

Three things Claude Code has no automatic trigger for, so they are stated here:

- **This specification decides.** It binds implementations, not the other way round —
  [`AGENTS.md`](AGENTS.md) §"What decides here" has the two limits. Do not carry the reference
  implementation's rule across.
- **When editing any `*.md`**, also read
  [`docs/agents/documentation-strategy.md`](docs/agents/documentation-strategy.md), and — for
  anything under `spec/` — [`docs/agents/spec-authoring.md`](docs/agents/spec-authoring.md).
- **Before proposing a commit**, walk the definition of done in the documentation strategy; the
  `sync-docs` skill is the procedure.

Skills in [`.claude/skills/`](.claude/skills/) are thin wrappers. The procedures themselves live in
`docs/agents/` so every agent can follow them.
