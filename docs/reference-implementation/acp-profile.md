# The reference implementation: expressing the model in ACP

**This is not the specification.** The contract describes what a pod decides, never how — see
[`../vision.md`](../vision.md). This document is the reference implementation's design: how it
intends to express every deployment it must serve in one small profile of the Solid Community
Group's [Access Control Policy (ACP)](https://solid.github.io/authorization-panel/acp-specification/),
and what that costs.

It lives here rather than in the implementation repository while the two are being worked out
together. At `0.1` it moves, and nothing in the specification has to move with it.

**Nothing here binds anybody.** A pod that answers every request the way the contract says is
conformant whether it evaluates policies, rewrites queries, or has the rules in its code.

The behaviour this expresses is in [`../concepts/access-control.md`](../concepts/access-control.md).
The worked scenarios in [`../../examples/`](../../examples/README.md) are the evidence that the
expression holds: each is ordinary ACP, run through ACP's own resolution algorithm by an engine that
knows nothing about sempods.

## The authorization primitive (SOLL)

The primitive is an access decision, not a storage graph or an OAuth scope:

```text
authorize(target, mode, accessContext) -> granted | denied
```

The **target** is an IRI controlled by the evaluator. Every pod binds it to the statement's context
IRI. A pod that declares the resource module binds a second evaluation to the subject IRI as well.

The **access context** is the trusted description of one attempted access: verified agent, verified
client, issuer where relevant, target, pod, and server-derived facts such as owner or creator. This
is ACP's `acp:Context`; the qualified name *ACP access context* is used throughout sempods to avoid
confusing it with a sempods context (named graph).

The **policy** connects allowed sempods modes to matchers over that access context. Silence denies.
The pod owner is represented by an implicit system policy using ACP's owner-matcher semantics. That
moves owner handling through the common evaluator, but does not pretend the owner stopped being a
server-provided rule.

### A pure ACP profile

sempods uses ACP's vocabulary **and** its resolution algorithm. What the profile constrains is what a
sempods ACR may contain, not how it is evaluated — which is the difference between a profile of ACP
and a variant of it:

- an ACR contains no `acp:deny` and no `acp:noneOf`, so nothing is ever subtracted from the allowed
  set and the result stays monotone;
- an ACR contains no `acp:memberAccessControl`, so no policy decides a target other than its own;
- a policy states every mode it allows, expanded, rather than relying on an implication ACP does not
  have; and,
- `acp:allOf` and `acp:anyOf` carry conjunction and alternatives between matchers, as ACP defines
  them.

Stated this way the restrictions cost nothing: ACP's algorithm subtracts nothing where nothing is
denied and gathers nothing from ancestors where no member access control exists, so a full ACP engine
produces exactly these results. Running the whole algorithm is also the safer choice, because
`acp:deny` and `acp:noneOf` can only ever restrict — honouring an unexpected one fails safe, ignoring
it does not.

The gain is that conformance becomes checkable instead of asserted: an independent ACP engine, given
a sempods ACR and a context graph, must produce the same access grant graph.

Three limits on that, and each matters. It holds **per evaluation** and not for the whole decision,
because the conjunction between evaluations and the OAuth ceiling are sempods' and not ACP's. And it
holds for **ACP's own matcher attributes** and not beyond them: an access control resource using the
principal-set matcher defined below carries an attribute a plain ACP engine does not know, so that
engine leaves the matcher unsatisfied where sempods would resolve it through a trusted membership
authority. Checking such a resource needs an oracle that knows the extension, or it reports a
difference that is the extension rather than a defect.

And it holds for **what an access control resource says**, not for everything a pod decides. The
owner holds every mode on every context implicitly, and
[`SPS-GRANT-011`](../../spec/core/grants.md#SPS-GRANT-011) forbids requiring those grants to be
stored — so an independent engine given the ACR and the access context returns nothing for an owner
request where sempods returns full authority. That is not a difference between two readings of the
policy; it is authority the policy was never asked to carry. Any conformance harness has to exclude
it, which is what [`examples/10-one-context.md`](../../examples/10-one-context.md) means when it says
no fixture there can show Anna's own access.

The **direction** of that difference is the part worth guaranteeing: a foreign engine should answer
less, never more. It does not follow on its own. ACP conjoins the attribute types within a single
matcher, and an engine that does not know an attribute does not see a conjunct to fail — so
`[ acp:agent carol ; sps:principalSet engineers ]` means *Carol, and only while she is in the group*
to sempods and plain *Carol* to everyone else. The extension makes the answer wider rather than
narrower, which is the one outcome the claim rules out.

So the profile requires that **a matcher carries either ACP's attributes or an extension attribute,
never both**. The conjunction is written as two matchers under `acp:allOf`, where it means the same
thing to sempods and a foreign engine leaves the extension matcher unsatisfied — failing the whole
conjunction, which is the safe direction. Nothing is lost but the shorter spelling.

The modes are the ones [`SPS-GRANT-006`](../../spec/core/grants.md#SPS-GRANT-006) names, with the
implications [`SPS-GRANT-009`](../../spec/core/grants.md#SPS-GRANT-009) fixes, and the profile keeps
both by **expanding when the policy is written**. ACP is mode-agnostic and carries no implication of
its own, so writing the expansion out is what makes a foreign engine agree. Where a sempods mode
means what an ACL mode means, the ACL term is used — minting a synonym is the opposite of
interoperability:

| | written as |
|---|---|
| `read` | `acl:Read` |
| `write` | `acl:Read`, `acl:Write` |
| `manage` on a resource | `acl:Read`, `acl:Write`, `acl:Control` |
| `manage` on a context | `acl:Read`, `acl:Write`, a sempods term of its own |

`acl:Control` is *"read and write operations on an ACL resource"* and nothing more, which is exactly
what managing a resource is. Managing a context is more: it creates one that does not exist yet
([`SPS-GRANT-033`](../../spec/core/grants.md#SPS-GRANT-033)), deletes one
([`SPS-CTX-019`](../../spec/modules/context-management.md#SPS-CTX-019)) and reaches slash-delimited descendants
([`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007)). Writing `acl:Control` there would name
a smaller authority than the one that holds, which is the one mistake a shared vocabulary must not
make. The context mode is therefore sempods' own, and stays **one** term rather than splitting the
bundle, so [`SPS-GRANT-006`](../../spec/core/grants.md#SPS-GRANT-006) keeps three values.

Neither implication is a convenience, and this is why neither can be dropped. `write` implies `read`
because a write path is a read oracle — a conditional request, an entity tag, a patch that succeeds
or fails on what is already there. [`SPS-GRANT-010`](../../spec/core/grants.md#SPS-GRANT-010) closes
the illusion that reading can be withheld from somebody who may write, because an implementation
believing otherwise builds *"a read path that hides data its own write path can reach"*. And `manage`
implies `write` one level up for the same shape of reason: whoever may write an access control
resource writes themselves a policy, so a `manage` that did not imply `read` would look like
separation of duties and enforce none.

The combination that costs is the one WAC allows and this does not — administering permissions
without being able to read the content. Keeping the context mode a bundle gives up a second one that
*would* have been enforceable, reading an access control resource without being able to change it.
What both buy is a model that claims no separation it cannot hold.

One deviation remains and this concept does not resolve it. On a context, `manage` reaches
slash-delimited descendants ([`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007)) — a policy on
one target deciding another, which is the one thing the profile otherwise excludes. Until it is
settled a context access control resource is not complete on its own, and that is the artefact every
pod has. It is carried below as an open decision, with the two ways to close it.
### What is guaranteed and what is convention

The restrictions above are not all held up the same way, and reading them as one kind is how an
implementation comes to trust something nothing checks.

| Rule | Held up by | |
|---|---|---|
| Authorization facts are read only from stores no data write can reach | topology — the two graph sets are disjoint by construction | **guarantee**, with one declared exception below |
| Evaluations compose by intersection | the pod, on every request | **guarantee** |
| An ACR carries no `acp:deny` and no `acp:noneOf` | whatever writes the ACR | convention |
| A policy states its modes expanded | whatever writes the ACR — and a target requirement, since an unexpanded set is not a smaller grant but an impossible one | convention today, guarantee in the target |
| An ACR carries no `acp:memberAccessControl` | whatever writes the ACR, and today the server as well | convention, and the one to watch |
| A shared policy's referring targets have the same manager | the deployment | convention, until the open decision below closes it |

Policy is written through control-plane operations rather than by hand: somebody shares a document,
and something turns that into a policy. That layer is where a convention lives, and it can hold rules
a policy language cannot express — which is also why the distinction matters, because an owner
holding `manage` can write an ACR directly and step around every convention in it.

A hand-written deny is honoured and narrows, which is the one that really does **fail towards less
access**: it hands nobody anything the owner could not have granted outright.

Modes left unexpanded do not. `allow acl:Write` without `acl:Read` resolves to write alone, and this
concept's own argument is that a write path *is* a read oracle — a conditional request, an entity
tag, a patch that succeeds or fails on what is there — which is why
[`SPS-GRANT-010`](../../spec/core/grants.md#SPS-GRANT-010) refuses to pretend read can be withheld
from somebody who may write. So the resulting grant is not a smaller one; it is one the model says
cannot exist, and the pod believes it granted less than it did. The same holds for `allow acl:Read,
acl:Write` beside `deny acl:Read`. **Closure has to be enforced where policy is ingested rather than
assumed of whoever wrote it** — which is a requirement to write, not a convention to trust, and it is
carried below.

Nor do the last two. Take member access control first, because it is the one to watch. `acp:memberAccessControl` does not restrict — it adds
an ancestor's policies to a descendant's effective set, and under union adding policies can only
widen. A hand-written one is inert today, but **not because this convention holds**: it is inert
because the server supplies no ancestors for it to resolve against, and ACP expects the resource
server to provide exactly that information. A different guarantee is doing the work.

Answer the `manage` question below with member access control and the server begins supplying them,
at which point this restriction can fail the wrong way — and by the rule that governs the rest of
this table, **a convention that could fail the other way would have to become a guarantee**. Which of
the two it is therefore depends on a decision this concept has not made.

The shared-policy row is the same rule reached from a different direction: it fails the wrong way
today, not after some future decision, because a caller managing one referring target rewrites a
policy deciding access on the rest. It is stated with its two closings where sharing is described,
and it stays a convention only until one is chosen.
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
- membership facts come from a protected identity graph or an external authority, and not from data
  writable through LOD CRUD — except where a pod has **declared** an ordinary context an authority,
  which is the exception stated below and not a second route in through the front.

This maps the enterprise model without changing its algebra:

| Enterprise concept | sempods policy model |
|---|---|
| Visible Space | Context policy |
| Document ACL | Resource policy, where the resource module is declared |
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

- a context ACR is canonical for one context IRI;
- a resource ACR, where the module is declared, is canonical for one subject IRI; and,
- identity and principal-set facts live in a separate protected authority.

The lookup key is the pair — **which decision, and which IRI** — and not the IRI alone. That is not
tidiness: the two dimensions are independent by
[`SPS-CRUD-011`](../../spec/core/lod-crud.md#SPS-CRUD-011), and a statement may be *about* a context,
which [`SPS-CTX-026`](../../spec/core/contexts.md#SPS-CTX-026) not only permits but illustrates
(`<{pod}/_system/contexts/contacts> rdfs:label "Privat"`). Keyed by IRI alone, that subject's resource
ACR and the contacts context's own ACR would be one document, and a resource policy could then widen
who reaches the context — an inversion of the rule that the finer decision only ever subtracts.

An implementation may represent these as RDF named graphs internally. They are control-plane
graphs, not registered sempods data contexts: they do not appear in context discovery, cannot be
selected by `?context=`, and are unreachable through LOD CRUD.

That needs one more sentence than it has been given, because
[`SPS-CTX-001`](../../spec/core/contexts.md#SPS-CTX-001) says every statement **stored in a pod**
belongs to exactly one context, and a named graph holding an access control resource is stored in the
pod. Invariant 1 is about the pod's *data* — the statements CRUD and SPARQL reach, which is the same
set the sandboxes are stated over — and control-plane state is outside it by construction, which is
what makes it unreachable at all. The invariant survives untouched; what does not survive is
`SPS-CTX-001`'"'"'s wording, which draws no such line today and would have to. That distinction ends the apparent
recursion in which the graph carrying policy would need a user policy of its own.

An ACR is reached through a control-plane route and linked from the target — and *from the target*
needs saying carefully, because a resource decision may control a subject that has no LOD address at
all. [`SPS-CRUD-003`](../../spec/core/lod-crud.md#SPS-CRUD-003) makes the system layer the route that
exists for `did:`, `urn:` and foreign `https:` IRIs, so that is the response carrying the link: the
client follows it from the answer it already has, rather than composing an address, which it may not
do here for the same reason it may not compose a context IRI. Reading or changing it is
itself authorized: `manage` on the target permits policy management, subject to the implicit owner
policy and the OAuth ceiling. The client-facing answer to “what may I do?” remains an effective-
permission view; clients are not expected to reimplement policy evaluation from raw RDF.

**A policy referenced by several targets breaks that sentence, and the break is an escalation.**
`acp:apply` names a policy resource, which is what makes one edit reach a whole channel instead of a
sweep across every article. It also means a caller holding `manage` on one referring target can
rewrite a policy that decides access on targets they hold nothing over — authority acquired by
reference rather than granted. Two ways to close it, and neither is free:

- ~~require `manage` on every referring target~~. **Refused**, not weighed: refusing an edit tells
  the caller that a target they cannot see references this policy, and the rule this repository holds
  itself to is that a caller asking about a context they cannot read gets the same answer as one
  asking about a context that holds nothing. Answering as though the edit succeeded is not available
  either, because it did not. That is the whole branch, so it is gone rather than listed; and,
- **give the shared artifact an authorization boundary of its own** — a policy resource is a target,
  with `manage` on it distinct from `manage` on anything applying it. No leak, and a third thing to
  administer, plus a bootstrap question: who holds `manage` on a policy the moment it is created.

What is open is the second shape and any alternative to it, and the criterion is the one the refused
branch failed: **the answer to an edit must not depend on whether a target the caller cannot see
references the policy.** Until it is settled, a shared policy is safe only where every referring
target has the same manager, which is a condition on the deployment rather than something the pod
checks — the same shape as the declared authority above, and the third entry for the convention side
of that table. It is carried below as an open decision.

The security boundary is topological:

> Authorization facts are read only from stores that no data write can reach.

Looking like policy never makes ordinary RDF authoritative. A caller may write statements about an
ACR IRI or use ACP predicates as ordinary data; none of those statements enter the evaluator's
policy set.

**The one exception, stated rather than buried.** A pod may declare an ordinary context a
principal-set authority — an address book that decides an audience, say — and membership is then read
from a graph the data path can write. That is a hole in the sentence above, and calling it anything
else would be worse than having it. What bounds it:

- it exists only where a pod **declares** it, in control-plane state a data write cannot reach. The
  declaration is the guarantee; the graph it points at is not;
- it carries membership, never policy. No `acp:allow` written into such a context is read, so the
  worst it can do is admit somebody to a set some policy already trusts; and,
- the declaration is sound only while **every agent and client pair whose writes are still in the
  authority held at least `manage` on everything it now grants, by an authority that did not depend
  on those writes**. The last clause is not pedantry: where a target policy grants `manage` to
  members of the set, a caller with `write` on the authority adds itself and the condition then reads
  as satisfied — validated by the very write it was supposed to bound. Where that holds, everyone whose
  writing is being believed could have written the policy directly, and nothing is reachable that was
  not already.

Two things make that condition easy to state wrongly, and both fail in the direction that matters.

**It is about the pair, not the person.** A grant is resolved from the verified client together with
the verified subject ([`SPS-GRANT-002`](../../spec/core/grants.md#SPS-GRANT-002)), and the thing that
writes an address book is usually an application. It can hold `write` on the authority while its
delegation stops well short of `manage` on what the authority grants — at which point the ceiling
refuses to let it write the policy and this route lets it write the answer instead.

**And it is about writes, not writers.** Membership outlives the authority to have written it. A pair
adds somebody while it holds `manage` on everything the set then governs, loses both grants, and the
set stays populated; a later policy references it from a target that pair never managed, and the
condition reads as satisfied because nobody who can write it today lacks anything. The write is still
being believed, so it still has to be covered — which makes revocation and new references the moments
that matter, not the write.

So such an authority is sound where its writers are control-plane code rather than delegated
applications, or where their delegation reaches that far *and* membership is revalidated when the
writers change or a new target references the set. Neither is something the pod checks today.

The condition is on the deployment rather than something the pod checks, which puts it on the
convention side of the table above and makes it the second one to watch. Whether to keep the
exception at all is an open decision below.

This is where [`SPS-CTX-026`](../../spec/core/contexts.md#SPS-CTX-026) acquires a hazard it does not
have today. Treating a statement about a `_system` IRI as ordinary data is right and stays right —
but once policy is RDF, "ordinary data that looks exactly like policy" is something a caller can
write. The requirement does not change; what changes is that an implementation reading policy from
anywhere a caller can reach is now wrong in a way the text does not yet warn about.
[`SPS-CTX-025`](../../spec/core/contexts.md#SPS-CTX-025) already refuses the write path as a route to
control-plane state, and the boundary above is the read-side half it does not state.

## What was rejected, and what is still open

The entries below moved here with the profile. They are decisions about **how the reference
implementation writes policy down**, not about what a pod must do — nothing in the specification
depends on either answer.

**ACP deny and exclusion.** They turn positive confinement into negative evaluation over the
effective policy set. What a positive algebra buys is narrow and worth stating exactly: access
contributed by satisfied policies accumulates by union, with no subtractive exception to account for,
so adding an allow policy never removes access. It does not by itself make the policy set
enumerable backwards from an agent — a principal-set matcher holds a set IRI rather than a list of
agents, owner and creator are server-derived, and a decision also depends on client, issuer, the
OAuth ceiling and — where the module is declared — the resource decision as well. Reading it backwards
starts from the context, which every pod decides: a resource policy nominating a subject in a context
the caller cannot read adds nothing, and treating that decision as the optional one would widen the
answer past the read sandbox. An implementation may still index policies in that direction;
that is a strategy, not a consequence of the algebra.

“Everyone in this group except one person” is expressed one layer down instead: a principal set may
be defined by difference, so the matcher still asks a single membership question. This moves the
negation into the membership resolver rather than removing it. What is monotone is the policy
algebra over unchanged membership facts, which is the property the enforcement mechanisms depend on;
the authorization system as a whole is not monotone, because a membership fact can be withdrawn.

**ACP member inheritance between resources.** An inheriting policy needs a containment relation, and
ACP expects the resource server to supply one. This specification defines none between resources:
[`SPS-CRUD-011`](../../spec/core/lod-crud.md#SPS-CRUD-011) makes a resource and a context independent
dimensions rather than a member and its container, so there is nothing for a resource policy to
descend along. Introducing one later is a definition, not a switch — which relation creates
containment, between which resource kinds, which policies and modes propagate, what bounds the depth
— and the cost ACP's model carries, evaluation over a transitive closure on every decision, is the
reason to answer those before adopting it rather than after.

Between **contexts** the situation differs and the profile above records it as open rather than
rejected: the slash-delimited `manage` coverage of
[`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007) is a specified relation, bounded by path
depth, and `acp:memberAccessControl` is one of the two ways to express it.

Introducing it later is a definition, not a switch: which relation creates containment, between which
resource kinds, which policies and modes propagate, what bounds the depth, and whether it is
`acp:memberAccessControl` or a rule of sempods' own. Until those are answered the exclusion stands,
and the cost ACP's model carries — evaluation over a transitive closure on every decision — is the
reason to answer them before adopting it rather than after.

**Resource policies stored beside each data context.** It makes policy discovery depend on data
visibility, duplicates policy for subjects spanning contexts and lets deleting one context destroy
authority for a resource that still exists elsewhere — [`SPS-CTX-017`](../../spec/modules/context-management.md#SPS-CTX-017)
removes what rested on a deleted context, which is correct for a grant naming it and wrong for a
resource that outlives it. Canonical target-indexed ACRs avoid all three.

**Claiming Solid interoperability.** A single-context, resource-policy pod is close to a Solid
resource-server use case, but sempods resources remain RDF subjects, sempods does not adopt ACP
container inheritance, and its CRUD and SPARQL surfaces remain its own. Protocol interoperability is
a separate feature with a separate conformance cost.

**A context access control resource is not complete on its own.**
[`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007) makes `R#manage` reach `R/inbox`, so a
policy on one context decides another. An engine handed only the descendant's access control resource
does not see the authority governing it — which is precisely the claim per-evaluation conformance
rests on, and this is the artefact every pod has rather than one behind a module.

Two ways close it, both pure ACP, neither free:

- Choose the creation bootstrap between an atomic caller-supplied ACR and an advertised server policy
  template. A third option, an implicit creator policy, is not available in core — and not because
  the fact is unrecorded but because it is undefined. A resource here is a subject some statement
  mentions, so creating one is not an act anybody performs, and a pod routinely holds statements
  about IRIs nobody in it created at all
  ([`SPS-CRUD-003`](../../spec/core/lod-crud.md#SPS-CRUD-003)). `acp:CreatorAgent` is therefore
  unsatisfied here rather than forbidden, exactly as `acp:vc` is in a pod that presents no
  credentials, and a profile built around documents may state a creator and use it.
  [`examples/60-creator.md`](../../examples/60-creator.md) runs both cases.
- Decide how a policy referenced by several targets is authorized for editing. An authorization
  boundary on the policy resource itself is the shape that survives; anything else has to meet the
  same test, that the answer to an edit does not depend on whether a target the caller cannot see
  references the policy. Requiring `manage` on every referring target fails it and is refused above.
  What is still open is the boundary's own bootstrap: who holds `manage` on a policy the moment it
  exists. Sharing a policy is what makes an audience change one edit rather than a sweep, so this is
  not a corner — it is the price of the feature.

- Define the concrete sempods mode and principal-set vocabulary IRIs.
- Decide whether a pod may declare an ordinary context a principal-set authority at all. Refusing it
  keeps the topological guarantee whole and costs the personal case its best feature — an audience
  that follows the app somebody actually uses. Keeping it means the guarantee has a declared hole,
  bounded by a condition on the deployment rather than by the pod, and that condition has to be
  written as a requirement rather than left as advice. Its wording is where the cost shows: it is
  over agent and client pairs rather than people, and over writes that are still believed rather than
  writers who can still write — so keeping the exception means specifying revalidation on revocation
  and on a new reference, not only a rule about who may write.

- **Express the coverage as `acp:memberAccessControl`** on the ancestor's access control resource.
  ACP's own mechanism, and the context path supplies exactly the membership information ACP expects a
  resource server to provide. It costs an ancestor walk on every decision — bounded by path depth
  rather than running a transitive closure, so the objection recorded against inheritance between
  resources does not carry over — and the profile's exclusion of member access control has to become
  an exclusion *between resources*, which is where no containment relation exists.
- **Materialise the policy into each registered descendant.** Every access control resource stays
  self-contained and evaluation stays flat. It costs a write across every descendant when `manage` is
  granted, and [`SPS-GRANT-033`](../../spec/core/grants.md#SPS-GRANT-033) means a descendant that does
  not exist yet cannot be written to — so the policy has to be applied again each time one is created,
  which makes context creation and policy propagation one operation.

Leaving it open is the one thing that is not available: until it is decided, the model's primary
artefact is one an independent engine cannot check on its own, and that is the property the ACP
