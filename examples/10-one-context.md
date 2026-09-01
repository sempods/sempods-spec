# A pod with one place to put things

Anna keeps recipes in her pod. She has never thought about contexts and does not need to: her pod has
one, it was there when the pod was made, and everything she writes goes into it.

Then she shares the lot with her brother Ben.

This is the whole model at its smallest. **The thing access is decided on is the context**, sharing
is a policy on it, and there is nothing else in play.

## The one context, and who may reach it

One rule, and it is the only one Anna wrote.

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://anna.example/_system/contexts/default> ;
  acp:accessControl [ acp:apply <#ben> ]
] .

<#ben>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://ben.example/profile#me> ] .
```

**The target is the context, not a recipe.** One decision covers every statement the context holds.
Anna has thousands of them and one rule.

**And Anna herself is not in it.** The pod owner holds everything on every context implicitly, and
[`SPS-GRANT-011`](../spec/core/grants.md#SPS-GRANT-011) says an implementation must not require those
grants to be stored. So the authority that matters most appears in no access control resource, and no
fixture here can show it: what the runner evaluates is what somebody wrote down, and nobody writes
that down. The pod supplies it.

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

No policy on a recipe. Nothing for a client to choose between — but the catalogue is still there, and
that is the point rather than an exception.

Anna's writes carry `?context=`, naming the one context, and the discovery route
([`SPS-CTX-021`](../spec/core/contexts.md#SPS-CTX-021)) is where a client reads that name: it may not
construct the IRI itself ([`SPS-CTX-023`](../spec/core/contexts.md#SPS-CTX-023)). So a listing of one
is not a formality — it is the only specified way to learn the value the write must carry.

The parameter looks like ceremony and is not: the invariant it serves forbids an implicit fallback,
and a pod with a single candidate is precisely where a fallback would appear and never be noticed. It
costs a client the same call it would make with fifty contexts, and it keeps the pod from acquiring a
default it would later have to take away.

A pod can stay like this forever. The next two scenarios add one thing each: several contexts to
choose between, and then a second, finer decision inside them.
