# Access control

Status: **Proposed; non-normative.**
Owning issue and adoption: [#68](https://github.com/sempods/sempods-spec/issues/68).
The design was introduced by [#52](https://github.com/sempods/sempods-spec/pull/52); its merge did
not adopt it. [#69](https://github.com/sempods/sempods-spec/issues/69) owns unresolved contract
choices, [#70](https://github.com/sempods/sempods-spec/issues/70) their normative preparation, and
[#72](https://github.com/sempods/sempods-spec/issues/72) validation against that candidate.

## Purpose

This is the authorization part of the [authorized data access proposal](data-access.md). It proposes
observable guarantees for reads, writes, queries and delegation while leaving policy mechanisms to
implementations, following [the vision](../vision.md#what-belongs-in-the-contract). Data access owns
the core/module split and requirement impact; this document develops the operation boundaries.

## The current model

The [specified boundary](data-access.md#the-specified-boundary) remains Context-based. The
[grants chapter](../../spec/core/grants.md) also defines the owner's implicit authority and bounds
an application's delegation by the person's effective permissions.

The [worked ACP scenarios](../../examples/README.md) illustrate one possible design. Their
[fixture guide](../guides/acp-fixtures.md) separates supplied assumptions from specified behavior.
The [ACP implementation proposal](authorization-implementation/README.md) retains design choices
awaiting disposition under #64; it describes no verified implementation.

## Policy-independent enforcement

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

## Operation boundaries

### Queries and retrieval

For fixed data and authorization state, a supported SPARQL query returns the result it would produce
against the caller-authorized dataset. The dataset is a semantic model of what can be observed; the
implementation need not materialize it. Views, native store restrictions and query rewriting are
possible enforcement mechanisms if they preserve that result.

The [logical dataset recommendation](data-access.md#logical-dataset-and-operation-scope) defines
an aggregate default graph, authorized named projections, ordinary-write placement and explicit
selection. Graph placement and disclosable graph names are part of the result contract, not storage
choices. Conformance fixtures use identical logical membership and names across implementations;
physical partitions remain free. Empty datasets still use standard query evaluation, including
empty group patterns and aggregates.

Client-supplied dataset clauses and graph names cannot widen access. Store-local authorization data
and other pods are outside the caller's data view unless an explicit contract makes them available.

Filtering final results is insufficient. Hidden statements must not alter an ASK answer, aggregate,
negation, join, property path or subquery. For example, adding a document hidden from a caller leaves
that caller's count unchanged. Filtering a resource out after counting it fails that comparison.

The same read policy applies to direct resource reads and find. Hidden text cannot nominate a
visible search hit; unreadable statements cannot affect matching, ranking, limits or expansion.
Find's ranking may remain implementation-defined, while this isolation property does not.

### Mutations and partial representations

The following recommendations are the mutation portion of
[#69](https://github.com/sempods/sempods-spec/issues/69), reviewed against specification revision
`4e7a27044dbcadc318f288cb9111edc8eeccd9ec`. They remain **proposed**, including the changed slot
outcomes. The [current CRUD chapter](../../spec/core/lod-crud.md) continues to bind. The proposed
[logical dataset](data-access.md#logical-dataset-and-operation-scope) identifies the graphs a
request addresses; both recommendations need coordinated review before normative adoption.

#### Standard behavior and the pod's remaining choice

Use [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) for method and conditional-request
semantics, [RFC 5789 §2](https://www.rfc-editor.org/rfc/rfc5789.html#section-2) for PATCH atomicity,
and [RFC 7396 §2](https://www.rfc-editor.org/rfc/rfc7396.html#section-2) for JSON Merge Patch.
Those standards do not select the RDF facts addressed by a pod operation or its authorization
boundary. These are the choices below. No policy language, storage partition or transaction
algorithm follows from them.

The **operation scope** consists of the addressed resource, slot or edge within the logical data
space selected by the [dataset recommendation](data-access.md#logical-dataset-and-operation-scope):
the whole space for an ordinary operation, or the explicitly selected Context graph. It is fixed
independently of which stored facts happen to be readable. A filtered GET is a read representation, not permission to redefine
a later PUT as replacement of just that visible subset.

| Operation | Recommended effect within that scope |
|---|---|
| Resource PUT | Replace all outgoing statements of the addressed subject; preserve incoming statements. |
| Resource DELETE | Remove all outgoing statements of that subject; preserve incoming statements. |
| Object-shaped merge PATCH | Replace or remove the complete values of each named predicate, including `@type` where supplied; preserve unnamed predicates. Apply the existing canonical-shape constraints and RFC 7396 arrays/nulls. |
| Slot PUT / DELETE | Replace / clear all values of the addressed subject and predicate. |
| Slot POST | Add the supplied set of values as one operation; existing values are unchanged. |
| IRI edge DELETE | Remove the single addressed triple; preserve other values. |

For every operation, authorization covers its entire effect, including facts removed by omission
and the values being added. A request either applies that effect completely or changes nothing.
A body that names only permitted additions does not authorize replacing protected old values.
A no-op does not bypass authorization. Admission to a write request is checked even when the body
names no changes: PATCH requires current authority to edit at least one predicate of the addressed
resource; slot POST requires current authority to add at least one value to the addressed slot.
These are permissions over possible edits, independent of whether any such fact currently exists.
For a non-empty body, admission alone is insufficient: every requested effect is also authorized.
This describes an authorization outcome, not a new stored permission or policy API.

An empty `{}` PATCH, a PATCH containing only the matching `@id`, and an empty `[]` slot POST remain
valid no-op inputs. After admission and applicable preconditions, recommend `204` with no body,
Location or validator and no resource creation. An authenticated read-only or unrelated caller gets
`403` for existing, hidden and absent targets alike; missing or invalid credentials get `401`.
The target's absence alone does not prevent admission where policy permits an edit there. An empty
slot PUT or a PATCH assigning an empty array is different: it clears values and needs authority for
that effect. Atomicity covers the addressed logical scope, including all occurrences affected by an
ordinary aggregate operation; it introduces no bulk-operation API.

#### Complete scope authority and non-disclosure

Recommend authorizing the whole resource for PUT/DELETE, the complete named predicates for merge
PATCH, the whole slot for replacement/clearing, and the named values for addition or edge removal.
The authority covers both additions and removals. Finer authorized edits can therefore succeed
while an entire resource replacement is refused. A response that distinguishes existence, such as
resource creation versus replacement, additionally requires authority to observe that distinction.
In particular, unconditional predicate replacement by PATCH or slot PUT needs complete write
authority over that predicate, including any unreadable values it removes; complete read visibility
is not an additional requirement. Hidden values that are not writable still prevent replacement.
Use a content-free success response (`204` for PATCH, `200` for slot PUT), subject to the metadata
rule below. No exported policy catalogue or new authorization flag is needed.

"Complete" is a property of the authority for that scope, including empty states. Comparing the
currently visible facts with the stored facts is insufficient: accepting when no hidden fact
exists and refusing when one exists would itself disclose hidden data. Under unchanged authorization state (including policy inputs),
caller-visible data and request, varying hidden facts cannot change the refusal or any visible
mutation effect. If the implementation cannot satisfy that property for a scope, it refuses that
class of mutation consistently, including on the corresponding empty scope. A deployment can
still grant complete authority over selected subjects, predicates or values and support their
successful operations.

For a valid authenticated caller whose operation is not authorized, recommend a uniform `403`
without existence diagnostics, validators or a Location header. An invalid credential remains a
`401`; data reads keep their absent/inaccessible `404` behavior. Determine authorization before
returning an existence-dependent write result. This is the proposed generalization of
[#45](https://github.com/sempods/sempods-spec/issues/45); that issue still owns the current
Context-oracle repair. Syntax errors and unsupported media types retain their normal errors and
must not depend on hidden facts.

Write authority need not imply read authority universally. For example, an explicitly authorized
set addition can return the uniform `204` proposed below without revealing whether the value was
already present. That does not authorize removing a protected existing value. A resource PUT
supplying outgoing statements keeps its creation/replacement distinction and therefore needs
visibility of that distinction as well as complete write authority. A pod cannot claim success for
a partial replacement, or accept a hidden collision by redirecting the write elsewhere.

#### Preconditions and concurrent changes

Apply current authorization independently of the supplied validator. Follow RFC 9110 §13.2.1 for
precondition evaluation after the normal request checks: an unauthorized caller gets the same
refusal with `If-Match`, `If-None-Match: *` or no conditional field. Preconditions are evaluated
only when the unconditional response would be successful or `412`; otherwise preserve the normal
error. Thus an authorized resource DELETE of an absent target stays `404` even with `If-Match: *`.
When evaluation applies, a false precondition yields `412` and no change.

Validators identify the selected representation. They grant no authority and must not change
solely because hidden data changed. LOD and system aliases for the same subject, logical scope and
representation agree. A changed scope cannot reuse a previous tag to validate a different target;
a changed policy is always enforced, even if the selected bytes and tag are unchanged. Resource
and slot tags remain specific to their own representations.

For every mutation, response content and metadata reveal only state the caller may read. A blind
replacement therefore does not echo the stored values. A validator is emitted only when the caller
may read the complete representation it validates; omit ETag, Last-Modified and other metadata
derived from unreadable state. A filtered-view tag cannot validate replacement of unreadable
facts. Uniform status codes alone do not prevent this disclosure. For slots, this requires a
coordinated change to [`SPS-CRUD-052`](../../spec/core/lod-crud.md#SPS-CRUD-052).

An otherwise applicable condition that tests unreadable state, or would validate replacement of
unreadable facts, receives uniform `403`, with no mutation or validator. This includes `If-Match`
and `If-None-Match: *`; do not evaluate a hidden-state predicate and distinguish true from false.
For a slot mutation that evaluates a complete-slot condition, the caller therefore needs complete
slot visibility. Unconditional authorized additions, replacements and clearing remain available.
Empty slot POST and empty resource PUT follow the same condition rule. Existing prescribed
ignoring of conditions, such as edge DELETE's `If-Match`, remains separate from evaluation and
introduces no state test. The proposal changes CRUD-034/052/053/054's applicability and needs
matching OpenAPI wording at adoption.

The current Context-specific slot-tag rules continue to bind until normative adoption;
[#9](https://github.com/sempods/sempods-spec/issues/9) can repair their current OpenAPI view
independently.

Authorization, preconditions and effects need one coherent outcome under races. A completed
revocation precedes authorization of the next request. Overlapping writes and revocation may be
ordered either way, but must not combine an earlier permission decision with a later incompatible
target or return a partly applied effect. This requires observable consistency, not a particular
lock, database transaction or write/check sequence.

#### Slot batches and outcomes

For [#6](https://github.com/sempods/sempods-spec/issues/6), recommend retaining multi-value slot
POST and reporting successful completion with `204`, without a body or Location. The effect is
set addition regardless of whether none, some or all supplied values were already present.
Duplicates in the request do not create duplicate RDF statements. A single unauthorized value
refuses the complete request; no permitted prefix is inserted. The permission to add a named value
is checked even if it already exists, so a no-op cannot disclose membership by bypassing a denial.

Recommend the same `204` completion for slot and edge DELETE, including an already empty slot or
absent edge after authorization. For a resource PUT supplying at least one outgoing RDF statement,
retain `201` plus Location when the addressed scope previously had none, and `200`/`204` otherwise.
Resource DELETE retains `204`/`404` after authorization. These existence distinctions require
permission to observe that scope.

A valid resource PUT supplying no outgoing RDF statements is a clearing operation, including a
body containing only the matching `@id` or only empty predicate arrays. With complete whole-resource
write authority, return `204` without a body, Location or validator whether the scope was empty or
not; preserve incoming links. No separate resource marker is created. A subsequent GET with no
visible outgoing statements returns `404`. Conditional requests follow the rules above: a caller
entitled to test existence can use `If-None-Match: *`; a false condition still gives `412`, while
repeating an empty PUT against the empty scope succeeds with `204`. This explicitly revises
CRUD-033's creation classification rather than making empty RDF input invalid.

This deliberately replaces the current custom slot/edge outcome bodies and POST `201` distinction
in CRUD-044/047, together with the validator changes above. A client permitted to read resulting
values reads the slot. No batch result envelope,
literal-edge URL, or arbitrary choice of one new edge for Location is introduced. The normative
patch must align the status/body descriptions and references together; this recommendation changes
no current OpenAPI schema.

#### Request cases for review

Let `R` be `https://example.org/alice/notes/one`, `p` be `https://schema.org/name`, and `q` be
`https://example.org/private`. Requests use the existing LOD and system route encodings. Each row
states policy setup; it is a proposed protocol case, not an executed ACP fixture.

| Setup and request | Recommended response and effect |
|---|---|
| Complete resource authority; PUT R with only `p = ["new"]` over `p = ["old"]` | `200` or `204`; the outgoing resource is replaced, incoming links survive. |
| Same authority, absent R; PUT supplying p with `If-None-Match: *` | `201`, Location R; repeating it gives `412` and preserves the first write. |
| Policy permits only p; GET R returns p; PUT R containing p | `403`, no changes, both when q has hidden values and when q is empty. A resource replacement is outside this authority in both states. |
| Same policy; PATCH R with `{"https://schema.org/name":[{"@value":"new"}]}` | Success with the complete p array replaced; q is unchanged. Complete write authority over p is assumed, including unreadable values; partial read visibility alone does not require refusal. Return `204` without unreadable content or metadata. |
| Policy gives no complete authority over R; PUT R with `If-None-Match: *` | Same `403` for a hidden existing R and an absent R; no Location, validator or mutation. |
| Complete slot authority; p contains A; POST the IRI values A and B | `204`; p contains A and B. Repeating gives `204` with no further change. |
| Caller may add A but lacks authority for B; POST A and B | `403`; neither value is added, including when B is absent. |
| Authorized resource edit with stale `If-Match` | `412`, no changes. With authority revoked before the request, `403` instead. |
| Hidden q changes while the caller can read only p | The visible representation/tag and the authorized p-only edit are unaffected; whole-resource replacement remains uniformly refused. |
| An authorized edge is already absent; DELETE that edge | `204`; other values survive. Without authority for that edge, uniform `403` whether present or absent. |
| Authorized resource DELETE of absent R, with `If-Match: *` or a supplied tag | `404`, no change; the unconditional error makes the precondition inapplicable. |
| Caller may add B to p but cannot read the complete slot; unconditional POST B | `204`, no validator or hidden-state metadata. Hidden A changing before a repeat does not change the response. |
| Same blind writer; slot POST B or `[]` with `If-Match` or `If-None-Match: *` | Uniform `403`, no change, for both matching/nonmatching tags and empty/nonempty slots. |
| Caller may edit p of R but not q; unconditional PATCH `{}` or a matching `@id` only | `204`, no validator or creation, whether R is present or absent. A read-only caller gets `403` in both cases. |
| Caller may add B to p; unconditional slot POST `[]` | `204`, no validator or creation, whether p is empty or not. A caller with no addition authority gets `403`; missing/invalid credentials get `401`. |
| Complete resource write authority; unconditional PUT R with only its matching `@id` | `204`, no Location, validator or persistent marker, on both absent and existing R. Outgoing statements are cleared, incoming links survive; repetition remains `204`. |
| Same writer may observe existence; empty PUT R with `If-None-Match: *` | `412` if outgoing statements exist; otherwise `204`, including repetitions. Without authority to test that state, uniform `403`. |
| Complete write authority over p, only partial read visibility; unconditional slot PUT with a new array | `200`, no body or unreadable-state metadata; all p values are replaced, including writable hidden ones, and q survives. |
| Some existing p values are outside write authority; PATCH replacing p or slot PUT | Uniform `403`, no change, whether protected values currently exist or not. |

Repeat the cases through aliases and in a single-graph, Context-based and area/document-policy
model once their logical scopes are defined. Include concurrent revocation, input validation,
retries, mixed batches and zero-change outcomes. The observable cases are the acceptance target;
implementation setup may differ.

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

Bulk administration has a distinct authorization question from editing one resource. The
[Context lifecycle recommendation](context-contract.md#lifecycle) authorizes its complete
administrative effect independently of ordinary data-write restrictions. It specifies uniform
outcomes across hidden-data differences and preserves unrelated memberships on deletion.

## Optional Context permissions

The Context module supplies a named-graph access profile with explicit selection and observable
Context-level modes. Those modes do not define RDF graph semantics or require stored grant strings;
core-only implementations need neither synthetic Contexts nor a global rights catalogue.

Where a pod adds finer restrictions, a reported Context grant describes that level's authority.
It is not a guarantee that every resource operation succeeds. The
[registry proposal](context-contract.md#catalogue-and-caller-rights) defines the caller-scoped
summary and its cache boundary. Any more precise permission hint needs an explicit target and
operation; the later request is still authorized.

## Who may share, and why there is no chain

This is a proposed sharing design for Context-based implementations, retained for the worked
resharing example. Core specifies no interpersonal sharing API and does not require this design.
Its peer rules are candidates for an optional Context contract; the owner's implicit authority is
already specified by `SPS-GRANT-011`.

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

The reader-resharing alternative needs provenance to distinguish the supplied end states.
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


## What the examples establish

The ACP fixtures check the listed access decisions under their supplied assumptions.
The resharing case compares supplied end states; it does not execute the revocation process.
The runner's self-tests verify its guards, not the security of an implementation's query engine.
A green run is therefore evidence about those fixtures, not conformance of either proposed core or
a future Context module.

## Validation before adoption

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

This proposal does not standardize an ACP management API or require every policy to be exportable.
It makes no Solid conformance claim. [Data mirroring](data-access.md#mirroring-data) is separate
from delegation: copies are governed by the destination's policy, and source revocation does not
recall them automatically.
