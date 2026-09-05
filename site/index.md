# The sempods specification

A **pod** is a person's or an organisation's own store of linked data: they hold it, they say who
may read and write which part of it, and applications talk to it over HTTP. This site is the
contract such a pod implements. It is written so that somebody who has never seen the reference
implementation can build a conformant pod in a language of their choosing — and can tell whether
they succeeded.

The point is not a new protocol stack. sempods profiles and composes standards that already exist:
HTTP resources, RDF and named graphs, JSON-LD, SPARQL, OAuth/OIDC and MCP. The specification adds
the pod contract between them: one base URL, one context per statement, server-resolved grants,
sandboxed reads and writes, and an agent surface that uses the same rules as every other client.

!!! warning "This specification is not yet binding"

    This text decides: an implementation that disagrees with it is the bug. What it is not yet is
    **fixed** — until the `0.1` release a requirement may still be deleted, renumbered, or change
    meaning, so nothing here is safe to cite from a conformance report.
    [Governance](GOVERNANCE.md) says what the tag changes and when it happens.

## Core and modules

**Core is not optional.** [Contexts](spec/core/contexts.md), [grants](spec/core/grants.md),
[auth](spec/core/auth.md), [CRUD](spec/core/lod-crud.md), [SPARQL](spec/core/sparql.md) and
[find](spec/core/find.md) are what makes a pod a pod. Something implementing a subset of them is
something else, and should not use the name.

**Modules are optional and versioned separately.**
[Context management](spec/modules/context-management.md), [OIDC](spec/modules/oidc.md),
[media](spec/modules/media.md) and [MCP](spec/modules/mcp.md) each add a surface a pod may choose
to offer. A pod may implement core `0.1` alongside media `0.2`.

"Optional" only means something if a client can ask, so a pod announces what it implements at
`GET {pod}/_system/conformance` — see [the core chapter](spec/core/index.md).

The chapter map, the requirement scheme and what an identifier promises are on
[the specification page](spec/README.md).

## Try it

[**The HTTP surface**](api/index.html) is described in OpenAPI and rendered with a client you can
send requests from. Anonymous reads and SPARQL need no token, so the read surface can be explored
without registering anything.

## Elsewhere

- [**Vocabulary**](vocabulary/README.md) — the `sps:` terms, and what stability they promise.
- [**sempods-kotlin**](https://github.com/sempods/sempods-kotlin) — the reference implementation.
  It is one implementation of this contract, not the definition of it.
- [**The repository**](https://github.com/sempods/sempods-spec) — where the text is edited, and
  where a disagreement with it is filed.
