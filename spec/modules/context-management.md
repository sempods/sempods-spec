# Module: Context management

**Optional.** Everything in this chapter binds only an implementation that advertises the module IRI
`https://schema.sempods.org/module/context-management` at the conformance endpoint
([`SPS-CORE-005`](../core/index.md#SPS-CORE-005)). Contexts themselves are core
([`../core/contexts.md`](../core/contexts.md)); what is optional is a client-facing surface for
**creating and deleting** them.

A pod that never grows a second context — a fixed deployment serving public knowledge, provisioned
once — has no use for this and is conformant without it. Its contexts come into existence at
deployment, outside this interface, and core says a pod always has at least one
([`SPS-CTX-028`](../core/contexts.md#SPS-CTX-028)).

The requirements here keep their `SPS-CTX-` identifiers. They were core before this module existed
and moved unchanged; `SPS-CORE-003` makes an identifier permanent from the `0.1` tag, and renaming
them to match a chapter would have cost sixteen stable names to gain a naming convention. What
decides whether a requirement is mandatory is the chapter it stands in, which is what
`requirements.json` reports in its `part` field.

**Status: descriptive.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: RFC 9110. Error codes are [`../core/index.md`](../core/index.md) §5; authorization is
[`../core/grants.md`](../core/grants.md).

## 1. The route and the name

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
path and a transfer turns each of those IRIs into a lie — and [`SPS-CTX-002`](../core/contexts.md#SPS-CTX-002) has already promised
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

## 2. What a context may be called

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

## 3. Lifecycle

<a id="SPS-CTX-015"></a>
**`SPS-CTX-015`** — `PUT {pod}/_system/contexts/{path}` MUST create the context at that IRI. The
request body is OPTIONAL; where present it MAY carry a human-readable `label`, a `description`, and
a `public` flag.

<a id="SPS-CTX-027"></a>
**`SPS-CTX-027`** — Where the `public` flag is absent — including on a request with no body at all —
the context MUST be created **private**.

This is [`SPS-CTX-030`](../core/contexts.md#SPS-CTX-030) applied to a request body: core requires a
context to be private unless an explicit choice made it public, and here the choice is a field that
may be absent. The body is optional, so the quiet path is the one without it, and a default of public
would make omission the dangerous choice.

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
path. A sub-context is a separate context that shares a prefix, and [`SPS-GRANT-007`](../core/grants.md#SPS-GRANT-007) already refuses
to treat a shared prefix as containment.

<a id="SPS-CTX-019"></a>
**`SPS-CTX-019`** — `PUT` and `DELETE` MUST require the pod owner, or a `#manage` grant covering the
target context under the slash-delimited rule of [`SPS-GRANT-007`](../core/grants.md#SPS-GRANT-007).

<a id="SPS-CTX-029"></a>
**`SPS-CTX-029`** — `DELETE` MUST refuse to remove a pod's last remaining context, with `409`.

Core requires a pod to have one ([`SPS-CTX-028`](../core/contexts.md#SPS-CTX-028)), and this is the
only route that could take it away. Refusing here rather than letting the pod repair itself
afterwards is what keeps the core requirement true at every moment rather than eventually.

<a id="SPS-CTX-020"></a>
**`SPS-CTX-020`** — On `DELETE`, an implementation MUST check authorization **before** existence, so
that a caller outside their sandbox receives `403` and not a `404` that would confirm the context
exists.

