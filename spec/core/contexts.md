# Contexts

A **context** is a named graph in a pod, and it is the permission boundary. Not the resource, not
the property, not a role. One concept carries the whole access-control model, which is why this
chapter comes before [`grants`](grants.md) rather than inside it.

Creating and deleting contexts is a separate, optional surface:
[`../modules/context-management.md`](../modules/context-management.md). What is here is what every
pod has — what a context *is*, what its IRI may be, how a caller discovers the ones it may reach, and
the boundary that keeps the control plane out of the data path. The naming rules are here rather than
there for the reason that decides every such split: they bind however a context came into existence,
and a pod provisioned outside that module still has contexts.

**Status: this text decides, and can still change.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: RDF 1.1 (named graphs). Registry representations use the graph vocabulary from
[SPARQL Service Description, 21 March 2013, §3](https://www.w3.org/TR/2013/REC-sparql11-service-description-20130321/#vocab),
[RDF Schema 1.1, 25 February 2014](https://www.w3.org/TR/2014/REC-rdf-schema-20140225/) and
[DCMI Terms, 20 January 2020](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/).
Only their term meanings are used; no service-description endpoint is required.
[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) §§8.8, 12 and 13 govern negotiated registry
representations, validators and conditional reads; [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html)
governs caching. Error codes are [`index.md`](index.md) §5.

## 1. The boundary

<a id="SPS-CTX-001"></a>
**`SPS-CTX-001`** — Every statement stored in a pod MUST belong to exactly one context. There is no
default context, no unassigned statement, and no statement in two contexts at once.

<a id="SPS-CTX-002"></a>
**`SPS-CTX-002`** — A context MUST be identified by its full canonical IRI. An implementation MUST
NOT expose an internal identifier in its place, and MUST NOT require a client to construct one.

<a id="SPS-CTX-003"></a>
**`SPS-CTX-003`** — An implementation MUST NOT introduce a permission abstraction above or beside
the context — no project, no folder, no role, no group. Every permission attaches to a context.

That last one is a requirement about what an implementation may *add*, which is unusual and
deliberate. A role layer bolted on top would still be expressible in grants, and the two would
disagree the first time somebody edited one of them.

## 2. Where context IRIs live

<a id="SPS-CTX-004"></a>
**`SPS-CTX-004`** — Context IRIs MUST live under `{pod}/_system/contexts/`. A context is
control-plane state, so it inherits the reserved area's protection rather than needing a rule of its
own.

These bind however a context comes into existence. They are about what a context IRI *is* — which
names are reserved, which shapes can be addressed again, what a path says about delegation — and a
pod provisioned outside the context-management module holds itself to them exactly as one that
creates contexts through a route does. What the module adds is the duty to *enforce* them at
creation.

<a id="SPS-CTX-006"></a>
**`SPS-CTX-006`** — A context **delegated** to someone MUST carry a delegation type as its first
path segment, followed by the delegate's identifier. A context the pod owner **keeps** MUST NOT
carry one, and is otherwise named freely.

```
{pod}/_system/contexts/contacts                    ← the owner's own area
{pod}/_system/contexts/projects/alpha              ← still the owner's; nesting is not a type
{pod}/_system/contexts/apps/notes/public           ← delegated to an app
```

A type means delegation, not ownership. `apps/notes` does not say "belongs to the notes app"; it
says "the area it may work in".

<a id="SPS-CTX-007"></a>
**`SPS-CTX-007`** — The pod owner's identity MUST NOT appear in a context path.

Pod ownership is transferable and may be held by an organisation. Put the owner's WebID in every
path and a transfer turns each of those IRIs into a lie — and `SPS-CTX-002` has already promised
that the IRI is the identity, so it cannot be rewritten afterwards.

<a id="SPS-CTX-008"></a>
**`SPS-CTX-008`** — The delegation type `users` is reserved for guest contexts. This version of the
specification does **not** define the path shape below it, and an implementation MUST NOT mint one.

The intent is recorded so the name is not taken by something else: a guest's access is bound to them
personally, so naming them in the path would say something that stays true — the deliberate
exception to `SPS-CTX-007`, where the pod owner must never appear because ownership transfers.

What is not settled is how an identity URI occupies a path segment. A WebID such as
`https://id.example/alice#me` carries a scheme, an empty segment and a fragment, every one of which
[`SPS-CTX-013`](#SPS-CTX-013) refuses — so the shape cannot simply be written down, and specifying
an encoding for it before any implementation needs one is how a specification acquires a rule nobody
can check. It waits for a guest implementation.

<a id="SPS-CTX-010"></a>
**`SPS-CTX-010`** — A context path MUST NOT contain the segment `_system`, anywhere in it.

It is held free so that a context IRI can later carry `<context-iri>/_system/<operation>` for
per-context operations. Context names and operation names are both open sets; without a reserved
separator they eventually collide, and a name banned after the fact would break pods already using
it.

<a id="SPS-CTX-011"></a>
**`SPS-CTX-011`** — The delegation types `apps` and `users` MUST be reserved as the **first** path
segment. `users` is reserved without being implemented, so that the name cannot be taken by
something else first.

<a id="SPS-CTX-013"></a>
**`SPS-CTX-013`** — A context path MUST be one that can be addressed again. Specifically, it MUST
NOT contain an empty segment, a relative segment (`.` or `..`), a percent-encoded character, a
fragment, or a query, and MUST be one an implementation's URI parser can parse.

Each of these produces a registry entry no route can reach. Percent-encoding is the one that looks
harmless: both producers receive the path already decoded, so a stored `foo%23bar` is only ever
asked for as `foo#bar` — which is refused — and `foo%2Fbar` as `foo/bar`, which finds a different
entry. A fragment is worse than unreachable: `<pod>/_system/contexts/foo#bar` cannot be parsed back
out of the grant string `<context-iri>#<permission>`, because `…foo#bar#read` has two candidate
split points and the wrong one wins.

<a id="SPS-CTX-028"></a>
**`SPS-CTX-028`** — A pod that does not provide the
[context-management module](../modules/context-management.md) MUST have at least one registered
context.

Without the module, contexts are provisioned outside this interface. The minimum keeps such a pod
able to hold statements. With the module, a pod can start or become empty: the owner can create a
context through `PUT`. Every stored statement still belongs to a context (`SPS-CTX-001`).

<a id="SPS-CTX-030"></a>
**`SPS-CTX-030`** — A context MUST be private unless it was made public by an explicit choice. This
holds however the context came into existence, including provisioning outside any interface this
specification defines.

Pods are isolated by default (`AGENTS.md` §"Non-negotiable invariants"), and a context becomes
readable without a grant because somebody said so — never because nobody said anything. The rule is
stated here rather than only where a context is created, because the route that creates one is
optional ([`../modules/context-management.md`](../modules/context-management.md)) and the guarantee
is not: a pod without that module still has the context `SPS-CTX-028` requires, and it arrived
without anybody calling anything.

## 3. Discovery

<a id="SPS-CTX-021"></a>
**`SPS-CTX-021`** — `GET {pod}/_system/contexts` MUST list the contexts visible to the caller,
each with the permissions the caller effectively holds on it, and MUST separately name the contexts
the caller may write to.

<a id="SPS-CTX-022"></a>
**`SPS-CTX-022`** — This route is the authoritative client-visible view of effective context
permissions. An implementation MUST NOT require a client to derive them from an access token, and a
client MUST NOT treat a token's `scope` claim as a context catalogue.

<a id="SPS-CTX-023"></a>
**`SPS-CTX-023`** — A client MUST NOT construct a context IRI. Every context IRI a client uses MUST
have come from this route or from the pod.

The last two are what let the context namespace move without a client change, and they are why
`?context=` takes a full IRI rather than a name.

<a id="SPS-CTX-024"></a>
**`SPS-CTX-024`** — `GET {pod}/_system/contexts/{path}` MUST return what the registry holds for that
context. Where the caller cannot see the context, the response MUST be `404` — never `403`.

### RDF representations

Let C be a Context IRI and L be `{pod}/_system/contexts`. The response describes registry state;
resource reads remain the separate surface for ordinary statements about those IRIs.

<a id="SPS-CTX-031"></a>
**`SPS-CTX-031`** — Successful GET responses for L and C MUST represent registry RDF using the
canonical JSON-LD shape and content negotiation of [`SPS-CRUD-023`](lod-crud.md#SPS-CRUD-023),
[`SPS-CRUD-024`](lod-crud.md#SPS-CRUD-024), [`SPS-CRUD-026`](lod-crud.md#SPS-CRUD-026) and
[`SPS-CRUD-027`](lod-crud.md#SPS-CRUD-027). N-Quads MUST express the same RDF in its default graph.
JSON-LD `@type` values MUST be arrays of absolute IRIs. These responses MUST NOT use the legacy `Context` or `ContextList` JSON envelopes.

<a id="SPS-CTX-032"></a>
**`SPS-CTX-032`** — A Context description MUST identify C as `sd:NamedGraph`, have exactly one
`sd:name` equal to C, and have exactly one Boolean `sps:public` expressing its registry public-read
setting, using a native JSON Boolean value in JSON-LD. It MUST include the registry's label and description, when present, as `rdfs:label` and
`dcterms:description` string literals; a known creation time as `dcterms:created` with datatype
`xsd:dateTime`; and an `rdfs:seeAlso` IRI `{pod}/_system/resources/{base64url(C)}` using UTF-8 and
[`SPS-CRUD-005`](lod-crud.md#SPS-CRUD-005). It MUST NOT include caller permissions, stored policy
rules or ordinary statements about C. Clients MUST tolerate additional descriptive predicates.

Prefixes in this section have their published RDF meanings; `sps:` is
`https://schema.sempods.org/`. `rdfs:seeAlso` asserts relevance, not data existence, equivalence or
authority. Its construction needs no read of the ordinary data. Following it can return `404` even
when the registry description is visible. Known timestamps are reported, not invented.

<a id="SPS-CTX-033"></a>
**`SPS-CTX-033`** — A catalogue MUST identify L as `sd:GraphCollection` and link every registered
Context visible to this caller with `sd:namedGraph`. Its caller permissions MUST be direct
`sps:readableContext`, `sps:writableContext` and `sps:manageableContext` IRI relationships from L
to those Contexts. The sets MUST be complete, with no absent Contexts or hypothetical descendants;
empty sets have no RDF triples. The catalogue MUST NOT embed the individual Context descriptions.
An empty catalogue MUST still return `200` with L's identity and collection type.

<a id="SPS-CTX-034"></a>
**`SPS-CTX-034`** — The catalogue relationships MUST report the requesting client's current effective
read, write and manage permissions under [`grants`](grants.md), including implied modes, delegation
limits and applicable public read. Visibility MUST require at least one such mode. A server MUST
NOT substitute a person's broader rights or treat a copied catalogue statement as authorization.
Clients MUST treat the summary as response-relative information, not permission for a later request.

Write therefore appears in both readable and writable sets; manage appears in all three. Anonymous
callers see public Contexts through the readable relationship; invalid supplied credentials remain
`401` under the authentication contract. Membership does not require data in the named graph.

<a id="SPS-CTX-035"></a>
**`SPS-CTX-035`** — Successful registry and catalogue GET responses MUST supply strong ETags and
support `If-None-Match` under RFC 9110. The server MUST establish current authorization and the normal
response status before evaluating a conditional read. Hidden and absent individual Contexts MUST
both return indistinguishable `404` responses, including bodies, links and validators; a previously
visible but now hidden Context MUST NOT return `304`. Individual tags MUST describe the registry
representation, independently of graph contents or ordinary assertions about C. A catalogue tag
MUST change when its represented membership or permissions change.

<a id="SPS-CTX-036"></a>
**`SPS-CTX-036`** — Registry responses, including errors, MUST NOT be reused across caller/client
authorization contexts or without current authorization. Any stored response MUST preserve that
isolation and representation freshness under RFC 9111. A request validator MUST NOT extend access
or disclose a hidden Context.

`Cache-Control: no-store` on all registry responses is one sufficient strategy. Private storage with
mandatory revalidation can also satisfy the guarantees when cache selection distinguishes the
credential/authorization inputs and negotiated variants. These are alternatives; neither storage
layout nor one specific cache-header combination is prescribed.

The [registry representation cases](../../docs/guides/context-registry.md) illustrate descriptions,
empty and permission-bearing catalogues, conditional reads and authority separation.

## 4. `_system` is protected, not undescribable

This is the distinction most likely to be lost, and losing it costs the model.

<a id="SPS-CTX-025"></a>
**`SPS-CTX-025`** — Control-plane state MUST NOT be reachable through the data path. No RDF write —
CRUD or otherwise — may create, alter or delete a context, a grant or a registration.

<a id="SPS-CTX-026"></a>
**`SPS-CTX-026`** — A statement whose subject is a `_system` IRI MUST be treated as ordinary data.
An implementation MUST NOT refuse it on the grounds of its subject.

A pod may hold `<{pod}/_system/contexts/contacts> rdfs:label "Privat"` exactly as it holds statements
about `did:web:bob.example` or about another pod's resources. What a statement is *about* is
independent of where it is stored; the writable context is the authorization boundary, and the
subject IRI never is.

So: ask `GET {pod}/_system/contexts/{path}` what a context **is**, and the resource routes what
anyone has **said about** it. Reading the second as the first is the error this section exists to
prevent — no amount of RDF about a context IRI changes the context.
