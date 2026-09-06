# Module: Media

**Optional.** Everything in this chapter binds only an implementation that advertises the module IRI
`https://schema.sempods.org/module/media` at the conformance endpoint
([`SPS-CORE-005`](../core/index.md#SPS-CORE-005)). A pod holds RDF; only a deployment that means to
hold binaries provides this.

**Status: this text decides, and can still change.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: RFC 9110, RFC 7232, RFC 4648 §5. Error codes are [`../core/index.md`](../core/index.md) §5;
authorization is [`../core/grants.md`](../core/grants.md).

## 1. The model

<a id="SPS-MEDIA-001"></a>
**`SPS-MEDIA-001`** — This module holds bytes and a content type. An implementation MUST NOT
introduce image knowledge, variants, resizing or transformation. Rendering is the application's
business, done before upload.

<a id="SPS-MEDIA-002"></a>
**`SPS-MEDIA-002`** — Where the module is not provided, the media routes MUST NOT exist. An
implementation MUST NOT answer them with an error that implies they are temporarily unavailable.

<a id="SPS-MEDIA-003"></a>
**`SPS-MEDIA-003`** — A media identifier MUST be the SHA-256 of the bytes, encoded base64url without
padding.

<a id="SPS-MEDIA-004"></a>
**`SPS-MEDIA-004`** — Content addressing MUST deduplicate within a pod, and a collected object MUST
become unretrievable at that pod whatever else holds the same bytes.

The second half is what the first one costs if it is taken too far. Deduplicating across a
boundary — one stored blob behind several pods — is invisible from here until a collection, and then
it is a deletion this pod asked for and did not get. Written as "MUST NOT deduplicate across pods"
it named other pods to constrain this one, and no test against a single pod could settle it. Written
as an effect at this pod's boundary it is the same guarantee and can be checked: store, unassign,
collect, read.

<a id="SPS-MEDIA-005"></a>
**`SPS-MEDIA-005`** — An upload MUST NOT write RDF. It returns a media URL; whoever wants a
`schema:ImageObject` writes one themselves.

The registry and the graph do not know about each other, so there is nothing to keep in step and
nothing that can drift. The cost is stated in §6.

## 2. Routes

```
POST   {pod}/_system/media?context=<ctx>          upload
GET    {pod}/_system/media/{id}                   metadata
HEAD   {pod}/_system/media/{id}
GET    {pod}/_system/media/{id}/content           the bytes
HEAD   {pod}/_system/media/{id}/content
PUT    {pod}/_system/media/{id}?context=<ctx>     assign to a further context
DELETE {pod}/_system/media/{id}?context=<ctx>     drop one assignment
```

<a id="SPS-MEDIA-026"></a>
**`SPS-MEDIA-026`** — On a raw upload, the request's `Content-Type` header is the media's declared
type. An implementation MUST record it, MUST return it as the assignment's content type, and MUST
NOT infer it from the bytes.

<a id="SPS-MEDIA-028"></a>
**`SPS-MEDIA-028`** — Where a raw upload declares no type, the implementation MUST record
`application/octet-stream`. It MUST NOT reject the upload, and MUST NOT choose a type of its own.

Delivery depends on the declared type — `SPS-MEDIA-017` decides inline against attachment from it —
so an implementation with nowhere to carry one would have to sniff, and sniffing is exactly what
`SPS-MEDIA-016` disables on the way out. `application/octet-stream` is the honest answer and the
allowlist serves it as an attachment.

<a id="SPS-MEDIA-029"></a>
**`SPS-MEDIA-029`** — An implementation providing this module MUST serve exactly these addresses,
with these verbs:

| Route | Verbs |
|---|---|
| `{pod}/_system/media` | `POST` — upload |
| `{pod}/_system/media/{id}` | `GET`, `HEAD` — metadata · `PUT` — assign · `DELETE` — unassign |
| `{pod}/_system/media/{id}/content` | `GET`, `HEAD` — the bytes |

Without this the requirements below would constrain each verb once implemented while leaving an
implementation free to put it somewhere else — and `SPS-MEDIA-013` fixes the content address, which
only works if the others are fixed too.

<a id="SPS-MEDIA-006"></a>
**`SPS-MEDIA-006`** — `POST`, `PUT` and `DELETE` MUST each resolve exactly one write context, with
the rules of [`SPS-CRUD-007`](../core/lod-crud.md#SPS-CRUD-007).

Media is control-plane state that is nonetheless context-bound. It is the one part of the control
plane that takes `?context=`.

<a id="SPS-MEDIA-007"></a>
**`SPS-MEDIA-007`** — `PUT` MUST be idempotent, and `DELETE` MUST be ensure-absent: dropping an
assignment that is not there MUST succeed.

<a id="SPS-MEDIA-008"></a>
**`SPS-MEDIA-008`** — Assigning a media to a further context MUST require **both** write on the
target context and read on a context the media is already assigned to.

Write alone would let anyone attach an arbitrary media identifier to a context they control — and
since the identifier is a content hash, a caller who has the file elsewhere could confirm the pod
holds it, and then read it.

## 3. Authorization

<a id="SPS-MEDIA-009"></a>
**`SPS-MEDIA-009`** — A media MUST be readable exactly when its assignment set intersects the
caller's readable contexts. An implementation MUST NOT add media-specific authorization.

Anonymous access, `public-read`, the manage cascade, revocation and the context-deletion cascade all
follow from that one sentence, with no second model to keep aligned.

<a id="SPS-MEDIA-010"></a>
**`SPS-MEDIA-010`** — A media the caller may not read MUST answer `404`, and an identifier that does
not exist MUST answer the same `404`.

<a id="SPS-MEDIA-011"></a>
**`SPS-MEDIA-011`** — `POST` MUST always answer `201`, never `200`, including where the bytes were
already stored.

<a id="SPS-MEDIA-012"></a>
**`SPS-MEDIA-012`** — Metadata MUST list only the assignments the caller may read.

These three are one rule seen from three sides. The identifier is the digest of the content, so any
observable difference between "stored" and "not stored" answers the question *does this pod hold
exactly this file* — for a caller who already has the file and only wants to know who else does.

## 4. Delivery

<a id="SPS-MEDIA-027"></a>
**`SPS-MEDIA-027`** — Where the same bytes carry different declared types across several
assignments, the type used for a content response MUST be chosen deterministically from the
assignments **the caller may read** — by the lowest context IRI among them.

Content addressing deduplicates by bytes, and the declared type hangs off the assignment, so the
same media identifier can legitimately carry `image/png` in one context and
`application/octet-stream` in another. The content route names no context, so without a rule two
implementations answer differently and `SPS-MEDIA-017` picks a different disposition from each.

<a id="SPS-MEDIA-013"></a>
**`SPS-MEDIA-013`** — The content URL MUST always be `{pod}/_system/media/{id}/content`.

This is the load-bearing property of the module. A deployment that later serves bytes from a CDN or
a signed storage URL changes what the server *answers* there, never what the stored data *says* — so
it is an optimisation rather than a migration of everyone's `schema:contentUrl` values.

<a id="SPS-MEDIA-014"></a>
**`SPS-MEDIA-014`** — The entity tag on a content response MUST be derived from the content hash and
from the declared type of the assignment the response was built from
([`SPS-MEDIA-027`](#SPS-MEDIA-027)). `If-None-Match` MUST be honoured.

It is a strong validator by construction rather than by convention — the identifier already is the
digest of the bytes. The type has to be in it because two callers with different read access may
receive different declared types, and so different representations, at the same URL. A tag over the
bytes alone would let a conditional request or a cache carry one caller's representation to the
other, which is also why `SPS-MEDIA-015` requires the response to be private and to vary on the
credential.

<a id="SPS-MEDIA-015"></a>
**`SPS-MEDIA-015`** — Metadata and content responses MUST be marked private and MUST vary on the
credential. An implementation MUST NOT permit a shared cache to store them.

The answer changes per caller and, for the same caller, over time — revocation is promised to be
immediate ([`SPS-GRANT-003`](../core/grants.md#SPS-GRANT-003)), and a shared cache would outlive it.

<a id="SPS-MEDIA-016"></a>
**`SPS-MEDIA-016`** — Every content response MUST carry `X-Content-Type-Options: nosniff` and a
content security policy that sandboxes the response.

<a id="SPS-MEDIA-017"></a>
**`SPS-MEDIA-017`** — `Content-Disposition` MUST be decided by an **allowlist**: inline for a small
set of known-safe image types, attachment for everything else, including unknown types.

<a id="SPS-MEDIA-018"></a>
**`SPS-MEDIA-018`** — `image/svg+xml` and `text/html` MUST always be attachment.

SVG carries script. Served inline from the pod's own origin, an uploaded SVG is same-origin code
with access to everything that origin can reach — and it arrives looking like an image, which is why
a denylist of "dangerous types" is the wrong shape here and an allowlist is the right one.

## 5. Fetching a source

<a id="SPS-MEDIA-019"></a>
**`SPS-MEDIA-019`** — An implementation MAY accept an upload that names a source URL for the server
to fetch. Where it does, all of the following MUST hold:

- the scheme is checked against an allowlist;
- **every** address the host resolves to is validated, not just the first;
- the validated address is pinned for the connection that follows;
- the whole chain is re-run for every redirect hop;
- a size cap is enforced while streaming rather than after.

<a id="SPS-MEDIA-030"></a>
**`SPS-MEDIA-030`** — Where the server fetched the bytes, the declared type MUST be the
`Content-Type` the fetched response carried. Where it carried none, or none that parses, the
implementation MUST record `application/octet-stream`. It MUST NOT infer a type from the bytes or
from a filename.

`SPS-MEDIA-026` answers this for a raw upload and said nothing about the fetched path, which leaves
the same media reachable under a different `Content-Type`, a different `ETag`
([`SPS-MEDIA-014`](#SPS-MEDIA-014)) and a different disposition depending on which route stored it.
Inferring from the filename is the tempting alternative and the worst one: the filename comes from
the same untrusted source as the bytes.

<a id="SPS-MEDIA-020"></a>
**`SPS-MEDIA-020`** — The address policy MUST be derived from the IANA special-purpose address
registries' *not globally reachable* column, not from a hand-written list of private ranges.

Every element of `SPS-MEDIA-019` closes a specific bypass, and leaving one out defeats the rest.
Validating one address of several lets a host with two records pass on the public one and connect on
the private one; not pinning it lets the name resolve differently between check and connect; not
re-running per hop lets a public URL redirect inward. A hand-written range list is how link-local
metadata endpoints keep being reachable.

## 6. Lifecycle

<a id="SPS-MEDIA-021"></a>
**`SPS-MEDIA-021`** — Deleting a context MUST remove it from every media assignment.

<a id="SPS-MEDIA-022"></a>
**`SPS-MEDIA-022`** — A media whose assignment set becomes empty MUST be marked unreferenced from
that moment, and the mark MUST be cleared if it is assigned again.

<a id="SPS-MEDIA-023"></a>
**`SPS-MEDIA-023`** — Collection MUST NOT be immediate. An implementation MUST observe a grace
period after a media becomes unreferenced before removing its bytes.

<a id="SPS-MEDIA-024"></a>
**`SPS-MEDIA-024`** — Collection MUST delete the stored object before the registry entry.

The reason is **retryability**, not the harmlessness of the interrupted state — and getting that
backwards is easy, because the interrupted state of this order looks like the worse one.

Interrupt it and an entry survives whose object is gone. That entry is still marked unreferenced and
still past the grace period, so the next collection run finds it, deletes an object that is already
gone, and completes. The damage is bounded by one sweep interval and repairs itself.

Delete the entry first and the interruption leaves an object nothing points at — and nothing will
ever retry, because the entry that drove the sweep is what went first. That is a permanent leak, and
only reconciliation can even find it, which [`SPS-MEDIA-025`](#SPS-MEDIA-025) requires to report
rather than repair.

<a id="SPS-MEDIA-025"></a>
**`SPS-MEDIA-025`** — A reconciliation facility, where offered, MUST report divergence and MUST NOT
repair it.

Automatic repair means a route that deletes bytes on the strength of a query. The remedy is an
operator's: delete the stray object, or restore the missing one from a backup.

## 7. Named limitations

Stated so they are not discovered:

- **No range requests.** Nothing here requires them, and the reference implementation does not
  advertise them.
- **Two check-then-act races survive.** The media registry, the context registry and the byte store
  are separate systems with no shared transaction. An upload can complete against bytes a
  concurrent collection has just removed; a context can be deleted between authorizing an upload and
  writing its assignment. The second is narrowed by re-checking at the point of decision and
  answering `409` ([`SPS-CORE-014`](../core/index.md#SPS-CORE-014)), and the residual gap is one
  statement wide.
- **Nothing reconciles the graph against the registry.** Deleting a `schema:ImageObject` through the
  CRUD surface does not drop the assignment, and the bytes stay. That is the price of
  `SPS-MEDIA-005`, and an application owning both sides handles it.
- **Checksums are not re-verified.** An upload is covered by construction — the identifier is the
  digest — but nothing re-reads the bytes afterwards. Corruption at rest is the store's and the
  backup's problem.

A deployment that provides this module takes on one obligation this specification cannot discharge:
the store holds the only copy of every byte, and nothing in a pod can restore one.
