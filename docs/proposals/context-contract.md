# Discoverable Contexts and RDF registry descriptions

Status: **Partly adopted in this revision; remaining recommendations are non-normative.**
RDF registry adoption: [#92](https://github.com/sempods/sempods-spec/issues/92), implemented by
[PR #93](https://github.com/sempods/sempods-spec/pull/93), owns descriptions, catalogues and creation
response representations in the linked normative chapters. [#90](https://github.com/sempods/sempods-spec/issues/90)
is the completed recommendation source.
Empty-registry lifecycle: [#37](https://github.com/sempods/sempods-spec/issues/37) /
[PR #104](https://github.com/sempods/sempods-spec/pull/104) permits empty registries with the current
context-management module; deletion remains destructive.
Remaining proposal: [#69](https://github.com/sempods/sempods-spec/issues/69) owns the module/default-access
and full lifecycle decisions; [#68](https://github.com/sempods/sempods-spec/issues/68), through #69–#74,
owns their coordinated normative adoption. This document retains those non-normative recommendations.

## Scope and standards

Applications describe resources and their relationships in RDF. A Context identifies a logical
view of that data; membership may be stored or computed. It does not define the application's
vocabulary, a folder for a resource, or a physical store. The same resource IRI can occur across Contexts without changing
what it identifies. Ordinary clients use the
[implicit data-scope recommendation](data-access.md#logical-dataset-and-operation-scope) without this module.

The [vision's selection test](../vision.md#what-belongs-in-the-contract) separates three concerns:

| Concern | Contract boundary |
|---|---|
| Semantic data | RDF identities, assertions and stored/computed views; a native named graph need not be a registered sempods Context. |
| Context access profile | An advertised Context has registry RDF, a caller-authorized projection and an access summary. Its SPARQL projection is a logical named graph, including when computed over a store with no physical named graphs. |
| Lifecycle | The same contexts module supplies authorized creation/deletion. Storage, policy language, provisioning and additional administration remain implementation choices. |

In the first RDF delivery, retain the current Context-mode implications for compatibility. In the
full view contract, read, data-write and view-management authority are independent. A manager can
register or remove a computed view without authority to edit, or even read, its sources. Where a
membership-based policy profile implies read/write from manage, report the resulting modes;
do not extend that implication to every view. Slash-bounded management limits administrative
authority, not RDF containment or domain relationships. Neither wire-level grant parsing nor a
particular policy representation follows from a Context's identity.

The baseline is the proposal and current contract at
[`303d8aa`](https://github.com/sempods/sempods-spec/tree/303d8aa3acf3d7838e7c1a7062a705ab958d7954).
Reuse the existing canonical JSON-LD/N-Quads read profile and RFC 9110 for negotiation, validators
and conditional reads. Creation retains the current lifecycle contract as described below.
[RDF Schema 1.1](https://www.w3.org/TR/2014/REC-rdf-schema-20140225/)
supplies `rdfs:label` and `rdfs:seeAlso`;
[DCMI Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)
supplies `dcterms:description` and `dcterms:created`.
[SPARQL Service Description, 21 March 2013](https://www.w3.org/TR/2013/REC-sparql11-service-description-20130321/#vocab)
supplies the graph-description vocabulary only. Reusing its terms does not add a SPARQL service
endpoint or assert that the registry is the caller's query dataset. HTTP cache directives retain
[RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html)'s meanings.

## Module boundary and bootstrap

Use one optional module, `https://schema.sempods.org/module/contexts`, initially `0.1-dev`. It covers
Context selection, identities, registry reads, caller-access discovery and lifecycle together.
A core client needs none of those capabilities. The module preserves ordinary requests without a
selector through the [implicit-scope recommendation](data-access.md#recommended-implicit-scope).
Its [four acceptance sequences](data-access.md#default-access-acceptance-sequences) and
[authorization/conditional cases](data-access.md#authorization-and-conditional-boundaries) specify
the proposed default-access resolution for #69. The single-module boundary is the selected
direction; this resolution remains non-normative pending coordinated adoption.

At full adoption, this module supersedes the current `context-management` contract and the
Context-specific parts of current core. It is not a second layer depending on a lifecycle module.
Keep the old IRI's historical meaning and published references; do not silently alias or rename it.
The earlier RDF response delivery still uses the current core and `context-management` declarations.
The new identity is allocated and advertised only with its coordinated normative adoption.
A development version is mutable; adoption and implementation evidence also name the source revision.

For the later adopted contract, the existing conformance fields suffice:

```json
{
  "specVersion": "0.1-dev",
  "modules": [
    {"id": "https://schema.sempods.org/module/contexts", "version": "0.1-dev"}
  ]
}
```

For these capabilities there are two configurations: core alone, or core with `contexts`.
Advertising the module commits to its complete API contract, including lifecycle. Authorization
can deny individual operations and some views can be read-only; those are data/access states, not
additional module combinations. Validation includes permitted operations, not only denials; an
implementation cannot replace a missing advertised capability with universal `403`. Unsupported
Context input on a core-only pod retains the proposed `400` outcome. No extra capability flags or
policy-management API are introduced.

In the default-access recommendation, the pod supplies an implicit D scope even with no registered
Contexts. An authorized ordinary creation writes there without registry setup. D can be backed by
an internal default Context or storage with no Context concept; its public Context IRI is optional.
Additional Context registration does not change D. Read, find and the ordinary SPARQL default graph
use that same scope within the caller's authority. Source writes may change dependent computed views.
The [authorization proposal](access-control.md#authorization-without-context-setup) defines the
consent/delegation recommendation for this access, with remaining profile decisions under #69.
Choosing a default creates no authority; permission on independent A does not authorize a write to D.
The current contract still requires explicit Context selection on data writes. Its minimum count
applies only without context-management ([`SPS-CTX-028`](../../spec/core/contexts.md#SPS-CTX-028));
an empty registry with that module permits Context creation, not Context-free data writes.

A single physical graph can support several computed Contexts, for example tasks selected by
assignee or project. A pod can implement the selection with query evaluation, an ACP-based access
calculation or a materialized view, while providing the same observable projection. ACP does not
itself define this data-view mapping. A materialized result cannot broaden access or lag behind the
state observed by the request. Computed projections satisfy the shared authorized-query equivalence.

Context-selected reads, find expansion and `GRAPH <C>` use the same authorized projection of C;
its contents can overlap other Contexts and change when source facts, selection or authorization
change. `sd:NamedGraph` describes this query projection, not a physical partition or a separately
owned copy. Context selection neither exposes the policy definition nor confers source authority.
The [dataset contract](data-access.md#logical-dataset-and-operation-scope) owns these read/write
boundaries and their stored-versus-computed cases.

### Selected-write boundary

The membership-write contract in that document supports independently mutable assertion membership,
however implemented. Such writes can change dependent computed views, while unrelated source
assertions survive. A computed view lacking that contract is read-only through selected CRUD,
even if its manager can edit its definition or its callers can separately edit the sources.
Omit `writableContext` for it; valid selected writes give uniform `403`, including no-ops and absent
targets. No fallback to source or default-scope writes and no implicit changes to selection rules.

This bounds the first computed-view support. General write-through views need a later explicitly
discoverable contract for source updates, insertion placement, overlap and updates that leave the
view. An implementation cannot advertise the present writable contract while choosing those effects
for itself. #69 owns the explicit deferral and any later profile decision; early RDF adoption does
not claim computed-view support or reopen the current write semantics.

## Adopted RDF surface and proposed lifecycle

The RDF registry surface from #90 is adopted separately under
[#92](https://github.com/sempods/sempods-spec/issues/92). Its normative owners are
[`SPS-CTX-031`](../../spec/core/contexts.md#SPS-CTX-031)–
[`SPS-CTX-036`](../../spec/core/contexts.md#SPS-CTX-036) and
[`SPS-CTX-037`](../../spec/modules/context-management.md#SPS-CTX-037), with
[representations and HTTP verification cases](../guides/context-registry.md).
Current grant implications, creation input/effects and destructive deletion remain in force.
The full optional module's independent read/write/manage modes remain a recommendation under #69.

Current context-management permits deletion of the last Context and owner creation in an empty
registry under [`SPS-CTX-017`](../../spec/modules/context-management.md#SPS-CTX-017) and
[`SPS-CTX-019`](../../spec/modules/context-management.md#SPS-CTX-019). The proposed non-destructive
deletion below remains separate from that contract.

Deleting C unregisters its view and withdraws its published Context projection; it does not delete
source assertions, clear an underlying graph or remove independent views. Retained assertions do
not automatically become public or gain broader authorization. Their ordinary accessibility still
requires independent current authority; old C-bound grants authorize neither retained sources nor
a later re-created C. Shared ACP rules or other policy state used independently elsewhere are not
removed merely because C referenced them. Store cleanup is free only where these outcomes hold.

This also applies when C was implemented with explicit membership: the data survives removal of its
view, but the old Context IRI cannot silently remain exposed as a native-graph fallback. Other
computed views are reevaluated under their definitions; removing C does not alter those definitions
or delete their shared sources. Data deletion uses a separately authorized data operation with its
own complete effect; view-management permission cannot substitute for that authority.

Authorize unregistering independently of hidden source contents. Existing authorized C gives `204`,
absent C gives `404`; outside management authority both give `403`. Success completes the full
unregistration and authority withdrawal; failure leaves both unapplied. No minimum registered Context count or
replacement Context is required at full adoption. Unregistering a public name for D leaves the
implicit data scope in place; it neither redirects ordinary writes nor grants new source access.
Creation with the existing ContextCreate fields creates an empty membership-capable view; provisioning computed definitions stays with an
implementation's authorized administration, without adding a rule language to this contract.

The normative adoption must reconcile CTX-017 and consumers such as MEDIA-021 with the separation
of view deletion from source/media deletion. Preserve the earlier contract until that coordinated
change; neither deleting shared data nor stripping independent permissions is an allowed shortcut.

## Request cases

These are proposed HTTP expectations, not executed conformance tests. Unless stated otherwise,
credentials are valid, requests are well-formed, C is a private registered membership-capable view
using the current mode implications, and further policies allow the operation. Computed-view rows
state their distinct setup and modes. Repeat discovery cases with empty and nonempty graphs.

| Setup and request | Expected response/effect |
|---|---|
| Core-only pod; conformance GET, then authorized ordinary resource PUT | No Context modules; `201` without registry setup or selection. A Context selector gives `400`. |
| Context module, empty registry; catalogue GET, then consented ordinary resource PUT | Empty RDF collection `200`; write to D `201`, registry still empty. Storage may use an internal default Context. No consent: write `403`. |
| Context module advertised; client discovers modules | Selection, registry, access discovery and lifecycle form one supported contract; caller authority is checked per operation. No second module dependency. |
| Manage caller deletes the last C at full adoption, including C exposing D | `204`, empty registry; source assertions survive under independent authorization. D remains the implicit scope, with no write redirection or public fallback. Old C-bound grants do not revive on recreation. |
| Authorized administrator unregisters C; another registered view C/sub selects the same source | `204`, C's published projection disappears; source assertions and C/sub's independent definition survive. |
| Same administrative authority; unregister C with versus without hidden source data whose writes are denied | Both `204`; no source deletion. A policy denying the administrative action itself gives uniform `403`, also for an absent target. |
| No physical named graphs; computed C selects Alice's tasks from D; ordinary creation and then assignee update | C includes the matching task, then drops it when it no longer matches. No Context-membership write was needed. |
| C has child path C/sub and both views select the same task | No domain relation or RDF containment is inferred from the path; updates to shared source data can change both projections. |
| Caller manages computed C but cannot read or edit its sources | Catalogue links C through `manageableContext` only; registry GET `200`, data projection empty, selected writes `403`. No read/write implication from manage. |
| Readable computed C has no membership-write contract; selected PATCH/PUT/DELETE, including no-op requests | Uniform `403`; source facts, rules and grants unchanged. Authorized ordinary writes address sources inside D; no implicit write-through to sources outside D. |
| Manager unregisters computed C backed by a rule also used by independent E | C's projection disappears and its bound grants cease to authorize; shared rule/source assertions and E survive. Re-creating C does not restore old C-bound authority. |


## Remaining adoption boundary

The RDF descriptions, catalogue and creation responses are adopted by #92 on the current Context
model. Their vocabulary properties and representations are owned by the normative chapters and
[guide](../guides/context-registry.md). Server/client/MCP migration is tracked in
[Kotlin #180](https://github.com/sempods/sempods-kotlin/issues/180), coordinating #166/#176.

Full adoption of the context-free core and optional `contexts` module remains under #69–#74/#68.
It must review the default-access resolution and settle authentication/delegation decisions, then
align module identity/version, core boundaries, stored/computed projections, membership-write limits, independent
modes, Context-free data writes and non-destructive lifecycle, including media. The adopted RDF slice
advertises no new module and does not satisfy #68's adoption gate. The
[data-access inventory](data-access.md#requirement-changes-to-prepare) owns the wider impact.
