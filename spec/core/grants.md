# Grants

What a caller may do with a context, and how an implementation decides it. The model is
deliberately small: durable per-context policy, set-intersection delegation, and enforcement on the
server.

**Status: descriptive.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: RFC 6749 (for what a *scope* is, and is not). Error codes are [`index.md`](index.md) §5.
Contexts are [`contexts.md`](contexts.md).

## 1. Grant and scope are different things

Conflating them is the mistake this chapter exists to prevent, and it is an easy one — both are
strings, and both say something about permission.

| | Travels in the access token | Example |
|---|---|---|
| **Grant** | no | `<context-iri>#read`, `#write`, `#manage` |
| **Scope** (RFC 6749) | yes | `public-read`, `openid`, `offline_access` |

<a id="SPS-GRANT-001"></a>
**`SPS-GRANT-001`** — A **grant** is durable server-side policy on one context. An implementation
MUST NOT place a grant inside an access token, and MUST NOT treat a token's contents as the
authorization decision for a context.

<a id="SPS-GRANT-002"></a>
**`SPS-GRANT-002`** — An implementation MUST resolve a request's grants from durable storage, keyed
by the requester's verified identity, on every request.

<a id="SPS-GRANT-003"></a>
**`SPS-GRANT-003`** — A grant that is revoked MUST take effect on the caller's next request. An
implementation MUST NOT let an already-issued access token retain access for the remainder of its
lifetime.

The reason these are requirements rather than an implementation note: a context grant is
*named-graph visibility policy*, not a capability. A capability scope tells a client which API to
call and shapes its behaviour. Here the data API is uniform — the same requests go to the same
routes whatever the caller holds, and the server filters what comes back. Row-level security is the
right analogy, not an OAuth scope, and policy in a client-facing token was a category error whose
visible symptom was tokens that grew with the pod.

The cost is stated rather than hidden: the grant store is on the hot path of every authenticated
request, so the token is not self-contained. That is acceptable *here* because the authorization
server and the resource server are the same pod, and it is a trade an implementation splitting them
would have to reconsider.

## 2. Grammar

```
<context-iri>#read       read the context
<context-iri>#write      write to the context
<context-iri>#manage     manage this context root and its slash-delimited descendants
```

<a id="SPS-GRANT-004"></a>
**`SPS-GRANT-004`** — The separator MUST be the **last** `#` in the grant string.

<a id="SPS-GRANT-005"></a>
**`SPS-GRANT-005`** — The left side MUST be a canonical context IRI inside the pod's base URL. An
implementation MUST reject a grant naming an IRI outside it, and MUST reject the pod base URL
itself.

A grant on the pod root would match every context under it under any prefix rule, which is exactly
the wildcard the next requirement refuses.

<a id="SPS-GRANT-006"></a>
**`SPS-GRANT-006`** — The right side MUST be exactly one of `read`, `write` or `manage`. An
implementation MUST reject any other permission, and MUST NOT interpret a wildcard.

## 3. `manage` is slash-delimited, not a string prefix

<a id="SPS-GRANT-007"></a>
**`SPS-GRANT-007`** — Given `R#manage`, an implementation MUST authorize a context `C` if and only
if `C` equals `R`, or `C` begins with `R` followed by `/`. An implementation MUST NOT authorize a
context that merely shares a string prefix with `R`.

`tasks#manage` reaches `tasks` and `tasks/inbox`. It MUST NOT reach `tasks-private`.

This is the one place the model deviates from what a naive implementation would write, and it is
load-bearing for context-tree isolation: a raw `startsWith` hands an app every sibling whose name
begins with the same letters. It is worth implementing once, in one place, and calling it from every
site that asks the question — the read path, the write path and context management all have to give
the same answer.

<a id="SPS-GRANT-008"></a>
**`SPS-GRANT-008`** — A `#manage` grant MUST expand only over contexts that are **registered**. An
implementation MUST NOT treat it as authority over a context that does not exist.

## 4. What implies what

<a id="SPS-GRANT-009"></a>
**`SPS-GRANT-009`** — `#write` MUST imply `#read`, and `#manage` MUST imply both `#write` and
`#read`, on the same context.

<a id="SPS-GRANT-010"></a>
**`SPS-GRANT-010`** — A client MUST NOT request `#read` alongside `#write` for the same context, and
an implementation MUST NOT require it.

The second half matters for anyone reading a grant set: there is no such thing as a write-only
context here. An implementation that assumes one will build a read path that hides data its own
write path can reach.

## 5. Who holds what

<a id="SPS-GRANT-011"></a>
**`SPS-GRANT-011`** — The pod owner MUST hold `read`, `write` and `manage` on every registered
context of that pod, implicitly. An implementation MUST NOT require the owner's grants to be stored
or granted.

<a id="SPS-GRANT-012"></a>
**`SPS-GRANT-012`** — Any other person's grants MUST be explicit, stored per pod and per identity.

<a id="SPS-GRANT-013"></a>
**`SPS-GRANT-013`** — What an application receives MUST be the intersection of what it requested
with what the authorizing person **effectively holds**:

```
granted = requested ∩ person's effective permissions
```

An implementation MUST NOT grant an application more than the person effectively holds, and MUST NOT
require the application to be "installed" first, or the person to be the owner.

<a id="SPS-GRANT-028"></a>
**`SPS-GRANT-028`** — "Effectively holds" MUST be the person's grants **after** expanding
`#manage` roots over the registered contexts they cover ([`SPS-GRANT-007`](#SPS-GRANT-007)) and
after applying the implications of [`SPS-GRANT-009`](#SPS-GRANT-009). An implementation MUST NOT
compute the intersection over the stored grant strings.

The distinction is the difference between working and not. A person holding `R#manage` who is asked
for `R/sub#write` does hold that authority — but the two strings are different, so a literal
intersection is empty and the flow answers `consent_required` for an ordinary descendant. The
expansion is not an optimisation; it is what the earlier requirements already promised.

<a id="SPS-GRANT-014"></a>
**`SPS-GRANT-014`** — Where that intersection is empty and no public context is available, the
authorization flow MUST fail as `consent_required`, which is recoverable. An implementation MUST NOT
answer `access_denied`, which is reserved for a hard signal such as an invalid identity token or an
explicit refusal.

The difference is what a client does next. `consent_required` says "ask again, differently";
`access_denied` says "stop". Returning the second for an ordinary empty intersection strands a
client that had a perfectly good next move.

## 6. Revocation

An intersection computed at consent time is a snapshot, and a person who later narrows their own
grants would otherwise leave an application holding access they no longer have.

<a id="SPS-GRANT-015"></a>
**`SPS-GRANT-015`** — When a person's grants are narrowed or removed, an implementation MUST
recompute what they still hold and remove every application delegation no longer covered by it.

<a id="SPS-GRANT-016"></a>
**`SPS-GRANT-016`** — That removal MUST be a recomputation, not a string match on the revoked grant.

Because `<root>#manage` expands into its registered descendants, revoking the root has to sweep
derived delegations like `<root>/child#write` — whose text matches nothing in the grant that was
removed. A string match silently leaves them behind, and they keep working.

<a id="SPS-GRANT-017"></a>
**`SPS-GRANT-017`** — Deleting a context MUST run the same recomputation, for the same reason.

<a id="SPS-GRANT-018"></a>
**`SPS-GRANT-018`** — Consent MUST persist its result first and re-check second, and MUST answer
`consent_required` if nothing survives the re-check.

Time passes between intersecting a request and storing the result. A revocation landing inside that
window is invisible to both sides otherwise — the intersection is already stale, and the
revocation's sweep runs before the delegation exists to be swept. Both sides writing first and
checking second is what makes them unable to miss each other.

<a id="SPS-GRANT-019"></a>
**`SPS-GRANT-019`** — Widening a person's grants MUST NOT widen an application retroactively. An
application receives more only through a fresh consent.

The asymmetry is deliberate: narrowing propagates, widening does not. A person who regains access
they had revoked should not silently re-arm every application that once asked for it.

## 7. `public-read`

<a id="SPS-GRANT-020"></a>
**`SPS-GRANT-020`** — `public-read` is a **scope**, not a grant. It MUST travel in the access token,
and it MUST be additive: where present, the pod's currently public contexts are unioned into the
caller's readable set on top of the grants resolved from storage.

<a id="SPS-GRANT-021"></a>
**`SPS-GRANT-021`** — The set of public contexts MUST be expanded at access time, not frozen at
consent time.

<a id="SPS-GRANT-022"></a>
**`SPS-GRANT-022`** — Revoking a person's context grants MUST NOT remove `public-read`. It is not a
grant on a context, and removing it would end a session over an unrelated narrowing.

## 8. Enforcement

<a id="SPS-GRANT-023"></a>
**`SPS-GRANT-023`** — An implementation MUST enforce grants on the server. It MUST NOT rely on a
client restricting its own requests, and MUST NOT trust a client-supplied statement about which
contexts a request should touch.

<a id="SPS-GRANT-024"></a>
**`SPS-GRANT-024`** — A read MUST return statements only from contexts the caller may read.

<a id="SPS-GRANT-025"></a>
**`SPS-GRANT-025`** — A write MUST name its target context explicitly and MUST land only there. An
implementation MUST NOT provide an implicit or default write context.

<a id="SPS-GRANT-026"></a>
**`SPS-GRANT-026`** — The statements parsed from a write request MUST concern the target resource
only. An implementation MUST reject a request carrying statements about other subjects alongside it.

<a id="SPS-GRANT-027"></a>
**`SPS-GRANT-027`** — A valid token whose scope is insufficient for an operation MUST produce `403`.
A missing or rejected token MUST produce `401`. An implementation MUST NOT conflate the two.
