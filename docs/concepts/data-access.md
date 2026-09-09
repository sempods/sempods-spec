# Authorized data access (Concept)

## Purpose

A pod exposes linked data through a common, authorized interface: federated authentication,
LOD CRUD, SPARQL and `find`. An application can use that interface without adopting the pod's
storage layout or permission model. A single RDF graph and a platform with several independent
policy conditions can implement the same data operations.

This is a **contract proposal (SOLL), not an adopted specification change**. It proposes a smaller
core and an optional Context module. The current normative chapters remain in force. Examples and
the requirement impact below allocate no identifiers and make no conformance claim.

## The specified boundary (IST)

Core currently requires contexts as the authorization boundary
([`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001),
[`SPS-CTX-003`](../../spec/core/contexts.md#SPS-CTX-003)), context-granular grants and their
discovery ([`SPS-CTX-021`](../../spec/core/contexts.md#SPS-CTX-021)), and an explicit context on
every write ([`SPS-CRUD-007`](../../spec/core/lod-crud.md#SPS-CRUD-007)). Only the HTTP lifecycle
surface is optional: [`context-management`](../../spec/modules/context-management.md).

The query sandbox is defined over readable contexts
([`SPS-SPARQL-007`](../../spec/core/sparql.md#SPS-SPARQL-007)) and prohibits enforcing it by query
rewriting ([`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009)). Consequently, removing a
required parameter alone cannot make an implementation with a different authorization model
conformant.

## The proposed core (SOLL)

Core specifies the observable data contract and the guarantees of its authorization. Policy
evaluation and administration belong to the implementation. The
[access-control concept](access-control.md) owns those guarantees and the difficult operation
boundaries; this document owns the core/module split.

| Core provides | An implementation chooses |
|---|---|
| A specified federated authentication and client-authorization flow | Policy language, storage and administrative UI |
| Stable resource identities and defined CRUD effects | Physical storage and internal partitions |
| A caller-authorized RDF dataset for SPARQL and retrieval | How policies produce that authorized view |
| Bounded delegation, revocation and non-disclosing errors | How authorization state is represented |
| Discovery of optional client-facing contracts | Which additional contracts it implements |

Core does not require a Context IRI, a context registry, a context selector, a default-context
designation or a global grant catalogue. There is no `implicitWriteContext` flag: data requests
without a Context selector are the ordinary core interface. Native RDF named graphs do not become
sempods permission objects merely by being present. SPARQL's ordinary dataset model also permits a
default graph with no named graphs ([SPARQL 1.1 §13](https://www.w3.org/TR/sparql11-query/#rdfDataset)).

This is a reduction of required structure, not permission to vary the meaning of an authorized
operation. A successful replacement, a conditional write and a deletion have the same specified
effect across implementations. An implementation can deny an operation under its policy; it cannot
claim success for an incompatible effect. Core remains indivisible, with a conformance suite that
checks allowed operations as well as denied ones.

### Policy is enforced without being exported

The server evaluates the actual caller, client, target and requested operation. Policies may depend
on resource, area, identity or other server-side attributes. A client is not required to fetch or
evaluate those policies. An implementation can expose its own management interface, or implement a
standardized optional one.

An internal ACP evaluator or an additional document restriction does not itself require a module
declaration. A declaration promises a client-facing contract, such as Context selection or policy
management. ACP is a describable language, but its extensible attributes and matching rules need not
be understood by a generic sempods client ([ACP](https://solidproject.org/TR/acp)).

Permission introspection is also distinct from enforcement. A statement such as "this data space is
writable" cannot describe every resource- or payload-dependent policy. Core therefore does not
promise a universal effective-grant list. Any optional rights hint needs a defined target, operation
and scope; it never substitutes for authorizing the later request.

### Data identity and operation scope

Internal partitions do not require clients to choose where an ordinary CRUD operation lands. The
pod resolves the resource and authorizes its specified effect. LOD and system addresses for the same
resource agree, including conditional requests; queries and retrieval expose the same read policy.
Revocation never redirects a retry to a different destination or broadens its authority.

An authorized read may reveal only part of a resource. The write contract must say what replacement
and deletion mean in that case before the normative change is adopted. A read-modify-write must not
silently erase protected statements or mutate only part of what the response claims was changed.
The [operation cases](access-control.md#operation-boundaries-soll) include this and creation at an
IRI already used by hidden data. A smaller core still owes answers to those questions.

## Optional Context contracts (SOLL)

A Context module provides a shared model where applications need it: named authorization areas,
explicit selection, context-granular grants and their discovery. A pod can have internal areas
without offering this contract. An implementation advertising it provides the whole declared
contract; internal terminology alone is insufficient.

The existing `context-management` module can remain a separate lifecycle extension, depending on
the Context module. That dependency, the new module's identity and version, and the distribution of
requirements have to be specified together. No new module IRI or discovery field is allocated here.
Published module IRIs retain their existing identities.

The two Context questions have the following homes:

- **An empty pod and first authorization.** Core requires authorization to access data, not the
  creation of a Context first. Implementations can provision their own structures during authorized
  setup. In the Context module, decide how an application using ordinary core requests is bound to
  a selected area, including owner consent on a pod that has none. Provisioning cannot manufacture
  authority or require that application to call a management API it does not use.
- **A client querying its grants.** The Context module can keep `GET {pod}/_system/contexts` and
  its context-level rights. A single-graph implementation offering that module can synthesize one
  stable Context identity. A core-only implementation owes no such object. Where further policies
  can narrow access within a Context, the catalogue describes the context-level authority rather
  than guaranteeing every operation inside it.

The module must preserve ordinary core CRUD without a selector. A client supplying an unsupported
or invalid Context selector receives a defined error, never a successful request with the selector
ignored. For pods offering selection, settle the relationship between implicit resource operations,
explicit graph selection and merged reads, including validators and repeated resource IRIs. The
module cannot reintroduce mandatory selection for every core client.

## Two implementation examples (SOLL)

These are acceptance cases for a future HTTP conformance suite, not fixtures executed by the current
ACP example runner. They assume policies deliberately configured to allow the stated operations.
That setup can be specific to each implementation; the data requests and expected effects are not.

### One RDF graph

An adapter exposes a single RDF graph. A person authorizes a client through the core flow. No
Context, `#write` grant string or context-discovery request is needed by the protocol. Let
`P = https://example.org/alice` be the pod base; the requests carry that client's valid credential.

| Request | Expected result |
|---|---|
| `PUT P/notes/one`, JSON-LD body `{"@id":"https://example.org/alice/notes/one","https://schema.org/name":[{"@value":"First"}]}` | `201`, `Location: https://example.org/alice/notes/one`; resource created |
| `GET P/notes/one` | `200`, name `First`, strong ETag `E1` |
| `PATCH P/notes/one`, `If-Match: E1`, merge-patch body `{"https://schema.org/name":[{"@value":"Changed"}]}` | Success; the specified property changes |
| `GET P/notes/one` | `200`, name `Changed`, ETag `E2` |
| `DELETE P/notes/one`, `If-Match: E2` | `204` |
| `GET P/notes/one` | `404` |

Requests use the media types already specified for those operations. Repeat against the system
resource and slot routes where the same effect is expressible; check stale validators and denied
writes. Query and `find` see the authorized data, including additions and removals. The adapter
still supplies all core operations; wrapping a graph alone is not a conformance claim.

### Areas combined with document policies

A pod places documents in internal areas and applies both an area condition and a document policy.
For this implementation both must allow. Its own management UI configures them; no Context or ACP
management module is needed solely to enforce the conditions. This composition is an example, not
a required policy architecture for other pods.

With both conditions allowing the operation, the client performs the same sequence above. With a
document hidden, neither direct reads, `find` nor SPARQL expose it. With write authority removed,
the same credential cannot mutate it. No grant catalogue is required to explain these decisions.

The query implementation may enforce policy through SPARQL rewriting. Its results must be
equivalent to evaluating the client's supported query against the same client-visible authorized
dataset, with the same graph placement and names. Cases include aggregates, negation, subqueries
and property paths. Testing compares those outcomes, not query
strings. An implementation that merely filters completed results fails the cases in
[access control](access-control.md#operation-boundaries-soll).

## Mirroring data (SOLL)

A future sync module can mirror readable knowledge into a second pod with its own permission
system. Resource IRIs continue to identify the same things; copy location and source provenance are
separate facts. The destination's rules govern the copy. Transferring RDF does not transfer a policy
or grant authority to change destination permissions.

Fetching resources changed since a source-maintained modification time is a useful first mechanism
where the source supplies such metadata. It does not by itself handle deletion, lost visibility,
timestamp ties or pagination during concurrent writes. A complete mirror needs an authorized change
feed, removal records or periodic reconciliation, with a defined checkpoint rule.

Revocation at the source cannot recall copies already made. Whether an ongoing mirror removes data
that becomes inaccessible is a sync policy to specify; absence from one incremental response is not
evidence of deletion. No sync route, timestamp property or module is standardized by this proposal.

## Requirement changes to prepare (SOLL)

The entries below identify the coordinated normative change, not changes applied by this document.
Move only the Context-specific parts: general authentication and authorization guarantees remain
core. The [adoption roadmap](../roadmaps/core-data-access.md) tracks the remaining work.

| Current contract | Proposed disposition |
|---|---|
| [`SPS-CORE-004`](../../spec/core/index.md#SPS-CORE-004)–[`SPS-CORE-006`](../../spec/core/index.md#SPS-CORE-006) | Keep indivisible core and modules; change core membership and specify the Context/lifecycle dependency. |
| [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001)–[`SPS-CTX-003`](../../spec/core/contexts.md#SPS-CTX-003) | Move Context identity and per-statement Context membership to the optional contract; remove the universal prohibition on other permission models. |
| [`Contexts`](../../spec/core/contexts.md) namespace and discovery requirements | Move Context naming, selection support and the permissions catalogue to the module. No synthetic Context requirement in core. |
| [`SPS-CTX-028`](../../spec/core/contexts.md#SPS-CTX-028), [`SPS-CTX-029`](../../spec/modules/context-management.md#SPS-CTX-029) | Remove the minimum registered count and last-visible-context deletion refusal. |
| [`SPS-CTX-025`](../../spec/core/contexts.md#SPS-CTX-025), [`SPS-CTX-026`](../../spec/core/contexts.md#SPS-CTX-026), [`SPS-CTX-030`](../../spec/core/contexts.md#SPS-CTX-030) | Preserve core protection of control-plane authority and explicit public access; generalize their subjects beyond Contexts. Data about a control-plane IRI remains data. |
| [`Grants`](../../spec/core/grants.md) grammar, `manage` expansion and mode implications | Move Context-specific policy semantics to the module. Retain core delegation bounds, revocation, public-access rules and server enforcement, expressed independently of this grammar. |
| [`SPS-GRANT-020`](../../spec/core/grants.md#SPS-GRANT-020)–[`SPS-GRANT-022`](../../spec/core/grants.md#SPS-GRANT-022), [`SPS-GRANT-031`](../../spec/core/grants.md#SPS-GRANT-031), [`SPS-GRANT-032`](../../spec/core/grants.md#SPS-GRANT-032), [`SPS-AUTH-042`](../../spec/core/auth.md#SPS-AUTH-042)–[`SPS-AUTH-044`](../../spec/core/auth.md#SPS-AUTH-044) | Preserve unauthenticated public reads and rejection of invalid credentials. Decide whether `public-read` survives, its authenticated/anonymous token behavior, current-policy evaluation and revocation semantics, and the replacement for the public-Context existence test. Align OAuth discovery and OpenAPI. |
| [`SPS-GRANT-002`](../../spec/core/grants.md#SPS-GRANT-002), [`SPS-GRANT-018`](../../spec/core/grants.md#SPS-GRANT-018), [`SPS-AUTH-063`](../../spec/core/auth.md#SPS-AUTH-063) | Retain client/subject isolation and revocation-race outcomes; review prescribed storage lookups and write/check sequences as implementation mechanisms. |
| [`SPS-GRANT-025`](../../spec/core/grants.md#SPS-GRANT-025), [`SPS-CRUD-007`](../../spec/core/lod-crud.md#SPS-CRUD-007)–[`SPS-CRUD-014`](../../spec/core/lod-crud.md#SPS-CRUD-014) | Define ordinary authorized resource operations in core; put explicit Context selection, Context-local effects and multi-Context restrictions in the module. Keep invalid selectors from being ignored. |
| [`SPS-CRUD-020`](../../spec/core/lod-crud.md#SPS-CRUD-020)–[`SPS-CRUD-022`](../../spec/core/lod-crud.md#SPS-CRUD-022), [`SPS-CRUD-031`](../../spec/core/lod-crud.md#SPS-CRUD-031), [`SPS-CRUD-035`](../../spec/core/lod-crud.md#SPS-CRUD-035), [`SPS-CRUD-039`](../../spec/core/lod-crud.md#SPS-CRUD-039) | Define reads and mutation scope without Contexts; settle partial visibility and hidden-resource collisions before adoption. |
| [`SPS-CRUD-002`](../../spec/core/lod-crud.md#SPS-CRUD-002), [`SPS-CRUD-029`](../../spec/core/lod-crud.md#SPS-CRUD-029), [`SPS-CRUD-034`](../../spec/core/lod-crud.md#SPS-CRUD-034), [`SPS-CRUD-050`](../../spec/core/lod-crud.md#SPS-CRUD-050)–[`SPS-CRUD-052`](../../spec/core/lod-crud.md#SPS-CRUD-052), [`SPS-CRUD-057`](../../spec/core/lod-crud.md#SPS-CRUD-057) | Keep representation and validator agreement across resource, slot and edge operations; separate Context-specific provenance and selection rules. |
| [`SPS-SPARQL-006`](../../spec/core/sparql.md#SPS-SPARQL-006)–[`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009), [`SPS-FIND-009`](../../spec/core/find.md#SPS-FIND-009), [`SPS-FIND-014`](../../spec/core/find.md#SPS-FIND-014) | Specify an authorized view across query and retrieval; replace the rewrite prohibition with outcome equivalence. Keep supported SPARQL read-only and dataset clauses unable to widen access; review the blanket ban on other implementation write interfaces. |
| [`SPS-SPARQL-007`](../../spec/core/sparql.md#SPS-SPARQL-007), [`SPS-SPARQL-011`](../../spec/core/sparql.md#SPS-SPARQL-011)–[`SPS-SPARQL-014`](../../spec/core/sparql.md#SPS-SPARQL-014) | Define the client-visible default and named graphs, the graph placement observable after ordinary writes, and dataset selection without universal Context identities. Keep physical partitions from determining query semantics. Graph-sensitive cases are adoption blockers. |
| [`Auth`](../../spec/core/auth.md), especially [`SPS-AUTH-013`](../../spec/core/auth.md#SPS-AUTH-013), [`SPS-AUTH-024`](../../spec/core/auth.md#SPS-AUTH-024) | Keep a concrete interoperable authentication/delegation profile; remove universal Context-grant and Context-selection assumptions for people and service clients. |
| [`SPS-MCP-017`](../../spec/modules/mcp.md#SPS-MCP-017), [`SPS-MCP-020`](../../spec/modules/mcp.md#SPS-MCP-020), [`SPS-MEDIA-006`](../../spec/modules/media.md#SPS-MEDIA-006), [`SPS-MEDIA-009`](../../spec/modules/media.md#SPS-MEDIA-009) | Align optional tools and media with the new core; do not make either implicitly require the Context module. Specify Context-specific integration where both are advertised. |
| [`SPS-CORE-018`](../../spec/core/index.md#SPS-CORE-018), [`SPS-CRUD-010`](../../spec/core/lod-crud.md#SPS-CRUD-010) | Preserve non-disclosure independently of policy representation; coordinate the current defect with [#45](https://github.com/sempods/sempods-spec/issues/45). |

Adoption deliberately changes the Context assumptions in `AGENTS.md` invariants 1–4 and the vision's
core mapping. The replacement invariants protect the caller-authorized data view, write effects and
pod isolation. This is not merely moving a chapter: OpenAPI, module versions, the requirement index,
site discovery examples, MCP schemas and downstream citations need the same review. The
[governance window](../../GOVERNANCE.md) determines whether identifiers may move or change meaning;
external adoption can close it before the tag.

## Decisions before normative adoption (SOLL)

- Define the generic write scope for partial resources and hidden-resource collisions, with
  consistent authorization and conditional-request behavior. See [access control](access-control.md).
- Profile the federated authentication, client identity and delegation flows precisely enough for
  one client to use both examples; "supports OAuth" alone is insufficient. Resolve the
  [`public-read` migration](access-control.md#public-access-and-public-read), including token
  issuance when no data is currently public.
- Define the [client-visible dataset layout](access-control.md#queries-and-retrieval), including
  ordinary writes, `GRAPH`, dataset clauses and optional Context selection. Equivalent triples alone
  do not define equivalent query results.
- Specify the Context module boundary, lifecycle dependency, unknown-selector errors and how it
  preserves ordinary core requests. Bootstrap and Context-rights discovery are module questions.
- Define conformance fixtures with known allowed and denied data for both implementation models.
  Always returning `403` or an empty graph is not evidence of conformance. Test query semantics and
  revocation using implementation-specific setup but the same public operations.

Spec [#36](https://github.com/sempods/sempods-spec/issues/36) and
[#37](https://github.com/sempods/sempods-spec/issues/37), and implementation
[#80](https://github.com/sempods/sempods-kotlin/issues/80), motivate this broader split. Their
flag/default-context proposals would be replaced by it. Stable identities across versions remain
[#21](https://github.com/sempods/sempods-spec/issues/21)'s concern. Solid interoperability and a
complete sync protocol remain separate follow-up work; this concept makes neither claim.
