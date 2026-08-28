# Procedure: consolidate a roadmap

Retire a roadmap whose milestone has shipped. The concept absorbs what is now true, the roadmap file
goes away, and nothing is left pointing at it.

Read [`documentation-strategy.md`](documentation-strategy.md) first — this procedure applies its
rules and does not restate them. Wrapped for Claude Code as the `consolidate-roadmap` skill; any
other agent can be pointed at this file directly.

**Run this when the milestone is done, not before.** A roadmap with open items keeps its completed
entries — that is the point of it.

## 1. Inventory

Read the roadmap. For each item, decide **done / partially done / open**, with evidence rather than
the checkbox: does the chapter exist, does it carry requirement IDs, does the OpenAPI description
cover the routes it names, does the conformance suite reference those IDs.

```bash
git log --oneline --grep=<keyword>
grep -rn 'SPS-<AREA>-' spec/
```

A ticked item whose chapter is not there is the failure mode this step exists to catch. So is a
chapter that exists but carries no requirement IDs: prose about a surface is not a specification of
it.

## 2. Rewrite the concept

Open the concept the roadmap links to. For every item that is done, its SOLL section becomes IST:
present tense, describing what the specification *says*, not what was written.

- Move a section from SOLL to IST, or merge it into an existing IST section — do not leave a SOLL
  section that has come true.
- Keep the reasoning that a future reader needs to not undo the decision. Drop the reasoning that
  only explains the sequence of work.
- If the concept is now entirely IST and small enough, it may collapse into the chapter it points
  at — but only the *reasoning* collapses into the chapter's prose, never into a requirement.
  Deleting a concept that has nothing left to say is correct.

If the roadmap carried concept-level content the concept never had — a trade-off, a rejected
alternative, a boundary — lift it now, at concept level. Drop per-iteration step lists, file
manifests and dated banners.

## 3. Handle what is left

- An item still open that belongs to **this** milestone means the milestone is not done, and this
  procedure is premature. Stop here: the file keeps every entry it has, completed ones included.
  Slimming it down to the open items is the one thing a running roadmap must never have done to it.
- An item still open that belongs to a **different** milestone: move it to that roadmap, or file a
  new one for it, rephrased as work still to do.
- A deviation that survives: it belongs in the chapter, called out as a deviation with the reason
  the contract looks that way. This is the one case where rule 3 of the strategy yields.
- A minor open item that deserves no roadmap section: a GitHub issue, not a `TODO` in the text. A
  specification with a `TODO` in it is a specification an implementer cannot rely on.

## 4. Delete

Delete the roadmap file. A consolidation that reaches this step is one where nothing is left to
carry: what was done lives in the concept and the chapters, and what was open has moved to the
roadmap that owns it.

## 5. Sweep

- Search the sources for the roadmap's filename. `git grep` rather than `grep -r`, because tracked
  files are exactly the right scope.

  ```bash
  git grep -n '<roadmap-filename>' -- '*.md' '*.yaml' '*.yml'
  ```

  Update or remove every hit.
- Check every `AGENTS.md` from the root down: remove entries for the retired roadmap, add entries
  for any new chapter or concept.
- Check [`../../spec/README.md`](../../spec/README.md). A shipped milestone almost always moves a
  row in the chapter table, and that table is what a visitor reads first.
- Check whether the reference implementation still points at documentation this milestone moved
  here. That sweep crosses a repository boundary, so nothing local will catch it.
- Run `lychee --offline --include-fragments --no-progress --exclude-path site .`.

## 6. Report — do not commit

A tight summary: what was deleted, what was rewritten, which content moved into which document,
which items remain open, which links were repaired. Stage the changes and propose a commit message;
the commit itself is the maintainer's.

## Pitfalls

- **Do not paraphrase the roadmap into the concept.** The concept describes the state of things in
  the present tense; the roadmap described a plan. Rewrite, do not copy.
- **Do not drop the why.** A constraint or trade-off the roadmap explained is usually the most
  valuable thing it holds — subject to rule 3: keep what stops a reader undoing it, drop the rest.
- **Do not tidy a roadmap that is still running.** Pruning finished items from an open roadmap is
  the opposite of what this repository wants.
