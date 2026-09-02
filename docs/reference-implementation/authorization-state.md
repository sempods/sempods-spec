# Holding authorization state, and answering with it

The contract says what a pod decides, never how ([`../vision.md`](../vision.md)). This is the *how*
for one implementation: where authorization state lives, what it costs to answer a request from it,
and which of those choices are forced rather than preferred.

Nothing here has a requirement ID. A pod that reaches the same answers by other means is exactly as
conformant, and several of the shapes below exist because an obvious alternative fails in a direction
worth naming.

## Storage is native, ACP is a projection

Grants are held in the implementation's own structures — rows keyed by context, holder and mode,
indexed the way the read path wants them. They are **not** stored as RDF policies.

[`acp-profile.md`](acp-profile.md) makes the case that every deployment this implementation serves is
expressible in one small ACP profile, and the examples run that claim against an engine that has
never heard of sempods. Expressible is not the same as *stored*: the permission check sits on the hot
path of every authenticated request ([`SPS-GRANT-002`](../../spec/core/grants.md#SPS-GRANT-002)
resolves from durable storage every time), and parsing a policy graph per request is the wrong shape
for a join.

So ACP appears at one boundary only — where authorization state is handed to a client — and the
boundary is rare enough to afford it.

## What a read renders

A grants view of a context is assembled at read time from four sources, and only the first is stored
as a grant:

| Source | Rendered as |
|---|---|
| a person's grant | `acp:agent` with their WebID |
| an application delegation | `acp:allOf` over `acp:agent` and `acp:client` |
| a service client | the same conjunction, plus the service marker |
| the context's `public` flag | `acp:agent acp:PublicAgent` |

**The view is effective, never stored.** Whatever inheritance the store uses internally is resolved
before the response leaves, because a client that had to gather policies from ancestors would be
running ACP's algorithm — which is the thing the contract is built to keep out of clients.

**A delegation is rendered, never persisted as a policy.** It is derivable by definition —
`requested ∩ effectively held` ([`SPS-GRANT-013`](../../spec/core/grants.md#SPS-GRANT-013)) — and
persisting a derived value means keeping it in step. That maintenance is a cache whose failure mode
is *more* access: stale means an application still holding what the person no longer has, which
[`SPS-GRANT-029`](../../spec/core/grants.md#SPS-GRANT-029) forbids. Computed per response, it cannot
drift.

The deeper reason the intersection cannot become a policy: a ceiling **subtracts**, and ACP's algebra
only adds. A delegation written as a policy beside the others is an independent source of access
rather than a bound on one, so it holds only as long as a sweep keeps up
([`SPS-GRANT-015`](../../spec/core/grants.md#SPS-GRANT-015),
[`SPS-GRANT-016`](../../spec/core/grants.md#SPS-GRANT-016)) — on the revocation path, where
[`SPS-GRANT-003`](../../spec/core/grants.md#SPS-GRANT-003) wants the effect by the next request. An
invariant that holds structurally becomes one that holds if maintenance succeeds.

**An audience renders as a name or as its members, depending on who is reading.** Expanding it for a
caller who may not read the source hands them the identity source through the grants view. Where they
may, expanding is the more useful answer and the portable one.

## What a write accepts

The boundary runs along direction rather than along syntax:

- **accepted** — what maps onto the native structures: one policy, one matcher, one attribute, plus
  `acp:allOf` for conjunction. That is the whole shape the read path emits, so it is the whole shape
  a round trip needs;
- **refused**, with `400` and the supported shape named — everything else, `acp:deny` and
  `acp:noneOf` included.

Refusing beats a general fallback. An opaque policy stored for later evaluation puts a full ACP
engine back on the hot path for every context carrying one, which is what the native structures exist
to avoid.

Refusing the negative constructs needs its own reason, because
[`acp-profile.md`](acp-profile.md) says honouring an unexpected `acp:deny` fails safe while ignoring
it does not — and that is true of an **engine**, which sees the whole policy set and can subtract
from it. A store holding positive rows has nothing to subtract from: a `deny` is equivalent to an
absent row only when no other policy grants the same holder, and deciding *that* is the evaluation
this design does not do. So a restriction accepted here would be a restriction dropped, which is the
failure the fail-safe argument warns about, reached from the other end. The two rules are not in
conflict; they answer different questions, and conflating what an engine may honour with what a store
may accept is what makes them look alike.

Two things a write does regardless of which branch it takes.

**Modes are closed at ingest.** `acl:Write` alone is stored as read and write, because
[`SPS-GRANT-009`](../../spec/core/grants.md#SPS-GRANT-009) implies one from the other and ACP has no
such rule. Left unexpanded, the pod believes it granted less than it did — a write path is a read
oracle, which is why [`SPS-GRANT-010`](../../spec/core/grants.md#SPS-GRANT-010) refuses to pretend
otherwise.

**Rendered entries are not writable.** Delegations, service clients and the `public` flag appear in
the view and are owned elsewhere; a write naming one is refused rather than absorbed. Addressing the
surface per holder rather than per document is what makes this a check instead of a hazard — there is
no whole-document round trip for a client to send back.

A public policy is the one case where a write reaches through: `acp:PublicAgent` with `acl:Read` sets
the context's flag rather than creating a second record of the same fact. `acp:PublicAgent` with
`acl:Write` is refused outright — resolution is keyed on the pair of verified client and verified
subject, and an anonymous writer presents neither.

## Service clients are grant rows with an origin

A service client's grants are fixed at registration and consist only of per-context grants
([`SPS-AUTH-013`](../../spec/core/auth.md#SPS-AUTH-013)). Where they are *kept* is not specified, and
keeping them in the ordinary grant store is what makes them visible: a separate registry is a second
place access comes from, and the grants view cannot show what it does not hold.

Which forces one thing. Registration is host-operator authority and must not be reachable from a
pod-scoped token ([`SPS-AUTH-012`](../../spec/core/auth.md#SPS-AUTH-012)) — so a row written by the
operator carries an origin marker, and the pod-scoped surface refuses to modify it. Without the
marker, sharing a store with the manageable grants hands every `manage` holder the registration
authority the requirement withholds.

Not two stores kept in step. Two stores that must agree drift, and here drift is an access
difference.

## Computing a request's sandbox

Before a query runs, the readable set has to exist. The two halves behave oppositely, and separating
them is what makes the whole thing affordable:

```text
policy evaluation   →  symbolic, cacheable    "A, B, and C if in audience X"
audience membership →  one ASK per audience, live, never cached
```

Membership is never cached because removing somebody from an audience is a revocation in effect, and
[`SPS-GRANT-003`](../../spec/core/grants.md#SPS-GRANT-003) wants it effective on the next request. At
one ASK per *distinct* audience named in the surviving policies, that is affordable — the count
follows the number of audiences a deployment declared, not the number of people in them. The
deduplication is a condition rather than an optimisation: without it, a materialised policy referring
to one audience from a thousand descendants asks the same question a thousand times.

The part that scales with data is the part that caches, which leaves the open question in
[`acp-profile.md`](acp-profile.md) — inheritance against materialisation — as the one that decides
whether this is affordable at all. It is worth adding what the profile's framing does not say: seen
from the query side rather than from CRUD, the two are not close. Inheritance lets the sandbox be a
set of **path prefixes**, computed once per distinct policy and independent of how many contexts
exist; materialisation leaves every access control resource independent, so the sandbox is an
enumeration or a reverse index somebody maintains.

## Audiences: one declaration, live resolution, revalidation

An audience is not created per group. The deployment names one identity source — a context, the
predicate holding the key, the predicate holding the WebID — and audiences then exist for every value
that appears. Tagging somebody in the address book they already use is the whole act.

Resolution is the ASK above, run with the **server's** authority rather than the caller's. The
requester learns the answer as access or as nothing; the graph the guard consults and the graphs a
client's patterns reach stay disjoint sets.

Declaring an ordinary context an authority is the stated exception to the topological guarantee, and
[`examples/45-audiences-from-pod-data.md`](../../examples/45-audiences-from-pod-data.md) carries the
condition that bounds it. Two obligations follow from that condition being about *writes still
believed* rather than writers who can still write:

- on every revocation of a delegation, revalidate what its remaining writes in the source still
  decide; and,
- on every new reference to an audience, check the condition again rather than once at declaration.

The declaration itself is control-plane state and is not a client act. A route would have to check a
property of the source's past at the moment of the call, which is not a check that exists.

## What consent has to say

An application holding `manage` on a context may make it public in one call. The bound is not in the
protocol — it is that the person granted `#manage` deliberately.

So the consent screen states what `manage` carries, rather than showing a context name with a word
beside it. This is the one place in this document where the cost of a decision lands on an interface
rather than on a store.
