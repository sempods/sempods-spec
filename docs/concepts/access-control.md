# Access control (Concept)

## Purpose

sempods identifies a resource by its LOD IRI — an RDF subject — but decides access at a different
unit today: the Context that holds a statement. Both units are useful. Treating either one as the
whole model is what creates the tension: a Context is too coarse for document-level audiences, while
a subject alone cannot distinguish statements deliberately placed in different security domains.

The target model makes the distinction explicit. **Resource policy is the access-control primitive;
multiple managed Contexts are an optional second constraint.** A pod with only its canonical Context
has a small, resource-oriented model. A deployment that needs graph-level isolation enables the
Contexts module, and a deployment with enterprise audiences enables both dimensions.

The policy language is a deliberately small profile of the Solid Community Group's
[Access Control Policy (ACP)](https://solid.github.io/authorization-panel/acp-specification/). ACP
provides the useful frame — target, access context, policy, matcher and access mode — without making
sempods a Solid server or importing ACP's complete resolution algorithm.

Sections below are marked **IST** (specified today, verifiable against the chapters) or **SOLL**
(target state). The SOLL has no roadmap yet and changes several current core requirements and
project invariants; it is therefore a governance change, not an editorial reinterpretation.

## The two decision units (IST)

Five things in the specification could carry a permission. Only two have a stable identity at a
useful granularity.

| Candidate | Defined by | Useful as a decision unit |
|---|---|---|
| Statement | [`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001) | No — no route addresses one statement |
| Slot `(subject, predicate)` in one Context | [`lod-crud`](../../spec/core/lod-crud.md) §5 | No — policy would be repeated per predicate |
| **Resource** (subject) | [`SPS-CRUD-001`](../../spec/core/lod-crud.md#SPS-CRUD-001) | **Yes** — it has an LOD IRI |
| **Context** (named graph) | [`SPS-CTX-002`](../../spec/core/contexts.md#SPS-CTX-002) | **Yes** — it is registered under an IRI |
| Pod | [`SPS-CORE-007`](../../spec/core/index.md#SPS-CORE-007) | Only for bootstrapping authority |

The current specification chooses the Context. Every statement belongs to exactly one Context
([`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001)); reads expose only readable Contexts and
writes land in one explicitly named Context
([`SPS-GRANT-024`](../../spec/core/grants.md#SPS-GRANT-024),
[`SPS-GRANT-025`](../../spec/core/grants.md#SPS-GRANT-025)). The resource IRI and Context remain
independent, so one subject may have statements in several Contexts
([`SPS-CRUD-011`](../../spec/core/lod-crud.md#SPS-CRUD-011)).

There is consequently no containment relation between a Context and a resource. A Context is not
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
optional Context evaluator instead binds it to the statement's Context IRI.

The **access context** is the trusted description of one attempted access: verified agent, verified
client, issuer where relevant, target, pod, and server-derived facts such as owner or creator. This
is ACP's `acp:Context`; the qualified name *ACP access context* is used throughout sempods to avoid
confusing it with a sempods Context (named graph).

The **policy** connects allowed sempods modes to matchers over that access context. Silence denies.
The pod owner is represented by an implicit system policy using ACP's owner-matcher semantics. That
moves owner handling through the common evaluator, but does not pretend the owner stopped being a
server-provided rule.

### A monotone ACP profile

sempods uses ACP's vocabulary and matcher frame, but not its complete effective-policy resolution
algorithm. The sempods profile is **allow-only and non-inheriting**:

- resource evaluation uses only policies directly associated with the evaluated subject; Context
  evaluation may additionally use a Manage policy whose target covers the evaluated Context under
  the existing slash-delimited rule;
- satisfied policies contribute their allowed modes by union;
- `acp:allOf` and `acp:anyOf` express conjunction and alternatives between matchers;
- `acp:deny`, `acp:noneOf` and `acp:memberAccessControl` do not participate; and,
- no satisfied policy means no allowed mode.

Full ACP gathers direct policies and member policies inherited from ancestor resources, then removes
every mode denied by a satisfied policy from the allowed set. That model is valuable where a server
has a real container hierarchy and needs exceptions. sempods has neither containment between
Contexts and resources nor a present deny model. Importing those operations would add negative
checks over a transitive closure to every access decision and would make the result non-monotone.

The modes belong to sempods rather than being aliases for similarly named ACL modes, because their
implications are part of the contract:

```text
expand(Manage) = { Manage, Write, Read }
expand(Write)  = { Write, Read }
expand(Read)   = { Read }
```

On a resource, Manage governs its access-control resource (ACR). On a Context, Manage additionally
retains the existing slash-delimited descendant authority. That coverage rule is a sempods Context
rule, not ACP resource membership or policy inheritance. Reusing ACP's policy machinery does not give
two differently specified mode systems the same meaning.

## Resource core and optional Contexts (SOLL)

Every conforming pod evaluates resource policy. There is no configurable evaluator list and no
empty-chain special case. Optional modules add fixed constraints with specified composition rather
than extension points whose meaning differs between deployments.

Core has one canonical data Context with no independent access policy. It remains true that every
stored data statement belongs to exactly one Context, but a single-Context pod does not expose
Context creation, discovery, provenance or selection as client concepts. Writes omit `?context=`
because there is no choice to make, and reads address resources rather than storage partitions.

The optional multi-Context module exposes the current Context lifecycle, discovery, explicit write
target and read downscope. It also adds the Context evaluator. For a statement
`q = (subject, predicate, object, context)`, visibility then has one definition:

```text
resource-only pod:  visible(q) = resourceAllows(subject, Read)

multi-Context pod:  visible(q) = resourceAllows(subject, Read)
                                  AND contextAllows(context, Read)
```

The same intersection applies to the requested mode on updates and deletes. It is sempods'
composition rule, not ACP policy union and not `acp:allOf`: the two decisions have different targets.
An evaluator that has no matching policy denies, so enabling multi-Context support requires Context
policies to exist before the module becomes active.

A subject may span any number of Contexts under either profile. Resource policy is resolved once by
the subject IRI and applies uniformly to that resource's statements; the Context evaluator, where
present, independently decides which of those statements are reachable. No policy is discovered by
merging the authorization graphs adjacent to whichever data Contexts a caller can already see.

### OAuth remains a ceiling

Policy answers what the verified agent and client may do now. OAuth delegation answers how much of
the agent's non-public authority the client received. Neither substitutes for the other:

```text
authenticated modes = delegated client ceiling
                      ∩ resource policy decision
                      ∩ optional Context policy decision

public modes = public resource policy decision
               ∩ optional public Context policy decision

effective modes = authenticated modes ∪ public modes
```

This preserves immediate policy revocation and the distinction between agent and client. A broad
policy for a person does not silently broaden every application that person uses. Public authority
does not come from the agent and therefore cannot be delegated or removed by the agent's OAuth
ceiling. The ceiling may constrain modes, targets or both; OAuth owns how a person selects that
subset, while access control owns the per-request decision. In particular, the resource-only profile
cannot quietly reuse Context selection as its consent vocabulary.

Public access becomes an ordinary resource or Context policy matched by ACP's public-agent
semantics. A `public` convenience field may project to that policy, but it is not a second decision
path. An authenticated request remains able to read what an unauthenticated request can read; the
present `public-read` scope therefore has to be reconsidered when this target state becomes a
roadmap.

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
| Visible Space | Context policy, when the multi-Context module is enabled |
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

Policy is indexed by the target it controls, not by the data Context that happens to hold a target's
statements:

- a resource ACR is canonical for one subject IRI;
- a Context ACR is canonical for one Context IRI; and,
- identity and principal-set facts live in a separate protected authority.

An implementation may represent these as RDF named graphs internally. They are control-plane
graphs, not registered sempods data Contexts: they do not appear in Context discovery, cannot be
selected by `?context=`, and are unreachable through LOD CRUD. That distinction ends the apparent
recursion in which the graph carrying policy would need a user policy of its own.

An ACR is reached through a control-plane route and linked from the target. Reading or changing it is
itself authorized: Manage on the target permits policy management, subject to the implicit owner
policy and the OAuth ceiling. The client-facing answer to “what may I do?” remains an effective-
permission view; clients are not expected to reimplement policy evaluation from raw RDF.

The security boundary is topological:

> Authorization facts are read only from stores that no data write can reach.

Looking like policy never makes ordinary RDF authoritative. A caller may write statements about an
ACR IRI or use ACP predicates as ordinary data; none of those statements enter the evaluator's
policy set.

## Operation boundaries (SOLL)

Read authorization is evaluated per candidate statement. This gives resource retrieval, find and
SPARQL one rule even though an implementation may enforce it through dataset pruning, query joins or
post-filtering.

Existing-resource mutations require the requested mode on the resource and, with the multi-Context
module enabled, on the target Context. Slot and edge operations use their subject as the resource
target. A SPARQL update is acceptable only when every statement it can add or remove satisfies the
same rule; client-supplied dataset clauses never expand the server-derived sandbox.

Creation is necessarily different because a new resource has no policy yet. Its authority comes
from the destination: Write on the pod's bootstrap ACR in a single-Context pod, or Write on the
target Context in a multi-Context pod. Creation and the resource's initial policy have to be one
operation from the client's perspective; otherwise the resource is either born unreachable or is
temporarily unprotected. The exact bootstrap policy — creator management, an explicitly supplied
ACR, or a server-owned template — remains an open design choice for the roadmap, but silent creation
without one is not a complete model.

Authorization is checked before target existence wherever different responses would reveal protected
topology. ACP does not close an enumeration oracle by itself: the HTTP contract still has to make an
unknown target and an inaccessible target indistinguishable to a caller outside its authority.

## What becomes smaller (SOLL)

The target state removes parallel authorization concepts rather than merely renaming them:

- public access is a public-agent policy rather than a flag plus a separate resolution branch;
- owner access is an implicit system policy evaluated by the common engine;
- direct users, clients, groups and tenant-wide audiences are matchers in one policy model;
- a single-Context pod has no Context management surface; and,
- enterprise deployments add a Context constraint without changing resource policy semantics.

The remaining complexity is visible where it belongs: multi-dimensional deployments opt into a
second decision, while the core no longer makes every client manage a graph partition before it can
write one resource.

## Rejected alternatives

**Full ACP deny, exclusion and member inheritance.** They solve real container-policy problems, but
sempods has no resource-container relation from which to derive them. They turn positive query
confinement into negative evaluation over a transitive closure. “Everyone in this group except one
person” is deliberately represented by a principal set without that person.

**Contexts as the core policy unit.** It keeps the current model small only while every audience
aligns with a graph. A deployment needing finer audiences then creates one graph per permission set
and turns a policy edit into data movement. It also prevents the single-Context Resource/ACR model
from being the ordinary case.

**A configurable evaluator chain.** A generic list creates an empty-chain identity problem and lets
two conforming pods attach incompatible meaning to the same request. Fixed core and module semantics
give conformance discovery something concrete to advertise and test.

**Additive composition of Resource and Context decisions.** Union lets either dimension override
the other. A document policy that appears to restrict a broad Context grant would then be unable to
restrict it. Independent security boundaries compose by intersection.

**Resource policies stored beside each data Context.** It makes policy discovery depend on data
visibility, duplicates policy for subjects spanning Contexts and lets deleting one Context destroy
authority for a resource that still exists elsewhere. Canonical target-indexed ACRs avoid all three.

**Client-authored conditions.** Policy evaluation necessarily runs with more authority than the
caller. Letting a caller supply a query as a condition turns the decision into an oracle over data
the caller cannot read. Named, closed, server-resolved relations provide enterprise attributes
without executing policy-holder code.

**Claiming Solid interoperability.** A single-Context, resource-policy pod is close to a Solid
resource-server use case, but sempods resources remain RDF subjects, sempods does not adopt ACP
container inheritance, and its CRUD and SPARQL surfaces remain its own. Protocol interoperability is
a separate feature with a separate conformance cost.

## Open decisions before a roadmap

- Choose the creation bootstrap: implicit creator policy, atomic caller-supplied ACR, or an advertised
  server policy template.
- Define the concrete sempods mode and principal-set vocabulary IRIs.
- Define the consent granularity for a resource-only pod, where no Context catalogue exists from
  which an application can request a subset.
- Decide which current public-context and `public-read` behaviours are withdrawn or projected onto
  public-agent policy.
- Define how an existing multi-Context pod installs complete Resource policies before switching to
  the intersected model.

## Not in scope

- **Identity proof.** [`auth`](../../spec/core/auth.md) and the `oidc` module establish agent, client
  and issuer. Access control consumes their verified result.
- **One enforcement implementation.** Dataset pruning, algebra rewriting and filtered retrieval are
  conformant strategies only when they produce the same decision for every supported operation.
- **Solid protocol conformance.** ACP-inspired policy and a Solid-compatible HTTP resource server are
  separate claims.
