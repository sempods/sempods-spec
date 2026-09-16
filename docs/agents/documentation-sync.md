# Procedure: sync the documentation

Bring the repository back into internal agreement after a change. This is the working half of the
definition of done in [`documentation-strategy.md`](documentation-strategy.md) — run it before
requesting review on every PR, including partial work.

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

- **Every new sempods-authored obligation has an ID**, and the ID is higher than every ID ever
  issued in its area — withdrawn ones included. Check against the text, not against memory:

  ```bash
  grep -rho 'SPS-[A-Z]*-[0-9]\{3\}' spec/ | sort -u
  ```

- **No ID was reused, renumbered or deleted.** A deleted ID is the failure mode this step exists to
  catch, and `git diff` shows it as an ordinary removed line.

  ```bash
  git diff HEAD -- spec/ | grep '^-' | grep -o 'SPS-[A-Z]*-[0-9]\{3\}' | sort -u
  ```

  Every ID that appears there must also appear in the new text — as a withdrawal, or unchanged
  somewhere else in the diff. One that does not is a break, with one exception:
  [`../../GOVERNANCE.md`](../../GOVERNANCE.md) permits deletion and renumbering while its window is
  open, and says what closes it. Inside that window the question is not whether the ID is gone but whether the change says
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

## 5. Contract sources and informative documents

Check the affected chapter's standards incorporation, OpenAPI, vocabulary and generated index
against [governance](../../GOVERNANCE.md#contract-sources). Review semantic effects, not just IDs:
an edit to the standards profile can change inherited obligations without changing an identifier.

Update affected proposals and maintained guides for this PR's delivered scope. Record proposal
disposition and adoption links; for partial adoption, keep remaining scope visible in its issue.
Reference the revision a guide explains. Reduce redundant text while preserving useful explanation
and required evidence. A proposal merge does not change the normative contract.

Apply [the writing rules](documentation-strategy.md#the-writing-rules) to prose, docstrings and
code comments:

- Can each sentence be understood on first reading? Split dense sentences and use familiar words.
- Would a concrete input and outcome make a consequence clearer? Keep the example informative and
  link its requirement.
- Does explanatory text repeat a contract? Link its source and explain only what the reader needs here.
- Did the edit make any text redundant? Remove it; keep useful explanations and examples.
- For wording-only edits, compare actors, obligation levels, conditions, exceptions and outcomes
  under [spec authoring](spec-authoring.md#2-write-it). An example cannot supply a missing obligation.

## 6. Work record

Apply [Issue planning](documentation-strategy.md#issue-planning), including its private-security
and bot-update rules. Compare this PR with its acceptance and blockers; record
completed work, check results, documentation updates or a specific no-change reason, and remaining
scope. Partial PRs leave the issue open. Closure requires the deliverable and relevant merged PRs,
checks and documentation evidence; verify a parent's own acceptance and any explicit scope reductions.

## 7. Outbound and inbound links

- A new document is reachable from at least one `AGENTS.md`.
- A deleted or moved document is gone from every `AGENTS.md` and every cross-link.
- **A chapter that moved here from the reference implementation leaves nothing behind.** The
  document there is deleted, and what pointed at it points at a requirement ID here. Two copies
  means one of them is wrong.

Run the [repository checks](../guides/repository-checks.md#before-requesting-review), including
links/anchors and the full site render. Read diagnostics and unlinked prose when a document moves;
link validation cannot find those references.

## 8. Downstream

Where the change overtakes an implementation, raise the defect there in an issue.

Where it deletes an identifier, renumbers one, or changes what one stands for, the sweep is part of
this change rather than a note about it: the companion pull request re-vendoring
[`requirements.json`](../../requirements.json) is open, and every citation of the affected
identifier has been read. A reused number passes a downstream existence check while pointing at a
different obligation, and `GOVERNANCE.md` §"Deleting and renumbering, before `0.1`" calls that the
one failure nothing downstream can see.

Neither fits in this repository's commit, which is why both are opened before this pull request is
rather than remembered after it merges.

## 9. Report

Name what was updated, what was **deleted** and why, which requirement IDs were added or withdrawn,
and any remaining acceptance. Record the commands, results and skipped checks in the applicable
work record. A specific no-change reason, such as “The existing guide still describes the same
standards profile”, is a valid documentation outcome.
