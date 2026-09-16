# Discover a pod and its services

Status: **Proposed; non-normative.**
Owning issue: [#96](https://github.com/sempods/sempods-spec/issues/96).
Adoption: no normative adoption PR yet. This first design covers the entry point and a SPARQL
service binding, against revision `6fa7b6b87204c5bd6a53c522554b196336547a5b`.

## Start with a pod address

Alice gives a notes app `https://pods.example/alice`. The app finds the pod's description, learns
where it can query Alice's data, and obtains permission for that service. Alice's query service
might run on another host. Bob might use that host too, with a separate data and permission boundary.

Recommend one public description reached through a typed HTTP link from the pod address. It combines
conformance declarations with service locations. Detailed operations and access flows belong to each
service's identified protocol profile. This follows [the vision](../vision.md#what-belongs-in-the-contract):
sempods connects contracts while leaving deployment and storage choices open.

A pod can keep its services under `/_system/`, use external services, or combine both. Local services
remain a permanent option. Discovery removes the client's need to construct their addresses; it does
not require implementations to remove them. A pod with only external operational endpoints still
answers discovery at its entry address and satisfies the full authorized-data core. AI and S3
compatibility are possible future profiles, not choices made here.

## Keep the local data namespace predictable

Keep the existing reservations: `_system` and `.well-known`, immediately below the pod base, and
all their descendants are unavailable to ordinary LOD resources. They stay reserved even when no
service is hosted there. Segment boundaries matter: `/alice/_system-notes` is not `/alice/_system`.

Service routes and discovery documents inside the pod namespace use those reserved spaces. External
endpoints may lie outside the pod's namespace, including elsewhere on the same origin; they do not
reserve more of its local data space. A binding for ordinary LOD access retains the existing data
addressing rules. Publishing a query or token endpoint at `/alice/notes` cannot turn an ordinary data
address into a service route. Clients need no changing list of implementation-defined reservations.

The exact pod entry `/alice` has a separate, public bootstrap role. Its GET response and discovery
link are controlled by the pod, not read from an ordinary user-writable RDF resource. Ordinary LOD
PUT, PATCH and DELETE cannot replace or remove it. Statements *about* that IRI can still be stored
and accessed through the data API; they do not configure the entry or its services. This is an
explicit proposed exception to ordinary LOD addressing, to be reconciled with CRUD-001–004/018 at
adoption. #78 still owns whether a pod base itself may end in a reserved segment.

Apply one common separation rule: service requests are handled under their service contract.
Unsupported methods or representations never fall through to ordinary LOD CRUD. Generic data
operations cannot read service internals, change service state or bypass service authorization.
A service may return RDF when its contract specifies it; its IRI may also be described as data.
Neither turns user-authored RDF into authoritative service configuration. Modules define their own
operations and permissions, and inherit this shared boundary instead of repeating it. Reservation
does not require authentication: a discovery document can be public while remaining outside ordinary
LOD CRUD.

## Find the description without guessing a path

The proposed bootstrap is an unauthenticated `GET` of the exact pod entry URL, with `Accept: */*`.
A successful response carries one `service-desc` link for the pod-description media type:

```http
GET /alice HTTP/1.1
Host: pods.example
Accept: */*

HTTP/1.1 200 OK
Link: <https://pods.example/alice/_system/description>; rel="service-desc"; type="application/sempods-discovery+json"
Content-Type: text/html
Access-Control-Allow-Origin: *
Access-Control-Expose-Headers: Link
Cache-Control: no-cache
```

The body may be Alice's public landing page or a service-defined RDF description of the pod. A client
follows the typed link, requests that media type and validates the returned description. The media
type above is a **proposed, unregistered name**; its registration and exact format need review before adoption. The `service-desc` relation
is registered by [RFC 8631 §4.2](https://www.rfc-editor.org/rfc/rfc8631.html#section-4.2), an
Informational RFC. It defines the relation, not this proposed description format.
[RFC 8288 §3](https://www.rfc-editor.org/rfc/rfc8288.html#section-3) supplies link parsing and context.

Keep this first bootstrap small: one link from the entry URL and one description fetch, both with
`200`, or a validated cached response. No redirects, description chaining or `anchor` override are
used for this flow. Reject a missing or ambiguous matching link, wrong response type or mismatched
pod identity. Unrelated links are ignored. Clients apply finite response-size and time limits and
report discovery failure when a limit is reached. Resolve link targets under RFC 8288; fetched URLs
use HTTPS without userinfo or fragments. Clients do not fetch every service or profile IRI.

The entry URL is the pod identifier for this design. It uses the existing canonical HTTPS base-URL
form; service URLs need not share its prefix. The description's `pod` value matches that identifier
exactly. The description may itself be hosted elsewhere: the authenticated HTTPS response at the
entry URL delegates its description to that exact link target. A document claiming Alice's identity
without that link is not authoritative. Moving the entry identity is separate work under
[#21](https://github.com/sempods/sempods-spec/issues/21); moving a service does not move it.

Discovery GETs send no bearer token or ambient credentials. Browser access needs CORS for the entry
and description, including exposure of `Link` (see the informative
[Fetch CORS explanation](https://fetch.spec.whatwg.org/#http-cors-protocol)); service profiles also
need to account for their own browser requests. A server-side client retains its network-access
restrictions when following URLs, including checks after DNS resolution. A trusted discovery link is
not permission to reach an otherwise forbidden internal address. This proposal's external cases use
HTTPS; loopback-only development remains a separate, explicitly configured case.

### Alternatives

| Approach | Assessment |
|---|---|
| Typed `service-desc` link from the pod entry | Recommended. Reuses a relation and allows an HTML or RDF bootstrap response. The linked description can be under `/_system/` or outside the pod namespace. |
| Content negotiation directly at the pod entry | Viable alternative with one fewer request. It adds the discovery representation to the entry's existing representation and cache handling. Keep one required bootstrap rather than requiring both. |
| A fixed `/_system/` path as the sole bootstrap | Requires the client to construct that address. Keep the reserved namespace and allow services there permanently; the entry link also supports an external description. |
| A host-rooted well-known path | Useful when the host supports it, but cannot be the sole general bootstrap for a pod that controls only its own path. Protocol-specific well-known requirements still apply. |
| RDF links alone | Natural for semantic clients, but a client needs a defined representation and authoritative link before it can find the right RDF. It does not by itself settle bootstrap. |

## Keep one small description

Recommend JSON, reusing the existing conformance fields. An RDF representation can be considered
separately; semantic data access does not require every discovery client to process RDF. The proposed
fields are:

| Field | Meaning |
|---|---|
| `discoveryVersion` | Version of this description format, separate from core/module versions. An unsupported format version stops interpretation. |
| `pod` | Stable pod entry identifier. It is not a prefix to append to service URLs. |
| `specVersion`, `modules` | Full core and module conformance claims, as in the existing conformance response. Module entries keep `id` and `version`; an absent module is not offered. |
| `services` | Public service bindings: each has a `capability` IRI, a `profile` IRI identifying an exact protocol contract, and an absolute HTTPS `endpoint`. A profile defines whether its endpoint is a complete operation URL or a service base. |

Conformance says what behavior the pod promises; a service binding says where to use it. A module
can need several bindings, and a core capability such as query is not an optional module just because
it has a binding. An endpoint entry alone never declares module conformance. A complete description
provides the bindings required by its declared versions; missing required bindings make it unusable
for those operations, not permission to invent a route.

Recognized profiles define their required fields, methods, authentication and pod selection. Unknown
capabilities, profiles and optional members are ignored. An unknown profile for a needed capability
means unsupported, not permission to send a guessed request. Security-critical changes need a new
profile or format version, not an unknown field an older client would ignore. In this first design,
one binding exists for each capability/profile pair; duplicate pairs are invalid. Alternative
replicas, priorities and automatic failover are outside this slice.

The document is public and caller-independent. It contains no tokens, per-user grants, private
Context names or personalized endpoint lists. Discovery availability does not imply permission to
use a service, or prove that a service is healthy. Conformance and service entries come from one
coherent document, avoiding two independent catalogues that can disagree.

### One query binding

This is an **illustrative service entry**, not a complete conformance response. The two
`schema.sempods.org` capability/profile IRIs below are candidate names, not published vocabulary.
An adoption needs actual format/profile identities and all bindings required by its chosen core.

```json
{
  "capability": "https://schema.sempods.org/capability/query",
  "profile": "https://schema.sempods.org/profile/sparql-query-discovery-draft",
  "endpoint": "https://query.example/tenants/alice/query",
  "oauth": {
    "resource": "https://query.example/tenants/alice/query",
    "authorizationServers": ["https://login.example/tenant-alice"]
  }
}
```

For this example profile, the endpoint is the complete query URL and the OAuth resource equals
that URL. POST accepts `application/sparql-query` and uses the existing read-only query and sandbox
behavior; only location and authorization binding are proposed changes. It does not enable SPARQL
Update, federation or a new dataset. SPARQL service descriptions can describe supported query
features without copying them into this catalogue.

The `oauth` object is part of this proposed service profile, not a requirement that every possible
protocol use OAuth. It binds the intended token target and the issuers Alice's pod accepts for that
service. Other protocol profiles need their own defined access flow before they can be used. An
OpenAI-compatible or S3-compatible label alone is insufficient.

## From a discovered service to authorized access

For the query example, recommend the following sequence. This adds an explicit service target to
[the proposed consent flow](access-control.md#authorization-without-context-setup); it does not
let discovery grant data access.

| Step | Request and observation |
|---|---|
| 1. Find Alice's pod | GET `https://pods.example/alice`; follow its one typed link. The description names that exact pod and the query binding above. |
| 2. Find resource metadata | From the binding's resource identifier, GET `https://query.example/.well-known/oauth-protected-resource/tenants/alice/query`. Its `resource` equals the query endpoint and `bearer_methods_supported` includes `header`. Select an issuer present both in its `authorization_servers` and the binding's approved issuer list; no intersection means stop. |
| 3. Find authorization endpoints | For the selected issuer, GET `https://login.example/.well-known/oauth-authorization-server/tenant-alice`. The returned `issuer` matches exactly. Use its advertised authorization/token endpoints and supported client-registration mechanism. |
| 4. Obtain permission | Run the recognized Authorization Code profile with S256 PKCE, asking for `resource=https://query.example/tenants/alice/query`. Bind Alice's approval to her pod, this client, the requested service and the permitted data/operations. An unsupported target is an error, not a pod-wide fallback. |
| 5. Query | POST `ASK {}` to the query endpoint with the resulting access token. A permitted request returns `200` with a SPARQL result. Private-data cases use a query with known allowed and hidden statements. |

Resource and issuer metadata validation follows RFC 9728 §3.3 and RFC 8414 §3.3 respectively.
Metadata fetches remain credential-free and subject to the URL, size and time checks above. A
service's `401` can instead supply a `resource_metadata` location under RFC 9728 §5; it still has
to describe the same requested endpoint and pass the issuer restriction above. Successful public
reads do not need an artificial `401`: direct metadata discovery supports voluntary authorization.
A metadata or issuer mismatch stops authorization before any code or token is sent to the new party.

Code and token exchange bind the same requested resource; refresh cannot silently switch targets.
The chosen server issues a token restricted to this service target; the service verifies that target,
the issuing authority, client/subject and current permission for Alice's pod. A client does not need
to decode the token to validate the descriptor. The server's configured binding between endpoint,
resource and pod is authoritative: a caller-supplied pod name cannot switch that binding. Listing
a service is not a cryptographic attestation of its implementation; its operator is trusted to
enforce the advertised contract, just as a locally hosted pod is.

An existing token for the pod or another service is not forwarded to the discovered endpoint. Sharing
an issuer, person or host does not share consent. Two tenants on the same query host use distinct
resource/endpoint bindings in this profile. A shared URL needing another tenant selector would need
a profile defining that selector and its authorization binding; this draft does not guess one.

External services retain the pod's applicable data sandbox, denial and revocation guarantees.
Removing a catalogue entry alone does not revoke a token or permission: the old service needs the
corresponding authorization withdrawal. A backend that cannot enforce the promised guarantees
cannot be advertised as satisfying that profile. Discovery changes no permission-store algorithm
and does not require a particular token exchange or gateway.

### What this means for #66 and #67

[#66](https://github.com/sempods/sempods-spec/issues/66) can define the challenge hint without
requiring a general discovery catalogue first. For external service profiles, its resource binding
must be explicit: pod-level metadata cannot silently stand in for metadata naming a query endpoint.

[#67](https://github.com/sempods/sempods-spec/issues/67) still owns the issuer/address decision.
This example chooses standard host-rooted metadata addresses served by the query and authorization
operators. A pod entry hosted only under `/alice` need not serve either host-rooted route itself.
That moves the hosting responsibility; it does not remove it. An operator controlling only a service
subpath still needs support for those standard routes or an explicitly reviewed deviation. A general
discovery document cannot make a nonstandard OAuth route discoverable to every generic OAuth client.

The worked example changes AUTH-028's pod-base issuer assumption and adds service-targeted issuance.
The merged authorization proposal alone does neither. Keep those changes explicit when coordinating
#69 and #66/#67; this proposal creates no new dependency on implementing AI, S3 or a general
discovery system first.

## Cases to review

These are proposed client sequences and expected outcomes, not executed HTTP or conformance tests.
Use the same allowed/private RDF fixture across deployments; successful reads must return the
same authorized data, not merely an empty result everywhere.

| Setup and sequence | Expected outcome |
|---|---|
| All local: entry links `https://pods.example/alice/_system/description`; query endpoint is `https://pods.example/alice/_system/sparql/query`; use its selected profile | Follow the published URLs. This layout remains supported, not scheduled for removal. During an additive rollout, existing clients keep their routes and token contract. |
| Mixed: entry describes local RDF access and the external query binding above; approve and query | Query sees the same authorized logical data as the pod's RDF surface. The endpoint location adds no permission. |
| External only: entry serves the link; description and every operational endpoint are on other hosts; no service is served under `/alice/_system` | A discovery-aware client completes the five steps above. Both reserved local spaces remain unavailable to ordinary LOD CRUD despite being unused. Other core operations need their own adopted bindings. |
| Ordinary resource creation targets `/alice/_system`, `/alice/_system/notes`, `/alice/.well-known` or `/alice/.well-known/notes`, with data-write authority | No ordinary LOD resource is created and no service state changes, whether services occupy those addresses or not. `/alice/_system-notes` remains an ordinary data address under the usual CRUD rules. |
| A new query binding names `/alice/notes`, where ordinary data may live | Reject that service placement; keep the data address and its behavior. A descriptor cannot create a new local reservation or displace existing data. |
| A valid RDF PUT targets the pod entry or a token endpoint; an unsupported method or representation is sent to a service route | The relevant entry/service contract refuses it without ordinary LOD fallback or configuration changes. Data-write permission is not service-management permission. |
| A service returns RDF under its own contract; a client separately stores RDF statements about the pod or service IRI through the data API | Both are possible under their respective permissions. Stored statements do not alter the bootstrap link, endpoint routing or service state. The service response is not a generic LOD view. |
| Alice and Bob have distinct pod entries and `/tenants/alice/query` versus `/tenants/bob/query` on one host; present Alice's token at Bob's endpoint | Rejected credential (`401`); no Bob data. A token properly authorized for Bob can query Bob's allowed data. The service cannot select Alice's pod from an unchecked request field. |
| Valid Alice token, but no permission to one private statement | That statement has no effect on query results under the query sandbox. Discovery does not turn an empty authorized view into a `403`. |
| Required authorization refused, or resource/issuer metadata conflicts with the binding | No authorized private query. OAuth refusal stays a refusal; mismatched metadata stops discovery/authorization, without a fallback token or endpoint. |
| Unknown optional capability/profile beside a recognized query binding | Ignore the unknown entry; query still works. If only an unknown query profile exists, report unsupported. |
| Wrong `pod`, two matching description links, duplicate binding pair, or a discovery redirect/loop | Reject the ambiguous or invalid discovery result; do not select the first match or follow a recursive catalogue. |
| Endpoint A moves to B; revalidated description names B | Obtain authority for B before sending credentials there. Revoke A's authority separately where required. Pod/resource identities remain stable; an HTTP redirect from A cannot transfer credentials to B. |
| Removed service, unavailable endpoint, or expired discovery cache that cannot be revalidated | Report the observed absence or failure. Do not claim module support disappeared because its server is down; do not guess another route or fall back to a broader credential. |

Use HTTP freshness and validators for both discovery responses. Recommend `Cache-Control: no-cache`
with validators so a cached response is revalidated before starting a new connection; do not use
stale discovery on an error. On endpoint/authentication failure, allow one fresh bootstrap before
reporting failure. An in-flight write is not automatically replayed elsewhere. Server-side revocation
still governs existing connections; metadata revalidation is not a substitute for it.

## Standards and contract impact

The proposed profile uses RFC 8288 §3 for HTTP links and RFC 8631 §4.2 for `service-desc`;
[RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html) for JSON; and
[RFC 9111 §§4–5](https://www.rfc-editor.org/rfc/rfc9111.html#section-4) for cache handling.
For the OAuth query binding, use [RFC 9728 §§2–5](https://www.rfc-editor.org/rfc/rfc9728.html#section-2),
[RFC 8414 §§2–3](https://www.rfc-editor.org/rfc/rfc8414.html#section-2),
[RFC 8707 §2](https://www.rfc-editor.org/rfc/rfc8707.html#section-2) for resource targeting, and
[RFC 9700 §2.3](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.3) for audience restrictions.
Code exchange and PKCE use the bounded [authorization profile](access-control.md#adoption-impact-and-remaining-profile-work).
Query transport uses [SPARQL 1.1 Protocol §2.1](https://www.w3.org/TR/sparql11-protocol/#query-operation).
[SPARQL Service Description](https://www.w3.org/TR/sparql11-service-description/) is an informative
reuse option for detailed feature discovery. These references do not adopt every optional feature.

| Current contract | Proposed impact |
|---|---|
| CORE-007/008/019/020: addressing and reserved paths | Allow service locations outside the pod prefix while retaining both local reserved spaces, even when unused. Give the exact pod entry its bootstrap role; keep ordinary data paths free of new service reservations. #78 retains the pod-base naming question. |
| CORE-010–013: conformance route and document | Reuse core/module claims inside the linked description. Add format identification and service bindings. Keep unknown-extension tolerance without weakening known-profile validation. |
| AUTH-008/021/027/028/030/045–048: OAuth routes, issuer and metadata | Separate service resource, issuer and pod identities; support resource-targeted issuance and validation. Preserve client, consent and revocation boundaries. #66/#67 own the immediate discovery gaps. |
| SPARQL-001 and MCP-001/009: fixed endpoints and pod-level resource | Identify complete operation endpoints and their authorization binding. A general catalogue does not override a protocol's own discovery/initialization rules. |
| CRUD-001–004/018/040–044, FIND-004, Context/media/OIDC module routes | Reconcile the pod-entry exception and central service/data separation with existing addressing. Retain reserved-path exclusions. External placement still needs operation bindings and stable LOD dereferencing through an identity resolver/forwarding arrangement or a reviewed replacement. No full external CRUD binding is supplied here. |
| OpenAPI, vocabulary, index and conformance versions | Coordinated adoption needs matching descriptions, registered/owned media and profile identifiers, version decisions and downstream client/server changes. This proposal changes none of them. |

Recommend the smallest adoption slice as the typed entry link and description format, with bindings
that first point to existing routes. While supporting the current contract, keep
`/_system/conformance` and its required routes; both descriptions agree on core/module versions.
A missing new link can lead to the fixed route only when the client deliberately supports the legacy
contract and the entry response establishes that discovery is absent. An invalid new description or
network failure is not absence and does not trigger a downgrade.

A deployment may keep its local routes indefinitely. Retiring particular routes or advertising
external bindings requires adopted profiles and a compatible core version; neither releases the local reserved
spaces for data. Old clients cannot use an external-only pod by assumption. Before that step, resolve
media-type/format publication, complete bindings for all required core operations,
browser access, migration and the identity/authorization changes above. #96 owns this remaining
design; #21 owns general identity/version transitions. The existing vision and invariants of pod
isolation and authorized data access remain the criteria, not a requirement to co-locate services.
