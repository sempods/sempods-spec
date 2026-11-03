# SPARQL

The query surface: read-only, sandboxed by the server, and the route for questions that cross
resources or contexts within one pod.

**This chapter is new writing.** It existed in the reference implementation only as fragments across
three documents, one of which deferred to a "SPARQL surface" document that was never written. It was
assembled from those fragments and from the implementation, which is why it carries more than any
one of them did.

**Status: this text decides, and can still change.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: SPARQL 1.1 Query and the SPARQL 1.1 Protocol. The optional service description in §6 uses
[SPARQL 1.1 Service Description, 21 March 2013](https://www.w3.org/TR/2013/REC-sparql11-service-description-20130321/)
§2 and the §3 terms it needs. Error codes are [`index.md`](index.md) §5; what a caller may read is
[`grants.md`](grants.md).

## 1. Read-only, and why that is structural

<a id="SPS-SPARQL-001"></a>
**`SPS-SPARQL-001`** — An implementation MUST offer `POST {pod}/_system/sparql/query`, accepting
`application/sparql-query`.

<a id="SPS-SPARQL-002"></a>
**`SPS-SPARQL-002`** — The SPARQL surface MUST be read-only. An implementation MUST NOT offer a
SPARQL Update endpoint, and MUST reject every Update form — `INSERT`, `DELETE`, `LOAD`, `CLEAR`,
`CREATE`, `DROP`, `COPY`, `MOVE`, `ADD` — anywhere in a submitted query.

<a id="SPS-SPARQL-003"></a>
**`SPS-SPARQL-003`** — Rejection MUST be decided by **parsing** the query against the SPARQL grammar.
An implementation MUST NOT decide it by searching the query text for keywords.

A substring search misclassifies in both directions, and both are damaging. A literal containing the
word `INSERT` is refused although it is an ordinary read; and a keyword split across the constructs
the grammar allows is admitted although it writes. Parsing gets both right for free, because a
literal is a literal to a parser.

<a id="SPS-SPARQL-004"></a>
**`SPS-SPARQL-004`** — A query that does not parse as a read query MUST be refused, and the refusal
MUST NOT distinguish a malformed query from an Update.

An implementation cannot reliably tell the two apart without a second parse against the Update
grammar, and the safe direction is not to try. Reporting "this is an Update" separately from "this
is malformed" tells a prober which of the two it wrote, and the only path forward for a caller is a
valid read query either way.

<a id="SPS-SPARQL-005"></a>
**`SPS-SPARQL-005`** — `SERVICE` MUST be rejected anywhere in a query, including inside a subquery.
The check MUST walk the parsed query, not the query text.

Federation from inside a pod is an SSRF surface with the pod's own network position behind it. It is
refused for the same reason a `did:web:` identifier is never dereferenced
([`SPS-AUTH-003`](auth.md#SPS-AUTH-003)) — the pod does not make outbound requests a caller chose.

<a id="SPS-SPARQL-006"></a>
**`SPS-SPARQL-006`** — Mutations reach a pod through the CRUD surface only
([`lod-crud.md`](lod-crud.md)). An implementation MUST NOT provide any other write path.

Together with [`SPS-CRUD-013`](lod-crud.md#SPS-CRUD-013) this is what makes "no atomic multi-context
write" a property of the system rather than of one route: there is no second door.

## 2. The sandbox

<a id="SPS-SPARQL-007"></a>
**`SPS-SPARQL-007`** — A query MUST see exactly the contexts the caller may read, and nothing else.
The restriction MUST be applied by the server when the query is executed.

<a id="SPS-SPARQL-008"></a>
**`SPS-SPARQL-008`** — An implementation MUST NOT trust a client-supplied dataset clause. `FROM` and
`FROM NAMED` in the query text MUST NOT widen what the query can see.

<a id="SPS-SPARQL-009"></a>
**`SPS-SPARQL-009`** — An implementation MUST NOT attempt to enforce the sandbox by rewriting the
query. The dataset the query executes against is what carries the restriction.

Rewriting is where sandboxes fail. A rewriter has to be correct against the whole of SPARQL —
subqueries, property paths, `GRAPH ?g`, `VALUES`, negation — and every construct it does not know
about is a hole. Restricting the dataset is one decision, taken once, that the query engine then
cannot see around.

<a id="SPS-SPARQL-010"></a>
**`SPS-SPARQL-010`** — Where the caller can read nothing, the implementation MUST answer
successfully with an empty result. It MUST NOT answer `403`, and MUST NOT answer with an error that
distinguishes "you may read nothing" from "nothing matched".

## 3. Dataset parameters

The SPARQL 1.1 Protocol's `default-graph-uri` and `named-graph-uri` are accepted as a **downscope**,
never as a widening.

<a id="SPS-SPARQL-011"></a>
**`SPS-SPARQL-011`** — An implementation MAY accept `default-graph-uri` and `named-graph-uri`. Where
it does, the effective set MUST be the intersection of the requested contexts with the caller's
readable contexts.

<a id="SPS-SPARQL-012"></a>
**`SPS-SPARQL-012`** — A requested context the caller cannot read MUST be dropped silently, with no
error and no diagnostic ([`SPS-CORE-017`](index.md#SPS-CORE-017)).

<a id="SPS-SPARQL-013"></a>
**`SPS-SPARQL-013`** — Presence of a dataset parameter MUST be judged on the **raw** parameter, not
on its value. A present-but-empty parameter — `?default-graph-uri=` — is a downscope request and
MUST resolve to the empty set. An implementation MUST NOT fall back to the caller's full readable
set.

This is the requirement most likely to be implemented backwards, and getting it wrong is a
privilege escalation with a friendly appearance: a client that meant to narrow its query to nothing
would silently receive everything it may read. Fail closed — an empty downscope is an answer, not an
absence.

<a id="SPS-SPARQL-014"></a>
**`SPS-SPARQL-014`** — Dataset-parameter resolution MUST use the same context resolution as the rest
of the pod, so that a context IRI means the same thing on every surface.

## 4. Results

<a id="SPS-SPARQL-015"></a>
**`SPS-SPARQL-015`** — `SELECT` and `ASK` MUST produce `application/sparql-results+json`. An
implementation MUST answer `406` where the client accepts nothing else.

<a id="SPS-SPARQL-016"></a>
**`SPS-SPARQL-016`** — `CONSTRUCT` and `DESCRIBE` MUST produce `application/ld+json` by default, and
MUST support `application/n-quads` by content negotiation.

<a id="SPS-SPARQL-017"></a>
**`SPS-SPARQL-017`** — An empty query body MUST be `400`.

<a id="SPS-SPARQL-018"></a>
**`SPS-SPARQL-018`** — An empty result MUST be a well-formed result document of the negotiated type,
not an error and not an empty body.

## 5. Availability

<a id="SPS-SPARQL-019"></a>
**`SPS-SPARQL-019`** — An implementation MUST bound a query's execution time.

An unbounded query engine reachable by any caller holding a read grant is a denial-of-service
surface that needs no privilege to reach. The bound is a deployment's number; having one is not.

<a id="SPS-SPARQL-020"></a>
**`SPS-SPARQL-020`** — Where an implementation exposes the same query capability through another
surface, both MUST dispatch through the same validation and the same sandbox.

Two implementations of a sandbox are two chances to be wrong, and the second one is the one nobody
tests. In the reference implementation this is why the HTTP route and the agent-facing tools share a
single service rather than each preparing their own query.

## 6. Service description

A client can ask the endpoint what it refuses before it sends a query.
[SPARQL 1.1 Service Description §2](https://www.w3.org/TR/2013/REC-sparql11-service-description-20130321/#accessing)
lets an endpoint answer a `GET` without a query string with an RDF description of itself. Serving
one is optional. When a pod serves one, it has to answer for the caller who asks, because what a pod
refuses can differ between callers.

<a id="SPS-SPARQL-021"></a>
**`SPS-SPARQL-021`** — An implementation that answers `GET {pod}/_system/sparql/query` without a query
string with a service description MUST link the described `sd:Service` with `sps:unsupportedFeature`
to exactly the catalogued features it refuses in a query from the requesting caller. The catalogued
features are `sd:BasicFederatedQuery` and the `sd:Feature` individuals of the
[sempods vocabulary](../../vocabulary/README.md).

`sd:feature` is open-world: a description that does not mention a feature says nothing about it.
That is why refusals are stated, and why the list is exact: a catalogued feature without
`sps:unsupportedFeature` was not refused for that caller when the description was produced. The
catalogue gives every implementation the same names; it grants no permission to refuse. `SERVICE`
is always refused ([`SPS-SPARQL-005`](#SPS-SPARQL-005)), so `sd:BasicFederatedQuery` is always
listed. Refusing any other catalogued feature departs from the SPARQL 1.1 Query profile; listing it
makes the departure visible, not conformant. Read-only needs no feature: the description names
`sd:SPARQL11Query` and not the update language, and an Update keeps the refusal of
[`SPS-SPARQL-004`](#SPS-SPARQL-004).

The description is a read, so the rules for reads apply unchanged: authentication as for a query,
and no unreadable context named in it ([`SPS-CORE-017`](index.md#SPS-CORE-017)). Because the answer
depends on the caller, `Cache-Control: no-store` or `Vary: Authorization` keeps a cache from handing
it to someone else. A refusal MAY point to the description with `rel="service-desc"`
([RFC 8631 §4.2](https://www.rfc-editor.org/rfc/rfc8631.html#section-4.2)), as long as a malformed
query and an Update stay indistinguishable. Wording that helps a caller rewrite a refused query is
the implementation's choice.

An informative description, in Turtle, for a caller that may use everything but `SERVICE`:

```turtle
@prefix sd:      <http://www.w3.org/ns/sparql-service-description#> .
@prefix sps:     <https://schema.sempods.org/> .
@prefix formats: <http://www.w3.org/ns/formats/> .

<https://example.org/alice/_system/sparql/query>
  a sd:Service ;
  sd:endpoint <https://example.org/alice/_system/sparql/query> ;
  sd:supportedLanguage sd:SPARQL11Query ;
  sd:resultFormat formats:SPARQL_Results_JSON, formats:JSON-LD, formats:N-Quads ;
  sps:unsupportedFeature sd:BasicFederatedQuery .
```

| Situation | Outcome |
|---|---|
| The pod refuses only what the specification refuses | The description lists `sd:BasicFederatedQuery` alone |
| The pod also refuses `UNION` for this caller | The description lists `sps:Union` as well; the refusal is still a departure from the SPARQL 1.1 Query profile |
| The pod refuses `UNION` but does not list it | Violates [`SPS-SPARQL-021`](#SPS-SPARQL-021) |
| The `GET` carries a rejected token | `401` ([`SPS-AUTH-043`](auth.md#SPS-AUTH-043)); no description |
| The pod serves no description | Conformant; the client learns of a refusal only from the `400` |

## 7. Not defined here

The query surface is deliberately unadorned. This specification defines no result pagination, no
stored queries, no query-plan introspection and no federation. A pod is a single tenant's store, and
a query that needs any of those is usually a question that belongs to [`find.md`](find.md) or to a
consumer holding the results.
