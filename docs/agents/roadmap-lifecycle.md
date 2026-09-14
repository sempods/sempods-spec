# Procedure: retire a retained roadmap

This procedure applies only within the
[roadmap transition](documentation-strategy.md#roadmap-transition).
[#62](https://github.com/sempods/sempods-spec/issues/62) owns the replacement mapping and retires
this procedure and its wrapper. It does not require the tracked protocol work to be delivered first.
Every PR still runs [documentation-sync](documentation-sync.md).

## 1. Verify the mapping

Read each source entry, including completed work and unresolved decisions. Compare it with the
chapters and existing issue/PR evidence; a checkbox or closed issue alone does not prove delivery.
Give it an evidenced destination or disposition under #62. Reuse existing issues, preserve useful
reasoning, and keep private material outside public records. Verify native relationships and
prerequisites without duplicating sub-issue status in another checklist.

## 2. Switch ownership

Keep the source authoritative until the mapping is complete. Switch ownership and retire it in one
change, including the release-gate and milestone wording required by #62. Preserve the substance of
release conditions; mapping a task does not deliver it. Preserve useful proposal support and current
explanations at usable paths for the classification in #61. Do not rewrite a proposal as current
contract merely because tracking moved.

## 3. Sweep and report

Search tracked sources for the retired paths and unlinked roadmap references, including comments,
diagnostics, wrappers and frontend instructions. Repair navigation and run the applicable
[repository checks](../guides/repository-checks.md). Record destinations, preserved decisions,
remaining acceptance and check/documentation evidence in #62's PR. Stage only this change and
propose a commit message; the commit itself is the maintainer's.
