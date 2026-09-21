# Module: Context management

**Optional.** Everything in this chapter binds only an implementation that advertises the module IRI
`https://schema.sempods.org/module/context-management` at the conformance endpoint
([`SPS-CORE-005`](../core/index.md#SPS-CORE-005)). Contexts themselves are core
([`../core/contexts.md`](../core/contexts.md)); what is optional is a client-facing surface for
**creating and deleting** them.

What is *not* here is what a context IRI may be. The reserved names, the delegation types, the shapes
that cannot be addressed again — those bind however a context comes into existence, so they are core
invariants and this chapter only enforces them at creation. A pod provisioned outside this interface
is held to them all the same.

A fixed deployment can provision its contexts outside this interface and omit the module;
[`SPS-CTX-028`](../core/contexts.md#SPS-CTX-028) requires it to have at least one. A pod providing
the module can have an empty registry and let its owner create the first context.

The requirements here carry `SPS-CTX-` identifiers, which is the same area the core contexts
chapter uses. That is deliberate: `SPS-CORE-003` makes an identifier permanent from the `0.1` tag,
so a requirement that becomes conditional keeps the name it already had. **What decides whether a
requirement is mandatory is the chapter it stands in**, which is what `requirements.json` reports in
its `part` field — never the identifier.

**Status: this text decides, and can still change.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

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

## 2. What a context may be called

The rules are permissive about names and strict about structure.

<a id="SPS-CTX-009"></a>
**`SPS-CTX-009`** — An implementation MUST accept a freely chosen context name that breaks none of
the structural rules — [`SPS-CTX-006`](../core/contexts.md#SPS-CTX-006),
[`SPS-CTX-007`](../core/contexts.md#SPS-CTX-007), [`SPS-CTX-008`](../core/contexts.md#SPS-CTX-008),
[`SPS-CTX-010`](../core/contexts.md#SPS-CTX-010),
[`SPS-CTX-011`](../core/contexts.md#SPS-CTX-011) and
[`SPS-CTX-013`](../core/contexts.md#SPS-CTX-013) in core, and `SPS-CTX-012` below. `privat`,
`2026-sommer` and `projects/alpha` are all valid.

<a id="SPS-CTX-012"></a>
**`SPS-CTX-012`** — A **type root** — a path consisting of a delegation type and one further
segment, such as `apps/notes` — MUST NOT be creatable through the context management route. Type
roots are established by the control plane.

<a id="SPS-CTX-014"></a>
**`SPS-CTX-014`** — This route MUST apply the naming rules on **creation only** — the structural
ones core states, and `SPS-CTX-012` here. Reading and deleting MUST keep working for every context
that exists, including shapes that predate a rule.

A rule that made an existing context unreadable, or a type root undeletable, would be a one-way
door. [`SPS-CTX-013`](../core/contexts.md#SPS-CTX-013) is the exception that proves it: a path that
was never addressable was never a context, whenever it was written — which is why it is an invariant
in core rather than a check this route performs.

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

<a id="SPS-CTX-037"></a>
**`SPS-CTX-037`** — Successful Context PUT responses (`200` and `201`) MUST return the registry RDF
description defined by [`SPS-CTX-031`](../core/contexts.md#SPS-CTX-031) and
[`SPS-CTX-032`](../core/contexts.md#SPS-CTX-032), using their content negotiation and
[`SPS-CTX-036`](../core/contexts.md#SPS-CTX-036)'s cache isolation. The server MUST establish that
an acceptable success representation can be returned before creating the Context; unsatisfiable
`Accept` MUST return `406` without creation. The optional JSON creation input and the create-only
`201`/`200` effects remain those of `SPS-CTX-015`, `SPS-CTX-016` and `SPS-CTX-027`.

This response representation does not make PUT a general RDF update or add conditional writes.
A client reads the registry with GET for its validator and conditional-read contract.

<a id="SPS-CTX-017"></a>
**`SPS-CTX-017`** — `DELETE {pod}/_system/contexts/{path}` MUST remove the context, and MUST also
remove the state that rested on it: the grants naming it, and the context's statements.

No refresh token rests on it: this specification gives one no binding to a context, and authority
over a context is a grant ([`SPS-GRANT-001`](../core/grants.md#SPS-GRANT-001)). The grant removal
above is what closes the window a re-created IRI would otherwise open. A module an implementation
advertises may rest more on a context than this chapter does —
[`SPS-MEDIA-021`](media.md#SPS-MEDIA-021) has the deletion reach media assignments.

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

Authorization failures follow [`SPS-CORE-018`](../core/index.md#SPS-CORE-018).

For example, an authenticated caller without `manage` on `apps/notes` receives `403` for a
well-formed `PUT` whether that type root exists or not. The creation-only naming restriction does
not turn the absent case into `400` for that caller.

An authorized caller deleting its only visible context receives `204`, whether or not the pod
contains other contexts. The owner can create a new context even after the registry becomes empty.
