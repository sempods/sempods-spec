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
| OAuth 2.1 draft-13 overriding RFC 6749 | Revise: use RFC 6749 §§2–7 for selected code, service, refresh and token operations, RFC 7636 for PKCE, RFC 6750 §§2.1/3 for Bearer presentation/challenges, and the security scope below. Retain the implicit/password-grant prohibitions. Remove the unversioned OAuth 2.1 claim rather than adopt the draft wholesale. The observable choices are the grant types, client binding and protections; importing unrelated draft changes has no demonstrated need. | Auth profile, AUTH-001/018/023/027 and core profile overview. |
| Browser and native clients | Retain RFC 10017 for browser clients' selected authorization-code/token handling, not a required backend or browser architecture; RFC 8252 §7.3 supplies loopback redirects. Keep HTTPS/loopback and did:web origin/path constraints as explicit sempods choices. Private-use URI schemes are not added by this selection. | AUTH-003–009/018–023/055–057; MCP redirect references. |
| Dynamic registration | Retain RFC 7591 §§2–3, including defaults, actual registered metadata and error responses. The unauthenticated public profile stays separate from protected service registration in the [service-client recommendation](access-control.md#service-clients-and-registration-authority). Software statements, registration management and metadata fetching do not become required capabilities. | AUTH-008/009/011; registration OpenAPI under #77/#71. |
| Service refresh-token prohibition | Reject the candidate's unconditional ban; retain RFC 6749 §4.4.3's recommendation against issuance. An exception needs the bounded credential behavior below. This deliberately generalizes the current code-seeded family rule rather than silently treating service refresh as already specified. | AUTH-017/027/031–034/063; TokenResponse. Never reuse current AUTH-064 for this candidate. |
| OAuth `prompt` | Retain OpenID Connect Core 1.0 errata set 2 §3.1.2.1 only for the parameter selected by AUTH-039–041. This does not make the pod OAuth surface an OIDC provider. | Auth profile; no new `openid` scope or ID Token. |
| OIDC bridge and redirect exception | Select OIDC Core and Discovery 1.0, both errata set 2, for the code flow, ID Token issuance/validation and provider metadata in OIDC-002–010. Retain the registration-free origin rule as an explicit deviation from pre-registered exact redirect matching, with exact code-to-redirect binding at token exchange. Neither implicit/hybrid flows nor WebFinger discovery become mandatory. | OIDC profile and OIDC-010; core AUTH-004/005/007 redirect exception. |
| MCP revision, lifecycle and messages | Select MCP 2025-11-25 basic messages, initialization/version/capability negotiation and the server operations selected by the module. Keep JSON-RPC 2.0 as the base with the explicit MCP error-ID distinction below. Extra client features and transports are not required. Existing empty resource/prompt lists and anonymous public access remain sempods choices. | MCP profile, MCP-001–005; message schemas. |
| MCP Streamable HTTP | Select that revision's Streamable HTTP behavior at the existing endpoint. A server may use JSON responses with GET returning 405, without persistent sessions or SSE. If it offers streams or sessions, their conditional rules apply. POST notifications use 202; version and Origin validation apply. This adds observable transport obligations beyond the current explicit POST surface and needs normative adoption. | MCP-001/002/004/007/009; GET/DELETE and header/response views under #71. |
| MCP authorization exclusion | Reject the candidate's blanket exclusion: #111 already selects discovery, resource and token portions of MCP 2025-11-25 authorization. Preserve that bounded selection; neither its whole OAuth draft nor Client ID Metadata Documents is imported. | MCP-033–038 and current profile; no rollback of #111. |
| RDF named-graph model | Retain RDF 1.1 Concepts, Recommendation 2014-02-25, §§3–4. RDF supplies graphs/datasets, not storage partitions, grants, the contents of D or exclusive statement membership. Those choices are owned by the [data-access proposal](data-access.md). | Context/grant profile introductions; CTX-001 and related impact map. |
| OAuth scope definition | Retain RFC 6749 §3.3 for feature-scope syntax/semantics; it does not define the server's data-grant representation. | Grants profile and GRANT-001–003. |
| CRUD and media representations/validators | Retain RFC 7396, RFC 4648 §5 and JSON-LD 1.1 Recommendation 2020-07-16 within selected operations and existing canonical-shape deviations. Use RFC 9110 §§8.8/13 and [§9.3.4](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.4) for validator fields, preconditions and the prohibition on PUT response validators after transformation instead of the superseded RFC 7232 reference. Keep Linked Data principles informative. Optional edit links already use RFC 8288 §3/RFC 5023 §16.4 through CRUD-058. | Core overview, CRUD/media introductions and CRUD-030's citation correction from §10.2.3 (Retry-After) to §9.3.4 (PUT); no full JSON-LD expansion requirement. |
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

## Service credentials and registration metadata

[RFC 6749 §4.4.3](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4.3) discourages service
refresh tokens; it does not prohibit them. The normal service obtains another access token using
its client credentials. No interoperability case identified here requires strengthening that
recommendation to an unconditional ban.

The proposed exception preserves the service subject/class, current service authority, client
binding, rotation/reuse revocation and resource binding where MCP applies. A confidential service
authenticates when refreshing under RFC 6749 §6. Refresh cannot express a person or grant public-read
or OIDC scopes. Service removal or withdrawn authority cannot be bypassed with an older credential.
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

For a seed-then-recheck implementation, creation rechecks the same live registration instance,
client-authentication validity, current assigned authority and credential-revocation state **after**
seeding. A failed check invalidates that unadmitted family and its access credentials. The final
check and admission also need a transaction, conditional generation binding or equivalent
coordination: a sweep between them cannot leave credentials valid against an obsolete decision.
Other designs may enforce the same ordering without seeding first. This is an implementation path,
not a required storage algorithm; checking code consent cannot protect a service exchange with no code.

For registration, [RFC 7591 §§2 and 2.1](https://www.rfc-editor.org/rfc/rfc7591.html#section-2.1)
defines defaults and the relationship between grant and response types. A missing `grant_types`
means `authorization_code`; a missing `response_types` means `code`. The standard advises servers
to prevent inconsistent combinations. It does not impose a universal rule that every supplied
`grant_types` array contain `authorization_code`.

Reject that proposed blanket schema restriction. A `refresh_token`-only request with omitted
`response_types` has an inconsistent default, so the recommended public registration behavior is
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
keeps the request's ID; an uncorrelatable MCP error omits it. This rejects the review's universal
nullable-ID correction and avoids silently claiming that these two profiles agree.

[Streamable HTTP](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
also permits an optional ID-less error body for rejected input or invalid Origin. Model that
transport rejection separately from a response to an identifiable method call. Omission is not
permission to drop the ID from an ordinary method error. #77 owns schema/tests; adopting the dated
message profile and this explicit distinction belongs to #70/#71. Keep MCP-004's bearer error code
and the adopted MCP-009 challenge. Preserve the upstream obligation levels: invalid Origin requires
`403`, while session DELETE permits `405`; transport error bodies remain optional.

## Proposed request and response cases

These cases are acceptance inputs, not executed HTTP or conformance evidence. Each starts with
otherwise valid input, correct authority and an independent state unless stated otherwise.
`P=https://example.org/alice`, `M=P/_system/mcp`; OAuth routes use `P/_system/auth/`.

| Case | Request or input | Expected outcome under the recommendation |
|---|---|---|
| P01 | Valid service `POST token`, `grant_type=client_credentials`, no scope | `200` service access token; normally no refresh token. Another authenticated Client Credentials request remains usable without refresh. |
| P02 | Same exchange under a justified service-refresh policy; then authenticated refresh by that service | `200`; optional refresh issuance, then rotation, service subject/class and unchanged authority ceiling. No person/public-read/OIDC authority appears. |
| P03 | A different authenticated service presents P02's refresh token | `400 invalid_grant`; no replacement credentials. Invalid client authentication instead follows the token endpoint's client-authentication error. |
| P04 | Service disabled, then its old refresh token presented with no valid client authentication | Client authentication fails; no token. If client authentication remains valid but the refresh authorization was revoked, `400 invalid_grant`; withdrawing data rights alone is the separate P31 case. |
| P05 | Service requests `scope=public-read` on Client Credentials | `400 invalid_scope`; refresh support does not relax AUTH-032. |
| P06 | Service refresh token is reused after rotation | `400 invalid_grant` and family revocation; a concurrent exchange cannot preserve withdrawn authority. |
| P07 | Public registration with `redirect_uris`, method `none`, grant/response types omitted | `201` if accepted; defaults are code flow. Return actual registered metadata; no service credentials or promise of refresh issuance. |
| P08 | Public registration with `grant_types:["refresh_token"]`, response types omitted | Recommended `400 invalid_client_metadata`, or `201` with explicitly normalized consistent code-flow metadata. Never return the contradictory defaults as accepted metadata. |
| P09 | Same grant list with explicit `response_types:[]` | If unsupported, `400 invalid_client_metadata`; if accepted, `201` with those actual values. No code-flow entitlement or refresh credential is created by registration. |
| P10 | Public registration requests `client_credentials` | Reject or normalize to supported public metadata; never advertise or issue service authority. |
| P11 | did:web app requests code without S256 PKCE | Proposed rejection under the authorization recommendation; no code. Current AUTH-023 must change explicitly before this becomes binding. |
| P12 | `did:web:app.example:notes` with `https://app.example/notes/cb` versus `/notes-other/cb` | First can authorize with S256 and consent; second is refused without redirecting to the rejected URI. Same host alone is insufficient. |
| P13 | Native client registered `http://127.0.0.1:49152/cb` requests port 49153; path stays `/cb` | The loopback URI matches despite the changed port; a changed path or non-loopback host does not receive that exception. |
| P14 | OIDC pod client uses its permitted origin for code callback; token exchange changes that original callback URI | Authorization can succeed without preregistration; exchange fails with `invalid_grant` under OIDC Core §3.1.3.2. The origin exception does not extend to code redemption. |
| P15 | Valid MCP `initialize` proposes `2025-11-25` | Negotiates that supported revision and capabilities. This module does not require support for every earlier or future revision. |
| P16 | MCP call with `id:7` names an unknown method | JSON-RPC error `-32601`, `id:7`; no result. An ID-less error is invalid for this identifiable method failure. |
| P17 | MCP POST contains truncated JSON with unreadable ID and is rejected before message acceptance | HTTP error; an empty body is permitted. If the server includes a JSON-RPC error body, use parse error `-32700` without `id`; neither `id:null` nor a result is a valid proposed MCP error envelope. |
| P18 | Valid `notifications/initialized`, without ID | Accepted notification: HTTP `202`, empty body. It does not receive a JSON-RPC result. |
| P19 | Present, invalid Origin at M | HTTP `403`, required by the selected transport's security rule; the optional transport error body can omit ID even if the unprocessed body contains one. |
| P20 | GET M on a server without SSE; DELETE of a session whose server declines client termination | GET requires `405`. For DELETE, `405` is permitted, not required; do not fail the case solely for another response allowed by the selected profile. Any `405` includes `Allow` under RFC 9110. Neither SSE nor client-requested session deletion becomes mandatory. |
| P21 | Request after initialization with invalid/unsupported `MCP-Protocol-Version` | HTTP `400`. Optional session behavior and missing-version fallback follow the selected upstream transport. |
| P22 | Authorized direct SPARQL POST of `SELECT ?s WHERE { ?s ?p ?o }` | `200`, authorized query results. A server need not expose GET/form POST; their absence does not fail this selected profile. |
| P23 | SPARQL POST with `SERVICE` or an Update form | Rejected without executing it; this proposal leaves the specified rejection/error contract unchanged. |
| P24 | Permitted resource GET has a matching `If-None-Match` | `304` under RFC 9110; mutation authorization/not-found checks still precede preconditions as covered by the existing mutation cases. |
| P25 | Service Client Credentials request authenticates and reads authority; removal or withdrawal completes its sweep; the request then seeds a refresh family | The old issuance decision fails; no usable access token or refresh family survives. Removal that invalidates current client authentication gives `invalid_client`, with status/challenge under [RFC 6749 §5.2](https://www.rfc-editor.org/rfc/rfc6749.html#section-5.2); prior authentication success does not override the recheck. Authority-only withdrawal with client authentication still valid gives `400 invalid_grant` for the invalidated issuance decision. A seed-then-recheck path invalidates its seed. Repeat with authority narrowing and with withdrawal between the final check and admission. |
| P26 | Service issuance takes effect first; service removal or revocation of the issued access/refresh credentials completes before the successful exchange response reaches the caller | The late response cannot revive those credentials: access-token use fails authentication (`401`), and refresh issues no credentials (`invalid_client` if current client authentication fails, otherwise `400 invalid_grant`). The revoked family stays unusable. Authority-only withdrawal is P31. |
| P27 | Removal and recreation of the same service identifier, or withdrawal and restoration of its permissions, complete while an old issuance decision is pending | The old pending decision and any unadmitted family remain invalid. A fresh authenticated Client Credentials request can return `200` under the new registration/authority. Revoked credentials never revive; the distinct case of already-issued credentials that remain valid is P31. |
| P28 | Authorized SELECT or ASK accepts only `application/sparql-results+xml` | `406` under SPARQL-015. The incorporated protocol's list of possible result formats does not add XML support to the selected sempods contract. |
| P29 | Authorized CONSTRUCT or DESCRIBE, first without a format preference, then accepting `application/n-quads`; repeat all query forms over empty data | Graph responses use JSON-LD by default and N-Quads when requested (SPARQL-016). Empty results retain a well-formed representation of the selected type (SPARQL-018); SELECT/ASK retain their JSON result document. Preserve SPARQL-018's nonempty-body constraint: for N-Quads an empty graph can use a comment-only document; JSON-LD uses an empty graph representation and SELECT/ASK use their result documents. |
| P30 | Direct query POST has an empty body; repeat with a nonempty malformed query | Both return `400` under SPARQL-017 and the protocol's failure rules, without executing a query. An authorized valid empty result remains a success as in P29. |
| P31 | Service issuance takes effect first; only its D write authority is withdrawn before the response arrives. Registration, access/refresh credentials and D read authority remain valid; repeat the former PUT and a permitted GET, then refresh | PUT returns `403` without mutation; GET still returns `200`. Valid retained refresh authorization can yield `200` and rotated credentials, but another PUT remains `403`. If refresh authorization is separately revoked, refresh gives `400 invalid_grant` instead. Explicit later write assignment can allow a write using still-valid credentials; renewal alone cannot restore rights. |

D, independent A/B assertions, empty catalogues, computed views and lifecycle/media cases remain
in the existing proposals. This profile selection does not replace them or add general write-through,
registration-management, external-service discovery or a new module.

## Adoption impact and evidence

The table identifies requirement families; #70 audits the complete affected chapters rather than
copying #82. #71 aligns schemas with the same candidate. Correct the core authorize operation's OAuth 2.1 summary with its profile. In particular, separate MCP
request/notification/result/error and transport-error shapes; show optional SSE/session behavior
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
