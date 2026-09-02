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
**`SPS-CTX-029`** — `DELETE` MUST refuse to remove the only context **visible to the caller**, with
`409`.

Core requires a pod to have one ([`SPS-CTX-028`](../core/contexts.md#SPS-CTX-028)), and this is the
only route that could take it away. Refusing here rather than letting the pod repair itself
afterwards is what keeps the core requirement true at every moment rather than eventually.

**The condition is the caller's view and not the pod's count**, which is the part worth reading
twice. Written against the pod's last context, the status answers a question the caller may not ask:
a delegated manager deleting the one context they can see would get `409` where the pod holds nothing
else and `204` where it holds contexts they cannot see, so the response would report the size of a
namespace [`SPS-CTX-024`](../core/contexts.md#SPS-CTX-024) hides from them.

Asked of what the caller can see, the answer is the same either way and the invariant still holds.
The pod owner sees every context ([`SPS-GRANT-011`](../core/grants.md#SPS-GRANT-011)), so for them
the two conditions are one. Nobody else can empty the pod, because reaching zero would mean deleting
a context while seeing a second one — and where the pod has one context, there is no second one for
anybody to see.

<a id="SPS-CTX-020"></a>
**`SPS-CTX-020`** — On `DELETE`, an implementation MUST check authorization **before** existence, so
that a caller outside their sandbox receives `403` and not a `404` that would confirm the context
exists.

