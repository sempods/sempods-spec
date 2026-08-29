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
implementation once, against a state that is real. S7 comes last for that reason.

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
      ruleset requires status checks **by name**, so renaming any of those jobs silently blocks
      every pull request until the ruleset is updated with it. Which checks it requires is asked of
      the ruleset and not written down beside it: a copy of that list is a second inventory, and the
      one nobody edits is the one somebody audits from.
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
- [x] 13 — Follow-up filed against the reference implementation: the endpoint does not exist there.
      This is the first place the new direction bites, and it is worth being the example.
      `sempods/sempods-kotlin#54`. What the issue turns on is not the route but what advertising a
      module asserts — `SPS-CORE-006` makes it a claim that every `MUST` in that chapter holds,
      which is a claim the conformance suite is what can check.
- [x] 38 — **One pod, one base URL.** Numbered after the items already issued rather than inserted,
      because it settles what S2 owns and was decided late. `SPS-CORE-007` now says a pod has a base
      URL and stops prescribing how it decomposes; `spec/core/index.md` §2 states that the subject of
      this specification is one pod, and `spec-authoring.md` §1 makes *can a single pod satisfy this
      on its own?* the first question an author answers — the boundary existed and was nowhere
      written, which is how two requirements got past it.
      `SPS-AUTH-056` and `SPS-AUTH-057` are **deleted rather than withdrawn**: both obliged a pod to
      answer on a route above its own base, which a pod cannot serve and a host can. That needed
      `GOVERNANCE.md` §"Deleting and renumbering, before `0.1`" first, and the requirements checker
      carries the matching exception — it reports such a deletion as a notice, and closes the window
      by itself at the tag. `SPS-MEDIA-004` says the same thing it said, as a pod rather than by
      naming other pods.
      All four OpenAPI descriptions template one `podBaseUrl`, the host-rooted metadata path item is
      gone with the requirement behind it, and `site/build.py` holds one `DEMO_POD_BASE_URL` where it
      held an origin and a pod name.
      Two more were past the line and in neither the sweep nor this item as first written, and both
      **keep their identifiers and lose the offending clause** — the treatment `SPS-MEDIA-004` got,
      because a requirement whose satisfiable half is being used is narrowed rather than deleted.
      `SPS-MCP-031` demanded the metadata at an MCP URL's host-rooted form *and* at the append form
      on that URL; only the first is above the pod base. `SPS-MCP-004` required a distinct JSON-RPC
      code with HTTP `404` for an **unknown pod** — a response to a request that by definition never
      reaches a pod, so the actor is whatever routes to pods rather than a pod. The rest of its
      error model is untouched, and `openapi/module-mcp.yaml` lost the same sentence.
      `SPS-AUTH-054` is the sixth and the last: "a sign-in at one pod MUST NOT be a sign-in at
      another" named a second pod to constrain this one, so conformance could only be judged with
      that other pod present. It now binds a session credential's scope to the pod's own base URL,
      which is the same property tested on the pod that has to hold it.
      That the sweep found three and the count is six is the argument for writing the test down:
      every one after the third was found by reading the change rather than by looking for them.
      **`SPS-CORE-019` is the one addition**, and it exists because this change created the hole it
      fills: while `{pod}` was an identifier segment a trailing slash was not expressible, and now
      that it is the whole base URL, `{pod}/_system/…` had no defined composition. A pod's base URL
      MUST NOT end in a slash. Stating it as prose was tried and is wrong — `SPS-CORE-002` says a
      statement without an identifier does not bind, so the notation could not have qualified
      anything. `SPS-CORE-003` carries its own dated exception for the same reason.
      **The narrowing that follows is deliberate**: a generic client's pre-flight RFC 9728 discovery
      no longer finds a path-scoped pod, at the pod level or at an MCP URL. What that leans on is an
      open decision below.

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

- [x] 20 — `oidc` (`OIDC`) — `SPS-OIDC-001`…`013`. The split ran differently than planned: what a
      pod stores about a person holds with or without an identity service, so it became
      `SPS-AUTH-049`…`054` in **core**, and the module carries only how a person arrives.
- [x] 21 — `media` (`MEDIA`) — `SPS-MEDIA-001`…`025`. The SSRF requirement lists its five parts
      separately because each closes a distinct bypass and four of five is none.
- [x] 22 — `mcp` (`MCP`) — `SPS-MCP-001`…`028`. `clients.md` stayed behind as planned: observed
      client behaviour is operational knowledge, not a contract. The hosted multi-pod service is
      explicitly **not** in the module — it is a different thing with no anonymous mode, and the
      chapter says so rather than leaving it to be assumed.

## S5 — Vocabulary

- [x] 23 — `NAMESPACE.md` and `vocabulary/sempods.ttl` moved, as `vocabulary/README.md` and
      `vocabulary/sempods.ttl`. Two corrections on the way: the document said the three terms
      describe "the metadata a `find` response carries" in the present tense and that they were
      adopted because "an implementation needed them, used them" — neither is true, and it now says
      so and says why publishing them anyway is still right. Removing them from the reference
      implementation is S7.
- [x] 24 — Serve `https://schema.sempods.org/` with content negotiation. Deliberately **after** the
      chapters settled which terms are normative: the first stability guarantee says an IRI never
      changes, so publishing early sets it in stone.
      It serves no files. Caddy negotiates and redirects; the vocabulary document and the module
      chapters are the ones this site already publishes, with the content types they need, so there
      is no second copy to keep true. Turtle at the namespace or at any term IRI reaches the
      document, a browser reaches the readable page, and `/module/<name>` reaches that module's
      chapter — those identifiers are conformance markers rather than terms.
      **JSON-LD is not served** — item 37. The routing is complete; what is missing is a document
      to route to, which is a change to this repository's build rather than to the namespace.

## S6 — OpenAPI and the rendered specification

- [x] 25 — `openapi/sempods-core.yaml` — 14 paths, 28 operations, each naming the requirements it
      realises. **One file for the whole of core rather than one per chapter**, against the original
      plan: the chapters share the context rule, the canonical representation, the conditional-write
      semantics and the error model, so five files would have to duplicate or cross-reference the
      shared components and a reader would have to merge them before anything was usable.
- [x] 26 — `openapi/module-media.yaml`, `openapi/module-mcp.yaml` and `openapi/module-oidc.yaml`.
      The `oidc` file is one path long and says so in its own summary: the module's pod-side surface
      is a single callback route, and the rest is standard OpenID Connect at a service that is not
      the pod, which a description here would only re-explain. It exists rather than being omitted
      because the callback's *path* is fixed nowhere else — `SPS-OIDC-014` requires the route and
      `SPS-OIDC-011`/`SPS-OIDC-015` fix its behaviour, but none of them says where it sits.
      The checker now fails on an `x-sps-requirements` citation naming an identifier no chapter
      defines, which is the only drift a hand-written description can be guarded against locally.
      Both new jobs are in the ruleset's required checks, so neither is advisory.
- [x] 27 — `spec.sempods.org` on GitHub Pages, rendering the chapters and the OpenAPI with **Scalar**.
      Built by `site/build.py`, which stages the normative tree rather than editing it: MkDocs
      refuses a docs directory containing its own configuration, and pointing one at the repository
      root would publish the agent instructions. Pages is enabled with the workflow as its source,
      the DNS record is in place, and **`build` was added to the ruleset's required status checks**
      — without that the strict render was advisory, in exactly the way item 7 warns about.
- [ ] 28 — Try-it against a public demo pod. Anonymous reads and SPARQL need no token at all. For
      authenticated calls the docs origin is itself a client identity — `did:web:spec.sempods.org` —
      so no dynamic registration step is needed in front of the login.
      **The anonymous half is live.** The authenticated half needed an `oauth2` security scheme,
      which the core description did not have; it has one now, and it belongs there on its own
      merit — the chapters specify the OAuth surface and the description was silent about how a
      token is obtained.
      **Open until a login actually succeeds.** What is verified is that the flow is *aimed*
      correctly: the client is `did:web:spec.sempods.org`, the endpoints are the demo pod's, and
      the redirect Scalar computes is the page itself, which satisfies `SPS-AUTH-004` by sharing
      the identifier's host and port. None of that exercises consent, the code exchange, PKCE,
      CORS on the token endpoint, or an authenticated read. Ticking it on displayed strings would
      record an assumption as a result.
      The endpoint URLs are absolute on a placeholder pod in the description and on the demo pod in
      the staged copy, `site/build.py` moving them with the `servers` defaults. Relative was tried
      and is wrong — it resolves away the pod segment — and templating them with the `servers`
      variable was tried and is worse: Scalar drops the flow entirely rather than substituting. The description states the
      residue, that a consumer substitutes its pod here as well as in `servers`.
- [ ] 29 — `homepage` set on the repository, and the website links here instead of describing the
      API itself. **The repository half is done**; the website half is deliberately last, after this
      specification and the reference implementation are finished, so that every outbound link and
      every constraint is known before the page is written once rather than edited three times.
      What it has to correct is a sentence that is now false: the site says the specification
      repository "is being prepared and will carry the formal specification and OpenAPI contract".

## S7 — Retire the second copy in the reference implementation

- [x] 30 — Delete every document that moved, and replace its inbound links with requirement-ID links.
- [x] 31 — Publish a generated `requirements.json`. **Shape decided differently from the sketch
      here**: identifier → chapter → first sentence → withdrawn, and deliberately **no URL** — one
      would have to pin a branch or a tag, and the consumer is who knows which it wants. No
      timestamp either, or every regeneration is a diff. Generated by the checker (`--write-index`),
      committed, and verified: a drifted or missing copy fails the build. The reference
      implementation vendors it and extends `checkDocLinks` to validate citations against it, so
      there is no network in CI and a specification upgrade arrives there as a reviewable diff.
- [x] 32 — Declare the implemented specification version in `gradle.properties`. **The README
      points at that declaration rather than repeating the number**, against the sketch here: two
      copies of a version is one copy that goes stale, and the same argument this file already
      makes about tracking issues holds for a number. What the README carries instead is the
      rule that makes the claim checkable — `checkDocLinks` fails if the declaration drifts from
      the vendored index.
- [x] 33 — Correct the reference implementation's README: "a standalone specification document" is
      listed there as something that does not exist yet.
- [x] 34 — Re-read `context7.json` in the reference implementation. Its `rules` array asserts facts
      about grants, contexts, SPARQL and client identity that this milestone restates — and it is
      served to agents outside the project.

## S8 — After 0.1

- [ ] 35 — The conformance suite, cited by requirement ID.
- [ ] 36 — `tools/` — a checker an implementer can point at a running pod.
- [ ] 37 — Publish the vocabulary as JSON-LD and serve it. `vocabulary/README.md` names it beside
      Turtle and HTML as what the namespace should answer; today an explicit request for it gets a
      406, which is honest but not the stated intent. Generating it from the Turtle needs an RDF
      library in the site build, so it is a dependency decision as much as a routing one — and the
      routing is already there, waiting for a document to point at.
      Here rather than in S5 because nothing in `0.1` claims it: an IRI is an identifier before it
      is a URL, and Turtle plus HTML is a complete answer for a consumer that dereferences at all.

---

## Open decisions

- **Seven OpenAPI fidelity items are deferred, deliberately.** Review found the descriptions lagging
  the chapters in seven places that change no obligation: media `security` still admitting anonymous
  mutations, the content response fixed to `octet-stream`, `If-None-Match` missing from reads, `204`
  missing from the system-layer `PUT`, the SPARQL dataset parameters advertised as universal though
  `SPS-SPARQL-011` makes them optional, `@context` refused on a `PUT` body that
  `SPS-CRUD-012` treats as advisory, and `ContextList` carrying no `required` list. They ride into
  the S6 rendering work, where the descriptions get another pass against a renderer rather than
  against a reader.


- **Item 38 left two holes in `auth` §10 where deleted requirements used to speak.** Both are the
  same shape — a `MUST` went, and what replaced it is convention — and both are cheap, one `AUTH`
  requirement each. **Before `0.1`.**
  - **The `resource_metadata` hint that discovery now depends on is not required.** With the
    host-rooted address gone there is one address for Protected Resource Metadata, the append form,
    and no standard way to find it: a client makes an unauthenticated request and reads
    `resource_metadata` out of the `401`'s `WWW-Authenticate`.
    [`SPS-MCP-009`](../../spec/modules/mcp.md#SPS-MCP-009) requires that header of a pod providing
    the MCP module and nothing requires it of one that does not — which is the "invisible until a
    real client arrives" failure the deleted requirement was written against, moved one layer down.
    The chapter's prose already names this as an acknowledged gap.
  - **Nothing says where RFC 8414 Authorization Server Metadata lives.** `SPS-AUTH-057` carried
    both its addresses, so deleting it took the pod-relative one with the host-rooted one.
    `spec/core/auth.md` still declares it profiles RFC 8414 and
    [`SPS-AUTH-048`](../../spec/core/auth.md#SPS-AUTH-048) still constrains the document's contents,
    but the address is unstated — and RFC 8414's own is host-rooted, so the standard the chapter
    profiles names a place a path-scoped pod cannot serve. Unlike the hint above this is not a
    reinstatement: the append form was never the standard's, and requiring it is a decision about
    blessing a convention rather than about writing down what everyone already does.

- **How an implementation's version relates to the specification's, and what a pre-release looks
  like.** `GOVERNANCE.md` says the specification's line is independent of any implementation, and
  gives the reason — the implementation must not force a specification release. The proposal on the
  table points the other way and is compatible with that: an implementation *follows*, so spec
  `0.1` gives sempods-kotlin `0.1.<n>`, counting up. A second implementation would do the same.
  What is undecided, and wanted before the project is public:
  - Whether a tagged `0.1` can still move at all, or whether every change after the tag is `0.2`.
    The current text implies the latter — the switch to prescriptive happens *at* the tag — and the
    `0.x` promise already allows breaking between minors, which makes frequent minors cheap.
  - Whether the specification gets pre-release versions of its own (`0.2.0-SNAPSHOT` or similar)
    so a change can be worked on while `0.1` stays fixed, and what an implementation declares while
    tracking one. `specVersion` is a free-form string today (`SPS-CORE-011`), and the reference
    implementation already declares `0.1-dev` — so the question is not whether it is expressible
    but what it is allowed to mean.
  - What "pulling a version" is as a procedure: what gets tagged, in what order the two
    repositories move, and what the conformance endpoint reports in between.
  This is `GOVERNANCE.md`'s subject, not a roadmap item — but it has to be settled before `0.1`,
  because the tag is what makes all of it binding.

- **`SPS-CORE-018` is a context-enumeration oracle, and has to close before `0.1` is prescriptive.**
  On a write, an unregistered context answers `404` and a registered one the caller may not write
  answers `403`, so a caller who can reach the write path learns which guessed context IRIs exist.
  It is what the reference implementation does and the specification is descriptive, so it is
  recorded rather than silently corrected — but it contradicts the security stance in `AGENTS.md`,
  which calls a requirement leaking context topology a defect. The shape of the fix is already in
  the specification: authorize **before** testing existence, the way context deletion does
  ([`SPS-CTX-020`](../../spec/core/contexts.md#SPS-CTX-020)). Changing it means a matching change in
  the reference implementation, which is why it is a decision and not a text edit.

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
- `grep -rho 'SPS-[A-Z]*-[0-9]\{3\}' spec/ | sort -u` yields no duplicate, and every gap in it is
  one the roadmap accounts for. There is none today: item 38 deleted the two highest `AUTH` numbers
  while `GOVERNANCE.md`'s pre-`0.1` window was open, so 056 and 057 are back in the pool rather than
  missing from a sequence. From the tag on, a gap can only come from a withdrawal, a renumbering
  cannot happen at all, and the highest ever issued parts company with the highest still in the
  chapters.
- `lychee --offline --include-fragments --no-progress --exclude-path site .` passes.
- No document that moved here still exists in the reference implementation.
- `0.1` is tagged, and `GOVERNANCE.md`'s switch has therefore happened.
