# GitHub Copilot instructions

The canonical guidance is the root [`AGENTS.md`](../AGENTS.md), reached through the shared hub
[`docs/agents/ai-instructions.md`](../docs/agents/ai-instructions.md). Read both when you can follow
a link.

Copilot Chat loads this file in isolation, so the minimum is repeated below. It is a **subset** —
`AGENTS.md` is the source of truth, and this file is updated after it, never instead of it. The
registered duplication is listed in the hub under "Auto-injection constraints".

## What this repository is

The **specification** of sempods: an open standard for self-hosted "semantic pods" — a pod is an
isolated tenant holding RDF, reachable over HTTP, usable by many apps. The Kotlin/JVM reference
implementation is a different repository, `sempods/sempods-kotlin`.

There is no code here and no build system. Markdown, and later OpenAPI descriptions and a
conformance suite.

## What decides here

**This specification decides. An implementation that disagrees with it is the bug**, the reference
implementation included. Until `0.1` or the first adopter the text may still be edited, and a
requirement a chapter records as wrong binds nobody until it is repaired — `GOVERNANCE.md` is the
authority.

## Non-negotiable invariants

These bind the specification itself, not only implementations of it.

1. Every statement belongs to exactly one **context** (named graph).
2. Read sandbox: a request reads only contexts it has read rights for.
3. Write sandbox: a request writes only into contexts it has write rights for.
4. A CRUD write names its target context explicitly — there is no implicit fallback.
5. Pods are isolated by default. No cross-pod access without a spec-defined sync mechanism.
6. Prefer explicit specification plus conformance tests over clever query rewriting.

Sandboxing is enforced server-side; client-supplied `FROM` / `FROM NAMED` is never trusted. Errors
are deterministic HTTP status codes. A requirement that leaks context topology is a defect.

A **grant** is durable server-side policy on a context (`<context-iri>#read|write|manage`) and never
travels in a token. A **scope** is an OAuth scope and does.

## Requirement IDs

Every normative statement carries one, and it is permanent:

```markdown
<a id="SPS-CRUD-011"></a>
**`SPS-CRUD-011`** — A write request MUST name exactly one context …
```

- Format `SPS-<AREA>-<NNN>`. Areas: `CTX`, `GRANT`, `AUTH`, `CRUD`, `SPARQL`, `FIND` (core);
  `OIDC`, `MEDIA`, `MCP` (modules).
- **Never reused, never renumbered, never deleted.** A requirement that is no longer wanted is
  marked *withdrawn*, keeps its ID and its original text, and names its successor. IDs are cited in
  conformance suites and in other people's test reports. One dated exception, live today: until
  `0.1` is tagged a requirement may be deleted and identifiers renumbered — `GOVERNANCE.md` states
  when that ends, and it ends for good.
- RFC 2119 as clarified by RFC 8174: only the uppercase keywords bind. Name the actor — "the server
  MUST…", not "it MUST be…".
- A statement without an ID is not normative.

Full rules: [`docs/agents/spec-authoring.md`](../docs/agents/spec-authoring.md).

## Writing rules

- **Name the standard; do not re-explain it.** A chapter says which RFC it profiles and specifies
  the deviation. Restating RFC 9110 is how a specification becomes long and wrong.
- **No stub chapters.** A chapter exists when it is written; until then it is a row with a status in
  `spec/README.md`.
- **Reasoning goes in `docs/concepts/`, not into a requirement.** A requirement that carries its own
  justification cannot be told apart from the justification.
- Every behaviour change updates the chapter, the OpenAPI description, the chapter table and the
  roadmap item **in the same change**.

Full rules: [`docs/agents/documentation-strategy.md`](../docs/agents/documentation-strategy.md).

## Checks

```bash
lychee --offline --include-fragments --no-progress --exclude-path site .
```

## Commits

Full imperative sentences in plain English — **not** Conventional Commits, no `docs:` prefix. Every
commit needs `Signed-off-by` (`git commit -s`); the DCO workflow fails the pull request otherwise.
