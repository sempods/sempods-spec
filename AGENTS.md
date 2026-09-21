# AGENTS.md — sempods-spec

Scope: project-level guidance for the whole repository. This is the **specification** repository;
the Kotlin/JVM reference implementation lives in
[sempods-kotlin](https://github.com/sempods/sempods-kotlin) and has its own `AGENTS.md`, which does
not govern anything here.

No module carries its own `AGENTS.md` today. That is the normal case, not a gap to be filled.

## Start here

- [`docs/agents/ai-instructions.md`](docs/agents/ai-instructions.md) — how instructions are
  discovered and which file wins where two disagree. Every agent frontend routes through it.
- [`docs/agents/documentation-strategy.md`](docs/agents/documentation-strategy.md) — document ownership and the
  rules for when *not* to write something. Read it before touching any `*.md`, which in this repository means before touching anything at all.
- [`docs/agents/spec-authoring.md`](docs/agents/spec-authoring.md) — how a normative statement is
  written: RFC 2119 keywords, the requirement-ID scheme, how a requirement is withdrawn.

`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` and `.cursor/rules/` are compatibility
pointers back to this file — Codex and opencode read it directly. Decision and publication rules
are in `GOVERNANCE.md`; work rules are here or under `docs/agents/`; a pointer that grows rules of its own is a pointer that drifts.

## What decides here

**This specification decides. An implementation that disagrees with it is the bug**, the reference
implementation included. Assuming the code decides is the most likely way to damage this
repository, which is why this stands before the mission.

An identifier may still be deleted, renumbered, or come to mean something else within the window
[`GOVERNANCE.md`](GOVERNANCE.md) defines.

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
- **Requirement ID**: `SPS-<AREA>-<NNN>`, the handle on one normative statement — permanent from
  the `0.1` tag, and until then still deletable and renumberable under the window
  [`GOVERNANCE.md`](GOVERNANCE.md) opens.

## Non-negotiable invariants

These bind the current specification, not only implementations of it. An explicit maintainer
request may open a reassessment as a **non-normative proposal** identifying the affected invariants and
replacement guarantees. Merging that proposal does not change the current contract. Adoption
requires a normative pull request under [GOVERNANCE.md](GOVERNANCE.md#how-a-change-is-made), updating
the affected requirements, these invariants and the corresponding contract views together.

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
- **Modules**: `context-management`, `oidc`, `media`, `mcp`.
- OpenAPI is **not** a module. It is a view: one description for core, and one per module that adds
  an HTTP surface of its own. Not one per chapter — the core chapters share the context rule, the
  canonical representation, the conditional-write semantics and the error model, and splitting them
  would duplicate those components across files a reader then has to merge. See
  [`openapi/README.md`](openapi/README.md).

"Optional" is only real if a client can discover it, so conformance discovery is part of core, not a
nicety. Module identity is an IRI under `https://schema.sempods.org/`, which the vocabulary's scope
already anticipates ("conformance markers").

## Documentation

[`docs/agents/documentation-strategy.md`](docs/agents/documentation-strategy.md) is the authority.
The short version:

- **Document ownership and lifecycle** distinguish normative text, the vision, proposals and
  maintained guides. Issues own planning; milestones track agreed release conditions.
- Read [the vision](docs/vision.md#what-belongs-in-the-contract) for requirement selection; follow
  [spec authoring](docs/agents/spec-authoring.md) to apply it.
- **No history and no decision log.** Keep only the reasoning a future reader needs in order not to
  undo the decision; the rest is what commit messages are for.
- **Every document is reachable through at least one `AGENTS.md` pointer.**

## Documentation map

Every document in this repository, and what it answers. A document that is not reachable from here
will not be read.

Front door and governance:

- [`README.md`](README.md) — what this repository is, the three-repository table, the licence split
- [`GOVERNANCE.md`](GOVERNANCE.md) — the independent version line, module versions, what the tag
  changes and what it no longer does, how a change is made and who decides
- [`NOTICE`](NOTICE) — the licence summary and the trademark position, including the two reserved
  conformance terms that mean nothing until the suite exists
- [`docs/brand/`](docs/brand/) — canonical project logo assets, attribution and downstream copy
  rules

The specification:

- [`requirements.json`](requirements.json) — the generated machine-readable index of every
  requirement, which the reference implementation vendors so it can check its own citations without
  a network call. Regenerated with `--write-index`; CI fails if the committed copy has drifted
- [`openapi/README.md`](openapi/README.md) — the hand-written OpenAPI descriptions, why they are
  hand-written, and what they structurally cannot say
- [`vocabulary/README.md`](vocabulary/README.md) — the RDF terms published under
  `https://schema.sempods.org/` and the stability guarantees they carry. Normative, and versioned
  with the specification rather than with any implementation
- [`spec/README.md`](spec/README.md) — how to read a chapter, the requirement-identifier scheme, and
  the chapter tables. Six core chapters and four modules are present; the tables say which source
  each was extracted from, and are what a visitor reads first
- [`spec/core/`](spec/core/) and [`spec/modules/`](spec/modules/) — the normative text itself
- [`examples/README.md`](examples/README.md) — worked access-control fixtures and their format;
  [repository checks](docs/guides/repository-checks.md) explains what their execution establishes

The rendered site — [`site/`](site/):

- [`site/index.md`](site/index.md) — the landing page at `spec.sempods.org`. Published content, and
  the hand-written entry page alongside the generated revision page: it says what a pod is for a
  reader who arrived without knowing, and links revisions, releases, proposals and check evidence. Its links
  are written against the staged layout and resolve nowhere in the repository, which is why lychee
  skips this directory and the Pages build checks them instead.
- [`site/build.py`](site/build.py) — stages the specification and renders it. Names the demo pod the
  try-it page talks to, in the one place it is named, and refuses to build a page whose OpenAPI
  descriptions would point somewhere else. Its `STAGED` constant is the list of what the site
  publishes — `spec/`, `vocabulary/`, `GOVERNANCE.md` and `docs/vision.md`, and nothing else from
  `docs/` or `examples/`. The builder also generates a revision page and build metadata
- [`docs/guides/specification-revisions.md`](docs/guides/specification-revisions.md) — development, publication and consistent artifact consumption
- [`docs/agents/publish-specification.md`](docs/agents/publish-specification.md) — preparing and verifying an authorized publication
- [`site/test_build.py`](site/test_build.py) — regression checks for links across source and staged layouts
- [`site/api/index.html`](site/api/index.html) — the try-it page. Outside the documentation theme on
  purpose; the Scalar bundle is pinned with an integrity hash.

Agent instructions — [`docs/agents/`](docs/agents/):

- [`ai-instructions.md`](docs/agents/ai-instructions.md) — the hub: how instructions are discovered,
  the tool directory, the self-check
- [`documentation-strategy.md`](docs/agents/documentation-strategy.md) — document ownership, issue planning and
  the writing rules
- [`spec-authoring.md`](docs/agents/spec-authoring.md) — how a normative statement is formed,
  identified, numbered and withdrawn
- [`documentation-sync.md`](docs/agents/documentation-sync.md) — the procedure run before a commit
- [`issue-work.md`](docs/agents/issue-work.md) — scope, bounded delivery and completion evidence
- [`docs/guides/repository-checks.md`](docs/guides/repository-checks.md) — check commands, setup and
  evidence boundaries
- [`docs/proposals/README.md`](docs/proposals/README.md) — writing and disposition of proposals

Vision, proposals and fixture explanation:

- [Vision](docs/vision.md) — canonical direction and requirement-selection test; read before
  proposing a requirement. The site publishes it as informative guidance.
- [Pod and service discovery](docs/proposals/pod-discovery.md) — proposed entry link, conformance
  description and service bindings under #96, with external endpoints and stable local reserved paths
- [Authorized data access](docs/proposals/data-access.md) — proposed smaller core and optional
  Context contract, operation cases, mirroring boundaries and requirement impact; adoption belongs to #68
- [Context registry](docs/proposals/context-contract.md) — remaining optional-module, default-access,
  bootstrap and lifecycle recommendations under #69/#68; #92/PR #93 owns the separate RDF registry
  adoption, based on the completed #90 recommendation
- [Access control](docs/proposals/access-control.md) — proposed policy-independent guarantees,
  delegation, revocation, query equivalence, mutation boundaries and sharing design
- [Context registry representations](docs/guides/context-registry.md) — RDF examples and HTTP
  verification cases; the representation checker validates shapes and RDF, not a running server
- [ACP fixture guide](docs/guides/acp-fixtures.md) — supplied model assumptions and what the examples
  establish; independent of an implementation's storage or management API
- [Authorization implementation proposal support](docs/proposals/authorization-implementation/README.md)
  — candidate ACP and native-state designs retained under the temporary #64 disposition exception

Not in this repository, and deliberately: the licensing, DCO, AI-assistance and conduct rules that
hold across the whole project live once in the organisation's `.github` repository and are inherited
here rather than copied.

## Working rules

- **Requirement IDs are permanent.** Never renumber, never reassign, never delete. Withdraw instead.
  One exception, live today: a requirement may be deleted and identifiers renumbered, for a
  statement that should never have been written or one a later requirement has swallowed whole,
  rather than one that is merely in the way.
  [`GOVERNANCE.md`](GOVERNANCE.md) owns that rule and names both events that end it — do not restate
  the deadline here or anywhere else, because a deadline copied into five files is a deadline four
  of them will get wrong. The checker enforces the half it can observe.
- **Every sempods-authored obligation has a requirement ID.** Explicitly incorporated standards
  retain their own identifiers; informative references create no obligations. Follow
  [spec authoring](docs/agents/spec-authoring.md#standards-incorporation).
- **No empty placeholder files.** A chapter appears when it is written; until then it is a row with
  a status in [`spec/README.md`](spec/README.md). A directory of stubs is documentation debt with a
  progress bar drawn on it.
- Be conservative with backward-incompatible changes, and never make one silently.

## Before you commit

1. Run the [repository checks](docs/guides/repository-checks.md#before-requesting-review), including
   the base-ref comparison and full site render. That guide owns setup, commands and evidence limits.
2. Run [documentation-sync](docs/agents/documentation-sync.md) for this PR's diff. Record checks,
   affected documentation or a specific no-change reason, and remaining acceptance in the applicable
   work record under [Issue planning](docs/agents/documentation-strategy.md#issue-planning).
3. `git commit -s`. The DCO workflow fails the pull request without a `Signed-off-by` line. Work
   done with an AI assistant also carries `Co-Authored-By` for the model, and it is the human who
   signs off who is the author.
4. Commit messages are **full imperative sentences in plain English**, not Conventional Commits —
   "Say what a context is before saying who may read one", not `docs: …`. The subject names the
   change directly, in the fewest words that stay correct — writing rule 3 in
   [`docs/agents/documentation-strategy.md`](docs/agents/documentation-strategy.md). The body
   explains what was wrong and why the fix has the shape it does.

## What this repository deliberately does not have

**No build system for the specification.** No Gradle, no npm, no formatter, no linter. Markdown is
written by hand, and a chapter is a file somebody wrote. Gradle arrives with the conformance suite
and not before — a build file that exists to run nothing is a dependency to maintain for no return.

`site/` is the exception and stays one: it renders the published site and has a locked dependency
tree of its own. Nothing under `spec/` depends on it, and the specification is complete without it.

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
