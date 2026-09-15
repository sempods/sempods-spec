# Discoverable Contexts and RDF registry descriptions

Status: **Proposed; non-normative.**
Owning issues: [#69](https://github.com/sempods/sempods-spec/issues/69) for the module boundary and
[#90](https://github.com/sempods/sempods-spec/issues/90) for registry descriptions and their lifecycle.
Adoption: [#68](https://github.com/sempods/sempods-spec/issues/68), through its coordinated normative
preparation and validation. This document recommends decisions; merging it changes no contract.

## Scope and standards

A Context-aware client needs to discover named authorization areas, their descriptions and its
context-level rights. Ordinary clients continue to use the
[aggregate data contract](data-access.md#logical-dataset-and-operation-scope) without this module.
The choices below apply the [vision's selection test](../vision.md#what-belongs-in-the-contract):
agree on those observable meanings and their security boundaries; leave policy representation,
physical graphs, provisioning and administrative interfaces to implementations.

The baseline is the proposal and current contract at
[`303d8aa`](https://github.com/sempods/sempods-spec/tree/303d8aa3acf3d7838e7c1a7062a705ab958d7954).
Reuse the existing canonical JSON-LD/N-Quads profile and RFC 9110 for negotiation, validators,
conditional requests and PUT. [RDF Schema 1.1](https://www.w3.org/TR/2014/REC-rdf-schema-20140225/)
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

Zero registered Contexts is valid, including after deletion of the last one. Authorized setup can
supply ordinary data authority while the registry is empty. With consent covering an ordinary
resource creation, `PUT P/notes/one` without a Context selector succeeds and adds logically
unassigned statements; subsequent ordinary GET, find and SPARQL can read them within the caller's
authority. The registry can remain empty. No implicit selected Context, application call to Context
management, or invented pod-root Context grant is part of that flow. Without the requisite consent,
the same write is `403`; provisioning alone supplies no authority.

How a person supplies that consent and how a pod stores/enforces it remain separate from the
Context registry. The [authentication iteration](https://github.com/sempods/sempods-spec/issues/69)
still owes the exact authorization-request profile; this recommendation fixes its required empty-pod
outcome, not an alternative OAuth flow. Context grants describe only Context scope and do not, by
themselves, authorize an ordinary replacement across other graphs and unassigned statements.

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
| `dcterms:created` | Optional single `xsd:dateTime` creation instant when known; preserve it on metadata replacement. No invented date or required storage mechanism. |
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
C's data graph. These generated descriptions and the catalogue are outside the ordinary pod data
space, including ordinary SPARQL. The Context IRI identifies a named data graph while GET at that
IRI describes its registry entry; reading its data uses the selected data surfaces.

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

This reuses the graph vocabulary already needed for the entries. It avoids an LDP container's
additional protocol contract and needs no Hydra collection machinery. A bare list of Context
subjects would lack an explicit collection identity and membership relation. Registry membership
can include an empty Context; the SPARQL named projection still omits graphs with no readable
triples, as the dataset proposal specifies.

Put caller rights on the **catalogue subject**, using one further candidate property:
`sps:effectiveGrant`, with string values in the Context grant grammar `<context-iri>#read|write|manage`.
For each listed Context, report every effective Context-level mode, including the read implied by
write and both modes implied by manage. Expand only over registered, visible Contexts, not absent
descendants or hypothetical namespace roots. Evaluate the requesting client/subject and applicable
credential/delegation ceilings; never report the person's broader authority or decode a token as a
grant list. Public Context-level read contributes `#read` for a caller to whom it applies.

A Context is visible in this registry when the caller has at least one such Context-level mode.
Other policy conditions can further restrict individual operations and data visibility. An effective
mode is therefore a current Context-level authorization result, not a stored-policy export or a
capability: copying the RDF grants nothing. Every later operation is authorized again. In
particular, a listed `#write` need not permit replacing a predicate blocked by an additional policy.
These Context-mode implications leave independent core data read/write policies possible.

No suitable standard property was identified for this request-relative Context grant summary.
`acl:Authorization` would represent a policy rule; [`acl:Control` and WAC-Allow](https://solidproject.org/TR/2024/wac-20240512#access-privileges)
use WAC modes, where control of an ACL does not imply read/write on the resource. Mapping sempods
`manage` to that mode would change its meaning. HTTP `Allow` describes methods, not the caller's
Context authority. Retaining one catalogue summary avoids a per-Context OPTIONS discovery sequence
and introduces neither WAC adoption nor another rights endpoint.

For a caller with write authority on C, a complete catalogue can be:

```json
{
  "@id": "https://example.org/alice/_system/contexts",
  "@type": ["http://www.w3.org/ns/sparql-service-description#GraphCollection"],
  "http://www.w3.org/ns/sparql-service-description#namedGraph": [{"@id": "https://example.org/alice/_system/contexts/tasks"}],
  "https://schema.sempods.org/effectiveGrant": [
    {"@value": "https://example.org/alice/_system/contexts/tasks#read"},
    {"@value": "https://example.org/alice/_system/contexts/tasks#write"}
  ]
}
```

The same C description is returned to read, write and manage callers; the catalogue summary differs.
A caller with no visible Contexts receives `200` with L's identity and collection type, no members
and no grants. Unauthenticated callers see only their public Context view; invalid supplied
credentials still produce `401`. A missing C and an existing C without visibility both give `404`,
without distinguishing bodies, links or validators, including conditional reads.

Registry responses use `Vary: Accept` for negotiated representations. Recommend
`Cache-Control: private, no-cache` for individual descriptions, including hidden/absent responses:
reusing a stored response requires revalidation with current authorization, and a revoked caller's
matching `If-None-Match` gets `404`, never `304`. Use `Cache-Control: no-store` for the caller-scoped
catalogue and errors; emit no catalogue validators. The collection's URI alone cannot identify its
caller-specific RDF snapshot. Consumers keep its rights in that request's context and refresh them
when needed. These directives specify wire behavior, not a cache implementation; neither caches nor
validators can prolong authority. Individual tags track registry representation changes, not data
contents, ordinary assertions about C, or the caller's grant set.

## Lifecycle

Recommend a canonical JSON-LD metadata body for `PUT C` on pods advertising context-management.
An optional body uses `application/ld+json`, the target C as `@id`, and only `rdfs:label`,
`dcterms:description`, and `sps:public` as writable predicates. Labels/descriptions accept sets of
plain or language-tagged strings; public accepts one Boolean. An optional `@type` names only
`sd:NamedGraph`. Reject unknown predicates, wrong types/cardinalities, a different subject, nested
nodes/graphs or a JSON-LD context with `400`; unsupported body media types give `415`. No body
means empty metadata and private visibility. A present body needs the canonical subject object.
Server-derived `sd:name`, `dcterms:created` and `rdfs:seeAlso` are read-only and rejected in input.
This is metadata creation/replacement, not a general RDF write into the registry.

Use standard [RFC 9110 PUT semantics](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.4):
first creation returns `201`; replacing metadata on an existing Context returns `200`, both with
the negotiated registry description. Omitted optional metadata is removed; omitted public is
false. The Context identity, data, existing grants and known creation date survive replacement.
An identical repeated request leaves state unchanged. This deliberately replaces CTX-016's
create-only `200` that silently ignores differing input. A client wanting creation without
replacement uses `If-None-Match: *`; an existing authorized target then yields `412`.

Creation does not imply authority to choose public access beyond the authorized management scope.
Retain owner or delegated slash-bounded `manage` authorization, including the authority to create
an as-yet absent descendant. Validate authentication and request syntax normally; outside management
authority, well-formed PUT/DELETE returns uniform `403` for existing and absent targets, before
conditional checks. The lifecycle routes reject a `context` parameter with `400`; data selection
never changes a control-plane target. A successful PUT returns `Location: C` on creation; it omits
validators because input is transformed by defaults and derived registry fields. GET supplies the
representation validator for a subsequent conditional metadata replacement.

Deleting C removes its registry entry and its named memberships. Other Context memberships,
unassigned occurrences and independent descendants survive. Grants tied specifically to the deleted
Context cease to authorize a later re-created C; independent ancestor-management authority remains
subject to its own revocation. This describes the revocation outcome without prescribing how a
store removes or invalidates policy. Lifecycle authorization covers the target's entire administrative effect. A finer policy denying
ordinary writes to a resource does not, by itself, prevent an authorized administrator from deleting
its Context membership. Further restrictions on the administrative action can deny that action as
a whole, independently of whether protected data is present. Never decide deletion by scanning for
hidden statements the caller could not edit: that would reveal their presence through success or
failure. An allowed deletion completes all effects; failure leaves them unapplied. Other advertised
modules retain their coordinated lifecycle obligations, such as media assignments. An authorized DELETE returns `204` for an existing target,
`404` for an absent one. No last-Context count or automatic replacement Context is required.

## Request cases

These are proposed HTTP expectations, not executed conformance tests. Unless stated otherwise,
credentials are valid, requests are well-formed, C is private and registered, and further policies
allow the operation. Repeat discovery cases with empty and nonempty graphs.

| Setup and request | Expected response/effect |
|---|---|
| Core-only pod; conformance GET, then authorized ordinary resource PUT | No Context modules; `201` without registry setup or selection. A Context selector gives `400`. |
| Context module, empty registry; catalogue GET, then consented ordinary resource PUT | Empty RDF collection `200`; write `201`, unassigned data, registry still empty. No consent: write `403`. |
| Context module without lifecycle; client discovers modules | Registry/selection available; client does not assume management support. |
| Read caller; GET L and GET C | L contains C and only `C#read`; C description `200`, with no caller rights. |
| Write caller; GET L, GET C, selected data PUT | L contains `C#read` and `C#write`; same C description; data write succeeds. Lifecycle PUT/DELETE remains `403`. |
| Manage caller; GET L, GET C, lifecycle PUT for C/sub | All three modes for C, same description; new child `201` when lifecycle is advertised. No absent child is listed before creation. |
| No-access caller; GET L, C and absent X | C/X omitted from L, both direct GETs `404` with no distinguishing validators or links. |
| Public C, anonymous GET L and C | L reports `C#read`; C description `200`. Invalid supplied credential: `401`. |
| Read revoked after GET C with tag E; GET C with `If-None-Match: E` | `404`. Authorized unchanged request: `304`. |
| Writer stores ordinary `<C> sps:public true` while registry says false | Ordinary system-resource read can show true; registry GET still false with unchanged tag; no policy change. Repeat where only one of these two reads is authorized. |
| Visible empty C; GET L, C and SPARQL `ASK { GRAPH <C> {} }` | L contains C, description `200`, query false because its named projection is omitted. |
| Manage caller; `PUT C` for absent C, body `{"@id":"https://example.org/alice/_system/contexts/tasks","http://www.w3.org/2000/01/rdf-schema#label":[{"@value":"Tasks"}]}` | `201`, `Location: C`, RDF description, public false, no validator. Repeat: `200` with same state. |
| Same caller; PUT existing C with label Changed, then PUT with no body | `200`, new label; then `200`, label removed and private. Data, identity and grants survive. |
| Same caller; PUT existing C with `If-None-Match: *`; conditional PUT with stale GET tag | Both `412`, no metadata or policy change. |
| Non-manager; well-formed PUT/DELETE C versus absent X, including conditional requests | Uniform `403`, no existence signal or effect. Invalid credential is `401`. |
| Authorized PUT C with two public values, another subject, or caller-rights predicate | `400`, no creation or change. `?context=C` also gives `400`. |
| Manage caller deletes the last C | `204`, empty registry; ordinary unassigned data remains usable. Old grants tied to C do not revive on recreation. |
| Authorized administrator deletes C; a triple also has an unassigned occurrence and membership in registered C/sub | `204`, C membership removed; unassigned occurrence and C/sub survive. |
| Same administrative authority; delete C with versus without a hidden resource whose ordinary data writes are denied | Both `204`, complete deletion of C membership. A policy denying the administrative action itself gives uniform `403`, also for an absent target. |
| One physical graph, one synthetic Context C; ordinary addition then selected addition | First remains unassigned, second belongs to C. Selected removal cannot remove the unassigned occurrence. |
| GET C with Accept N-Quads; GET L with Accept JSON-LD | Same registry meaning in RDF; L's grant summary stays on L. Rights are never added to C. |
| GET C or L with only `Accept: application/json` after adoption | RDF JSON-LD under the existing media-type alias, no legacy Context/ContextList DTO. |

## Transition and adoption impact

Recommend replacing the legacy `Context`, `ContextList` and `ContextCreate` JSON shapes at coordinated
adoption, with no required dual-serving interval. `Accept: application/json` follows the existing
RDF read alias and returns `application/ld+json`; it does not select the legacy DTO. For lifecycle
input, legacy JSON DTO bodies cease to be accepted by this module version. Ordinary RDF negotiation
handles unsupported Accept values with `406`. Implementations can stage migration to the adopted
revision, but an advertisement of this contract means the RDF behavior is available in full.
General version coexistence remains [#21](https://github.com/sempods/sempods-spec/issues/21)'s work.

This is a breaking recommendation: clients need RDF catalogue parsing and caller-scoped grants;
metadata PUT now replaces supplied state, so create-only callers need a conditional request. Current
Kotlin context readers, MCP `list_contexts`, and the work tracked by Kotlin #166/#174 need coordinated
migration. The ContextList required-property candidate in spec #77 needs reassessment against the
replacement schema, not a patch to an obsolete DTO.

Normative preparation needs coordinated Context/module chapters, CTX-015/016 and CTX-021–024,
registry/data separation, deletion effects and revocation wording, the Context-grant parts of the
grants/auth chapters, core/module discovery and versions, OpenAPI, the two candidate RDF predicates,
the index and downstream consumers. CTX-028/029's minimum-count rules go; CTX-025/026's authority
separation and private defaults remain. The
[data-access impact inventory](data-access.md#requirement-changes-to-prepare) owns the wider core
change. This document chooses no additional policy-management interface and changes none of those
normative artifacts. #69 retains authentication and delegation decisions; #90 owns review of these
registry recommendations, with adoption and integrated conformance validation still separate.
