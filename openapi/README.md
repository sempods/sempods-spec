# OpenAPI descriptions

Hand-written, and part of the contract. Not generated from any implementation.

**Where a description and a chapter disagree, the chapter wins.** A requirement carries an
identifier somebody can cite; a description realises requirements and says which in
`x-sps-requirements`. So a conflict is drift in the description, and the seven known ones are
listed in [`../docs/roadmaps/spec-0.1.md`](../docs/roadmaps/spec-0.1.md) rather than left for a
reader to find — none of them changes an obligation, and a client that follows the chapter is
conformant while one of them stands.

That was a decision rather than a convenience. A generated description specifies whatever one
implementation happens to do, and an implementer in another language reads its choices as
obligations — the shape of its error bodies, the order of its parameters, an endpoint it grew for
its own convenience. Hand-written keeps the description saying what an implementation *must* do.

The cost of hand-writing is that nothing tells you when it drifts. Two things are done about that:

- **Every operation names the requirements it realises**, in `x-sps-requirements`. A citation
  pointing at an identifier no chapter defines fails CI
  ([`../.github/scripts/check-requirements.py`](../.github/scripts/check-requirements.py)).
- **The set of files is derived from the chapters, not listed.** Every module chapter must have a
  description and every description must have a chapter, so deleting one — or adding a module
  without one — fails. A list of expected filenames would be a thing to forget the day a module is
  added, and the check would then enforce yesterday's shape.
- **Agreement with a running implementation is the conformance suite's job**, not a lint here. That
  suite does not exist yet; until it does, these files are checked against the chapters and not
  against any server.

## The files

| File | Covers |
|---|---|
| [`sempods-core.yaml`](sempods-core.yaml) | the whole core HTTP surface — conformance, contexts, resources, slots, query, retrieval, auth |
| [`module-context-management.yaml`](module-context-management.yaml) | the context-management module — creating and deleting contexts |
| [`module-media.yaml`](module-media.yaml) | the media module |
| [`module-mcp.yaml`](module-mcp.yaml) | the MCP module |
| [`module-oidc.yaml`](module-oidc.yaml) | the OIDC module — one route |

**One file for the whole of core**, rather than one per chapter as first planned. The chapters share
the context rule, the canonical representation, the conditional-write semantics and the error model;
split into five documents, a reader has to merge them before anything is usable, and the shared
components have to be duplicated or referenced across files. A module is different — it is optional,
so its description has to be separable, and it is.

**The OIDC file describes one route**, and that is the whole of what the module adds to a *pod*.
Everything else it specifies happens at an identity service, as standard OpenID Connect; restating
that here would be the re-explanation the writing rules rule out, so it is named and linked instead.
A file for one route still earns its place — leaving it out meant a required route that no
description mentioned, which is worse than a short document.

## What these files cannot say

The part that decides what a request may see: grant resolution, the context sandbox on every read
and write, and the SPARQL sandbox on every query. No schema language expresses them, which is why
the chapters are the specification and these are a view of it.

Two consequences visible in the files themselves. A path parameter like `resourcePath` may contain
slashes, which OpenAPI path templating has no way to express — tooling will render it as one
segment. And a `404` frequently means *does not exist, or you may not see that it does*, which is a
security property rather than a description of the resource.
