# sempods specification 0.1 (SOLL)

> Progress is tracked in place. Completed items stay in this file, marked done, until the whole
> milestone is consolidated. Do not prune them individually — the roadmap documents progress, not
> only remaining work.

_Status: ☐ open · ◐ in progress · ☑ done_

**Goal.** A stranger can implement a conformant pod from this repository alone, in a language of
their choosing, and can tell whether they succeeded. Concretely: core is specified with requirement
IDs, the HTTP surface has a hand-written OpenAPI description, the reference implementation's
documentation no longer holds a second copy of any of it, and `0.1` is tagged — the point at which
this repository stops following the implementation and starts binding it.

**There is no concept file for this milestone.** The reasoning that a concept would carry is already
permanent elsewhere and would only be duplicated here:
[`../../GOVERNANCE.md`](../../GOVERNANCE.md) for versioning and the descriptive→prescriptive switch,
[`../../spec/README.md`](../../spec/README.md) for the core/module split and what a chapter is, and
[`../agents/spec-authoring.md`](../agents/spec-authoring.md) for the requirement-ID scheme. A
concept will be written for the first chapter whose *content* needs one.

---

## How the work lands

**One branch here, one pull request at the end — and the same in the reference implementation, once
this repository's first version is done.** The first attempt at the reference implementation's side
(sempods-kotlin#52) was closed for this reason: while the chapters do not exist, every sentence
there has to describe a half-state — "the specification lives at that address, but not yet", "read
it, but not for the contract" — and each of those sentences is rewritten the moment a chapter lands.
Three review rounds went into prose with a known expiry date.

So the order is: finish the normative text and the OpenAPI here, *then* rewire the reference
implementation once, against a state that is real. S7 is deliberately not started early.

## What gates the announce

The launch checklist that owns this milestone from the outside is the private go-public roadmap —
its workstream D. What it needs before the announce is **not** the whole of this file:

- **S1** complete — the repository exists, is hardened, and is legible.
- **S2** complete — the conformance model and the requirement scheme are settled, because every
  later chapter depends on them.
- **S3** far enough that the specification is not empty.
- **S6** at least for core, so the OpenAPI description the announce claims actually exists.

S4, S5, S7 and S8 may trail the announce. Saying so here is the point: without it, every phase looks
equally urgent and the announce waits on all of them.

---

## S1 — Repository, hardening, instructions

- [x] 1 — Repository `sempods/sempods-spec` created, public, described, topics set. `homepage`
      deliberately **empty** until `spec.sempods.org` serves — a link into a 404 is worse than no
      link, which the org profile already learned the hard way.
- [x] 2 — Licences: `LICENSE` CC BY 4.0 for the text and the vocabulary, `LICENSE-CODE` Apache 2.0
      for the conformance suite and tooling, `NOTICE` stating which is which and the trademark
      position.
- [x] 3 — Agent instructions carried over from the reference implementation and adapted:
      `AGENTS.md`, the hub, the documentation strategy, the two procedures, the four tool pointers,
      the two Claude skills.
- [x] 4 — `spec-authoring.md`: RFC 2119 usage, the `SPS-<AREA>-<NNN>` scheme, the anchor convention,
      the withdrawal rule, the area registry.
- [x] 5 — `GOVERNANCE.md`: independent version line, module versions, the dated switch from
      descriptive to prescriptive at the `0.1` tag, how a change is made.
- [x] 6 — `spec/README.md`: the chapter map with a status per chapter, and the two chapters that are
      new writing rather than a move.
- [x] 7 — Repository hardening: squash-only, delete branch on merge, `protect-main` ruleset, secret
      scanning and push protection, Dependabot alerts and security updates, private vulnerability
      reporting, `CODEOWNERS`, issue forms, pull-request template, DCO workflow, link checker. The
      ruleset requires two status checks by name — `check` from the DCO workflow and `lychee` from
      the link workflow — so renaming either job silently blocks every pull request until the
      ruleset is updated with it.
- [x] 8 — The org code-security configuration `sempods baseline` is `enforced` here. Nothing was
      done to achieve it: the configuration is the organisation default for new repositories, so it
      attached at creation. Worth recording rather than re-doing — attaching it by hand needs
      `admin:org`, which the maintainer's usual token does not carry.
- [ ] 9 — Pin the repository on the organisation profile alongside sempods-kotlin and the website.
      Needs `admin:org` and therefore the web UI; the website is still private, so the pin set is
      not complete anyway.

## S2 — The foundation every chapter rests on

- [x] 10 — `spec/core/index.md`: conformance, the RFC 2119 declaration, the requirement-ID scheme as
      a normative statement rather than an authoring convention, the core/module model, pod
      addressing, and the shared error model. `SPS-CORE-001`…`018`. A new area `CORE` was registered
      for it.
- [x] 11 — **Conformance discovery** settled in the chapter: `GET {pod}/_system/conformance`,
      unauthenticated, carrying `specVersion` and a `modules` array of IRI plus version
      (`SPS-CORE-010`…`013`). A module absent from the array counts as not provided, and a client
      must tolerate entries it does not recognise.
- [x] 12 — A CI guard for the ID promise: `.github/scripts/check-requirements.py`, run by the
      `requirements` workflow. It checks that anchors match their identifiers, that none is used
      twice, and that none disappeared against the pull request's base — comparing the paths that
      existed *then*, so splitting a chapter does not read as a mass deletion. **Add `requirements`
      to the ruleset's required checks**, or the guard is advisory.
- [ ] 13 — Follow-up filed against the reference implementation: the endpoint does not exist there.
      This is the first place the new direction bites, and it is worth being the example.

## S3 — Core chapters

- [ ] 14 — `contexts` (`CTX`) — extracted from `docs/auth/authorization.md`.
- [ ] 15 — `grants` (`GRANT`) — same source. The `#manage` subtree rule is the one requirement most
      likely to be implemented as a string-prefix check, so it needs its own requirement and its own
      conformance test.
- [ ] 16 — `auth` (`AUTH`) — from `docs/auth/oauth.md`, `oauth-errors.md`, `service-clients.md`.
      The three client-identity shapes are the part an implementer gets wrong first.
- [ ] 17 — `lod-crud` (`CRUD`) — from `docs/lod-crud/`. The largest move and the most nearly
      specification-shaped already.
- [ ] 18 — `sparql` (`SPARQL`) — **new writing.** It exists today only in fragments across three
      documents, and the LOD chapter openly defers to a SPARQL document that was never written.
- [ ] 19 — `find` (`FIND`) — **new writing.** Exists as a concept, not as a contract.

## S4 — Modules

- [ ] 20 — `oidc` (`OIDC`) — from `docs/auth/identity.md`, split from the identity service's own
      internals, which stay with the implementation.
- [ ] 21 — `media` (`MEDIA`) — from `docs/media.md`.
- [ ] 22 — `mcp` (`MCP`) — from `docs/mcp/`. `clients.md` stays behind: observed client behaviour is
      operational knowledge, not a contract.

## S5 — Vocabulary

- [ ] 23 — `NAMESPACE.md` and `vocabulary/sempods.ttl` move here, and the reference implementation
      links instead of holding them.
- [ ] 24 — Serve `https://schema.sempods.org/` with content negotiation. It has no DNS record today
      while every ontology IRI points at it. Deliberately **after** the chapters settle which terms
      are normative: the first stability guarantee says an IRI never changes, so publishing early
      sets it in stone.

## S6 — OpenAPI and the rendered specification

- [ ] 25 — One hand-written OpenAPI 3.1 description per core chapter, each operation carrying the
      requirement IDs it realises.
- [ ] 26 — Descriptions for the modules.
- [ ] 27 — `spec.sempods.org` on GitHub Pages, rendering the chapters and the OpenAPI with **Scalar**
      — chosen over Redoc because it has a built-in API client, which is the whole point of putting
      it there.
- [ ] 28 — Try-it against a public demo pod. Anonymous reads and SPARQL need no token at all. For
      authenticated calls the docs origin is itself a client identity — `did:web:spec.sempods.org` —
      so no dynamic registration step is needed in front of the login.
- [ ] 29 — `homepage` set on the repository, and the website links here instead of describing the
      API itself.

## S7 — Retire the second copy in the reference implementation

- [ ] 30 — Delete every document that moved, and replace its inbound links with requirement-ID links.
- [ ] 31 — Publish a generated `requirements.json` per release: ID → title → URL. The reference
      implementation vendors it and extends its own `checkDocLinks` to validate outbound
      specification links against it. No network in CI, and a specification upgrade becomes a visible
      diff rather than a silent drift.
- [ ] 32 — Declare the implemented specification version in `gradle.properties` and in the README.
- [ ] 33 — Correct the reference implementation's README: "a standalone specification document" is
      listed there as something that does not exist yet.
- [ ] 34 — Re-read `context7.json` in the reference implementation. Its `rules` array asserts facts
      about grants, contexts, SPARQL and client identity that this milestone restates — and it is
      served to agents outside the project.

## S8 — After 0.1

- [ ] 35 — The conformance suite, cited by requirement ID.
- [ ] 36 — `tools/` — a checker an implementer can point at a running pod.

---

## Open decisions

- **What the conformance suite is written in (S8).** The JVM is cheapest — the reference client
  already exists — but a suite meant to test a non-JVM implementation probably wants to be a
  container running HTTP tests. Decide once S3 shows how much of the contract is behaviour rather
  than shape.
- **What `sempods.org/` itself answers.** Already open on the launch checklist, and this milestone
  adds two more hostnames to the question: `spec.sempods.org` and `schema.sempods.org`.
- **Where `docs/vision.md` ends up.** It is the project's vision, not the implementation's, and its
  "core capabilities" section is already specification-shaped. Moving it means the reference
  implementation links rather than holds it. Not urgent, and it should not move before S3 has
  settled what the core chapters say.

## Acceptance

- Every core chapter exists and carries requirement IDs; `spec/README.md` shows no core row as
  planned.
- `grep -rho 'SPS-[A-Z]*-[0-9]\{3\}' spec/ | sort -u` yields no duplicate and no gap that came from
  a renumbering.
- `lychee --offline --include-fragments --no-progress .` passes.
- No document that moved here still exists in the reference implementation.
- `0.1` is tagged, and `GOVERNANCE.md`'s switch has therefore happened.
