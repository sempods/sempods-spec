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

## Proposed designs

- [Pod and service discovery](pod-discovery.md) — proposed path-independent entry discovery,
  conformance and service bindings, with external endpoints and stable local reservations. Design and
  adoption planning belong to [#96](https://github.com/sempods/sempods-spec/issues/96).
- [Authorized data access](data-access.md) and [access control](access-control.md) — one proposal
  for ordinary access without Context setup, core selection, optional management and policy-independent
  guarantees. Normative adoption belongs to [#68](https://github.com/sempods/sempods-spec/issues/68).
- [Protocol profiles](protocol-profiles.md) — recommended standards scope, OAuth/OIDC redirects,
  service refresh, registration and MCP transport/error cases under #69. Records the adopted MCP
  discovery input and the independent client evidence remaining in #99.
- [Discoverable Contexts and RDF registry descriptions](context-contract.md) — the core selection/optional
  management boundary, default-access and lifecycle recommendations under #69/#68, including retained
  source/media authority, last-Context removal and collection eligibility. #92/PR #93 owns the
  separate RDF registry adoption from the completed #90 recommendation; its normative chapters and
  maintained examples own those details.
- [Authorization implementation support](authorization-implementation/README.md) — a possible ACP
  profile and native-state design retained solely for [#64](https://github.com/sempods/sempods-spec/issues/64)'s
  disposition under the temporary implementation-support exception.

The [ACP fixture guide](../guides/acp-fixtures.md) explains the illustrative model and its tests;
its existence changes neither proposal's status.
