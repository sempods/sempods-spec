# Find

Use `find` when you have words and want a resource IRI. From a hit you can follow links
into the rest of the pod.

**Status: this text decides, and can still change.** See [governance](../../GOVERNANCE.md).

## 1. What `find` is

<a id="SPS-FIND-029"></a>
**`SPS-FIND-029`** — Every hit MUST be an IRI that occurs as the subject of a stored statement
in the effective selection.

The effective selection is all contexts the caller may read, narrowed by any [context filter](#SPS-FIND-009).

<a id="SPS-FIND-001"></a>
**`SPS-FIND-001`** — An implementation MUST be free to use any search engine or combination of engines.
A caller MUST NOT be required to choose one.

One server might look up words in a text index. Another might also search by similarity.

<a id="SPS-FIND-003"></a>
**`SPS-FIND-003`** — The server MUST return a traversable RDF subgraph that callers can merge
into their own graph. A custom result envelope MUST NOT replace it.

## 2. The request

```http
GET https://pod.example/_system/find?text=harbour&type=https://schema.org/Article&type=https://schema.org/Book&context=https://pod.example/_system/contexts/A&context=https://pod.example/_system/contexts/B
```

```http
POST https://pod.example/_system/find
Content-Type: application/json

{
  "text": "harbour",
  "type": ["https://schema.org/Article", "https://schema.org/Book"],
  "contexts": ["https://pod.example/_system/contexts/A", "https://pod.example/_system/contexts/B"]
}
```

<a id="SPS-FIND-004"></a>
**`SPS-FIND-004`** — The server MUST offer equivalent GET and POST forms. The [POST body](../../openapi/sempods-core.yaml)
mirrors the query parameters, using `contexts` for the GET parameter `context`.

<a id="SPS-FIND-013"></a>
**`SPS-FIND-013`** — The server MUST parse the POST body strictly and reject unknown members.

<a id="SPS-FIND-005"></a>
**`SPS-FIND-005`** — `text` is REQUIRED. The caller MAY send search terms or a natural-language
question.

<a id="SPS-FIND-002"></a>
**`SPS-FIND-002`** — The request MUST NOT carry a mode, an engine name or a ranking strategy.

The server decides how to interpret the text.

<a id="SPS-FIND-006"></a>
**`SPS-FIND-006`** — `type` is OPTIONAL and repeatable. When supplied, the filter MUST accept
hits with any of the requested `rdf:type` values and exclude the rest.

<a id="SPS-FIND-007"></a>
**`SPS-FIND-007`** — The server MUST match type IRIs exactly. A hit's `rdf:type` MUST NOT match
a requested type solely because it is a subclass of that type.

Callers can list the subtypes they want to include.

<a id="SPS-FIND-008"></a>
**`SPS-FIND-008`** — The server MAY match through a linked resource. The type filter applies
to the returned hit.

An article can match through its `schema:about` link to a topic. Find can include that link
with the article. A topic described in a selected context can also be a hit in its own right.

<a id="SPS-FIND-025"></a>
**`SPS-FIND-025`** — `limit` is OPTIONAL. The server MUST cap the number of distinct matched resource
IRIs at the effective limit, applying a default when omitted and enforcing a maximum.

<a id="SPS-FIND-012"></a>
**`SPS-FIND-012`** — Find has no cursor or pagination. The complete answer within the effective
limit MUST be available in one request.

## 3. The sandbox

<a id="SPS-FIND-014"></a>
**`SPS-FIND-014`** — Find MUST apply the same context sandbox as CRUD and SPARQL.
Anonymous callers search public contexts. For authenticated callers, the
[grants and `public-read` rules](grants.md#7-public-read) determine the readable set.

<a id="SPS-FIND-009"></a>
**`SPS-FIND-009`** — The context filter is `context` on GET (repeatable) and `contexts` on POST.
It uses the [CRUD read filter](lod-crud.md#SPS-CRUD-014), including
[silent omission of unreadable contexts](lod-crud.md#SPS-CRUD-015).

<a id="SPS-FIND-010"></a>
**`SPS-FIND-010`** — The server MUST apply the context filter throughout the search,
including matching, ranking, observations and expansion.

Suppose A identifies a resource as an article and only its title in B matches “harbour”.
A search for “harbour” in A alone leaves out the article, even when the caller can read B.

<a id="SPS-FIND-015"></a>
**`SPS-FIND-015`** — If the caller can read nothing or the context filter leaves an empty selection,
the server MUST return `200` with an empty graph.

A search with no matches gets the same [`200` with an empty graph](../../openapi/sempods-core.yaml).
A [resource read with no visible statements](lod-crud.md#SPS-CRUD-017) returns `404`.
Both follow the [same visibility rule](index.md#SPS-CORE-017).

## 4. The response

<a id="SPS-FIND-032"></a>
**`SPS-FIND-032`** — Each hit IRI MUST be the subject of at least one statement in the response.

Type and label are optional, even when both are available. A [stored statement](#SPS-FIND-030)
about the hit or a [bare observation link](#SPS-FIND-028) is enough.
A JSON-LD node with only `@id` contributes no statement on its own.

<a id="SPS-FIND-017"></a>
**`SPS-FIND-017`** — An implementation MUST NOT return a full `DESCRIBE`-style expansion by default.

<a id="SPS-FIND-020"></a>
**`SPS-FIND-020`** — The response MUST be content-negotiated, with JSON-LD as the default and
N-Quads available.

<a id="SPS-FIND-026"></a>
**`SPS-FIND-026`** — By default the server MUST return all statements in the default graph.
A caller MUST NOT infer rank from statement order.

<a id="SPS-FIND-027"></a>
**`SPS-FIND-027`** — With `include_contexts=true`, the server MUST group every statement by context,
using the context IRI as the graph name. Stored statements MUST keep their source context.
The server MUST place each generated observation link or detail in one or more contexts in the
effective selection that hold the hit. Grouping MUST change only the representation.

A context holds a hit when a stored statement there has the hit IRI as its subject.
Among those contexts, the server can use the one where the match occurred, repeat an observation,
or put its link in one and its details in another. A link in A can appear even if an A-only search would find nothing.
A stored `sps:findResult` link keeps its [source context](contexts.md#SPS-CTX-001).

## 5. Caching

<a id="SPS-FIND-021"></a>
**`SPS-FIND-021`** — The server MUST NOT allow shared caching of a bearer-backed response unless
the cache varies on the credential. The server SHOULD mark such responses private.

## 6. What matched

<a id="SPS-FIND-028"></a>
**`SPS-FIND-028`** — The server MAY annotate a hit. For each observation it supplies, it MUST
link the hit IRI to a response-local blank node with `sps:findResult`.

```turtle
@prefix sps: <https://schema.sempods.org/> .

<https://pod.example/articles/42> sps:findResult [] .
```

A hit can have zero, one or several observations. The link works without an explicit
`sps:FindResult` type. The node can give an excerpt (`schema:text`), an engine (`sps:engine`)
or a 1-based position in the list that produced it (`schema:position`). One resource can be
second in one list and seventh in another.

<a id="SPS-FIND-030"></a>
**`SPS-FIND-030`** — Apart from generated observation links, statements about the hit itself
MUST come from pod data in the effective selection.

<a id="SPS-FIND-031"></a>
**`SPS-FIND-031`** — Find MUST NOT persist the observations it generates.

Copying all outgoing statements about a hit also copies its observation links.
The [response examples](../../examples/find/responses.yaml) show both flat and grouped results.

<details markdown="1">
<summary>Withdrawn requirements</summary>

<a id="SPS-FIND-011"></a>
**`SPS-FIND-011`** — *Withdrawn in 0.1-dev. Superseded by [`SPS-FIND-025`](#SPS-FIND-025).*
`limit` is OPTIONAL. An implementation MUST apply a default and MUST enforce a
maximum.

<a id="SPS-FIND-016"></a>
**`SPS-FIND-016`** — *Withdrawn in 0.1-dev. Superseded by [`SPS-FIND-032`](#SPS-FIND-032).*
The response MUST include each hit. The server SHOULD include the hit's
`rdf:type` if available in the effective selection and its label if available there.

<a id="SPS-FIND-018"></a>
**`SPS-FIND-018`** — *Withdrawn in 0.1-dev. Superseded by [`SPS-FIND-026`](#SPS-FIND-026).*
By default the response MUST be a flat graph: no ordering, no score, and no
marker distinguishing a hit from an expansion. A caller MUST NOT infer rank from statement order.

<a id="SPS-FIND-019"></a>
**`SPS-FIND-019`** — *Withdrawn in 0.1-dev. Superseded by [`SPS-FIND-027`](#SPS-FIND-027).*
`include_contexts=true` MUST group the response by the context each statement
came from — named-graph JSON-LD, or the fourth term in N-Quads. It MUST change only the
representation, never which resources match.

<a id="SPS-FIND-022"></a>
**`SPS-FIND-022`** — *Withdrawn in 0.1-dev. Superseded by [`SPS-FIND-028`](#SPS-FIND-028).*
Per-hit metadata MUST NOT appear in the default response. An implementation MAY
emit it only in a representation the client explicitly asked for, and this version of the
specification defines no such request.

<a id="SPS-FIND-023"></a>
**`SPS-FIND-023`** — *Withdrawn in 0.1-dev. Superseded by [`SPS-FIND-030`](#SPS-FIND-030).*
Authoritative facts about a hit — its types, its labels, its timestamps — MUST
come from the store during expansion and MUST NOT be asserted by the metadata node.

<a id="SPS-FIND-024"></a>
**`SPS-FIND-024`** — *Withdrawn in 0.1-dev. Superseded by [`SPS-FIND-031`](#SPS-FIND-031) and [`SPS-FIND-027`](#SPS-FIND-027).*
Where such metadata is emitted, it is **transient**: it MUST NOT be written to
the store, it MUST NOT appear in the named-graph grouping that `include_contexts=true` produces, and
a caller MUST NOT expect to retrieve it again.

</details>
