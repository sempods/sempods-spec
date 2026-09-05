# AI instruction hub

The entry point for every AI agent working in this repository. It defines **how** instructions are
discovered and applied — not what the rules are. The rules live in the root
[`AGENTS.md`](../../AGENTS.md); how documents are written lives in
[`documentation-strategy.md`](documentation-strategy.md); how a normative statement is written lives
in [`spec-authoring.md`](spec-authoring.md).

Start here, then read what this file points at. It is deliberately short.

## Instruction sources, in order of specificity

1. **Root [`AGENTS.md`](../../AGENTS.md)** — the canonical rules: the inverted source-of-truth rule,
   the mission, terminology, the non-negotiable invariants, the security stance, the commit
   checklist.
2. **[`documentation-strategy.md`](documentation-strategy.md)** — the five document types and the
   rules for writing them.
3. **[`spec-authoring.md`](spec-authoring.md)** — required before writing or editing anything under
   `spec/`. The strategy says which document a thing belongs in; this says how a normative sentence
   is formed.
4. **Scoped `AGENTS.md` files** in subtrees. None exist today. A subtree without one takes the root
   file directly — that is the normal case, not a gap to fill.
5. **Tool compatibility pointers** (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`,
   `.cursor/rules/`). They route back here and add nothing of their own, with one registered
   exception below.

## Context resolution

- What governs a change is the `AGENTS.md` files on the path from the repository root **down to the
  directory of the file being changed** — those, and no others.
- **The more specific file wins** where two on that path conflict.
- Reading another repository's `AGENTS.md` for orientation is fine, and for this project it is often
  useful: the reference implementation's file carries the same invariants. It still does not govern
  an edit here, and its rule 1 on source of truth is the one that is **inverted** in this
  repository — see the root `AGENTS.md`.
- Documentation nests the same way. Any `docs/` directory may hold the same types.

## Tool directory

Every agent frontend this repository supports, and how it finds the rules. When adding one, create
its pointer file and add a row here.

| Tool | Reads | Mechanism |
|---|---|---|
| Codex | `AGENTS.md` | Native. Walks the tree itself; needs no pointer file. |
| opencode | `AGENTS.md` | Native. Same. |
| Claude Code | `CLAUDE.md` → `AGENTS.md` | Pointer. Skills in `.claude/skills/` wrap the procedures in this folder. |
| GitHub Copilot | `.github/copilot-instructions.md` | Auto-injected in isolation — see the constraint below. |
| Gemini CLI | `GEMINI.md` → `AGENTS.md` | Pointer. |
| Cursor | `.cursor/rules/sempods.mdc` → `AGENTS.md` | Pointer, `alwaysApply: true`. |

## Auto-injection constraints

Some files are loaded by their tool **in isolation** — the tool reads that one file and follows no
link out of it. A pure pointer would be useless there, so a minimal subset is duplicated inline.
This is the complete list; nothing else in this repository may duplicate rules.

| File | Injected by | What stays inline |
|---|---|---|
| `.github/copilot-instructions.md` | Copilot Chat and the Copilot coding agent | The inverted source-of-truth rule, the invariants in short form, the requirement-ID scheme, the documentation duty |

The rules for that duplication: the source of truth is always `AGENTS.md`; update it first and sync
the subset after; keep the subset minimal and let it link out for everything else.

## Shared principles

- **Keep all canonical guidance in English.** The specification text too — an implementer in another
  country reads it.
- **Link, don't duplicate.** A pointer file that grows rules is a pointer file that drifts, and so
  is a chapter that restates another chapter.
- Add a rule at the **narrowest** scope where it holds.
- A document is reachable from at least one `AGENTS.md` pointer, or it will not be read.
- **This repository has no code to check the rules against.** Everything here is judgement plus one
  link checker, which raises the cost of a sloppy edit rather than lowering it.

## Self-check

Hand this to any agent as a task:

> *"Perform the AI instruction self-check from `docs/agents/ai-instructions.md` and confirm all
> relevant instructions are loaded."*

1. Read the root `AGENTS.md` and note what it references — in particular the inverted
   source-of-truth rule and how much of this text may still move.
2. Read `docs/agents/documentation-strategy.md`.
3. If the change touches `spec/`, read `docs/agents/spec-authoring.md`.
4. For each file you intend to change, load the `AGENTS.md` files on the path from the repository
   root down to its directory — not the ones in subtrees you are not touching.
5. Confirm the tool's own pointer file, if any, still routes back here.
6. Before writing, state the rules that apply and confirm no conflict remains.

## Maintenance

- New procedure → a markdown file in this folder, tool-neutral, plus a thin
  `.claude/skills/<name>/SKILL.md` wrapper that points at it. The procedure is never written into
  the skill; every agent must be able to follow it.
- New tool → a pointer file plus a row in the tool directory.
- Retired pointer → remove the file and the row. The link checker catches what is left behind.
