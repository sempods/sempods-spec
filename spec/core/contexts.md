# Contexts

A **context** is a named graph in a pod, and it is the permission boundary. Not the resource, not
the property, not a role. One concept carries the whole access-control model, which is why this
chapter comes before [`grants`](grants.md) rather than inside it.

**Status: descriptive.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: RDF 1.1 (named graphs). Error codes are [`index.md`](index.md) §5.

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

<a id="SPS-CTX-005"></a>
**`SPS-CTX-005`** — The management route and the context IRI MUST be the same string:
`PUT {pod}/_system/contexts/apps/notes/public` manages exactly the context
`{pod}/_system/contexts/apps/notes/public`. An implementation MUST NOT decompose the path into an
identifier on either side.

Identity and route are one string so they cannot drift apart. There is no mapping table to get wrong
and nothing to migrate when the route changes shape.

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

## 3. What a context may be called

The rules are permissive about names and strict about structure.

<a id="SPS-CTX-009"></a>
**`SPS-CTX-009`** — An implementation MUST accept a freely chosen context name that breaks none of
the structural rules below. `privat`, `2026-sommer` and `projects/alpha` are all valid.

<a id="SPS-CTX-010"></a>
**`SPS-CTX-010`** — The segment `_system` MUST be rejected anywhere in a context path.

It is held free so that a context IRI can later carry `<context-iri>/_system/<operation>` for
per-context operations. Context names and operation names are both open sets; without a reserved
separator they eventually collide, and a name banned after the fact would break pods already using
it.

<a id="SPS-CTX-011"></a>
**`SPS-CTX-011`** — The delegation types `apps` and `users` MUST be reserved as the **first** path
segment. `users` is reserved without being implemented, so that the name cannot be taken by
something else first.

<a id="SPS-CTX-012"></a>
**`SPS-CTX-012`** — A **type root** — a path consisting of a delegation type and one further
segment, such as `apps/notes` — MUST NOT be creatable through the context management route. Type
roots are established by the control plane.

<a id="SPS-CTX-013"></a>
**`SPS-CTX-013`** — A context path that could not be addressed again MUST be rejected. Specifically,
an implementation MUST reject a path containing an empty segment, a relative segment (`.` or `..`),
a percent-encoded character, a fragment, or a query, and any path its URI parser cannot parse.

Each of these produces a registry entry no route can reach. Percent-encoding is the one that looks
harmless: both producers receive the path already decoded, so a stored `foo%23bar` is only ever
asked for as `foo#bar` — which is refused — and `foo%2Fbar` as `foo/bar`, which finds a different
entry. A fragment is worse than unreachable: `<pod>/_system/contexts/foo#bar` cannot be parsed back
out of the grant string `<context-iri>#<permission>`, because `…foo#bar#read` has two candidate
split points and the wrong one wins.

<a id="SPS-CTX-014"></a>
**`SPS-CTX-014`** — The naming rules `SPS-CTX-009` through `SPS-CTX-012` MUST apply on **creation
only**. Reading and deleting MUST keep working for every context that exists, including shapes that
predate a rule.

A rule that made an existing context unreadable, or a type root undeletable, would be a one-way
door. `SPS-CTX-013` is the exception that proves it: a path that was never addressable was never a
context, whenever it was written.

## 4. Lifecycle

<a id="SPS-CTX-015"></a>
**`SPS-CTX-015`** — `PUT {pod}/_system/contexts/{path}` MUST create the context at that IRI. The
request body is OPTIONAL; where present it MAY carry a human-readable `label`, a `description`, and
a `public` flag.

<a id="SPS-CTX-027"></a>
**`SPS-CTX-027`** — Where the `public` flag is absent — including on a request with no body at all —
the context MUST be created **private**.

The body is optional, so the quiet path is the one without it, and a default of public would make
omission the dangerous choice. Pods are isolated by default
(`AGENTS.md` §"Non-negotiable invariants"); a context becomes readable without a grant because
somebody said so, never because they said nothing.

<a id="SPS-CTX-016"></a>
**`SPS-CTX-016`** — `PUT` MUST be idempotent. Creating a context that already exists MUST answer
`200` with the existing context and MUST NOT alter it. A first creation MUST answer `201`.

Two callers creating the same context concurrently both get their post-condition, so the loser of
that race is `200` and not an error.

<a id="SPS-CTX-017"></a>
**`SPS-CTX-017`** — `DELETE {pod}/_system/contexts/{path}` MUST remove the context, and MUST also
remove the state that rested on it: grants naming it, refresh tokens scoped to it, and the
context's statements.

<a id="SPS-CTX-018"></a>
**`SPS-CTX-018`** — Deletion MUST NOT cascade into sub-contexts. Deleting `R` leaves `R/sub` in
place.

The two preceding requirements read as a contradiction and are not. Deletion cascades through
everything that *pointed at* the context and stops at everything that merely *sits below* it in the
path. A sub-context is a separate context that shares a prefix, and [`SPS-GRANT-007`](grants.md#SPS-GRANT-007) already refuses
to treat a shared prefix as containment.

<a id="SPS-CTX-019"></a>
**`SPS-CTX-019`** — `PUT` and `DELETE` MUST require the pod owner, or a `#manage` grant covering the
target context under the slash-delimited rule of [`SPS-GRANT-007`](grants.md#SPS-GRANT-007).

<a id="SPS-CTX-020"></a>
**`SPS-CTX-020`** — On `DELETE`, an implementation MUST check authorization **before** existence, so
that a caller outside their sandbox receives `403` and not a `404` that would confirm the context
exists.

## 5. Discovery

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

## 6. `_system` is protected, not undescribable

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
