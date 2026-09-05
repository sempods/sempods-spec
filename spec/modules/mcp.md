# Module: MCP

**Optional.** Everything in this chapter binds only an implementation that advertises the module IRI
`https://schema.sempods.org/module/mcp` at the conformance endpoint
([`SPS-CORE-005`](../core/index.md#SPS-CORE-005)).

A pod's MCP endpoint is an agent-facing projection of surfaces the core chapters already define. It
adds no authority and no data path of its own — which is the property most of the requirements below
exist to preserve.

**Status: descriptive.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: the Model Context Protocol, JSON-RPC 2.0, RFC 9728, RFC 8252 §7.3. Error codes are
[`../core/index.md`](../core/index.md) §5.

## 1. The endpoint

<a id="SPS-MCP-001"></a>
**`SPS-MCP-001`** — An implementation MUST serve `POST {pod}/_system/mcp` speaking JSON-RPC 2.0 over
`application/json`.

<a id="SPS-MCP-002"></a>
**`SPS-MCP-002`** — It MUST support `initialize`, `notifications/initialized`, `tools/list` and
`tools/call`.

<a id="SPS-MCP-003"></a>
**`SPS-MCP-003`** — It MUST answer `resources/list` and `prompts/list` with an empty collection.
Every capability is exposed as a tool.

The empty answers are not placeholders. Several clients probe those methods on connect, and a
`method not found` is noise a reader of the logs then has to learn to ignore.

<a id="SPS-MCP-004"></a>
**`SPS-MCP-004`** — Error responses MUST use JSON-RPC codes: parse error, invalid request, method or
tool not found, invalid params, internal error. A rejected bearer MUST be a distinct code paired with
HTTP `401`.

## 2. Authentication modes

<a id="SPS-MCP-005"></a>
**`SPS-MCP-005`** — Anonymous access MUST be supported. With no bearer at all, a caller MUST be able
to `initialize`, list tools, and use the read tools against the pod's public contexts.

Anonymous is a supported mode on a pod's own endpoint, not a degraded one. An implementation MUST
NOT require authentication for a public read here.

<a id="SPS-MCP-006"></a>
**`SPS-MCP-006`** — Write tools MUST require a bearer.

<a id="SPS-MCP-007"></a>
**`SPS-MCP-007`** — An invalid bearer — expired, tampered, wrong signature — MUST be rejected. An
implementation MUST NOT silently downgrade it to anonymous.

<a id="SPS-MCP-008"></a>
**`SPS-MCP-008`** — The sandbox for a bearer MUST be the grants resolved server-side for its
`(client, subject)` pair, unioned with the pod's public contexts **only** where the token carries
`public-read` ([`SPS-GRANT-020`](../core/grants.md#SPS-GRANT-020)).

<a id="SPS-MCP-009"></a>
**`SPS-MCP-009`** — Every `401` MUST carry `WWW-Authenticate: Bearer` naming the pod's realm and the
pod-level Protected Resource Metadata URL.

The pod is the protected resource for an MCP caller exactly as it is for an HTTP caller, so both get
the same metadata address. A separate MCP-level resource identity would fork the OAuth flow for no
gain.

## 3. The `authorize` tool

<a id="SPS-MCP-010"></a>
**`SPS-MCP-010`** — An implementation MUST expose a synthetic `authorize` tool, and it MUST be
visible in `tools/list` in every authentication mode.

Most MCP clients are defensive: they list contexts, see nothing writable, and tell the person to
reconnect by hand rather than calling a write tool that would have produced the `401` the OAuth flow
needs. A tool the model can call the moment more access is wanted is what covers that case, and it
has to be visible before the caller has any access at all.

<a id="SPS-MCP-011"></a>
**`SPS-MCP-011`** — Calling it without sufficient access MUST produce the `401` challenge of
`SPS-MCP-009`. Calling it with a context-granted bearer and no re-authorization request MUST be an
idempotent acknowledgement.

<a id="SPS-MCP-029"></a>
**`SPS-MCP-029`** — The `authorize` tool MUST declare exactly one argument, a boolean
`reauthorize`, OPTIONAL and defaulting to false. Its schema is closed like every other
([`SPS-MCP-024`](#SPS-MCP-024)).

<a id="SPS-MCP-030"></a>
**`SPS-MCP-030`** — Its acknowledgement result MUST be an object naming the pod and the contexts the
caller may write. A challenge is not a result: it is the `401` of
[`SPS-MCP-009`](#SPS-MCP-009), not a tool error.

The tool is synthetic — it projects no HTTP operation — so a client cannot infer its shape from
anywhere else. Left undefined, each implementation invents a flag and the flow that exists to
recover access stops working across implementations, which is the one thing it cannot afford.

<a id="SPS-MCP-012"></a>
**`SPS-MCP-012`** — Where `reauthorize` is true, the implementation MUST issue the challenge even
for a bearer that would otherwise suffice, and, where that bearer names a person, MUST revoke the
refresh tokens the affected `(pod, client)` holds for them — every equivalent identity URI, per
[`SPS-AUTH-061`](../core/auth.md#SPS-AUTH-061), and not only the subject it carries.

An explicit re-authorization means *review the current consent*. Leaving parallel sessions able to
rotate around the consent screen would make the review cosmetic, and a family recorded under another
of the person's URIs is such a session.

A service token names no person ([`SPS-AUTH-017`](../core/auth.md#SPS-AUTH-017)) and carries no
refresh token ([`SPS-AUTH-036`](../core/auth.md#SPS-AUTH-036)); an anonymous `public-read` subject
is synthetic and per-request. Both get the challenge and have nothing to revoke.

<a id="SPS-MCP-013"></a>
**`SPS-MCP-013`** — An implementation MUST distinguish the client's automatic replay after the OAuth
round trip from a fresh re-authorization request, and MUST answer the replay with the
acknowledgement rather than a second challenge.

The two calls are near-identical: same tool, same arguments, same client. What separates them is the
bearer — the replay carries a token issued at or after the moment the challenge was recorded, and a
different token identity. An implementation that cannot tell them apart puts the client in a
challenge loop.

<a id="SPS-MCP-014"></a>
**`SPS-MCP-014`** — A recorded challenge MUST expire, and MUST be consumable exactly once.

<a id="SPS-MCP-031"></a>
**`SPS-MCP-031`** — Some clients treat the MCP URL itself as the protected-resource identifier. An
implementation MUST therefore serve Protected Resource Metadata at the append form on the MCP URL,
and it MUST return the **pod-level** document.

The MCP URL is an alternative spelling of the same protected resource, not a resource of its own:
the pod stays the unit of access control ([`SPS-AUTH-045`](../core/auth.md#SPS-AUTH-045)).

The host-rooted address RFC 9728 §3.1 constructs from an MCP URL is not required here, for the
reason [`../core/auth.md`](../core/auth.md) §10 gives for the pod-level one: it inserts the
well-known segment in front of the path, which puts it on the origin rather than under the pod's
base URL. A pod cannot serve what is above it. A client that probes there before its first request
finds nothing and falls back to the `401`, which [`SPS-MCP-009`](#SPS-MCP-009) makes a complete
answer for this module.

<a id="SPS-MCP-032"></a>
**`SPS-MCP-032`** — An implementation MUST NOT serve Authorization Server Metadata for the MCP URL.

The MCP URL is not an issuer identifier, and RFC 8414 §3.3 requires the `issuer` a document serves
to match the URL it was fetched from. There is no document that could satisfy both.

## 4. Client registration

<a id="SPS-MCP-015"></a>
**`SPS-MCP-015`** — An end-user MCP client MUST use dynamic registration
([`SPS-AUTH-008`](../core/auth.md#SPS-AUTH-008)). An implementation MUST NOT expect one to present a
`did:web:` identity.

Such a client has no stable origin of its own, so there is nothing for a `did:web:` identifier to
name.

<a id="SPS-MCP-016"></a>
**`SPS-MCP-016`** — Where a client re-registers with the same stable metadata, the implementation
MUST return the existing client identifier rather than minting a new one. The dedup key MUST be
derived from the registration's stable parts, with loopback redirect ports normalised away
([`SPS-AUTH-020`](../core/auth.md#SPS-AUTH-020)).

Clients that keep no persistent state re-register on every reconnect. Without dedup, each reconnect
mints an identifier the person never consented to and orphans the consent they gave — so the pod
accumulates dead grants and the user is asked again every time. Normalising the loopback port is
what makes the key survive the ephemeral port a desktop client picks per launch.

## 5. Tools

<a id="SPS-MCP-017"></a>
**`SPS-MCP-017`** — The tool catalogue MUST cover context discovery, query, retrieval, resource
read, resource write, and slot-level property editing:

| Read | Write |
|---|---|
| `list_contexts` | `create_resource` |
| `sparql_select`, `sparql_graph` | `update_resource` |
| `find` | `delete_resource` |
| `get_resource` | `set_property_values` |
| `get_property_values` | `add_property_value` |
| | `remove_property_value` |
| | `clear_property_values` |

<a id="SPS-MCP-018"></a>
**`SPS-MCP-018`** — Every tool MUST be a projection of the HTTP surface the core chapters define. An
implementation MUST NOT give a tool an authority, a sandbox or a write path the HTTP surface does not
have.

<a id="SPS-MCP-019"></a>
**`SPS-MCP-019`** — The query tools MUST dispatch through the same validation and the same sandbox as
the HTTP query surface ([`SPS-SPARQL-020`](../core/sparql.md#SPS-SPARQL-020)).

<a id="SPS-MCP-020"></a>
**`SPS-MCP-020`** — A write tool MUST carry its target context as an argument, and MUST resolve
exactly one.

<a id="SPS-MCP-021"></a>
**`SPS-MCP-021`** — Tools MUST accept absolute IRIs only, and MUST perform no prefix or CURIE
expansion ([`SPS-CRUD-025`](../core/lod-crud.md#SPS-CRUD-025)).

<a id="SPS-MCP-022"></a>
**`SPS-MCP-022`** — An implementation MUST accept any absolute resource IRI, including one in the
pod's own control-plane area ([`SPS-CRUD-011`](../core/lod-crud.md#SPS-CRUD-011)).

<a id="SPS-MCP-023"></a>
**`SPS-MCP-023`** — Where a tool wraps one of the three operations for which
[`SPS-CRUD-044`](../core/lod-crud.md#SPS-CRUD-044) defines an outcome word — adding a value to a
slot, clearing a slot, removing an edge — its result MUST carry that same word. A tool wrapping any
other write MUST NOT invent one.

A wholesale replace has no second case to report, which is why `SPS-CRUD-044` gives it no word and
why this requirement must not demand one: an implementation asked to mirror a word that does not
exist has to make one up, and two implementations would make up different ones.

An agent and a plain HTTP client reporting the same event in different words is a support burden
that never ends, and the two surfaces have no reason to disagree.

### Closed schemas

<a id="SPS-MCP-024"></a>
**`SPS-MCP-024`** — Every tool schema MUST declare that no additional arguments are permitted, and
the implementation MUST **enforce** it: a call carrying an argument the tool does not declare MUST be
rejected before dispatch.

<a id="SPS-MCP-025"></a>
**`SPS-MCP-025`** — An unknown argument MUST NOT be silently dropped.

This is the module's most important requirement and the one an implementation is most likely to get
wrong by doing the ordinary thing. The caller is a language model, and a model that invents a
plausible argument — a filter the specification does not have, a mistyped context, a second body
field alongside the real one — must not have it ignored. Ignoring it executes a *different*
operation than the one the model asked for, broader on a read and wrong on a write, and returns
success. Failing closed turns a hallucination into an error message the model can act on.

<a id="SPS-MCP-026"></a>
**`SPS-MCP-026`** — The advertised schema and the enforcement MUST come from one source, so they
cannot drift.

## 6. Session instructions

<a id="SPS-MCP-027"></a>
**`SPS-MCP-027`** — `initialize` SHOULD return per-session instructions naming the pod, the contexts
granted with their permission levels, which of them are writable, and how to discover the pod's
vocabulary.

<a id="SPS-MCP-028"></a>
**`SPS-MCP-028`** — Where instructions are returned, they MUST be regenerated on every `initialize`,
so that a reconnect after a consent change reflects the new access.

A pod pins no vocabulary, so a client cannot assume one. Telling it at connect time what is there
and how to look is what replaces the schema an agent would otherwise guess at.

## 7. Not defined here

A **hosted multi-pod MCP service** — one connection fronting many pods, including pods run by other
people — is a different thing from a pod's own endpoint and is not specified by this module. Two
differences are worth knowing so nothing here is read into it: such a service has no anonymous mode,
and toward each pod it is an ordinary OAuth client rather than part of the pod.

Also outside: which upstream MCP protocol revisions an implementation negotiates, per-client quirks,
and audit-log shape.
