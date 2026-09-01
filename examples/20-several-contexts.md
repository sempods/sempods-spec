# A pod with areas

Anna's pod has grown. Her recipes are worth publishing, her bank statements are not, and she is
planning a trip with Ben who should see the plan and edit it.

So she makes three contexts. Nothing about the model changes — **each context is decided exactly the
way the single one was**, and what she gains is something to choose between.

This is the shape most pods have, and the one the chapters describe today.

## Recipes, published

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://anna.example/_system/contexts/recipes> ;
  acp:accessControl [ acp:apply <#recipesOwner>, <#recipesPublic> ]
] .

<#recipesOwner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#recipesPublic>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:PublicAgent ] .
```

`acp:PublicAgent` matches every request, including one carrying no agent at all. That is what makes a
context public — an ordinary policy, not a separate branch of the decision.

## Anybody at all reads a recipe

```turtle context
[
  acp:target <https://anna.example/_system/contexts/recipes> ;
  acp:owner  <https://anna.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

No agent in the request, and it still works. Public data is dereferenceable by anyone, which is the
property [`SPS-GRANT-031`](../spec/core/grants.md#SPS-GRANT-031) protects: anonymous is a supported
mode and not a degraded one.

## Bank statements, for nobody but Anna

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://anna.example/_system/contexts/finances> ;
  acp:accessControl [ acp:apply <#financesOwner> ]
] .

<#financesOwner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .
```

```turtle context
[
  acp:target <https://anna.example/_system/contexts/finances> ;
  acp:agent  <https://ben.example/profile#me> ;
  acp:owner  <https://anna.example/profile#me>
] .
```

```turtle grant
# nothing
```

Ben may read the recipes and not the statements. Two contexts, two access control resources, and no
rule anywhere says "Ben may not" — his access simply stops at the areas that mention him.

## The trip, shared for real

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://anna.example/_system/contexts/trip> ;
  acp:accessControl [ acp:apply <#tripOwner>, <#tripBen> ]
] .

<#tripOwner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#tripBen>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://ben.example/profile#me> ] .
```

```turtle context
[
  acp:target <https://anna.example/_system/contexts/trip> ;
  acp:agent  <https://ben.example/profile#me> ;
  acp:owner  <https://anna.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write .
```

Ben may write here, and `acl:Read` is written out beside `acl:Write` for the same reason as before.
It is not politeness: a write path is a read oracle — a conditional request, an entity tag, a patch
that succeeds or fails on what is already there — so
[`SPS-GRANT-010`](../spec/core/grants.md#SPS-GRANT-010) refuses to pretend that read can be withheld
from somebody who may write.

## What the client sees

Three areas, three answers, and the pod tells a client which is which: `GET {pod}/_system/contexts`
lists what the caller may reach and what they may write to
([`SPS-CTX-021`](../spec/core/contexts.md#SPS-CTX-021)). Ben sees `recipes` and `trip`, and can write
to `trip`. He never learns that `finances` exists.

That listing is what makes the choice usable — a client picks a write target from it and names it with
`?context=` ([`SPS-CRUD-007`](../spec/core/lod-crud.md#SPS-CRUD-007)) rather than constructing an IRI
of its own ([`SPS-CTX-023`](../spec/core/contexts.md#SPS-CTX-023)).

Still no policy anywhere on a single recipe or a single note. Every audience Anna has lines up with an
area, so an area is all she needs.
