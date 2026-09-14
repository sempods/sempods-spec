# Module: OIDC bridge

**Optional.** Everything in this chapter binds only an implementation that advertises the module
IRI `https://schema.sempods.org/module/oidc` at the conformance endpoint
([`SPS-CORE-005`](../core/index.md#SPS-CORE-005)). An implementation that identifies people some
other way is conformant without it.

**Status: this text decides, and can still change.** See [`../../GOVERNANCE.md`](../../GOVERNANCE.md).

Profiles: OpenID Connect Core 1.0, OIDC Discovery 1.0, RFC 7636 (PKCE). What a pod stores about a
person regardless of this module is [`../core/auth.md`](../core/auth.md) §9.

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
**`SPS-OIDC-005`** — The assertion MAY carry the equivalent identity URIs known for the person. A
relying party MUST apply them only where a grant or ownership is decided
([`SPS-AUTH-052`](../core/auth.md#SPS-AUTH-052)).

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
