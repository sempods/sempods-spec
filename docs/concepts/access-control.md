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

The policy language is a deliberately small profile of the Solid Community Group's
[Access Control Policy (ACP)](https://solid.github.io/authorization-panel/acp-specification/), used
for both decisions: the same vocabulary and the same algorithm, differing only in what `acp:target`
binds to. ACP provides the frame — target, access context, policy, matcher and access mode — without
making sempods a Solid server.

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
the folder in which a resource lives, and ACP member inheritance cannot manufacture that relation.

A context is best read as an **area**: something a caller may enter, addressed by an IRI the pod hands
out, carrying its own permission boundary. That is what
[`SPS-CTX-021`](../../spec/core/contexts.md#SPS-CTX-021) reports — the permissions held *on* the
context, not a summary of everything within it, which is why finer policy inside an area does not
contradict it, any more than a readable folder is contradicted by a file it hides. The reading has two
limits, and both are deliberate rules rather than oversights: deleting an area leaves the areas
beneath it standing ([`SPS-CTX-018`](../../spec/core/contexts.md#SPS-CTX-018)), and a resource does not
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
- silence is private ([`SPS-CTX-027`](../../spec/core/contexts.md#SPS-CTX-027)); and,
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

- ACP as the vocabulary and the algorithm. No implementation emits or evaluates an access control
  resource today;
- policy indexed by the target it controls, and the ACR as an addressable artifact reached through a
  link;
- the resource module as a declared, advertised second decision, rather than one deployment's
  internal arrangement;
- the principal-set matcher and the mode vocabulary; and,
- everything under "Operation boundaries" beyond what the read and write paths already enforce.

The line matters most where the two meet. **The composition rule is the part with a deployment behind
it; expressing either decision in ACP is the part with none.** So the intersection is the least
likely thing here to be wrong, and the ACP profile the most likely to move — which is the reverse of
what the amount of text about each suggests.

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

Two limits on that, and both matter. It holds **per evaluation** and not for the whole decision,
because the conjunction between evaluations and the OAuth ceiling are sempods' and not ACP's. And it
holds for **ACP's own matcher attributes** and not beyond them: an access control resource using the
principal-set matcher defined below carries an attribute a plain ACP engine does not know, so that
engine leaves the matcher unsatisfied where sempods would resolve it through a trusted membership
authority. Checking such a resource needs an oracle that knows the extension, or it reports a
difference that is the extension rather than a defect.

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
([`SPS-CTX-019`](../../spec/core/contexts.md#SPS-CTX-019)) and reaches slash-delimited descendants
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
| A policy states its modes expanded | whatever writes the ACR | convention |
| An ACR carries no `acp:memberAccessControl` | whatever writes the ACR, and today the server as well | convention, and the one to watch |
| A shared policy's referring targets have the same manager | the deployment | convention, until the open decision below closes it |

Policy is written through control-plane operations rather than by hand: somebody shares a document,
and something turns that into a policy. That layer is where a convention lives, and it can hold rules
a policy language cannot express — which is also why the distinction matters, because an owner
holding `manage` can write an ACR directly and step around every convention in it.

That is acceptable for the first two, and the reason is worth stating rather than assumed: they
**fail towards less access**. A hand-written deny is honoured and narrows; modes left unexpanded grant
less than intended. Neither hands anybody access the owner could not have granted outright.

The last two do not. Take member access control first, because it is the one to watch. `acp:memberAccessControl` does not restrict — it adds
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
documents are not all for the same readers — a pod declares the resource module, and `acp:target`
binds to a subject IRI as well. For a statement `q = (subject, predicate, object, context)`:

```text
without the module:  visible(q) = contextAllows(context, read)

with the module:     visible(q) = contextAllows(context, read)
                                    AND resourceAllows(subject, read)
```

The same intersection applies to the requested mode on updates and deletes. It is sempods'
composition rule, not ACP policy union and not `acp:allOf` — the two decisions have different
targets, and ACP has no operator joining two evaluations.

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

The ceiling is expressible in ACP's own vocabulary, but as **its own evaluation** rather than as
policies inside a target's ACR: a per-principal ACR whose policies require the agent and the client
together, with `acp:client` carrying the application's `did:web:` identifier
([`SPS-AUTH-003`](../../spec/core/auth.md#SPS-AUTH-003)). Merged into a target's ACR it would fail,
because ACP composes policies by union while a ceiling can only restrict. And ACP can hold it but
not produce it: `granted = requested ∩ effective`
([`SPS-GRANT-013`](../../spec/core/grants.md#SPS-GRANT-013)) is a computation at consent time, and
the revocation sweep ([`SPS-GRANT-015`](../../spec/core/grants.md#SPS-GRANT-015),
[`SPS-GRANT-016`](../../spec/core/grants.md#SPS-GRANT-016)) is a recomputation over the store. ACP
evaluates a state; it does not establish one.

This preserves immediate policy revocation and the distinction between agent and client. That an
application is not broadened by a policy written for the person is the property being aimed at rather
than one the model already has: a ceiling agreed over a scope reaches whatever enters that scope
afterwards, which is the open decision recorded below. Public authority
does not come from the agent and therefore cannot be delegated or removed by the agent's OAuth
ceiling. The ceiling constrains **modes**, and whether it can also constrain targets is open in a way worth
being exact about: with `acp:target` bound to the principal, one evaluation answers for every request
that person makes, and nothing in it names the data target — so a per-target ceiling needs either a
second artifact carrying the target or a sempods rule selecting among several delegation policies.
That is the scope question recorded below, and it is unanswered rather than merely unwritten. OAuth
owns how a person selects the subset, while access control owns the per-request decision.

Public access becomes an ordinary context policy and, where the resource module is enabled, an
ordinary resource policy as well, matched by ACP's public-agent semantics. The sempods profile permits that
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
selected by `?context=`, and are unreachable through LOD CRUD. That distinction ends the apparent
recursion in which the graph carrying policy would need a user policy of its own.

An ACR is reached through a control-plane route and linked from the target. Reading or changing it is
itself authorized: `manage` on the target permits policy management, subject to the implicit owner
policy and the OAuth ceiling. The client-facing answer to “what may I do?” remains an effective-
permission view; clients are not expected to reimplement policy evaluation from raw RDF.

**A policy referenced by several targets breaks that sentence, and the break is an escalation.**
`acp:apply` names a policy resource, which is what makes one edit reach a whole channel instead of a
sweep across every article. It also means a caller holding `manage` on one referring target can
rewrite a policy that decides access on targets they hold nothing over — authority acquired by
reference rather than granted. Two ways to close it, and neither is free:

- **require `manage` on every referring target.** Safe, and it leaks: refusing an edit tells the
  caller that a target they cannot see references this policy, which is exactly the kind of
  requirement `AGENTS.md` calls a defect. Answering as though the edit succeeded is not available
  either, because it did not; and,
- **give the shared artifact an authorization boundary of its own** — a policy resource is a target,
  with `manage` on it distinct from `manage` on anything applying it. No leak, and a third thing to
  administer, plus a bootstrap question: who holds `manage` on a policy the moment it is created.

Until one is chosen, a shared policy is safe only where every referring target has the same manager,
which is a condition on the deployment rather than something the pod checks — the same shape as the
declared authority above, and the third entry for the convention side of that table. It is carried
below as an open decision.

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
  authority holds at least `manage` on everything it now grants**. Where that holds, everyone whose
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
covering it ([`SPS-CTX-019`](../../spec/core/contexts.md#SPS-CTX-019),
[`SPS-GRANT-033`](../../spec/core/grants.md#SPS-GRANT-033)). Nothing more is needed, because a new
resource is covered by its context's policy from the moment it exists.

**Deleting a context is the operation the composition rule does not yet reach.** It removes every
statement the context holds ([`SPS-CTX-017`](../../spec/core/contexts.md#SPS-CTX-017)) and is
authorized from the context grant alone
([`SPS-CTX-019`](../../spec/core/contexts.md#SPS-CTX-019)), so with the resource module declared a
caller holding `manage` on a context destroys statements about subjects whose resource policies
refuse them `write` — the one route where the second decision is skipped rather than applied. The
rule above covers mutations of an existing resource; a bulk lifecycle operation is not one of those
and needs saying either way. The two ways to say it:

- **compose it like any other mutation** — deletion requires the resource decision to allow `write`
  on every affected subject. Consistent, and it makes an operation the chapters describe as a single
  authorization decision depend on however many subjects the context happens to hold, with a partial
  failure to define; and,
- **state it as an exception**, on the ground that `manage` on a context already means creating and
  deleting the context itself rather than editing what is in it, and that a context nobody may enter
  is not made safer by the policies inside it. Simpler, and it has to be written down rather than
  left to be inferred, because it is the one place the words "both must allow" stop being true.

This is carried below as an open decision. It is not reachable today — the module does not exist — but
it is reachable the moment it does.

The resource module reopens the question, and only there. A new resource has no resource policy yet,
so creation and that policy have to be one operation from the client's perspective — otherwise the
resource is born unreachable, or reachable while it should not be. Which bootstrap policy applies is
an open design choice; what is not open is that silent creation without one leaves the module
incomplete.

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
- context policy and resource policy are one vocabulary and one algorithm differing only in what
  `acp:target` binds to, so a tool that reads one reads the other; and,
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
| [`SPS-CORE-004`](../../spec/core/index.md#SPS-CORE-004) — every `MUST` in `contexts` is core, with no partial core | Adding the resource module does not touch it. Letting a pod omit the *management* of several contexts does: the lifecycle ([`SPS-CTX-015`](../../spec/core/contexts.md#SPS-CTX-015)) and the management route ([`SPS-CTX-005`](../../spec/core/contexts.md#SPS-CTX-005)) are core obligations today, and moving them behind a declaration relocates them. Discovery ([`SPS-CTX-021`](../../spec/core/contexts.md#SPS-CTX-021)) stays where it is: a write names its context and a client may not construct that IRI, so the route it reads the name from is needed most in the pod with the fewest contexts |
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

**A context access control resource is not complete on its own.**
[`SPS-GRANT-007`](../../spec/core/grants.md#SPS-GRANT-007) makes `R#manage` reach `R/inbox`, so a
policy on one context decides another. An engine handed only the descendant's access control resource
does not see the authority governing it — which is precisely the claim per-evaluation conformance
rests on, and this is the artefact every pod has rather than one behind a module.

Two ways close it, both pure ACP, neither free:

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
profile exists to buy.

The rest are ordinary open questions:

- Decide whether `public-read` still earns a scope. Nothing about public access has to be withdrawn —
  the `public` flag, its private default and the guarantee that an unauthenticated caller reads
  exactly the public contexts all keep their subject
  ([`SPS-CTX-027`](../../spec/core/contexts.md#SPS-CTX-027),
  [`SPS-GRANT-031`](../../spec/core/grants.md#SPS-GRANT-031)). But once a public context carries an
  ordinary policy matched by ACP's public-agent semantics, an anonymous request is already satisfied
  by the policy, and the scope
  ([`SPS-GRANT-020`](../../spec/core/grants.md#SPS-GRANT-020)) is left doing only what the OAuth
  ceiling does anyway.

- Choose the creation bootstrap between an atomic caller-supplied ACR and an advertised server policy
  template. A third option, an implicit creator policy, is not available in core — and not because
  the fact is unrecorded but because it is undefined. A resource here is a subject some statement
  mentions, so creating one is not an act anybody performs, and a pod routinely holds statements
  about IRIs nobody in it created at all
  ([`SPS-CRUD-003`](../../spec/core/lod-crud.md#SPS-CRUD-003)). `acp:CreatorAgent` is therefore
  unsatisfied here rather than forbidden, exactly as `acp:vc` is in a pod that presents no
  credentials, and a profile built around documents may state a creator and use it.
  [`examples/60-creator.md`](../../examples/60-creator.md) runs both cases.
- Decide how a policy referenced by several targets is authorized for editing — `manage` on every
  referring target, which is safe and leaks topology, or an authorization boundary on the policy
  resource itself, which does not leak and adds a third thing to administer and a bootstrap question
  with it. Sharing a policy is what makes an audience change one edit rather than a sweep, so this is
  not a corner: it is the price of the feature.
- Decide how deleting a context composes with the resource decisions inside it, once the module
  exists: as a mutation requiring `write` on every affected subject, or as a stated exception where
  context `manage` carries the whole context. Leaving it unsaid is the only option that is wrong,
  because the operation removes statements either way.
- Define the concrete sempods mode and principal-set vocabulary IRIs.
- Decide whether a pod may declare an ordinary context a principal-set authority at all. Refusing it
  keeps the topological guarantee whole and costs the personal case its best feature — an audience
  that follows the app somebody actually uses. Keeping it means the guarantee has a declared hole,
  bounded by a condition on the deployment rather than by the pod, and that condition has to be
  written as a requirement rather than left as advice. Its wording is where the cost shows: it is
  over agent and client pairs rather than people, and over writes that are still believed rather than
  writers who can still write — so keeping the exception means specifying revalidation on revocation
  and on a new reference, not only a rule about who may write.
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
- Define how a pod installs complete resource policies before declaring the resource module, given
  that an evaluator with no matching policy denies — and, in the same decision, when a resource ACR
  is **retired**. A resource ACR is indexed by subject and independent of any data context, so
  deleting a subject's last statement leaves its policies standing; recreating that subject then
  publishes new content under old grants, with no bootstrap in between. A subject whose statements
  span several contexts makes "its last statement" a question rather than an event, which is why
  retirement belongs beside installation rather than after it.

These are not all the same kind of open. Every one above except the last is a **contract blocker**:
until it is answered there is no target contract to implement, so nothing can be conformant against
it. The sandbox restatement belongs in that group rather than beside it — the read sandbox is what
the resource module has to preserve, and the paragraph below says as much when it observes that
partial query support claims no conformance.

The last is an **adoption blocker** — a pod that never declares the resource module has nothing to
install, and a pod that does needs its policies in place before the second decision starts denying.

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
