# A resource only its owner may touch

Alice keeps a contact in her pod. Nobody else should see it, and she does not want to write a rule
saying so — she just does not grant anyone.

This is the smallest complete policy there is, and it shows the two things everything else builds on:
**nothing is granted unless a policy grants it**, and **the owner is a role, not a name**.

Demonstrates [`SPS-GRANT-011`](../spec/core/grants.md#SPS-GRANT-011) and
[`SPS-GRANT-009`](../spec/core/grants.md#SPS-GRANT-009).

## The policy

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/contacts/bob-smith> ;
  acp:accessControl [ acp:apply <#owner> ]
] .

<#owner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .
```

Two details worth naming, because they are what makes this file readable by any ACP engine and not
only by ours.

`acp:OwnerAgent` is not a WebID. It is a fixed comparison: *the agent making the request is one of
the resource's owners.* The server supplies both facts and the engine compares them. Without it a
policy could only ever list names, and Alice would have to write her own WebID into every resource
she creates.

The three modes are **written out**. sempods says `manage` implies `write` implies `read`
([`SPS-GRANT-009`](../spec/core/grants.md#SPS-GRANT-009)), but ACP has no such rule — so the
implication is applied when the policy is written, not when it is evaluated. A policy that said only
`acl:Control` would grant only `acl:Control` to anyone reading it as plain ACP.

## Alice reads her own contact

The server describes the request. `acp:owner` is its own statement about the resource, not something
the caller sends.

```turtle context
[
  acp:target <https://alice.example/contacts/bob-smith> ;
  acp:agent  <https://alice.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write, acl:Control .
```

## Carla asks for the same contact

Carla is a real, authenticated person. No policy mentions her, and she does not own the resource.

```turtle context
[
  acp:target <https://alice.example/contacts/bob-smith> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
# nothing
```

Nothing was denied here. The single policy simply was not satisfied, and an unsatisfied policy
contributes no modes. There is no rule to write for "Carla may not" — the absence of a grant *is* the
answer, which is why a pod is private before anybody configures it.

## Nobody at all asks

An unauthenticated request carries no agent.

```turtle context
[
  acp:target <https://alice.example/contacts/bob-smith> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
# nothing
```

Same outcome, different reason: with no agent in the request there is nothing for `acp:OwnerAgent` to
compare against. Public access is never accidental — it takes a policy that says so, and this
resource has none.
