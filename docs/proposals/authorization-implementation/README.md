# Authorization implementation proposal support

Status: **Proposed; non-normative. No implementation is asserted.**
Owning disposition: [#64](https://github.com/sempods/sempods-spec/issues/64).
Related contract proposal: [authorized data access](../data-access.md), owned by
[#68](https://github.com/sempods/sempods-spec/issues/68).

These drafts explore one possible realization of that proposal. The intended recipient is an
implementation repository that adopts the design; **sempods-kotlin is a candidate, not a confirmed
recipient**. #64 owns that choice and the receiving issue before transfer.

This is the temporary [implementation-support exception](../../agents/documentation-strategy.md#retained-design-material):
the material remains here solely for #64's disposition. It ends with verified receiving changes
and source cleanup, or an explicit maintainer-approved no-transfer decision and cleanup. A release
tag or a handoff issue alone does not authorize removing still-needed design.

| Draft | Scope |
|---|---|
| [ACP profile](acp-profile.md) | Possible policy representation, management boundary, audience authority and unresolved design choices |
| [Authorization state](authorization-state.md) | Native storage, ACP projections, ingestion, service-client origins and sandbox evaluation |

The implementation-neutral [fixture guide](../../guides/acp-fixtures.md) and
[examples](../../../examples/README.md) explain the supplied model independently of this handoff.
Their tests establish neither adoption nor a running implementation.
