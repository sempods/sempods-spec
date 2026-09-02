# A client with no person behind it

A log shipper writes into a pod every few minutes. Nobody authorised it in a browser; an operator
registered it out of band, and its grants were fixed at that moment
([`SPS-AUTH-012`](../spec/core/auth.md#SPS-AUTH-012),
[`SPS-AUTH-013`](../spec/core/auth.md#SPS-AUTH-013)).

That makes it the one caller the delegation formula does not describe. There is no person, the
subject **is** the client ([`SPS-AUTH-017`](../spec/core/auth.md#SPS-AUTH-017)), and there is no
ceiling to intersect because nobody delegated anything.

## What it was registered with

Not a policy. No access control resource carries this, and none could: it is registration state, and
it takes the place of both the ceiling and the context decision.

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
  acp:owner  <https://acme.example/profile#me>
] .

[
  acp:target <https://acme.example/logs/2026-09-02> ;
  acp:agent  <did:web:shipper.example> ;
  acp:client <did:web:shipper.example> ;
  acp:owner  <https://acme.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write .
```

**The context policy never mentions the shipper and it writes anyway.** That is not the policy being
bypassed — it is the registered grant standing where a context decision would stand for a person.
Olga is admitted by a policy; the shipper is admitted by its registration, and the two are different
routes to the same place.

The resource decision still applies, and is the half that can still refuse. Take the shipper out of
`#entry` and this case goes empty however generously it was registered: what registration replaces is
the *context* decision, not every decision.

## Why this needs saying at all

Read the effective-modes formula with a service token in mind and it asks for a ceiling that does not
exist. Following it literally denies every service client — nobody delegated to them — or invents a
per-principal delegation the contract does not define. Neither is what a pod should do, and neither
is visible until somebody writes the request down.

Which is what this file is: the branch, spelled out, with a runner that would otherwise have answered
it with the formula for a person.
