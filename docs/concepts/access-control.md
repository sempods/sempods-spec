# Access control (Concept)

## Purpose

A pod decides access to data for a verified caller and client. Core specifies the effects that
decision has on reads, writes, queries and delegation. The policy language, evaluation strategy and
management interface belong to the implementation.

This is the authorization part of the [authorized data access proposal](data-access.md).
Sections marked **SOLL** are proposed behavior, not adopted requirements. That document owns the
core/module split and requirement impact. This one owns the boundaries a different policy model
still has to preserve.

## The current model (IST)

The normative chapters require Contexts as the permission boundary
([contexts](../../spec/core/contexts.md)), durable per-Context grants and their mode implications
([grants](../../spec/core/grants.md)), and explicit write selection
([`SPS-GRANT-025`](../../spec/core/grants.md#SPS-GRANT-025)). The owner has implicit authority, and
an application's delegation is bounded by the person's effective permissions. The query sandbox is
currently restricted to readable Contexts and forbids enforcement by rewriting
([`SPS-SPARQL-007`](../../spec/core/sparql.md#SPS-SPARQL-007),
[`SPS-SPARQL-009`](../../spec/core/sparql.md#SPS-SPARQL-009)).

The [worked ACP scenarios](../../examples/README.md) exercise one design combining area and resource
decisions. Their runner verifies ACP resolution over supplied fixtures; it does not verify an HTTP
server, a query rewrite, revocation races or lifecycle transitions. The
[reference implementation's profile](../reference-implementation/acp-profile.md) and
[authorization state](../reference-implementation/authorization-state.md) describe that design.
They are implementation proposals, not additional core requirements.

## Policy-independent enforcement (SOLL)

A request's authority follows from the verified caller and client, the requested operation, the
applicable delegation and the pod's current policy. Core does not prescribe Contexts, role
hierarchies, policy storage or one evaluator. An implementation can combine area and document
conditions, use resource policies alone, or have a small fixed permission model.

Where a deployment uses two independent restrictions, both constrain the operation. For example,
area access and a document policy can compose by intersection. This is one implementation's design,
not an obligation to give every pod two policy layers. Internal use of ACP or of document-level
conditions requires no feature declaration. A module declaration is needed for an additional
client-facing contract, such as Context selection or interoperable policy management.

An implementation's own administrative UI can manage policies without a core policy API. Reading
policy syntax, evaluating a request and editing permissions are separate capabilities. A generic
client need not understand private attributes or reproduce the server's evaluator. Neither the
ability to read a resource nor possession of an access token grants policy-management authority.

### Delegation and revocation

An authenticated application receives only the non-public authority actually delegated to it, bounded
by what the person may delegate. Public access is separately authorized by the pod's policy.
Service clients are authorized as themselves; they do not acquire a fictional person's delegation.
Client isolation survives whichever storage model supplies the answer.

A completed revocation affects the next request even if a credential has not expired. Narrowing the
person's authority narrows dependent delegations; widening it does not silently restore a delegation
that was removed. Races between consent, token issuance and revocation must preserve those outcomes.
Core specifies that result rather than a mandatory order of database writes and reads.

A changing audience makes the delegation boundary a substantive contract question. Access to a
collection may include resources added later; access to a selected set may not. These are different
authorizations. The [delegation example](../../examples/50-delegation.md) illustrates why a policy
change can broaden reachable data without changing a stored grant. Settle how consent distinguishes
such scopes before generalizing the current per-Context ceiling; a broad token scope is not an
answer on its own.

### Public access and `public-read`

Public access follows explicit current policy and is available without a credential. Omission does
not publish data, and a rejected credential never turns into an anonymous request. A client receives
deterministic protocol errors without learning whether inaccessible data exists.

Before adoption, decide whether the `public-read` OAuth scope survives. If retained, define how it
adds public data to an authenticated caller's view, how an anonymous subject receives a token, and
how policy changes and delegation revocation affect it. Replace the current "no public context"
issuance test with a rule that a core-only pod can implement, including a pod with no currently
public data. If removed, define the replacement behavior and migration for clients requesting it.
Unauthenticated public reads and invalid-credential rejection remain guarantees in either case.

## Operation boundaries (SOLL)

### Queries and retrieval

For fixed data and authorization state, a supported SPARQL query returns the result it would produce
against the caller-authorized dataset. The dataset is a semantic model of what can be observed; the
implementation need not materialize it. Views, native store restrictions and query rewriting are
possible enforcement mechanisms if they preserve that result.

The dataset includes graph placement and observable graph names, not only a set of triples
([SPARQL 1.1 §13](https://www.w3.org/TR/sparql11-query/#rdfDataset)). A triple in the default graph
does not match `GRAPH ?g { ?s ?p ?o }`; the same triple in a named graph does. An implementation
cannot expose arbitrary storage partitions and still claim equivalent results for the same logical
data. A named graph is not automatically a sempods Context.

The client-visible layout is an open contract decision before adoption: define the default graph,
which named graphs are observable, where ordinary core writes appear, and how explicit Context
selection interacts with both. Settle `GRAPH`, `FROM`, `FROM NAMED` and protocol dataset parameters
against that layout. The RDF dataset model alone does not choose it, and this proposal does not
exclude graph-sensitive queries to avoid the decision. Conformance fixtures need identical logical
graph placement and names across implementations, while physical storage remains free.

Client-supplied dataset clauses and graph names cannot widen access. Store-local authorization data
and other pods are outside the caller's data view unless an explicit contract makes them available.

Filtering final results is insufficient. Hidden statements must not alter an ASK answer, aggregate,
negation, join, property path or subquery. For example, adding a document hidden from a caller leaves
that caller's count unchanged. Filtering a resource out after counting it fails that comparison.

The same read policy applies to direct resource reads and find. Hidden text cannot nominate a
visible search hit; unreadable statements cannot affect matching, ranking, limits or expansion.
Find's ranking may remain implementation-defined, while this isolation property does not.

### Mutations and partial representations

A permitted operation has the specified effect on its addressed resource, slot or edge. Storage
partitions cannot silently redirect it, and a failed authorization cannot leave a partial mutation.
Conditional requests validate the representation and operation scope they protect. LOD and system
addresses for the same resource agree.

Three cases require exact normative answers before the proposal can be adopted:

| Case | Property to preserve |
|---|---|
| A read hides some properties, then a client sends PUT based on that read | Protected statements are not silently removed; the response does not claim a complete replacement when only a different subset changed. |
| A client creates a resource whose IRI is already used by hidden data | Neither overwriting hidden data nor distinguishing its existence through a different outcome is acceptable. |
| A policy or destination changes between GET and a conditional write | A validator for the earlier representation cannot authorize an unrelated mutation or bypass the current permission decision. |

The normative write scope must say when the entire operation is authorized, when it is refused and
whether a separately specified partial operation is available. Applying permissions to the request
body alone is insufficient: replacement and deletion also affect statements the body does not name.

### Creation and lifecycle

An empty pod can authorize creation under its existing policy without first exposing a Context.
An implementation may provision internal storage or initial policy during an authorized setup or
creation flow. A request does not acquire management authority just because something is absent.

Where resource creation needs an initial policy, both become effective together from a client's
perspective. Cancellation or failure grants nothing. Reusing an identifier must not accidentally
restore a delegation that was revoked. The lifecycle of policy retained after deletion therefore
needs a deliberate implementation mapping to the core revocation contract.

Ordinary RDF about a control-plane IRI is data. It is not a policy update. Implementations may offer
separate administrative interfaces, but those interfaces enforce their own authority; a blanket ban
on every write interface beyond sempods CRUD would prevent legitimate administration.

Bulk administration has a distinct authorization question from editing one resource. An optional
Context-management contract must decide how deletion interacts with finer policies, without
revealing hidden resources through its success or failure. It cannot leave that decision to the
phrase "both must allow" or silently inherit ordinary document-write permissions.

## Optional Context permissions (SOLL)

The Context module can standardize named areas, explicit selection, mode implications and
context-level grants. Those are promises to clients using that module. They do not require a
core-only implementation to synthesize a Context or a global rights catalogue.

Where a pod adds finer restrictions, a reported Context grant describes that level's authority.
It is not a guarantee that every resource operation succeeds. The module must define that meaning
so clients do not mistake a coarse grant for the fully evaluated request decision. Any more precise
permission hint needs an explicit target and operation; the later request is still authorized.

## Who may share, and why there is no chain (SOLL)

This is a proposed sharing design for Context-based implementations, retained for the worked
resharing example. Core specifies no interpersonal sharing API and does not require this design.
Its peer and owner assumptions belong to the optional Context contract.

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


## What the examples establish (IST)

The ACP fixtures show that the chosen policy design can express the listed access decisions.
The resharing case compares supplied end states; it does not execute the revocation process.
The runner's self-tests verify its guards, not the security of an implementation's query engine.
A green run is therefore evidence about those fixtures, not conformance of either proposed core or
a future Context module.

## Validation before adoption (SOLL)

Use two implementations with different policy mechanisms and the same public requests. Configure
known allowed and denied resources through each implementation's own setup. Check successful CRUD,
rejected writes with no partial changes, revocation with an existing credential, and equivalent
authorization on direct reads, SPARQL and find. Always denying access is not a passing implementation.

For query enforcement, compare results with a reference evaluation over the same authorized dataset,
including its logical graph placement and names. Include unqualified patterns, `GRAPH ?g`, fixed
graph names, aggregates, negation, subqueries, paths and adversarial dataset clauses. Alter hidden
data and physical partitions while holding that logical dataset fixed. Test find for hidden
matches, ranking and expansion. Cover public reads without credentials, tokens with and without
`public-read`, no currently public data, policy changes, revocation and invalid credentials.
An enforcement mechanism earns conformance from these observable properties, not its name.

The outstanding protocol decisions are generic mutation scope, the delegation ceiling for changing
audiences, the `public-read` migration, client-visible dataset layout and the optional Context
contracts. Rewrite correctness is an implementation obligation.
Installation of an implementation's policies is a deployment concern unless a client-facing
management contract is being specified.

## Scope

This concept does not standardize an ACP management API or require every policy to be exportable.
It makes no Solid conformance claim. [Data mirroring](data-access.md#mirroring-data-soll) is separate
from delegation: copies are governed by the destination's policy, and source revocation does not
recall them automatically.
