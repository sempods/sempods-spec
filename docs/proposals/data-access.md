# Authorized data access

Status: **Proposed; non-normative.**
Owning issue and adoption: [#68](https://github.com/sempods/sempods-spec/issues/68).
The design was introduced by [#52](https://github.com/sempods/sempods-spec/pull/52); its merge did
not adopt it. [#69](https://github.com/sempods/sempods-spec/issues/69) owns unresolved contract
choices, [#70](https://github.com/sempods/sempods-spec/issues/70) their normative preparation, and
[#72](https://github.com/sempods/sempods-spec/issues/72) validation against that candidate.

## Purpose

A pod exposes linked data through a common, authorized interface: federated authentication,
LOD CRUD, SPARQL and `find`. An application can use that interface without adopting the pod's
storage layout or permission model. A single RDF graph and a platform with several independent
policy conditions can implement the same data operations.

The proposal reduces core and makes the Context contract optional. The examples and requirement
impact below allocate no identifiers and make no conformance claim. Requirement selection follows
[the vision](../vision.md#what-belongs-in-the-contract).

## The specified boundary

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

## The proposed core

Core specifies the observable data contract and the guarantees of its authorization. Policy
evaluation and administration belong to the implementation. The
[access-control proposal](access-control.md) owns those guarantees and the difficult operation
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

### Logical dataset and operation scope

These are the dataset recommendations for
[#69](https://github.com/sempods/sempods-spec/issues/69), against merged revision
`3b8cb0a08e4476d4dcf0fad850171844ad7296ba`. They bind the
[mutation recommendations](access-control.md#mutations-and-partial-representations) to a logical
scope, while remaining **proposed**. Current Context selection and query rules continue to bind
until coordinated adoption.

Use [RDF 1.1 Concepts, 25 February 2014, §4](https://www.w3.org/TR/2014/REC-rdf11-concepts-20140225/#section-dataset)
and [SPARQL 1.1 Query, 21 March 2013, §13](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#rdfDataset)
for datasets and query semantics, and
[SPARQL 1.1 Protocol, 21 March 2013, §2.1.4](https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#dataset)
for dataset selection on the existing query POST route. This does not add Update, federation or
other HTTP query forms. Those standards leave the service's default dataset to the service. The
aggregate view, mutation placement and local-only graph resolution below are sempods choices.

#### Ordinary access uses the aggregate graph

Recommend one logical data space per pod. Statements can be unassigned to a named graph or occur
in one or more logical named graphs. These are observable memberships, independent of physical
partitions. A core-only pod can have no named graphs; exposing a native RDF graph does not by
itself promise Context grants or management. Logical names exposed through SPARQL are IRIs.

For a caller, the ordinary SPARQL default graph is the set union of all readable statements in
that space, including readable statements from named graphs. Ordinary resource/slot/edge reads
and find use that same aggregate graph. The same triple occurring in two graphs appears once in
the aggregate; SPARQL still applies its normal solution multiplicities. Preserve logical RDF term
identity, including shared blank nodes; unrelated nodes do not become equal because two storage
partitions use the same local label.

The named part of the dataset contains the authorized projections of logical named graphs whose
names may be disclosed and whose projections are nonempty. `GRAPH` operates on that named part,
not on internal partitions or the unassigned statements. An empty or wholly unreadable graph is
omitted, including from `GRAPH ?g {}`. This avoids requiring a persistent empty-graph registry in
core; Context lifecycle and rights discovery remain separate. A readable statement whose graph
name cannot be disclosed can still occur in the aggregate, without exposing its membership.

This default layout lets an ordinary client find authorized data without graph discovery. A graph
name is additional observable information, not a new permission. A supplied name cannot reveal
more than the caller's projection. Control-plane policy storage and other pods are outside this
logical data space unless an explicit contract exposes data about them.

#### Writes have an observable graph effect

Without a Context selector, resource, predicate, slot and edge scopes span the whole logical data
space, before read filtering. Apply their specified removals to every occurrence in that scope.
An ordinary DELETE cannot report removal while leaving another occurrence of the same triple in
a named graph. New statements from an ordinary write are logically unassigned: they appear in the
aggregate, but do not acquire named-graph membership. A request body does not choose a graph;
existing accepted-input rules still apply.

Replacement removes the previous memberships of the replaced statements and inserts the supplied
statements unassigned, even when a supplied value equals an old value. Predicate/slot operations
preserve other predicates; resource replacement covers all outgoing statements. Incoming statements
survive both. Slot POST adds an unassigned occurrence and preserves all
existing occurrences; repeating it is idempotent, including when the same triple also occurs in a
named graph. This placement rule prevents implementation-specific routing from changing later
`GRAPH` results. It requires no physical default context, registry entry or public IRI.

A Context-selected write instead has exactly that graph as its scope; additions stay in it and
other graphs, including unassigned statements, are unchanged. Its readable effects also appear in
the aggregate. Removing one occurrence can therefore leave the same triple in an ordinary read
when another occurrence survives. Subject identity and graph selection remain independent.

In either mode, authorization covers the complete requested effect, including removals and the
placement of additions. Authority over one graph alone cannot authorize an ordinary whole-space
replacement. Apply the mutation proposal's uniform refusal even when other graphs currently hold
no matching statements; do not choose a writable graph by inspecting hidden collisions. An
implementation may retain Context-based policies and storage, but needs an authorized realization
of ordinary operations as well as any selected operations it advertises.

LOD and system aliases agree for the same mode and scope. A validator identifies that selected
representation: an aggregate tag does not validate a Context-selected write, or vice versa, even
when the returned triples coincide. Aggregate resource tags validate the aggregate representation,
not named-graph membership; a membership-only change need not alter them. Current complete-scope
authority is still checked, and tags never validate unreadable facts or grant permission. A selected
graph's changes cannot invalidate an unrelated graph's representation solely through a shared
internal revision counter.

#### Query dataset selection

Recommend accepting `FROM`, `FROM NAMED`, `default-graph-uri` and `named-graph-uri` as selectors
over the caller's named graph projection, independently of Context-module support. Resolve IRIs
locally; never fetch a graph from the network or fall back to another pod. The unnamed aggregate
has no graph IRI a client can fabricate to select it.

When a dataset description is supplied, construct its default graph from the selected default
sources and its named part from the selected named sources, following the cited SPARQL semantics.
In particular, `FROM g` alone supplies no named graph and `FROM NAMED g` alone supplies an empty
default graph. Protocol parameters take precedence over query-text dataset clauses. With neither,
use the ordinary aggregate/default and named layout above. `GRAPH` narrows the active graph in the
resulting dataset; it cannot reach graphs excluded by that dataset description.

Unknown and non-disclosable graph IRIs contribute nothing, with no diagnostic; omit them from the
named part rather than manufacturing empty named graphs. A present-but-empty protocol parameter
is an empty selection for that occurrence, not absence of selection. Other valid occurrences still
contribute to their respective components. Reject malformed nonempty graph IRIs with `400`;
repeated identical IRIs do not duplicate a graph. Never fall back to the ordinary dataset when
all requested graphs are excluded. This profiles graph resolution and empty-input handling rather
than restating the SPARQL algebra.

Evaluate the resulting dataset using
[SPARQL §18.6](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#sparqlAlgebraEval), even when it
contains no statements. An empty dataset does not mean every query has zero solutions: `ASK {}` is true and `COUNT(*)` over a triple
pattern is zero. Use those standard results rather than a synthetic empty-response shortcut.

#### Request cases for review

Let `R` be `https://example.org/alice/notes/one`, `p` be `https://schema.org/name`, and `A` and `B`
be distinct logical graph IRIs supplied by test setup. Each row starts from its stated initial data. Unless narrowed,
policy allows reading the named graphs and complete writes over the stated scope. These are
proposed acceptance cases, not executable fixtures or an implementation conformance report.

| Setup and request | Recommended result and effect |
|---|---|
| Empty pod with no named graphs; ordinary PUT R with p = "new" | `201`; ordinary GET and `SELECT ?v WHERE { <R> <p> ?v }` see "new". `GRAPH ?g { <R> <p> ?v }` has no match. Repeat the PUT: `200`/`204`, with no graph membership created. |
| R p "same" in both A and B; ordinary GET and `SELECT (COUNT(*) AS ?n) WHERE { <R> <p> ?v }` | One value and count 1. `SELECT ?g WHERE { GRAPH ?g { <R> <p> "same" } }` returns A and B. |
| R p "same" in A and B; authorized Context-selected DELETE of R in A | A loses R's outgoing statements; B retains them and ordinary GET still returns "same". |
| R p "same" in A and B; authorized ordinary DELETE of R | All occurrences of R's outgoing statements disappear, in A, B and unassigned data; incoming links survive. Ordinary GET is `404` and the corresponding triple patterns match nothing. |
| R p "old" in A and B; complete ordinary PUT R with p = "new" | Aggregate contains only "new" for R; neither A nor B contains outgoing statements of R. "new" is unassigned. |
| R p "same" in A; ordinary slot POST of "same", then selected edge DELETE in A | POST is `204` and adds an unassigned occurrence without changing A; after selected deletion ordinary GET still sees "same", while A has no such triple. |
| Authority covers only A; ordinary PUT or PATCH over R | Uniform `403` both with and without matching protected occurrences elsewhere. A selected write can succeed under A's authority without changing B. |
| Ordinary PUT creates R unassigned; selected PUT of R with p = "other" in A | Selected creation is `201` when A had no outgoing statements of R, regardless of ordinary existence. Aggregate includes both contributions; selected GET contains only A's. |
| Hidden data in B changes, with the caller's readable data and policy inputs fixed | Ordinary reads, find matches and supported query results remain unchanged; B contributes no unreadable names or facts. |
| A's readable projection is empty, or A is absent/unreadable; `SELECT ?g WHERE { GRAPH ?g {} }` | A is absent from the results in all three cases. Context registry visibility is a separate request. |
| R p "a" in A, R p "b" in B; query with `FROM <A>` | Bare triple pattern sees "a"; `GRAPH ?g` sees no graphs. |
| R p "a" in A, R p "b" in B; query with only `FROM NAMED <A>` | Bare triple pattern matches nothing; `GRAPH <A>` sees "a". |
| Readable nonempty A and B; query text uses `FROM <A>`; protocol supplies only `named-graph-uri=B` | Default graph is empty; only B is a named graph. Query-text A does not widen the protocol dataset. |
| Query text uses `FROM <A>`; protocol supplies only `default-graph-uri=` | Both dataset components are empty. No fallback to A or the aggregate; `ASK {}` is true and a triple-pattern count is 0. |
| Only absent/unreadable IRIs selected, including an external HTTPS IRI | Empty dataset with ordinary query semantics, no fetch and no existence diagnostic. `GRAPH <missing> {}` has no match. |
| Same returned triples through ordinary and A-selected GET | Each tag is scoped to its representation; a tag from one scope cannot satisfy `If-Match` for the other. |

`<R>`, `<p>`, `<A>` and `<B>` in these query sketches stand for the full IRIs, not relative IRIs
sent on the wire. Repeat ordinary-operation cases on a single graph, a Context-based store and an
area/document-policy store. Repeat named-graph cases where that logical data is exposed, with
identical graph names and membership; storage partitions are not fixture inputs. Blank-node cases
compare RDF identity up to consistent renaming, not response-local labels.

## Optional Context contracts

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
  setup. In the Context module, decide how owner consent supplies authority for ordinary aggregate
  operations and unassigned additions, including on an empty pod. Internal placement does not turn
  that request into a graph-selected write. Provisioning cannot manufacture authority or require
  that application to call a management API it does not use.
- **A client querying its grants.** The Context module can keep `GET {pod}/_system/contexts` and
  its context-level rights. A single-graph implementation offering that module can synthesize one
  stable Context identity. A core-only implementation owes no such object. Where further policies
  can narrow access within a Context, the catalogue describes the context-level authority rather
  than guaranteeing every operation inside it.

The module preserves the [ordinary aggregate access](#logical-dataset-and-operation-scope) and
provides selection of its Context graphs. An ordinary write can leave statements logically
unassigned even in a pod offering Contexts; the module does not require every core statement to
belong to a public Context. An internal Context used to store those statements is not automatically
a graph name in the logical dataset. This revises the proposed universal membership rule even
within a Context-capable pod, not merely the location of the current chapter.

Recommend the following selector outcomes after normal authentication and syntax checks:

| Request | Recommended selection and outcome |
|---|---|
| Ordinary CRUD or find without Context fields | Aggregate scope, on both core-only and Context-capable pods. |
| A core-only pod receives a Context selector or Context-output field, including an empty value or `include_contexts=false` | `400` for unsupported Context input; never silently ignore it. |
| Context-capable pod; resource/slot read or find with one or more valid Context IRIs | Union of the requested authorized graph projections; absent/unreadable Contexts contribute nothing. Empty resource selection gives `404`; find gives its ordinary successful empty result. Selection also bounds find expansion. |
| Context-capable pod; find POST with `contexts: []` | Explicit empty selection and a successful empty find result. Omitting the field selects the aggregate; `null` is invalid input. |
| Context-capable pod; write with exactly one valid Context IRI | Only that graph is the operation scope. Apply the shared mutation authorization, precondition and response rules. |
| Context-capable pod; empty/malformed Context IRI, or repeated selector on a write | `400`; repetition counts occurrences, even identical or empty ones. Read repetition remains set selection; comma-separated lists are not decoded. |
| Context-capable pod; well-formed unknown or unauthorized write selector | Uniform `403`, no mutation or Context registration; a data write does not provision a selected Context. |
| SPARQL query request with a `context` parameter | `400`; use the standard query dataset selectors, whose behavior is independent of Context support. |

Context-grouped output labels only disclosable named memberships. Unassigned statements remain
unlabelled; requesting provenance does not invent a Context for them or expose a hidden graph name.
The representation needs alignment with the existing find output at normative adoption.

Context IRIs resolve consistently across the module's surfaces. Canonical IRIs remain accepted;
any supported relative Context paths resolve before selection. SPARQL dataset IRIs follow the
standard's IRI resolution and identify those same logical graphs by absolute IRI. Knowing a graph
name, or seeing a Context rights hint, never substitutes for authorizing an operation. The exact
module identity/version, lifecycle dependency and bootstrap/rights flows remain decisions under
#69; this iteration allocates no discovery field or module IRI.

## Two implementation examples

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
[access control](access-control.md#operation-boundaries).

## Mirroring data

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

## Requirement changes to prepare

The entries below identify the coordinated normative change, not changes applied by this document.
Move only the Context-specific parts: general authentication and authorization guarantees remain
core. The table identifies affected contracts; it is not a completed dependency inventory.
The [normative preparation issue](https://github.com/sempods/sempods-spec/issues/70) requires a full
chapter and cross-reference sweep before the normative patch is complete.

| Current contract | Proposed disposition |
|---|---|
| [`SPS-CORE-004`](../../spec/core/index.md#SPS-CORE-004)–[`SPS-CORE-006`](../../spec/core/index.md#SPS-CORE-006) | Keep indivisible core and modules; change core membership and specify the Context/lifecycle dependency. |
| [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001)–[`SPS-CTX-003`](../../spec/core/contexts.md#SPS-CTX-003) | Move Context identity and selected-graph membership to the optional contract. Permit unassigned core statements even on Context-capable pods, and remove the universal prohibition on other permission models. |
| [`Contexts`](../../spec/core/contexts.md) namespace and discovery requirements | Move Context naming, selection support and the permissions catalogue to the module. No synthetic Context requirement in core. |
| [`SPS-CTX-028`](../../spec/core/contexts.md#SPS-CTX-028), [`SPS-CTX-029`](../../spec/modules/context-management.md#SPS-CTX-029) | Remove the minimum registered count and last-visible-context deletion refusal. |
| [`SPS-CTX-025`](../../spec/core/contexts.md#SPS-CTX-025), [`SPS-CTX-026`](../../spec/core/contexts.md#SPS-CTX-026), [`SPS-CTX-030`](../../spec/core/contexts.md#SPS-CTX-030) | Preserve core protection of control-plane authority and explicit public access; generalize their subjects beyond Contexts. Data about a control-plane IRI remains data. |
| [`Grants`](../../spec/core/grants.md) grammar, `manage` expansion and mode implications | Move Context-specific policy semantics to the module. Retain core delegation bounds, revocation, public-access rules and server enforcement, expressed independently of this grammar. |
| [`SPS-GRANT-020`](../../spec/core/grants.md#SPS-GRANT-020)–[`SPS-GRANT-022`](../../spec/core/grants.md#SPS-GRANT-022), [`SPS-GRANT-031`](../../spec/core/grants.md#SPS-GRANT-031), [`SPS-GRANT-032`](../../spec/core/grants.md#SPS-GRANT-032), [`SPS-AUTH-042`](../../spec/core/auth.md#SPS-AUTH-042)–[`SPS-AUTH-044`](../../spec/core/auth.md#SPS-AUTH-044) | Preserve unauthenticated public reads and rejection of invalid credentials. Decide whether `public-read` survives, its authenticated/anonymous token behavior, current-policy evaluation and revocation semantics, and the replacement for the public-Context existence test. Align OAuth discovery and OpenAPI. |
| [`SPS-GRANT-002`](../../spec/core/grants.md#SPS-GRANT-002), [`SPS-GRANT-018`](../../spec/core/grants.md#SPS-GRANT-018), [`SPS-AUTH-063`](../../spec/core/auth.md#SPS-AUTH-063) | Retain client/subject isolation and revocation-race outcomes; review prescribed storage lookups and write/check sequences as implementation mechanisms. |
| [`SPS-GRANT-025`](../../spec/core/grants.md#SPS-GRANT-025), [`SPS-CRUD-007`](../../spec/core/lod-crud.md#SPS-CRUD-007)–[`SPS-CRUD-014`](../../spec/core/lod-crud.md#SPS-CRUD-014) | Define ordinary authorized resource operations in core; put explicit Context selection and Context-local effects in the module. Replace the blanket multi-Context write prohibition with complete aggregate-operation effects. Keep invalid selectors from being ignored. |
| [`SPS-CRUD-015`](../../spec/core/lod-crud.md#SPS-CRUD-015)–[`SPS-CRUD-017`](../../spec/core/lod-crud.md#SPS-CRUD-017), [`SPS-CORE-017`](../../spec/core/index.md#SPS-CORE-017) | Move Context downscoping, silent exclusion of unreadable Contexts and selector syntax to the module. Retain the core resource-read `404` and indistinguishability of absent and inaccessible data, expressed without a Context prerequisite. |
| [`SPS-CRUD-020`](../../spec/core/lod-crud.md#SPS-CRUD-020)–[`SPS-CRUD-022`](../../spec/core/lod-crud.md#SPS-CRUD-022), [`SPS-CRUD-031`](../../spec/core/lod-crud.md#SPS-CRUD-031), [`SPS-CRUD-035`](../../spec/core/lod-crud.md#SPS-CRUD-035), [`SPS-CRUD-039`](../../spec/core/lod-crud.md#SPS-CRUD-039) | Apply the aggregate/selected operation scopes and the mutation recommendations, including partial visibility and hidden collisions. |
| [`SPS-CRUD-002`](../../spec/core/lod-crud.md#SPS-CRUD-002), [`SPS-CRUD-029`](../../spec/core/lod-crud.md#SPS-CRUD-029), [`SPS-CRUD-034`](../../spec/core/lod-crud.md#SPS-CRUD-034), [`SPS-CRUD-050`](../../spec/core/lod-crud.md#SPS-CRUD-050)–[`SPS-CRUD-052`](../../spec/core/lod-crud.md#SPS-CRUD-052), [`SPS-CRUD-057`](../../spec/core/lod-crud.md#SPS-CRUD-057) | Keep representation and validator agreement across resource, slot and edge operations; separate Context-specific provenance and selection rules. |
| [`SPS-SPARQL-006`](../../spec/core/sparql.md#SPS-SPARQL-006)–[`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009), [`SPS-FIND-009`](../../spec/core/find.md#SPS-FIND-009), [`SPS-FIND-014`](../../spec/core/find.md#SPS-FIND-014) | Specify an authorized view across query and retrieval; replace the rewrite prohibition with outcome equivalence. Keep supported SPARQL read-only and dataset clauses unable to widen access; review the blanket ban on other implementation write interfaces. |
| [`SPS-SPARQL-007`](../../spec/core/sparql.md#SPS-SPARQL-007), [`SPS-SPARQL-010`](../../spec/core/sparql.md#SPS-SPARQL-010)–[`SPS-SPARQL-014`](../../spec/core/sparql.md#SPS-SPARQL-014) | Apply the proposed aggregate default graph, named projections, unassigned additions and local dataset selection. Replace the empty-result shortcut with standard evaluation on empty datasets; align protocol precedence and empty selections in the chapter and OpenAPI. |
| [`SPS-FIND-004`](../../spec/core/find.md#SPS-FIND-004), [`SPS-FIND-009`](../../spec/core/find.md#SPS-FIND-009), [`SPS-FIND-010`](../../spec/core/find.md#SPS-FIND-010), [`SPS-FIND-013`](../../spec/core/find.md#SPS-FIND-013) | Keep equivalent GET/POST forms and strict parsing in core. Put `context`/`contexts` fields and downscoping through expansion in the module; define rejection of unsupported Context fields so a core-only pod never silently broadens a request. |
| [`SPS-FIND-019`](../../spec/core/find.md#SPS-FIND-019), [`SPS-FIND-024`](../../spec/core/find.md#SPS-FIND-024) | Move `include_contexts` and Context-grouped output rules to the module. Retain the separation of transient result metadata from stored facts in core, without requiring named-graph provenance. |
| [`SPS-FIND-015`](../../spec/core/find.md#SPS-FIND-015), [`SPS-FIND-021`](../../spec/core/find.md#SPS-FIND-021) | Preserve successful empty search results and caller-sensitive cache isolation in core using the authorized data view. Apply empty Context downscopes only where the module supplies that selector. |
| [`Auth`](../../spec/core/auth.md), especially [`SPS-AUTH-013`](../../spec/core/auth.md#SPS-AUTH-013), [`SPS-AUTH-024`](../../spec/core/auth.md#SPS-AUTH-024) | Keep a concrete interoperable authentication/delegation profile; remove universal Context-grant and Context-selection assumptions for people and service clients. |
| [`SPS-MCP-017`](../../spec/modules/mcp.md#SPS-MCP-017), [`SPS-MCP-020`](../../spec/modules/mcp.md#SPS-MCP-020), [`SPS-MEDIA-006`](../../spec/modules/media.md#SPS-MEDIA-006), [`SPS-MEDIA-009`](../../spec/modules/media.md#SPS-MEDIA-009) | Align optional tools and media with the new core; do not make either implicitly require the Context module. Specify Context-specific integration where both are advertised. |
| [`SPS-CORE-018`](../../spec/core/index.md#SPS-CORE-018), [`SPS-CRUD-010`](../../spec/core/lod-crud.md#SPS-CRUD-010) | Preserve non-disclosure independently of policy representation; coordinate the current defect with [#45](https://github.com/sempods/sempods-spec/issues/45). |

The refresh-token baseline includes [#65](https://github.com/sempods/sempods-spec/pull/65):
`SPS-AUTH-058` and `SPS-AUTH-060` are absent. This proposal does not restore their token-issuance
guarantees. The `public-read` existence test above is the separate, still-specified
[`SPS-AUTH-044`](../../spec/core/auth.md#SPS-AUTH-044). Generalizing revocation outcomes also does
not remove the currently binding sequencing in `SPS-AUTH-063`; that needs normative review.

Adoption deliberately changes the Context assumptions in `AGENTS.md` invariants 1–4 and the vision's
core mapping. The replacement invariants protect the caller-authorized data view, write effects and
pod isolation. This is not merely moving a chapter: OpenAPI, module versions, the requirement index,
site discovery examples, MCP schemas and downstream citations need the same review. The
[governance window](../../GOVERNANCE.md) determines whether identifiers may move or change meaning;
external adoption can close it before the tag.

## Decisions before normative adoption

- Review the [dataset and selection recommendations](#logical-dataset-and-operation-scope) together
  with the merged [mutation recommendations](access-control.md#mutations-and-partial-representations).
  Confirm the aggregate effects, unassigned additions and named projections before normative drafting.
- Profile the federated authentication, client identity and delegation flows precisely enough for
  one client to use both examples; "supports OAuth" alone is insufficient. Resolve the
  [`public-read` migration](access-control.md#public-access-and-public-read), including token
  issuance when no data is currently public.
- Complete the Context module identity/version, lifecycle dependency, bootstrap and rights discovery
  against the [proposed selection behavior](#optional-context-contracts). Resolve how authorized
  setup supplies ordinary write authority without requiring a core client to select a Context.
- Define conformance fixtures with known allowed and denied data for both implementation models.
  Always returning `403` or an empty graph is not evidence of conformance. Test query semantics and
  revocation using implementation-specific setup but the same public operations.

Spec [#36](https://github.com/sempods/sempods-spec/issues/36) and
[#37](https://github.com/sempods/sempods-spec/issues/37), and implementation
[#80](https://github.com/sempods/sempods-kotlin/issues/80), motivate this broader split. Their
flag/default-context proposals would be replaced by it. Stable identities across versions remain
[#21](https://github.com/sempods/sempods-spec/issues/21)'s concern. Solid interoperability and a
complete sync protocol remain separate follow-up work; this proposal makes neither claim.
