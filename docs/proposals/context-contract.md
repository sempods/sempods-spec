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
[implicit data-scope recommendation](data-access.md#logical-dataset-and-operation-scope) without discovering or selecting a Context.

The [vision's selection test](../vision.md#what-belongs-in-the-contract) separates three concerns:

| Concern | Contract boundary |
|---|---|
| Semantic data | RDF identities, assertions and stored/computed views; a native named graph need not be a registered sempods Context. |
| Context access profile | An advertised Context has registry RDF, a caller-authorized projection and an access summary. Its SPARQL projection is a logical named graph, including when computed over a store with no physical named graphs. |
| Lifecycle | Optional context-management supplies authorized creation/deletion. External provisioning and administration remain implementation choices; core discovery/selection works without the module. |

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

## Core selection and optional management

Recommend Context catalogue/description reads, caller-access summaries and selection as core,
with client-facing creation/deletion in optional `https://schema.sempods.org/module/context-management`.
Every implementation supports the core contract; ordinary clients need no Context-related requests.
A single-graph pod can expose no Contexts and return an empty catalogue. CMS-derived spaces can
appear as selectable Contexts without a sempods lifecycle API.

Keep `spec/core/contexts.md`, `spec/modules/context-management.md` and their corresponding OpenAPI
ownership. Retain the existing management module identity and allocate no `module/contexts` IRI.
Historical revisions retain their meaning; changes to lifecycle effects need explicit version and
compatibility treatment under [governance](../../GOVERNANCE.md#versioning).

For this boundary there are two conformance configurations: core, or core plus context-management.
After coordinated adoption, an implementation with CMS-derived Contexts and no other modules can
describe itself using the existing conformance fields:

```json
{
  "specVersion": "0.1-dev",
  "modules": []
}
```

No `supportsContexts` or default-context flag is needed. A missing management declaration means
that clients cannot rely on sempods creation/deletion; an owner's CMS administration rights do not
supply that API. Advertising management commits to its specified successful operations when
supported targets and authority allow them. Universal `403` does not implement an advertised module.
A deployment may also contain externally managed Contexts whose lifecycle is unavailable through
that module; their catalogue modes follow the [access summary](#caller-access-summary).

### Ordinary bootstrap

The pod supplies the [implicit D scope](data-access.md#recommended-implicit-scope) even with no
exposed Contexts. An authorized ordinary creation writes there without registry setup. D can use an
internal default Context or storage with no Context concept; its public Context IRI is optional.
Registering another Context does not change D. Read, find and the ordinary SPARQL default graph
use that same scope within current authority; source writes can change dependent computed views.
The [default-access sequences](data-access.md#default-access-acceptance-sequences) and
[authorization cases](access-control.md#authorization-without-context-setup) own those guarantees.
Choosing D grants nothing; permission on independent A does not authorize a write to D.

The current contract still requires explicit Context selection on data writes. Its minimum count
applies without context-management ([`SPS-CTX-028`](../../spec/core/contexts.md#SPS-CTX-028)); an empty
registry with that module permits Context creation, not Context-free data writes. The recommendation
changes both restrictions only through coordinated normative adoption.

### Stored and computed views

A registered Context names an addressable RDF view; a registry is a logical catalogue, not a
required physical table. Membership may be stored or computed from CMS spaces, user membership or
source facts. Expose canonical Context IRIs supplied by the pod; a client never constructs them
from CMS identifiers. The view definition and policy language need no public query or management API.

Context-selected reads, find expansion and `GRAPH <C>` use C's same authorized projection.
`sd:NamedGraph` describes that projection, not physical storage or a separately owned copy.
Projections can overlap; the same triple occurs once in their RDF union, while SPARQL retains its
normal solution multiplicities. A materialized view cannot broaden access or supply a stale
successful projection. The [dataset contract](data-access.md#logical-dataset-and-operation-scope)
owns term identity, named-graph visibility and selected-read/write effects.

### Caller access summary

Recommend reusing the RDF catalogue relationships with defined scope-level meanings. These are
proposed changes to the current grant-based [`SPS-CTX-034`](../../spec/core/contexts.md#SPS-CTX-034),
not an assertion that the adopted contract already supports arbitrary policy models.

The catalogue lists every Context for which this caller/client has at least one mode below. Each
mode reports current eligibility for that class of operation on C. Eligibility is a necessary
condition, not a claim that every resource, payload or precondition passes. Resolve it from the
applicable delegation or service assignment and current policy, including applicable public read,
independently of whether C contains data. Do not infer it from a successful request to one resource
or inspect hidden resource existence to decide the summary. Storage of grants or a separate policy layer is not required.

| Relationship from the catalogue to C | Proposed meaning |
|---|---|
| `readableContext` | The caller may select C's authorized data projection, possibly empty. Resource rules still filter that projection. It does not promise access to all of C's sources. |
| `writableContext` | C supports the membership-write contract and the caller has scope-level authority for selected data writes. Additional target, payload and complete-effect checks can refuse an individual mutation. |
| `manageableContext` | The management module provides lifecycle for C and the caller has authority to manage that view. External CMS administration alone does not qualify; without the module this set is empty. Data access is independent. |

Absence of a mode means that operation class is unavailable to this caller at the represented state;
it is not permission to try a broader fallback. A model with only resource-dependent rules still
has to define this bounded eligibility for any Context it exposes. It can instead expose those
resources through ordinary D access, without inventing Context-level permissions. Eligibility may
be established for an empty view or for a view whose resource rules currently hide every assertion.
A catalogue need not reveal hidden resources to be complete.

Keep the current RDF shape, negotiation and authorization/cache isolation. No new permission fields
or universal grant catalogue are needed. The server authorizes each later request again. The
catalogue's validator changes when represented membership or modes change; resource/view validators
follow their own representations. Reading a stale summary never restores authority. A Context's
public-read setting likewise permits an anonymous projection subject to applicable data rules; it
does not label every source assertion public. Public access retains the separate
[public-read rules](access-control.md#public-access-and-public-read).

### Selected-write boundary

The [membership-write contract](data-access.md#writes-within-the-addressed-scope) permits independently
mutable assertions, however implemented. A computed view lacking that contract is read-only through
selected CRUD, even when its manager can edit the definition or separately write the sources.
Omit `writableContext`; valid selected writes uniformly give `403`, including no-ops and absent
targets. No source/default-scope fallback or implicit selection-rule change is allowed.

A listed writable Context can still refuse a target under document or payload policy. Such denial
uses the [complete-effect and non-disclosure guarantees](access-control.md#complete-scope-authority-and-non-disclosure),
including hidden collisions and conditional requests. Managing a view grants neither read nor
source-write authority. General write-through computed views remain deferred until a discoverable
contract defines insertion, overlap, source updates and updates that leave the view.

### Externally changing spaces

A CMS may change a view's data membership or remove its public Context without a sempods management
request. Core specifies the resulting observations, not a CMS administration or sync protocol.
After a completed source or authorization change, the next request uses the updated authorized
projection; a stale materialization or cache cannot justify old access. Data growth within an
approved dynamic boundary differs from withdrawing authority or broadening the selection rule;
[delegation](access-control.md#request-selection-and-delegation) fixes those limits.

After C disappears, omit it from the catalogue. Its description returns the same `404` as a hidden
or absent Context, including for a conditional request with its old validator. Explicit C-selected
reads contribute no data; writes give uniform `403`. Never redirect to D or expose the old name as
a native-graph fallback. Core removal of the projection does not itself delete source assertions
or redirect ordinary writes. Independent current source authority still governs D and other views;
it must not be inferred from C's disappearance. A separate CMS data deletion has its own effects.

If C is later recreated, old C-bound authority does not revive. An unchanged IRI is insufficient to
establish the same authorization basis. Re-establish the relevant authority explicitly, including
fresh app consent where its ceiling or revoked authority requires it. Implementations choose how to
track that boundary; the public API adds no generation identifier.

## Adopted RDF surface and proposed lifecycle

The RDF registry surface from #90 is adopted separately under
[#92](https://github.com/sempods/sempods-spec/issues/92). Its normative owners are
[`SPS-CTX-031`](../../spec/core/contexts.md#SPS-CTX-031)–
[`SPS-CTX-036`](../../spec/core/contexts.md#SPS-CTX-036) and
[`SPS-CTX-037`](../../spec/modules/context-management.md#SPS-CTX-037), with
[representations and HTTP verification cases](../guides/context-registry.md).
Current grant implications, creation input/effects and destructive deletion remain in force.
The independent read/write/manage modes above and the optional lifecycle effects below remain
recommendations under #69. Keeping management optional does not settle its deletion semantics.

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
credentials are valid, requests are well-formed, C is a private registered membership-capable view,
and policies allow the stated operation. Lifecycle rows assume the management module and the
proposed lifecycle effects above; computed-view rows state their distinct setup and modes. Repeat
discovery cases with empty and nonempty graphs.

| Setup and request | Expected response/effect |
|---|---|
| Single graph, no management, no exposed Contexts; ordinary PUT/GET/PATCH/DELETE | The [ordinary sequence](data-access.md#one-rdf-graph) succeeds without any catalogue request or Context field; query sees D. |
| Same pod; catalogue GET before and after an allowed ordinary creation | Both `200` with an empty RDF collection; creation does not register a Context. |
| Same pod; resource GET and find selecting unknown C, or explicit empty selection | Resource `404`, find successful empty result; never D or unsupported-feature `400`. Malformed selectors remain `400`. |
| Empty registry, with or without management; consented ordinary resource PUT | Write to D `201`, registry still empty. Storage may use an internal default Context. No consent: write `403`. |
| CMS spaces C/E over D; no management; catalogue GET and selected reads | Visible spaces have readable relationships and descriptions, no manageable relationships. Selection works through core; no Context creation/setup is needed. |
| Same CMS pod; CMS owner requests conformance and catalogue | Both `200`; no management module declaration or manageable relationships. CMS ownership does not supply a sempods lifecycle API. |
| Management advertised; permitted Context creation, then ordinary data creation | Context PUT `201`; ordinary PUT still writes D. Context creation neither redirects D nor becomes a prerequisite for the data write. |
| Manage caller deletes the last C at full adoption, including C exposing D | `204`, empty registry; source assertions survive under independent authorization. D remains the implicit scope, with no write redirection or public fallback. Old C-bound grants do not revive on recreation. |
| Authorized administrator unregisters C; another registered view C/sub selects the same source | `204`, C's published projection disappears; source assertions and C/sub's independent definition survive. |
| Same administrative authority; unregister C with versus without hidden source data whose writes are denied | Both `204`; no source deletion. A policy denying the administrative action itself gives uniform `403`, also for an absent target. |
| No physical named graphs; computed C selects Alice's tasks from D; ordinary creation and then assignee update | C includes the matching task, then drops it when it no longer matches. No Context-membership write was needed. |
| C has child path C/sub and both views select the same task | No domain relation or RDF containment is inferred from the path; updates to shared source data can change both projections. |
| Caller manages computed C but cannot read or edit its sources | Catalogue links C through `manageableContext` only; registry GET `200`, data projection empty, selected writes `403`. No read/write implication from manage. |
| Readable computed C has no membership-write contract; selected PATCH/PUT/DELETE, including no-op requests | Uniform `403`; source facts, rules and grants unchanged. Authorized ordinary writes address sources inside D; no implicit write-through to sources outside D. |
| Manager unregisters computed C backed by a rule also used by independent E | C's projection disappears and its bound grants cease to authorize; shared rule/source assertions and E survive. Re-creating C does not restore old C-bound authority. |
| C has scope-level write eligibility; target-specific policy denies R | Catalogue includes `writableContext C`; R write gives `403`, including with a matching validator or hidden collision, without any mutation. A permitted target write succeeds under its normal contract. |
| C supports membership writes, but the caller lacks scope-level write authority | No `writableContext C`; selected writes give `403` even if the payload is empty or identical. |
| Caller may select C; all its assertions are hidden by document rules | C remains readable/discoverable with an empty projection; GET of R is `404`, find is empty and `GRAPH <C>` contains no triples. |
| C and E are read-only views over D selecting Alice's tasks and open tasks; R is both | Each selected GET and fixed-graph query returns R; C/E-union reads contain each triple once. Find uses the same authorized union for matching and expansion. |
| Same views; authorized ordinary PATCH changes R's assignee to Bob | Ordinary GET shows Bob; C no longer contains R, E still does. No independent copy or selected write is created. |
| Caller loses C access, while independent D and E authority remains | Catalogue loses C's modes; conditional C-description GET with an old tag gives `404`, never `304`; selected R GET is `404`. Ordinary D and E reads retain their independent results. |
| CMS removes C without removing its sources | Catalogue omits C; description `404`; selected R GET `404`, find empty and selected writes `403`. Independently authorized D/E results remain; no fallback to D under C's name. |
| CMS recreates C at the same IRI after removal | Old C-bound authority remains ineffective. Explicitly re-established authority is required; independent D authority is unaffected. |

Repeat the projection cases with a completed source/membership change followed by conditional reads
and cached catalogue access. Compare each selected read and query against the same authorized RDF
fixture; compare find against the same engine on that fixture, without prescribing its ranking.
These cases complement the [request-filter/delegation cases](access-control.md#request-selection-and-delegation).
They are proposed HTTP/model expectations, not evidence that a CMS adapter, cache or policy engine
has implemented them.

## Remaining adoption boundary

The RDF descriptions, catalogue and creation responses are adopted by #92 on the current Context
model. Their vocabulary properties and representations are owned by the normative chapters and
[guide](../guides/context-registry.md). Server/client/MCP migration is tracked in
[Kotlin #180](https://github.com/sempods/sempods-kotlin/issues/180), coordinating #166/#176.

Full adoption of ordinary access without Context setup, core discovery/selection and optional
context-management remains under #69–#74/#68.
It must review the default-access resolution and settle authentication/delegation decisions, then
align core/module versions, stored/computed projections, membership-write limits, independent
modes, Context-free data writes and non-destructive lifecycle, including media. The adopted RDF slice
advertises no new module and does not satisfy #68's adoption gate. The
[data-access inventory](data-access.md#requirement-changes-to-prepare) owns the wider impact.
