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
**`SPS-CTX-028`** — A pod MUST have at least one registered context.

Where the context-management module ([`../modules/context-management.md`](../modules/context-management.md))
is not provided, there is no route that creates one, so the first context comes into existence at
deployment and outside this interface. Without this requirement the specification would permit a pod
with no contexts and no specified way to make one — conformant, and unable to hold a statement, since
`SPS-CTX-001` puts every statement in a context and a write names the one it targets.

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
