<!-- Keep this short. What the change does and why it is right are the parts a reviewer
     cannot read off the diff; everything else is already in the diff. -->

## What this changes

<!-- One or two sentences. Link the work record: "Refs #123" for partial work;
     "Closes #123" only when merging meets all acceptance and required follow-up actions.
     Routine bot updates may use this PR; embargoed work uses the private security record. -->

## Why

<!-- A specification change needs a written rationale, because other implementations
     depend on it. -->

## Before requesting review

- [ ] Every commit is signed off — `git commit -s`, or `dco` fails
- [ ] Every new sempods-authored obligation has a requirement ID, and its anchor matches it
      exactly
- [ ] **No requirement ID was reused, renumbered or deleted.** A requirement that is no
      longer wanted is marked *withdrawn* and keeps its ID — it is cited in conformance
      suites and in other people's test reports. `GOVERNANCE.md` permits a deletion while
      its window is open; tick this box anyway and say in the description which ID went
      and why
- [ ] The OpenAPI description moved with the chapter, if the HTTP surface moved
- [ ] `spec/README.md`'s chapter table still reflects reality
- [ ] The applicable work record has check and documentation evidence, with remaining scope
      visible under [Issue planning](https://github.com/sempods/sempods-spec/blob/main/docs/agents/documentation-strategy.md#issue-planning)
- [ ] Documentation-sync is complete for this diff; affected documents are current or a specific
      no-change reason is recorded
- [ ] Proposal, adoption and publication claims match the delivered scope; standards-profile
      edits have been reviewed for semantic effects
- [ ] The applicable [repository checks](https://github.com/sempods/sempods-spec/blob/main/docs/guides/repository-checks.md#before-requesting-review)
      pass, including links/anchors and full site rendering; commands, results and skipped checks
      are reported

<!-- Is this a breaking change to the contract? Say so here. The project is 0.x and
     breaking is allowed — it is just never meant to be accidental or silent. -->
