# Access control (Concept)

## Purpose

sempods decides access in two chapters that do not agree with each other about what a *thing* is.
[`lod-crud`](../../spec/core/lod-crud.md) says a resource's identity is its LOD IRI — a subject.
[`grants`](../../spec/core/grants.md) attaches every permission to a context — a named graph. Both
statements are correct today and neither is wrong; they simply answer different questions and have
never been reconciled.

This concept reconciles them by naming the missing piece: **the granularity at which access is
decided is a choice, and sempods has to make it explicitly rather than twice by accident.** The
frame it uses is the Solid Community Group's
[Access Control Policy (ACP)](https://solid.github.io/authorization-panel/acp-specification/), which
supplies an evaluation algorithm and a vocabulary and deliberately leaves that choice open.

Sections below are marked **IST** (specified today, verifiable against the chapters) or **SOLL**
(target state). The SOLL has no roadmap yet, and cannot become normative while the specification is
still descriptive — [`GOVERNANCE.md`](../../GOVERNANCE.md) owns that window.

## The granularity ladder (IST)

Five things in this specification could carry a permission. Only two of them can carry one usefully.

| Candidate | Defined by | Usable as a decision unit |
|---|---|---|
| Statement | [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001) | No — nothing addresses a single statement |
| Slot `(subject, predicate)` in one context | [`lod-crud`](../../spec/core/lod-crud.md) §5 | No — one policy per predicate per subject |
| **Subject** | [`SPS-CRUD-001`](../../spec/core/lod-crud.md#SPS-CRUD-001) | **Yes** — it has an IRI |
| **Context** | [`SPS-CTX-002`](../../spec/core/contexts.md#SPS-CTX-002) | **Yes** — registered, has an IRI |
| Pod | [`SPS-CORE-007`](../../spec/core/index.md#SPS-CORE-007) | Yes, and far too coarse |

The specification decides at the *context* today and identifies at the *subject*. That gap is the
subject of this document.

One consequence constrains everything that follows.
[`SPS-CRUD-011`](../../spec/core/lod-crud.md#SPS-CRUD-011) makes the resource IRI and the target
context independent dimensions, so a subject's statements may be spread across any number of
contexts and a read returns the union of the readable ones
([`SPS-CRUD-014`](../../spec/core/lod-crud.md#SPS-CRUD-014)).

**There is therefore no containment between a context and a subject.** A context is not the folder a
resource sits in. Any design that inherits permissions downward from a context to the resources
"inside" it is describing a relation this specification does not have.

## What the model already is (IST)

Read as an access-control model rather than as a set of routes, the current chapters describe
something small and consistent:

- The decision unit is the context ([`SPS-GRANT-024`](../../spec/core/grants.md#SPS-GRANT-024)).
- Policy is durable, server-side, and resolved per request from the pair of client and subject
  ([`SPS-GRANT-002`](../../spec/core/grants.md#SPS-GRANT-002)) — never from a token.
- The model is **monotone**: grants only. There is no deny and no exclusion.
- Modes form a small lattice, `manage` ⊃ `write` ⊃ `read`
  ([`SPS-GRANT-009`](../../spec/core/grants.md#SPS-GRANT-009)).
- The owner's authority is implicit and unstored
  ([`SPS-GRANT-011`](../../spec/core/grants.md#SPS-GRANT-011)).
- Silence means private ([`SPS-CTX-027`](../../spec/core/contexts.md#SPS-CTX-027)).

Two of these — monotonicity and the implicit owner — are load-bearing further down and are the
reason the target state is a reframing rather than a replacement.

Delegation to an application is a separate mechanism and stays one: an application receives the
intersection of what it asked for with what the authorizing person holds
([`SPS-GRANT-013`](../../spec/core/grants.md#SPS-GRANT-013)). This is a consent-time computation over
OAuth, not a policy evaluation, and no access-control frame replaces it.

## ACP as the shared contract (SOLL)

What sempods adopts from ACP is **the resolution algorithm and the vocabulary**, not a normative
dependency on a document that is still an editor's draft. The terms are named and profiled here;
their meaning is not restated.

What ACP does **not** define, and what sempods therefore has to supply, is the whole of the
interesting part:

1. **What a resource is.** ACP's `acp:target` binds to "the resource", and the specification never
   says what that is. Its inheritance requires containment information it expects the resource
   server to provide.
2. **How several evaluations compose.** ACP composes *policies* by union within one evaluation. It
   has no operator that joins two evaluations.

Both are sempods' contribution, and both are already implied by the chapters.

### The evaluator chain

A pod declares an ordered — in effect unordered, since the operator is commutative — list of
**evaluators**. Each names what `acp:target` binds to and where its policies come from. A mode is
granted if and only if **every** evaluator grants it.

```
granted = ⋂ evaluate(e, request)   for every configured evaluator e
```

The AND is sempods', not ACP's. Writing it down matters, because an implementer who looks for
conjunction inside ACP will not find it and may reach for `acp:deny` to simulate it — which the
rejected alternatives below explain is the expensive way.

Three properties follow, and all three are wanted:

**It fails closed.** Under ACP, no satisfied policy means no modes. An evaluator with nothing to say
about a resource says *no*, not *don't care*. An implementation MUST NOT add a rule that skips a
silent evaluator; that rule is a privilege escalation wearing the clothes of a convenience.

**Enabling an evaluator is a breaking operation.** Adding a second evaluator to a pod that has no
policies for it removes all access until policies exist. This is correct behaviour and belongs in an
operator's documentation, not in a special case.

**The empty chain is already specified.** A pod with no evaluators grants exactly what
[`SPS-GRANT-011`](../../spec/core/grants.md#SPS-GRANT-011) gives the owner, and nothing else — which
is the safe and complete answer to "what does a pod without any policy do".

## Profiles (SOLL)

Two evaluators are worth defining. They differ only in the binding of `acp:target`.

| | `acp:target` | Where it belongs |
|---|---|---|
| **Context profile** | the context IRI | Core. It is the present model, restated |
| **Resource profile** | the subject IRI | A module, advertised through conformance discovery |

The split is not a compromise between two camps. For most pods the number of distinct audiences is
small, so a permission per named graph is the right size and a second layer would be cost without
benefit. The resource profile earns its keep exactly when a deployment needs **more permission
distinctions than it wants graphs** — at which point graph-level enforcement would require one graph
per audience, and moving a resource between audiences would become a data migration rather than a
policy edit.

Module identity is an IRI under `https://schema.sempods.org/`, and
[`SPS-CORE-006`](../../spec/core/index.md#SPS-CORE-006) already makes advertising one a claim about
every `MUST` in its chapter. A client does not need to understand either profile: it never constructs
a context IRI ([`SPS-CTX-023`](../../spec/core/contexts.md#SPS-CTX-023)) and never derives its
permissions from a token — it asks the pod. **That existing blindness is what makes the policy model
pluggable at all**, and it is why the client-facing contract does not move.

### The precondition the resource profile carries

Where the resource profile is the *only* evaluator, a subject's statements can no longer be
discriminated from one another — the profile decides per subject, and there is no second axis. A pod
providing it must therefore guarantee that **a subject does not span contexts**.

This is not a theoretical caveat. An implementation that reads a subject's policies from the merged
authorization graphs of every context the caller can see, while scoping content per graph, will
authorize content in one context using a policy stored beside another — unless subjects are confined.
The guarantee has to be stated in the module and tested, not assumed from how resources are usually
written.

Where both evaluators run, the axes are orthogonal and compose cleanly: the context evaluator
discriminates statements, the resource evaluator discriminates subjects, and the intersection is
well defined even for a subject that spans contexts.

## Where policy lives (SOLL)

Policies are RDF, held in **authorization graphs** that are not contexts and appear in no registry.
One per context is the right unit: it keeps the separation an implementation needs and makes
[`SPS-CTX-017`](../../spec/core/contexts.md#SPS-CTX-017) — deletion removes the grants naming the
context — a graph drop instead of a query.

They are not contexts for a structural reason rather than a stylistic one. A context carries grants;
if the graph holding grants were itself a context, it would need grants of its own, held in a graph
that needs grants. Keeping authorization graphs outside the registry ends the recursion at the first
step.

Reaching them is a control-plane operation. An ACR is served under its own route and found through a
link relation, the way ACP already describes; it is not addressable through the data path, which
[`SPS-CRUD-004`](../../spec/core/lod-crud.md#SPS-CRUD-004) and
[`SPS-CTX-025`](../../spec/core/contexts.md#SPS-CTX-025) between them already refuse. The
authoritative answer to "what may I do" stays the discovery route, not the raw policy graph.

### The trust boundary is a requirement, not an implementation note

This is the one place where sempods must be stricter than the standard it profiles, because ACP does
not say who may read or write an ACR at all.

> Authorization facts MUST be read from a graph set that no data write can reach.

Without it, the model is trivially defeated: a caller writes a triple that looks like a grant into a
context they may write, and it is read back as policy. The defence is not validation but topology —
the set of graphs consulted for policy and the set writable through the data path are disjoint by
construction, so a forged edge is never in the merge that decides.

**This gives [`SPS-CTX-026`](../../spec/core/contexts.md#SPS-CTX-026) a hazard it does not have
today.** A statement whose subject is a `_system` IRI must be treated as ordinary data, and that is
right — but once policy is RDF, "ordinary data that looks exactly like policy" is a thing a caller
can write. The requirement does not change. What changes is that an implementation reading policy
from anywhere a caller can write is now wrong in a way the text does not currently warn about.

## What the change removes (SOLL)

Both entries below are the argument for doing this at all: the frame makes the specification
*smaller*.

**The owner stops being a special case.**
[`SPS-GRANT-011`](../../spec/core/grants.md#SPS-GRANT-011) is today an extra rule beside the grant
system. Expressed as policy it is one implicit rule every pod carries, evaluated by the same
algorithm as everything else. ACP's owner and creator constants exist precisely because a policy
language of literal values cannot otherwise compare the requesting agent with a fact about the
resource.

**A known defect closes on the way.**
[`SPS-CORE-018`](../../spec/core/index.md#SPS-CORE-018) is recorded as a context-enumeration oracle:
on a write, an unregistered context answers `404` and a registered one the caller may not write
answers `403`, so a caller learns which context IRIs exist. A policy evaluation has no such step —
it asks whether the effective policies grant the mode, and absent policy grants nothing whether or
not the target exists. The two responses converge without a rule being written to make them, which
is the shape [`SPS-CTX-020`](../../spec/core/contexts.md#SPS-CTX-020) already uses for deletion.

## Rejected alternatives

**`acp:deny` and container inheritance.** Both are in ACP and neither is adopted. The present model
is monotone, and monotonicity is what lets an implementation enforce access by composing a policy
check into a query as a join. A deny is a negation over the effective policy set; inheritance adds a
negation over a transitive closure, evaluated per subject per request. Together they change the shape
of enforcement rather than its cost. The price is real and is named here so nobody pays it twice:
"everyone in this group except one person" is not expressible, and must be handled by not putting the
person in the group.

**Additive composition of the two profiles.** Union is ACP's own semantics across policies, and it
was the first thing tried. It fails for the case the resource profile exists to serve: without
`acp:deny`, a context grant unioned with a resource policy overrides it, so the finer layer can only
ever widen access and never protect. A layer that looks like a restriction and cannot restrict is
worse than no layer.

**One ACP evaluation instead of a chain.** Attractive, and not available. The conjunction sempods
needs is between evaluations on different targets, and ACP's `acp:allOf` operates between matchers
inside a single policy. Claiming a single evaluation would mean an implementer looking for the AND in
the wrong specification.

**Renaming `context` to `graph` and reserving `context` for the optional layer.** The two roles a
context plays — the storage unit every statement belongs to, and the unit permissions attach to — are
genuinely distinct, and one of them is optional while the other is not. Two words would say so. But
the rename reaches [`AGENTS.md`](../../AGENTS.md) §Terminology, the first non-negotiable invariant,
the project mission and every chapter, and it buys a distinction that separating the two statements
in [`contexts`](../../spec/core/contexts.md) §1 also buys. The smaller claim is also the truer one:
what is optional is the management of *several* contexts, not the context.

**Conditions authored by the holder of a policy.** A policy that carries its own query — "grant read
where this expression holds" — is the natural way to express a derived relation, and it must not be
allowed. Policy is evaluated with more authority than the caller has, by necessity, so a caller-
supplied expression inside it turns the access decision into an oracle over data the caller may not
read: write a policy whose condition tests someone else's value, request your own resource, and read
the answer off the status code. Derived attributes are therefore a **closed, implementation-defined
vocabulary**: a policy selects a named relation, it does not define one. This is a hardening of what
ACP's extensibility section already recommends, from a `SHOULD` about implementations into a
prohibition on clients.

## Open decisions

**Whether `?context=` may be omitted on a write.** Two decisions have been travelling together and
should not:

- *A canonical default context always exists.* Nearly free. It makes the RDF dataset's default graph
  the ordinary case rather than an excluded one, gives a single-context pod a real story, and leaves
  the first invariant intact — every statement is still in exactly one context.
  [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001) would lose the clause denying it.
- *`?context=` becomes optional on writes, defaulting to it.* This is the one with a cost.
  [`SPS-CRUD-007`](../../spec/core/lod-crud.md#SPS-CRUD-007) requires the parameter and
  [`SPS-GRANT-025`](../../spec/core/grants.md#SPS-GRANT-025) forbids an implicit target; the fourth
  invariant in [`AGENTS.md`](../../AGENTS.md) states it as non-negotiable, so this is a governance
  decision and not a text edit.

The cost is not the one the invariant was written against. A private default makes omission safe
rather than leaky, so the [`SPS-CTX-027`](../../spec/core/contexts.md#SPS-CTX-027) argument does not
carry over. The cost is **fragmentation**: a client that omits the parameter on some writes spreads
one subject across two contexts, which [`SPS-CRUD-011`](../../spec/core/lod-crud.md#SPS-CRUD-011)
permits and nothing reports. It is invisible to the author, whose own reads union the contexts back
together, and it surfaces later as a resource that looks incomplete to somebody else — with
[`SPS-CRUD-017`](../../spec/core/lod-crud.md#SPS-CRUD-017) deliberately making "unreadable" and "not
there" indistinguishable, so the diagnosis is unavailable by design.

It also removes the precondition the resource profile depends on: a subject silently split across
contexts is exactly what that profile may not have.

The safe corridor is narrow and worth stating: omission is harmless on a pod where the default
context is the *only* context, because nothing can fragment. That is a property a pod can declare and
a client can discover, rather than a behaviour that changes the first time somebody creates a second
context.

## Not in scope

- **How an application receives a subset of a person's access.** That is consent-time intersection
  over OAuth ([`grants`](../../spec/core/grants.md) §5), and it is orthogonal: it decides what an
  application holds, not what a policy grants.
- **Identity.** Who the agent, client and issuer *are* is [`auth`](../../spec/core/auth.md) and the
  `oidc` module. Access control consumes those as facts.
- **Enforcement strategy.** Whether an implementation filters after reading, prunes a dataset, or
  composes the check into a query is its own affair. The sixth invariant in
  [`AGENTS.md`](../../AGENTS.md) prefers explicit specification and conformance tests over clever
  rewriting for exactly this reason: the contract is the policy vocabulary and the resolution
  algorithm, and a strategy that satisfies it is conformant however it is built.
- **Interoperability with Solid's own protocol.** Adopting ACP's evaluation model does not make a pod
  a Solid server, and nothing here should be read as claiming it. That would be a separate goal with
  a separate cost, and the project mission does not currently name it.
