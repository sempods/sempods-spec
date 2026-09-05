# Find

The entry primitive: text in, a subgraph out. `find` is where a consumer that does not yet know an
IRI gets a foothold, after which it traverses links like any other Linked Data client.

**This chapter is new writing.** It existed in the reference implementation only as a concept
document, which mixes what is built with what is planned. What follows is the built half.

**Status: this text decides, and can still change.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Error codes are [`index.md`](index.md) §5; the read downscope is
[`lod-crud.md`](lod-crud.md) §3; what a caller may read is [`grants.md`](grants.md).

## 1. What `find` is

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

The retrieval unit is a resource, not a text fragment. An event is one entity with all its
properties, and every IRI-valued property is an exact traversal path — which is what lets a consumer
follow the data instead of guessing at it.

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
**`SPS-FIND-010`** — The downscope MUST apply to the whole operation, the expansion included. An
implementation MUST NOT expand a hit with statements from a context outside it.

<a id="SPS-FIND-011"></a>
**`SPS-FIND-011`** — `limit` is OPTIONAL. An implementation MUST apply a default and MUST enforce a
maximum.

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

<a id="SPS-FIND-018"></a>
**`SPS-FIND-018`** — By default the response MUST be a flat graph: no ordering, no score, and no
marker distinguishing a hit from an expansion. A caller MUST NOT infer rank from statement order.

<a id="SPS-FIND-019"></a>
**`SPS-FIND-019`** — `include_contexts=true` MUST group the response by the context each statement
came from — named-graph JSON-LD, or the fourth term in N-Quads. It MUST change only the
representation, never which resources match.

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

## 6. Result metadata is reserved, not specified

The sempods vocabulary defines terms for per-hit metadata — which engine produced a hit, where it
ranked, and the excerpt that matched. **This chapter does not require them, because no
implementation emits them.**

They are recorded here so that an implementation does not mint competing terms for the same idea, and
so that a later version of this chapter can specify them without a migration. Until then,
`SPS-FIND-018` is the contract: the response is flat.

<a id="SPS-FIND-022"></a>
**`SPS-FIND-022`** — Per-hit metadata MUST NOT appear in the default response. An implementation MAY
emit it only in a representation the client explicitly asked for, and this version of the
specification defines no such request.

The reserved terms link a matched resource to its metadata node, and that link *is* a marker
separating a hit from an expansion — exactly what [`SPS-FIND-018`](#SPS-FIND-018) forbids. A `MAY`
that could be exercised in the default response would therefore have contradicted the flat-graph
contract rather than extended it. The terms stay reserved; what has to arrive before they can be
emitted is a negotiated representation to emit them in.

<a id="SPS-FIND-024"></a>
**`SPS-FIND-024`** — Where such metadata is emitted, it is **transient**: it MUST NOT be written to
the store, it MUST NOT appear in the named-graph grouping that `include_contexts=true` produces, and
a caller MUST NOT expect to retrieve it again.

This does not weaken [`SPS-CTX-001`](contexts.md#SPS-CTX-001), and the distinction is worth being
exact about because the two look like they collide. That invariant governs **statements a pod
stores** — every one of those belongs to exactly one context. A `find` response is a
representation the server computes and hands over; the matched statements in it came from contexts
and can be grouped by them, while a metadata node describes the *response* and was in no context to
begin with. An implementation that stored one would be creating a statement with no context, which
the invariant forbids — which is what `MUST NOT be written to the store` says.

<a id="SPS-FIND-023"></a>
**`SPS-FIND-023`** — Authoritative facts about a hit — its types, its labels, its timestamps — MUST
come from the store during expansion and MUST NOT be asserted by the metadata node.

The distinction is the same one [`contexts.md`](contexts.md) §6 makes for control-plane IRIs: what
something *is* comes from whatever owns it, and what a response *says about* it is a claim with a
narrower lifetime.
