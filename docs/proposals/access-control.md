# Access control

Status: **Partly adopted; remaining design is proposed and non-normative.**
The conditional `state` echo is specified by [SPS-AUTH-025](../../spec/core/auth.md#SPS-AUTH-025)
under [#10](https://github.com/sempods/sempods-spec/issues/10), with normative adoption in
[PR #105](https://github.com/sempods/sempods-spec/pull/105).
The equivalent-identity claim is specified by [SPS-OIDC-005](../../spec/modules/oidc.md#SPS-OIDC-005)
and [SPS-OIDC-016](../../spec/modules/oidc.md#SPS-OIDC-016)–[018](../../spec/modules/oidc.md#SPS-OIDC-018) under
[#5](https://github.com/sempods/sempods-spec/issues/5), with normative adoption in
[PR #107](https://github.com/sempods/sempods-spec/pull/107).
Owning issue and adoption: [#68](https://github.com/sempods/sempods-spec/issues/68).
The design was introduced by [#52](https://github.com/sempods/sempods-spec/pull/52); its merge did
not adopt it. [#69](https://github.com/sempods/sempods-spec/issues/69) owns unresolved contract
choices, [#70](https://github.com/sempods/sempods-spec/issues/70) their normative preparation, and
[#72](https://github.com/sempods/sempods-spec/issues/72) validation against that candidate.

## Purpose

This is the authorization part of the [authorized data access proposal](data-access.md). It proposes
observable guarantees for reads, writes, queries and delegation while leaving policy mechanisms to
implementations, following [the vision](../vision.md#what-belongs-in-the-contract). Data access owns
the core/module split and requirement impact; this document develops the operation boundaries.

## The current model

The [specified boundary](data-access.md#the-specified-boundary) remains Context-based. The
[grants chapter](../../spec/core/grants.md) also defines the owner's implicit authority and bounds
an application's delegation by the person's effective permissions.

The [worked ACP scenarios](../../examples/README.md) illustrate one possible design. Their
[fixture guide](../guides/acp-fixtures.md) separates supplied assumptions from specified behavior.
The [ACP implementation proposal](authorization-implementation/README.md) retains design choices
awaiting disposition under #64; it describes no verified implementation.

## Policy-independent enforcement

A request's authority follows from the verified caller and client, the requested operation, the
applicable delegation and the pod's current policy. Core discovery and selection do not prescribe
Context-based authorization, role hierarchies, policy storage or one evaluator. An implementation
can combine area and document conditions, use resource policies alone, or have a small fixed permission model.

Where a deployment uses two independent restrictions, both constrain the operation. For example,
area access and a document policy can compose by intersection. This is one implementation's design,
not an obligation to give every pod two policy layers. Internal use of ACP or of document-level
conditions requires no feature declaration. A module declaration is needed for an additional
client-facing contract, such as Context creation/deletion or interoperable policy management.

An implementation's own administrative UI can manage policies without a core policy API. Reading
policy syntax, evaluating a request and editing permissions are separate capabilities. A generic
client need not understand private attributes or reproduce the server's evaluator. Neither the
ability to read a resource nor possession of an access token grants policy-management authority.

### Authorization without Context setup

A notes app asks Alice for permission to read, create and edit notes in her pod. Alice approves
the data and operations it may use. The app can then create a note, even in an empty pod, without
choosing or creating a Context. This section proposes that consent flow, its delegation limits, public reads and withdrawal
of access. It complements the [default-access cases](data-access.md#four-default-access-decisions);
D is the implicit data scope used by ordinary requests.

The app starts authorization without Context grant strings or a new data-scope parameter. The pod
authenticates Alice and asks for approval. Alice need not own the pod or install the app, but she can
approve only access she may delegate. The app then uses its Bearer token on the ordinary routes;
no Context registry request is needed.

Keep the [existing client roles, pod-local routes and token format](../../spec/core/auth.md).
For both `did:web:` and `dyn:` apps, recommend Authorization Code with S256 PKCE. This changes
AUTH-023: validating a `did:web:` redirect does not protect an intercepted authorization code.
Its local origin/path validation still applies; it proves neither Alice's identity nor her consent.
Each client identity needs its own permission, even if one app switches between these client types.

A service uses Client Credentials and explicitly assigned service authority. It acts as itself,
with no person represented by its token. Service `public-read` and OIDC scopes remain prohibited;
a service can separately read public data without credentials. The
[service-client recommendation](#service-clients-and-registration-authority) separates that
authority from the mechanism used to provision it.

Approval binds Alice, the pod, client, redirect and allowed access to one authorization transaction.
It can be accepted only once. Cancellation, replay or swapping transactions cannot create or restore
permission. A browser login alone is not approval. Existing `prompt` rules and interactive `dyn:`
confirmation remain; implementations choose the UI, policy language and consent storage.

Keep the [current state-echo contract](../../spec/core/auth.md#SPS-AUTH-025). The proposed RFC 9700
profile protects against CSRF and multi-issuer mix-up, including when clients omit `state`.

Each request checks the person and client separately. Identity assertions and browser sessions keep
their pod/audience restrictions and cannot replace a pod API token. A person's external identifier
is their WebID URI. Two identifiers count as the same person only through a trusted identity
relationship; `owl:sameAs` data, matching email addresses and caller-supplied aliases do not suffice.
Consent changes, withdrawal and forced reauthorization cover that person's trusted aliases for the
affected pod/client. Keep that coverage while leaving the lookup placement open (AUTH-052).
These cases assume a trusted mapping. The OIDC wire claim follows
[SPS-OIDC-005](../../spec/modules/oidc.md#SPS-OIDC-005); changing AUTH-052's prescribed lookup
placement remains proposed here.

### Service clients and registration authority

This is a non-normative recommendation under [#69](https://github.com/sempods/sempods-spec/issues/69),
against merged revision `99bac2095e1d11f5625fed0d3f927ed741877824`. It incorporates the corrected
service-registration input from [Kotlin #124](https://github.com/sempods/sempods-kotlin/issues/124).
AUTH-008/011/012/013 still bind until coordinated adoption; an implementation of this proposal
does not thereby conform to those current requirements.

For example, Alice authorizes an installer to create a backup service for her pod. The installer
does not thereby gain access to Alice's data or permission to rotate another service's secret.
Alice can approve the backup's read access separately, or an authorized provisioning operation can
assign it at creation. The backup subsequently authenticates and reads under its own identity.
The common contract needs those authority boundaries, not a required installer or consent sequence.

Use [RFC 7591 §§2, 3.1 and 3.2](https://www.rfc-editor.org/rfc/rfc7591.html#section-3) for dynamic
registration metadata and messages, and [RFC 6749 §4.4](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4)
for confidential clients using Client Credentials. RFC 7591 distinguishes open registration from
registration protected by an initial access token; it leaves that token's issuance and validation
policy to the deployment. A presented token or a requested grant type alone proves no service
creation authority. The proposed sempods boundary is:

- Keep the existing unauthenticated registration profile at `POST {pod}/_system/auth/register`:
  public `dyn:` clients, `token_endpoint_auth_method=none`, and no service credentials or
  `client_credentials` in accepted metadata. Registration grants no data access; user-facing
  authorization, PKCE and consent rules still apply.
- Scope AUTH-008's prefix and AUTH-011's registration-response restriction to that profile,
  including when an implementation also offers protected registration at the same route. Keep
  `dyn:` as the public-client class; a protected service registration uses a separate identity.
  Changing the spelling alone is insufficient: both profile restrictions need revision, and
  service eligibility is validated server-side rather than inferred from a caller-chosen prefix.
- Creating a service client requires explicit authority for that operation in the target pod.
  Assigning or widening its access, rotating its secret and managing an existing registration
  each require authority covering the operation and target. Approval to create a new service
  cannot be spent on an unrelated existing service. Ordinary data access, an owner-valued `sub`,
  or a service's own credentials supply none of this administrative authority by themselves.
  Assignment authority also bounds the data and operations being granted; permission to create
  a client alone supplies no assignment authority.
- Permit operator provisioning, owner-authorized installation and embedded configuration.
  A service's effective data authority can be assigned or changed after registration under the
  same authorization boundary. Neither immutable registration-time grants nor Context-shaped
  grants belong in core. Keep the service subject/class distinction and the exclusions of
  `public-read` and OIDC scopes; ordinary D access grants no Context or pod administration.

Owner installation is visible to an installer, but a portable installer protocol is not part of
the promised common contract. No protected-registration route, scope literal, management API,
credential lifetime, number of consent screens or new module is selected here. If a common
installer contract is later needed, define a discoverable optional profile. Supporting Client
Credentials remains required by AUTH-002/027 in this iteration; whether that capability should
be optional is a separate decision. The [protocol-profile recommendation](protocol-profiles.md#service-credentials-and-registration-metadata)
rejects a blanket service refresh-token ban and records the required family-contract change.

#### Service-client cases for review

These proposed acceptance cases are not executed HTTP tests. Repeat the data cases on a single-graph
pod and a Context-backed pod with equivalent authority. Use fresh independent setups, pod P,
ordinary data scope D, and service S; administrative operations use the implementation's own
surface. Their wire format and status are not standardized by this proposal.

| Setup and request | Proposed response or effect |
|---|---|
| Valid unauthenticated registration for Authorization Code at P | RFC 7591 `201`, `dyn:` identity and public-client metadata; no service secret, service eligibility or private data access. |
| Same profile requests `client_credentials` or a service authentication method | Reject the metadata or return the supported public-client metadata under RFC 7591 §3.2.1. Neither outcome creates service credentials or advertises `client_credentials`. |
| That public client calls the token endpoint with `grant_type=client_credentials` | OAuth error under RFC 6749 §5.2, no access token. Supplying a service-looking identifier cannot change the client's class. |
| A valid data token naming P's owner requests service creation or grant assignment | Denied without the separate operation authority; no service credential or permission change. Owner identity does not turn app data consent into installation consent. |
| P explicitly authorizes creation of S through a protected registration extension at the same route | Registration can succeed with a separate service identity and the accepted confidential-client metadata. The unauthenticated profile remains unchanged. |
| An installer authorized to create S attempts to rotate existing T's secret, assign T access, or create a service in pod Q | Denied unless its authority independently covers that operation and target; T and Q are unchanged. |
| An assignment authorization covers S reading D; the caller attempts to give S write access or access to independent A | Denied without separate covering authority; S's permissions are unchanged. The assignment cannot exceed its approved data and operation boundary. |
| S is registered without data authority; an authorized administrator later assigns D read access | Registration alone enables no private read. After assignment, S can authenticate and read approved D data without changing its identity or creating a Context. |
| S has approved D write authority on an empty pod; Client Credentials exchange, then nonempty LOD resource PUT | Token response `200`, service subject S; PUT `201` with the ordinary resource Location. No Context registry setup is required. |
| S has only D read authority; authenticated resource PUT | `403`, no mutation. Registration and client authentication do not imply write or administrative authority. |
| S's data authority is withdrawn while its access token remains otherwise valid; repeat the previously permitted write | `403` after withdrawal, with no mutation. If the credential itself was revoked, authentication instead fails with `401`; token renewal cannot restore withdrawn authority. |
| S exchanges Client Credentials with `scope=public-read` or an OIDC scope | `invalid_scope` under the retained AUTH-032 rule; no person or public-read authority is introduced. |

An implementation can realize this with its existing permission store or another policy model.
The proposed boundary does not require storing grants in tokens, an installer-token format or a
specific revocation algorithm. [Kotlin #35](https://github.com/sempods/sempods-kotlin/issues/35)
already owns an implementation-specific installation design and its delivery issues; its scope,
two-consent flow and credential-lifecycle choices are not adopted here.

### Delegation and revocation

For a non-public operation, check three limits: what the person may currently delegate, what the
app still has consent to do, and what the pod's current policy permits for the complete operation.
All three must allow it. For example, Alice's permission to edit a note does not let an app edit it
if she approved only reading. For a service, its explicitly assigned authority replaces the first two
limits. Feature scopes and a valid token do not grant extra access. Public reads follow the rules
below. Tokens identify their client and subject; core introduces no Context-grant list or client-side
policy evaluation.

Consent describes both the allowed effects and the data selection's behavior over time:

| Consent shape | Proposed ceiling |
|---|---|
| Fixed selection, such as two chosen resource IRIs | Only those resources and approved operations. Later sharing of another document adds no application authority. |
| A bounded dynamic data space, such as D or the tasks in project X | Future resources matching the agreed boundary may be included where the person may delegate that boundary. The approval makes this future-membership effect explicit. Creation can be allowed before any resource exists. |

These are descriptions of authority, not required UI controls, policy syntax or new OAuth scope
strings. An implementation can offer either shape or both; it still supports ordinary authorized
creation without Context setup. The dynamic case needs authority over the described space, rather
than an inference from the few documents currently visible. A person permitted to share only two
documents cannot authorize all of D. A newly created task inside an approved project is data growth
within the ceiling; adding another project or granting additional modes is a ceiling expansion
requiring fresh consent. An unspecified "whatever this person can access later" is not a substitute
for the described boundary. This resolves the ambiguity illustrated by the
[delegation fixture](../../examples/50-delegation.md) without requiring a photo-picker or ACP.

Narrowing the person's authority also narrows dependent delegations. Removed authority stays removed
from the old delegation if the person's permissions later grow again; fresh consent is needed to
restore it. Client X's consent never grants client Y access, even for the same person or alias.
Changing data membership under an agreed dynamic selection differs from removing/reinstating the
person's permission or broadening the selection rule. A stored grant representation is not required,
but losing track of that distinction cannot be repaired by silently broadening a client's access.

A completed withdrawal takes effect on the next request, including requests using unexpired tokens.
Narrowing a delegation need not invalidate its token: reads lose the withdrawn private assertions
and refused writes give `403`. Disconnecting the connection or requiring fresh authorization ends
its previous codes, refresh credentials and API tokens; presenting such a token gives `401` rather
than silently becoming anonymous. Reconnecting creates a new authorization basis; it cannot make
old credentials usable again. An independently obtained public-only credential is separate.

#### Request selection and delegation

A Context selector addresses data for one request; it creates no delegation ceiling. A client
holding broad D authority can omit a selector later and still use that authority. A client with a
bounded C delegation cannot escape it by omitting C, selecting E, or using SPARQL. Those requests
are evaluated inside their addressed scope and the same delegation ceiling. Ordinary access does
not widen D to reach C's sources outside it, and C's authority alone does not authorize D mutations.

For a CMS-derived space, distinguish a source-data membership change inside an approved dynamic
boundary from a change to authority or to the boundary itself. New matching data can enter the
projection; removal of the person's space membership narrows dependent delegations. Reinstating
that membership does not restore revoked app authority without fresh consent. Redefining C to
include an additional space is a ceiling expansion even when its IRI is unchanged. Naming C in a
request or consent record cannot stand in for recording the agreed boundary's meaning.

These proposed cases assume valid credentials, ordinary response preconditions and independent
public access disabled, so public-read cannot mask private authority failures. C is a view of D;
R is in C and private S is in D outside C. Unless stated otherwise, the client has read authority
bounded to C and no mutation authority. The credential itself remains valid when data authority
is narrowed; a terminated connection instead follows the `401` rule above.

| Request or transition | Proposed observation |
|---|---|
| GET R with C, ordinary GET R, find and SPARQL with or without C | Each sees only its addressed data within the same C-bound authority. Omission does not reveal S, including through find expansion or query paths. |
| Ordinary GET S or E-selected GET S; E would expose S to the person outside this app's consent | `404`; neither selecting E nor omitting selection supplies app authority. |
| Ordinary or C-selected mutation using the read-only delegation | `403` with no data change; a selector cannot grant a mode. |
| Different client has broad D read authority and requests C, then omits the selector | First request selects C; the ordinary request may also see S. This is filtering under existing authority, not a persistent downscope. |
| An explicitly approved dynamic C gains a matching task through an independently authorized source write | The next authorized C projection can include that task; a fixed-resource consent remains limited to its original IRIs. |
| Person loses C authority, then regains CMS membership | The next request loses the withdrawn private projection; restoring membership alone does not restore the old app delegation. Fresh consent can establish new authority. |
| CMS changes C's definition to include another space | Existing consent does not expand to the additional space. If its old boundary cannot be enforced, suspend its dependent authority pending fresh consent. |
| C disappears and is recreated at the same IRI | No revival of old C-bound authority; apply the [external-space rule](context-contract.md#externally-changing-spaces). |

#### Consent and credential races

Recommend replacing GRANT-018/AUTH-063's prescribed write/check order with this outcome: concurrent
consent, code/refresh exchange and withdrawal have an order consistent with completed operations.
If withdrawal or required reauthorization completes before an old exchange is admitted, exchange
fails with OAuth `invalid_grant` (`400`). If an exchange takes effect first, its credentials are
covered by the later withdrawal even when its HTTP response arrives afterwards. No credential from
the withdrawn authorization can authorize a subsequent request or seed a surviving refresh family.
Apply this to session-only access tokens as well as refresh-token families. Retain rotation and
family revocation on refresh-token reuse; no guaranteed refresh-token issuance is restored.

A changed consent decision invalidates its outstanding codes (AUTH-062), including changes under a
trusted equivalent identity. A forced-reauthorization challenge is itself a barrier even if the
person has not answered yet. For #49, acknowledge the MCP replay only when its authorization comes
from a fresh consent transaction completed after that barrier for the same person, pod and client;
that transaction is bound to the pending challenge. A newly minted token from an older code or a
refresh exchange is insufficient. This comparison concerns the authorization transaction, not
clock precision, token `iat` or a new public claim. Existing one-time challenge consumption and
expiry remain. A second barrier invalidates an unfinished transaction tied to the first.

Locks, serializable transactions, conditional generation checks or another design can enforce this
outcome. For example, an exchange conditionally tied to a live authorization generation can lose to
a generation change; if it wins, credentials tied to that old generation cease to authorize after
the change. A design spanning stores must close the check/commit race as well. Merely checking a
flag before minting, waiting for JWT expiry, or sweeping only refresh families fails the cases.
This illustrates an implementation path, not an algorithm required by core.

### Public access and `public-read`

Recommend retaining `public-read` as an additive feature scope for valid non-service API tokens.
It permits reading the currently public projection of the requested data scope. Without a token,
that public projection is also readable. With a valid token lacking `public-read`, only the
caller's independently authorized projection is exposed. A rejected credential always fails;
it is never retried as anonymous. Public read permission grants no writes or administrative rights.

Public policy is evaluated for each request. For ordinary reads it contributes only data in D;
explicit named/Context selection still bounds the operation. A public Context outside D does not
silently enlarge the default graph. Direct reads, query results and find use the same resulting
scope and the proposal's non-disclosure/cache guarantees.

Keep authorization requests for `scope=public-read` with or without a person. Without a person,
use the existing per-request opaque anonymous subject and bind the code/token to the requesting
client; this subject grants no private identity or delegation. Validate client, redirect and PKCE
normally. An invalid presented identity assertion gives `access_denied`, not anonymous success.
An interactive public-only approval can confirm that feature without identifying a person; it
creates no private delegation. The existing prompt rules still apply, including `prompt=none`
refusal without the required remembered identity/consent. For an otherwise valid request, issue
the public-read access token even when no data is currently public. Replace AUTH-044 and the
public-existence branch of GRANT-014 accordingly: the feature can be authorized independently of today's data, without querying or exposing a Context registry.
An ordinary private-delegation request with no surviving authority and no approved public-read
scope still receives `consent_required`; explicit refusal remains `access_denied`.

Removing private authority does not remove `public-read` from a token that remains valid. Removing
a public policy removes its read contribution immediately; any separate private authority still
applies. Token expiry, explicit credential revocation and a connection disconnect are credential
failures and give `401`, including on public read routes. An anonymous public-only credential has
no private authority to restore. Refresh availability remains the existing separate choice: this
recommendation neither requires nor prohibits issuing refresh tokens to that class.

Retaining the scope preserves the difference between existing authenticated clients with and
without it. At adoption, translate existing Context delegations only where an equivalent bounded
authority can be established. A grant on independent A cannot become permission on D. If an old
credential's subject/client, scope, consent boundary or revocation lineage cannot be preserved,
reject it and require fresh authorization; never treat it as anonymous or broad D access. This is
a fail-closed credential transition, not a general protocol-version negotiation mechanism (#21).
The current no-public-Context issuance refusal remains binding until normative adoption.

### Authorization request cases

These are proposed acceptance cases for #72, not executed HTTP or race tests. Use a pod P without
management or exposed Contexts, empty implicit D, person U and clients X/Y. U can delegate read and
complete resource creation/replacement in D unless a row narrows it. Valid test requests use the
existing media types, a validated redirect and fresh S256 PKCE; table rows reset state. The
independent-A case configures P to expose A through core Context discovery and selection, without
management. MCP challenge cases add MCP. Installation of policy and the consent UI are
implementation-specific; public protocol requests and observations are shared.

| Setup and request | Proposed result |
|---|---|
| X obtains U's approval for D read/write through Authorization Code, without a Context scope or registry call; exchanges the code, then PUTs nonempty RDF at a new LOD R | Code exchange `200`; PUT `201`, Location R; GET `200`. No Context identity, membership grant or ownership is required. Repeat with a non-owner who may delegate the same authority. |
| X repeats authorization using its registered `dyn:` identity or its origin-bound `did:web:` identity | The respective existing client validation/consent rules apply; both use S256 PKCE and reach the same approved ordinary operations. |
| A public client omits PKCE, or redeems a code with the wrong verifier | Missing challenge is refused at authorization (`invalid_request`); wrong verifier gives token endpoint `400 invalid_grant`. The failed step issues no access token and cannot enlarge legitimate consent. |
| X supplies `state=s` versus omitting it in otherwise protected/valid authorization transactions | Keep the current state-echo contract for success and error redirects; the proposed client profile also checks transaction and issuer binding. |
| U refuses consent, or an earlier consent submission is replayed after narrowing | Explicit refusal returns `access_denied`; replay is rejected without restoring the earlier permission. Neither case issues a code for that old authority. |
| Y has a valid token naming U, but no private delegation; X's consent allows R | Y's private resource GET is `404`, its valid write `403`, regardless of X's authority. No subject-only grant lookup. |
| P exposes independent A through core; U has consented only to A; X attempts an ordinary write to D | `403`, no fallback, new Context or write into A. A default mapping creates no authority. |
| Service S is provisioned with D read/write; uses Client Credentials and then ordinary PUT | Token response `200`; allowed nonempty creation `201`. Subject is S and no person/Context setup is fabricated. A `dyn:` client cannot obtain this service authority. |
| U approves a fixed selection containing R; later gains access to unrelated private R2 | X's R2 GET remains `404`, write `403`; fresh consent is required. |
| U can delegate the project-X data space and approves its dynamic read selection; a new task joins that project | X can read that task. A task in project Y remains hidden; changing the agreed selection to include Y requires fresh consent. |
| U loses permission to R, then regains it, without fresh application consent | X loses the delegated R access at the first change and does not regain it at the second, even with an unexpired token. Independent public access is tested separately. |
| Two configured trusted URIs identify U; withdrawal arrives under the other URI | X loses the same authority and affected credentials across both aliases. A claim from an untrusted issuer or ordinary `owl:sameAs` data cannot gain or revoke another person's authority. |

The following cases isolate public-read behavior. R is inside D; successful resource reads have
visible outgoing statements. Use empty or unrelated public data in the zero-data cases so status
codes do not depend on undisclosed resources.

| Setup and request | Proposed result |
|---|---|
| R is public; GET without a credential | `200`. R private/absent instead gives the same `404`; find/query have their ordinary authorized-empty results. |
| R is public; valid token has no private R authority, with versus without `public-read` | GET `200` with the scope, `404` without it. The public branch does not add write authority. |
| No public data or registered Contexts; valid anonymous `scope=public-read` authorization and code exchange | Public-read code/token flow succeeds; token endpoint `200`. Resource reads are `404`, find/query use the empty projection. No registry-existence prerequisite or mandatory refresh token. |
| A public-only token exists; R becomes public and then private | GET changes from `404` to `200` to `404` without reissuing the token. |
| Private R authority is withdrawn but R is public and the token remains valid with `public-read` | GET remains `200` through the public branch; the removed private write gives `403`. |
| R is public; expired, wrong-pod or explicitly revoked Bearer token | `401` with a Bearer challenge; no anonymous fallback. The same R remains readable by a separate credential-free request. |
| Anonymous public-read authorization carries an invalid identity assertion | `access_denied`; no anonymous code/token is issued. |
| An existing A-bound credential cannot be mapped to an equivalent authorization after adoption | Reject the credential (`401` on data access; `400 invalid_grant` for its invalidated refresh credential). Fresh consent is needed; it never acquires D authority by migration. |

For races, control the relative completion points rather than sleeping for token timestamps.
Repeat with and without refresh issuance, and with consent/withdrawal under U's equivalent URI.

| Interleaving | Proposed result |
|---|---|
| Consent approved; withdrawal completes; old code is exchanged | `400 invalid_grant`; no usable API token or refresh family. |
| Code exchange takes effect; disconnect completes; exchange response then arrives | Returned credentials cannot authorize the next request (`401`) or refresh (`400 invalid_grant`). The response arriving last does not revive the connection. |
| Consent narrowed while an older code is outstanding | Older code gives `400 invalid_grant` even if some permissions survive. A code for the new decision can exercise only that decision. |
| Session-only exchange overlaps a forced MCP reauthorization barrier | Old-consent token cannot acknowledge the replay or access private data after the barrier. Fresh challenge-bound consent is required even though no refresh family exists. |
| An older consent screen is submitted after that barrier, or after a newer barrier supersedes it | No usable authorization for that challenge; the stale transaction cannot count as its fresh consent. |
| Client refreshes while its connection is disconnected | Refresh fails, or its earlier-issued result is unusable after disconnect; a replacement family cannot survive. |
| Client completes fresh challenge-bound consent, then replays MCP authorize | One acknowledgement, subject to current sufficient authority; no challenge loop. An unrelated or expired challenge cannot be consumed. |

### Adoption impact and remaining profile work

This authorization recommendation for [#69](https://github.com/sempods/sempods-spec/issues/69)
is based on revision `721b109342a2031500038850a80718d3d707fb75`. Current auth/grant requirements
remain binding until coordinated normative adoption.

The [protocol-profile recommendation](protocol-profiles.md#selected-standards-and-candidate-dispositions)
selects the dated standards, operation scope and redirect exceptions for these cases. It retains
RFC 6749 code/service/refresh operations, S256 PKCE and Bearer presentation while applying the
selected security protections. It imports neither every OAuth extension nor an unversioned draft.

The remaining changes below are coordinated under #70/#71 and reviewed before #74 adoption.
The conditional state echo is already covered by AUTH-025 through #10/PR #105; the remaining
proposal adopts no normative changes. #65's removal of guaranteed refresh-token issuance remains intact.

| Existing contract | Proposed disposition |
|---|---|
| AUTH-008/009/010/011 | Preserve the unauthenticated public `dyn:` profile, PKCE/consent and its exclusion from service access. Narrow the endpoint-wide prefix and registration-response restrictions to that profile; protected service registration, if offered, is a distinct authorized profile even at the same route. |
| AUTH-012 | Replace mandatory out-of-band host-operator provisioning and the blanket ban on pod-token/dynamic provisioning with operation-, target- and pod-bounded service administration. Ordinary data authority is insufficient; no common installer API is selected. |
| AUTH-013/017 | Remove fixed-at-registration and mandatory per-Context grant form. Preserve the service identity/class, independently authorized assignment changes, and the public-read/OIDC exclusions. |
| AUTH-002/027/032 | Retain Client Credentials support and the current service token endpoint contract in this iteration. Making service access optional remains separate. The [protocol recommendation](protocol-profiles.md#service-credentials-and-registration-metadata) retains the standard recommendation against service refresh issuance and proposes bounded exceptions with matching family semantics. |
| AUTH-033/034/063 | Apply the [service-refresh recommendation](protocol-profiles.md#service-credentials-and-registration-metadata): retain rotation, client binding and revocation; generalize code-only family seeding for a justified service-refresh exception. Check live registration, current authority and credential-revocation state at issuance. Distinguish credential revocation from authority-only withdrawal: valid authentication still uses current rights, including after late responses and refresh. No guaranteed issuance. |
| AUTH-014/024, GRANT-013/014/028/029/030 | Express ordinary consent and service data authority without Context prerequisites. Keep the Context-specific management boundary in the optional module; no pod-wide service administration follows from D data access. |
| AUTH-009/022/023 | S256 PKCE for both user-facing client shapes. Preserve client/redirect validation and AUTH-025's current response contract; use the [selected profile and explicit redirect exceptions](protocol-profiles.md#selected-standards-and-candidate-dispositions). |
| AUTH-026, GRANT-002/015/016/018/019, AUTH-052/061/062/063 | Retain client isolation, trusted-alias coverage, delegation ceilings and fresh-consent barriers; replace prescribed storage/lookups/write ordering with the tested outcomes above. Narrowing never silently restores removed authority. |
| GRANT-020/021/022/031/032, AUTH-042/043/044 | Retain additive public-read and credential-free reads; generalize to public assertions in the requested scope and permit public-only issuance on an empty pod. Keep invalid-credential rejection. |
| MCP-011/012/013/030 | Coordinate ordinary data-access authorization acknowledgement and forced reauthorization. Replace issuance-time evidence with challenge-bound fresh consent (#49); do not require Context grants or a writable-Context list to acknowledge core authority. The exact MCP result shape remains a module-view decision. |

The current [OAuth discovery profile](../../spec/core/auth.md#10-discovery) supplies core pod-local
metadata. The [MCP profile](../../spec/modules/mcp.md#discovery-and-resource-binding), adopted by
[PR #111](https://github.com/sempods/sempods-spec/pull/111), uses the MCP endpoint as resource and
audience and the pod base as issuer. #99 retains its incomplete client-validation evidence;
external service identities remain proposed under #96.
The [protocol-profile recommendation](protocol-profiles.md) supplies the remaining #82 dispositions,
registration/error-ID cases and #77 handoff. Its proposed changes, the authorization cases here and
the [Context lifecycle recommendation](context-contract.md#adopted-rdf-surface-and-proposed-lifecycle)
need coordinated normative adoption; their proposal merges do not change the current contract.

Validation compares these cases on a Context-backed store and a policy-based store with equivalent
authority, including empty D and future creation. Existing ACP fixtures demonstrate their supplied
static policy model; they do not execute these consent, credential, migration or race transitions.
An implementation path must show all relevant interleavings, not merely report a green query model.

## Operation boundaries

### Queries and retrieval

For fixed data and authorization state, a supported SPARQL query returns the result it would produce
against the caller-authorized dataset. The dataset is a semantic model of what can be observed; the
implementation need not materialize it. Views, native store restrictions and query rewriting are
possible enforcement mechanisms if they preserve that result.

The [logical dataset recommendation](data-access.md#logical-dataset-and-operation-scope) defines
a coherent implicit default scope, authorized named projections, ordinary-write placement and explicit
selection. Graph placement and disclosable graph names are part of the result contract, not storage
choices. Conformance fixtures use identical assertions, view definitions and names across implementations;
physical partitions remain free. Empty datasets still use standard query evaluation, including
empty group patterns and aggregates.

Client-supplied dataset clauses and graph names cannot widen access. Store-local authorization data
and other pods are outside the caller's data view unless an explicit contract makes them available.

Filtering final results is insufficient. Hidden statements must not alter an ASK answer, aggregate,
negation, join, property path or subquery. For example, adding a document hidden from a caller leaves
that caller's count unchanged. Filtering a resource out after counting it fails that comparison.

The same read policy applies to direct resource reads and find. Hidden text cannot nominate a
visible search hit; unreadable statements cannot affect matching, ranking, limits or expansion.
Find's ranking may remain implementation-defined, while this isolation property does not.

### Mutations and partial representations

The following recommendations are the mutation portion of
[#69](https://github.com/sempods/sempods-spec/issues/69), reviewed against specification revision
`4e7a27044dbcadc318f288cb9111edc8eeccd9ec`. They remain **proposed**, including the changed slot
outcomes. The [current CRUD chapter](../../spec/core/lod-crud.md) continues to bind. The proposed
[logical dataset](data-access.md#logical-dataset-and-operation-scope) identifies the graphs a
request addresses; both recommendations need coordinated review before normative adoption.

#### Standard behavior and the pod's remaining choice

Use [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) for method and conditional-request
semantics, [RFC 5789 §2](https://www.rfc-editor.org/rfc/rfc5789.html#section-2) for PATCH atomicity,
and [RFC 7396 §2](https://www.rfc-editor.org/rfc/rfc7396.html#section-2) for JSON Merge Patch.
Those standards do not select the RDF facts addressed by a pod operation or its authorization
boundary. These are the choices below. No policy language, storage partition or transaction
algorithm follows from them.

The **operation scope** consists of the addressed resource, slot or edge within the logical data
space selected by the [dataset recommendation](data-access.md#logical-dataset-and-operation-scope):
the implicit D scope for an ordinary operation, or a selected Context's independently mutable assertions
under the membership-write contract. General computed views are read-only through selected CRUD
until a separate write-through contract is defined. The direct write scope is fixed independently
of response filtering; dependent views are reevaluated after mutation. A filtered GET is not
permission to redefine a later PUT as replacement of just that visible subset.

The [default-access acceptance sequences](data-access.md#default-access-acceptance-sequences)
apply this boundary to single-graph, independent-Context and computed-view cases. Their
[authorization and conditional cases](data-access.md#authorization-and-conditional-boundaries)
exercise the guarantees below against the same D scope, including hidden collisions and revocation.

| Operation | Recommended effect within that scope |
|---|---|
| Resource PUT | Replace all outgoing statements of the addressed subject; preserve incoming statements. |
| Resource DELETE | Remove all outgoing statements of that subject; preserve incoming statements. |
| Object-shaped merge PATCH | Replace or remove the complete values of each named predicate, including `@type` where supplied; preserve unnamed predicates. Apply the existing canonical-shape constraints and RFC 7396 arrays/nulls. |
| Slot PUT / DELETE | Replace / clear all values of the addressed subject and predicate. |
| Slot POST | Add the supplied set of values as one operation; existing values are unchanged. |
| IRI edge DELETE | Remove the single addressed triple; preserve other values. |

For every operation, authorization covers its entire effect, including facts removed by omission
and the values being added. A request either applies that effect completely or changes nothing.
A body that names only permitted additions does not authorize replacing protected old values.
A no-op does not bypass authorization. Admission to a write request is checked even when the body
names no changes: PATCH requires current authority to edit at least one predicate of the addressed
resource; slot POST requires current authority to add at least one value to the addressed slot.
These are permissions over possible edits, independent of whether any such fact currently exists.
For a non-empty body, admission alone is insufficient: every requested effect is also authorized.
This describes an authorization outcome, not a new stored permission or policy API.

An empty `{}` PATCH, a PATCH containing only the matching `@id`, and an empty `[]` slot POST remain
valid no-op inputs. After admission and applicable preconditions, recommend `204` with no body,
Location or validator and no resource creation. An authenticated read-only or unrelated caller gets
`403` for existing, hidden and absent targets alike; missing or invalid credentials get `401`.
The target's absence alone does not prevent admission where policy permits an edit there. An empty
slot PUT or a PATCH assigning an empty array is different: it clears values and needs authority for
that effect. Atomicity covers the addressed logical scope, including all occurrences affected by an
ordinary operation in D; it introduces no bulk-operation API.

#### Complete scope authority and non-disclosure

Recommend authorizing the whole resource for PUT/DELETE, the complete named predicates for merge
PATCH, the whole slot for replacement/clearing, and the named values for addition or edge removal.
The authority covers both additions and removals. Finer authorized edits can therefore succeed
while an entire resource replacement is refused. A response that distinguishes existence, such as
resource creation versus replacement, additionally requires authority to observe that distinction.
In particular, unconditional predicate replacement by PATCH or slot PUT needs complete write
authority over that predicate, including any unreadable values it removes; complete read visibility
is not an additional requirement. Hidden values that are not writable still prevent replacement.
Use a content-free success response (`204` for PATCH, `200` for slot PUT), subject to the metadata
rule below. No exported policy catalogue or new authorization flag is needed.

"Complete" is a property of the authority for that scope, including empty states. Comparing the
currently visible facts with the stored facts is insufficient: accepting when no hidden fact
exists and refusing when one exists would itself disclose hidden data. Under unchanged authorization state (including policy inputs),
caller-visible data and request, varying hidden facts cannot change the refusal or any visible
mutation effect. If the implementation cannot satisfy that property for a scope, it refuses that
class of mutation consistently, including on the corresponding empty scope. A deployment can
still grant complete authority over selected subjects, predicates or values and support their
successful operations.

For a valid authenticated caller whose operation is not authorized, recommend a uniform `403`
without existence diagnostics, validators or a Location header. An invalid credential remains a
`401`; data reads keep their absent/inaccessible `404` behavior. Determine authorization before
returning an existence-dependent write result. This generalizes the Context-existence protection of
[`SPS-CORE-018`](../../spec/core/index.md#SPS-CORE-018). Syntax errors and unsupported media types
retain their normal errors and must not depend on hidden facts.

Write authority need not imply read authority universally. For example, an explicitly authorized
set addition can return the uniform `204` proposed below without revealing whether the value was
already present. That does not authorize removing a protected existing value. A resource PUT
supplying outgoing statements keeps its creation/replacement distinction and therefore needs
visibility of that distinction as well as complete write authority. A pod cannot claim success for
a partial replacement, or accept a hidden collision by redirecting the write elsewhere.

#### Preconditions and concurrent changes

Apply current authorization independently of the supplied validator. Follow RFC 9110 §13.2.1 for
precondition evaluation after the normal request checks: an unauthorized caller gets the same
refusal with `If-Match`, `If-None-Match: *` or no conditional field. Preconditions are evaluated
only when the unconditional response would be successful or `412`; otherwise preserve the normal
error. Thus an authorized resource DELETE of an absent target stays `404` even with `If-Match: *`.
When evaluation applies, a false precondition yields `412` and no change.

Validators identify the selected representation. They grant no authority and must not change
solely because hidden data changed. LOD and system aliases for the same subject, logical scope and
representation agree. A changed scope cannot reuse a previous tag to validate a different target;
a changed policy is always enforced, even if the selected bytes and tag are unchanged. Resource
and slot tags remain specific to their own representations.

For every mutation, response content and metadata reveal only state the caller may read. A blind
replacement therefore does not echo the stored values. A validator is emitted only when the caller
may read the complete representation it validates; omit ETag, Last-Modified and other metadata
derived from unreadable state. A filtered-view tag cannot validate replacement of unreadable
facts. Uniform status codes alone do not prevent this disclosure. For slots, this requires a
coordinated change to [`SPS-CRUD-052`](../../spec/core/lod-crud.md#SPS-CRUD-052).

An otherwise applicable condition that tests unreadable state, or would validate replacement of
unreadable facts, receives uniform `403`, with no mutation or validator. This includes `If-Match`
and `If-None-Match: *`; do not evaluate a hidden-state predicate and distinguish true from false.
For a slot mutation that evaluates a complete-slot condition, the caller therefore needs complete
slot visibility. Unconditional authorized additions, replacements and clearing remain available.
Empty slot POST and empty resource PUT follow the same condition rule. Existing prescribed
ignoring of conditions, such as edge DELETE's `If-Match`, remains separate from evaluation and
introduces no state test. The proposal changes CRUD-034/052/053/054's applicability and needs
matching OpenAPI wording at adoption.

The current Context-specific slot-tag rules continue to bind until normative adoption;
[#9](https://github.com/sempods/sempods-spec/issues/9) can repair their current OpenAPI view
independently.

Authorization, preconditions and effects need one coherent outcome under races. A completed
revocation precedes authorization of the next request. Overlapping writes and revocation may be
ordered either way, but must not combine an earlier permission decision with a later incompatible
target or return a partly applied effect. This requires observable consistency, not a particular
lock, database transaction or write/check sequence.

#### Slot batches and outcomes

For [#6](https://github.com/sempods/sempods-spec/issues/6), recommend retaining multi-value slot
POST and reporting successful completion with `204`, without a body or Location. The effect is
set addition regardless of whether none, some or all supplied values were already present.
Duplicates in the request do not create duplicate RDF statements. A single unauthorized value
refuses the complete request; no permitted prefix is inserted. The permission to add a named value
is checked even if it already exists, so a no-op cannot disclose membership by bypassing a denial.

Recommend the same `204` completion for slot and edge DELETE, including an already empty slot or
absent edge after authorization. For a resource PUT supplying at least one outgoing RDF statement,
retain `201` plus Location when the addressed scope previously had none, and `200`/`204` otherwise.
Resource DELETE retains `204`/`404` after authorization. These existence distinctions require
permission to observe that scope.

A valid resource PUT supplying no outgoing RDF statements is a clearing operation, including a
body containing only the matching `@id` or only empty predicate arrays. With complete whole-resource
write authority, return `204` without a body, Location or validator whether the scope was empty or
not; preserve incoming links. No separate resource marker is created. A subsequent GET with no
visible outgoing statements returns `404`. Conditional requests follow the rules above: a caller
entitled to test existence can use `If-None-Match: *`; a false condition still gives `412`, while
repeating an empty PUT against the empty scope succeeds with `204`. This explicitly revises
CRUD-033's creation classification rather than making empty RDF input invalid.

This deliberately replaces the current custom slot/edge outcome bodies and POST `201` distinction
in CRUD-044/047, together with the validator changes above. A client permitted to read resulting
values reads the slot. No batch result envelope,
literal-edge URL, or arbitrary choice of one new edge for Location is introduced. The normative
patch must align the status/body descriptions and references together; this recommendation changes
no current OpenAPI schema.

#### Request cases for review

Let `R` be `https://example.org/alice/notes/one`, `p` be `https://schema.org/name`, and `q` be
`https://example.org/private`. Requests use the existing LOD and system route encodings. Each row
states policy setup; it is a proposed protocol case, not an executed ACP fixture.

| Setup and request | Recommended response and effect |
|---|---|
| Complete resource authority; PUT R with only `p = ["new"]` over `p = ["old"]` | `200` or `204`; the outgoing resource is replaced, incoming links survive. |
| Same authority, absent R; PUT supplying p with `If-None-Match: *` | `201`, Location R; repeating it gives `412` and preserves the first write. |
| Policy permits only p; GET R returns p; PUT R containing p | `403`, no changes, both when q has hidden values and when q is empty. A resource replacement is outside this authority in both states. |
| Same policy; PATCH R with `{"https://schema.org/name":[{"@value":"new"}]}` | Success with the complete p array replaced; q is unchanged. Complete write authority over p is assumed, including unreadable values; partial read visibility alone does not require refusal. Return `204` without unreadable content or metadata. |
| Policy gives no complete authority over R; PUT R with `If-None-Match: *` | Same `403` for a hidden existing R and an absent R; no Location, validator or mutation. |
| Complete slot authority; p contains A; POST the IRI values A and B | `204`; p contains A and B. Repeating gives `204` with no further change. |
| Caller may add A but lacks authority for B; POST A and B | `403`; neither value is added, including when B is absent. |
| Authorized resource edit with stale `If-Match` | `412`, no changes. With authority revoked before the request, `403` instead. |
| Hidden q changes while the caller can read only p | The visible representation/tag and the authorized p-only edit are unaffected; whole-resource replacement remains uniformly refused. |
| An authorized edge is already absent; DELETE that edge | `204`; other values survive. Without authority for that edge, uniform `403` whether present or absent. |
| Authorized resource DELETE of absent R, with `If-Match: *` or a supplied tag | `404`, no change; the unconditional error makes the precondition inapplicable. |
| Caller may add B to p but cannot read the complete slot; unconditional POST B | `204`, no validator or hidden-state metadata. Hidden A changing before a repeat does not change the response. |
| Same blind writer; slot POST B or `[]` with `If-Match` or `If-None-Match: *` | Uniform `403`, no change, for both matching/nonmatching tags and empty/nonempty slots. |
| Caller may edit p of R but not q; unconditional PATCH `{}` or a matching `@id` only | `204`, no validator or creation, whether R is present or absent. A read-only caller gets `403` in both cases. |
| Caller may add B to p; unconditional slot POST `[]` | `204`, no validator or creation, whether p is empty or not. A caller with no addition authority gets `403`; missing/invalid credentials get `401`. |
| Complete resource write authority; unconditional PUT R with only its matching `@id` | `204`, no Location, validator or persistent marker, on both absent and existing R. Outgoing statements are cleared, incoming links survive; repetition remains `204`. |
| Same writer may observe existence; empty PUT R with `If-None-Match: *` | `412` if outgoing statements exist; otherwise `204`, including repetitions. Without authority to test that state, uniform `403`. |
| Complete write authority over p, only partial read visibility; unconditional slot PUT with a new array | `200`, no body or unreadable-state metadata; all p values are replaced, including writable hidden ones, and q survives. |
| Some existing p values are outside write authority; PATCH replacing p or slot PUT | Uniform `403`, no change, whether protected values currently exist or not. |

Repeat the cases through aliases and in a single-graph, Context-based and area/document-policy
model once their logical scopes are defined. Include concurrent revocation, input validation,
retries, mixed batches and zero-change outcomes. The observable cases are the acceptance target;
implementation setup may differ.

### Creation and lifecycle

An empty pod can authorize creation under its existing policy without first exposing a Context.
An implementation may provision internal storage or initial policy during an authorized setup or
creation flow. A request does not acquire management authority just because something is absent.

Where resource creation needs an initial policy, both become effective together from a client's
perspective. Cancellation or failure grants nothing. Reusing an identifier must not accidentally
restore a delegation that was revoked. The lifecycle of policy retained after deletion therefore
needs a deliberate implementation mapping to the core revocation contract.

Ordinary RDF about a control-plane IRI is data. It is not a policy update. Implementations may offer
separate administrative interfaces, but those interfaces enforce their own authority; a blanket ban
on every write interface beyond sempods CRUD would prevent legitimate administration.

Bulk administration has a distinct authorization question from editing one resource. The
[Context lifecycle recommendation](context-contract.md#adopted-rdf-surface-and-proposed-lifecycle) separates unregistering a view
from deleting its source data. Full adoption withdraws Context-bound authority while retaining
source assertions, media associations and independent authority. Retention grants no access and
recreating the IRI restores no revoked authority. Its [completion and race boundary](context-contract.md#lifecycle-authorization-and-completion)
also covers selected media writes; its [acceptance cases](context-contract.md#lifecycle-acceptance-cases)
cover independent D access and loss of the last public view. Current destructive deletion remains
binding until coordinated normative adoption.

## Context access modes

Core provides Context discovery, selection and access summaries without requiring physical named
graphs or stored grant strings. A pod can return an empty catalogue. Ordinary clients need no
Context-related request. Read, data-write and view-management authority are independent; the last
requires the optional management surface, and managing a view does not authorize source writes.

The [proposed caller-access summary](context-contract.md#caller-access-summary) defines scope-level
eligibility and its limits under target/payload policies. It changes the current grant-based
[`SPS-CTX-034`](../../spec/core/contexts.md#SPS-CTX-034) at adoption. Keep current response-relative
interpretation, cache isolation and authorization of every later request. No copied RDF relationship
or old validator confers authority; a writable hint does not make a hidden collision observable.

## Who may share, and why there is no chain

This is a proposed sharing design for Context-based implementations, retained for the worked
resharing example. Core specifies no interpersonal sharing API and does not require this design.
Its peer rules are candidates for a membership-based Context sharing profile. The current contract
already specifies the owner's implicit authority in `SPS-GRANT-011`.

Passing access to another person requires `manage` on the context. Reading it is not enough, and the
difference is the whole design: a reader who may pass on what they can already see turns every grant
into the root of a tree somebody has to keep.

Every holder of `manage` on a context is a peer of every other. There is no first among them and no
order of precedence — a person granted `manage` yesterday may remove the grants of the person who
granted it, and either may remove anybody else's. What makes that safe rather than reckless is a
floor the pod supplies and nobody can edit: that profile gives the owner every mode on each of its
membership-based Contexts implicitly, and [`SPS-GRANT-011`](../../spec/core/grants.md#SPS-GRANT-011) forbids requiring those grants to be
stored, so there is no row for a peer to delete. A peer set cannot empty itself out from under the
pod.

**And that is what removes the chain.** A share is always issued directly by somebody holding
`manage` at the moment they issue it, so there is no derived access to trace and no provenance to
keep: deciding whether a grant may be removed never requires knowing who wrote it. What a peer does
on revocation is recompute the remaining authority — the instruction
[`SPS-GRANT-016`](../../spec/core/grants.md#SPS-GRANT-016) already gives for delegations, and not one
step deeper.

The reader-resharing alternative needs provenance to distinguish the supplied end states.
[`examples/70-resharing.md`](../../examples/70-resharing.md) shows two states that compile to the
same access control resource — a defect and a correct outcome, told apart by nothing in the graph —
because what separates them is who issued which grant, and a policy has no room for that. Provenance
kept beside the access control resource is the price, and a resource whose policy no longer explains
itself is what it buys.

Because `manage` is slash-delimited ([`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007)),
this is a tree of peer sets rather than one: a peer on `projects` is a peer on `projects/alpha`, and
a peer on `projects/alpha` is not a peer anywhere above it.

What none of this decides is whether a pod offers a sharing surface at all. **None is specified.** No
route writes a grant for a person, and the model above is the shape such a route would need rather
than one that exists — which is what makes leaving it out a decision instead of an omission.


## What the examples establish

The ACP fixtures check the listed access decisions under their supplied assumptions.
The resharing case compares supplied end states; it does not execute the revocation process.
The runner's self-tests verify its guards, not the security of an implementation's query engine.
A green run is therefore evidence about those fixtures, not conformance of the proposed core or
optional Context management.

## Validation before adoption

Use two implementations with different policy mechanisms and the same public requests. Configure
known allowed and denied resources through each implementation's own setup. Check successful CRUD,
rejected writes with no partial changes, revocation with an existing credential, and equivalent
authorization on direct reads, SPARQL and find. Always denying access is not a passing implementation.

For query enforcement, compare results with a reference evaluation over the same authorized dataset,
including its logical graph placement and names. Include unqualified patterns, `GRAPH ?g`, fixed
graph names, aggregates, negation, subqueries, paths and adversarial dataset clauses. Alter hidden
data and physical partitions while holding that logical dataset fixed. Test find for hidden
matches, ranking and expansion. Cover public reads without credentials, tokens with and without
`public-read`, no currently public data, policy changes, revocation and invalid credentials.
An enforcement mechanism earns conformance from these observable properties, not its name.

Review the authorization cases and their [remaining profile work](#adoption-impact-and-remaining-profile-work)
alongside the mutation/dataset recommendations and core Context/optional management boundary before
adoption. Rewrite correctness is an implementation obligation.
Installation of an implementation's policies is a deployment concern unless a client-facing
management contract is being specified.

## Scope

This proposal does not standardize an ACP management API or require every policy to be exportable.
It makes no Solid conformance claim. [Data mirroring](data-access.md#mirroring-data) is separate
from delegation: copies are governed by the destination's policy, and source revocation does not
recall them automatically.
