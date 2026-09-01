# A pod with one place to put things

Anna keeps recipes in her pod. She has never thought about contexts and does not need to: her pod has
one, it was there when the pod was made, and everything she writes goes into it.

Then she shares the lot with her brother Ben.

This is the whole model at its smallest. **The thing access is decided on is the context**, sharing
is a policy on it, and there is nothing else in play.

## The one context, and who may reach it

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://anna.example/_system/contexts/default> ;
  acp:accessControl [ acp:apply <#owner>, <#ben> ]
] .

<#owner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#ben>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://ben.example/profile#me> ] .
```

Two things to notice, because everything later builds on them.

**The target is the context, not a recipe.** One decision covers every statement the context holds.
Anna has thousands of them and one rule.

**`acp:OwnerAgent` is a role, not a name.** The pod states who owns it and the engine compares; Anna's
WebID appears nowhere. If the pod ever changed hands the policy would still be right — which is why
[`SPS-CTX-007`](../spec/core/contexts.md#SPS-CTX-007) keeps an owner's identity out of context paths
for the same reason.

## Anna works on her recipes

```turtle context
[
  acp:target <https://anna.example/_system/contexts/default> ;
  acp:agent  <https://anna.example/profile#me> ;
  acp:owner  <https://anna.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write, acl:Control .
```

The three modes are written out rather than implied. sempods says `manage` covers `write` covers
`read` ([`SPS-GRANT-009`](../spec/core/grants.md#SPS-GRANT-009)), but ACP has no such rule, so the
implication is applied when the policy is written. A policy saying only `acl:Control` would grant only
that to anyone reading it as plain ACP.

## Ben looks something up

```turtle context
[
  acp:target <https://anna.example/_system/contexts/default> ;
  acp:agent  <https://ben.example/profile#me> ;
  acp:owner  <https://anna.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

## Somebody else tries

```turtle context
[
  acp:target <https://anna.example/_system/contexts/default> ;
  acp:agent  <https://mallory.example/profile#me> ;
  acp:owner  <https://anna.example/profile#me>
] .
```

```turtle grant
# nothing
```

No rule was written to keep Mallory out. Neither policy is satisfied, an unsatisfied policy
contributes nothing, and nothing is what she gets. **A pod is private before anybody configures it**,
and staying private takes no work.

## What is not here

No policy on a recipe. No `?context=` on Anna's writes — there is nothing to choose between, so the
parameter has nothing to say. No catalogue for a client to browse, because a list of one is not a
choice.

A pod can stay like this forever. The next two scenarios add one thing each: several contexts to
choose between, and then a second, finer decision inside them.
