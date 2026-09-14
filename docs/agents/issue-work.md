# Procedure: work on an issue

Apply [Issue planning](documentation-strategy.md#issue-planning), which owns scope, work-record
exceptions, metadata and closure. [Governance](../../GOVERNANCE.md#how-a-change-is-made) owns
proposal, normative adoption and publication decisions.

## 1. Establish the work record

Read the owning issue, its parent, relevant decisions and prerequisite links. For routine bot
updates or embargoed security work, use the exception's record. Load the applicable instructions.
Confirm the problem, intended result, boundaries, acceptance and checks; resolve decisions blocking
this iteration. Filers supply links and proposed scope; maintainers or triagers set native
relationships and metadata. Parent membership is not a dependency.

## 2. Deliver a bounded change

Link the PR to its work record. Use `Refs #N` for partial work and `Closes #N` only when merging
satisfies all acceptance and required follow-up actions. Keep private evidence in the private record.

Run the applicable [repository checks](../guides/repository-checks.md) and
[documentation-sync](documentation-sync.md) before review. Record check results, skipped checks,
updated documentation or a specific no-change reason, and remaining acceptance. Review normative
semantics, including standards incorporation; unchanged requirement IDs alone do not prove equivalence.

## 3. Verify completion

Compare the delivered work and merged PRs with the recorded acceptance. Incorporate actionable
review and discussion results into the owning description; keep unfinished scope visible there.
Check a parent's own acceptance and required children, with explicit decisions for dropped scope.
A completed proposal deliverable establishes neither adoption nor publication. Close only when the
issue-planning completion conditions and evidence are satisfied.
