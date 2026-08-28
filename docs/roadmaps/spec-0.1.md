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

- [x] 14 — `contexts` (`CTX`) — `SPS-CTX-001`…`026`. The one thing the source did not state as a
      rule: on `DELETE`, authorization is checked *before* existence, so an out-of-sandbox caller
      gets `403` rather than a `404` that would confirm the context exists.
- [x] 15 — `grants` (`GRANT`) — `SPS-GRANT-001`…`027`. The `#manage` subtree rule is
      `SPS-GRANT-007` and says "if and only if" for the reason it exists. Two rules that were only
      in `context7.json` and not in the documentation were verified against
      `PodContextPermissionResolver` before being written down: `write`/`manage` imply `read`, and
      a `#manage` root expands only over *registered* contexts.
- [x] 16 — `auth` (`AUTH`) — `SPS-AUTH-001`…`048`, from `docs/auth/oauth.md` and
      `service-clients.md`. `oauth-errors.md` deliberately did **not** move: it is per-code recovery
      guidance for a client, which is documentation and not a contract. The error *codes* are
      normative and appear in the flow requirements.
      Left behind as deployment choices rather than contract: the rate-limit numbers and their
      environment variables, the OIDC leg timeouts, the audit-log retention, and the storage
      shapes.
- [x] 17 — `lod-crud` (`CRUD`) — `SPS-CRUD-001`…`056`, from all three files in
      `docs/lod-crud/`. The largest move and the one that was most nearly specification-shaped
      already. Two limitations became requirements rather than caveats, because an implementation
      differing on either produces data another one reads wrongly: predicate IRIs are never
      canonicalised, and there is no atomic multi-context write anywhere. The TOCTOU gap on
      conditional writes stayed prose — it is an implementation limitation, not a contract.
- [x] 18 — `sparql` (`SPARQL`) — `SPS-SPARQL-001`…`020`, written from the fragments and from
      `SparqlQueryService` / `SparqlEndpoint`. Two rules came from the code and from no document:
      a malformed query and an Update are refused *identically*, so a prober cannot learn which it
      wrote; and a present-but-empty dataset parameter fails closed to the empty set rather than
      falling back to the full readable set. The second is a privilege escalation if implemented
      the other way round.
- [x] 19 — `find` (`FIND`) — `SPS-FIND-001`…`023`, from the concept's IST half plus the endpoint.
      **Finding: the three `sps:` vocabulary terms appear nowhere in the Kotlin code.** `NAMESPACE.md`
      describes them in the present tense as "the metadata a `find` response carries about each
      hit", and no implementation emits them. The chapter therefore specifies the flat graph as the
      contract and records the terms as reserved-but-not-emitted, so nobody mints a competing set.
      **`NAMESPACE.md` needs correcting when it moves in S5** — see the open decisions.

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

- **`NAMESPACE.md` overstates what the vocabulary is used for.** It says the three `sps:` terms are
  "the metadata a `find` response carries about each hit" and that they were adopted because "an
  implementation needed them, used them". Neither is true today: the terms appear in no Kotlin
  source. Correcting it is part of S5, and it changes what D6 is for — publishing a namespace whose
  terms nothing emits is still worth doing for the deprecation promise, but it is not the "it is
  already in use" argument the document currently makes.

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
