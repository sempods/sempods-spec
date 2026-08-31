# Access control (Concept)

## Purpose

sempods identifies a resource by its LOD IRI — an RDF subject — but decides access at a different
unit today: the context that holds a statement. Both units are useful. Treating either one as the
whole model is what creates the tension: a context is too coarse for document-level audiences, while
a subject alone cannot distinguish statements deliberately placed in different security domains.

The target model makes the distinction explicit. **Resource policy is the access-control primitive;
multiple managed contexts are an optional second constraint.** A pod with only its canonical context
has a small, resource-oriented model. A deployment that needs graph-level isolation enables the
contexts module, and a deployment with enterprise audiences enables both dimensions.

The policy language is a deliberately small profile of the Solid Community Group's
[Access Control Policy (ACP)](https://solid.github.io/authorization-panel/acp-specification/). ACP
provides the useful frame — target, access context, policy, matcher and access mode — without making
sempods a Solid server or importing ACP's complete resolution algorithm.

Sections below are marked **IST** (specified today, verifiable against the chapters) or **SOLL**
(target state). The SOLL has no roadmap yet, and it contradicts requirements and project invariants
that are in force — "Specification impact" names the load-bearing ones. It is therefore a
governance decision, not an editorial reinterpretation, and nothing here is adopted by having been
written down.

## The two decision units (IST)

Five things in the specification could carry a permission. Only two have a stable identity at a
useful granularity.

| Candidate | Defined by | Useful as a decision unit |
|---|---|---|
| Statement | [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001) | No — no route addresses one statement |
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

There is consequently no containment relation between a context and a resource. A context is not
the folder in which a resource lives, and ACP member inheritance cannot manufacture that relation.

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
- silence is private ([`SPS-CTX-027`](../../spec/core/contexts.md#SPS-CTX-027)); and,
- OAuth delegation is a ceiling: an application receives no more than the authorizing person holds
  ([`SPS-GRANT-013`](../../spec/core/grants.md#SPS-GRANT-013)).

Those properties survive the target model. What changes is the unit against which policy is first
resolved.

## The authorization primitive (SOLL)

The primitive is an access decision, not a storage graph or an OAuth scope:

```text
authorize(target, mode, accessContext) -> granted | denied
```

The **target** is an IRI controlled by the evaluator. In core it is the resource's subject IRI. The
optional context evaluator instead binds it to the statement's context IRI.

The **access context** is the trusted description of one attempted access: verified agent, verified
client, issuer where relevant, target, pod, and server-derived facts such as owner or creator. This
is ACP's `acp:Context`; the qualified name *ACP access context* is used throughout sempods to avoid
confusing it with a sempods context (named graph).

The **policy** connects allowed sempods modes to matchers over that access context. Silence denies.
The pod owner is represented by an implicit system policy using ACP's owner-matcher semantics. That
moves owner handling through the common evaluator, but does not pretend the owner stopped being a
server-provided rule.

### A monotone ACP profile

sempods uses ACP's vocabulary and matcher frame, but not its complete effective-policy resolution
algorithm. The sempods profile is **allow-only and non-inheriting**:

- resource evaluation uses only policies directly associated with the evaluated subject; context
  evaluation may additionally use a `manage` policy whose target covers the evaluated context under
  the existing slash-delimited rule
  ([`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007));
- satisfied policies contribute their allowed modes by union;
- `acp:allOf` and `acp:anyOf` express conjunction and alternatives between matchers;
- `acp:deny`, `acp:noneOf` and `acp:memberAccessControl` do not participate; and,
- no satisfied policy means no allowed mode.

Full ACP gathers direct policies and member policies inherited from ancestor resources, then removes
every mode denied by a satisfied policy from the allowed set. That model is valuable where a server
has a real container hierarchy and needs exceptions. sempods has neither containment between
contexts and resources nor a present deny model. Importing those operations would add negative
checks over a transitive closure to every access decision and would make the result non-monotone.

The modes keep the names and the implications the grants chapter already fixes
([`SPS-GRANT-006`](../../spec/core/grants.md#SPS-GRANT-006),
[`SPS-GRANT-009`](../../spec/core/grants.md#SPS-GRANT-009)). They belong to sempods rather than being
aliases for similarly named ACL modes, because those implications are part of the contract:

```text
expand(manage) = { manage, write, read }
expand(write)  = { write, read }
expand(read)   = { read }
```

On a resource, `manage` governs its access-control resource (ACR). On a context, `manage` additionally
retains the slash-delimited descendant authority of
[`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007). That coverage rule is a sempods context
rule, not ACP resource membership or policy inheritance. Reusing ACP's policy machinery does not give
two differently specified mode systems the same meaning.

## Resource core and optional contexts (SOLL)

Every conforming pod evaluates resource policy. There is no configurable evaluator list and no
empty-chain special case. Optional modules add fixed constraints with specified composition rather
than extension points whose meaning differs between deployments — a module is advertised, and
[`SPS-CORE-006`](../../spec/core/index.md#SPS-CORE-006) makes advertising one a claim about every
`MUST` in it.

Core has one canonical data context with no independent access policy. It remains true that every
stored data statement belongs to exactly one context, but a single-context pod does not expose
context creation, discovery, provenance or selection as client concepts. Writes omit `?context=`
because there is no choice to make, and reads address resources rather than storage partitions. That
requires a different CRUD contract from
[`SPS-CRUD-007`](../../spec/core/lod-crud.md#SPS-CRUD-007); "Specification impact" below lists it
with the other load-bearing changes.

The optional multi-context module exposes the current context lifecycle, discovery, explicit write
target and read downscope. It also adds the context evaluator. For a statement
`q = (subject, predicate, object, context)`, visibility then has one definition:

```text
resource-only pod:  visible(q) = resourceAllows(subject, read)

multi-context pod:  visible(q) = resourceAllows(subject, read)
                                  AND contextAllows(context, read)
```

The same intersection applies to the requested mode on updates and deletes. It is sempods'
composition rule, not ACP policy union and not `acp:allOf`: the two decisions have different targets.
An evaluator that has no matching policy denies, so enabling multi-context support requires context
policies to exist before the module becomes active.

A subject may span any number of contexts under either profile. Resource policy is resolved once by
the subject IRI and applies uniformly to that resource's statements; the context evaluator, where
present, independently decides which of those statements are reachable. No policy is discovered by
merging the authorization graphs adjacent to whichever data contexts a caller can already see.

### OAuth remains a ceiling

Policy answers what the verified agent and client may do now. OAuth delegation answers how much of
the agent's non-public authority the client received. Neither substitutes for the other:

```text
authenticated modes = delegated client ceiling
                      ∩ resource policy decision
                      ∩ optional context policy decision

public modes = { read } if public resource policy allows read
                         and, when present, public context policy allows read
               ∅ otherwise

effective modes = authenticated modes ∪ public modes
```

This preserves immediate policy revocation and the distinction between agent and client. A broad
policy for a person does not silently broaden every application that person uses. Public authority
does not come from the agent and therefore cannot be delegated or removed by the agent's OAuth
ceiling. The ceiling may constrain modes, targets or both; OAuth owns how a person selects that
subset, while access control owns the per-request decision. In particular, the resource-only profile
cannot quietly reuse context selection as its consent vocabulary.

Public access becomes an ordinary resource policy and, where multi-context support is enabled, an
ordinary context policy matched by ACP's public-agent semantics. The sempods profile permits that
matcher for `read` only; anonymous `write` or `manage` is not part of the target model. A `public`
convenience field may project to that policy, but it is not a second decision path. An authenticated
request remains able to read what an unauthenticated request can read; the present `public-read`
scope therefore has to be reconsidered when this target state becomes a roadmap.

## Enterprise matchers (SOLL)

ACP directly describes request attributes such as agent, client and issuer. Enterprise systems also
need principal sets whose membership changes independently of policy: groups, audiences, tenant
membership and sometimes roles. Flattening those sets into copied per-user policies would make every
membership change a policy migration.

sempods therefore defines a closed matcher extension for a principal set. A policy names a set IRI;
the server resolves whether the verified agent belongs to it from a trusted authority. A tenant-wide
matcher is the same mechanism with the pod's member set, not a role bypass. An administrator is
authorized because a policy names an administrator set, not because evaluation has an unrestricted
branch around policy.

The extension is closed in two senses:

- clients select relations and principal-set IRIs from a vocabulary the implementation advertises;
  they do not submit SPARQL, code or arbitrary expressions for the evaluator to execute; and,
- membership facts come from a protected identity graph or an external authority, never from data
  writable through LOD CRUD.

This maps the enterprise model without changing its algebra:

| Enterprise concept | sempods policy model |
|---|---|
| Visible Space | Context policy, when the multi-context module is enabled |
| Document ACL | Resource policy |
| Several grants on a document | Several allow policies (OR) |
| Requirements within one grant | `acp:allOf` matchers (AND) |
| Several accessors satisfying one requirement | One matcher with alternative agents, or a principal-set matcher (OR) |
| Group or audience | Trusted principal-set matcher |
| Branch-wide content | Pod-member matcher |
| Application-specific delegation | Agent/client policy plus the OAuth ceiling |

Membership is resolved at access time, so removing someone from a group narrows their next request
without rewriting every resource policy. Failure of the trusted resolver fails closed. A later
normative profile has to define freshness and availability expectations for an external resolver;
the concept does not prescribe whether an implementation uses a local graph, an indexed service or
another mechanism.

## Policy location and control plane (SOLL)

Policy is indexed by the target it controls, not by the data context that happens to hold a target's
statements:

- a resource ACR is canonical for one subject IRI;
- a context ACR is canonical for one context IRI; and,
- identity and principal-set facts live in a separate protected authority.

An implementation may represent these as RDF named graphs internally. They are control-plane
graphs, not registered sempods data contexts: they do not appear in context discovery, cannot be
selected by `?context=`, and are unreachable through LOD CRUD. That distinction ends the apparent
recursion in which the graph carrying policy would need a user policy of its own.

An ACR is reached through a control-plane route and linked from the target. Reading or changing it is
itself authorized: `manage` on the target permits policy management, subject to the implicit owner
policy and the OAuth ceiling. The client-facing answer to “what may I do?” remains an effective-
permission view; clients are not expected to reimplement policy evaluation from raw RDF.

The security boundary is topological:

> Authorization facts are read only from stores that no data write can reach.

Looking like policy never makes ordinary RDF authoritative. A caller may write statements about an
ACR IRI or use ACP predicates as ordinary data; none of those statements enter the evaluator's
policy set.

This is where [`SPS-CTX-026`](../../spec/core/contexts.md#SPS-CTX-026) acquires a hazard it does not
have today. Treating a statement about a `_system` IRI as ordinary data is right and stays right —
but once policy is RDF, "ordinary data that looks exactly like policy" is something a caller can
write. The requirement does not change; what changes is that an implementation reading policy from
anywhere a caller can reach is now wrong in a way the text does not yet warn about.
[`SPS-CTX-025`](../../spec/core/contexts.md#SPS-CTX-025) already refuses the write path as a route to
control-plane state, and the boundary above is the read-side half it does not state.

## Operation boundaries (SOLL)

`read` authorization is evaluated per candidate statement. Resource retrieval and find discard a
statement before it can contribute to an answer. SPARQL executes against a server-derived statement
view that already excludes denied statements before query algebra, joins, filters, aggregates or
result construction can observe them. Selecting readable contexts provides the context half of that
view; in the multi-context profile it does not replace the resource decision.

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

Existing-resource mutations require the requested mode on the resource and, with the multi-context
module enabled, on the target context. Slot and edge operations use their subject as the resource
target. SPARQL remains read-only
([`SPS-SPARQL-006`](../../spec/core/sparql.md#SPS-SPARQL-006)); the target model does not add a
second mutation path beside CRUD, and client-supplied dataset clauses never expand the server-derived
statement view ([`SPS-SPARQL-008`](../../spec/core/sparql.md#SPS-SPARQL-008)).

Creation is necessarily different because a new resource has no policy yet. Its authority comes
from the destination: `write` on the pod's bootstrap ACR in a single-context pod, or `write` on the
target context in a multi-context pod. Creation and the resource's initial policy have to be one
operation from the client's perspective; otherwise the resource is either born unreachable or is
temporarily unprotected. The exact bootstrap policy — creator management, an explicitly supplied
ACR, or a server-owned template — remains an open design choice for the roadmap, but silent creation
without one is not a complete model.

Authorization is checked before target existence wherever different responses would reveal protected
topology. ACP does not close an enumeration oracle by itself: the HTTP contract still has to make an
unknown target and an inaccessible target indistinguishable to a caller outside its authority. That
is the open half of [`SPS-CORE-018`](../../spec/core/index.md#SPS-CORE-018), and the shape it needs is
the one [`SPS-CTX-020`](../../spec/core/contexts.md#SPS-CTX-020) already uses for deletion.

## What becomes smaller (SOLL)

The target state removes parallel authorization concepts rather than merely renaming them:

- public access is a public-agent policy rather than a flag plus a separate resolution branch;
- owner access is an implicit system policy evaluated by the common engine;
- direct users, clients, groups and tenant-wide audiences are matchers in one policy model;
- a single-context pod has no context management surface; and,
- enterprise deployments add a context constraint without changing resource policy semantics.

The remaining complexity is visible where it belongs: multi-dimensional deployments opt into a
second decision, while the core no longer makes every client manage a graph partition before it can
write one resource.

## Specification impact (SOLL)

The target state changes the specification's architecture rather than merely its vocabulary. Some of
what follows is contradicted outright, including invariants that
[`AGENTS.md`](../../AGENTS.md) §"Non-negotiable invariants" says are refused rather than debated;
one entry keeps its principle and changes only its wording. The load-bearing impacts are:

| In force today | What the target state does to it |
|---|---|
| Invariants 2 and 3 — the read and write sandboxes are stated over contexts | Superseded in the resource-only profile, which has no context authorization decision against which they could be satisfied. Both have to be restated over the target of a decision |
| Invariant 4 — a CRUD write names its target context explicitly | Contradicted: a single-context pod omits `?context=` because there is nothing to choose |
| Mission, third goal — "graph-based access control where the 4th RDF dimension … is called Context" | Core access control stops being graph-based; the graph dimension becomes the optional constraint |
| [`SPS-CORE-004`](../../spec/core/index.md#SPS-CORE-004) — `contexts` and `grants` are part of an indivisible core | The core has to be cut around resource policy, with multi-context lifecycle and context policy moved behind one advertised module |
| [`SPS-CTX-003`](../../spec/core/contexts.md#SPS-CTX-003) — no permission abstraction above or beside the context | Resource policy is such an abstraction, and it becomes the primitive |
| [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001) — there is no default context | The canonical context is one. The invariant it serves — every statement in exactly one context — survives untouched |
| [`SPS-CRUD-007`](../../spec/core/lod-crud.md#SPS-CRUD-007) — every write carries exactly one `?context=` | Applies to the multi-context profile; a resource-only write has no context parameter |
| [`SPS-GRANT-025`](../../spec/core/grants.md#SPS-GRANT-025) — no implicit or default write context | The same requirement seen from the grants chapter |
| [`SPS-SPARQL-007`](../../spec/core/sparql.md#SPS-SPARQL-007) — a query sees exactly the readable contexts | Too permissive once the decision unit is the resource: within a readable context, individual subjects are denied |
| [`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009) — the dataset carries the sandbox, and the query is never rewritten | Kept, and made precise: the dataset a query executes against need not be the graphs a store holds, so an authorized statement view satisfies it |
| [`grants`](../../spec/core/grants.md) §2 — the grant grammar `<context-iri>#read` | Becomes the multi-context module's spelling of a context policy; the core spelling is a policy on a subject IRI |

Two entries are reversals of intent rather than mechanical edits, and they are what makes this a
governance decision rather than an editorial one. The mission names the graph dimension as *the*
access-control model, and `SPS-CTX-003` was written specifically to keep a second permission concept
out. Both were right for a model whose only decision unit was the context, and both were load-bearing
for the argument [`contexts`](../../spec/core/contexts.md) §1 makes.

What survives is worth stating beside it. Invariant 1 holds unchanged, and so does every property
listed under "The current model" above: monotone policy, the mode implications, the implicit owner,
silence as private, and the OAuth ceiling.

Adoption requires one coherent change to the affected core and module contracts, their conformance
descriptions and the implementation. The concept records why that change has this shape; it is not a
second contract beside the specification chapters.

## Rejected alternatives

**ACP deny and exclusion.** They turn positive confinement into negative evaluation over the
effective policy set. What a positive algebra buys is narrow and worth stating exactly: access
contributed by satisfied policies accumulates by union, with no subtractive exception to account for,
so adding an allow policy never removes access. It does not by itself make the policy set
enumerable backwards from an agent — a principal-set matcher holds a set IRI rather than a list of
agents, owner and creator are server-derived, and a decision also depends on client, issuer, the
OAuth ceiling and the optional context. An implementation may still index policies in that direction;
that is a strategy, not a consequence of the algebra.

“Everyone in this group except one person” is expressed one layer down instead: a principal set may
be defined by difference, so the matcher still asks a single membership question. This moves the
negation into the membership resolver rather than removing it. What is monotone is the policy
algebra over unchanged membership facts, which is the property the enforcement mechanisms depend on;
the authorization system as a whole is not monotone, because a membership fact can be withdrawn.

**ACP member inheritance.** An inheriting policy needs a containment relation, and ACP expects the
resource server to supply one. This specification defines none between resources, and
[`SPS-CRUD-011`](../../spec/core/lod-crud.md#SPS-CRUD-011) makes a resource and a context independent
dimensions rather than a member and its container — the slash-delimited `manage` coverage of
[`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007) is a sempods rule over context paths, not
resource membership. Inheritance is therefore excluded, and the profile above says so.

Introducing it later is a definition, not a switch: which relation creates containment, between which
resource kinds, which policies and modes propagate, what bounds the depth, and whether it is
`acp:memberAccessControl` or a rule of sempods' own. Until those are answered the exclusion stands,
and the cost ACP's model carries — evaluation over a transitive closure on every decision — is the
reason to answer them before adopting it rather than after.

**Contexts as the core policy unit.** It keeps the current model small only while every audience
aligns with a graph. A deployment needing finer audiences then creates one graph per permission set
and turns a policy edit into data movement. It also prevents the single-context resource/ACR model
from being the ordinary case.

**A configurable evaluator chain.** A generic list creates an empty-chain identity problem and lets
two conforming pods attach incompatible meaning to the same request. Fixed core and module semantics
give conformance discovery something concrete to advertise and test.

**Additive composition of resource and context decisions.** Union lets either dimension override
the other. A document policy that appears to restrict a broad context grant would then be unable to
restrict it. Independent security boundaries compose by intersection.

**Resource policies stored beside each data context.** It makes policy discovery depend on data
visibility, duplicates policy for subjects spanning contexts and lets deleting one context destroy
authority for a resource that still exists elsewhere — [`SPS-CTX-017`](../../spec/core/contexts.md#SPS-CTX-017)
removes what rested on a deleted context, which is correct for a grant naming it and wrong for a
resource that outlives it. Canonical target-indexed ACRs avoid all three.

**Client-authored conditions.** Policy evaluation necessarily runs with more authority than the
caller. Letting a caller supply a query as a condition turns the decision into an oracle over data
the caller cannot read. Named, closed, server-resolved relations provide enterprise attributes
without executing policy-holder code.

**Claiming Solid interoperability.** A single-context, resource-policy pod is close to a Solid
resource-server use case, but sempods resources remain RDF subjects, sempods does not adopt ACP
container inheritance, and its CRUD and SPARQL surfaces remain its own. Protocol interoperability is
a separate feature with a separate conformance cost.

## Open decisions before a roadmap

Two of these are a different size from the rest and come first. In both, a section of a current
chapter loses the thing it is about — they are not details left to settle.

**Delegation has no unit in a resource-only pod.** [`grants`](../../spec/core/grants.md) §5 and §6
rest on the context catalogue throughout: an application asks for a set of contexts and receives the
intersection with what the person effectively holds
([`SPS-GRANT-013`](../../spec/core/grants.md#SPS-GRANT-013),
[`SPS-GRANT-028`](../../spec/core/grants.md#SPS-GRANT-028)), and narrowing a person's own access
sweeps every delegation no longer covered by recomputing it rather than matching strings
([`SPS-GRANT-015`](../../spec/core/grants.md#SPS-GRANT-015),
[`SPS-GRANT-016`](../../spec/core/grants.md#SPS-GRANT-016)). Take contexts out of core and consent
has nothing enumerable left to offer, while the resource population is far too large and too
short-lived to put in its place. Whether the ceiling becomes coarser (modes only), attaches to
principal sets, or keeps a context-shaped surface that a resource-only pod synthesises, is
unresolved — and the answer decides how much of §5 and §6 survives.

**`public-read` is a scope in a model that no longer has the thing it scopes.** Seven requirements
carry today's answer: the `public` flag and its private default
([`SPS-CTX-015`](../../spec/core/contexts.md#SPS-CTX-015),
[`SPS-CTX-027`](../../spec/core/contexts.md#SPS-CTX-027)), the scope itself and its access-time
expansion ([`SPS-GRANT-020`](../../spec/core/grants.md#SPS-GRANT-020),
[`SPS-GRANT-021`](../../spec/core/grants.md#SPS-GRANT-021),
[`SPS-GRANT-022`](../../spec/core/grants.md#SPS-GRANT-022)), and the guarantee that an
unauthenticated caller reads exactly the public contexts and is not a degraded client
([`SPS-GRANT-031`](../../spec/core/grants.md#SPS-GRANT-031),
[`SPS-GRANT-032`](../../spec/core/grants.md#SPS-GRANT-032)). A public-agent policy can carry the
guarantee, which is the property worth keeping. What has to be decided is whether a scope remains
useful as a coarse discovery or token capability once public access is an ordinary policy rather
than a second resolution branch.

The rest are ordinary open questions:

- Choose the creation bootstrap: implicit creator policy, atomic caller-supplied ACR, or an advertised
  server policy template.
- Define the concrete sempods mode and principal-set vocabulary IRIs.
- Define the resource-only protocol projection: graph-aware representations and SPARQL dataset
  parameters, the context filters in `find`, the MCP tool catalogue and arguments, and whether media
  requires the multi-context module or receives resource policy of its own.
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
- Define how an existing multi-context pod installs complete resource policies before switching to
  the intersected model.

These are not all the same kind of open. The two named above and the first four bullets are
**contract blockers**: until they are answered there is no target contract to implement, so nothing
can be conformant against it. The last is an **adoption blocker** — a pod starting in the target model
has nothing to migrate, and what is unresolved is how an existing multi-context pod gets there.

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
- **Solid protocol conformance.** ACP-inspired policy and a Solid-compatible HTTP resource server are
  separate claims.
