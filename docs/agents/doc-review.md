# Procedure: review the documentation

Check the repository's text against its contract sources and the
[writing rules](documentation-strategy.md#the-writing-rules) for one target: your own change, a
pull request or a path. It applies every step below that would change a file, except steps 2
(Requirement IDs) and 4 (OpenAPI), which always report instead: assigning or renumbering a
normative requirement ID and hand-authoring a normative OpenAPI change both want a human decision,
not a silent rewrite. `--report-only` lists every other finding instead, without touching a file.
Applying on a pull request edits its branch, so check it out first: `gh pr checkout 123`. Run it
on your own change before requesting review — it is the working half of the
[definition of done](documentation-strategy.md#definition-of-done), on every PR, including partial
work.

Wrapped for Claude Code as the `doc-review` skill. Any other agent: *"Follow
`docs/agents/doc-review.md` for `<target>`."*

## 1. Target

| Call | Target | Read |
|---|---|---|
| `doc-review` | your branch | the commands below |
| `doc-review #123`, `doc-review <branch>` | a pull request | `gh pr diff 123` or `git diff origin/main...<branch>`, and the PR description |
| `doc-review spec/modules/media.md`, `doc-review docs/guides/` | a path | the chapter, guide or proposal as it stands |

For your branch:

```bash
git status --short
git diff --merge-base origin/main          # committed, staged and unstaged, in one diff
git diff --cached --merge-base origin/main # what is staged, even where the working tree hides it
git ls-files --others --exclude-standard   # new files, which no diff shows — read them
```

Against the merge base, so committed work counts as much as uncommitted work: `git diff HEAD`
misses the commits, a bare `git diff` also the staged part. A new chapter arrives as an untracked
file, and a chapter is the thing this procedure most needs to look at. Every command here names the
base `origin/main`; in a checkout without an `origin` remote, use `main`.

For a path, the steps check the text as it stands, and there is no diff:

| Step | For a path |
|---|---|
| 2 | Every obligation has an ID and a matching anchor; `check-requirements.py origin/main` replaces the diff check |
| 3 | The path's row in the chapter table |
| 4 | The chapter agrees with its OpenAPI description, whether or not anything moved |
| 5 | Everything except the proposal-disposition and wording-only checks |
| 6, 8 | Do not apply |
| 7 | Reachability and the repository checks |
| 9 | The report is the result; there is no work record to write to |

## 2. Requirement IDs

The half that has no equivalent in the reference implementation, and the half that is expensive to
get wrong. Always a finding for the report, never an automatic edit: assigning the next ID,
withdrawing one inside the governance window, or repairing a mismatched anchor is a decision for
the person who owns the change, not a rewrite this procedure applies by itself.

- **Every new sempods-authored obligation has an ID**, and the ID is higher than every ID ever
  issued in its area — withdrawn ones included. Check against the text, not against memory:

  ```bash
  grep -rho 'SPS-[A-Z]*-[0-9]\{3\}' spec/ | sort -u
  ```

- **No ID was reused, renumbered or deleted.** A deleted ID is the failure mode this step exists to
  catch, and `git diff` shows it as an ordinary removed line. Run this over the target's diff; shown
  for your branch:

  ```bash
  git diff --merge-base origin/main -- spec/ | grep '^-' | grep -o 'SPS-[A-Z]*-[0-9]\{3\}' | sort -u
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
nothing will tell you it has gone stale except this step. Always a finding for the report, never an
automatic edit: external implementers read this file, and a rewrite gets a human read before it
changes what they see.

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

Apply [Implementation follow-up](../../GOVERNANCE.md#implementation-follow-up): record known gaps
and normally open or reuse an implementation issue with the needed behavior, documentation and
verification work. Link that record from the specification PR; implementation delivery may follow.

For deleted, renumbered, reused or redefined identifiers, inspect downstream citations and include
the index refresh and citation corrections in the follow-up. A stale index can still accept a
deleted identifier or hide changed meaning. Record the affected paths and remaining work; do not
report downstream synchronization as complete until it is verified. No companion PR is required
before this specification PR can be reviewed or merged.

## 9. Report

List each finding as `file:line — rule — correction`, apply it, and name what was updated, what was
**deleted** and why, which requirement IDs were added or withdrawn, and any remaining acceptance.
With `--report-only`, list the findings without applying them. A step-2 or step-4 finding is always
listed, never applied. Record the commands, results and skipped checks in the applicable
work record. A specific no-change reason, such as “The existing guide still describes the same
standards profile”, is a valid documentation outcome.
