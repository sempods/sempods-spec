# Protocol profiles for the data-access contract

Status: **Proposed; non-normative.**
Owning decision issue: [#69](https://github.com/sempods/sempods-spec/issues/69), under
[#68](https://github.com/sempods/sempods-spec/issues/68).
Adoption: [#70](https://github.com/sempods/sempods-spec/issues/70) prepares selected requirements,
[#71](https://github.com/sempods/sempods-spec/issues/71) their views and
[#72](https://github.com/sempods/sempods-spec/issues/72) their validation; #74 owns adoption.
No change proposed here is adopted by merging this document.

## Boundary

A client needs a known wire contract, not every capability of the libraries implementing it.
Apply the [vision's selection test](../vision.md#what-belongs-in-the-contract) and
[SPS-CORE-021](../../spec/core/index.md#SPS-CORE-021): select the operations and capabilities first,
then incorporate their standard behavior. A scoped reference does not prohibit an implementation
from offering an additional compatible capability unless a requirement explicitly does so.

This recommendation evaluates the protocol candidates retained from
[PR #82 at `4d35c56`](https://github.com/sempods/sempods-spec/tree/4d35c56ef9ed301fbb0d6b5b674b9638cad3b575)
against [main at `159d89a`](https://github.com/sempods/sempods-spec/tree/159d89aa88404d41427ba920f3a0b70972f0aa18).
The candidate's identifiers are historical: its service-refresh `AUTH-064` is not today's
[SPS-AUTH-064](../../spec/core/auth.md#SPS-AUTH-064), which governs authentication challenges.
The old branch is reference material; reuse requires the dispositions below.

## Already adopted inputs

Core discovery follows [auth §10](../../spec/core/auth.md#10-discovery), adopted in
[PR #98](https://github.com/sempods/sempods-spec/pull/98). For MCP,
[PR #111](https://github.com/sempods/sempods-spec/pull/111) adopted endpoint resource identity,
host-rooted discovery and resource-bound credentials in
[SPS-MCP-033–038](../../spec/modules/mcp.md#discovery-and-resource-binding).
The endpoint is the resource and token audience; the pod base is the issuer. The candidate's
MCP append-alias and pod-resource validation recommendations are superseded. MCP-031/032 remain
withdrawn under [PR #108](https://github.com/sempods/sempods-spec/pull/108).

[#99](https://github.com/sempods/sempods-spec/issues/99) retains the unmodified-client evidence:
parent-resource, origin-resource and mismatching-issuer metadata still reach a redirect in the
recorded SDK experiment. The [evidence guide](../guides/repository-checks.md#mcp-endpoint-discovery-experiment)
states its limits. Those failed cases do not reopen the adopted identity/address choice or prevent
#69 from recording it. They remain required acceptance in #99; no release condition is waived.
Kotlin delivery and deployment verification remain in
[sempods-kotlin#193](https://github.com/sempods/sempods-kotlin/issues/193).

The conditional state response and equivalent-identity claim are separately adopted in
[PR #105](https://github.com/sempods/sempods-spec/pull/105) and
[PR #107](https://github.com/sempods/sempods-spec/pull/107). Preserve their current requirements.

## Selected standards and candidate dispositions

These are recommended inputs to normative preparation. “Retain” preserves the selected capability;
“revise” identifies a proposed profile change, not an editorial shortcut.

| Candidate | Recommendation and reason | Affected contract |
|---|---|---|
| Shared HTTP profile and chapter-local HTTP references | Already supplied by CORE-020/021. Retain RFC 9110 for selected HTTP operations, including optional media and management. No duplicate obligations. | Core §6; media and context-management profile introductions. |
| OAuth 2.1 draft-13 overriding RFC 6749 | Select RFC 6749 §§2–3, 4.1, 4.4 and 5–7 for client identity, endpoints, code, service, refresh and token use; RFC 7636 §§4/7 for PKCE; RFC 6750 §§2.1/3 for Bearer presentation/challenges; and the security scope below. AUTH-001 continues to prohibit implicit/password grants; §4.5 adds no extension grant. Replace the unversioned OAuth 2.1 claim. Preserve the explicit registration, redirect, scope and error choices identified below. | Auth profile, AUTH-001/003–011/018–023/025/027/031–033/037–038/059/064–068, GRANT-001–003 and core profile/error model; authorize/token operations and OAuthError. |
| Browser and native clients | Select the [bounded RFC 10017 profile below](#browser-client-profile); RFC 8252 §7.3 supplies native loopback redirects. Keep HTTPS/loopback and did:web origin/path constraints as explicit sempods choices. Private-use URI schemes are not added by this selection. | Auth profile; AUTH-003–009/018–023/033/055–057/059 and browser-facing endpoint views, including CORS; MCP redirect references. |
| Dynamic registration | Retain RFC 7591 §§2–3, including defaults, actual registered metadata and error responses. The unauthenticated public profile stays separate from protected service registration in the [service-client recommendation](access-control.md#service-clients-and-registration-authority). Software statements, registration management and metadata fetching do not become required capabilities. | AUTH-008/009/011; registration OpenAPI under #77/#71. |
| Service refresh-token prohibition | Reject the candidate's unconditional ban; retain RFC 6749 §4.4.3's recommendation against issuance. The exception below generalizes code-seeded families and applies §6's confidential-client authentication to service refresh. | AUTH-015–017/027/031–034/037 and its dispatch explanation/063; token operation, TokenRequest/TokenResponse and authentication errors. Never reuse current AUTH-064 for this candidate. |
| OAuth `prompt` | Retain OIDC Core 1.0 errata set 2 §3.1.2.1 for `prompt` alone. Preserve AUTH-010/039–041's consent/session choices, including the `dyn:` restriction on silent authorization. | Auth profile and authorize operation; no new `openid` scope or ID Token on the pod OAuth surface. |
| OIDC bridge and redirect exception | Select the [OIDC bridge profile below](#oidc-bridge-profile), including the registration-free redirect exception and exact exchange binding. | OIDC profile, OIDC-002–011/014–018 and their explanatory prose; module-oidc callback and identity-service discovery/token views. |
| MCP revision, lifecycle and messages | Select MCP 2025-11-25 [Messages](https://modelcontextprotocol.io/specification/2025-11-25/basic/index#messages), [Lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle), and the tools/list, tools/call, resources/list and prompts/list operations selected by MCP-002/003. Keep JSON-RPC 2.0 §§4–5 with the error-ID distinction below. No other client/server feature or transport is selected. Empty resource/prompt lists and anonymous public access remain sempods choices. | MCP profile, MCP-001–005/017–018/024–025; request/notification/result/error schemas and capability declarations. |
| MCP Streamable HTTP | Select only the Streamable HTTP section of that revision's Transports page: security, sending/listening, connections, conditional resumability/sessions and protocol-version headers. A server may use JSON responses with GET returning 405, without sessions or SSE. Stdio, custom transports and backwards compatibility add no required capability. Reconcile transport failures with the core error model as below. | CORE-014–016, MCP-001/002/004–007/009; POST/GET/DELETE, conditional session/version headers, bodies and response views under #71. |
| MCP authorization exclusion | Reject the candidate's blanket exclusion: #111 already selects discovery, resource and token portions of MCP 2025-11-25 authorization. Preserve that bounded selection; neither its whole OAuth draft nor Client ID Metadata Documents is imported. | MCP-033–038 and current profile; no rollback of #111. |
| RDF named-graph model | Retain RDF 1.1 Concepts, Recommendation 2014-02-25, §§3–4. RDF supplies graphs/datasets, not storage partitions, grants, the contents of D or exclusive statement membership. Those choices are owned by the [data-access proposal](data-access.md). | Context/grant profile introductions; CTX-001 and related impact map. |
| OAuth scope definition | Retain RFC 6749 §3.3 for feature-scope syntax/semantics; it does not define the server's data-grant representation. | Grants profile and GRANT-001–003. |
| CRUD and media representations/validators | Select RFC 7396 §2 for PATCH processing; RFC 4648 §5 with CRUD-005's no-padding choice; JSON-LD 1.1 (2020-07-16) §§8–9/10.1 for the data model, grammar and RDF correspondence of the selected resource/value/named-graph shapes. CRUD-012/023–025/035–038 retain their input and shape restrictions; no general JSON-LD processor, framing or context fetching is selected. Use RFC 9110 §§8.8/13 and [§9.3.4](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.4) instead of RFC 7232. Linked Data principles remain informative; CRUD-058 already selects RFC 8288 §3/RFC 5023 §16.4 for optional edit links. | Core/CRUD/media profiles, CRUD-005/012/023–030/034–038/052–054/058 and representation/conditional-response views. Correct CRUD-030's §10.2.3 citation to §9.3.4; retain its broader sempods ban on write ETags rather than attributing that whole ban to PUT. |
| SPARQL revision and transport exclusions | Select Query and Protocol Recommendations 2013-03-21: Query semantics subject to the sandbox; Protocol §1, [§2.1.3 (direct POST)](https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#query-via-post-direct), §§2.1.4–2.1.7 (datasets/responses), §2.3 and §4. Form POST is §2.1.2, outside this selection. Full-protocol §5 conformance is not claimed. GET/form POST are not required; Update and SERVICE remain expressly forbidden. | SPARQL profile; SPARQL-001–014 for input/datasets, SPARQL-015–018 for result media types, 406, empty input and well-formed empty results, and SPARQL-019/020 for bounded execution/shared validation. Audit those SPS constraints against the inherited response rules; preserve them and optional dataset-parameter support pending the coordinated selector changes. |
| Response quoting, schema validation and CI | Keep with #77. These are independent fidelity/tooling candidates, not justification to add protocol restrictions. The two semantic findings have the dispositions below; the remaining validators and operation repairs still need their own current-main audit. | OpenAPI descriptions and repository tooling; no new core capability. |

The security scope is [RFC 9700 §§2.1, 4.4, 4.5, 4.7, 4.8 and 4.14](https://www.rfc-editor.org/rfc/rfc9700.html)
for redirect/code protection, mix-up, CSRF, PKCE downgrade and refresh replay on the selected flows.
Retain the [authorization proposal](access-control.md#authorization-without-context-setup)'s S256
PKCE for both user-facing client shapes, conditional state echo, issuer-bound transactions and
fresh-consent barriers. The did:web registration-free origin/path check is an explicit exception
to pre-registered exact matching, not proof of client authentication. PKCE protects code redemption;
consent and current policy independently bound authority. Dynamic clients retain registered-URI
matching with the native-loopback port exception.
The pod's feature scopes remain distinct from data grants (GRANT-001–003); AUTH-032 rejects
service-exchange scope input and AUTH-059 keeps `offline_access` optional. Preserve AUTH-038's
`429 slow_down` and AUTH-064's bearer challenges as sempods choices. Token-endpoint client
authentication errors instead follow RFC 6749 §5.2, including Basic's `401` and matching challenge;
they are not resource-server `invalid_token` errors.

Primary profile sources: [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html),
[RFC 7636](https://www.rfc-editor.org/rfc/rfc7636.html),
[RFC 7591](https://www.rfc-editor.org/rfc/rfc7591.html),
[RFC 8252 §7.3](https://www.rfc-editor.org/rfc/rfc8252.html#section-7.3),
[RFC 10017](https://www.rfc-editor.org/rfc/rfc10017.html),
[OIDC Core errata 2](https://openid.net/specs/openid-connect-core-1_0-errata2.html),
[OIDC Discovery errata 2](https://openid.net/specs/openid-connect-discovery-1_0-errata2.html),
[MCP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25),
[RDF 1.1](https://www.w3.org/TR/2014/REC-rdf11-concepts-20140225/),
[JSON-LD 1.1](https://www.w3.org/TR/2020/REC-json-ld11-20200716/),
[SPARQL Query](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/) and
[SPARQL Protocol](https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/).

## Browser-client profile

Select [RFC 10017 §§6.3.2–6.3.3](https://www.rfc-editor.org/rfc/rfc10017.html#section-6.3.2)
for public browser OAuth clients and their authorization/resource-server counterparts:
code/PKCE, CSRF, optional refresh, client authentication/impersonation, conditional cross-window
messaging and CORS on exposed browser endpoints. These obligations apply to the actor named by
the RFC; client-internal behavior is not a pod-server test.

Retain AUTH-033's rotation choice. Preserve §6.3.2.3's lifetime limits and obligation levels,
including its session-linkage recommendation; refresh issuance stays optional under #65.
The did:web rule is an explicit exception to §6.3.3.2.1's registered exact redirect matching.
It supplies no authenticated-client proof for automatic consent.

Other RFC 10017 sections are informative for this selection. In particular, §§6.1–6.2 and §8
impose no backend architecture or browser storage mechanism; §9.2 adds no DPoP requirement.
The separately selected OAuth/security profile governs prohibited flows and mix-up protection.
This scoped profile makes no whole-BCP conformance claim.

## OIDC bridge profile

For the identity-service issuer and pod relying party, select OIDC Core 1.0 errata set 2
§§2, 3.1, 5.1.2, 8 (public subjects), 9 (`none` for the registration-free pod), 10.1,
13–14, 15.1/15.4 and the §16 security rules for that code/signature flow. Select Discovery 1.0
errata set 2 §§3–5/7 for provider metadata, retrieval, validation and security. Issuer configuration
uses Discovery's append path, distinct from MCP's host-rooted OAuth metadata. This is a scoped
bridge profile, not a claim to implement every capability of either specification.

OIDC-010 replaces Core §3.1.2.1's registered redirect match with the permitted origin;
§3.1.3.2 still binds redemption to the original redirect. Its registration-free client uses
`none`, not §9's default `client_secret_basic`; origin matching is not client authentication.
Remove OIDC-010's misleading client-secret equivalence. OIDC-003/004 retain WebID subject and
relying-party audience. OIDC-006–009 require nonce, signature checking even on the back channel,
PKCE and code-only browser delivery; OIDC-011/014/015 retain parked, single-use callback state.
OIDC-005/016–018 retain the separately adopted equivalent-identity claim and trust boundary.

No implicit/hybrid flow, third-party login initiation, UserInfo, Request Object, self-issued or
pairwise provider, encryption, offline/refresh flow or WebFinger capability is selected. Advertise
actual code-flow capabilities, signing keys/algorithms and `none` authentication explicitly;
do not inherit metadata defaults for unsupported capabilities. `openid` belongs to this bridge
exchange, not to the pod's separate OAuth scopes.

## Service credentials and registration metadata

[RFC 6749 §4.4.3](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4.3) discourages service
refresh tokens; it does not prohibit them. The normal service obtains another access token using
its client credentials. No interoperability case identified here requires strengthening that
recommendation to an unconditional ban.

The proposed exception preserves the service subject/class, current service authority, client
binding, rotation/reuse revocation and resource binding where MCP applies. Public-client refresh
identifies the client with form `client_id` and requires no secret. Confidential service refresh
requires current client authentication under RFC 6749 §§3.2.1/6, using Basic as for its service
exchange. Replace AUTH-037's explanation that all non-`client_credentials` grants ignore Basic:
dispatch follows the client class and refresh-token binding. Invalid authentication cannot fall
back to the public-client path; conflicting identities or multiple authentication methods fail.
Retain AUTH-037's network-address rate-limit tier. Refresh cannot express a person or grant
public-read or OIDC scopes. Older credentials cannot bypass removal or withdrawn authority.
Generalize AUTH-033's family origin from only code exchange to whichever authorized grant issued
it; do not imply consent for a service. AUTH-032's rejection of `scope` on Client Credentials stays.
This is proposed new permission under the current family contract, with corresponding tests and
migration review required at adoption. Clients cannot demand refresh issuance or a particular lifetime.

Service issuance is admitted against the live registration instance, current client authentication,
assigned authority and credential-revocation state. Removal, revocation or an authority change that
wins before admission invalidates the old issuance decision; a fresh request uses the new state.
Recreating the same identifier or restoring permissions cannot revive a pending old decision or a
revoked credential. A logical generation can distinguish these states without prescribing storage.

For credentials issued before a change, distinguish authentication from current data authority:

- Service removal or revocation of the issued credentials makes their subsequent use fail
  authentication. A late successful issuance response cannot revive them.
- With only data authority withdrawn, otherwise valid credentials still authenticate. The server
  resolves current rights for each request: a previously allowed write is now `403`, while an
  independently retained read still succeeds. Refresh may succeed if its authorization survives,
  but cannot restore the withdrawn rights. If the refresh authorization itself was revoked,
  refresh fails. Explicit later assignment can grant new data authority to the still-valid service;
  that administrative action does not revive a revoked credential or an old issuance decision.

This preserves the [service-client cases](access-control.md#service-client-cases-for-review).
The [credential-race outcome](access-control.md#consent-and-credential-races) applies when service
credentials are revoked; data-authority changes alone do not imply that all credentials are revoked.

An illustrative seed-then-recheck path checks those same states after seeding, invalidates a failed
seed, and coordinates the final check/admission with withdrawal. Equivalent ordering without
seeding first is permitted. The required outcome is no usable family from an obsolete pending
decision; checking code consent alone cannot protect a service exchange with no code.

For registration, [RFC 7591 §§2 and 2.1](https://www.rfc-editor.org/rfc/rfc7591.html#section-2.1)
defines defaults and the relationship between grant and response types. A missing `grant_types`
means `authorization_code`; a missing `response_types` means `code`. The standard advises servers
to prevent inconsistent combinations. It does not impose a universal rule that every supplied
`grant_types` array contain `authorization_code`.

Reject that proposed blanket schema restriction. The proposed sempods profile chooses consistent
returned metadata, making the standard's recommendation an explicit profile rule. A
`refresh_token`-only request with omitted `response_types` has an inconsistent default, so the
recommended public registration behavior is
`400 invalid_client_metadata` or normalization to supported code-flow metadata, returned explicitly
under §3.2.1. An explicit empty response list has no such default conflict: the server may still
reject an unsupported configuration, but the schema cannot call it universally invalid merely
because it cannot bootstrap a token. Accepting metadata issues no refresh credential. The public
profile never gains service authority through normalization. #77 can model those alternatives;
#70 must not turn a recommendation in the standard into a silent universal prohibition.

## MCP errors and transport

[MCP 2025-11-25 basic messages](https://modelcontextprotocol.io/specification/2025-11-25/basic/index)
uses string/integer request IDs and permits an error without an ID when the request ID cannot be
read. [JSON-RPC 2.0 §5](https://www.jsonrpc.org/specification#response_object) instead specifies
`id: null` in that case. Select the MCP form explicitly for this module. A correlated result/error
keeps the request's ID; an uncorrelatable MCP error omits it. This is an explicit exception to
JSON-RPC's null-ID rule.

[Streamable HTTP](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
also permits an optional ID-less error body for rejected input or invalid Origin. Model that
transport rejection separately from a response to an identifiable method call. Omission is not
permission to drop the ID from an ordinary method error. #77 owns schema/tests; adopting the dated
message profile and this explicit distinction belongs to #70/#71. Preserve MCP-004's bearer error
code and MCP-009's challenge; make the body optional only for the selected transport rejections.
Method errors retain their codes and IDs. Under the proposed CORE-014 exception, a present invalid
Origin gives `403` even for an otherwise permitted anonymous request: this is transport refusal,
not evidence that the caller authenticated or lacked a data grant. CORE-015/016 and MCP-005–007
retain their authentication meaning for requests that pass that transport check. GET without SSE
requires `405`; session DELETE permits it. Malformed JSON under otherwise valid request conditions
gives `400` under [SPS-CORE-014](../../spec/core/index.md#SPS-CORE-014).

## Proposed request and response cases

These cases are acceptance inputs, not executed HTTP or conformance evidence. Each starts with
otherwise valid input, correct authority and an independent state unless stated otherwise.
`P=https://example.org/alice`, `M=P/_system/mcp`; OAuth routes use `P/_system/auth/`.
Public registration cases supply valid `redirect_uris` and `token_endpoint_auth_method: none`.

| Case | Request or input | Expected outcome under the recommendation |
|---|---|---|
| P01 | Valid service `POST token`, `grant_type=client_credentials`, no scope | `200` service access token; normally no refresh token. Another authenticated Client Credentials request remains usable without refresh. |
| P02 | Same exchange under a justified service-refresh policy; then authenticated refresh by that service | `200`; optional refresh issuance, then rotation, service subject/class and unchanged authority ceiling. No person/public-read/OIDC authority appears. |
| P03 | A different authenticated service presents P02's refresh token; separately, a refresh request supplies conflicting Basic and form client identities | Wrong authenticated service: `400 invalid_grant`. Conflicting identities: `400 invalid_request`. Neither request receives replacement credentials or falls back to public-client refresh. |
| P04 | P02's service refresh with missing or wrong authentication; repeat after service removal | `invalid_client`, no token and no public-client fallback. Failed Basic authentication returns `401` with a matching Basic challenge under RFC 6749 §5.2; without an Authorization header, `400` or a permitted `401` client-authentication challenge follows that section. If client authentication remains valid but refresh authorization was revoked, `400 invalid_grant`; withdrawing data rights alone is P31. |
| P05 | Service requests `scope=public-read` on Client Credentials | `400 invalid_scope`; refresh support does not relax AUTH-032. |
| P06 | Service refresh token is reused after rotation | `400 invalid_grant` and family revocation; a concurrent exchange cannot preserve withdrawn authority. |
| P07 | Public registration with `redirect_uris`, method `none`, grant/response types omitted | `201` if accepted; defaults are code flow. Return actual registered metadata; no service credentials or promise of refresh issuance. |
| P08 | Public registration with `grant_types:["refresh_token"]`, response types omitted | Recommended `400 invalid_client_metadata`, or `201` with explicitly normalized consistent code-flow metadata. Never return the contradictory defaults as accepted metadata. |
| P09 | Same grant list with explicit `response_types:[]` | If unsupported, `400 invalid_client_metadata`; if accepted, `201` with those actual values. No code-flow entitlement or refresh credential is created by registration. |
| P10 | Public registration requests `client_credentials` | `400 invalid_client_metadata`, or `201` with explicitly normalized supported public metadata; never advertise or issue service authority. |
| P11 | did:web app requests code without S256 PKCE | Proposed `invalid_request` under the authorization recommendation; no code. AUTH-025 governs redirectable errors and conditional state echo; invalid client/redirect input instead forbids automatic redirection. Current AUTH-023 must change explicitly before this becomes binding. |
| P12 | `did:web:app.example:notes` with `https://app.example/notes/cb` versus `/notes-other/cb` | First can authorize with S256 and consent; second is refused without redirecting to the rejected URI. Same host alone is insufficient. |
| P13 | Native client registered `http://127.0.0.1:49152/cb` requests port 49153; path stays `/cb` | The loopback URI matches despite the changed port; a changed path or non-loopback host does not receive that exception. |
| P14 | OIDC pod client uses its permitted origin for code callback and `none` client authentication; repeat with a changed callback at exchange, then independently with mismatching discovery issuer, invalid ID Token issuer/audience/nonce/signature/expiry or replayed callback state | Valid code/PKCE flow can succeed without preregistration or a shared secret. Changed exchange callback gives `invalid_grant` under Core §3.1.3.2; the origin exception does not extend to redemption. Discovery mismatch fails metadata validation; each assertion/state failure rejects the login without resuming parked authorization under OIDC-006/015. |
| P15 | Valid MCP `initialize` proposes `2025-11-25` | Negotiates that supported revision and capabilities. This module does not require support for every earlier or future revision. |
| P16 | MCP call with `id:7` names an unknown method | JSON-RPC error `-32601`, `id:7`; no result. An ID-less error is invalid for this identifiable method failure. |
| P17 | MCP POST contains truncated JSON with unreadable ID and is rejected before message acceptance | HTTP `400` under CORE-014; an empty body is permitted. If the server includes a JSON-RPC error body, use parse error `-32700` without `id`; neither `id:null` nor a result is a valid proposed MCP error envelope. |
| P18 | Valid `notifications/initialized`, without ID | Accepted notification: HTTP `202`, empty body. It does not receive a JSON-RPC result. |
| P19 | Present, invalid Origin at M, first for an otherwise permitted anonymous request and then with valid bearer authentication | HTTP `403` in both cases: the proposed CORE-014 transport exception says nothing about authentication or data grants. The optional transport error body can omit ID even if the unprocessed body contains one. |
| P20 | GET M on a server without SSE; DELETE of a session whose server declines client termination | GET requires `405`. For DELETE, `405` is permitted, not required; do not fail the case solely for another response allowed by the selected profile. Any `405` includes `Allow` under RFC 9110. Neither SSE nor client-requested session deletion becomes mandatory. |
| P21 | Request after initialization with invalid/unsupported `MCP-Protocol-Version` | HTTP `400`. Optional session behavior and missing-version fallback follow the selected upstream transport. |
| P22 | Authorized direct SPARQL POST of `SELECT ?s WHERE { ?s ?p ?o }` | `200`, authorized query results. A server need not expose GET/form POST; their absence does not fail this selected profile. |
| P23 | SPARQL POST with `SERVICE` or an Update form | Rejected without executing it; this proposal leaves the specified rejection/error contract unchanged. |
| P24 | Permitted resource GET has a matching `If-None-Match` | `304` under RFC 9110; mutation authorization/not-found checks still precede preconditions as covered by the existing mutation cases. |
| P25 | Service Client Credentials request authenticates and reads authority; removal or withdrawal completes its sweep; the request then seeds a refresh family | The old issuance decision fails; no usable access token or refresh family survives. Removal that invalidates current client authentication gives `invalid_client`, with status/challenge under [RFC 6749 §5.2](https://www.rfc-editor.org/rfc/rfc6749.html#section-5.2); prior authentication success does not override the recheck. Authority-only withdrawal with client authentication still valid gives the proposed sempods `400 invalid_grant` for the invalidated issuance decision. A seed-then-recheck path invalidates its seed. Repeat with authority narrowing and with withdrawal between the final check and admission. |
| P26 | Service issuance takes effect first; service removal or revocation of the issued access/refresh credentials completes before the successful exchange response reaches the caller | The late response cannot revive those credentials: access-token use fails authentication (`401`), and refresh issues no credentials (`invalid_client` if current client authentication fails, otherwise `400 invalid_grant`). The revoked family stays unusable. Authority-only withdrawal is P31. |
| P27 | Removal and recreation of the same service identifier, or withdrawal and restoration of its permissions, complete while an old issuance decision is pending | The old pending decision and any unadmitted family remain invalid. A fresh authenticated Client Credentials request can return `200` under the new registration/authority. Revoked credentials never revive; the distinct case of already-issued credentials that remain valid is P31. |
| P28 | Authorized SELECT or ASK accepts only `application/sparql-results+xml` | `406` under SPARQL-015. The incorporated protocol's list of possible result formats does not add XML support to the selected sempods contract. |
| P29 | Authorized CONSTRUCT or DESCRIBE, first without a format preference, then accepting `application/n-quads`; repeat all query forms over empty data | Graph responses use JSON-LD by default and N-Quads when requested (SPARQL-016). Empty results retain a well-formed representation of the selected type (SPARQL-018); SELECT/ASK retain their JSON result document. Preserve SPARQL-018's nonempty-body constraint: for N-Quads an empty graph can use a comment-only document; JSON-LD uses an empty graph representation and SELECT/ASK use their result documents. |
| P30 | Direct query POST has an empty body; repeat with a nonempty malformed query | Both return `400` under SPARQL-017 and the protocol's failure rules, without executing a query. An authorized valid empty result remains a success as in P29. |
| P31 | Service issuance takes effect first; only its D write authority is withdrawn before the response arrives. Registration, access/refresh credentials and D read authority remain valid; repeat the former PUT and a permitted GET, then refresh | PUT returns `403` without mutation; GET still returns `200`. Valid retained refresh authorization can yield `200` and rotated credentials, but another PUT remains `403`. If refresh authorization is separately revoked, refresh gives `400 invalid_grant` instead. Explicit later write assignment can allow a write using still-valid credentials; renewal alone cannot restore rights. |
| P32 | Public browser client completes a valid cross-origin code/PKCE exchange | `200` readable by that browser through CORS; no shared client secret required. Test preflight where applicable. |
| P33 | Browser refresh family has a fixed expiry T; rotate before T, then present the latest token after T | Rotation cannot move expiry past T; after T, `400 invalid_grant`. An inactivity-expiry policy is the permitted alternative to a fixed maximum lifetime. |

D, independent A/B assertions, empty catalogues, computed views and lifecycle/media cases remain
in the existing proposals. This profile selection does not replace them or add general write-through,
registration-management, external-service discovery or a new module.

## Adoption impact and evidence

The table identifies requirement families; #70 audits the complete affected chapters rather than
copying #82. #71 aligns schemas with the same candidate. Correct the core authorize operation's
OAuth 2.1 summary with its profile. Add the token operation's
missing Basic-authentication `401`/challenge response and remove its blanket service-refresh ban.
Separate MCP request/notification/result/error and transport-error shapes; show optional SSE/session behavior
without requiring it; distinguish registration defaults, accepted values and failure alternatives.
A schema cannot by itself enforce request/response ID correlation or credential lifecycle.

Compatibility review covers the proposed OAuth baseline and S256 change, service refresh-family
origin, explicit OIDC redirect exception, dated MCP negotiation/transport and error-ID behavior.
The current weak schemas are not evidence that every admitted payload is conformant. Retain the
already adopted MCP resource/audience migration independently of these proposed changes.
The service credential cases also require existing client-secret rotation/removal semantics to be
examined: an old refresh token cannot bypass current client authentication, and removing the service
invalidates its grant. Secret rotation alone does not silently convert or widen a grant.
No requirement ID is allocated, moved or changed here; no OpenAPI or generated index is changed.

#72 needs executable positive and negative cases against the coordinated normative revision.
#77 retains the independent OpenAPI/validator repairs; a failing validator is not a standard.
#73 tracks implementation, index and semantic citation consequences with the existing downstream
issues. Repository/link/site checks establish document consistency only; this proposal supplies
no new client, HTTP, token-lifecycle, concurrency or Kotlin execution evidence.
