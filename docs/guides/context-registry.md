# Context registry representations

This informative guide follows the [Context registry contract](../../spec/core/contexts.md#SPS-CTX-031)
at the same repository revision. It illustrates RDF representation and HTTP verification
inputs; it is not a report of a running server passing these cases. The
[representation checker](../../.github/scripts/check-context-registry.py) validates the JSON-LD
examples against the actual OpenAPI schemas, their RDF meaning and selected invalid payloads.
It does not execute authorization, caching or lifecycle operations.

## A description and its caller's catalogue

For a private Context named Tasks, a visible registry GET can return this canonical JSON-LD.
The registry's public setting and metadata describe the Context independently of its contents.

```json
{
  "@id": "https://example.org/alice/_system/contexts/tasks",
  "@type": [
    "http://www.w3.org/ns/sparql-service-description#NamedGraph"
  ],
  "http://www.w3.org/ns/sparql-service-description#name": [
    {
      "@id": "https://example.org/alice/_system/contexts/tasks"
    }
  ],
  "http://www.w3.org/2000/01/rdf-schema#label": [
    {
      "@value": "Tasks"
    }
  ],
  "https://schema.sempods.org/public": [
    {
      "@value": false
    }
  ],
  "http://www.w3.org/2000/01/rdf-schema#seeAlso": [
    {
      "@id": "https://example.org/alice/_system/resources/aHR0cHM6Ly9leGFtcGxlLm9yZy9hbGljZS9fc3lzdGVtL2NvbnRleHRzL3Rhc2tz"
    }
  ]
}
```

A caller with write permission has both read and write in the current contract. Its catalogue
uses direct IRI relationships, without embedding descriptions or composite permission strings:

```json
{
  "@id": "https://example.org/alice/_system/contexts",
  "@type": [
    "http://www.w3.org/ns/sparql-service-description#GraphCollection"
  ],
  "http://www.w3.org/ns/sparql-service-description#namedGraph": [
    {
      "@id": "https://example.org/alice/_system/contexts/tasks"
    }
  ],
  "https://schema.sempods.org/readableContext": [
    {
      "@id": "https://example.org/alice/_system/contexts/tasks"
    }
  ],
  "https://schema.sempods.org/writableContext": [
    {
      "@id": "https://example.org/alice/_system/contexts/tasks"
    }
  ]
}
```

A caller seeing no Contexts still receives an RDF collection:

```json
{
  "@id": "https://example.org/alice/_system/contexts",
  "@type": [
    "http://www.w3.org/ns/sparql-service-description#GraphCollection"
  ]
}
```

N-Quads carries these registry statements in the default graph. Graph names inside the description
are RDF objects; they do not place registry facts in the Context's data graph. A client may query
separately retained catalogue and description snapshots locally to obtain writable Contexts and
optional labels. Ordinary data asserting the same access predicates is not a registry snapshot.

## HTTP cases for implementation validation

Use a registered C, its catalogue L, and an absent X. Policies explicitly supply the stated caller
permissions. Credentials and requests are valid except where the row says otherwise. These cases
retain the current Context membership, grant implications and lifecycle contract.

| Setup/request | Required result or invariant |
|---|---|
| Read, write and manage callers GET C | Same registry description, no caller rights; catalogue respectively includes read, read/write and read/write/manage links. |
| Anonymous caller; C public | Catalogue includes C as readable; description is visible. Supplied invalid credentials give `401` with a Bearer challenge, even when data is public; RFC 6750 recommends `error="invalid_token"` for an invalid or expired token. |
| Caller cannot see C; GET C and absent X | Indistinguishable `404`, including conditional requests, links and validators. |
| GET C/L without Accept, with JSON-LD, or with application/json | `200` canonical JSON-LD; the JSON alias does not select a legacy DTO. |
| GET C/L with N-Quads | Same registry RDF in the default graph. |
| Authorized GET with an unsatisfiable Accept | `406`. |
| Authorized unchanged GET with matching If-None-Match | `304` without a body; current authorization still applies. |
| Read revoked after a description/tag was fetched | Conditional GET is `404`, not `304`. A cache cannot serve the previously visible response without current authorization. |
| Write revoked, read retained; conditional catalogue GET | Changed rights representation and tag, not `304` for its old tag. |
| A registry error is received before credentials, rights or Accept change; retry after the change | A stored `401`, `404` or `406` cannot be reused across authorization contexts or without current authorization and representation freshness. Apply the same isolation to creation errors. |
| GET absent X returns `404`; X is then created and becomes visible | A cached absence cannot hide the newly visible Context. Storage/revalidation preserves current authorization and freshness; `no-store` is one sufficient strategy. |
| Write ordinary RDF about C, including sps:public or a catalogue rights predicate | Ordinary data changes; registry RDF, registry tags and authority are unchanged. Following seeAlso still performs an independently authorized data read. |
| Manager creates absent C with ContextCreate JSON, or no body | `201` with RDF description and private defaults where public is omitted. JSON input remains accepted. |
| Same creation request for existing C, including a different label | `200` with its unchanged registry description. No metadata update is implied. |
| Manager's creation request has an unsatisfiable Accept | `406`, no new Context. Authentication and management checks still apply. |
| Creation request with missing versus rejected bearer token | Same `401` response with `invalid_token` under SPS-CORE-015; public-read access does not authorize creation. |
| Authenticated non-manager tries PUT/DELETE of C or X | Current uniform `403`; this RDF migration adds no authority. |
| Manager deletes its only visible C, with or without other hidden Contexts | `204` in both cases. C, its statements, grants and media assignments are removed; other Contexts remain. |
| Owner deletes the pod's last C | `204`; the registry is empty. An authorized catalogue GET returns `200` with no Context entries. |
| Owner creates C in an empty pod providing context-management | `201`; this also works after deleting the last Context. |
| Pod does not provide context-management | At least one registered Context is provided outside this HTTP interface (SPS-CTX-028). |

Normative sources: [`SPS-CTX-031`](../../spec/core/contexts.md#SPS-CTX-031)–
[`SPS-CTX-036`](../../spec/core/contexts.md#SPS-CTX-036),
[`SPS-CTX-037`](../../spec/modules/context-management.md#SPS-CTX-037), and the existing
[grant](../../spec/core/grants.md), [lifecycle](../../spec/modules/context-management.md) and
[media cleanup](../../spec/modules/media.md#SPS-MEDIA-021) contracts.
Server/client verification of the RDF registry belongs to
[Kotlin #180](https://github.com/sempods/sempods-kotlin/issues/180); empty-registry lifecycle and
client contract synchronization belong to [Kotlin #186](https://github.com/sempods/sempods-kotlin/issues/186).
