# Module: OIDC bridge

**Optional.** Everything in this chapter binds only an implementation that advertises the module
IRI `https://schema.sempods.org/module/oidc` at the conformance endpoint
([`SPS-CORE-005`](../core/index.md#SPS-CORE-005)). An implementation that identifies people some
other way is conformant without it.

**Status: this text decides, and can still change.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: OpenID Connect Core 1.0, OIDC Discovery 1.0, RFC 7636 (PKCE). What a pod stores about a
person regardless of this module is [`../core/auth.md`](../core/auth.md) §9.

The equivalent-identity claim uses the additional-claim mechanism in
[OpenID Connect Core 1.0, errata set 2, §5.1.2](https://openid.net/specs/openid-connect-core-1_0.html#AdditionalClaims)
and the collision-resistant claim naming of
[RFC 7519 §4.2](https://www.rfc-editor.org/rfc/rfc7519.html#section-4.2).

## 1. What the module adds

A pod knows people as WebID URIs whether or not this module is present. What the module adds is a
way for a person to *arrive* — an identity service that turns a login at an upstream provider into
an identity assertion a pod can verify.

<a id="SPS-OIDC-001"></a>
**`SPS-OIDC-001`** — Without this module, an implementation MUST still be able to address a person by
a deterministic identity URI derived from an email address
([`SPS-AUTH-050`](../core/auth.md#SPS-AUTH-050)). The module MUST NOT be a prerequisite for holding
grants.

That layering is the point. A pod with no identity service can still name people and store their
grants; connecting one later makes those same identifiers dereferenceable without rewriting a single
grant.

## 2. The identity assertion

<a id="SPS-OIDC-002"></a>
**`SPS-OIDC-002`** — The identity assertion MUST be an OpenID Connect ID Token, signed, with the
issuer's keys published at a JWKS endpoint.

<a id="SPS-OIDC-003"></a>
**`SPS-OIDC-003`** — `sub` MUST be the person's canonical WebID URI.

<a id="SPS-OIDC-004"></a>
**`SPS-OIDC-004`** — `aud` MUST name the relying party the assertion was issued to. A pod MUST
reject an assertion whose audience is not itself.

An assertion without an audience is valid at every pod that trusts the issuer, which is exactly what
makes it worth stealing. This requirement exists because that token shape was shipped once and had
to be withdrawn.

<a id="SPS-OIDC-005"></a>
**`SPS-OIDC-005`** — An issuer MAY carry the person's equivalent identities in the ID Token claim
`https://schema.sempods.org/claims/equivalent-identities`, whose value MUST be a JSON array of WebID
URI strings consistent with [`SPS-AUTH-049`](../core/auth.md#SPS-AUTH-049).
Each entry MUST identify the same person as `sub` using an HTTP or HTTPS URI matching the `URI`
syntax of [RFC 3986 §3](https://www.rfc-editor.org/rfc/rfc3986.html#section-3), with a fragment permitted.

<a id="SPS-OIDC-016"></a>
**`SPS-OIDC-016`** — A relying party MUST reject the identity assertion if the equivalent-identity
claim is present with a value other than the array of WebID URI strings defined by
[`SPS-OIDC-005`](#SPS-OIDC-005), including `null` or an array containing any invalid entry.

<a id="SPS-OIDC-017"></a>
**`SPS-OIDC-017`** — A relying party MUST interpret a valid equivalent-identity claim as an unordered
set of identities equivalent to `sub`, with omission or an empty array asserting no additional
identities in this token.

<a id="SPS-OIDC-018"></a>
**`SPS-OIDC-018`** — A relying party MUST apply the claimed equivalent identities only from an issuer
trusted to assert equivalence for this subject, and only where a grant or ownership is decided
([`SPS-AUTH-052`](../core/auth.md#SPS-AUTH-052)).

WebIDs with or without a fragment fit; a `urn:` identity does not. Duplicate entries or an entry
equal to `sub` add no identity. An omitted or empty claim says nothing about previously established
equivalences; it is not a revocation signal.
Token validation under [`SPS-OIDC-006`](#SPS-OIDC-006) still applies. Trust in an issuer for login
alone does not establish its authority to assert another identity's equivalence.
The issuer's validated assertion supplies the equivalence; this claim adds no profile-fetch step.

For example, this excerpt asserts two equivalent identities for the person named by `sub`:

```json
{
  "sub": "https://id.example/alice#me",
  "https://schema.sempods.org/claims/equivalent-identities": [
    "https://other.example/alice#me",
    "https://third.example/people/alice"
  ]
}
```

This is an ID Token excerpt, not a browser callback payload. A scalar string, `[null]`,
`["/alice"]`, or `["urn:example:alice"]` fails [`SPS-OIDC-016`](#SPS-OIDC-016). The claim name is a JWT
identifier, not a new RDF property. The registered `also_known_as` claim describes a human pseudonym,
not identity equivalence
([informative reference](https://openid.net/specs/openid-connect-4-ida-claims-1_0.html#Claims)); it
does not substitute for this claim.

<a id="SPS-OIDC-006"></a>
**`SPS-OIDC-006`** — A relying party MUST validate issuer, audience, nonce, expiry and signature
together against the issuer's published keys. Validating a subset is not validation.

## 3. How a pod obtains one

<a id="SPS-OIDC-007"></a>
**`SPS-OIDC-007`** — A pod MUST act as an ordinary OpenID Connect relying party: discover the issuer
through its discovery document, send the browser to the issuer's authorization endpoint with PKCE, a
`state` and a `nonce`, and fetch the assertion over a back channel.

<a id="SPS-OIDC-008"></a>
**`SPS-OIDC-008`** — The PKCE verifier MUST NOT travel through the browser.

<a id="SPS-OIDC-009"></a>
**`SPS-OIDC-009`** — An identity assertion MUST NOT be delivered to a redirect address, in a query
parameter, in a fragment, or in any other browser-visible form. The redirect carries a single-use
code, and the assertion is fetched with it.

The alternative was shipped and removed: a redirect that appended the assertion to a caller-supplied
return address, accepted from anyone, let any site collect a visitor's identity by asking for it.

<a id="SPS-OIDC-010"></a>
**`SPS-OIDC-010`** — A pod MUST identify itself to the issuer as `did:web:` its own host, and MUST
NOT be required to register. The issuer MUST permit a redirect address only on the origin that
identifier names.

That origin restriction is what stands in for a client secret. It is the same rule as
[`SPS-AUTH-004`](../core/auth.md#SPS-AUTH-004), applied by the issuer rather than by the pod.

<a id="SPS-OIDC-011"></a>
**`SPS-OIDC-011`** — The request the person was making MUST be parked on the server under the
`state` and resumed at the callback. It MUST NOT be carried through the browser.

<a id="SPS-OIDC-014"></a>
**`SPS-OIDC-014`** — A pod providing this module MUST serve a callback route under its own
control-plane prefix, and it is the **only** HTTP surface the module adds to a pod. Everything else
this chapter specifies happens at the identity service.

<a id="SPS-OIDC-015"></a>
**`SPS-OIDC-015`** — The callback MUST reject a `state` it did not park, and MUST consume each one
exactly once.

## 4. Federation

<a id="SPS-OIDC-012"></a>
**`SPS-OIDC-012`** — Federation between identity services, where offered, MUST be expressed as
`owl:sameAs` links between WebID documents. An implementation MUST NOT require a central registry.

<a id="SPS-OIDC-013"></a>
**`SPS-OIDC-013`** — Federation MUST be opt-in. An implementation MUST NOT treat an inbound
`owl:sameAs` assertion from an unconfigured issuer as establishing identity.

Following an arbitrary `owl:sameAs` would let anyone who can publish RDF claim to be anyone.

## 5. Not defined here

Which upstream providers an identity service integrates, how it derives a WebID URI from a provider
subject, how it merges two identities that turn out to be the same person, and how it stores any of
it. Those are an identity service's own design, and two implementations of this module may differ on
every one of them while remaining interchangeable to a pod.
