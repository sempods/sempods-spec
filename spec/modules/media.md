# Module: Media

**Optional.** Everything in this chapter binds only an implementation that advertises the module IRI
`https://schema.sempods.org/module/media` at the conformance endpoint
([`SPS-CORE-005`](../core/index.md#SPS-CORE-005)). A pod holds RDF; only a deployment that means to
hold binaries provides this.

**Status: descriptive.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

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
**`SPS-MEDIA-004`** — Content addressing MUST deduplicate within a pod and MUST NOT deduplicate
across pods.

Sharing one stored object between two pods makes one pod's deletion depend on the other's, which is
a tenancy boundary crossed for a storage saving.

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

<a id="SPS-MEDIA-013"></a>
**`SPS-MEDIA-013`** — The content URL MUST always be `{pod}/_system/media/{id}/content`.

This is the load-bearing property of the module. A deployment that later serves bytes from a CDN or
a signed storage URL changes what the server *answers* there, never what the stored data *says* — so
it is an optimisation rather than a migration of everyone's `schema:contentUrl` values.

<a id="SPS-MEDIA-014"></a>
**`SPS-MEDIA-014`** — The entity tag on content MUST be the content hash, and `If-None-Match` MUST
be honoured.

It is a strong validator by construction rather than by convention: the identifier already is the
digest.

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

That order is the one whose interrupted state is harmless. An object with no entry is inert and
discoverable by a reconciliation report; an entry with no object is a media that reads as present
and fails on access.

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
