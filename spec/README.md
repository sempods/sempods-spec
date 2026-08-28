# The specification

The normative text lives in this directory: six core chapters and three modules, 313 requirements.
A chapter appears here when it is written rather than as a stub that promises it will be, so the
tables below are the state of the specification rather than a plan for it.

[the 0.1 roadmap](https://github.com/sempods/sempods-spec/blob/main/docs/roadmaps/spec-0.1.md) is what remains before the `0.1`
release.

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

The authoring rules are in [`../docs/agents/spec-authoring.md`](https://github.com/sempods/sempods-spec/blob/main/docs/agents/spec-authoring.md).

## The requirement index

[`../requirements.json`](https://github.com/sempods/sempods-spec/blob/main/requirements.json) is the machine-readable form: every identifier, the
part it belongs to, the chapter it lives in, its first sentence, and whether it is withdrawn. A
withdrawn one also carries its withdrawal note and, where it has a successor, that identifier —
because the obligation is what makes a permanent identifier recognisable, and the withdrawal
preamble sits in front of it. It is
generated from the chapters and committed, and CI fails if the committed copy has drifted.

**A version per part, not one for the file.** Core and each module version independently
([`SPS-CORE-005`](core/index.md#SPS-CORE-005)), so `versions` carries all of them and every
requirement names its `part` rather than repeating a number that could then disagree with it.
`specVersion` remains core's, because that is what a consumer pins to say which specification it
implements. The module set comes from the chapters in [`modules/`](https://github.com/sempods/sempods-spec/tree/main/spec/modules) rather than from a
list, and CI fails if a module has no version or a version has no module — two registries that must
agree are two registries somebody keeps in step by remembering to. They are all equal today, which is exactly why the shape is settled now: adding the
field after somebody has vendored the file is a change every consumer has to absorb.

It exists for the consumer that is another repository. The reference implementation vendors it, so a
note in its code citing `SPS-GRANT-007` can be checked without a network call — and upgrading to a
newer specification arrives there as a reviewable diff rather than as a build that starts failing.

It deliberately carries no URL and no timestamp. A URL would pin a branch or a tag and the consumer
is the one who knows which it wants; a timestamp would turn every regeneration into a diff.

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

[`openapi/`](https://github.com/sempods/sempods-spec/tree/main/openapi) holds hand-written OpenAPI 3.1 descriptions — one for the whole of
core, one per module that has an HTTP surface of its own. Hand-written and part of the contract, not
generated from any implementation: a generated description specifies whatever the reference
implementation happens to do, and an implementer in another language would read one
implementation's choices as obligations.

Every operation names the requirements it realises, and a citation pointing at an identifier no
chapter defines fails CI.

What OpenAPI cannot carry is the reason it is not the specification on its own: grant resolution,
the context sandbox, the SPARQL sandbox — the behaviour that decides what a request is allowed to
see. That lives in the chapters.

## Vocabulary

[`../vocabulary/`](../vocabulary/README.md) holds the RDF terms published under
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
