# A possible authorization-state implementation

Status: **Proposed implementation design; non-normative.** Disposition and intended recipient:
[#64](https://github.com/sempods/sempods-spec/issues/64), under the
[temporary support exception](README.md). This draft explores the storage and management side of
the [ACP design](acp-profile.md); it describes no verified current implementation or adopted API.

## Native storage and ACP projection

The candidate store holds grants as native rows keyed by context, holder and mode, with indexes
for request evaluation. ACP would be a projection at a management boundary rather than a policy
parsed on every data request. This is a performance/design choice, not a requirement inferred from
[`SPS-GRANT-002`](../../../spec/core/grants.md#SPS-GRANT-002).

## What a read renders

A proposed effective view combines several sources:

| Source | Possible projection |
|---|---|
| Person's grant | `acp:agent` naming the WebID |
| Application delegation | `acp:allOf` over agent and client |
| Service-client grant | Agent/client conjunction with an origin marker |
| Context public flag | `acp:agent acp:PublicAgent` |

Resolve inherited authority before rendering the view. A rendered delegation represents the current
intersection of requested and held authority
([`SPS-GRANT-013`](../../../spec/core/grants.md#SPS-GRANT-013)), not an independent allow policy
beside the person's policies. A stale stored expansion could retain access after revocation;
computing it at read time avoids that particular cache, but still needs correct concurrency and
revocation handling. The generic fixture ceiling only bounds modes; target scope remains open.

Render an audience as its name unless the viewer may read its membership source. Expanding members
for another viewer would expose the source through the policy view. Neither form requires ordinary
data clients to evaluate policy themselves.

## What a write accepts

A possible management surface accepts only structures representable by the native rows: individual
holder entries using a policy, matcher and attribute, or agent/client conjunction. Other shapes,
including `acp:deny` and `acp:noneOf`, would receive `400` with supported-shape information. This is
a candidate interface, not an adopted request schema or a demonstrated general ACP round trip.

A full ACP engine can honor a deny by evaluating the whole policy set. A store of positive rows
cannot represent it as an absent row when another policy still grants access. Accepting and dropping
that restriction would widen access. Rejecting it preserves the native-store boundary without a
fallback evaluator on the request path.

Close modes at ingestion: the current sempods write grant includes read
([`SPS-GRANT-009`](../../../spec/core/grants.md#SPS-GRANT-009)). ACP does not infer that closure.
The proposed positive shape and closure need validation even when policy comes from an owner.

Delegation and service-registration entries would be read-only projections owned by their respective
operations. Addressing individual holders avoids accepting a whole effective document as writable
policy. The public entry is an explicit exception: writing a `PublicAgent` entry allowing read would update the
context's public flag. Public write would be rejected. Its authorization and route remain proposed.

## Service-client origins

The current contract requires host-operator registration and fixed per-Context grants
([`SPS-AUTH-012`](../../../spec/core/auth.md#SPS-AUTH-012),
[`SPS-AUTH-013`](../../../spec/core/auth.md#SPS-AUTH-013)). A candidate store can keep those grants
alongside ordinary rows, with an origin marker that prevents a pod-scoped management surface from
changing operator-owned registration state. Separate stores are also possible; choosing shared rows
avoids a separate source to assemble for the proposed view. The origin marker is an implementation
choice, not part of the service-token contract.

## Computing a sandbox

One possible decomposition separates symbolic policy evaluation from live audience membership:

```text
policy evaluation   -> reusable expression   "A, B, and C if in audience X"
audience membership -> live lookup per distinct audience
```

A graph-backed implementation could use one ASK per distinct audience. Deduplicating repeated
references avoids asking the same membership question for every descendant. Live lookup avoids a
membership-cache invalidation problem; it does not itself prove freshness of an external authority,
transaction ordering or performance. Policy-expression caches also need invalidation when policy
changes. An implementation would have to measure and validate both paths.

The [manage-coverage choice](acp-profile.md#remaining-choices) affects sandbox construction:
inheritance can retain path prefixes; materialized descendant policies need enumeration or a reverse
index. Reverse lookup still has to evaluate conjunctions, membership and the other request facts.

Three enforcement strategies explain the tradeoff illustrated by the group scenario:

- Join both area and resource restrictions into query evaluation. Correct guards become the boundary
  protecting the whole tenant dataset.
- Restrict the dataset to readable areas before evaluating resource restrictions. This bounds a
  resource-guard defect to those areas but requires an accurate readable set and any cache's invalidation.
- Fetch that readable set from current authorization state before each query. This trades a cache for
  a lookup and still depends on complete policy evaluation.

These are proposed strategies under [outcome equivalence](../access-control.md#queries-and-retrieval),
not exceptions to the current query-rewrite prohibition. The fixture runner executes none of them.

## Audience resolution and revalidation

A possible declaration names an identity source, key predicate and WebID predicate. Audience values
then come from that source. Resolution uses server authority; client queries do not gain access to
the authority's graph. An ordinary context used as the source remains readable under its own data
policy and is subject to the [declared exception](acp-profile.md#audiences-from-ordinary-data).

The condition covers retained writes, so revoking a writer's delegation and adding a new audience
reference both require revalidation. A declaration alone cannot establish that condition over past
writes. No management route or implementation of that validation is supplied here.

## Consent presentation

In the proposed management design, `manage` permits making a context public. A consent interface
would need to communicate that authority clearly. This is a consequence to evaluate with the API
and delegation design, not a specification of a particular screen or a currently available call.
