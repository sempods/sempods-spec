# Access control (Concept)

## Purpose

sempods identifies a resource by its LOD IRI — an RDF subject — but decides access at a different
unit: the context that holds a statement. Both units are useful, and treating either as the whole
model is what creates the tension. A context is too coarse for document-level audiences; a subject
alone cannot distinguish statements deliberately placed in different security domains.

The target model keeps the context as the deciding unit and adds the finer one where a deployment
needs it. **Every pod decides on contexts. A pod that needs audiences smaller than a context declares
a second decision, and both must allow.**

What becomes optional is not the context. Every statement belongs to exactly one, always. What a pod
may leave out is the **management of several** — the lifecycle — and a pod that leaves it out has one
canonical context, carrying policy like any other, with nothing for a client to choose between. The
catalogue is not on that list: it is where a client reads the name a write has to carry.

A write still names it. Invariant 4 forbids an implicit fallback context, and having only one
candidate is exactly the situation where a fallback is tempting and where it costs nothing to refuse:
the client reads the one context and names it, the same call it would make with fifty. What a
one-context pod removes is the *choice*, not the naming.

**This document is about what is decided, never about how.** Two pods that answer every request
alike are equally conformant, whether one evaluates a policy language and the other has the rules in
its code — [`../vision.md`](../vision.md) says why that is the shape of the contract rather than a
concession. The reference implementation's own answer, expressing all of this in one small profile
of the Solid Community Group's Access Control Policy, is in
[`../reference-implementation/acp-profile.md`](../reference-implementation/acp-profile.md), and the
worked scenarios in [`../../examples/`](../../examples/README.md) are the evidence that it holds.

Sections below are marked **IST** (specified today, verifiable against the chapters) or **SOLL**
(target state). The SOLL has no roadmap yet and touches requirements that are in force —
"Specification impact" names them. Nothing here is adopted by having been written down.

## The two decision units (IST)

Five things in the specification could carry a permission. Only two have a stable identity at a
useful granularity.

| Candidate | Defined by | Useful as a decision unit |
|---|---|---|
| Statement | [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001) | No, and not for want of an address — see below |
| Slot `(subject, predicate)` in one context | [`lod-crud`](../../spec/core/lod-crud.md) §5 | No — policy would be repeated per predicate |
| **Resource** (subject) | [`SPS-CRUD-001`](../../spec/core/lod-crud.md#SPS-CRUD-001) | **Yes** — it has an LOD IRI |
| **Context** (named graph) | [`SPS-CTX-002`](../../spec/core/contexts.md#SPS-CTX-002) | **Yes** — it is registered under an IRI |
| Pod | [`SPS-CORE-007`](../../spec/core/index.md#SPS-CORE-007) | Only for bootstrapping authority |

The current specification chooses the context. Every statement belongs to exactly one context
([`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001)); reads expose only readable contexts and
writes land in one explicitly named context
([`SPS-GRANT-024`](../../spec/core/grants.md#SPS-GRANT-024),
[`SPS-GRANT-025`](../../spec/core/grants.md#SPS-GRANT-025)). The resource IRI and context remain
independent, so one subject may have statements in several contexts
([`SPS-CRUD-011`](../../spec/core/lod-crud.md#SPS-CRUD-011)).

The statement is rejected for a reason worth stating precisely, because half of it is addressable.
The single-edge route names exactly `(subject, predicate, target)`, and
[`SPS-CRUD-042`](../../spec/core/lod-crud.md#SPS-CRUD-042) defines deletion through it — but only
where the object is an IRI. A decision unit that covers IRI-valued statements and not literal-valued
ones would be partial by construction, and one policy per statement is a policy per triple. It is the
granularity that fails, not the addressing.

There is consequently no containment relation between a context and a resource. A context is not
the folder in which a resource lives, and no inheritance mechanism can manufacture that relation.

A context is best read as an **area**: something a caller may enter, addressed by an IRI the pod hands
out, carrying its own permission boundary. That is what
[`SPS-CTX-021`](../../spec/core/contexts.md#SPS-CTX-021) reports — the permissions held *on* the
context, not a summary of everything within it, which is why finer policy inside an area does not
contradict it, any more than a readable folder is contradicted by a file it hides. The reading has two
limits, and both are deliberate rules rather than oversights: deleting an area leaves the areas
beneath it standing ([`SPS-CTX-018`](../../spec/modules/context-management.md#SPS-CTX-018)), and a resource does not
live *in* one — a subject may hold statements in several areas at once, and a read returns the union
of those the caller may see.

## The current model (IST)

Read as one access-control model, the current chapters say:

- policy is durable server-side state, resolved on every request from the verified client and OAuth
  subject rather than trusted from a token
  ([`SPS-GRANT-002`](../../spec/core/grants.md#SPS-GRANT-002));
- grants are positive and therefore monotone — there is no deny or exclusion;
- `manage` implies `write`, and `write` implies `read`
  ([`SPS-GRANT-009`](../../spec/core/grants.md#SPS-GRANT-009));
- the owner's authority is implicit and unstored
  ([`SPS-GRANT-011`](../../spec/core/grants.md#SPS-GRANT-011));
- silence is private ([`SPS-CTX-030`](../../spec/core/contexts.md#SPS-CTX-030), which
  [`SPS-CTX-027`](../../spec/modules/context-management.md#SPS-CTX-027) applies to a creation request); and,
- OAuth delegation is a ceiling: an application receives no more than the authorizing person holds
  ([`SPS-GRANT-013`](../../spec/core/grants.md#SPS-GRANT-013)).

Those properties survive the target model. What changes is the unit against which policy is first
resolved.

## What rests on running code (IST)

The target state is not uniformly speculative, and a reader should be able to tell which half they
are in. While the specification is descriptive ([`GOVERNANCE.md`](../../GOVERNANCE.md)), a section
describing something no implementation does is a proposal; one describing something that runs is a
reframing of it, and far less likely to be wrong.

**Running today**, in the reference implementation or in a deployment built on this model:

- deciding access on a context, with every property listed under "The current model" above;
- the OAuth ceiling — the consent-time intersection, resolution per request from the client and
  subject pair, and the revocation sweep;
- the topological trust boundary: authorization facts read only from a graph set that content writes
  cannot reach, with a graph's role fixed by its origin rather than by classifying it by name; and,
- a second, finer decision composed by intersection with the first — in one deployment, enforced by
  rewriting a query rather than by anything this concept describes.

**Design, with nothing implementing it yet:**

- the finer decision as a *declared* second decision a client is told about, rather than one
  deployment's internal arrangement; and,
- everything under "Operation boundaries" beyond what the read and write paths already enforce.

The line matters most where the two meet. **The composition rule is the part with a deployment behind
it; announcing it as a declared capability is the part with none.** So the intersection is the least
likely thing here to be wrong.

## One decision always, a second by declaration (SOLL)

Every conforming pod evaluates **context** policy. That is the decision the chapters already
describe, and it stays where it is: the target is a context IRI, the answer governs every statement
the context holds, and a pod that never hears of anything below it is complete.

Two things vary around that, and they are independent of each other.

**The management of several contexts.** A pod that provides it exposes the lifecycle and the read
downscope the chapters specify today. The catalogue and the explicit write target are not on that
list: a write names its context either way, and the route a client reads that name from is needed
most where there is only one. A pod that does not has
one canonical context — carrying policy exactly like any other, so sharing is still a policy on a
context — and nothing for a client to select between. Every statement still belongs to exactly one
context either way; what is absent is the choosing, not the context.

**A second decision on a finer target.** Where audiences are smaller than a context — a space whose
documents are not all for the same readers — a pod declares the finer decision, and it is made
about a subject IRI as well. For a statement `q = (subject, predicate, object, context)`:

```text
without the module:  visible(q) = contextAllows(context, read)

with the module:     visible(q) = contextAllows(context, read)
                                    AND resourceAllows(subject, read)
```

The same intersection applies to the requested mode on updates and deletes. It is sempods'
composition rule of sempods, and not something a policy language supplies: the two decisions have
different targets, and no policy vocabulary has an operator that joins two evaluations.

Both are declared rather than inferred. A module is advertised, and
[`SPS-CORE-006`](../../spec/core/index.md#SPS-CORE-006) makes advertising one a claim about every
`MUST` in it. **Neither may be an internal arrangement of a deployment**: a client receiving `404`
must be able to find out whether a second decision exists, or it cannot tell a missing resource from
a hidden one — and two pods would then differ in observable behaviour with no contract between them.
How policies are written, where they are stored and how the decision is enforced stay entirely a
deployment's own business.

An evaluator with no matching policy denies, so turning the resource module on before resource
policies exist removes access rather than adding a layer. That is correct and it is a breaking
operation, not a feature toggle.

A subject may span any number of contexts, and the two decisions stay orthogonal: the context
evaluator discriminates statements, the resource evaluator discriminates subjects, and the
intersection is well defined either way. No policy is discovered by merging the authorization graphs
adjacent to whichever data contexts a caller can already see.

### OAuth remains a ceiling

Policy answers what the verified agent and client may do now. OAuth delegation answers how much of
the agent's non-public authority the client received. Neither substitutes for the other:

```text
authenticated modes = delegated client ceiling
                      ∩ context policy decision
                      ∩ optional resource policy decision

public modes = { read } if public context policy allows read
                         and, where the resource module is declared,
                         public resource policy allows read
               ∅ otherwise

effective modes = authenticated modes ∪ public modes
```

**A service token is the case that formula does not describe**, and it is not a corner: it is a
mandatory flow. There is no person, the subject **is** the client
([`SPS-AUTH-017`](../../spec/core/auth.md#SPS-AUTH-017)), and its grants are fixed at registration
and are per-context only ([`SPS-AUTH-013`](../../spec/core/auth.md#SPS-AUTH-013)) — so there is no
delegation to bound, because nobody delegated. Reading a per-principal ceiling into it would deny
every service client or invent an artifact the contract does not have:

```text
service modes = registered per-context grant
                ∩ optional resource policy decision

effective modes = service modes ∪ public modes
```

The registered grant takes the place of the ceiling *and* the context policy, which is what
"fixed at registration" means. The resource decision still narrows where the module is declared, for
the same reason it narrows anywhere: a decision that can only subtract is not made safe to skip by
who is asking.

The public branch unions here too, and for the reason it does everywhere: public authority does not
come from anybody's grant, so nothing anybody was granted can take it away. Leaving it out would make
a service client the one caller that loses access by presenting a token — the same request without it
reads the public context perfectly well.

The ceiling is **its own decision**, about the pair of person and application, and it is not a rule
on the target — merging it into one would compose by union where a ceiling can only restrict. It is
keyed by the verified client identifier whatever shape that has: `did:web:` for a client identifying
itself by origin, `dyn:` for one registered dynamically
([`SPS-AUTH-008`](../../spec/core/auth.md#SPS-AUTH-008),
[`SPS-AUTH-003`](../../spec/core/auth.md#SPS-AUTH-003)).

A policy language can *hold* a ceiling but not *produce* one: `granted = requested ∩ effective`
([`SPS-GRANT-013`](../../spec/core/grants.md#SPS-GRANT-013)) is a computation at consent time, and
the revocation sweep ([`SPS-GRANT-015`](../../spec/core/grants.md#SPS-GRANT-015),
[`SPS-GRANT-016`](../../spec/core/grants.md#SPS-GRANT-016)) is a recomputation over the store.
Evaluation reads a state; it does not establish one.

This preserves immediate policy revocation and the distinction between agent and client. That an
application is not broadened by a policy written for the person is the property being aimed at rather
than one the model already has: a ceiling agreed over a scope reaches whatever enters that scope
afterwards, which is the open decision recorded below. Public authority
does not come from the agent and therefore cannot be delegated or removed by the agent's OAuth
ceiling. The ceiling constrains **modes**, and whether it can also constrain targets is open in a way worth
being exact about: with the ceiling keyed to the principal, one evaluation answers for every request
that person makes, and nothing in it names the data target — so a per-target ceiling needs either a
second artifact carrying the target or a sempods rule selecting among several delegation policies.
That is the scope question recorded below, and it is unanswered rather than merely unwritten. OAuth
owns how a person selects the subset, while access control owns the per-request decision.

Public access becomes an ordinary context policy and, where the resource module is enabled, an
ordinary resource decision as well, matched by whatever stands for "anybody". Anonymous access is
permitted for `read` only; anonymous `write` or `manage` is not part of the target model. A `public`
convenience field may project to that policy, but it is not a second decision path. An authenticated
request remains able to read what an unauthenticated request can read; the present `public-read`
scope therefore has to be reconsidered when this target state becomes a roadmap.

## Operation boundaries (SOLL)

`read` authorization is evaluated per candidate statement. Resource retrieval and find discard a
statement before it can contribute to an answer. SPARQL executes against a server-derived statement
view that already excludes denied statements before query algebra, joins, filters, aggregates or
result construction can observe them. Selecting readable contexts is what builds that view; where the
resource module is declared it narrows further, and neither replaces the other.

For find the boundary has to sit ahead of the whole pipeline — matching and index lookup, hit
selection, ranking, `limit` and expansion — and not around the graph that comes back. The reason is
in the chapter: [`SPS-FIND-008`](../../spec/core/find.md#SPS-FIND-008) permits an implementation to
match *through* a linked resource and return only the requested types, so an index that matched on a
denied statement could still decide which permitted resource appears as a hit. A resource nobody may
read must not be able to nominate one that everybody may.
[`SPS-FIND-010`](../../spec/core/find.md#SPS-FIND-010) already states this shape for the context
downscope — the whole operation, expansion included — and the authorized statement view needs the
same reach.

Filtering a completed SPARQL result is not sound: an inaccessible statement may already have
changed an `ASK`, aggregate, negation or join even when no final binding names it.

The authorized statement view **is** the dataset the query executes against. SPARQL 1.1 §13 defines
an RDF Dataset as a default graph plus zero or more named graphs and does not require those graphs to
be the ones a store holds, so a dataset assembled by filtering is a dataset. The property
[`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009) protects therefore survives intact —
one decision the engine cannot see around, no rewriting — and the requirement needs precision rather
than replacement.

```text
physical store → authorized statement view → effective dataset → unchanged SPARQL algebra
```

[`SPS-SPARQL-007`](../../spec/core/sparql.md#SPS-SPARQL-007) is the one that has to move: it fixes
what a query may see as *the readable contexts*, which is too permissive once individual subjects
inside a readable context are denied. Both are listed under "Specification impact".

Existing-resource mutations require the requested mode on the target context always and, where the
resource module is declared, on the resource as well. Slot and edge operations use their subject as the resource
target. SPARQL remains read-only
([`SPS-SPARQL-006`](../../spec/core/sparql.md#SPS-SPARQL-006)); the target model does not add a
second mutation path beside CRUD, and client-supplied dataset clauses never expand the server-derived
statement view ([`SPS-SPARQL-008`](../../spec/core/sparql.md#SPS-SPARQL-008)).

Creation keeps the rule the chapters already carry: its authority comes from the destination, so
creating a resource needs `write` on the target context and creating a context needs `manage`
covering it ([`SPS-CTX-019`](../../spec/modules/context-management.md#SPS-CTX-019),
[`SPS-GRANT-033`](../../spec/core/grants.md#SPS-GRANT-033)). Where the resource module is not
declared that is the whole operation, because a new resource is covered by its context's policy from
the moment it exists. Where it is, context `write` still says who may *begin* the creation, and
finishing it also installs the resource policy described below — one operation, or the resource is
born unreachable or reachable when it should not be.

**Deleting a context is the operation the composition rule does not yet reach.** It removes every
statement the context holds ([`SPS-CTX-017`](../../spec/modules/context-management.md#SPS-CTX-017)) and is
authorized from the context grant alone
([`SPS-CTX-019`](../../spec/modules/context-management.md#SPS-CTX-019)), so with the resource module declared a
caller holding `manage` on a context destroys statements about subjects whose resource policies
refuse them `write` — the one route where the second decision is skipped rather than applied. The
rule above covers mutations of an existing resource; a bulk lifecycle operation is not one of those
and needs saying either way. The two ways to say it:

- ~~compose it like any other mutation~~, requiring the resource decision to allow `write` on every
  affected subject. **Refused for the same reason as the shared-policy version above**: a caller who
  manages the context and is denied one hidden subject gets a failure the same request against an
  empty context does not get, so the outcome reports that the context holds something they may not
  see. That is the pattern this repository keeps — the same answer for a context you cannot read as
  for one that holds nothing — and it is not a cost to weigh against the alternative; and,
- **state it as an exception**, on the ground that `manage` on a context already means creating and
  deleting the context itself rather than editing what is in it, and that a context nobody may enter
  is not made safer by the policies inside it.

Which leaves the exception, and what is open is writing it down rather than choosing it: it is the
one place the words "both must allow" stop being true, so it has to be stated where the composition
rule is rather than left to be inferred. Not reachable today — the module does not exist — but
reachable the moment it does.

The resource module reopens the question, and only there. A new resource has no resource policy yet,
so creation and that policy have to be one operation from the client's perspective — otherwise the
resource is born unreachable, or reachable while it should not be. Which bootstrap policy applies is
an open design choice; what is not open is that silent creation without one leaves the module
incomplete.

Authorization is checked before target existence wherever different responses would reveal protected
topology. A policy model does not close an enumeration oracle by itself: the HTTP contract still has to make an
unknown target and an inaccessible target indistinguishable to a caller outside its authority. That
is the open half of [`SPS-CORE-018`](../../spec/core/index.md#SPS-CORE-018), and the shape it needs is
the one [`SPS-CTX-020`](../../spec/modules/context-management.md#SPS-CTX-020) already uses for deletion.

## Who may share, and why there is no chain (SOLL)

Passing access to another person requires `manage` on the context. Reading it is not enough, and the
difference is the whole design: a reader who may pass on what they can already see turns every grant
into the root of a tree somebody has to keep.

Every holder of `manage` on a context is a peer of every other. There is no first among them and no
order of precedence — a person granted `manage` yesterday may remove the grants of the person who
granted it, and either may remove anybody else's. What makes that safe rather than reckless is a
floor the pod supplies and nobody can edit: the owner holds every mode on every context implicitly,
and [`SPS-GRANT-011`](../../spec/core/grants.md#SPS-GRANT-011) forbids requiring those grants to be
stored, so there is no row for a peer to delete. A peer set cannot empty itself out from under the
pod.

**And that is what removes the chain.** A share is always issued directly by somebody holding
`manage` at the moment they issue it, so there is no derived access to trace and no provenance to
keep: deciding whether a grant may be removed never requires knowing who wrote it. What a peer does
on revocation is recompute the remaining authority — the instruction
[`SPS-GRANT-016`](../../spec/core/grants.md#SPS-GRANT-016) already gives for delegations, and not one
step deeper.

The alternative was reading being enough, and its cost is measured rather than asserted.
[`examples/70-resharing.md`](../../examples/70-resharing.md) shows two states that compile to the
same access control resource — a defect and a correct outcome, told apart by nothing in the graph —
because what separates them is who issued which grant, and a policy has no room for that. Provenance
kept beside the access control resource is the price, and a resource whose policy no longer explains
itself is what it buys.

Because `manage` is slash-delimited ([`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007)),
this is a tree of peer sets rather than one: a peer on `projects` is a peer on `projects/alpha`, and
a peer on `projects/alpha` is not a peer anywhere above it.

What none of this decides is whether a pod offers a sharing surface at all. **None is specified.** No
route writes a grant for a person, and the model above is the shape such a route would need rather
than one that exists — which is what makes leaving it out a decision instead of an omission.

## What becomes smaller (SOLL)

The target state removes parallel authorization concepts rather than merely renaming them:

- public access is a public-agent policy rather than a flag. What goes is the flag and the second
  *vocabulary*, not the union: the formula above still adds the public branch to whatever the
  authenticated one produced, so presenting a token can never remove access an anonymous request
  would have had. One engine, one policy language, and one place where two answers are combined;
- owner access is an implicit system policy evaluated by the common engine;
- direct users, clients, groups and tenant-wide audiences are conditions of one kind, not four
  mechanisms;
- context policy and resource policy are one vocabulary and one algorithm differing only in what
  the decision binds to, so a tool that reads one reads the other; and,
- a pod that manages one context has no context management surface, without the context ceasing to
  exist.

The remaining complexity is visible where it belongs: a deployment whose audiences are smaller than
its contexts opts into a second decision, and every other deployment never meets it.

## Specification impact (SOLL)

The target state keeps the deciding unit the chapters already use and adds a finer one behind a
declaration, so most of what is in force is untouched. What moves is listed here, because
[`AGENTS.md`](../../AGENTS.md) §"Non-negotiable invariants" says an invariant is refused rather than
debated and that rule cannot be applied to a proposal which does not name what it reaches.

| In force today | What the target state does to it |
|---|---|
| [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001) — there is no default context | A pod that does not manage several has one, canonical and carrying policy. The invariant it serves — every statement in exactly one context — survives untouched |
| Invariant 4 and [`SPS-CRUD-007`](../../spec/core/lod-crud.md#SPS-CRUD-007) — a write names its target context explicitly | Untouched. A pod with one context has no choice to offer and still takes the name, because an implicit fallback is what the invariant forbids and one candidate is where it would appear |
| [`SPS-GRANT-025`](../../spec/core/grants.md#SPS-GRANT-025) — no implicit or default write context | The same, seen from the grants chapter |
| [`SPS-CTX-003`](../../spec/core/contexts.md#SPS-CTX-003) — no permission abstraction above or beside the context | Has to permit a **narrowing** layer below one. The rule was written against a second concept competing with the context; a decision that can only subtract from it is not that |
| [`SPS-CORE-004`](../../spec/core/index.md#SPS-CORE-004) — every `MUST` in `contexts` is core, with no partial core | Adding the resource module does not touch it. Letting a pod omit the *management* of several contexts did, and **that sweep has since run** — the requirements below now stand in [`modules/context-management.md`](../../spec/modules/context-management.md), keeping their identifiers. It is recorded here because the set was larger than the two obvious entries: the management route ([`SPS-CTX-005`](../../spec/modules/context-management.md#SPS-CTX-005)) and creation ([`SPS-CTX-015`](../../spec/modules/context-management.md#SPS-CTX-015)) carry with them freely chosen names ([`SPS-CTX-009`](../../spec/modules/context-management.md#SPS-CTX-009)), idempotent creation ([`SPS-CTX-016`](../../spec/modules/context-management.md#SPS-CTX-016)), deletion and its cascade boundary ([`SPS-CTX-017`](../../spec/modules/context-management.md#SPS-CTX-017), [`SPS-CTX-018`](../../spec/modules/context-management.md#SPS-CTX-018)), and the lifecycle authorization and its non-enumeration rule ([`SPS-CTX-019`](../../spec/modules/context-management.md#SPS-CTX-019), [`SPS-CTX-020`](../../spec/modules/context-management.md#SPS-CTX-020)). Each of those is a `MUST` about an operation a pod with no management surface does not offer, so a sweep naming only the first two would leave core requiring what the declaration removed. Discovery ([`SPS-CTX-021`](../../spec/core/contexts.md#SPS-CTX-021)) stays where it is: a write names its context and a client may not construct that IRI, so the route it reads the name from is needed most in the pod with the fewest contexts |
| [`SPS-CRUD-020`](../../spec/core/lod-crud.md#SPS-CRUD-020) — `GET` returns every statement whose subject is the resource IRI and is visible in the selected contexts | Right for the base decision and too generous once a second one denies individual statements. Only a pod declaring the resource module needs it restated over the authorized statement view — the same move `SPARQL` makes, and it has to move with it or the two chapters describe different results |
| [`SPS-CTX-015`](../../spec/modules/context-management.md#SPS-CTX-015) and [`SPS-CTX-027`](../../spec/modules/context-management.md#SPS-CTX-027) — creation may carry a `public` flag, and its absence creates a private context | Both survive. What the target removes is the **second resolution path**, not the field: `public: true` becomes a request to install a public-agent policy, and `SPS-CTX-027`'"'"'s private default becomes the absence of one, which is the same answer arrived at by the ordinary route. A sweep that withdrew the field would break a creation contract for no gain; one that left it as a flag the evaluator reads would keep the branch the target exists to remove |
| [`SPS-MCP-008`](../../spec/modules/mcp.md#SPS-MCP-008), [`SPS-MCP-018`](../../spec/modules/mcp.md#SPS-MCP-018) and [`SPS-MCP-019`](../../spec/modules/mcp.md#SPS-MCP-019) — a bearer'"'"'s sandbox is the resolved context grants, and every tool is a projection of the HTTP surface | `SPS-MCP-018` is the one that saves the sweep work and the one that makes it unavoidable: a tool may not have an authority the HTTP surface lacks, so the tools narrow with the routes automatically — but only if `SPS-MCP-008` stops defining the sandbox from context grants alone. Left as it is, the projection rule and the sandbox rule contradict each other the moment the module is declared |
| [`SPS-MEDIA-009`](../../spec/modules/media.md#SPS-MEDIA-009) — a media is readable exactly when its assignment set intersects the caller'"'"'s readable contexts, and no media-specific authorization is added | "Exactly when" is the part that moves. A media whose bytes are described by statements a resource decision denies is not made readable by its context assignment, and the requirement as written says it is. The rule against media-*specific* authorization stays and is the reason this is a restatement rather than a new check |
| [`SPS-CORE-011`](../../spec/core/index.md#SPS-CORE-011) and [`SPS-CORE-012`](../../spec/core/index.md#SPS-CORE-012) — every module is announced by IRI in `modules`, and one absent from it is not provided | The resource module needs an IRI of its own and an entry there, or a client has no conforming way to learn that the second decision is being made — and `SPS-CORE-012` says probing the routes is not that way. The same holds for letting a pod omit the management of several contexts, which is a second thing a client has to be told rather than discover |
| [`SPS-CRUD-040`](../../spec/core/lod-crud.md#SPS-CRUD-040), [`SPS-CRUD-041`](../../spec/core/lod-crud.md#SPS-CRUD-041) and [`SPS-CRUD-042`](../../spec/core/lod-crud.md#SPS-CRUD-042) — the resource-node, slot and edge routes offer their mutations with §4's semantics | The second decision applies to each of them **where the subject already exists**. A sweep that gated reads and left writes to the context alone would produce a pod where a caller reads less than they may write, which is not "both must allow" in either direction. Creation is the exception and has to be written as one: a `PUT` bringing a subject into being has no resource policy to consult, so it is authorized from the context and installs the initial policy in the same operation. Gating it on a decision that does not exist yet would deny every creation. **What the split needs before it can be written is a collision rule** — see the open decisions |
| [`SPS-CRUD-010`](../../spec/core/lod-crud.md#SPS-CRUD-010) and [`SPS-CORE-014`](../../spec/core/index.md#SPS-CORE-014) — the status codes, and which denial gets which | Gains a second way to be refused, and the code has to be chosen rather than inherited. The property to hold on to is the one [`SPS-CRUD-017`](../../spec/core/lod-crud.md#SPS-CRUD-017) already states for reads: a resource that is absent, one in a context the caller cannot read, and one that does not exist answer alike. Either code can preserve it — `404` because it is already the answer for "absent or invisible", `403` only if it is also given for targets that do not exist — and either can break it if only one branch changes. This is the denial half of the sweep and belongs in it |
| [`SPS-CRUD-041`](../../spec/core/lod-crud.md#SPS-CRUD-041) and [`SPS-CRUD-057`](../../spec/core/lod-crud.md#SPS-CRUD-057) — a slot `GET` returns all values, across the readable contexts | The same restatement, and it has to be made here too rather than only on the LOD route. A conforming pod would otherwise hide a subject's statements at one address and hand them over at another, which is not a narrower answer but a different one |
| [`SPS-FIND-014`](../../spec/core/find.md#SPS-FIND-014) — the context sandbox applies to `find` exactly as to CRUD and SPARQL | Holds, and stays true by being restated with them rather than despite them: the sentence is that `find` is sandboxed the same way, so the restatement is what keeps it accurate. Matching, ranking and expansion all read statements, so the denied ones have to be gone before any of that, not filtered out of the results afterwards |
| [`SPS-SPARQL-007`](../../spec/core/sparql.md#SPS-SPARQL-007) and [`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009) — a query sees exactly the readable contexts, and the dataset carries the restriction | Exactly right for the base decision, which is graph-granular and expressible as a dataset against any store. Only a pod enabling the resource module needs them restated over an authorized statement view |

None of these is a reversal of intent. The mission's third goal — *"graph-based access control where
the 4th RDF dimension … is called Context"* — stays true, because the graph dimension remains the
decision every pod makes. Invariants 2 and 3 are untouched for the same reason: the sandboxes are
stated over contexts, and contexts are always there.
The grant grammar of [`grants`](../../spec/core/grants.md) §2 is untouched because grants stay keyed
by context.

What else survives is worth stating beside it. Invariant 1 holds unchanged, and so does every
property listed under "The current model" above: monotone policy, the mode implications, the implicit
owner, silence as private, and the OAuth ceiling.

Adoption requires one coherent change to the affected core and module contracts, their conformance
descriptions and the implementation. The concept records why that change has this shape; it is not a
second contract beside the specification chapters.

## Rejected alternatives

**Security labels as machine-managed graphs.** Assigning every statement to a graph that stands for
an audience, evaluating policy once per label and assembling the dataset from the labels that pass,
would keep the restriction in the dataset and leave the whole of SPARQL usable. It holds only while
audiences are shared. The label set is the product of the dimensions that must all be satisfied, so a
deployment layering an area, a resource and anything finer arrives at one label per resource and the
dataset degenerates into an enumeration. What is worth keeping from it is the part that already
survives elsewhere: membership resolved at access time, so changing who is in a group moves no data.

**The context as the only policy unit.** Keeping it the sole decision works while every audience
aligns with a graph, and stops working exactly where an audience is smaller than one. A deployment
that needed finer audiences would create a graph per permission set, which turns changing an
audience into moving data rather than editing a rule, and grows the number of graphs with the number
of distinct audiences rather than with how a pod is actually organised. Hence the finer decision —
optional, because most deployments never reach that point.

**A configurable evaluator chain.** A generic list — evaluators assembled per deployment, meaning
settled locally — creates an empty-chain identity problem and lets two conforming pods attach
incompatible meaning to the same request. A **closed set of named, advertised** combinations is not
that: the meaning is fixed per name, a client asks once, and
[`SPS-CORE-006`](../../spec/core/index.md#SPS-CORE-006) turns advertising one into a claim a
conformance suite can test.

**Additive composition of resource and context decisions.** Union lets either dimension override
the other. A document policy that appears to restrict a broad context grant would then be unable to
restrict it. Independent security boundaries compose by intersection.

**Client-authored conditions.** Policy evaluation necessarily runs with more authority than the
caller. Letting a caller supply a query as a condition turns the decision into an oracle over data
the caller cannot read. Named, closed, server-resolved relations provide enterprise attributes
without executing policy-holder code.

## Open decisions before a roadmap

Two are larger than the rest and come first.

**A ceiling reaches further than it was agreed for.** [`grants`](../../spec/core/grants.md) §5 and §6
survive the target state intact — an application still asks for a set of contexts and receives the
intersection with what the person effectively holds
([`SPS-GRANT-013`](../../spec/core/grants.md#SPS-GRANT-013),
[`SPS-GRANT-028`](../../spec/core/grants.md#SPS-GRANT-028)), and narrowing a person's own access
still sweeps every delegation no longer covered
([`SPS-GRANT-015`](../../spec/core/grants.md#SPS-GRANT-015),
[`SPS-GRANT-016`](../../spec/core/grants.md#SPS-GRANT-016)). The catalogue they rest on is still
there, because contexts are.

What is unresolved is subtler. A ceiling agreed once is **coarser than the decisions it bounds**, so it reaches resources that enter
its scope afterwards: a policy giving somebody access to one more document is reached by every
application they had already authorised, and nobody was asked again.
[`SPS-GRANT-019`](../../spec/core/grants.md#SPS-GRANT-019) is kept to the letter — no grant was
widened, a policy was changed, and those are different acts — while the reason it gives, that
regaining access should not silently re-arm every application that once wanted it, is walked around.
[`examples/50-delegation.md`](../../examples/50-delegation.md) is what the untreated case looks like.

Two shapes avoid it, and neither is free. A ceiling can be an **enumerated set a person extends**
rather than a scope that tracks — the pattern a photo picker uses when it hands an application
selected items instead of a library, so consent per resource is impractical as a dialog but not
impossible as a selection; it costs an interaction for each batch of new resources and a set that
grows without bound. Or the widening can stand and be made **visible**, which prevents nothing but
meets what the rule is for: `SPS-GRANT-019` guards against re-arming an application *silently*, not
against re-arming it.

The rest are ordinary open questions:

- Decide whether `public-read` still earns a scope. Nothing about public access has to be withdrawn —
  the `public` flag, its private default and the guarantee that an unauthenticated caller reads
  exactly the public contexts all keep their subject
  ([`SPS-CTX-027`](../../spec/modules/context-management.md#SPS-CTX-027),
  [`SPS-GRANT-031`](../../spec/core/grants.md#SPS-GRANT-031)). But once a public context carries an
  ordinary policy matched by whatever stands for "anybody", an anonymous request is already satisfied
  by the policy, and the scope
  ([`SPS-GRANT-020`](../../spec/core/grants.md#SPS-GRANT-020)) is left doing only what the OAuth
  ceiling does anyway.

- State, once the module exists, that deleting a context is authorized by context `manage` alone and
  that the resource decision does not narrow it — the one exception to "both must allow". Composing
  it instead is refused above, because failing on a subject the caller cannot see reports that the
  subject exists. What needs deciding is the wording and where it sits, not which way it goes.
- Mint the resource module's IRI and say what its `modules` entry carries, and do the same for the
  declaration that a pod manages several contexts. Without them a client cannot tell a pod making
  one decision from a pod making two, and `SPS-CORE-012` closes the fallback: a module absent from
  the list is not provided, and probing its routes is not discovery.
- Write mode closure as a requirement on what a pod accepts: a decision whose modes are not
  closed under [`SPS-GRANT-009`](../../spec/core/grants.md#SPS-GRANT-009) is refused rather than
  stored. It cannot stay a convention, because the state it produces is one the model forbids rather
  than a narrower one, and `manage` on a target is enough to write the rules by hand.
- Define what the resource module changes in the surfaces around it: whether `find` filters, the MCP
  tool arguments and the media surface acquire a resource dimension, or inherit the context one
  unchanged.
- Decide how far the context reaches into the client-facing surfaces of a pod that manages one —
  `find` filters and the MCP tool arguments may carry a context dimension or leave it out. Hiding it
  everywhere is not among the options: a write still names the context, and a client may not
  construct that IRI ([`SPS-CTX-023`](../../spec/core/contexts.md#SPS-CTX-023)), so the discovery
  route stays the pod-supplied source it reads the name from.
- Restate [`SPS-SPARQL-007`](../../spec/core/sparql.md#SPS-SPARQL-007) over the authorized statement
  view and make [`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009) precise about what a
  dataset is. The constraint to weigh while wording them: the SPARQL protocol lets a client *describe*
  a requested dataset through graph IRIs, while the **query service** constructs the authorized
  effective dataset — which is why
  [`SPS-SPARQL-008`](../../spec/core/sparql.md#SPS-SPARQL-008) can refuse the description any widening
  power. With a remote store the query service therefore needs either a trusted statement-level
  filtering facility in that store, or local construction and evaluation of the effective dataset.
  Passing an unchanged query down with a list of permitted graph IRIs is the one answer that is not
  sufficient, because it is graph-granular by construction.
- Decide what a write about a subject does when that subject exists somewhere the caller cannot
  see. The creation split above asks whether the subject is new, and answering it can be observed:
  a caller who may write context A but cannot read context B consults an existing resource policy
  for a subject held in B and may be refused, where the same request for a genuinely new subject
  succeeds — which reports that the subject exists. Treating it as new instead replaces a policy the
  caller cannot see. Neither is acceptable as it stands, and the property to preserve is the one
  [`SPS-CRUD-017`](../../spec/core/lod-crud.md#SPS-CRUD-017) already fixes for reads: absent and
  inaccessible answer alike. This is the same "a subject spans contexts" question the retirement
  item runs into, from the creating end.
- Define when the finer decision about a subject is **retired**. It is about the subject and
  independent of any data
  context, so deleting a subject's last statement leaves its policies standing; recreating that
  subject then publishes new content under old grants, with no bootstrap in between. A subject whose
  statements span several contexts makes "its last statement" a question rather than an event, and
  two pods answering it differently answer the same request differently — which is why this sits
  with the blockers rather than beside installation, where it started.
- Define how a pod installs complete resource policies before declaring the resource module, given
  that an evaluator with no matching policy denies.

These are not all the same kind of open. Every one above except the last is a **contract blocker**:
until it is answered there is no target contract to implement, so nothing can be conformant against
it. The sandbox restatement belongs in that group rather than beside it — the read sandbox is what
the resource module has to preserve, and the paragraph below says as much when it observes that
partial query support claims no conformance.

The last is an **adoption blocker** — a pod that never declares the resource module has nothing to
install, and a pod that does needs its policies in place before the second decision starts denying.
Installation happens once, before anything is enabled; retirement keeps happening afterwards, which
is the line between the two kinds and why the retirement half was moved above.

None of them blocks an experiment. Core is indivisible
([`SPS-CORE-004`](../../spec/core/index.md#SPS-CORE-004)), so an implementation that answers before
the contract blockers are settled, or that supports part of the query surface, makes no conformance
claim rather than a partial one. Both directions are conformance defects — refusing a query the
contract requires and returning a statement the contract denies — and only their severity differs,
which is a distinction for whoever triages the conformance suite rather than one the contract makes.

## Not in scope

- **Identity proof.** [`auth`](../../spec/core/auth.md) and the `oidc` module establish agent, client
  and issuer. Access control consumes their verified result.
- **One enforcement implementation.** The authorized statement view is the contract. How an
  implementation produces it is its own affair, subject to the sandbox requirements the open decision
  above leaves unresolved — what a mechanism owes is that view, exactly, for every operation it
  supports.
- **Solid protocol conformance.** Whether a pod is a Solid resource server is a separate claim from
  anything here, and this concept makes neither.
