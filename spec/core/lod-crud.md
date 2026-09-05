# CRUD

How a client reads, writes and modifies RDF over plain HTTP. Two layers over one store: the **LOD
layer**, which addresses a resource at its canonical IRI and refuses to bend HTTP; and the **system
layer**, which addresses a property slot or a single edge and is honest about the places where RDF
set semantics make it deviate.

**Status: this text decides, and can still change.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: RFC 9110, RFC 7396 (JSON Merge Patch), RFC 7232 (conditional requests), RFC 4648 §5
(base64url), JSON-LD 1.1, and the Linked Data principles. Error codes are [`index.md`](index.md) §5;
contexts are [`contexts.md`](contexts.md); who may do what is [`grants.md`](grants.md).

## 1. Two layers, one resource

<a id="SPS-CRUD-001"></a>
**`SPS-CRUD-001`** — A resource's **identity** is its LOD IRI. The system-layer URL is an
*operations* address for the same resource and MUST NOT be treated as a second identity.

```
identity:    https://example.org/alice/contacts/bob-smith
operations:  https://example.org/alice/_system/resources/aHR0cHM6Ly9leGFtcGxlL…
```

<a id="SPS-CRUD-002"></a>
**`SPS-CRUD-002`** — For a resource inside the pod namespace, the two addresses MUST behave
identically: the same body, the same entity tag, the same context rules, the same conditional-write
semantics. An implementation MUST NOT implement them twice.

<a id="SPS-CRUD-003"></a>
**`SPS-CRUD-003`** — For an IRI outside the pod namespace there is no LOD address. The system layer
MUST be the route that exists, and it MUST accept any IRI scheme — `did:`, `urn:`, `mailto:`, a
foreign `https:` — without special-casing.

<a id="SPS-CRUD-004"></a>
**`SPS-CRUD-004`** — A resource path equal to a segment reserved by
[`SPS-CORE-008`](index.md#SPS-CORE-008) — `_system` or `.well-known` — or beginning with one of
them followed by `/`, MUST NOT be addressable through the LOD layer.

## 2. Embedding an IRI in a path

<a id="SPS-CRUD-005"></a>
**`SPS-CRUD-005`** — An IRI embedded in a system-layer path segment MUST be encoded as base64url
without padding (RFC 4648 §5).

<a id="SPS-CRUD-006"></a>
**`SPS-CRUD-006`** — An implementation MUST NOT inspect an embedded IRI to decide how to decode it.
There is no `://` detection, no scheme allow-list and no container-specific rule; to the path parser
an embedded IRI is an opaque blob.

Percent-encoding was the obvious alternative and does not survive contact with reverse proxies and
servlet containers, which disagree about `%2F`, `%23` and `%3F`. base64url has Web precedent — JWT,
WebAuthn credential ids, PKCE challenges — and is a one-liner in every mainstream language.

```
{pod}/_system/resources/{b64url(iri)}                                       whole resource
{pod}/_system/resources/{b64url(subject)}/{b64url(predicate)}               slot
{pod}/_system/resources/{b64url(subject)}/{b64url(predicate)}/{b64url(iri)} single edge
```

## 3. The context rule

`?context=` selects the named graph an operation touches. It means different things on a write and
on a read, and both meanings hold on both layers.

### Writes

<a id="SPS-CRUD-007"></a>
**`SPS-CRUD-007`** — Every write MUST carry exactly one `?context=`. A write with none MUST be
`400`; a write with the parameter repeated MUST be `400`.

<a id="SPS-CRUD-008"></a>
**`SPS-CRUD-008`** — The repetition rule MUST be applied to the parameter's *occurrence count*, not
to its non-blank values. `?context=valid&context=` is a repeated parameter and MUST be `400`.

<a id="SPS-CRUD-009"></a>
**`SPS-CRUD-009`** — An implementation MUST accept a canonical context IRI, and MAY additionally
accept a pod-relative context path which it resolves to the canonical IRI.

<a id="SPS-CRUD-010"></a>
**`SPS-CRUD-010`** — A `?context=` value naming a context that is not registered MUST be `404`; a
registered context the caller may not write MUST be `403`
([`SPS-CORE-018`](index.md#SPS-CORE-018)).

This is the same known defect stated from the CRUD side, and it binds no more than its other half
does: an implementation that authorizes before testing existence answers alike either way and is
conformant today. Both go when the oracle is closed.

<a id="SPS-CRUD-011"></a>
**`SPS-CRUD-011`** — The resource IRI and the target context are **independent dimensions**. An
implementation MUST allow a write whose resource IRI lies outside the target context's path, and
MUST NOT derive one from the other.

This is the requirement that makes the model work, and the one an implementation is most tempted to
"tighten". A pod may hold statements about `did:web:bob.example`, about another pod's resources, and
about its own control-plane IRIs. What decides where they land is the writable context; the subject
never does.

<a id="SPS-CRUD-012"></a>
**`SPS-CRUD-012`** — Any `@graph` or context member inside a request body MUST be treated as
advisory. Statements MUST be persisted in the context named by `?context=`.

<a id="SPS-CRUD-013"></a>
**`SPS-CRUD-013`** — There is no atomic multi-context write, at any layer. An implementation MUST
NOT offer one, and MUST NOT offer a write path that spans contexts in one operation.

### Reads

<a id="SPS-CRUD-014"></a>
**`SPS-CRUD-014`** — On a read, `?context=` is an OPTIONAL downscope filter. With no value the
result MUST be the union of every context the caller may read. With one or more values, repeated as
separate parameters, the result MUST be the intersection of the requested set with the readable set.

<a id="SPS-CRUD-015"></a>
**`SPS-CRUD-015`** — A requested context the caller cannot read MUST be excluded silently
([`SPS-CORE-017`](index.md#SPS-CORE-017)).

<a id="SPS-CRUD-016"></a>
**`SPS-CRUD-016`** — A comma-separated list MUST NOT be accepted. Repetition is the only form.

A context IRI may legally contain a comma under RFC 3986, so a comma-separated list is ambiguous by
construction.

<a id="SPS-CRUD-017"></a>
**`SPS-CRUD-017`** — Where the resulting set contains no statement for the resource, the response
MUST be `404` — whether that is because the resource has none, because the requested contexts were
unreadable, or because they do not exist. The three MUST be indistinguishable.

## 4. LOD layer

<a id="SPS-CRUD-018"></a>
**`SPS-CRUD-018`** — An implementation MUST serve `GET`, `HEAD`, `OPTIONS`, `PUT`, `PATCH` and
`DELETE` at `{pod}/{resourcePath}`.

<a id="SPS-CRUD-019"></a>
**`SPS-CRUD-019`** — `POST` MUST NOT be offered on a resource IRI. Creation is `PUT` on the target
IRI, which is idempotent and leaves the identifier choice with the client.

### GET

<a id="SPS-CRUD-020"></a>
**`SPS-CRUD-020`** — `GET` MUST return every statement whose subject is the resource IRI and which
is visible in the selected contexts.

<a id="SPS-CRUD-021"></a>
**`SPS-CRUD-021`** — The default JSON-LD representation MUST be the **merged** resource object, with
named-graph provenance collapsed.

<a id="SPS-CRUD-022"></a>
**`SPS-CRUD-022`** — `include_contexts=true` MUST switch the representation to a JSON-LD named-graph
array grouped by RDF context. It MUST NOT change which contexts are readable — `?context=` remains
the only downscope.

### The canonical representation

<a id="SPS-CRUD-023"></a>
**`SPS-CRUD-023`** — The canonical JSON-LD shape is what `GET` returns with
`Accept: application/ld+json` and without `include_contexts=true`. It MUST be:

- a top-level object whose `@id` is the resource IRI;
- `@type` present where the resource has `rdf:type` values;
- predicate keys as **absolute IRIs** only;
- values as arrays of JSON-LD value objects — `{"@id": …}` for an IRI, `{"@value": …}` with an
  optional `@language` or `@type` for a literal.

<a id="SPS-CRUD-024"></a>
**`SPS-CRUD-024`** — An implementation MUST NOT emit a top-level `@context`, and MUST NOT emit
compact terms or CURIE-like keys.

<a id="SPS-CRUD-025"></a>
**`SPS-CRUD-025`** — An implementation MUST NOT expand CURIEs or resolve prefixes on any request
body. Prefix resolution is the client's business.

### Content negotiation

<a id="SPS-CRUD-026"></a>
**`SPS-CRUD-026`** — `application/ld+json` MUST be supported and MUST be the default.
`application/json` MUST be answered with `application/ld+json`. `application/n-quads` MUST be
supported.

<a id="SPS-CRUD-027"></a>
**`SPS-CRUD-027`** — An `Accept` header that cannot be satisfied MUST be `406`. A negotiated
response MUST carry `Vary: Accept`.

<a id="SPS-CRUD-028"></a>
**`SPS-CRUD-028`** — `application/n-quads` is graph-aware by format and MUST NOT be altered by
`include_contexts`.

### Entity tags

<a id="SPS-CRUD-029"></a>
**`SPS-CRUD-029`** — Every `GET` and `HEAD` response MUST carry a strong `ETag`, and
`If-None-Match` MUST be honoured per RFC 7232.

<a id="SPS-CRUD-030"></a>
**`SPS-CRUD-030`** — A successful write MUST NOT claim an entity tag for the representation it just
stored on the LOD resource path.

JSON-LD → RDF → JSON-LD is a transformation, so the stored representation is not byte-identical to
the request body, and RFC 9110 §10.2.3 does not permit claiming a tag for it. A client that needs the
new tag issues a `GET`.

### PUT

<a id="SPS-CRUD-031"></a>
**`SPS-CRUD-031`** — `PUT` MUST replace all outgoing statements of the resource **in the target
context**. Incoming statements from other resources MUST be untouched, and statements in other
contexts MUST be untouched.

<a id="SPS-CRUD-032"></a>
**`SPS-CRUD-032`** — A request body MUST contain statements for the target resource only. A body
carrying statements about other subjects MUST be `400`.

<a id="SPS-CRUD-033"></a>
**`SPS-CRUD-033`** — Creation MUST answer `201` with a `Location` header. Replacement MUST answer
`200` or `204`.

<a id="SPS-CRUD-034"></a>
**`SPS-CRUD-034`** — `If-Match` MUST be honoured, and a mismatch MUST be `412`. `If-None-Match: *`
MUST be honoured for create-or-fail, and an existing representation MUST be `412`.

### PATCH

<a id="SPS-CRUD-035"></a>
**`SPS-CRUD-035`** — `PATCH` MUST accept `application/merge-patch+json` and MUST apply RFC 7396
strictly to the canonical JSON-LD representation in the target context.

<a id="SPS-CRUD-036"></a>
**`SPS-CRUD-036`** — The accepted top-level members MUST be exactly: `@id` — OPTIONAL, and where
present it MUST equal the request's resource IRI or the request MUST be `400`; `@type`; and absolute
IRI predicate keys.

<a id="SPS-CRUD-037"></a>
**`SPS-CRUD-037`** — Every other JSON-LD keyword — including `@context`, `@graph`, `@reverse`,
`@nest` and `@included` — MUST be `400`. Compact terms and CURIE-like keys MUST be `400`.

`application/merge-patch+json` is JSON Merge Patch, not a JSON-LD processing mode. Accepting a
`@context` here would make the same document mean different things depending on a member the patch
format has no opinion about.

<a id="SPS-CRUD-038"></a>
**`SPS-CRUD-038`** — RFC 7396 array semantics MUST be preserved exactly: a multivalued property is
replaced wholesale. An implementation MUST NOT add a semantic RDF-aware merge.

Adding or removing one value from a multivalued property is what the system layer is for. This is a
property of RFC 7396, not a defect to work around — and working around it silently is how two
implementations stop agreeing about what a patch did.

### DELETE

<a id="SPS-CRUD-039"></a>
**`SPS-CRUD-039`** — `DELETE` MUST remove the resource's outgoing statements in the target context
and MUST leave incoming statements untouched. Success MUST be `204`; nothing to delete MUST be
`404`. `If-Match` MUST be honoured.

## 5. System layer

A **slot** is the container for all values of `(subject, predicate)` within one context. It is a
real HTTP resource: it has content, it answers `GET`, and it takes the standard verbs.

<a id="SPS-CRUD-040"></a>
**`SPS-CRUD-040`** — The resource-node route MUST offer `GET`, `HEAD`, `OPTIONS`, `PUT`, `PATCH` and
`DELETE` with the semantics of §4, for an IRI at any scheme.

<a id="SPS-CRUD-041"></a>
**`SPS-CRUD-041`** — The slot route MUST offer `GET`, `PUT`, `POST` and `DELETE`:

| Verb | Semantics |
|---|---|
| `GET` | all values as a JSON-LD array |
| `PUT` | replace the slot's contents; an empty array clears it |
| `POST` | add the given value or values |
| `DELETE` | empty the slot |

<a id="SPS-CRUD-057"></a>
**`SPS-CRUD-057`** — A slot `GET` MUST support `include_contexts` with the same meaning it has on a
resource read ([`SPS-CRUD-022`](#SPS-CRUD-022)): default is the merged value array, and `true`
switches to the named-graph form grouped by source context. It MUST change the representation only.

Without this the parameter is offered on a route that has nothing to do with it. A slot read spans
the same union of readable contexts a resource read does, so the same question — which context did
this value come from — is the same question here.

<a id="SPS-CRUD-042"></a>
**`SPS-CRUD-042`** — The single-edge route MUST offer `DELETE`, removing exactly
`(subject, predicate, target)` and leaving the slot's other values in place. It MUST be available
only where `target` is an IRI.

<a id="SPS-CRUD-043"></a>
**`SPS-CRUD-043`** — A `Location` header on a system-layer create MUST point at the system-layer
route, because the canonical path does not exist for an external IRI.

### The `outcome` representation

<a id="SPS-CRUD-044"></a>
**`SPS-CRUD-044`** — The three idempotent slot mutations MUST answer with a body naming the outcome:

| Route | Outcomes |
|---|---|
| slot `POST` | `created` (`201`, with `Location`) · `already_present` (`200`) |
| slot `DELETE` | `cleared` · `already_empty` (both `200`) |
| edge `DELETE` | `removed` · `already_absent` (both `200`) |

The distinction these report is precisely the one an idempotent status code cannot carry. A bare
`204` on a slot `DELETE` makes "there was nothing to clear" and "the slot is now empty"
indistinguishable to every caller outside the server. It is a body rather than a custom header so a
browser `fetch` can read it without an `Access-Control-Expose-Headers` entry.

### Deviations from HTTP, named

<a id="SPS-CRUD-045"></a>
**`SPS-CRUD-045`** — `POST` on a slot is idempotent in practice, because adding a statement that
already exists is a no-op under RDF set semantics. A client MAY retry it without a conditional
header. The verb stays `POST` because it expresses *extend*, not *replace*.

<a id="SPS-CRUD-046"></a>
**`SPS-CRUD-046`** — `GET` on a slot returns an unordered set. Array order MUST NOT be treated as
meaningful, and MAY differ between calls.

<a id="SPS-CRUD-047"></a>
**`SPS-CRUD-047`** — `POST` MUST answer `201` with `Location` when a new edge was inserted and
`200` without `Location` when the value was already present. `Location` is the unambiguous signal
that a new edge exists.

These three are the complete list of deviations. Any other behaviour that surprises a competent HTTP
client is a defect.

### Literals

<a id="SPS-CRUD-048"></a>
**`SPS-CRUD-048`** — A literal MUST NOT be addressable as a path segment. Removing or modifying one
literal value is `GET`, modify, `PUT` on the slot; `DELETE` on a slot holding literals empties the
whole slot.

<a id="SPS-CRUD-049"></a>
**`SPS-CRUD-049`** — `POST` MUST accept a literal, carrying `@value` and an optional `@language` or
`@type`.

This is the only structural asymmetry between IRI-valued and literal-valued slots. It is a
URL-encoding limit — a literal plus datatype plus language tag has no stable path encoding — and not
a design choice worth reproducing elsewhere.

### Conditional requests on slots

<a id="SPS-CRUD-050"></a>
**`SPS-CRUD-050`** — A slot `GET` resolving to exactly one context MUST emit an `ETag` when the slot
holds at least one statement there.

<a id="SPS-CRUD-051"></a>
**`SPS-CRUD-051`** — A slot `GET` spanning more than one context MUST NOT emit an `ETag`. The
representation is a union of snapshots that no single tag can validate.

<a id="SPS-CRUD-052"></a>
**`SPS-CRUD-052`** — `PUT`, `POST` and slot `DELETE` MUST echo the slot's new `ETag`, so a client can
chain conditional writes without an intervening `GET`.

<a id="SPS-CRUD-053"></a>
**`SPS-CRUD-053`** — `If-None-Match: *` on a slot MUST mean *the slot holds no statement for
`(subject, predicate)` in the write context*. It MUST NOT be interpreted as "the subject does not
exist".

The subject interpretation breaks both of the cases this route exists for: an external `did:web:`
subject that certainly "exists" elsewhere, and a local subject that already has values for other
predicates.

<a id="SPS-CRUD-054"></a>
**`SPS-CRUD-054`** — `PUT` MUST honour `If-Match`, with `412` on mismatch. `POST` MUST honour it
where provided and MUST NOT require it. Single-edge `DELETE` MUST ignore it — the operation names a
statement by identity, so the outcome is the same whether or not it was there.

## 6. What this layer does not do

<a id="SPS-CRUD-055"></a>
**`SPS-CRUD-055`** — An implementation MUST NOT canonicalise predicate IRIs. A predicate is stored
exactly as written, and `http://schema.org/name` and `https://schema.org/name` MUST remain distinct.

Silently unifying them would make two implementations disagree about what a pod contains, and the
disagreement would surface as data that vanishes on migration. A pod picks one canonical form and
says so; clients normalise on the way in.

<a id="SPS-CRUD-056"></a>
**`SPS-CRUD-056`** — An implementation MUST NOT accept SPARQL Update, JSON Patch or N3 Patch bodies
on either layer.

Not defined here, and named so a reader does not go looking: SHACL validation of cardinality,
datatype and value range — until that layer exists, both layers accept any structurally valid write;
bulk writes across several subjects in one call; and the atomic multi-context write ruled out by
`SPS-CRUD-013`.

One consequence of that last one is worth stating plainly rather than leaving to be discovered:
splitting a compound write per context does not reconstruct all-or-nothing semantics. The
intermediate state is externally visible, and a compensating write can fail in turn. What is left is
best-effort recovery. A caller who cannot tolerate that gap should not spread the data across
contexts in the first place.
