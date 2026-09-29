# A client with no person behind it

Current service-client identity and grant requirements are cited below. Their ACP encoding
and combination with a proposed resource restriction are fixture assumptions, not a required policy
architecture or an implemented service. See the
[fixture assumptions](../docs/guides/acp-fixtures.md).

A log shipper writes into a pod every few minutes. It has read and write grants on the `logs`
context ([`SPS-AUTH-013`](../spec/core/auth.md#SPS-AUTH-013)). How it was registered and who assigned
those grants are implementation choices.

That makes it the one caller the delegation formula does not describe. There is no person, the
subject **is** the client ([`SPS-AUTH-017`](../spec/core/auth.md#SPS-AUTH-017)), and there is no
ceiling to intersect because nobody delegated anything.

## Its current grants

The fixture supplies one snapshot of the service's grants in a `registered` block. In this model,
it replaces both the delegated ceiling and the context policy decision. Grants can change;
each request uses the current set ([`SPS-GRANT-002`](../spec/core/grants.md#SPS-GRANT-002)).

```turtle registered
[
  <https://example.invalid/runner#client> <did:web:shipper.example> ;
  <https://example.invalid/runner#in>     <https://acme.example/_system/contexts/logs> ;
  <https://example.invalid/runner#grants> acl:Read, acl:Write
] .
```

## The context it writes into

An ordinary context policy, and one that does **not** name the shipper.

```turtle acr-context
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/_system/contexts/logs> ;
  acp:accessControl [ acp:apply <#operators> ]
] .

<#operators>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://acme.example/people/olga#me> ] .
```

## A log entry, and the decision that governs it

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/logs/2026-09-02> ;
  acp:accessControl [ acp:apply <#entry> ] ] .

<#entry>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write ;
  acp:anyOf [ a acp:Matcher ; acp:client <did:web:shipper.example> ] .
```

```turtle holds
<https://acme.example/logs/2026-09-02>
  <https://example.invalid/runner#inContext> <https://acme.example/_system/contexts/logs> .
```

```turtle decision
[
  acp:target <https://acme.example/_system/contexts/logs> ;
  acp:agent  <did:web:shipper.example> ;
  acp:client <did:web:shipper.example> ;
  <https://example.invalid/runner#serviceToken> true ;
  acp:owner  <https://acme.example/profile#me>
] .

[
  acp:target <https://acme.example/logs/2026-09-02> ;
  acp:agent  <did:web:shipper.example> ;
  acp:client <did:web:shipper.example> ;
  <https://example.invalid/runner#serviceToken> true ;
  acp:owner  <https://acme.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write .
```

**The shipper can write because it holds a write grant.** The context policy grants Olga access;
the supplied service grants give the shipper access.

The proposed resource restriction still applies. Remove the shipper from `#entry` and this fixture
grants it nothing, even while its context grant remains.

## Reading the result

The service acts as itself ([`SPS-AUTH-017`](../spec/core/auth.md#SPS-AUTH-017)). The runner therefore
uses its supplied grants in place of a person's delegation. This checks the fixture's access
decision, not a registration or consent flow.
