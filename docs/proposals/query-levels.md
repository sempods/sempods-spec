# Say which SPARQL queries every pod answers

Status: **Proposed; non-normative.**
Owning issue: [#143](https://github.com/sempods/sempods-spec/issues/143). This proposal defines the
"supported SPARQL query" left open by
[#68](https://github.com/sempods/sempods-spec/issues/68), and is an alternative to the refusal list
proposed under [#140](https://github.com/sempods/sempods-spec/issues/140) in
[PR #141](https://github.com/sempods/sempods-spec/pull/141).
Adoption: no normative adoption PR.

## Purpose and scope

A client that queries a pod needs to know which queries it can send. Today the answer is simple.
The core profiles all of SPARQL 1.1 Query except `SERVICE` and Update
([`sparql.md`](../../spec/core/sparql.md)), and
[`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009) forbids enforcing the sandbox by
rewriting the query.

The [access-control proposal](access-control.md#queries-and-retrieval) changes the second half. An
implementation may choose its enforcement mechanism, query rewriting included, as long as a
*supported* query returns the result it would return against the caller-authorized dataset. That
proposal does not say which queries are supported. The [use case below](#use-case-a-per-document-rewriter)
shows why the question is real: a pod that checks every document against its policy by rewriting
the query answers some constructs exactly and others not at all.

This proposal fills that gap in three parts:

1. a **base level**: the queries every pod answers;
2. a positive **announcement** of what a pod answers beyond it, using
   [SPARQL 1.1 Service Description, 21 March 2013](https://www.w3.org/TR/2013/REC-sparql11-service-description-20130321/);
3. the **refusal** a client receives for a query the pod does not answer.

Update, `SERVICE`, [dataset selection](data-access.md#query-dataset-selection) and `find` are out of
scope. Their current rules hold at every level.

## Use case: a per-document rewriter

This is the [areas combined with document policies](data-access.md#areas-combined-with-document-policies)
example of the data-access proposal, enforced by rewriting. It follows the second of the
[enforcement strategies](authorization-implementation/authorization-state.md) in the ACP design
material: restrict the dataset to readable areas, then check each resource. It describes one
possible design, not a requirement and not a verified implementation.

The pod keeps documents in areas, one named graph per area. A caller sees the areas it belongs to.
Within them, each document has an [ACP](https://solidproject.org/TR/acp) policy, in the shape of the
[candidate ACP profile](authorization-implementation/acp-profile.md). Policies live in separate
authorization graphs that ordinary data writes cannot reach.

For each query, the pod builds a dataset: the caller's visible area graphs as **named** graphs, and
the authorization graphs as the **default** graph. It then rewrites the client's query in two steps:

1. Every client pattern moves into `GRAPH ?g`, so it reads only content. Policy facts sit in the
   default graph, where no client pattern can reach them.
2. Every distinct subject gets one check: a `FILTER EXISTS` over the default graph that asks whether
   a policy grants the caller read access to that document.

A client sends:

```sparql
PREFIX schema: <https://schema.org/>

SELECT ?doc ?title WHERE { ?doc schema:name ?title }
```

The pod evaluates, simplified to policies whose matchers all name agents:

```sparql
PREFIX schema: <https://schema.org/>
PREFIX acp:    <http://www.w3.org/ns/solid/acp#>
PREFIX acl:    <http://www.w3.org/ns/auth/acl#>

SELECT ?doc ?title WHERE {
  GRAPH ?__g0 { ?doc schema:name ?title }          # content, named graphs only
  FILTER EXISTS {                                  # policy, default graph only
    ?__acr acp:resource ?doc ; acp:accessControl ?__ac .
    ?__ac acp:apply ?__policy .
    ?__policy acp:allow acl:Read ; acp:allOf ?__any .
    FILTER NOT EXISTS {                            # no matcher may fail
      ?__policy acp:allOf ?__m .
      FILTER NOT EXISTS {
        ?__m acp:agent ?__agent .
        FILTER (?__agent IN (<https://example.org/carol#me>, acp:AuthenticatedAgent, acp:PublicAgent))
      }
    }
  }
}
```

Such a rewriter answers `SELECT` with basic graph patterns, `FILTER`, `OPTIONAL`, blank nodes,
sequence and inverse paths, `ORDER BY`, `LIMIT` and `OFFSET`. It refuses the rest. Its design work
found these pitfalls, and each one shapes the contract below:

| Pitfall | What it means for the contract |
|---|---|
| A join with the policy chain multiplies rows: a document that two policies grant appears twice. `FILTER EXISTS` decides without adding rows. | Equivalence covers row counts, not only row sets. |
| A check placed above `LIMIT` pages through rows the caller cannot read and returns short pages. | `LIMIT` and `OFFSET` count authorized rows only. |
| Blank node labels are scoped to one basic graph pattern. A check that reuses a client's blank node turns into "some readable document exists". | Blank nodes stay in the base level; the implementation renames them before checking. |
| Above a `GROUP BY`, the subject is gone, and the check degenerates the same way. | Aggregation lies above the base level. Only tests of the outcome reveal such a mistake. |
| A rewritten query printed back to text is parsed a second time. A literal that does not survive that round trip can change the check. | Validation includes literals with escape sequences and quotes. |
| A reserved variable prefix for the rewriter's own names leads it to refuse client queries using that prefix. | Internal names never cause a refusal; the implementation picks names the query does not use. |
| `GRAPH` in a client query collides with the graph position the rewriter fills itself. | Reaching the base level needs `GRAPH` intersected with the content graphs. |
| The same pod serves some callers through a plain dataset restriction, without rewriting. Those callers can use full SPARQL. | The level can differ per caller. |

## Proposed contract and cases

### Two levels

| Level | Candidate identifier | What a pod answers |
|---|---|---|
| Base | `sps:QueryBase`, an `sd:Language` | The constructs in the table below |
| Full | `sd:SPARQL11Query` | SPARQL 1.1 Query as the core profiles it today, without `SERVICE` |

Every pod answers every base-level query, for every caller who may query. A pod may answer more.
Every query a pod answers, at any level, follows the authorized-query equivalence: hidden statements
never change a result, including a row count, a negation or a path. An implementation's internal
names, such as variables it adds, never make it refuse a base-level query.

| Part of the query | In the base level |
|---|---|
| Query forms | `SELECT`, with `DISTINCT`, `REDUCED` and projection expressions; `ASK` |
| Graph patterns | Basic graph patterns with blank nodes, `FILTER` without `EXISTS`, `OPTIONAL`, `BIND`, `GRAPH` |
| Property paths | Sequence `a/b` and inverse `^a` |
| Solution modifiers | `ORDER BY`, `LIMIT`, `OFFSET` |

Everything else lies above the base level: `UNION`, `MINUS`, `EXISTS` and `NOT EXISTS`, `VALUES`,
subqueries, grouping and aggregates, the path operators `|`, `!`, `?`, `*` and `+`, and the
`CONSTRUCT` and `DESCRIBE` forms.

The line is drawn where a rewriting implementation can still be exact. Every data access in a
base-level query is a triple pattern in the main group or in an `OPTIONAL` group, which the use case
checks once per subject. `ASK` reports whether such a query has a row. `GRAPH` belongs to the base
level because the data-access proposal makes `GRAPH <C>` agree with a Context-selected read.

Above the line, the reasons differ:

- **Harder for a rewriter, but possible.** Aggregation and subqueries project the checked subject
  away before the check can see it. `UNION`, `MINUS` and `EXISTS` open groups that each need their
  own check.
- **Not expressible by rewriting.** `*` and `+` need a check on every step of a path of any length,
  and SPARQL 1.1 has no recursion to write it. A zero-length path matches every node of the graph,
  including nodes that only hidden statements mention. What `DESCRIBE` reads is up to the
  implementation.

An implementation that restricts the dataset beneath its query engine answers all of these exactly,
because the engine never sees a hidden statement. Such a pod answers the full level.

### Announcing more

A pod announces what it answers for a caller in a service description. SD §2 places it at the query
endpoint: a `GET` without a query string. The description is for the requesting caller, because the
level can differ between callers, as in the use case.

- `sd:supportedLanguage` names the level: `sd:SPARQL11Query` or `sps:QueryBase`.
- `sd:feature` names each construct above the base level that the pod answers for this caller. The
  feature individuals are the ones PR #141 proposes, used as positive statements.
- A client without a description relies on the base level. It may still send other queries and
  handle a refusal.

A caller whose queries run against a restricted dataset:

```turtle
@prefix sd: <http://www.w3.org/ns/sparql-service-description#> .

<https://example.org/alice/_system/sparql/query>
  a sd:Service ;
  sd:endpoint <https://example.org/alice/_system/sparql/query> ;
  sd:supportedLanguage sd:SPARQL11Query .
```

A caller whose documents are checked one by one, on a pod whose rewriter has added aggregation:

```turtle
@prefix sd:  <http://www.w3.org/ns/sparql-service-description#> .
@prefix sps: <https://schema.sempods.org/> .

<https://example.org/alice/_system/sparql/query>
  a sd:Service ;
  sd:endpoint <https://example.org/alice/_system/sparql/query> ;
  sd:supportedLanguage sps:QueryBase ;
  sd:feature sps:Aggregation .
```

An announcement is a promise. A pod answers every query that the level and the features it
announces to a caller cover. This is the one new obligation the announcement needs. Serving a
description keeps the SHOULD of SD §2: a pod that answers only the base level loses nothing by not
serving one.

The [pod discovery](pod-discovery.md) description stays caller-independent. It locates the query
service; the per-caller level lives in that service's description.

### Refusing a query

A pod refuses a query it does not answer for the caller with `400`, the status the
[core OpenAPI description](../../openapi/sempods-core.yaml) gives a rejected query today. The
[SPARQL 1.1 Protocol](https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#query-operation)
permits `500` for a query a service refuses to execute. A refusal the client can fix by changing its
query is a client error, and `400` keeps it apart from a server failure.

The refusal depends only on the parsed query and the caller's level. It never depends on data or on
hidden state, because a refusal that did would tell a caller something its result would hide. An
Update keeps the refusal of [`SPS-SPARQL-004`](../../spec/core/sparql.md#SPS-SPARQL-004),
indistinguishable from a malformed query. A refusal of a construct above the base level may name
that construct: the caller wrote it, and the description already says the pod does not answer it.
The wording and any problem type belong to the implementation.

### Cases

Run each case against a dataset-restricting pod and a per-document rewriter configured with the same
authorized data.

| Caller | Query | Outcome |
|---|---|---|
| Base level, no description served | `SELECT ?n WHERE { ?d schema:name ?n OPTIONAL { ?d schema:author ?a } }` | `200`; the rows of the caller-authorized dataset |
| Base level; two policies both grant one document | `SELECT ?d WHERE { ?d a schema:Article }` | The document appears once, as against the authorized dataset |
| Base level; 12 articles, 5 of them readable | `SELECT ?d WHERE { ?d a schema:Article } ORDER BY ?d LIMIT 3 OFFSET 3` | Rows 4 and 5 of the 5 readable articles |
| Base level | `ASK { <https://example.org/alice/hidden> ?p ?o }` for a resource the caller cannot read | `200`, `false`; the same answer as for a resource that does not exist |
| Base level | `SELECT ?p WHERE { ?x <http://www.w3.org/ns/solid/acp#allow> ?p }` | No rows: authorization facts are outside the caller's data view |
| Base level | A query whose variables use any prefix, including one the implementation uses internally | Answered like the same query with other variable names |
| Base level | `FILTER` on string literals with escape sequences and quotes | Answered exactly; no literal changes what the caller may read |
| Base level, no `sd:feature sps:Aggregation` | `SELECT (COUNT(*) AS ?c) WHERE { ?d a schema:Article }` | `400`; the same response whether hidden articles exist or not |
| Base level, announces `sps:Aggregation` | The same count, before and after a hidden article is added | `200` both times, with the same count |
| Base level, announces `sps:Aggregation` | The same count is refused | Violates the announcement rule |
| Full level | `SELECT ?b WHERE { <https://example.org/alice/me> schema:knows+ ?b }` | `200`; the path never steps over a hidden statement |
| Any level | A query using `SERVICE` | `400` ([`SPS-SPARQL-005`](../../spec/core/sparql.md#SPS-SPARQL-005)) |
| Any level | An Update | `400`, indistinguishable from a malformed query |

## Rationale and compatibility

**A positive statement, as SD intends.** SD says what a service implements: `sd:supportedLanguage`
names a language it implements and `sd:feature` a feature it supports. It has no term for a refusal.
A refusal list next to `sd:supportedLanguage sd:SPARQL11Query` contradicts that statement. A named
base level is a closed list a client can rely on. Above it, a missing `sd:feature` means only that
the client should not rely on the feature, which is what open-world RDF says anyway.

**Conformance instead of visibility.** Under PR #141, a pod that refuses `UNION` stays non-conformant
and says so. Here, the per-document rewriter is conformant once it answers the base level exactly.
The use case shows why the outcome, not the mechanism, has to carry the security argument: each of
its pitfalls looks like a correct rewrite, and only comparing results exposes it. That keeps the
preference of invariant 6 in [`AGENTS.md`](../../AGENTS.md#non-negotiable-invariants): explicit
specification and conformance tests decide, not a rewriter's cleverness.

**The selection test** of [the vision](../vision.md#what-belongs-in-the-contract):

- *What needs agreement?* Which queries a client can send to any pod. Today's answer cannot hold
  once the enforcement mechanism is free.
- *Why this scope?* The base level holds on every pod, so it is core. What lies above it can differ
  per caller, so it is announced per caller rather than claimed as a pod-wide module.
- *What must be observable?* Results under the equivalence, the refusal and the description.
- *Can different implementations satisfy it?* A store that restricts its dataset answers the full
  level. The per-document rewriter reaches the base level with `ASK`, `GRAPH` and renaming of its
  internal variables. A small embedded store can do either.

**Compatibility.** Today a client may rely on full SPARQL 1.1 Query on every pod. After adoption it
may rely on the base level, and on more where a pod announces it. This narrows the core guarantee
and is backward-incompatible for a client that uses constructs above the base level without
checking. A pod that answers the full level stays conformant and needs no change; serving a
description is recommended, not required. The vocabulary gains `sps:QueryBase` and the feature
individuals for constructs above the base level, and no `sps:unsupportedFeature`.

### Requirement impact

| Current | Proposed change |
|---|---|
| The SPARQL 1.1 Query profile of [`sparql.md`](../../spec/core/sparql.md) | Scope it by level: the base level on every pod, SPARQL 1.1 Query where announced |
| [`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009) | Replace with the outcome equivalence, as [data access](data-access.md#requirement-changes-to-prepare) already proposes |
| [`SPS-SPARQL-015`](../../spec/core/sparql.md#SPS-SPARQL-015), [`SPS-SPARQL-016`](../../spec/core/sparql.md#SPS-SPARQL-016) | Apply to the forms a pod answers; `CONSTRUCT` and `DESCRIBE` results only where announced |
| [`SPS-SPARQL-002`](../../spec/core/sparql.md#SPS-SPARQL-002), [`SPS-SPARQL-004`](../../spec/core/sparql.md#SPS-SPARQL-004), [`SPS-SPARQL-005`](../../spec/core/sparql.md#SPS-SPARQL-005), [`SPS-SPARQL-008`](../../spec/core/sparql.md#SPS-SPARQL-008) | Unchanged |
| Invariant 6 in [`AGENTS.md`](../../AGENTS.md#non-negotiable-invariants) | Review its wording together with `SPS-SPARQL-009` |
| New | Every pod answers every base-level query under the equivalence, whatever names the query uses |
| New | A pod answers every query covered by the level and features it announces to the caller |
| New | A refusal depends only on the parsed query and the caller's level, and is `400`: a stated deviation from the Protocol's permitted `500` |
| `SPS-SPARQL-021` proposed in PR #141 | Superseded by the announcement rule; the SD profile of that PR stays |

The query cases above extend the query-enforcement validation planned under
[#72](https://github.com/sempods/sempods-spec/issues/72) and described in
[access control](access-control.md#validation-before-adoption).

## Decisions requiring resolution

1. **Base content.** `ASK` and `GRAPH` are included above; the use case needs both to reach the base
   level. Negated property sets, `VALUES` and `CONSTRUCT` can also be checked pattern by pattern, at
   a cost to rewriting implementations. A higher base level serves clients better; a lower one admits
   more implementations.
2. **Identifier.** The name and IRI of the base language, and whether it is versioned with the
   specification.
3. **Where a level is claimed.** Per caller in the service description only, as recommended, or in
   addition as a pod-wide claim for pods whose callers all receive the full level.
4. **PR #141.** Merge it reduced to the SD profile now and add levels later, or hold it for this
   proposal.
5. **The use case as material.** Whether a per-document rewriter like the one above becomes
   retained design material beside the [ACP profile](authorization-implementation/README.md), whose
   disposition [#64](https://github.com/sempods/sempods-spec/issues/64) owns.
