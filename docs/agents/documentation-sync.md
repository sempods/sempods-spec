# Procedure: sync the documentation

Bring the repository back into internal agreement after a change. This is the working half of the
definition of done in [`documentation-strategy.md`](documentation-strategy.md) — run it before
proposing a commit, not as a separate pass later.

Wrapped for Claude Code as the `sync-docs` skill; any other agent can be pointed at this file
directly.

## 1. What changed

```bash
git status --short                        # everything, new and untracked files included
git diff HEAD                             # the change itself, staged or not
git ls-files --others --exclude-standard  # the new files, which no diff shows — read them
```

Against `HEAD`, not the index. A bare `git diff` compares the working tree with the index, so a
change that has already been staged shows nothing — and staging before proposing a commit is exactly
what this repository's procedures ask for.

The third command exists because the second cannot see an untracked file at all. A new chapter
arrives as an untracked file, and a chapter is the thing this procedure most needs to look at.

## 2. Requirement IDs

The half that has no equivalent in the reference implementation, and the half that is expensive to
get wrong.

- **Every new normative statement has an ID**, and the ID is higher than every ID ever issued in its
  area — withdrawn ones included. Check against the text, not against memory:

  ```bash
  grep -rho 'SPS-[A-Z]*-[0-9]\{3\}' spec/ | sort -u
  ```

- **No ID was reused, renumbered or deleted.** A deleted ID is the failure mode this step exists to
  catch, and `git diff` shows it as an ordinary removed line.

  ```bash
  git diff HEAD -- spec/ | grep '^-' | grep -o 'SPS-[A-Z]*-[0-9]\{3\}' | sort -u
  ```

  Every ID that appears there must also appear in the new text — as a withdrawal, or unchanged
  somewhere else in the diff. One that does not is a break, with one dated exception:
  [`../../GOVERNANCE.md`](../../GOVERNANCE.md) permits deletion and renumbering until `0.1` is
  tagged. Inside that window the question is not whether the ID is gone but whether the change says
  it is gone and why. The requirements checker prints such a deletion as a `notice:` line rather
  than failing, so run it and read what it let through.

- **Every anchor matches its ID**, character for character. A mismatched anchor makes a citation
  resolve to the top of the page rather than fail, so a reader sees the wrong requirement and is
  given no sign of it. The link check in CI runs with `--include-fragments` for exactly this, and it
  is the only automated check standing between an ID and a wrong citation — so it is worth running
  before the push rather than after it.

[`spec-authoring.md`](spec-authoring.md) has the rules; this step only verifies them.

## 3. The chapter map

[`../../spec/README.md`](../../spec/README.md) carries the chapter table with a status per chapter.
A new chapter changes a row from planned to present; a chapter that grew a section usually changes
nothing. The table is read by every visitor before anything else, so a stale row is the most
expensive kind of stale text here.

Rule 7 of the strategy applies while you are in there: a planned chapter is a row, not a link, and
not an empty file.

## 4. OpenAPI

If the change moved the HTTP surface — a route, a parameter, a status code, a media type — the
OpenAPI description moves in the **same commit**. The two are one change.

The description is hand-written and normative; it is not generated from any implementation. So
nothing will tell you it has gone stale except this step.

## 5. Concepts

Did the change alter a trade-off, or settle something a concept listed as open? Then the concept
changes too. A concept whose SOLL section has come true is rewritten as IST, not deleted — see
[`roadmap-lifecycle.md`](roadmap-lifecycle.md).

The reverse also counts: if a requirement now carries its own justification, move the justification
out. That is pitfall two in [`spec-authoring.md`](spec-authoring.md).

## 6. Roadmap

If a roadmap covers this work, tick the item **now**, in this change. Leave the completed items in
place; the roadmap is dissolved as a whole, later.

## 7. Outbound and inbound links

- A new document is reachable from at least one `AGENTS.md`.
- A deleted or moved document is gone from every `AGENTS.md` and every cross-link.
- **A chapter that moved here from the reference implementation leaves nothing behind.** The
  document there is deleted, and what pointed at it points at a requirement ID here. Two copies
  means one of them is wrong.

```bash
lychee --offline --include-fragments --no-progress --exclude-path site .
```

## 8. Report

Name what was updated, what was **deleted** and why, which requirement IDs were added or withdrawn,
and what was deliberately left alone. "No change needed, because the behaviour follows the standard
the chapter already profiles" is a complete and correct report.
