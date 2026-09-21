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

The proposal reduces core and adds one optional `contexts` module for selection, discovery and
lifecycle. The default-access decision below fixes one coherent ordinary data surface and states
its acceptance cases for review under #69. The examples and requirement impact allocate no
identifiers and make no conformance claim. Requirement selection follows
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
`cc41031a5c844d0bcf431d2e5221364182579083`, including its adopted RDF registry surface. They bind the
[mutation recommendations](access-control.md#mutations-and-partial-representations) to a logical
scope, while remaining **proposed**. Current Context selection and query rules continue to bind
until coordinated adoption.

Use [RDF 1.1 Concepts, 25 February 2014, §4](https://www.w3.org/TR/2014/REC-rdf11-concepts-20140225/#section-dataset)
and [SPARQL 1.1 Query, 21 March 2013, §13](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#rdfDataset)
for datasets and query semantics, and
[SPARQL 1.1 Protocol, 21 March 2013, §2.1.4](https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#dataset)
for dataset selection on the existing query POST route. This does not add Update, federation or
other HTTP query forms. Those standards leave the service's default dataset to the service. The
implicit scope, mutation placement and local-only graph resolution below are sempods choices.

#### Recommended implicit scope

Recommend one implicit logical data scope per pod, called **D** in the examples. Core resource and
slot reads, mutations, find (including expansion) and the SPARQL default graph use D when the client
makes no explicit selection. Read filtering applies within D; it does not shrink the complete scope
that a later mutation must be authorized to change. Core clients need no Context identity or setup.

The implementation supplies D and its insertion destination. D can be backed by a default Context,
a single graph or distributed storage. It is a coherent source-data scope with defined mutation
effects, not an arbitrary read-only view paired with an unrelated write target. The ordinary API
exposes neither a required name nor a configuration protocol for it. Resolve the same D across the
ordinary routes; do not choose another scope according to HTTP method, a resource's existence,
hidden collisions or an authorization failure. A successful allowed write is visible through the
ordinary read/query surface when that caller also has read authority and the state is unchanged.
Find evaluates matches and expansion within that same authorized scope; this does not prescribe
its matching algorithm, ranking or a result for every newly written resource.

Registering additional Contexts does not enlarge D. A separately selected A or B can hold statements
about the same resource IRI without contributing them to ordinary reads or mutations. The resource
IRI still identifies the same thing; its returned description depends on the requested scope.
A module may expose D under a Context IRI, but core requires neither that name nor its registration.
Explicit independent scopes and computed projections have the effects described below.

The tradeoff is deliberate: a core-only client does not automatically search every Context merely
because it may read them. It gets one coherent ordinary data surface. The alternative of reading
all Contexts while writing only a default target can leave old values after PUT; globally replacing
all those scopes broadens the write effect. The four cases below define the proposed resolution
for #69. Accepting these cases settles this data-scope choice; authentication, delegation and full Context
lifecycle remain separate decisions before normative adoption.

#### Four default-access decisions

D, A and B are independently mutable scopes in this fixture; A and B are outside D. C is explicitly
a computed view over D. Policies allow the stated reads and complete writes, including observing
existence. Each case starts fresh. Requests carry valid credentials, use the existing routes and
media types, and omit Context selectors unless stated. PUT bodies in these four cases contain at
least one outgoing statement; empty input and denied requests are covered separately below.

#### Default-access acceptance sequences

Use `R = https://example.org/pod/tasks/one`, `p = https://schema.org/name`,
`a = https://example.org/assignee`, `Alice = https://example.org/alice` and
`Bob = https://example.org/bob`. In the table, `p="old"` abbreviates the triple
`R p "old"`; `a=Alice` abbreviates `R a Alice`. An incoming link is a triple
`https://example.org/pod/inbox https://schema.org/hasPart R`. Neither these application terms nor
the names D/A/B/C are new sempods vocabulary. Wire bodies use full IRIs, for example:

```json
{
  "@id": "https://example.org/pod/tasks/one",
  "https://schema.org/name": [{"@value": "new"}]
}
```

Each row is a sequential scenario using R's LOD route; reset before the next row. Compare RDF
assertions, not JSON array order. Replacement success may use the existing `200` or `204` form.
The query probe is
`SELECT ?v WHERE { <https://example.org/pod/tasks/one> <https://schema.org/name> ?v }` on the existing
SPARQL POST route. Its results below refer to that bare pattern; a query explicitly selecting a
named graph can see separately authorized data outside D.

| Initial state | Requests and proposed observations |
|---|---|
| D has no outgoing R statements; no Context is registered | PUT `p="new"` → `201`, Location R. GET → `200`, exactly `p="new"`; query probe → `"new"`. Repeat PUT with `p="changed"` → replacement success; GET/query contain only `"changed"`. No registry request, Context IRI or Context-module support is required. |
| D has no outgoing R statements; A has `p="a"` | GET → `404`; query probe → no rows; resource DELETE → `404`. PUT `p="new"` → `201`, Location R. GET/query now expose only `"new"`. Authorized A-selected GET still exposes `"a"`. The earlier DELETE has not changed A. |
| D has `p="old"` and the incoming link; A has `p="a"`, B has `p="b"` | PUT `p="new"` → replacement success. GET/query expose only `"new"`; A/B still expose `"a"`/`"b"`. Resource DELETE → `204`; GET → `404`, query probe → no rows. The incoming link and A/B assertions remain; repeating resource DELETE → `404`. |
| D has the incoming link but no outgoing R statements; A has `p="a"`; computed C selects all outgoing statements of D subjects with `a=Alice` | PUT `p="new", a=Alice` → `201`. Ordinary and C-selected GET expose those two triples. PATCH `a=Bob` → success; ordinary GET exposes `p="new", a=Bob`, C-selected GET → `404`, and `GRAPH <C>` has no outgoing R statements. Resource DELETE → `204`; ordinary GET → `404`. The incoming link and A's independent assertion remain. |

Repeat the ordinary operations through their system aliases with the same data effects. For each
system-layer resource creation, expect Location to name the system-layer resource route for R,
as specified by [`SPS-CRUD-043`](../../spec/core/lod-crud.md#SPS-CRUD-043); the RDF identity remains R.
This route-specific expectation also applies when repeating the conditional cases below.
For find, compare against the same engine on D's authorized fixture: change only independent A/B
assertions and verify that ordinary matches, ranking and expansion are unaffected. This checks
scope without prescribing search recall.
For C, compare its selected representation and named query projection after each source change;
materialization may not supply a stale successful result.

#### Authorization and conditional boundaries

These cases apply the existing [mutation recommendations](access-control.md#mutations-and-partial-representations)
to D through R's LOD route; they introduce no permission type or credential claim. A refusal leaves
source assertions and dependent projections unchanged. Each row starts fresh, and authorization permits the complete
operation and observation of D unless the row narrows it.

| Setup and request | Proposed observation |
|---|---|
| R exists only in independent A; ordinary nonempty PUT with `If-None-Match: *` | `201`, Location R, creation in D. A's existence does not make the precondition false and A remains unchanged. |
| R exists in D; ordinary nonempty PUT with `If-None-Match: *` | `412`, D and A/B unchanged. |
| R exists only in A; ordinary resource DELETE with `If-Match: *` | `404`, no change. The ordinary not-found response precedes precondition evaluation. |
| Caller may write A but has no applicable D write authority; ordinary PUT/PATCH/DELETE, with or without conditions | Uniform `403`, whether R is absent, visible or hidden. No retry against A, automatic registration or fallback; conditional fields do not grant authority. |
| D contains unreadable values of p; caller may edit only visible values; ordinary PUT or PATCH replacing p | Uniform `403`, also in the counterpart with those hidden values absent under the same authority. Complete-scope authority is required; filtering GET does not narrow the replacement. |
| Caller can completely replace D's R but cannot observe its existence; ordinary nonempty PUT | Uniform `403`, with no Location or validator. The `201`/replacement distinction cannot reveal unreadable existence. Uniform slot operations retain their separately defined blind-write cases. |
| Whole-resource write is allowed; unconditional PUT containing only R's `@id` | `204`, no Location or validator, whether D's R was empty or populated. Outgoing R statements in D are cleared; incoming links and independent A/B survive. GET → `404`; no persistent resource marker is created. |
| D has `p="old"`; read its ordinary representation and obtain ETag E; change only independent A with D's representation and authorization inputs unchanged; conditional ordinary GET/PUT using E | A's change alone does not invalidate E: GET with `If-None-Match: E` → `304`; a permitted PUT with `If-Match: E` succeeds. Use a representation that does not include A's membership; graph-aware variants follow their represented data. |
| Current D write permission is revoked after GET returned E; PUT with `If-Match: E` | `403`, even if the representation and tag are unchanged. An ETag does not preserve authority. |
| C is the computed read-only view above; caller can edit D and manage C; valid C-selected PUT/PATCH/DELETE | Uniform `403`, including absent targets and no-ops. Sources and the view definition remain unchanged. A separately authorized ordinary write can edit D. |

The fixture permissions describe admission to the complete effect, not the mere absence of a
protected triple. Test denied mutations against empty and populated counterparts under the same
authority. Cases reaching precondition evaluation assume no intervening change except the one
stated, normal request checks pass and the caller can observe the tested representation. They do not specify an ETag
algorithm or an authorization-state storage mechanism.

#### Framework boundary and validation

RDF supplies graphs and shared identities; SPARQL supplies evaluation of the selected dataset.
[RFC 9110 §9.3.4](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.4) supplies PUT's
creation/replacement response distinction, and
[§13.2.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.2.1) orders preconditions after
normal request checks. The mutation proposal owns PATCH, empty-input and non-disclosure choices.
The additional sempods choice here is which logical assertions those operations address: D for
ordinary requests, the selected view for explicit Context requests. It prevents discovery, HTTP
method or hidden collisions from silently changing the operation's target.

Run the ordinary sequences on a single graph, an internal default Context and an area/document-policy
implementation configured with equivalent D and authority. A/B/C cases require the optional Context
contract; a core-only implementation is tested without those surfaces. Physical partition counts,
policy languages, indexes and view materialization strategies are free. The same IRI may occur in
independent scopes without requiring copies to be reconciled or all scopes to be searched.

These are acceptance cases for [#72](https://github.com/sempods/sempods-spec/issues/72), not an
executed HTTP suite. Logical RDF/query checks can verify the stated projections; they do not prove
HTTP outcomes, find behavior, authorization, atomic mutation or cache isolation. Reviewing this
decision does not allocate requirement IDs, change the adopted registry, advertise `contexts`, or
settle the remaining authentication and lifecycle decisions in #69.

#### Query projections

A Context identifies a logical RDF view whose membership may be stored or computed. Computed views
select existing source statements without adding independent assertions; several views may contain
the same statement. Query evaluation or ACP-based selection needs no physical named graph. Context
IRIs name their query projections, not their storage or policy rules. Core-only pods may expose
native RDF named graphs without assigning them sempods Context semantics.

For the caller, the ordinary SPARQL default graph is D's authorized RDF graph, also used by ordinary
retrieval and find. The named part contains disclosable, nonempty authorized projections of native
graphs and Context views. Those projections can expose separately authorized data outside D through
explicit `GRAPH` patterns or dataset selection; their presence never unions them into the default
graph or expands an ordinary mutation. Context-selected CRUD/find obtains the same authorized
projection as `GRAPH <C>`. Find expansion stays within its selected scope.

The same triple appears once in an RDF graph; SPARQL retains its normal solution multiplicities.
Preserve shared RDF term identity, including blank nodes; unrelated nodes with identical internal
labels remain distinct. An empty or wholly unreadable named projection is omitted, including from
`GRAPH ?g {}`. Registry visibility is separate. A hidden graph name is never inferred from ordinary
reads. Control-plane policy storage and other pods are outside this data space unless an explicit
contract exposes data about them. Test setup specifies D, independent scopes, view definitions,
disclosable names and authorization; physical partitions are not fixture inputs.

#### Writes within the addressed scope

An ordinary resource, predicate, slot or edge mutation affects only the addressed source assertions
in D. PUT replaces that scope's outgoing assertions; PATCH and slot/edge operations retain their
specified narrower effects; incoming links survive resource deletion. Additions go to D's
implementation-supplied insertion destination. Internal placement can use explicit membership;
there is no requirement to strip it or create logically unassigned assertions. Independent A/B
assertions are neither copied into D nor changed by an ordinary write. Existence, Location and
conditional-write evaluation use the addressed scope, never other occurrences of the resource.

A selected write has one supported meaning: the **membership-write contract**. Its addressed
assertion membership is independently mutable; additions join that scope and removals change only
its assertions. Other independent assertions survive. This is also the observable effect when D
is exposed under a Context IRI; an explicit selector does not give broader authority. No physical
named graph or stored grant representation is required.

Reevaluate dependent computed views after a source mutation. An addition can match several views,
an update can leave one and remain in another, and removing its source assertions removes their
computed occurrence. These are projection changes, not additional independent writes. The shared
view contract selects source facts; it defines no inference or CONSTRUCT language that invents facts.

General computed views without the membership-write contract are read-only through selected CRUD.
Omit them from writableContext; after authentication/syntax checks, valid selected writes uniformly
return `403`, including no-ops and absent targets. Do not change source data, rules or grants or
fall back to D. Ordinary CRUD can separately edit sources inside D with the required authority;
sources outside D require their own supported, authorized access. A general write-through contract
covering insertion, shared sources and leaving a view is explicitly deferred.

For either write scope, authority covers its complete direct effect, including unreadable assertions
and additions. Read or view-management permission alone grants no source-write authority. Refusal
is independent of hidden collisions; failed writes leave the effect unapplied. Projections satisfy
the shared authorized-query equivalence. An allowed response and subsequent read reflect the new
state; stale materialization is not an alternative successful effect.

LOD and system aliases agree on data effects and representations for the same mode and scope;
creation Location headers follow the route-specific rule above. A validator identifies that selected
representation: an implicit-scope tag does not validate a Context-selected write, or vice versa, even
when the returned triples coincide. Apply
[RFC 9110 §8.8.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.8.1) to each representation:
a membership-only change may leave the strong tag of the membership-collapsed representation
unchanged only if its representation data remain unchanged. Graph-aware variants, such as
`include_contexts=true` JSON-LD or N-Quads carrying graph names, need a different strong tag when
their represented memberships change. Different representation data cannot share a strong tag
merely because they express the same merged triples. This also applies to slot representations
where validators are emitted; it prescribes no serialization or tag-generation algorithm.

Current complete-scope authority is still checked, and tags never validate unreadable facts or
grant permission. A changed source or view definition can change several computed representations;
each corresponding strong tag changes when its represented data changes. A truly unrelated view's
representation is not invalidated solely through a shared internal revision counter.

#### Query dataset selection

Recommend accepting `FROM`, `FROM NAMED`, `default-graph-uri` and `named-graph-uri` as selectors
over the caller's named graph projection, independently of Context-module support. Resolve IRIs
locally; never fetch a graph from the network or fall back to another pod. D has no mandatory
public graph IRI. Only an actually exposed named projection can be selected by IRI.

When a dataset description is supplied, construct its default graph from the selected default
sources and its named part from the selected named sources, following the cited SPARQL semantics.
In particular, `FROM g` alone supplies no named graph and `FROM NAMED g` alone supplies an empty
default graph. Protocol parameters take precedence over query-text dataset clauses. With neither,
use the ordinary default and named layout above. `GRAPH` narrows the active graph in the
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

#### Additional request cases for review

These supplement the four default-access decisions. D, A and B are independent unless explicitly
identified; named projections and complete writes are authorized unless narrowed. R and p stand for
full resource/predicate IRIs, not relative wire values. Each row starts from its stated data.
These are proposed expectations, not executed HTTP conformance fixtures.

| Setup and request | Recommended result and effect |
|---|---|
| D has R p "same"; A and B independently contain the same triple | Ordinary GET/default-graph COUNT returns one value/count 1. `GRAPH ?g` returns the disclosed A/B names; it does not invent a name for D. |
| A and B contain R p "same"; selected DELETE of R in A | A loses its outgoing assertions; B retains them. Ordinary GET depends only on D. |
| A contains R p "same"; ordinary slot POST of "same", then selected edge DELETE in A | POST adds the assertion in D (`204`); deleting A's independent assertion leaves D's value readable. |
| Authority covers A but not D; ordinary PUT/PATCH R | Uniform `403` whether R exists in D or elsewhere. An allowed selected write in A changes only A and dependent computed projections. |
| D exposed as named Context A; ordinary creation R | Ordinary GET, A-selected GET and `GRAPH <A>` see the same authorized source data. Both write forms address that same source scope, with their respective authorization checks. |
| Hidden data in B changes with authorized projections and policy inputs fixed | Ordinary reads, find and supported query results remain unchanged; no hidden names or facts appear. |
| A is empty, absent or wholly unreadable; `SELECT ?g WHERE { GRAPH ?g {} }` | A is absent from results in all three cases; registry visibility is separate. |
| A contains R p "a", B contains R p "b"; query `FROM <A>` | Bare triple pattern sees "a"; `GRAPH ?g` sees no graphs. D is not added. |
| Same data; query `FROM NAMED <A>` | Default graph empty; `GRAPH <A>` sees "a"; B and D unavailable in that dataset. |
| Query text uses `FROM <A>`; protocol selects B with `default-graph-uri` | Protocol wins; default graph has B's authorized projection, named part empty. |
| Query text uses `FROM <A>`; protocol supplies only `default-graph-uri=` | Both components empty; no fallback to A or D. `ASK {}` is true; a triple-pattern count is 0. |
| Dataset selection names only unknown or non-disclosable graphs | No network fetch; empty selected dataset, standard query results, no existence diagnostic. |
| Ordinary and A-selected reads return identical triples | Representation-scoped tags do not validate a write in the other request scope, even where A exposes D. |
| C and E are computed views over unchanged D; change only C's membership definition | A membership-collapsed ordinary representation can retain its tag if its representation data are unchanged. A graph-aware variant including C changes its strong tag when represented membership changes; matching conditional reads follow those tags. Repeat for slot variants where tags are emitted. |
| C selects Alice's tasks from D; E selects project X's tasks from D; task matches both; ordinary assignee PATCH | D changes; task leaves C but remains in E with the updated assignee. Changed representations receive changed strong tags. |
| Same overlapping views; ordinary resource DELETE of the task | D and both computed projections lose its outgoing assertions; incoming source links and independent assertions outside D survive. |
| Independent A feeds computed C; selected DELETE in A | A's addressed assertions disappear; C reevaluates. Independent D/B assertions survive. |
| C is a computed read-only view; selected PUT/PATCH/slot POST/DELETE, including no-ops | Uniform `403`, no source change or fallback. A separately allowed ordinary mutation addresses D only. |
| Same sources; computed C's selection definition changes | Source assertions stay unchanged. Selected reads/query results and affected representation tags reflect the new definition; registry authority is separate. |

Repeat ordinary cases on a single graph, a Context-based store with implicit default and an
area/document-policy store. Use equivalent D/source assertions, view definitions, exposed names and
authority. Compare computed projections against the authorized source fixture, including overlap
and source/definition changes. Blank-node cases compare RDF identity up to consistent renaming.

## Optional Context contracts

A Context module exposes addressable logical views with stored or computed membership, explicit
selection and caller access discovery. A pod can have internal areas
without offering this contract. An implementation advertising it provides the whole declared
contract; internal terminology alone is insufficient.

[Discoverable Contexts and RDF registry descriptions](context-contract.md) recommends the module
identity/version, integrated lifecycle, implicit access and caller-rights discovery under
[#69](https://github.com/sempods/sempods-spec/issues/69) and
[#90](https://github.com/sempods/sempods-spec/issues/90). It owns the remaining module and lifecycle recommendations. The RDF registry surface is specified
by [Contexts](../../spec/core/contexts.md#SPS-CTX-031) and
[creation responses](../../spec/modules/context-management.md#SPS-CTX-037), under #92. The proposed
selector contract remains below.

The module preserves [ordinary implicit access](#recommended-implicit-scope). An implementation
can expose D as a Context, but clients need not discover or select it for ordinary operations.
Additional Contexts expose separate source scopes or computed views. Internal storage names and
policy-rule IRIs do not automatically become public graph names. The module includes lifecycle and
discovery as one contract; individual Contexts may be read-only, with independently evaluated modes.

Recommend the following selector outcomes after normal authentication and syntax checks:

| Request | Recommended selection and outcome |
|---|---|
| Ordinary CRUD or find without Context fields | Implicit D scope, on both core-only and Context-capable pods. |
| A core-only pod receives a Context selector or Context-output field, including an empty value or `include_contexts=false` | `400` for unsupported Context input; never silently ignore it. |
| Context-capable pod; resource/slot read or find with one or more valid Context IRIs | Union of the requested authorized graph projections; absent/unreadable Contexts contribute nothing. Empty resource selection gives `404`; find gives its ordinary successful empty result. Selection also bounds find expansion. |
| Context-capable pod; resource/slot read or find GET with exactly one empty `context=` parameter, or find POST with `contexts: []` | Explicit empty selection: resource GET is `404`, slot GET is `200` with an empty representation (an array by default), and find returns its successful empty result. No fallback to D. |
| Context-capable pod; write with exactly one valid Context IRI | With the membership-write contract and complete authority, change that scope's assertions and reevaluate dependent views. Otherwise uniform `403`; never reinterpret it as a source/default-scope write. |
| Context-capable pod; malformed nonempty Context IRI, or empty/repeated selector on a write | `400`; write repetition counts occurrences, even identical or empty ones. Nonempty read repetition remains set selection; comma-separated lists are not decoded. |
| Context-capable pod; read with `context=&context=A` or repeated empty values; find POST with an empty array member, such as `contexts: ["", "A"]` or `contexts: [""]`, or with `contexts: null` | `400`. A sole empty GET value encodes the empty list; an empty IRI inside a nonempty list is invalid. Do not drop invalid entries to produce a broader successful request. |
| Context-capable pod; well-formed unknown or unauthorized write selector | Uniform `403`, no mutation or Context registration; a data write does not provision a selected Context. |
| SPARQL query request with a `context` parameter | `400`; use the standard query dataset selectors, whose behavior is independent of Context support. |

For otherwise identical valid find requests, `GET ...?text=note&context=` and
`POST {"text":"note","contexts":[]}` select no data; omitting `context` or `contexts` selects the
implicit D scope in both forms. This preserves
[`SPS-FIND-004`](../../spec/core/find.md#SPS-FIND-004)'s equivalence. The empty GET encoding is shared
by resource and slot reads; writes still require a nonempty target when a selector is present.
The unsupported-input rule still applies on core-only pods, including these empty forms.

Context-grouped output labels only disclosable projection membership, whether stored or computed.
An assertion outside all disclosed projections remains unlabelled. A label reports view membership,
not physical provenance or an independent copy; it never exposes a hidden graph name.
The representation needs alignment with the existing find output at normative adoption.

Context IRIs resolve consistently across the module's surfaces. Canonical IRIs remain accepted;
any supported relative Context paths resolve before selection. SPARQL dataset IRIs follow the
standard's IRI resolution and identify those same logical graphs by absolute IRI. Knowing a graph
name, or seeing a Context rights hint, never substitutes for authorizing an operation. The
[module proposal](context-contract.md) supplies their discovery and lifecycle boundary; it allocates
no normative identifier or additional discovery field.

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
resource and slot routes where the same effect is expressible. A system-layer resource creation
returns its system-layer route in Location, following
[`SPS-CRUD-043`](../../spec/core/lod-crud.md#SPS-CRUD-043). Check stale validators and denied writes.
Query and `find` see the authorized data, including additions and removals. The adapter
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
dataset, with the same implicit D scope, graph placement and names. Cases include aggregates, negation, subqueries
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
| [`SPS-CORE-004`](../../spec/core/index.md#SPS-CORE-004)–[`SPS-CORE-006`](../../spec/core/index.md#SPS-CORE-006) | Keep indivisible core and modules; move all Context selection, discovery and lifecycle into one optional contexts module; preserve ordinary implicit access. |
| [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001)–[`SPS-CTX-003`](../../spec/core/contexts.md#SPS-CTX-003) | Define optional Contexts as stored or computed logical views. Separate explicit assertion membership from computed projection, preserve ordinary access and permit other policy models. |
| [`Contexts`](../../spec/core/contexts.md) namespace and discovery requirements | Move Context naming, selection support and the permissions catalogue to the module. No synthetic Context requirement in core. |
| [`SPS-CTX-017`](../../spec/modules/context-management.md#SPS-CTX-017)–[`SPS-CTX-019`](../../spec/modules/context-management.md#SPS-CTX-019) | At full adoption, deleting a Context unregisters its view and withdraws Context-bound authority, retaining source assertions and independent authority. Preserve current destructive deletion in the earlier response-only RDF delivery. |
| [`SPS-CTX-028`](../../spec/core/contexts.md#SPS-CTX-028) | Remove the remaining minimum registered count for pods without context-management when adopting the Context-free core. |
| [`SPS-CTX-025`](../../spec/core/contexts.md#SPS-CTX-025), [`SPS-CTX-026`](../../spec/core/contexts.md#SPS-CTX-026), [`SPS-CTX-030`](../../spec/core/contexts.md#SPS-CTX-030) | Preserve core protection of control-plane authority and explicit public access; generalize their subjects beyond Contexts. Data about a control-plane IRI remains data. |
| [`Grants`](../../spec/core/grants.md) grammar, `manage` expansion and mode implications | Separate Context read, data-write and view-management authority. Keep legacy mode implications in their compatibility scope, without inferring write ability from management of a computed view. Retain core delegation, revocation and enforcement independently of stored grant grammar. |
| [`SPS-GRANT-020`](../../spec/core/grants.md#SPS-GRANT-020)–[`SPS-GRANT-022`](../../spec/core/grants.md#SPS-GRANT-022), [`SPS-GRANT-031`](../../spec/core/grants.md#SPS-GRANT-031), [`SPS-GRANT-032`](../../spec/core/grants.md#SPS-GRANT-032), [`SPS-AUTH-042`](../../spec/core/auth.md#SPS-AUTH-042)–[`SPS-AUTH-044`](../../spec/core/auth.md#SPS-AUTH-044) | Apply the [public-read recommendation](access-control.md#public-access-and-public-read): retain the additive scope, public reads without credentials and invalid-credential rejection; permit public-only issuance without currently public data. Bound public access by the requested data scope and coordinate credential migration, discovery and OpenAPI. |
| [`SPS-GRANT-002`](../../spec/core/grants.md#SPS-GRANT-002), [`SPS-GRANT-018`](../../spec/core/grants.md#SPS-GRANT-018), [`SPS-AUTH-063`](../../spec/core/auth.md#SPS-AUTH-063) | Apply the [consent/credential race guarantee](access-control.md#consent-and-credential-races) to session-only tokens and refresh families, including forced reauthorization. Retain client/subject isolation while freeing storage lookup and write/check sequencing. |
| [`SPS-GRANT-025`](../../spec/core/grants.md#SPS-GRANT-025), [`SPS-CRUD-007`](../../spec/core/lod-crud.md#SPS-CRUD-007)–[`SPS-CRUD-014`](../../spec/core/lod-crud.md#SPS-CRUD-014) | Define ordinary source-data mutations and view reevaluation; selected writes use the explicit membership-write contract, with read-only computed views otherwise. Replace the blanket multi-Context write prohibition with complete effects within D or the explicitly selected scope. Keep invalid selectors from being ignored. |
| [`SPS-CRUD-015`](../../spec/core/lod-crud.md#SPS-CRUD-015)–[`SPS-CRUD-017`](../../spec/core/lod-crud.md#SPS-CRUD-017), [`SPS-CORE-017`](../../spec/core/index.md#SPS-CORE-017) | Move Context downscoping, silent exclusion of unreadable Contexts and selector syntax to the module. Retain the core resource-read `404` and indistinguishability of absent and inaccessible data, expressed without a Context prerequisite. |
| [`SPS-CRUD-020`](../../spec/core/lod-crud.md#SPS-CRUD-020)–[`SPS-CRUD-022`](../../spec/core/lod-crud.md#SPS-CRUD-022), [`SPS-CRUD-031`](../../spec/core/lod-crud.md#SPS-CRUD-031), [`SPS-CRUD-035`](../../spec/core/lod-crud.md#SPS-CRUD-035), [`SPS-CRUD-039`](../../spec/core/lod-crud.md#SPS-CRUD-039) | Apply the implicit/selected operation scopes and the mutation recommendations, including partial visibility and hidden collisions. |
| [`SPS-CRUD-002`](../../spec/core/lod-crud.md#SPS-CRUD-002), [`SPS-CRUD-029`](../../spec/core/lod-crud.md#SPS-CRUD-029), [`SPS-CRUD-034`](../../spec/core/lod-crud.md#SPS-CRUD-034), [`SPS-CRUD-050`](../../spec/core/lod-crud.md#SPS-CRUD-050)–[`SPS-CRUD-052`](../../spec/core/lod-crud.md#SPS-CRUD-052), [`SPS-CRUD-057`](../../spec/core/lod-crud.md#SPS-CRUD-057) | Keep resource/slot representation and validator agreement, including graph-aware variants; separate Context-specific provenance and selection rules. Preserve the existing edge DELETE surface. |
| [`SPS-SPARQL-006`](../../spec/core/sparql.md#SPS-SPARQL-006)–[`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009), [`SPS-FIND-009`](../../spec/core/find.md#SPS-FIND-009), [`SPS-FIND-014`](../../spec/core/find.md#SPS-FIND-014) | Specify an authorized view across query and retrieval; replace the rewrite prohibition with outcome equivalence. Keep supported SPARQL read-only and dataset clauses unable to widen access; review the blanket ban on other implementation write interfaces. |
| [`SPS-SPARQL-007`](../../spec/core/sparql.md#SPS-SPARQL-007), [`SPS-SPARQL-010`](../../spec/core/sparql.md#SPS-SPARQL-010)–[`SPS-SPARQL-014`](../../spec/core/sparql.md#SPS-SPARQL-014) | Apply the implicit default graph, independent named projections, implementation-supplied placement within D and local query dataset selection. Replace the empty-result shortcut with standard evaluation on empty datasets; align protocol precedence and empty selections in the chapter and OpenAPI. |
| [`SPS-FIND-004`](../../spec/core/find.md#SPS-FIND-004), [`SPS-FIND-009`](../../spec/core/find.md#SPS-FIND-009), [`SPS-FIND-010`](../../spec/core/find.md#SPS-FIND-010), [`SPS-FIND-013`](../../spec/core/find.md#SPS-FIND-013) | Keep equivalent GET/POST forms and strict parsing in core. Put `context`/`contexts` fields and downscoping through expansion in the module. Preserve GET/POST equivalence for absent, empty and nonempty selections, and reject unsupported Context fields on core-only pods. |
| [`SPS-FIND-019`](../../spec/core/find.md#SPS-FIND-019), [`SPS-FIND-024`](../../spec/core/find.md#SPS-FIND-024) | Move `include_contexts` and Context-grouped output rules to the module. Retain the separation of transient result metadata from stored facts in core, without requiring named-graph provenance. |
| [`SPS-FIND-015`](../../spec/core/find.md#SPS-FIND-015), [`SPS-FIND-021`](../../spec/core/find.md#SPS-FIND-021) | Preserve successful empty search results and caller-sensitive cache isolation in core using the authorized data view. Apply empty Context downscopes only where the module supplies that selector. |
| [`Auth`](../../spec/core/auth.md), especially [`SPS-AUTH-008`](../../spec/core/auth.md#SPS-AUTH-008), [`SPS-AUTH-011`](../../spec/core/auth.md#SPS-AUTH-011)–[`SPS-AUTH-013`](../../spec/core/auth.md#SPS-AUTH-013), [`SPS-AUTH-024`](../../spec/core/auth.md#SPS-AUTH-024) | Apply the remaining [authorization recommendation and impact map](access-control.md#authorization-without-context-setup), including Context-free consent/service authority and S256 PKCE. Use the [service-client boundary](access-control.md#service-clients-and-registration-authority) instead of prescribing an operator, provisioning interface or fixed registration-time grants; preserve the unauthenticated profile's exclusion from service access. Preserve the current conditional state echo in [`SPS-AUTH-025`](../../spec/core/auth.md#SPS-AUTH-025), adopted separately by [PR #105](https://github.com/sempods/sempods-spec/pull/105). Complete the remaining identity/discovery/profile decisions before adoption. |
| [`SPS-MCP-017`](../../spec/modules/mcp.md#SPS-MCP-017), [`SPS-MCP-020`](../../spec/modules/mcp.md#SPS-MCP-020), [`SPS-MEDIA-006`](../../spec/modules/media.md#SPS-MEDIA-006), [`SPS-MEDIA-009`](../../spec/modules/media.md#SPS-MEDIA-009) | Align optional tools and media with the new core; do not make either implicitly require the Context module. Specify Context-specific integration where both are advertised. |
| [`SPS-CORE-018`](../../spec/core/index.md#SPS-CORE-018) | Generalize context-existence protection to the proposed policy-independent write scope, including hidden-resource collisions. |

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

- Review the [default-access resolution and acceptance sequences](#four-default-access-decisions)
  together with the [mutation recommendations](access-control.md#mutations-and-partial-representations)
  and remaining dataset/selector cases. Preserve coherent D access, independent assertions and
  computed projections when preparing their coordinated requirements. General write-through computed
  views remain deferred until their discoverable update contract is defined.
- Review the [authorization cases](access-control.md#authorization-request-cases) for consent, bounded
  delegation, public-read and revocation against both examples. Complete the remaining
  [identity/discovery/profile decisions](access-control.md#adoption-impact-and-remaining-profile-work)
  and coordinate the credential transition before claiming a complete interoperable profile.
- Review the [Context registry and lifecycle recommendations](context-contract.md) with the
  [selection behavior](#optional-context-contracts). The authentication profile must realize their
  ordinary bootstrap outcome without requiring a core client to create or select a Context. Review
  independent view-management/data authority and non-destructive unregistration, including retained
  source authorization and media lifecycle, before the full module adoption.
- Define conformance fixtures with known allowed and denied data for both implementation models.
  Always returning `403` or an empty graph is not evidence of conformance. Test query semantics and
  revocation using implementation-specific setup but the same public operations.

Spec [#36](https://github.com/sempods/sempods-spec/issues/36) and
[#37](https://github.com/sempods/sempods-spec/issues/37), and implementation
[#80](https://github.com/sempods/sempods-kotlin/issues/80), motivate this broader split. Their
flag/default-context proposals need reconciliation with the implicit-scope decision; this proposal
adds no core flag or required Context identity. Stable identities across versions remain
[#21](https://github.com/sempods/sempods-spec/issues/21)'s concern. Solid interoperability and a
complete sync protocol remain separate follow-up work; this proposal makes neither claim.
