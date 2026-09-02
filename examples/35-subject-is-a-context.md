# When a subject is a context

A pod holds `<{pod}/_system/contexts/spaces/eng> rdfs:label "Engineering"`. That is an ordinary
statement: [`SPS-CTX-026`](../spec/core/contexts.md#SPS-CTX-026) says a statement about a `_system`
IRI is data like any other, and [`SPS-CRUD-011`](../spec/core/lod-crud.md#SPS-CRUD-011) makes the
subject and the context that holds it independent on purpose.

With the resource module declared, that one IRI now carries **two decisions**: who may read *in* the
space, and who may read statements *about* it. They are unrelated questions and this file is where
that stops being a technicality.

## Why the lookup key is a pair

Policy is indexed by the target it controls. If the index were the IRI alone, the two access control
resources above would be one document — and a resource policy could then widen who reaches the
context, which inverts the rule that the finer decision only ever subtracts.

So the key is **which decision, and which IRI**. The blocks below say which by their kind, and the
runner keeps them apart the same way a pod has to.

The label is stored in the space it is about, which nothing derives and the fixture therefore says:

```turtle holds
<https://acme.example/_system/contexts/spaces/eng>
  <https://example.invalid/runner#inContext> <https://acme.example/_system/contexts/spaces/eng> .
```

## Who may read in the space

```turtle acr-context
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/_system/contexts/spaces/eng> ;
  acp:accessControl [ acp:apply <#members> ]
] .

<#members>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write ;
  acp:anyOf [ a acp:Matcher ;
              acp:agent <https://dana.example/profile#me>,
                        <https://frank.example/profile#me> ] .
```

## Who may read statements about the space

Narrower on purpose. The label is part of how the organisation is arranged, and Frank is on the team
without being told how the teams are laid out.

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/_system/contexts/spaces/eng> ;
  acp:accessControl [ acp:apply <#aboutTheSpace> ]
] .

<#aboutTheSpace>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://dana.example/profile#me> ] .
```

## Dana reads the label

```turtle context
[
  acp:target <https://acme.example/_system/contexts/spaces/eng> ;
  acp:agent  <https://dana.example/profile#me> ;
  acp:owner  <https://acme.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

`read` and not `write`. The space admits her for both, the subject decision for reading only, and the
pod grants what both allow — the same intersection every other scenario uses, reached here without
two IRIs to compose across.

## Frank cannot

```turtle context
[
  acp:target <https://acme.example/_system/contexts/spaces/eng> ;
  acp:agent  <https://frank.example/profile#me> ;
  acp:owner  <https://acme.example/profile#me>
] .
```

```turtle grant
# nothing
```

He may read and write everything else the space holds. This one statement is about the space rather
than in it, and the second decision does not name him.

## What this file is guarding against

Keyed by IRI alone, the two access control resources here collide. An implementation has three ways
to get that wrong and all of them look reasonable from inside:

- **keep the first** — the subject policy never loads, and Frank reads the label;
- **keep the last** — the context policy never loads, and the space stops admitting anybody; or,
- **merge them** — the union of the two matchers admits Frank to both.

The third is the dangerous one, because it is the one that fails towards *more* access while looking
like a sensible way to reconcile two documents about the same IRI. None of the three is reachable
once the decision kind is part of the key.
