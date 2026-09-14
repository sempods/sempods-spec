# A possible ACP authorization profile

Status: **Proposed implementation design; non-normative.** Disposition and intended recipient:
[#64](https://github.com/sempods/sempods-spec/issues/64), under the
[temporary support exception](README.md). The [access-control proposal](../access-control.md)
owns intended contract guarantees; the [vision](../../vision.md) owns requirement selection.

[ACP](https://solidproject.org/TR/acp) is a possible representation and evaluator, not a sempods
requirement. The [fixture guide](../../guides/acp-fixtures.md) explains the algorithm boundary,
mode expansion, extensions, supplied owner facts and composition used by the examples. Those
fixtures do not demonstrate that this design covers every deployment or is implemented.

## Decision and profile

```text
authorize(target, mode, accessContext) -> granted | denied
```

In this design a context policy controls an area. An optional resource policy further restricts
access per subject. This is an internal composition choice; no `resource` module is specified.
The ACP access context carries trusted agent, client, issuer, target and server-derived facts.
An implementation could inject an implicit owner policy at evaluation time without storing owner
grants, preserving [`SPS-GRANT-011`](../../../spec/core/grants.md#SPS-GRANT-011).

The proposed positive profile excludes `acp:deny`, `acp:noneOf` and resource member inheritance.
Modes are expanded when policy is ingested. Matchers carry either native ACP attributes or an
extension, with conjunction across separate matchers. These restrictions simplify policy writing;
a full ACP evaluator still honors negative constructs in a supplied policy. The native store's
[accepted write shape](authorization-state.md#what-a-write-accepts) is a separate question.

For fixed membership facts, adding satisfied allow policies only adds modes. This does not make
all authorization monotone: membership and delegation can be revoked, and a second decision can
narrow the result. It also does not make reverse enumeration automatic. Finding accessible targets
still needs membership, conjunction, client and issuer checks, supplied owner/creator facts and
all applicable decision intersections.

### Proposed mode mapping

| Permission | ACP policy modes |
|---|---|
| Context read | `acl:Read` |
| Context write | `acl:Read`, `acl:Write` |
| Resource policy management | `acl:Read`, `acl:Write`, `acl:Control` |
| Context manage | `acl:Read`, `acl:Write`, a term still to be selected |

The read/write implication comes from
[`SPS-GRANT-009`](../../../spec/core/grants.md#SPS-GRANT-009); its read-oracle rationale is in
[`SPS-GRANT-010`](../../../spec/core/grants.md#SPS-GRANT-010). The proposed resource-management
bundle is a design choice, not a resource permission defined by that chapter. It gives up separate
policy-read authority; management can change a policy to grant content access.

Context `manage` also covers descendant paths, creation and deletion
([`SPS-GRANT-007`](../../../spec/core/grants.md#SPS-GRANT-007),
[`SPS-GRANT-033`](../../../spec/core/grants.md#SPS-GRANT-033),
[`SPS-CTX-019`](../../../spec/modules/context-management.md#SPS-CTX-019)). A policy-management
mode alone does not express that bundle. No new vocabulary IRI is allocated by this draft.

## Enforcement responsibilities

These are obligations a realization of this design would need to satisfy, not verified safeguards:

| Design property | Needed enforcement |
|---|---|
| Ordinary data cannot rewrite policy | Separate authority inputs from the data paths; see the audience exception below |
| Independent restrictions only narrow | Intersect decisions on every applicable operation |
| Positive native policy shape | Validate writes rather than trusting a policy editor |
| Expanded sempods modes | Enforce closure at ingestion; `Write` alone would misrepresent a read-capable authority |
| No unsupported member inheritance | Control both accepted policy constructs and server-supplied ancestor facts |
| Shared policies cannot widen a target manager's authority | Give their editing a separate authorization boundary or resolve the open alternative below |

A full evaluator honoring an unexpected deny narrows the grant. A positive row store cannot simply
ignore it. Likewise, ancestor policies are inert only while no ancestor facts are supplied; choosing
inheritance changes that assumption and requires corresponding enforcement.

## Principal sets

Groups, audiences, tenant membership and roles can be represented by a trusted principal-set
matcher. It names a set IRI; a resolver checks the verified agent's membership. A tenant-wide or
administrator set uses the same mechanism, without a role bypass around policy.

Clients would choose advertised relations and set IRIs, not submit executable queries or arbitrary
expressions. Membership comes from a protected authority or the explicitly declared exception below.
A policy can use several allow policies for alternatives, `acp:allOf` for conjunction and
`acp:anyOf` for alternatives between matchers. The space/document and group examples are in
[40](../../../examples/40-groups-and-shared-policy.md).

Live membership avoids rewriting every referring policy on a membership change. Resolver failure
would deny the dependent access. Freshness, availability and any advertised vocabulary remain open;
this draft chooses neither an external service nor a graph store. Defining a set by difference moves
negation into the resolver; it does not remove it from the authorization system.

## Policy location and control plane

The proposed lookup key is **decision kind and target IRI**. A context ACR controls an area; a
resource ACR controls a subject, independently of where its statements are stored. These can use the
same IRI, as [35](../../../examples/35-subject-is-a-context.md) illustrates. Keying only by IRI
would conflate authority over a context with authority over statements about it.

Target-indexed resource policies also avoid duplicating a subject's policy across data contexts,
making discovery depend on data visibility, or deleting policy when one of several contexts holding
its statements is removed. This is a design rationale, not a specified ACP storage contract.

An implementation could store ACRs as separate internal graphs. In this design they are outside
context discovery, selectors and ordinary CRUD/SPARQL. Data using ACP predicates or naming a
control-plane IRI remains ordinary data and is never included in the policy inputs. Before adoption,
the scope of “stored in a pod” in
[`SPS-CTX-001`](../../../spec/core/contexts.md#SPS-CTX-001) needs review alongside the existing
control-plane distinction in
[`SPS-CTX-025`](../../../spec/core/contexts.md#SPS-CTX-025) and
[`SPS-CTX-026`](../../../spec/core/contexts.md#SPS-CTX-026); this draft cannot silently narrow it.

A possible ACP management surface would link the ACR from an authorized target response. For a
foreign, `did:` or `urn:` subject with no LOD address, the system resource response could carry it.
Read/edit authorization, discovery and the OAuth ceiling would need an explicit contract before
clients could rely on them. The current specification does not provide this ACP surface.

### Shared policy editing

A policy referenced through `acp:apply` can affect several targets. Letting a manager of just one
target edit it would grant authority over the others. Requiring management of every referring target
can disclose hidden references through a refused edit; pretending the edit succeeded is also wrong.
The design therefore favors a separate authorization boundary on the shared policy resource.
Its bootstrap and any alternative remain open. An edit's outcome must not reveal whether a hidden
target references that policy. The fixture's common-manager setup is an assumption, not a safeguard
proved by the test runner.

### Audiences from ordinary data

[45](../../../examples/45-audiences-from-pod-data.md) explores a declared ordinary context as a
membership authority. The declaration itself would be protected control-plane state; its source
would supply membership only, never ACP policies. This is an explicit exception to separating all
authorization facts from ordinary writable data, and whether to permit it remains open.

The proposed safety condition covers **every agent/client pair whose writes are still believed**:
they held at least `manage` on everything those writes now authorize, through authority independent
of the writes themselves. Checking only the person lets a delegated sync exceed its ceiling.
Checking only today's writers misses entries left behind after revocation and targets that later
start trusting those entries. Self-membership cannot justify the write that created it.

A realization would need trusted control-plane writers or sufficiently authorized delegated writers,
plus revalidation when authority is revoked or a new target references the audience. Neither the
fixtures nor this draft implement those checks. Refusing the exception avoids that machinery;
keeping it needs an explicit, enforceable design rather than deployment advice.

## Remaining choices

The [disposition issue](https://github.com/sempods/sempods-spec/issues/64) owns implementation
handoff; contract decisions and adoption remain with
[#68](https://github.com/sempods/sempods-spec/issues/68). Open design choices include:

- **Context manage coverage.** ACP member access control could express ancestor-path policies,
  requiring a bounded ancestor walk and a revised exclusion limited to resources. Alternatively,
  materialize policies into every registered descendant and atomically propagate them when new
  contexts are created. A descendant ACR alone is incomplete until coverage is supplied by one of
  these mechanisms. The fixture suite does not test this choice.
- **Resource inheritance.** No resource-containment relation is specified. Introducing inheritance
  needs a relation, resource kinds, propagated modes and a depth rule; it cannot be inferred from a
  subject's data context. ACP's ancestor gathering is the standards reference for the mechanism.
- **Creation bootstrap.** Compare atomic caller-supplied policy with an advertised template.
  A generic RDF subject has no specified creator fact; an application with document semantics may
  supply one or name the creator directly. [60](../../../examples/60-creator.md) illustrates both.
- **Shared-policy bootstrap, mode and principal-set IRIs, and the audience exception** described above.

Solid protocol interoperability remains separate: expressing policies in ACP does not adopt Solid
resource semantics, containment, discovery or HTTP behavior. Query rewriting also remains a
proposal; the current [`SPS-SPARQL-009`](../../../spec/core/sparql.md#SPS-SPARQL-009) prohibits using
it to enforce the sandbox. The [access-control proposal](../access-control.md#queries-and-retrieval)
records the outcome-equivalence questions a normative change would have to settle.
