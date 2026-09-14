# Proposals

Use a document here when a substantial design needs reviewable prose alongside its issue. Small
changes use an issue and PR. [Document ownership](../agents/documentation-strategy.md#document-ownership)
defines status and retention; [governance](../../GOVERNANCE.md#how-a-change-is-made) defines adoption.

## Writing a proposal

Open with the owning issue, explicit **non-normative** status and disposition. Describe the intended
contract, boundaries, rationale and concrete cases. Identify affected requirements, incorporated
standards and compatibility implications, and link decisions still owned by issues. Link to
[the vision](../vision.md) when explaining requirement selection. Keep task lists in the issue.

A useful opening, completed with real issue and PR links when writing the document:

```text
# <Proposed change>

Status: Proposed; non-normative.
Owning issue: <issue link>
Adoption: <adoption issue or PR links; state when none exists>

## Purpose and scope
## Proposed contract and cases
## Rationale and compatibility
## Decisions requiring resolution
```

On disposition, identify what was adopted, partly adopted, rejected or superseded, with the
review/adoption links and any issue owning remaining scope. Keep explanation only where it remains
useful; a maintained guide describes the adopted revision and links to its contract.

The existing [data-access and access-control proposals](../concepts/README.md) remain at their
source paths until [#61](https://github.com/sempods/sempods-spec/issues/61) classifies and moves them.
Their current location does not make them normative.
