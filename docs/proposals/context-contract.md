# Discoverable Contexts and RDF registry descriptions

Status: **Proposed; non-normative.**
Owning issues: [#69](https://github.com/sempods/sempods-spec/issues/69) for the module boundary and
[#90](https://github.com/sempods/sempods-spec/issues/90) for registry descriptions and their lifecycle.
Adoption: [#68](https://github.com/sempods/sempods-spec/issues/68), through its coordinated normative
preparation and validation. This document recommends decisions; merging it changes no contract.

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
selector through the [implicit-scope recommendation](data-access.md#recommended-implicit-scope),
whose four access cases still await decision in #69. The single-module boundary is the selected
direction; the particular default-access effects are recommendations for review.

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
#69 still owes the exact core authorization/delegation profile for this access; choosing a default
creates no authority and permission on an independent A does not authorize a write to D.
The initial RDF delivery retains the current selector and minimum-count rules.

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

## Registry description

Let `P = https://example.org/alice`, `L = P/_system/contexts`, and `C = L/tasks` in the cases below.
Abbreviations in prose and tables stand for full IRIs on the wire.

Recommend these fields on `GET C`, describing registry state only:

| Predicate | Proposed meaning and shape |
|---|---|
| `rdf:type` / JSON-LD `@type` | Includes `sd:NamedGraph`. |
| `sd:name` | Exactly the Context IRI. Its explicit value supplies the named-graph vocabulary's graph name, even though the description is addressed at that same IRI. |
| `rdfs:label`, `dcterms:description` | Optional text held by the registry; plain or language-tagged strings. Choose DCMI for the description consistently with the creation date. |
| `dcterms:created` | Optional single `xsd:dateTime` creation instant when known; no invented date or required storage mechanism. |
| Candidate `sps:public` | Exactly one Boolean: whether the Context-level public-read condition is enabled. False by default. Further policies can narrow actual data access; this flag neither grants writes nor promises that every fact is publicly readable. |
| `rdfs:seeAlso` | Includes the derived system resource address for ordinary data about C. It is supplied by the registry response, whether or not readable statements currently exist there. |

Here `sps:` means `https://schema.sempods.org/`. `sps:public` is a candidate vocabulary term, not
published by this document. A generic access-rights description does not express this Boolean
Context condition. Registry reads can include other descriptive predicates; clients ignore ones
they do not understand. No caller rights, policy rules or graph contents are merged into this answer.

For a caller with Context visibility, `GET C` returns `200`, `Content-Type: application/ld+json`,
with this possible body and a strong representation ETag:

```json
{
  "@id": "https://example.org/alice/_system/contexts/tasks",
  "@type": ["http://www.w3.org/ns/sparql-service-description#NamedGraph"],
  "http://www.w3.org/ns/sparql-service-description#name": [{"@id": "https://example.org/alice/_system/contexts/tasks"}],
  "http://www.w3.org/2000/01/rdf-schema#label": [{"@value": "Tasks"}],
  "http://purl.org/dc/terms/created": [{"@value": "2026-09-15T10:00:00Z", "@type": "http://www.w3.org/2001/XMLSchema#dateTime"}],
  "https://schema.sempods.org/public": [{"@value": false}],
  "http://www.w3.org/2000/01/rdf-schema#seeAlso": [{"@id": "https://example.org/alice/_system/resources/aHR0cHM6Ly9leGFtcGxlLm9yZy9hbGljZS9fc3lzdGVtL2NvbnRleHRzL3Rhc2tz"}]
}
```

N-Quads represents the same registry statements in its default graph; it does not insert them into
C's data graph. The Context IRI identifies a named data graph while GET at that IRI describes its
registry entry; reading its data uses the selected data surfaces.

### Authority and query access

Registry authority follows the authenticated pod surface that supplied the response, not the use
of a particular subject IRI or predicate. Ordinary data can use the same terms without acquiring
control-plane authority. Registry-backed fields change only through an authorized administrative
action. That write boundary does not require storing registry state outside RDF or forbid querying
it through a separate interface.

The first interoperable surface is HTTP discovery: GET the catalogue and descriptions, then query
or join the returned RDF locally if useful. Such queries need no new server capability. Keep the
retrieved registry snapshots separate from ordinary assertions when their authority matters, and
retain their caller/request context. They describe what was disclosed at retrieval; no client-side
query result authorizes a later server operation.

No server-side registry query capability is standardized in this iteration. Ordinary CRUD/find and
SPARQL retain their data-space meaning from the dataset proposal; `FROM <C>` selects C's authorized
data, not the RDF returned by GET C, and does not fetch that URL. Implementations can offer separate
read-only registry query interfaces as extensions, with current caller filtering, source separation
and the same hidden/absent protections. Clients cannot infer such an interface from Context support.
A portable server-side registry query profile would need its own discovery and dataset contract;
it is neither a prerequisite for RDF discovery nor prohibited by this proposal.

The `rdfs:seeAlso` target is derived without testing data existence. Following it applies ordinary
resource-read authorization and scope: in the full default-access recommendation it addresses D,
not every Context containing statements about C. It can yield `404` while `GET C` succeeds, or vice versa. This link
asserts relevance, not authority, equivalence or a promise of content. A duplicate HTTP `Link` is
unnecessary for this contract. Ordinary writes can store `<C> sps:public true` as data without
changing the registry's `false`, registry validators or access decisions.

## Catalogue and caller rights

Recommend a canonical RDF description of L as `sd:GraphCollection`, with `sd:namedGraph` references
to the registered Contexts visible to this caller. Each referenced Context is described at its own
IRI with `sd:name` as above. Membership is complete for the request's authorized view; ordering is
irrelevant. Empty collections have no membership triples (JSON-LD may omit that predicate).
No pagination or total count is added by this iteration.

Reuse the graph vocabulary's collection identity and membership without adopting an LDP or Hydra
protocol. Registry membership can include an empty Context; the proposed SPARQL named projection
still omits graphs with no readable triples. These are distinct views.

Put caller access on the **catalogue subject** as direct RDF relationships to Context IRIs:

| Candidate predicate | Objects in this caller's catalogue snapshot |
|---|---|
| `sps:readableContext` | Registered Contexts for which the Context-level read condition allows the caller. |
| `sps:writableContext` | Registered Contexts supporting the membership-write contract for which the Context-level data-write condition allows this caller. |
| `sps:manageableContext` | Registered Contexts whose view/registration this caller may manage. This alone grants no source-data access. |

These three properties replace a composite grant literal with a relation whose predicate identifies
the mode and whose object is the Context IRI. They introduce no policy nodes, mode ontology or
separate rights endpoint. Emit the complete effective sets for registered, visible Contexts. Include
modes actually implied by the applicable policy profile; do not infer data-write from view management.
Empty sets have no triples. Do not enumerate absent descendants or hypothetical namespace
roots. Evaluate the requesting client/subject and credential/delegation ceilings, including any
applicable public read; never substitute the person's broader authority or a token's contents.

A Context is visible in this registry when the caller has at least one of these Context-level modes.
Additional policies can restrict individual operations and data visibility. Each relation therefore
reports a Context-layer authorization result for this request; `sps:writableContext` does not promise
that replacing a predicate blocked by another policy will succeed. It is not a stored-policy export
or a capability. Copying the RDF grants nothing, and the later request is authorized again. These
results leave independent data read/write and view-management policies possible.

The candidate predicates describe a response-relative access summary over Contexts.
[WAC](https://solidproject.org/TR/2024/wac-20240512#access-privileges) describes resource access modes
and ACL control; `acl:Authorization`/`acl:mode` describe authorizations, while WAC control does not
imply resource read/write. [ODRL 2.2](https://www.w3.org/TR/2018/REC-odrl-model-20180215/#permission)
expresses policy rules about assets and actions. Neither is reused as if a coarse, evaluated Context
summary were a complete authorization policy. `dcterms:accessRights` is broader descriptive metadata,
not these three queryable mode-to-Context relationships. No standard equivalent was identified for
that scoped result. Adoption needs vocabulary definitions with these limits; it does not import a
policy evaluation model. HTTP `Allow` continues to describe methods, not caller authority.

For a caller with write authority on C, a complete catalogue can be:

```json
{
  "@id": "https://example.org/alice/_system/contexts",
  "@type": ["http://www.w3.org/ns/sparql-service-description#GraphCollection"],
  "http://www.w3.org/ns/sparql-service-description#namedGraph": [{"@id": "https://example.org/alice/_system/contexts/tasks"}],
  "https://schema.sempods.org/readableContext": [{"@id": "https://example.org/alice/_system/contexts/tasks"}],
  "https://schema.sempods.org/writableContext": [{"@id": "https://example.org/alice/_system/contexts/tasks"}]
}
```

For example, a client can evaluate this standard SPARQL query locally over the catalogue and
registry descriptions it retrieved for the same caller. No string splitting or policy evaluation
is needed, and the query changes no server state:

```sparql
SELECT ?context ?label WHERE {
  <https://example.org/alice/_system/contexts>
    <https://schema.sempods.org/writableContext> ?context .
  OPTIONAL { ?context <http://www.w3.org/2000/01/rdf-schema#label> ?label }
}
```

Use only the separately retained registry responses as this query's input; a user-authored
`writableContext` statement in the data space is not a rights report. A missing optional label does
not remove a writable Context from the result. The same C description is returned to read, write
and manage callers; the catalogue summary differs.
A caller with no visible Contexts receives `200` with L's identity and collection type, no members
and no grants. Unauthenticated callers see only their public Context view; invalid supplied
credentials still produce `401`. A missing C and an existing C without visibility both give `404`,
without distinguishing bodies, links or validators, including conditional reads.

### Cache and validator guarantees

Negotiation follows the shared HTTP profile, including `Vary: Accept`. Stored registry responses,
including errors, cannot be reused across caller/client authorization contexts or without current
authorization. A revoked caller's conditional GET C receives `404`, not `304`; hidden and absent
responses remain indistinguishable. A rights change that changes the catalogue representation
invalidates its previous strong tag. Individual description tags track that registry representation,
not graph contents, ordinary assertions about C or the caller's access summary.

One sufficient strategy is `Cache-Control: no-store` on all registry responses. Private storage with
mandatory revalidation can also satisfy the guarantees when cache selection distinguishes all
credential/authorization inputs as well as negotiated variants. Implementations choose the RFC 9111
mechanisms that establish these outcomes; there is no blanket prohibition on catalogue validators.
A validator supplied on a request never replaces current authorization, and a rights snapshot never
extends the caller's authority. These guarantees apply consistently to descriptions, catalogues and
errors; the example strategies are alternatives, not conflicting header requirements.

## Lifecycle

Keep the existing creation input and create-only behavior from
[context-management](../../spec/modules/context-management.md#SPS-CTX-015) for the first RDF delivery:
optional `ContextCreate` JSON with label, description and public, private by default, first creation
`201`, existing target `200` without changing its state. Both success responses use the negotiated
registry RDF description. This selects #90's existing-input alternative; it does not add metadata
editing or claim that the existing create-only PUT is ordinary replacement semantics. A general
metadata-edit operation needs a separately justified contract; it is not required for this module's
creation/deletion capability. Clients do not send a retrieved registry description as a creation
body. The early change migrates readers and success representations, not creation input or effects.

Retain owner or delegated slash-bounded manage authorization, including authorized creation of an
absent descendant. After authentication and syntax validation, a well-formed PUT/DELETE outside
management authority produces uniform `403` for existing and absent targets. A `context` parameter
is `400`: data selection never changes a control-plane target. Success representations disclose no
caller rights, and creation input cannot grant authority beyond the caller's management scope.
The RDF read's validators and conditional behavior do not create a new conditional-write profile
for these lifecycle operations. ContextCreate's optional input is interpreted by the lifecycle
contract, not by general resource RDF mutation rules.

The full optional-Context adoption changes deletion and empty-pod behavior below. These effects
are not part of the initial RDF delivery, which preserves current destructive Context deletion.

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
| Read caller; GET L and GET C | L links C through `readableContext` only; C description `200`, with no caller rights. |
| Write caller; GET L, GET C, selected data PUT | L links C through `readableContext` and `writableContext`; same C description; data write succeeds. Lifecycle PUT/DELETE remains `403`. |
| Manage caller; GET L, GET C, lifecycle PUT for C/sub | All three modes for C, same description; new child `201` under the module lifecycle contract. No absent child is listed before creation. |
| No-access caller; GET L, C and absent X | C/X omitted from L, both direct GETs `404` with no distinguishing validators or links. |
| Public C, anonymous GET L and C | L links C through `readableContext`; C description `200`. Invalid supplied credential: `401`. |
| Read revoked after GET C with tag E; GET C with `If-None-Match: E` | `404`. Authorized unchanged request: `304`. |
| Writer stores ordinary `<C> sps:public true` while registry says false | Ordinary system-resource read can show true; registry GET still false with unchanged tag; no policy change. Repeat where only one of these two reads is authorized. |
| Visible empty C; GET L, C and SPARQL `ASK { GRAPH <C> {} }` | L contains C, description `200`, query false because its named projection is omitted. |
| Manage caller; create absent C with the existing ContextCreate JSON `{"label":"Tasks"}` | `201`, RDF description, public false. Repeat or submit another label to existing C: `200` with unchanged registry state. |
| Same caller; create absent C without a body, then repeat on existing C | `201` with private defaults, then `200` unchanged. No metadata-edit capability is implied. |
| Non-manager; well-formed PUT/DELETE C versus absent X, including conditional requests | Uniform `403`, no existence signal or effect. Invalid credential is `401`. |
| Lifecycle PUT C with `?context=C` | `400`, no creation or change. |
| Manage caller deletes the last C at full adoption, including C exposing D | `204`, empty registry; source assertions survive under independent authorization. D remains the implicit scope, with no write redirection or public fallback. Old C-bound grants do not revive on recreation. |
| Authorized administrator unregisters C; another registered view C/sub selects the same source | `204`, C's published projection disappears; source assertions and C/sub's independent definition survive. |
| Same administrative authority; unregister C with versus without hidden source data whose writes are denied | Both `204`; no source deletion. A policy denying the administrative action itself gives uniform `403`, also for an absent target. |
| No physical named graphs; computed C selects Alice's tasks from D; ordinary creation and then assignee update | C includes the matching task, then drops it when it no longer matches. No Context-membership write was needed. |
| GET C with Accept N-Quads; GET L with Accept JSON-LD | Same registry meaning in RDF; L's grant summary stays on L. Rights are never added to C. |
| GET C or L with only `Accept: application/json` after RDF adoption | RDF JSON-LD under the existing media-type alias, no legacy Context/ContextList DTO. |
| Local query above on retrieved catalogue/description RDF, with and without C's label | Returns C in both cases; optional label when present, no grant-string parsing. |
| An ordinary data graph asserts `L sps:writableContext C` for a caller lacking write | The trusted catalogue has no such link; the selected write is still `403`. |
| Context-capable server; ordinary SPARQL `FROM <C>` | Authorized data in C, no registry URL fetch or injection of registry metadata. A registry query endpoint is not implied by Context discovery. |
| C has child path C/sub and both views select the same task | No domain relation or RDF containment is inferred from the path; updates to shared source data can change both projections. |
| Write revoked but read retained; conditional catalogue GET with its former strong tag | Updated representation omits `writableContext` C and is not `304` for that tag. |
| Caller manages computed C but cannot read or edit its sources | Catalogue links C through `manageableContext` only; registry GET `200`, data projection empty, selected writes `403`. No read/write implication from manage. |
| Readable computed C has no membership-write contract; selected PATCH/PUT/DELETE, including no-op requests | Uniform `403`; source facts, rules and grants unchanged. Authorized ordinary writes address sources inside D; no implicit write-through to sources outside D. |
| Manager unregisters computed C backed by a rule also used by independent E | C's projection disappears and its bound grants cease to authorize; shared rule/source assertions and E survive. Re-creating C does not restore old C-bound authority. |

## Delivery boundary and adoption impact

Recommend two bounded deliveries, with their work and dependency records owned by #90/#69 and
[#68](https://github.com/sempods/sempods-spec/issues/68):

| Delivery | Observable scope and prerequisite |
|---|---|
| RDF Context surface | On the current Context model, migrate GET C, GET L and successful creation representations to the registry RDF and structured caller summary above. Preserve current Context identity/membership, selector semantics, creation input/effects, minimum-count/deletion rules and grant semantics. Agree on text, OpenAPI, vocabulary, HTTP cases and the server/client migration together. No new optional-module claim. |
| Optional Context contract | After #69's authentication/delegation decisions, adopt the smaller core, one module declaration, the decided implicit-scope/explicit-selection semantics, bootstrap, read-only general views and non-destructive view deletion with matching artifacts and validation under #70–#74. |

The first delivery does not require metadata editing, a registry query service, a new policy engine
or the full core migration. Its read/summary cases can be checked against the current Context model;
computed-view, implicit-scope, zero-Context, independent manage/data modes and revised deletion cases
belong to the second delivery. Normative changes
still require review, validation and downstream preparation before merging. Completing the first
delivery does not complete #68 or advertise the new Context module. The work records must explicitly
scope the independently reviewable adoption rather than treating this proposal merge as adoption.

For the RDF delivery, recommend replacing the legacy `Context` and `ContextList` response shapes,
with no required dual-serving interval. `Accept: application/json` follows the existing RDF read
alias and returns `application/ld+json`; it does not select the legacy response DTO. Creation keeps
its existing JSON input. General version coexistence remains
[#21](https://github.com/sempods/sempods-spec/issues/21)'s work. A concrete consumer migration is
required before adoption; implementations can stage that migration without inventing new conformance
claims. Current Kotlin readers and MCP `list_contexts` need coordinated updates. Kotlin #166 already
awaits #90; #174 repaired the current JSON member names and is completed work, not a new blocker.

The RDF delivery affects CTX-021–024, lifecycle response representations, the associated OpenAPI
schemas, the four candidate predicates (`public`, `readableContext`, `writableContext`,
`manageableContext`), the requirement index where requirements change and downstream consumers.
The ContextList required-property candidate in spec #77 needs reassessment against that replacement.

Full adoption also changes Context/module chapters, Context-grant and authentication boundaries,
discovery and component versions, stored/computed projection semantics, membership-write limits, non-destructive view deletion and
revocation wording, including Context-dependent media lifecycle.
CTX-028/029's minimum-count rules go at that stage; CTX-025/026's authority separation and private
defaults remain. The [data-access impact inventory](data-access.md#requirement-changes-to-prepare)
owns the wider core change. Both deliveries keep chapter text and contract artifacts consistent.
This proposal changes none of them and allocates no vocabulary or module identifiers.
