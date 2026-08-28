# sempods specification

**The contract a semantic pod implements.** A pod is a data space you host, addressed over HTTP,
holding structured linked data: apps and agents come to your data instead of keeping copies of it,
and you decide who may read or write what.

This repository holds the specification of that model. It is written to be implementable by
somebody who has never read the reference implementation — in any language, on any store.

## Where am I?

| | |
|---|---|
| **sempods-spec** (here) | the contract: what an implementation MUST do |
| [**sempods-kotlin**](https://github.com/sempods/sempods-kotlin) | the reference implementation for the JVM — pod server, identity service, hosted MCP, client libraries |
| **www.sempods.org** | the project website — not published yet, so this table carries no link to it |

This is the only text duplicated across the three repositories. Everything else lives in exactly
one of them and is linked from the others.

## Status

**Pre-`0.1`, and the specification was extracted rather than invented.** All six core chapters and
all three modules are written — 297 requirements — together with hand-written OpenAPI descriptions
of the HTTP surface. What is not done is the `0.1` release itself, the conformance suite, and
removing the second copy of this material from the reference implementation.

Until the `0.1` tag the reference implementation is the source of truth; from `0.1` on that reverses
and this repository is. [`GOVERNANCE.md`](GOVERNANCE.md) states the switch, and why it is a dated
event rather than a mood.

What that means concretely: **you can implement against this repository, and you cannot yet prove
you did.** The requirements are stable enough to build against and their identifiers are permanent;
what does not exist is the suite that would check an implementation against them.
[`docs/roadmaps/spec-0.1.md`](docs/roadmaps/spec-0.1.md) is what remains, and in which order.

## What a specification is here

Three artefacts, one anchor:

- **Normative text** under `spec/` — Markdown, RFC 2119 keywords, one stable requirement ID per
  normative statement. This *is* the specification.
- **An OpenAPI 3.1 description** per chapter, hand-written and part of the contract. It carries the
  shapes, parameters and status codes; it cannot carry grant resolution, the context sandbox or the
  SPARQL sandbox, which is why it is not the specification on its own.
- **A conformance suite**, later, which is what turns a requirement ID from a claim into a check.

The requirement IDs are the load-bearing part: a conformance test, a note in the reference
implementation and an OpenAPI operation all point at `SPS-CRUD-011` rather than at a file and a
heading. Chapters may then be split, renamed or moved without breaking anything that cites them.
[`spec/README.md`](spec/README.md) has the scheme and the chapter map.

Project brand assets live under [`docs/brand/`](docs/brand/). They are not part of the normative
specification, but this repository is their source of truth so the website, organisation profile
and applications all copy the same files.

## Core and modules

**Core** is what every sempods implementation must provide: contexts, grants, authorization,
LOD CRUD, SPARQL, find. There is no opt-out and no partial core.

**Modules** are optional, versioned separately, and named: OIDC, media, MCP. Optional only means
something if a client can find out, so an implementation advertises what it implements at a
discovery endpoint rather than in a README. The mechanism is part of the core chapter.

## Licence

- [`LICENSE`](LICENSE) — **CC BY 4.0**, for the specification text and the RDF vocabulary. Using
  the terms in your own data requires no licence, no attribution and no permission.
- [`LICENSE-CODE`](LICENSE-CODE) — **Apache 2.0**, for the conformance suite and tooling once they
  exist.
- [`NOTICE`](NOTICE) — the summary, and the trademark position: Apache-2.0 §6 grants no rights in
  the name, and what you may call your own work is set out in the reference implementation's
  `TRADEMARKS.md`.

Two terms are reserved and mean nothing yet: **"sempods conformant"** and **"sempods certified"**
require a written licence granted on passing the conformance suite, which does not exist. Write
"implements the sempods specification" and document your deviations.

## Contributing

A specification change moves slower than an implementation change and needs a written rationale,
because other implementations depend on it. [`GOVERNANCE.md`](GOVERNANCE.md) says how one is
proposed, who decides, and how versions work.

Everything that holds across the whole project — the Developer Certificate of Origin (`git commit
-s`, and deliberately no CLA), the licensing of contributions, the AI-assistance policy, the code of
conduct — lives once in the organisation's
[shared contributing guide](https://github.com/sempods/.github/blob/main/CONTRIBUTING.md) and is
inherited here rather than copied.

## Security

A vulnerability in the *specification* is a rule that cannot be implemented safely — a flow that
leaks context topology, an authorization check that is underspecified. Report it privately through
the repository's Security tab, or to **hello@sempods.org**, never in a public issue.

A vulnerability in the reference implementation belongs in
[sempods-kotlin](https://github.com/sempods/sempods-kotlin/security/policy) instead. The policy
itself is the organisation-wide
[`SECURITY.md`](https://github.com/sempods/.github/blob/main/SECURITY.md).
