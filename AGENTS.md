# AGENTS.md — sempods-spec

Scope: project-level guidance for the whole repository. This is the **specification** repository;
the Kotlin/JVM reference implementation lives in
[sempods-kotlin](https://github.com/sempods/sempods-kotlin) and has its own `AGENTS.md`, which does
not govern anything here.

No module carries its own `AGENTS.md` today. That is the normal case, not a gap to be filled.

## Start here

- [`docs/agents/ai-instructions.md`](docs/agents/ai-instructions.md) — how instructions are
  discovered and which file wins where two disagree. Every agent frontend routes through it.
- [`docs/agents/documentation-strategy.md`](docs/agents/documentation-strategy.md) — the five
  document types and the rules for when *not* to write something. Read it before touching any
  `*.md`, which in this repository means before touching anything at all.
- [`docs/agents/spec-authoring.md`](docs/agents/spec-authoring.md) — how a normative statement is
  written: RFC 2119 keywords, the requirement-ID scheme, how a requirement is withdrawn.

`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` and `.cursor/rules/` are compatibility
pointers back to this file — Codex and opencode read it directly. Everything canonical is here or
under `docs/agents/`; a pointer that grows rules of its own is a pointer that drifts.

## The one rule that is inverted here

In the reference implementation, the code is the source of truth and a document that disagrees with
it is a bug. **In this repository there is no code, and the specification is the source of truth: an
implementation that disagrees with it is the bug.**

With one dated exception, which is where the project stands today: **until the `0.1` release the
specification is descriptive** and is extracted from the reference implementation, so during that
window the implementation is still right and the text is still the bug.
[`GOVERNANCE.md`](GOVERNANCE.md) §"The switch from descriptive to prescriptive" is the authority,
and the window closes when `0.1` is tagged.

Getting this backwards is the single most likely way to damage this repository, which is why it is
stated before the mission.

## Project mission

sempods.org is a private, non-profit project that defines an open, copyable standard for self-hosted
"semantic pods". A pod is an isolated tenant — conceptually a separate store or account — that can
be hosted by anyone and used by multiple apps.

Core goals:

- Linked Data / JSON-LD CRUD over HTTP
- OAuth-based authorization for apps and agents
- Graph-based access control where the 4th RDF dimension (named graph) is called "Context"
- A SPARQL endpoint that enforces a context sandbox
- Future: agents and dataflows/sync between pods

This is not a business idea. Optimize for openness, clarity, and interoperability.

**This repository's own job**, narrower than the mission: state that contract so that somebody who
has never read the reference implementation can build a conformant pod in a language of their
choosing, and can prove it.

## Terminology

- **Pod**: a tenant / account boundary. Implementations may use separate repositories/stores per pod.
- **Context**: named graph / RDF context. Every statement belongs to exactly one context.
- **Grant**: a permission on a context, written `<context-iri>#read|write|manage`. Durable
  server-side policy, resolved per request — it never travels in an access token.
- **Scope**: an OAuth scope in the RFC 6749 sense — a coarse feature capability such as
  `public-read`. These *do* travel in the token.
- **Core**: the chapters every implementation must satisfy. No opt-out, no partial core.
- **Module**: an optional, separately versioned chapter set. An implementation advertises which ones
  it provides; it does not silently omit them.
- **Requirement ID**: `SPS-<AREA>-<NNN>`, the permanent handle on one normative statement.

## Non-negotiable invariants

These bind the specification itself, not only implementations of it. A proposed change that breaks
one of them is refused rather than debated.

1. Every statement always has exactly one Context (named graph).
2. Read sandbox: a request can only read contexts it has read rights for.
3. Write sandbox: a request can only write into contexts it has write rights for.
4. A CRUD write names its target context explicitly — there is no implicit fallback context.
5. Pods are isolated by default. No cross-pod access without an explicit, spec-defined sync
   mechanism.
6. Prefer explicit specification plus conformance tests over clever query rewriting.

## Security stance

- Sandboxing is enforced server-side. Client-supplied `FROM` / `FROM NAMED` is never trusted, and a
  requirement must never be written in a way that makes it trustable.
- Risky SPARQL features — `SERVICE` and federated queries above all — are forbidden or strictly
  gated.
- Errors are deterministic HTTP status codes.
- **A requirement that leaks context topology is a defect in the specification.** The pattern to
  keep: a caller who asks for a context they cannot read gets the same answer as one asking about a
  context that holds nothing.

## Core and modules

- **Core**: `contexts`, `grants`, `auth`, `lod-crud`, `sparql`, `find`.
- **Modules**: `oidc`, `media`, `mcp`.
- OpenAPI is **not** a module. It is a view: one description file per core chapter and per module.

"Optional" is only real if a client can discover it, so conformance discovery is part of core, not a
nicety. Module identity is an IRI under `https://schema.sempods.org/`, which the vocabulary's scope
already anticipates ("conformance markers").

## Documentation

[`docs/agents/documentation-strategy.md`](docs/agents/documentation-strategy.md) is the authority.
The short version:

- **Five types**, not four: the normative text under `spec/` joins `vision.md`, `concepts/`,
  `roadmaps/` and IST documents. It is prescriptive — neither IST nor SOLL.
- **Name the standard, do not re-explain it.** A chapter says which RFC it profiles and describes
  the deviation. Restating RFC 9110 is how a specification becomes unmaintainable.
- **No history and no decision log.** Keep only the reasoning a future reader needs in order not to
  undo the decision; the rest is what commit messages are for.
- **Every document is reachable through at least one `AGENTS.md` pointer.**

## Documentation map

Every document in this repository, and what it answers. A document that is not reachable from here
will not be read.

Front door and governance:

- [`README.md`](README.md) — what this repository is, the three-repository table, the licence split
- [`GOVERNANCE.md`](GOVERNANCE.md) — the independent version line, module versions, the dated switch
  from descriptive to prescriptive, how a change is made and who decides
- [`NOTICE`](NOTICE) — the licence summary and the trademark position, including the two reserved
  conformance terms that mean nothing until the suite exists
- [`docs/brand/`](docs/brand/) — canonical project logo assets, attribution and downstream copy
  rules

The specification:

- [`spec/README.md`](spec/README.md) — how to read a chapter, and the chapter table with a status
  per chapter and the source each is being extracted from. The chapters themselves do not exist yet;
  that table is the honest state of the specification and is what a visitor reads first

Agent instructions — [`docs/agents/`](docs/agents/):

- [`ai-instructions.md`](docs/agents/ai-instructions.md) — the hub: how instructions are discovered,
  the tool directory, the self-check
- [`documentation-strategy.md`](docs/agents/documentation-strategy.md) — the five document types and
  the writing rules
- [`spec-authoring.md`](docs/agents/spec-authoring.md) — how a normative statement is formed,
  identified, numbered and withdrawn
- [`documentation-sync.md`](docs/agents/documentation-sync.md) — the procedure run before a commit
- [`roadmap-lifecycle.md`](docs/agents/roadmap-lifecycle.md) — the procedure that retires a roadmap

Concepts and roadmaps:

- [`docs/concepts/README.md`](docs/concepts/README.md) — why a concept carries more weight in a
  specification repository than in an implementation, and the template. None exist yet
- [`docs/roadmaps/README.md`](docs/roadmaps/README.md) — the rules, and the template
- **Running:** [`docs/roadmaps/spec-0.1.md`](docs/roadmaps/spec-0.1.md) — the first specification
  release: core specified with requirement IDs, an OpenAPI description, the second copy in the
  reference implementation retired, and the switch at the `0.1` tag. It also states which of its
  phases gate the public announce and which may trail it

Not in this repository, and deliberately: the licensing, DCO, AI-assistance and conduct rules that
hold across the whole project live once in the organisation's `.github` repository and are inherited
here rather than copied.

## Working rules

- **Requirement IDs are permanent.** Never renumber, never reassign, never delete. Withdraw instead.
- **A normative statement without a requirement ID is not normative** — it is background, and a
  reader is entitled to treat it that way.
- **No empty placeholder files.** A chapter appears when it is written; until then it is a row with
  a status in [`spec/README.md`](spec/README.md). A directory of stubs is documentation debt with a
  progress bar drawn on it.
- Be conservative with backward-incompatible changes, and never make one silently.

## Before you commit

1. Every relative link resolves. CI runs [lychee](https://github.com/lycheeverse/lychee); locally:

   ```bash
   lychee --offline --include-fragments --no-progress .
   ```

2. Documentation is current *in this same change* — new chapters reachable from an `AGENTS.md`, the
   roadmap item ticked, requirement IDs consistent.
   [`docs/agents/documentation-sync.md`](docs/agents/documentation-sync.md) is the procedure.
3. `git commit -s`. The DCO workflow fails the pull request without a `Signed-off-by` line. Work
   done with an AI assistant also carries `Co-Authored-By` for the model, and it is the human who
   signs off who is the author.
4. Commit messages are **full imperative sentences in plain English**, not Conventional Commits —
   "Say what a context is before saying who may read one", not `docs: …`. The body explains what was
   wrong and why the fix has the shape it does.

## What this repository deliberately does not have

**No build system.** No Gradle, no npm, no formatter, no linter. Markdown is written by hand and
checked by one link checker. Gradle arrives with the conformance suite and not before — a build file
that exists to run nothing is a dependency to maintain for no return.

**No stub chapters.** See the working rules above.

**No copy of the reference implementation's documentation.** A chapter that has moved here is
*deleted* there and linked by requirement ID. Two copies means one of them is wrong, and the
maintenance cost of finding out which is the whole reason for keeping them apart.

## Naming

The product name is **sempods**, all lowercase, in prose and in identifiers — never "SemPods" and
never "Sempods". A pod is not the product: "a pod", "the pod owner" take no brand prefix.

Names that are frozen because something outside this project depends on them — environment
variables, stored collection names, the `urn:sempods:` prefix, the vocabulary IRIs — are listed in
the reference implementation's `docs/naming.md` §3. Never propose a consistency rename in that set;
it is a breaking change or a data migration, not an edit.
