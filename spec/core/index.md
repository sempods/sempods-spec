# Core — conformance, addressing, discovery

The chapter every other chapter rests on. It says what it means to conform, how a normative
statement is identified, how a pod is addressed, and how an implementation tells a client what it
provides.

**Status: descriptive.** Until this specification tags `0.1` it is being extracted from the
reference implementation, and where the two disagree the implementation is right. See
[`../../GOVERNANCE.md`](../../GOVERNANCE.md).

## 1. Conformance language

<a id="SPS-CORE-001"></a>
**`SPS-CORE-001`** — The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, `SHALL NOT`, `SHOULD`,
`SHOULD NOT`, `RECOMMENDED`, `MAY` and `OPTIONAL` in this specification are to be interpreted as
described in RFC 2119 and RFC 8174, and only when they appear in all capitals.

Prose that carries no such keyword is explanation. Where prose and a requirement appear to disagree,
the requirement is what binds.

<a id="SPS-CORE-002"></a>
**`SPS-CORE-002`** — Every normative statement in this specification carries a requirement
identifier of the form `SPS-<AREA>-<NNN>`. A statement without one is not normative and an
implementation is not obliged by it.

<a id="SPS-CORE-003"></a>
**`SPS-CORE-003`** — Requirement identifiers are permanent. An identifier MUST NOT be reassigned to
a different statement, and MUST NOT be renumbered. A requirement that is retired is marked
`withdrawn`, keeps its identifier and its original text, and names its successor if it has one.

That promise is what makes an identifier safe to cite from a conformance report, an implementation
note or a bug tracker that this project never sees. It is the same promise the vocabulary makes for
RDF terms, for the same reason.

It begins at the `0.1` tag, which is when there is first something to cite. Until then a requirement
may be deleted outright, identifiers may be renumbered, and a requirement whose meaning changes may
keep its identifier; [`../../GOVERNANCE.md`](../../GOVERNANCE.md) states the window, what it is not
for, and what closes it. This chapter is descriptive until that same tag, and the two facts expire
together.

## 2. What conforms

**The subject of this specification is one pod.** Every requirement in it can be satisfied by a pod
that is the only one in existence, and none of them needs a second pod to mean anything. A
deployment that serves many pods is conformant when each of those pods is; how it provisions them,
tells them apart, or administers them across the set is an extension of an implementation and not a
part of this specification.

<a id="SPS-CORE-004"></a>
**`SPS-CORE-004`** — A **conformant sempods implementation** MUST satisfy every `MUST` and
`REQUIRED` statement in the core chapters: this chapter, `contexts`, `grants`, `auth`, `lod-crud`,
`sparql` and `find`. There is no partial core.

<a id="SPS-CORE-005"></a>
**`SPS-CORE-005`** — A **module** is an optional chapter set with its own area prefix and its own
version. An implementation that advertises a module MUST satisfy every `MUST` and `REQUIRED`
statement in it. An implementation that does not advertise a module MAY omit it entirely.

<a id="SPS-CORE-006"></a>
**`SPS-CORE-006`** — An implementation MUST NOT advertise a module it satisfies only in part. There
is no partial module, for the same reason there is no partial core: a client that has to probe which
half it received has no contract.

The modules defined by this specification are `oidc`, `media` and `mcp`.

## 3. Addressing

<a id="SPS-CORE-007"></a>
**`SPS-CORE-007`** — A pod is addressed under a base URL. Every resource, context and control-plane
route of that pod lives under that base URL.

This specification does not prescribe how the base URL decomposes. A path segment under a shared
origin, a host of the pod's own, and an origin that is a single pod are the same pod as far as every
other requirement is concerned. What a client is given is the base URL, and `{pod}` throughout this
specification means it.

<a id="SPS-CORE-008"></a>
**`SPS-CORE-008`** — The path segment `_system` immediately below a pod base URL is reserved for the
control plane. An implementation MUST NOT serve ordinary Linked Data resources from
`{pod}/_system/…`, and MUST NOT allow RDF writes to alter control-plane state.

<a id="SPS-CORE-009"></a>
**`SPS-CORE-009`** — A pod's resource IRIs are minted from the address the server is publicly known
by, not from the address a particular request arrived at. An implementation MUST mint the same IRI
for the same resource regardless of the `Host` header a request carried.

Pod IRIs end up in other people's data. A pod that mints them from the request would emit a
different identifier for the same resource depending on how it was reached, and every one of those
would be wrong somewhere.

## 4. Conformance discovery

An implementation states what it provides at a well-known control-plane route, so that "optional"
is something a client can ask about rather than a heading in a document.

<a id="SPS-CORE-010"></a>
**`SPS-CORE-010`** — An implementation MUST serve `GET {pod}/_system/conformance`. The route MUST be
readable without authentication.

<a id="SPS-CORE-011"></a>
**`SPS-CORE-011`** — The response MUST be `application/json` and MUST carry a `specVersion` string
naming the core version implemented, and a `modules` array. Each entry MUST carry an `id` — the
module's IRI — and a `version` string.

```json
{
  "specVersion": "0.1",
  "modules": [
    { "id": "https://schema.sempods.org/module/media", "version": "0.1" },
    { "id": "https://schema.sempods.org/module/mcp",   "version": "0.1" }
  ]
}
```

<a id="SPS-CORE-012"></a>
**`SPS-CORE-012`** — A module absent from `modules` MUST be treated by a client as not provided. An
implementation MUST NOT rely on a client probing a module's routes to discover it.

<a id="SPS-CORE-013"></a>
**`SPS-CORE-013`** — A client MUST tolerate a `modules` entry whose `id` it does not recognise, and
MUST NOT fail on unknown members of the response object. Discovery is expected to grow.

## 5. Error model

The chapters that follow use these status codes with these meanings and do not restate them.

<a id="SPS-CORE-014"></a>
**`SPS-CORE-014`** — An implementation MUST answer with the following status codes:

| Status | When |
|---|---|
| `400` | Malformed request — including an invalid grant string and invalid SPARQL |
| `401` | Authentication is required and was missing, or was present and rejected |
| `403` | Authenticated, but lacking the grant or scope the operation requires |
| `404` | The resource or context does not exist, or the caller cannot see that it does |
| `409` | The request was well formed and authorized on arrival, and the state changed underneath it |
| `500` | Server error |

<a id="SPS-CORE-015"></a>
**`SPS-CORE-015`** — **On an operation that requires authentication**, a missing bearer token and a
rejected bearer token MUST produce the same response: `401` with `invalid_token`. An implementation
MUST NOT let a caller distinguish the two.

The qualifier is load-bearing and was missing. A public read requires no authentication
([`SPS-GRANT-031`](grants.md#SPS-GRANT-031)), so a request carrying no token is not a failed
authentication there — it is a request by a caller who never claimed to be anyone.

What does **not** depend on the operation: a token that was *presented* and rejected is always
`401`, on every route, including one an anonymous caller could have used without any token at all.
An implementation MUST NOT fall back to anonymous when a presented credential fails
([`SPS-AUTH-043`](auth.md#SPS-AUTH-043)).

<a id="SPS-CORE-016"></a>
**`SPS-CORE-016`** — Where an operation is one an unauthenticated caller may perform, the absence of
a bearer token is not an error. `401` is correct only where the operation itself requires
authentication.

<a id="SPS-CORE-017"></a>
**`SPS-CORE-017`** — On a **read**, an implementation MUST NOT disclose the existence of a context
the caller has no read grant for. A context named in a read downscope that the caller cannot read
MUST be excluded silently: no `403`, no `404`, no diagnostic header, and no difference from a
context that holds nothing.

This is the cross-cutting rule an implementation is most likely to break by accident, usually by
answering `403` where silence was required — which tells the caller the context exists. What an
empty result then means is the chapter's business: a resource read answers `404`, and a query or a
`find` answers success with nothing in it.

<a id="SPS-CORE-018"></a>
**`SPS-CORE-018`** — On a **write**, the two failures are currently distinguished: a context that is
not registered produces `404`, and a registered context the caller may not write produces `403`.

**This is a known defect, recorded rather than blessed.** It is what the reference implementation
does, and while this specification is descriptive that is what it says — but the asymmetry with
`SPS-CORE-017` is a context-enumeration oracle, not a design. A caller who can reach the write path
learns which guessed context IRIs are registered by watching which answer comes back, and context
names are freely chosen, so guessing is not hard.

What makes it narrower than the read path, and only narrower: a write names one context per request
rather than accepting a list, so enumeration costs one request per guess.

What an implementation is asked to weigh, given that this requirement will change: answering `404`
for both costs a caller the ability to tell "no such context" from "not yours", and a client that
cannot tell them apart retries a permission problem forever. Checking authorization *before*
existence — which context deletion already does ([`SPS-CTX-020`](contexts.md#SPS-CTX-020)) — gives
`403` without confirming anything, and is the shape this should take. Closing it is on the
specification's roadmap, before `0.1` becomes prescriptive.

## 6. Standards profiled

Named, not re-explained. A chapter states the deviations from these; where it is silent, the
standard applies unchanged.

| Standard | Where |
|---|---|
| RFC 9110 (HTTP Semantics) | throughout — verbs, status codes, conditional requests |
| RFC 7396 (JSON Merge Patch) | `lod-crud`, resource PATCH |
| RFC 7232 (Conditional Requests) | `lod-crud`, ETag and `If-Match` |
| RFC 8288 (Web Linking) | `lod-crud`, edit-URL advertisement |
| RFC 4648 §5 (base64url, no padding) | `lod-crud`, embedded IRIs in paths |
| RFC 6749 / OAuth 2.1 | `auth` |
| RFC 7636 (PKCE) | `auth` |
| RFC 7591 (Dynamic Client Registration) | `auth` |
| RFC 9728 (Protected Resource Metadata) | `auth` |
| RFC 8414 (Authorization Server Metadata) | `auth` |
| SPARQL 1.1 Query | `sparql` |
| JSON-LD 1.1 | `lod-crud` |
| Linked Data Principles (Berners-Lee) | `lod-crud`, resource GET |
