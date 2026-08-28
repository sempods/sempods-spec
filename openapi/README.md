# OpenAPI descriptions

Hand-written, and part of the contract. Not generated from any implementation.

That was a decision rather than a convenience. A generated description specifies whatever one
implementation happens to do, and an implementer in another language reads its choices as
obligations — the shape of its error bodies, the order of its parameters, an endpoint it grew for
its own convenience. Hand-written keeps the description saying what an implementation *must* do.

The cost of hand-writing is that nothing tells you when it drifts. Two things are done about that:

- **Every operation names the requirements it realises**, in `x-sps-requirements`. A citation
  pointing at an identifier no chapter defines fails CI
  ([`../.github/scripts/check-requirements.py`](../.github/scripts/check-requirements.py)).
- **Agreement with a running implementation is the conformance suite's job**, not a lint here. That
  suite does not exist yet; until it does, these files are checked against the chapters and not
  against any server.

## The files

| File | Covers |
|---|---|
| [`sempods-core.yaml`](sempods-core.yaml) | the whole core HTTP surface — conformance, contexts, resources, slots, query, retrieval, auth |
| [`module-media.yaml`](module-media.yaml) | the media module |
| [`module-mcp.yaml`](module-mcp.yaml) | the MCP module |

**One file for the whole of core**, rather than one per chapter as first planned. The chapters share
the context rule, the canonical representation, the conditional-write semantics and the error model;
split into five documents, a reader has to merge them before anything is usable, and the shared
components have to be duplicated or referenced across files. A module is different — it is optional,
so its description has to be separable, and it is.

There is **no file for the OIDC module**. Its pod-side surface is one callback route, and everything
else it specifies is standard OpenID Connect at an identity service that is not the pod. A
description restating OIDC would be the re-explanation the writing rules rule out.

## What these files cannot say

The part that decides what a request may see: grant resolution, the context sandbox on every read
and write, and the SPARQL sandbox on every query. No schema language expresses them, which is why
the chapters are the specification and these are a view of it.

Two consequences visible in the files themselves. A path parameter like `resourcePath` may contain
slashes, which OpenAPI path templating has no way to express — tooling will render it as one
segment. And a `404` frequently means *does not exist, or you may not see that it does*, which is a
security property rather than a description of the resource.
