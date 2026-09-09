# Core for authorized data access (SOLL)

> Progress is tracked in place. Completed items stay in this file, marked done, until the whole
> milestone is consolidated. Do not prune them individually — the roadmap documents progress, not
> only remaining work.

Concepts: [data access](../concepts/data-access.md) owns the core/module boundary and requirement
impact; [access control](../concepts/access-control.md) owns authorization semantics.

Goal: adopt a coherent core for authorized RDF access with an optional Context contract, and hand
off the resulting implementation changes. This milestone contributes to [spec 0.1](spec-0.1.md).
The normative chapters remain in force until adoption. Solid compatibility and data sync are
separate follow-up work.

## Work

- [x] 1 — Describe the target contract, implementation examples and requirement impact in the two
  concepts linked above.
- [ ] 2 — Resolve the [remaining contract decisions](../concepts/data-access.md#decisions-before-normative-adoption-soll)
  with concrete request/response cases and a recommended rule for each. Update the concepts with
  the resulting semantics. Include the mutation, identity and authorization gaps mapped below,
  the `public-read` scope and token migration, and the client-visible default/named graph layout
  after ordinary writes and explicit selection.
  Depends on 1.
- [ ] 3 — Turn the impact table into a coordinated normative patch: retain, generalize, move or
  remove each affected requirement. Cover core, authorization, CRUD, SPARQL, `find` and the optional
  Context contract, including its lifecycle dependency. Apply the identifier rules in
  [governance](../../GOVERNANCE.md). Depends on 2.
- [ ] 4 — Align OpenAPI, module discovery and versions, the requirement checker and index, chapter
  maps, vision and agent instructions with that patch. Review MCP and media for implicit Context
  dependencies and sweep citations. Ship together with 3.
- [ ] 5 — Validate common client operations for a single RDF graph, a Context-based pod and a pod
  with area/document policies. Define executable cases for allowed and denied operations, mutation
  scope, conditional writes, query equivalence and revocation, including the issue cases below.
  Cover public access with and without credentials, an empty public view, and graph-sensitive
  queries against a fixed logical dataset with different physical storage layouts;
  distinguish contract fixtures from tests actually run against an implementation. Depends on 2;
  review results before adopting 3–4.
- [ ] 6 — Reconcile the related issues with the final patch and prepare the implementation handoff:
  changed behavior, affected citations and the regenerated index. Follow the downstream issue and
  pull-request obligations in the [documentation strategy](../agents/documentation-strategy.md#definition-of-done).
  Context-based implementations can retain their policy model. Depends on 3–5.
- [ ] 7 — Adopt the reviewed specification change, update the concepts to describe the adopted
  contract, and [consolidate this roadmap](../agents/roadmap-lifecycle.md). Depends on 2–6.

## Issue coordination

The work numbers below refer to this roadmap. Links identify scope and dependencies; GitHub owns
each issue's state. Check the final requirement text before closing an issue. Independently
actionable fixes can land before this milestone; reconcile them instead of implementing them twice.
A milestone tracking issue links here without duplicating this checklist.

### Specification

| Issues | Work | Treatment |
|---|---|---|
| [#36 — context-free data surface](https://github.com/sempods/sempods-spec/issues/36), [#37 — minimum Context count and deletion](https://github.com/sempods/sempods-spec/issues/37) | 2–5 | Direct scope. Replace the flag and universal registered-Context proposals with ordinary core writes and an optional Context contract. Cover empty-pod setup, selection and Context-rights discovery. |
| [#45 — write existence oracle](https://github.com/sempods/sempods-spec/issues/45) | 2–5 | Define non-disclosing write failures across permission models, including hidden-resource collisions; keep the Context-module cases. Test observable outcomes without prescribing a storage/check sequence. |
| [#6 — multi-value slot POST](https://github.com/sempods/sempods-spec/issues/6) | 2–5 | Resolve batch effects, outcomes and `Location` together with mutation scope. Include mixed existing/new values and denied mutations. |
| [#9 — slot ETag in OpenAPI](https://github.com/sempods/sempods-spec/issues/9) | 2–5 | Define validators for the new resource scope, then describe and test them. Copying the current single-Context condition into OpenAPI would leave the core dependent on Contexts. |
| [#5 — equivalent-identity claim](https://github.com/sempods/sempods-spec/issues/5), [#10 — authorize state](https://github.com/sempods/sempods-spec/issues/10) | 2–5 | Resolve the shared auth profile: decide where identity-equivalence behavior belongs and specify its wire contract where retained; align `state` handling with the profiled OAuth contract. |
| [#49 — consent replay race](https://github.com/sempods/sempods-spec/issues/49) | 2, 4–5 | Coordinate the optional MCP reauthorization contract with core delegation/revocation. Cover an old code exchanged across a fresh-consent challenge; token issuance time alone is insufficient evidence of renewed consent. The independent fix need not wait for the split. |
| [#11 — find JSON-LD arrays](https://github.com/sempods/sempods-spec/issues/11) | 3–5 | Align the response schema with both ordinary core results and any retained optional Context representation; named graphs alone do not imply Context permissions. |
| [#8 — MCP metadata routes](https://github.com/sempods/sempods-spec/issues/8) | 4–5 | Align module OpenAPI with current discovery requirements. The issue's host-rooted-route premise is stale: current `SPS-MCP-031` requires the append form only. |
| [#21 — stable IRIs and version transitions](https://github.com/sempods/sempods-spec/issues/21) | 2–4, 6 | Include the resource-IRI stability gap identified in the [issue comment](https://github.com/sempods/sempods-spec/issues/21#issuecomment-5461857774). Assess the transition impact of changed write behavior; moving Context chapters alone does not prove compatibility. General version negotiation remains separate release work. |

[#4 — MCP error codes](https://github.com/sempods/sempods-spec/issues/4) and
[#7 — OIDC callback address](https://github.com/sempods/sempods-spec/issues/7) remain independent
[0.1 work](spec-0.1.md). Check any intervening fixes during work 4; the core split does not itself
resolve them.

### Reference implementation

| Issues | Work | Treatment |
|---|---|---|
| [#80 — context-free writes](https://github.com/sempods/sempods-kotlin/issues/80) | 6 | Rescope the implementation handoff to the adopted contract: its capability flag and mandatory listed write Context are proposal details this milestone replaces. |
| [#54 — conformance discovery](https://github.com/sempods/sempods-kotlin/issues/54) | 4, 6 | Coordinate the advertised core/module versions and Context-module declaration. Discovery can be implemented independently; the adopted module contract determines what may be advertised. |
| [#35 — owner-installed service clients](https://github.com/sempods/sempods-kotlin/issues/35) | 2, 6 | Check unattended-client delegation and bootstrap against the shared auth contract. Keep the installation workflow and UI in the implementation's own work. |

[#56 — base URL validation](https://github.com/sempods/sempods-kotlin/issues/56),
[#42 — facade boundaries](https://github.com/sempods/sempods-kotlin/issues/42),
[#28 — PodRef identity](https://github.com/sempods/sempods-kotlin/issues/28) and
[#15 — published API surface](https://github.com/sempods/sempods-kotlin/issues/15) remain independent
implementation work. They do not define the optional Context contract; a data type's identity
design in #28 is distinct from the protocol's resource-IRI stability in spec #21.

## Acceptance

The normative text and its generated and hand-written views agree. A client can perform the same
core operations without a Context selector across the three fixture models; authorization failures,
public-access/token behavior, query-visible graph layout and successful effects have defined
outcomes. Context-specific behavior is discoverable through
the optional contract. Test evidence states which implementations were exercised, and required
downstream follow-up is linked before adoption.

Run the checks in [AGENTS.md](../../AGENTS.md#before-you-commit), including the example runner's
self-test and the full site build. Existing ACP example checks alone do not establish conformance
to the new data-access contract.
