# Discoverable Contexts and RDF registry descriptions

Status: **Proposed; non-normative.**
Owning issues: [#69](https://github.com/sempods/sempods-spec/issues/69) for the module boundary and
[#90](https://github.com/sempods/sempods-spec/issues/90) for registry descriptions and their lifecycle.
Adoption: [#68](https://github.com/sempods/sempods-spec/issues/68), through its coordinated normative
preparation and validation. This document recommends decisions; merging it changes no contract.

## Scope and standards

Applications describe resources and their relationships in RDF. A Context gives an optional name
to a selectable part of that data space; it does not define the application's vocabulary, a folder
for a resource, or a physical store. The same resource IRI can occur across Contexts without changing
what it identifies. Ordinary clients use the
[aggregate data contract](data-access.md#logical-dataset-and-operation-scope) without this module.

The [vision's selection test](../vision.md#what-belongs-in-the-contract) separates three concerns:

| Concern | Contract boundary |
|---|---|
| Semantic data | RDF identities, relationships and logical graph membership; a native named graph need not be a registered sempods Context. |
| Context access profile | An advertised Context has discoverable registry RDF, explicit selection and a defined caller-access summary. This is one optional sempods profile, not a meaning imposed on all RDF graphs. |
| Lifecycle | A separate module supplies authorized creation/deletion. Storage, policy language, provisioning and additional administration remain implementation choices. |

The profile retains the existing Context modes for interoperability: write includes Context-level
read; manage includes both. These implications describe the advertised access contract, not a
required representation of stored policy. Catalogue consumers need neither grant-string parsing nor
knowledge of slash-prefix expansion. Where delegated management uses that expansion, it bounds
administrative authority only: a path prefix entails no RDF containment, data membership or domain
relationship. A policy engine can compute the same results without storing Context grant strings.
The exact client authorization/delegation exchange remains #69's separate decision.

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

Recommend `https://schema.sempods.org/module/contexts` as the new module identity, initially
`0.1-dev`. It covers Context identities, registry reads, Context-granular rights and their discovery,
explicit data selection and the [existing proposed selector outcomes](data-access.md#optional-context-contracts).
The lifecycle module keeps `https://schema.sempods.org/module/context-management` and its own version.
At adoption its revised development contract depends on `contexts` `0.1-dev`; publishing either
component follows governance and records the supported dependency version. Neither identity is
allocated or advertised by this proposal merge. A development version alone does not identify an
immutable contract; adoption and implementation evidence also name the source revision.

Use the existing conformance response fields, for example after adoption:

```json
{
  "specVersion": "0.1-dev",
  "modules": [
    {"id": "https://schema.sempods.org/module/contexts", "version": "0.1-dev"},
    {"id": "https://schema.sempods.org/module/context-management", "version": "0.1-dev"}
  ]
}
```

A pod can advertise neither module, `contexts` alone, or both. Advertising lifecycle without its
compatible Context dependency is an invalid conformance claim. A client discovers capabilities
through this response; it does not infer them from stored RDF or probe management routes. An
unsupported Context input retains the proposed `400` outcome. No additional discovery field,
policy-management API or general version-negotiation scheme is introduced.

For the full core/module adoption, zero registered Contexts is valid. Authorized ordinary resource
creation without a selector adds unassigned data while the registry can remain empty. Read, find
and SPARQL expose that data within the caller's authority; without consent the write is `403`.
Provisioning supplies no authority, and a core client need not create or select a Context.
[The data-access cases](data-access.md#two-implementation-examples) define the ordinary operations.
#69's authentication iteration still owes the exact authorization-request profile that realizes
this outcome. Context-level authority alone does not authorize an ordinary replacement across other
graphs and unassigned statements. The initial RDF delivery retains the current minimum-count rules.

A single physical graph can implement this module by preserving logical memberships separately.
It can expose one stable, provisioned Context with the same registry description as any other.
That identity covers only its named membership: it cannot alias the entire aggregate. An ordinary
addition remains unassigned; a selected addition belongs to the Context. Removing that membership
leaves any unassigned occurrence intact. A store unable to preserve this distinction can implement
core alone. Physical storage never justifies a different observable graph or mutation result.

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
resource-read authorization and can yield `404` while `GET C` succeeds, or vice versa. This link
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
| `sps:writableContext` | Registered Contexts for which the Context-level write condition allows the caller. |
| `sps:manageableContext` | Registered Contexts for which the Context-level manage condition allows the caller. |

These three properties replace a composite grant literal with a relation whose predicate identifies
the mode and whose object is the Context IRI. They introduce no policy nodes, mode ontology or
separate rights endpoint. Emit the complete sets for registered, visible Contexts, including implied
modes; empty sets have no triples. Do not enumerate absent descendants or hypothetical namespace
roots. Evaluate the requesting client/subject and credential/delegation ceilings, including any
applicable public read; never substitute the person's broader authority or a token's contents.

A Context is visible in this registry when the caller has at least one of these Context-level modes.
Additional policies can restrict individual operations and data visibility. Each relation therefore
reports a Context-layer authorization result for this request; `sps:writableContext` does not promise
that replacing a predicate blocked by another policy will succeed. It is not a stored-policy export
or a capability. Copying the RDF grants nothing, and the later request is authorized again. These
mode implications leave independent core data read/write policies possible.

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

The full optional-Context adoption additionally changes deletion and empty-pod behavior below;
these effects depend on the aggregate dataset contract and are not part of the initial RDF delivery.

Deleting C removes its registry entry and its named memberships. Other Context memberships,
unassigned occurrences and independent descendants survive. Grants tied specifically to the deleted
Context cease to authorize a later re-created C; independent ancestor-management authority remains
subject to its own revocation. This describes the revocation outcome without prescribing how a
store removes or invalidates policy. Lifecycle authorization covers the target's entire
administrative effect. A finer policy denying ordinary writes to a resource does not, by itself,
prevent an authorized administrator from deleting
its Context membership. Further restrictions on the administrative action can deny that action as
a whole, independently of whether protected data is present. Never decide deletion by scanning for
hidden statements the caller could not edit: that would reveal their presence through success or
failure. An allowed deletion completes all effects; failure leaves them unapplied. Other advertised
modules retain their coordinated lifecycle obligations, such as media assignments. An authorized
DELETE returns `204` for an existing target, `404` for an absent one. No last-Context count or automatic replacement Context is required.

## Request cases

These are proposed HTTP expectations, not executed conformance tests. Unless stated otherwise,
credentials are valid, requests are well-formed, C is private and registered, and further policies
allow the operation. Repeat discovery cases with empty and nonempty graphs.

| Setup and request | Expected response/effect |
|---|---|
| Core-only pod; conformance GET, then authorized ordinary resource PUT | No Context modules; `201` without registry setup or selection. A Context selector gives `400`. |
| Context module, empty registry; catalogue GET, then consented ordinary resource PUT | Empty RDF collection `200`; write `201`, unassigned data, registry still empty. No consent: write `403`. |
| Context module without lifecycle; client discovers modules | Registry/selection available; client does not assume management support. |
| Read caller; GET L and GET C | L links C through `readableContext` only; C description `200`, with no caller rights. |
| Write caller; GET L, GET C, selected data PUT | L links C through `readableContext` and `writableContext`; same C description; data write succeeds. Lifecycle PUT/DELETE remains `403`. |
| Manage caller; GET L, GET C, lifecycle PUT for C/sub | All three modes for C, same description; new child `201` when lifecycle is advertised. No absent child is listed before creation. |
| No-access caller; GET L, C and absent X | C/X omitted from L, both direct GETs `404` with no distinguishing validators or links. |
| Public C, anonymous GET L and C | L links C through `readableContext`; C description `200`. Invalid supplied credential: `401`. |
| Read revoked after GET C with tag E; GET C with `If-None-Match: E` | `404`. Authorized unchanged request: `304`. |
| Writer stores ordinary `<C> sps:public true` while registry says false | Ordinary system-resource read can show true; registry GET still false with unchanged tag; no policy change. Repeat where only one of these two reads is authorized. |
| Visible empty C; GET L, C and SPARQL `ASK { GRAPH <C> {} }` | L contains C, description `200`, query false because its named projection is omitted. |
| Manage caller; create absent C with the existing ContextCreate JSON `{"label":"Tasks"}` | `201`, RDF description, public false. Repeat or submit another label to existing C: `200` with unchanged registry state. |
| Same caller; create absent C without a body, then repeat on existing C | `201` with private defaults, then `200` unchanged. No metadata-edit capability is implied. |
| Non-manager; well-formed PUT/DELETE C versus absent X, including conditional requests | Uniform `403`, no existence signal or effect. Invalid credential is `401`. |
| Lifecycle PUT C with `?context=C` | `400`, no creation or change. |
| Manage caller deletes the last C | `204`, empty registry; ordinary unassigned data remains usable. Old grants tied to C do not revive on recreation. |
| Authorized administrator deletes C; a triple also has an unassigned occurrence and membership in registered C/sub | `204`, C membership removed; unassigned occurrence and C/sub survive. |
| Same administrative authority; delete C with versus without a hidden resource whose ordinary data writes are denied | Both `204`, complete deletion of C membership. A policy denying the administrative action itself gives uniform `403`, also for an absent target. |
| One physical graph, one synthetic Context C; ordinary addition then selected addition | First remains unassigned, second belongs to C. Selected removal cannot remove the unassigned occurrence. |
| GET C with Accept N-Quads; GET L with Accept JSON-LD | Same registry meaning in RDF; L's grant summary stays on L. Rights are never added to C. |
| GET C or L with only `Accept: application/json` after RDF adoption | RDF JSON-LD under the existing media-type alias, no legacy Context/ContextList DTO. |
| Local query above on retrieved catalogue/description RDF, with and without C's label | Returns C in both cases; optional label when present, no grant-string parsing. |
| An ordinary data graph asserts `L sps:writableContext C` for a caller lacking write | The trusted catalogue has no such link; the selected write is still `403`. |
| Context-capable server; ordinary SPARQL `FROM <C>` | Authorized data in C, no registry URL fetch or injection of registry metadata. A registry query endpoint is not implied by Context discovery. |
| C has child path C/sub and the same task IRI occurs in both graphs | No domain relation or RDF containment is inferred from the path; membership and selected effects remain independent. |
| Write revoked but read retained; conditional catalogue GET with its former strong tag | Updated representation omits `writableContext` C and is not `304` for that tag. |

## Delivery boundary and adoption impact

Recommend two bounded deliveries, with their work and dependency records owned by #90/#69 and
[#68](https://github.com/sempods/sempods-spec/issues/68):

| Delivery | Observable scope and prerequisite |
|---|---|
| RDF Context surface | On the current Context model, migrate GET C, GET L and successful creation representations to the registry RDF and structured caller summary above. Preserve current Context identity/membership, selector semantics, creation input/effects, minimum-count/deletion rules and grant semantics. Agree on text, OpenAPI, vocabulary, HTTP cases and the server/client migration together. No new optional-module claim. |
| Optional Context contract | After #69's authentication/delegation decisions, adopt the smaller core, module discovery/dependency, aggregate/unassigned semantics, bootstrap and deletion effects with matching artifacts and validation under #70–#74. |

The first delivery does not require metadata editing, a registry query service, a new policy engine
or the full core migration. Its read/summary cases can be checked against the current Context model;
aggregate, zero-Context and revised deletion cases belong to the second delivery. Normative changes
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
discovery and component versions, graph membership/deletion effects and revocation wording.
CTX-028/029's minimum-count rules go at that stage; CTX-025/026's authority separation and private
defaults remain. The [data-access impact inventory](data-access.md#requirement-changes-to-prepare)
owns the wider core change. Both deliveries keep chapter text and contract artifacts consistent.
This proposal changes none of them and allocates no vocabulary or module identifiers.
