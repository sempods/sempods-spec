# Find

Use `find` when you have words and want a resource IRI. The response is RDF, so you can
follow a link from a hit to the rest of the pod.

**Status: this text decides, and can still change.** See [governance](../../GOVERNANCE.md).

Error codes are [`index.md`](index.md) §5; the read downscope is
[`lod-crud.md`](lod-crud.md) §3; what a caller may read is [`grants.md`](grants.md).

## 1. What `find` is

<a id="SPS-FIND-029"></a>
**`SPS-FIND-029`** — Every hit MUST be an IRI that occurs as the subject of a stored statement
in the effective selection.

The effective selection is all contexts the caller may read, narrowed by any [context filter](#SPS-FIND-009).
An article can match through its `schema:about` link to a topic. The server can return that link
with the article. If another selected context describes the topic, the topic can match there
as a subject in its own right.

<a id="SPS-FIND-001"></a>
**`SPS-FIND-001`** — `find` is a contract, not an algorithm. An implementation MUST be free to
satisfy it with any engine — substring matching, a lexical index, vectors, query rewriting, or
several at once — and a caller MUST NOT be required to select one.

<a id="SPS-FIND-002"></a>
**`SPS-FIND-002`** — The request MUST NOT carry a mode, an engine name or a ranking strategy. A
caller sends text.

The name is deliberate. `search` implies a ranked engine and a relevance model; `find` promises only
to locate something and give the caller a starting point. Two implementations with entirely
different engines can both satisfy this chapter, and a caller written against one works against the
other.

<a id="SPS-FIND-003"></a>
**`SPS-FIND-003`** — The response MUST be RDF: a subgraph the caller can merge into a working graph
and traverse. An implementation MUST NOT answer with a bespoke result envelope in place of it.

The graph contains pod data and any [observations](#6-what-matched) the server offers about a hit.

## 2. The request

```
GET  {pod}/_system/find?text=…&type=…&context=…&include_contexts=…&limit=…
POST {pod}/_system/find   { "text": …, "type": […], "contexts": […], "include_contexts": …, "limit": … }
```

<a id="SPS-FIND-004"></a>
**`SPS-FIND-004`** — An implementation MUST offer both forms, and they MUST be equivalent. The
`POST` body mirrors the query parameters, with the context downscope named `contexts`.

The `POST` form exists for a request that no longer fits in a URL — most often a downscope naming
many contexts.

<a id="SPS-FIND-005"></a>
**`SPS-FIND-005`** — `text` is REQUIRED. It MAY be terms or a natural-language question, and how it
is interpreted is the implementation's business.

<a id="SPS-FIND-006"></a>
**`SPS-FIND-006`** — `type` is OPTIONAL, repeatable, and combines as OR. It MUST constrain the
`rdf:type` of the returned hits.

<a id="SPS-FIND-007"></a>
**`SPS-FIND-007`** — `type` MUST be matched exactly. An implementation MUST NOT apply subclass
reasoning; a caller that wants subtypes lists them.

<a id="SPS-FIND-008"></a>
**`SPS-FIND-008`** — `type` constrains what comes back, not where matching happens. An
implementation MAY match through a linked resource and still return only the requested types.

`rdf:type` is the one structured facet in the core contract because every engine knows a resource's
type cheaply. A general predicate filter is not part of it, and adding one would have to be
fail-closed — a half-honoured filter reintroduces exactly the plausible-but-wrong result that
structured retrieval exists to avoid.

<a id="SPS-FIND-009"></a>
**`SPS-FIND-009`** — `context` (GET, repeatable) and `contexts` (POST) are the read downscope, with
the semantics of [`SPS-CRUD-014`](lod-crud.md#SPS-CRUD-014) and
[`SPS-CRUD-015`](lod-crud.md#SPS-CRUD-015): intersection with the readable set, unreadable entries
dropped in silence.

<a id="SPS-FIND-010"></a>
**`SPS-FIND-010`** — The server MUST apply the read downscope throughout the search,
including matching, ranking, observations and expansion.

If the caller searches A and the only matching text is in B, the resource is absent even if
its type is visible in A. If it also matches in A, the server can return it using only evidence
from A, including for excerpts and ranking.

<a id="SPS-FIND-025"></a>
**`SPS-FIND-025`** — `limit` is OPTIONAL. The server MUST cap the number of distinct matched resource
IRIs at the effective limit, applying a default when omitted and enforcing a maximum.

<a id="SPS-FIND-012"></a>
**`SPS-FIND-012`** — There is no cursor and no pagination. An implementation MUST NOT require one to
retrieve a complete answer within `limit`.

<a id="SPS-FIND-013"></a>
**`SPS-FIND-013`** — A `POST` body MUST be parsed strictly. An unknown member MUST be rejected rather
than ignored.

Ignoring an unknown member is how a caller's typo becomes a silently broader search. A rejected
request is a bug report; an ignored filter is a data leak with a `200`.

## 3. The sandbox

<a id="SPS-FIND-014"></a>
**`SPS-FIND-014`** — The context sandbox MUST apply exactly as it does to CRUD and SPARQL. An
anonymous caller sees the pod's public contexts; an authorized caller sees more. It is the same
`find`, at a different depth.

<a id="SPS-FIND-015"></a>
**`SPS-FIND-015`** — Where the caller can read nothing, or where the downscope resolves to nothing,
the implementation MUST answer `200` with an empty graph. It MUST NOT answer `404` and MUST NOT
answer `403`.

This is where `find` deliberately differs from a resource read. A resource read answers `404` for an
empty result, because "no such resource" and "not for you" have to be indistinguishable. A search
that matched nothing *is* an answer, and a caller can act on it.

## 4. The response

<a id="SPS-FIND-016"></a>
**`SPS-FIND-016`** — The response MUST contain the matched resources, and SHOULD expand each with at
least its `rdf:type` and its label.

<a id="SPS-FIND-017"></a>
**`SPS-FIND-017`** — An implementation MUST NOT return a full `DESCRIBE`-style expansion by default.

Expansion is a payload-size decision. Returning everything reachable turns a ten-hit answer into a
transfer of most of the pod, and a caller that wants depth already holds the IRIs to ask for it.

<a id="SPS-FIND-026"></a>
**`SPS-FIND-026`** — By default the server MUST return all statements in the default graph.
A caller MUST NOT infer rank from statement order.

<a id="SPS-FIND-027"></a>
**`SPS-FIND-027`** — With `include_contexts=true`, the server MUST group every statement by context,
using the context IRI as the graph name. Stored statements MUST keep their source context.
The server MUST place each generated observation link or detail in one or more contexts in the
effective selection that hold the hit. Grouping MUST change only the representation.

A context holds a hit when the pod has a statement there with the hit IRI as its subject.
The server can place an observation where the match occurred. It can also repeat it in eligible
contexts or place its link in one and its details in another. A link in A tells you where the
server placed it. A search restricted to A can still come back empty.

[`SPS-CTX-001`](contexts.md#SPS-CTX-001) governs stored statements. Even a stored
`sps:findResult` link keeps its source context. A generated observation belongs to the response.

<a id="SPS-FIND-020"></a>
**`SPS-FIND-020`** — The response MUST be content-negotiated, with JSON-LD as the default and
N-Quads available.

## 5. Caching

<a id="SPS-FIND-021"></a>
**`SPS-FIND-021`** — A `find` response depends on the caller's readable contexts. An implementation
MUST NOT allow a bearer-backed response to be stored in a shared cache without varying on the
credential, and SHOULD mark such a response private.

A `find` result is a permission-shaped view of the pod. A shared cache that keys only on the URL
serves one caller's depth to the next one.

## 6. What matched

A server can say that an article matched with a single link:

```turtle
@prefix sps: <https://schema.sempods.org/> .

<https://pod.example/articles/42> sps:findResult [] .
```

<a id="SPS-FIND-028"></a>
**`SPS-FIND-028`** — The server MAY annotate a hit. For each observation it supplies, it MUST
link the hit IRI to a response-local blank node with `sps:findResult`.

A hit can have zero, one or several observations. The blank node can carry an excerpt
(`schema:text`), the engine (`sps:engine`) or its place in the list that produced it
(`schema:position`, starting at 1). A resource can be second in one list and seventh in another.
The link works on its own, even without an explicit `sps:FindResult` type.

<a id="SPS-FIND-030"></a>
**`SPS-FIND-030`** — Apart from generated observation links, statements about the hit itself
MUST come from pod data in the effective selection.

<a id="SPS-FIND-031"></a>
**`SPS-FIND-031`** — Find MUST NOT persist the observations it generates.

A client that copies all outgoing statements about a hit also copies the links the search added.
The same predicate can occur in stored data.

The [response examples](../../examples/find/responses.yaml) cover both representations.

<details markdown="1">
<summary>Withdrawn requirements</summary>

<a id="SPS-FIND-011"></a>
**`SPS-FIND-011`** — *Withdrawn in 0.1-dev. Superseded by [`SPS-FIND-025`](#SPS-FIND-025).*
`limit` is OPTIONAL. An implementation MUST apply a default and MUST enforce a
maximum.

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
