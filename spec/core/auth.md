# Authorization and client identity

How an application or an agent gets a token a pod will accept, and what a pod may conclude from it.
What that token then *permits* is [`grants.md`](grants.md); this chapter stops at the point where a
caller is identified.

**Status: descriptive.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: OAuth 2.1 and RFC 6749, RFC 7636 (PKCE), RFC 7591 (Dynamic Client Registration),
RFC 8252 §7.3 (native app redirect URIs), RFC 9728 (Protected Resource Metadata), RFC 8414
(Authorization Server Metadata), OIDC Core 1.0 §3.1.2.1 (`prompt`). Error codes are
[`index.md`](index.md) §5.

## 1. Flows

<a id="SPS-AUTH-001"></a>
**`SPS-AUTH-001`** — The only user-facing flow an implementation MUST support is OAuth 2.1
Authorization Code. An implementation MUST NOT accept the implicit flow or the resource owner
password credentials grant.

<a id="SPS-AUTH-002"></a>
**`SPS-AUTH-002`** — An implementation MUST support the Client Credentials grant for service clients
(§4), and MUST NOT offer it to any other class of client.

## 2. Client identity has three shapes

Prescribing the wrong one produces a client that cannot connect, so the distinction is a question
about the client's *role*, not about its label.

| Shape | Who | Registration |
|---|---|---|
| `did:web:*` | an application with a stable HTTPS origin | none — the identity *is* the origin |
| `dyn:*` | an end-user client with no origin of its own | RFC 7591 dynamic registration |
| service client | a backend acting inside its own sandbox | out-of-band, by the host operator |

### `did:web:*` — origin-bound

<a id="SPS-AUTH-003"></a>
**`SPS-AUTH-003`** — A `did:web:` client identifier MUST be parsed locally and structurally. An
implementation **MUST NOT** dereference it, MUST NOT fetch a DID document, and MUST NOT fetch a
client-metadata document.

This is the strongest `MUST NOT` in the chapter, and the one an implementer is most likely to
"correct". Fetching buys no security: the identifier is an assertion either way, and the only thing
that makes it meaningful is that the authorization code goes nowhere but that origin — which is a
local check. What fetching costs is an SSRF surface in the login path, a cache to keep coherent, and
a third party whose downtime becomes a sign-in outage.

<a id="SPS-AUTH-004"></a>
**`SPS-AUTH-004`** — A `did:web:` client's `redirect_uri` MUST match the identifier's host **and**
port.

<a id="SPS-AUTH-005"></a>
**`SPS-AUTH-005`** — A path-scoped identifier MUST be matched **per path segment**. `did:web:example.org:mcp`
covers `/mcp` and `/mcp/cb`; it MUST NOT cover `/mcp-other/cb`.

A raw `startsWith` is wrong here for the same reason it is wrong for `#manage`
([`SPS-GRANT-007`](grants.md#SPS-GRANT-007)), and the consequence is worse: two services sharing a
host would receive each other's authorization codes.

<a id="SPS-AUTH-006"></a>
**`SPS-AUTH-006`** — An identifier naming a loopback origin MUST be refused outside development, and
the refusal MUST be evaluated **before** the host-and-port match that would otherwise accept it.

A `did:web:` is asserted, not issued. Without this, anyone may claim `did:web:localhost%3A5173` and
route a code to whatever happens to be listening on that port on the user's machine.

<a id="SPS-AUTH-007"></a>
**`SPS-AUTH-007`** — An implementation MUST NOT require a `did:web:` client to register.

### `dyn:*` — dynamically registered

<a id="SPS-AUTH-008"></a>
**`SPS-AUTH-008`** — An implementation MUST offer RFC 7591 dynamic client registration at
`POST {pod}/_system/auth/register`, and MUST issue identifiers prefixed `dyn:`.

<a id="SPS-AUTH-009"></a>
**`SPS-AUTH-009`** — A `dyn:` client registers with `token_endpoint_auth_method=none`. PKCE is
therefore REQUIRED for it, and an implementation MUST reject an authorization request from a `dyn:`
client that carries no `code_challenge`.

<a id="SPS-AUTH-010"></a>
**`SPS-AUTH-010`** — An implementation MUST render the consent screen for every **interactive**
`dyn:` authorization request, regardless of existing grants and regardless of any `prompt` value
other than `none`. Existing grants SHOULD arrive pre-selected, so that the common path is a single
confirmation.

`prompt=none` is the exception, and it has to be: it means *show nothing*
([`SPS-AUTH-039`](#SPS-AUTH-039)), so "always show the screen" and "show no screen" cannot both hold.
The resolution is already in [`SPS-AUTH-040`](#SPS-AUTH-040) — a `dyn:` client never auto-grants, so
`prompt=none` from one is `consent_required`, which is the non-interactive way of saying what the
screen would have asked.

<a id="SPS-AUTH-011"></a>
**`SPS-AUTH-011`** — An implementation MUST NOT issue a service token to a `dyn:` client. Dynamic
registration responses MUST NOT advertise `client_credentials`.

The asymmetry with `did:web:` is deliberate. A dynamic client reaches `/authorize` only because the
person just triggered the flow, so a confirmation is what they expect; an origin-bound client
reaches it from background-facing UI, where an unavoidable dialog is disruptive.

### Service clients

<a id="SPS-AUTH-012"></a>
**`SPS-AUTH-012`** — A service client MUST be registered out of band, through host-level operator
authority. An implementation MUST NOT allow a service client to be created through dynamic
registration or through any pod-scoped token.

<a id="SPS-AUTH-013"></a>
**`SPS-AUTH-013`** — A service client's grants MUST be fixed at registration and MUST consist only
of per-context grants. An implementation MUST NOT accept `public-read` or an OIDC scope for one.

<a id="SPS-AUTH-014"></a>
**`SPS-AUTH-014`** — An implementation MUST refuse a service client's `#manage` root that sits at or
above the pod's context namespace.

`<pod>#manage` and `<pod>/_system#manage` are both ancestors of every context on the pod, so the
slash-delimited rule would make either of them match everything. Refusing the *position* rather than
the two spellings somebody happened to think of is what makes this hold for the third spelling.

<a id="SPS-AUTH-015"></a>
**`SPS-AUTH-015`** — A service client's secret MUST be stored only as a slow one-way hash, and MUST
be returned exactly once, at the moment it is minted.

<a id="SPS-AUTH-016"></a>
**`SPS-AUTH-016`** — An implementation MUST NOT let response timing reveal whether a client
identifier is registered. A request naming an unknown client MUST perform equivalent work to one
naming a known client.

<a id="SPS-AUTH-017"></a>
**`SPS-AUTH-017`** — A service token's `sub` MUST be the client identifier, and the token MUST be
marked as belonging to the service class. A service token MUST NOT express a person.

A backend acting outside its own sandbox, or an operation whose attribution to a person other
parties must trust, is user-delegated work and belongs in the Authorization Code flow. That is a
consequence of `SPS-AUTH-017` rather than a separate rule: there is no person in the token to
attribute it to.

## 3. Redirect URIs

<a id="SPS-AUTH-018"></a>
**`SPS-AUTH-018`** — A redirect URI MUST be absolute, MUST NOT carry a fragment, MUST use `https`
on any host, and MAY use `http` only on a loopback address.

Absolute and fragment-free are RFC 6749 §3.1.2 unchanged. The scheme half is not: §3.1.2.1 only
says the redirection endpoint `SHOULD` require TLS, and this requirement raises that to a `MUST` with
OAuth 2.1, then re-opens plain `http` for the loopback case RFC 8252 §7.3 describes. A reader
distinguishing inherited behaviour from this specification's own should read the first two clauses
as the profile and the last two as the deviation.

<a id="SPS-AUTH-056"></a>
**`SPS-AUTH-056`** — A redirect URI MUST NOT carry `code`, `response` or `state` as a query
parameter.

RFC 6749 §3.1.2 permits a query component, and `SPS-AUTH-055` requires an implementation to
preserve it. This is where that permission stops, and the reason is the fragment's: those three
names belong to the authorization response. An implementation that builds a response either
overwrites what the address already carried — breaking the client that registered it — or leaves it
in place, and then hands that client a value it cannot distinguish from the response's own — the
`code` this server issues, or the `state` the client itself chose and RFC 6749 §4.1.2 obliges this
server to return unchanged. A redirect URI registered as `…/cb?state=x` receives its own `x` back
as the `state` of a request that carried none; one registered as `…/cb?code=old` can, depending on
how the response is assembled, arrive carrying two codes. Which of the two such a client redeems is
a property of its parser rather than of this protocol, and that is the situation the prohibition
removes.

`error` and `error_description` are deliberately not prohibited. A client that registers them can
only confuse itself, and no other client's response is reachable through them.

<a id="SPS-AUTH-057"></a>
**`SPS-AUTH-057`** — A query parameter counts as one of `SPS-AUTH-056`'s prohibited names when its
name, percent-decoded and matched case-sensitively, equals that name — whether or not the parameter
carries a value.

One recognition rule, and three spellings decide whether an implementation has it right. `?CODE=`
is a different parameter and stays acceptable, because it is not the `code` any client reads;
`?%63ode=` reaches the client as `code`, so it is one; and `?code` with no `=` is still that name.
Decoding is per parameter name rather than over the whole query — decoding the query first would
split a value such as `?next=a%26state%3Dx` into a parameter that was never there.

<a id="SPS-AUTH-019"></a>
**`SPS-AUTH-019`** — An implementation MUST apply `SPS-AUTH-018` and `SPS-AUTH-056` at registration
as well as at authorization, so that an address a login could never honour is refused when it is
first offered rather than at first use.

<a id="SPS-AUTH-020"></a>
**`SPS-AUTH-020`** — A loopback redirect URI MUST be matched with its port ignored (RFC 8252 §7.3).
A non-loopback redirect URI MUST be matched with its port significant.

## 4. Authorization request

<a id="SPS-AUTH-021"></a>
**`SPS-AUTH-021`** — An implementation MUST serve `GET {pod}/_system/auth/authorize` accepting
`response_type=code`, `client_id`, `redirect_uri`, `state`, `code_challenge`,
`code_challenge_method`, and OPTIONAL `scope` and `prompt`.

<a id="SPS-AUTH-022"></a>
**`SPS-AUTH-022`** — Where a `code_challenge` is present, `S256` MUST be the only accepted method,
and the method name MUST be compared case-sensitively (RFC 7636 §4.3). `plain`, `s256` and an absent
method MUST all be refused.

<a id="SPS-AUTH-023"></a>
**`SPS-AUTH-023`** — PKCE is RECOMMENDED but NOT REQUIRED for a `did:web:` client. An implementation
MUST NOT reject a `did:web:` authorization request solely because it carries no `code_challenge`.

<a id="SPS-AUTH-024"></a>
**`SPS-AUTH-024`** — The standard delegation flow MUST NOT require a `scope` parameter naming
contexts. The authorizing person selects contexts at consent time.

<a id="SPS-AUTH-025"></a>
**`SPS-AUTH-025`** — On success the implementation MUST redirect to the request's **validated**
`redirect_uri` carrying `code` and `state`; on failure, carrying `error` and `error_description`, and
OPTIONALLY `error_uri`. A client MUST treat `error_uri` as optional.

"Validated" rather than "registered", because a `did:web:` client registers nothing
([`SPS-AUTH-007`](#SPS-AUTH-007)) — its address is validated against the origin its identifier names
(`SPS-AUTH-004`, `SPS-AUTH-005`). A `dyn:` client's address is validated against what it registered.
Both are validated; only one is registered.

<a id="SPS-AUTH-055"></a>
**`SPS-AUTH-055`** — The response parameters MUST be **added to** the redirect URI's query
component per RFC 6749 §4.1.2, preserving any component it already carries. An implementation MUST
NOT construct the redirect by appending `?` to the registered value.

A registered address may legitimately carry a query — `https://app.example/cb?tenant=a` is an
ordinary redirect URI. Appending `?code=…` to it produces a second `?`, which puts the
authorization response inside the value of `tenant` and loses the code.

Preserving a component the client chose is safe only because
[`SPS-AUTH-056`](#SPS-AUTH-056) keeps the response's own names out of it. Without that
prohibition this requirement is what makes a registered `code` reach the client alongside the
issued one.

## 5. Consent

<a id="SPS-AUTH-026"></a>
**`SPS-AUTH-026`** — Submitting a consent decision MUST require two independent things: a session
established on the pod's own origin, and a token minted for that one consent screen and accepted
only once.

Neither alone is enough, and the reason is not defence in depth for its own sake. A screen token
lifted out of a page cannot be spent without the session; the session alone does not imply consent
to anything. The single-use half is what stops a replay: a submission writes the selection as *the*
grant set, so a replayable form could restore a selection the person has since narrowed.

## 6. Token endpoint

<a id="SPS-AUTH-027"></a>
**`SPS-AUTH-027`** — An implementation MUST serve `POST {pod}/_system/auth/token` accepting
`application/x-www-form-urlencoded`, supporting `authorization_code`, `refresh_token` and
`client_credentials`.

<a id="SPS-AUTH-028"></a>
**`SPS-AUTH-028`** — An access token MUST be a signed JWT whose issuer is the pod's base URL, and
MUST carry the authorizing subject, the client identifier, and its scope set.

<a id="SPS-AUTH-029"></a>
**`SPS-AUTH-029`** — The `scope` claim MUST carry feature scopes only. An implementation MUST NOT
place per-context grants in it — see [`SPS-GRANT-001`](grants.md#SPS-GRANT-001).

<a id="SPS-AUTH-030"></a>
**`SPS-AUTH-030`** — An implementation MUST publish its signing keys at
`GET {pod}/_system/auth/jwks.json`.

<a id="SPS-AUTH-031"></a>
**`SPS-AUTH-031`** — A `scope` parameter on a refresh exchange MAY narrow the token's feature
scopes and MUST NOT widen them.

<a id="SPS-AUTH-032"></a>
**`SPS-AUTH-032`** — An implementation MUST reject a `scope` parameter on a `client_credentials`
exchange with `invalid_scope`.

A service token carries no per-token state that could express a subset; it grants the client's
registered set or nothing.

### Refresh tokens

<a id="SPS-AUTH-033"></a>
**`SPS-AUTH-033`** — Refresh tokens MUST be rotated. A refresh token belongs to a family seeded at
code exchange, and on detected reuse of an already-rotated token the implementation MUST revoke the
whole family.

<a id="SPS-AUTH-034"></a>
**`SPS-AUTH-034`** — A refresh token MUST NOT be stored in a form from which the presented value can
be recovered.

<a id="SPS-AUTH-035"></a>
**`SPS-AUTH-035`** — A token issued for `public-read` MUST NOT carry a refresh token. The client
re-authorizes when it expires.

<a id="SPS-AUTH-036"></a>
**`SPS-AUTH-036`** — A service token MUST NOT carry a refresh token.

### Abuse

<a id="SPS-AUTH-037"></a>
**`SPS-AUTH-037`** — An implementation SHOULD rate-limit the token endpoint, and where it does, it
MUST key the first tier on the caller's network address rather than on a client identifier.

The order is the whole point. A client identifier arrives as a form parameter, so a caller can vary
it, and counting it first hands out a fresh budget per invented name. Which name identifies the
caller is also decided by the grant and not by what is present: `client_credentials` authenticates
the Basic credential and never reads the form field; the other grants read the form field and ignore
the header. Accepting whichever is present gives a caller two key spaces to choose from.

<a id="SPS-AUTH-038"></a>
**`SPS-AUTH-038`** — Where a request is refused for rate, the response MUST be `429` with
`Retry-After` and the OAuth error `slow_down`.

## 7. `prompt`

<a id="SPS-AUTH-039"></a>
**`SPS-AUTH-039`** — An implementation MUST interpret `prompt` per OIDC Core 1.0 §3.1.2.1:
space-separated and multi-valued. Absent, it MAY auto-grant where grants exist; `consent` MUST show
the consent screen; `none` MUST show no interactive screen; `login` MUST force fresh authentication.

<a id="SPS-AUTH-040"></a>
**`SPS-AUTH-040`** — `prompt=none` MUST succeed only where all three hold: the pod itself remembers
the person, the client is not a `dyn:` client, and grants for that client survive. Otherwise the
implementation MUST answer `login_required` or `consent_required`.

<a id="SPS-AUTH-041"></a>
**`SPS-AUTH-041`** — `prompt=login` MUST NOT be satisfied by an existing session. The person asked
to prove themselves again, and the session is exactly what they asked to bypass.

A client SHOULD treat `login_required` and `consent_required` identically: fall back to a full
interactive authorization. The distinction is diagnostic, not actionable.

## 8. `public-read`

<a id="SPS-AUTH-042"></a>
**`SPS-AUTH-042`** — `scope=public-read` MUST be accepted at the authorization endpoint, with or
without an established identity. Without one, the issued token's subject MUST be a synthetic,
opaque, per-request anonymous identifier.

<a id="SPS-AUTH-043"></a>
**`SPS-AUTH-043`** — Where an identity assertion is present but invalid or expired, the
implementation MUST fail with `access_denied`. It MUST NOT silently downgrade the request to
anonymous.

The precedence is: invalid assertion beats invalid scope beats absent assertion. A manipulated
credential is a hard signal, and quietly treating its bearer as an anonymous visitor is how a
tampered token becomes a successful request.

<a id="SPS-AUTH-044"></a>
**`SPS-AUTH-044`** — Where the pod has no public context, the implementation MUST answer
`consent_required` rather than issue a token that can read nothing.

## 9. Identity

What a pod stores about a person, as opposed to how they signed in. How they signed in is the
[`oidc`](../modules/oidc.md) module, and it is optional; this is not.

<a id="SPS-AUTH-049"></a>
**`SPS-AUTH-049`** — A pod MUST know a person only as a WebID URI. An implementation MUST NOT store
a local user record as the identity a grant names, and MUST NOT accept a consumer's internal user
identifier in place of one.

<a id="SPS-AUTH-050"></a>
**`SPS-AUTH-050`** — Where a person is introduced by an email address, the implementation MUST derive
a deterministic identity URI from it and store that. The address itself MUST NOT become the
identity.

A deterministic derivation is what lets a pod address a person before any identity service exists,
and lets the same person keep their grants when one appears.

<a id="SPS-AUTH-051"></a>
**`SPS-AUTH-051`** — Pod ownership MUST be decided by comparing the request's subject against the
pod's recorded owner, not by a grant and not by a scope.

This is what lets a pod with no contexts acquire its first one. An owner whose authority came from a
grant would need a grant on a context that does not exist yet.

<a id="SPS-AUTH-052"></a>
**`SPS-AUTH-052`** — Where a person is known by several equivalent identity URIs, an implementation
MUST apply the equivalence when a grant is **written**, and MUST NOT apply it when one is read.

A request carries one identity URI. Resolving equivalences on the read path would put an identity
join on every authenticated request and make the answer depend on state that changed since the
grant was made.

<a id="SPS-AUTH-053"></a>
**`SPS-AUTH-053`** — An identity assertion MUST NOT be usable as a pod credential. An implementation
MUST consume it once, at the login callback, and MUST NOT accept it as a bearer token afterwards.

<a id="SPS-AUTH-054"></a>
**`SPS-AUTH-054`** — A pod MUST accept a browser session credential only where it issued that
credential for itself.

Stated as what the pod accepts rather than as where the browser sends it, because the browser is the
wrong place to put the boundary. A cookie is not scoped by port and only coarsely by path, so a
deployment cannot confine one to a pod's base URL, and a requirement that asked it to would forbid
ordinary cookie sessions while buying nothing: the credential still arrives, and what matters is
that the pod refuses it. Narrowing the cookie is worth doing and is an implementation's business.

A sign-in at one pod is therefore not a sign-in at another, including where both are served from the
same host. That follows from what each pod accepts, which is where it can be tested.

## 10. Discovery

<a id="SPS-AUTH-045"></a>
**`SPS-AUTH-045`** — An implementation MUST serve RFC 9728 Protected Resource Metadata at
`GET {pod}/.well-known/oauth-protected-resource`, without authentication, carrying at least
`resource`, `authorization_servers` and `bearer_methods_supported`.

That is the append form, and it is the only one this specification requires. The host-rooted address
RFC 9728 §3.1 constructs — the well-known segment inserted between the authority and the resource's
path — is a route on the origin rather than under the pod base, and a pod whose base URL is
path-scoped cannot serve it without owning everything beside it. A deployment can, and one that
hosts many pods is the right place for it.

The narrowing that follows is deliberate rather than an oversight. A generic client doing RFC 9728
discovery ahead of its first request finds nothing at the host-rooted address of a path-scoped pod,
and reaches the metadata only by asking the pod: an unauthenticated request, a `401`, and the
`resource_metadata` hint in `WWW-Authenticate` that names the address above.

**Core does not yet require that hint**, which makes the fallback weaker than it reads.
[`SPS-MCP-009`](../modules/mcp.md#SPS-MCP-009) requires it of a pod that provides the MCP module,
and nothing requires it of one that does not — so a client of such a pod is left constructing the
append form by convention. This chapter is likewise silent on where RFC 8414 Authorization Server
Metadata lives, though it profiles the standard and [`SPS-AUTH-048`](#SPS-AUTH-048) constrains what
that document may claim. Both are recorded rather than blessed, and closing them is on the
specification's roadmap, before `0.1` becomes prescriptive.

<a id="SPS-AUTH-046"></a>
**`SPS-AUTH-046`** — Protected Resource Metadata MUST NOT enumerate the pod's public context IRIs.
A count MAY be advertised.

The URIs would be a topology leak on an unauthenticated route — the same rule as
[`SPS-CORE-017`](index.md#SPS-CORE-017), reached from the other direction.

<a id="SPS-AUTH-047"></a>
**`SPS-AUTH-047`** — A consumer MUST tolerate members of the metadata document it does not
recognise.

<a id="SPS-AUTH-048"></a>
**`SPS-AUTH-048`** — Where an implementation advertises RFC 8414 Authorization Server Metadata, its
`grant_types_supported` MUST list `client_credentials` only if the implementation registers service
clients.
