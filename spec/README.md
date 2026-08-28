# The specification

The normative text lives in this directory. **It is empty today** — the chapters are being extracted
from the reference implementation one at a time, and a chapter appears here when it is written
rather than as a stub that promises it will be.

The table below is therefore the honest state of the specification, and
[`../docs/roadmaps/spec-0.1.md`](../docs/roadmaps/spec-0.1.md) is the order the work is being done
in.

## How to read a chapter

- **RFC 2119 / RFC 8174.** Only the uppercase keywords are normative: `MUST`, `MUST NOT`, `SHOULD`,
  `SHOULD NOT`, `MAY`, and their listed synonyms. A lowercase "must" is ordinary English.
- **Every normative statement carries a requirement ID** and its own anchor, so it can be cited from
  a conformance test, an implementation note or an OpenAPI operation:

  ```
  SPS-CRUD-011      →   spec/core/lod-crud.md#SPS-CRUD-011
  ```

  IDs are permanent. They are never reused, never renumbered, and a requirement that is dropped is
  marked **withdrawn** rather than deleted — the same promise the vocabulary makes for RDF terms,
  because an ID ends up in other people's test suites the way a term ends up in other people's data.
- **Standards are named, not re-explained.** A chapter states which RFCs it profiles and specifies
  the deviations. If a behaviour follows the profiled standard exactly, the chapter is silent about
  it on purpose.
- **Prose is not normative.** The paragraphs around the requirements exist to make them readable.
  Where prose and a requirement seem to disagree, the requirement is what binds.

The authoring rules are in [`../docs/agents/spec-authoring.md`](../docs/agents/spec-authoring.md).

## Core

Every sempods implementation provides all of it. There is no opt-out and no partial core.

| Chapter | Area | Status | Source being extracted from |
|---|---|---|---|
| [`core/index.md`](core/index.md) — conformance, addressing, discovery, the error model | `CORE` | **present** | new |
| [`core/contexts.md`](core/contexts.md) — the context as the permission boundary, the `_system/contexts` namespace, lifecycle and discovery | `CTX` | **present** | `docs/auth/authorization.md` |
| [`core/grants.md`](core/grants.md) — `#read` / `#write` / `#manage`, resolution, delegation, revocation, the `#manage` subtree rule | `GRANT` | **present** | `docs/auth/authorization.md` |
| [`core/auth.md`](core/auth.md) — OAuth 2.1, PKCE, the three client-identity shapes, consent, refresh rotation, discovery | `AUTH` | **present** | `docs/auth/oauth.md`, `service-clients.md` |
| [`core/lod-crud.md`](core/lod-crud.md) — the LOD layer and the system layer, `?context=`, base64url addressing, slots and edges | `CRUD` | **present** | `docs/lod-crud/` |
| [`core/sparql.md`](core/sparql.md) — the read-only query surface and the server-enforced sandbox | `SPARQL` | **present** | **new writing** — was scattered across three documents |
| [`core/find.md`](core/find.md) — retrieval: the request, the sandbox, the response graph | `FIND` | **present** | **new writing** — existed only as a concept |

Two of these were new writing rather than a move. `sparql` existed only as fragments across three
files in the reference implementation — whose LOD chapter deferred to a "SPARQL surface" document
that was never written — and `find` existed only as a concept, which mixes what is built with what
is planned. Both chapters therefore carry more than any single source did, and both were checked
against the implementation rather than against the prose.

## Modules

Optional, versioned separately from core and from each other. An implementation **advertises** which
modules it provides; a module is all-or-nothing, because a client that has to probe which half it
got has no contract.

| Module | Area | Status | Source being extracted from |
|---|---|---|---|
| [`modules/oidc.md`](modules/oidc.md) — the OIDC bridge: identity assertions, how a pod obtains one, federation | `OIDC` | **present** | `docs/auth/identity.md`, split |
| [`modules/media.md`](modules/media.md) — pod-owned binaries: content addressing, the context-bound registry, delivery, lifecycle | `MEDIA` | **present** | `docs/media.md` |
| [`modules/mcp.md`](modules/mcp.md) — the per-pod MCP endpoint, authentication modes, the tool catalogue, closed schemas | `MCP` | **present** | `docs/mcp/endpoint.md`, `tools.md`, `authentication.md` |

## OpenAPI

`openapi/` will hold one hand-written OpenAPI 3.1 description per core chapter and per module.
Hand-written and part of the contract, not generated from any implementation: a generated
description specifies whatever the reference implementation happens to do, and an implementer in
another language would read one implementation's choices as obligations.

What OpenAPI cannot carry is the reason it is not the specification on its own: grant resolution,
the context sandbox, the SPARQL sandbox — the behaviour that decides what a request is allowed to
see. That lives in the chapters.

## Vocabulary

[`../vocabulary/`](../vocabulary/) holds the RDF terms published under
`https://schema.sempods.org/`, together with the stability guarantees they carry — the strongest
promise this project makes: an IRI never changes, a meaning never narrows, and a retired term is
deprecated for at least twelve months rather than deleted.

It lives here rather than with an implementation because the terms are normative and versioned with
the specification, and because a term ends up inside other people's stored data — which is the same
reason a requirement identifier is permanent.

## Conformance

`conformance/` will hold the suite that turns a requirement ID from a claim into a check, and it is
what the reserved terms **"sempods conformant"** and **"sempods certified"** are gated on. Neither
exists, so nobody can pass it and the terms say nothing today. Write "implements the sempods
specification" and document your deviations.
