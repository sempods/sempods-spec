# The share Alice did not make

Alice shares a plan with Bob. Bob shares it on with Carla. Then Alice withdraws Bob's access.

What happens to Carla is a design question this specification has not answered, because today only a
`manage` grant lets somebody share at all
([`SPS-CTX-019`](../spec/core/contexts.md#SPS-CTX-019)). The question is whether reading should be
enough — every reader may pass on what they can already see — with revocation sweeping the shares
that were made under an access that is now gone.

**This scenario works the question rather than the answer.** The graphs are ordinary ACP either way;
what changes between them is which policies exist, which is exactly what the design decides.

## How three moments fit in a file

A fixture has no notion of time. So the same plan appears under three IRIs, one per state, and the
names say which:

| | |
|---|---|
| `…/plan` | after Alice shared with Bob and Bob shared on with Carla |
| `…/plan-swept` | after Alice withdrew Bob, with the sweep |
| `…/plan-kept` | after Alice withdrew Bob, with Carla still there |

## While the chain stands

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/plan> ;
  acp:accessControl [ acp:apply <#owner>, <#bob>, <#carla> ]
] .

<#owner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#bob>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://bob.example/profile#me> ] .

<#carla>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://carla.example/profile#me> ] .
```

```turtle context
[
  acp:target <https://alice.example/notes/plan> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

Look at what Carla's policy does **not** say: that Bob put it there. Every policy here is a flat
statement that somebody may read, and they are indistinguishable in origin. That is not a gap in the
example — ACP has no issuer, and a policy is a rule rather than a record of who wrote it.

## Alice withdraws Bob, and the sweep runs

Carla's access existed only because Bob's did. It goes with it.

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/plan-swept> ;
  acp:accessControl [ acp:apply <#ownerSwept> ]
] .

<#ownerSwept>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .
```

```turtle context
[
  acp:target <https://alice.example/notes/plan-swept> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
# nothing
```

```turtle context
[
  acp:target <https://alice.example/notes/plan-swept> ;
  acp:agent  <https://alice.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write, acl:Control .
```

This is what [`SPS-GRANT-016`](../spec/core/grants.md#SPS-GRANT-016) already demands for
applications, in a shape one step deeper: revocation is a **recomputation** and not a string match,
because what has to go is derived rather than named. Extending it from *what an application received*
to *what a person passed on* is the same instruction with a longer chain to walk.

## The same withdrawal, and Carla stays

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/plan-kept> ;
  acp:accessControl [ acp:apply <#ownerKept>, <#carlaKept> ]
] .

<#ownerKept>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#carlaKept>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://carla.example/profile#me> ] .
```

```turtle context
[
  acp:target <https://alice.example/notes/plan-kept> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

## The point of the file

That last state is **two different stories with one policy**, and nothing in the graph tells them
apart:

- there was no sweep, so a share Alice never made outlived the only person she did share with; or,
- the sweep ran correctly, and Carla stayed because Alice had granted her directly as well, so only
  Bob's share was removed.

The first is a defect. The second is exactly right. They compile to the same access control resource
because **the difference is not in the policy** — it is in who issued which grant, and a policy has
no room for that. So a design that lets readers pass access on has to keep provenance as
control-plane state beside the ACR, and the ACR becomes its output rather than the whole truth.

That is the real cost, and it is not the sweep. The sweep is a graph walk. The cost is a second thing
to keep in step with the first, and a resource whose policy no longer explains itself.

## Two consequences that are easy to miss

**The blast radius is wide and silent.** Alice withdraws one person. Carla, Dana and everybody
downstream lose access mid-task, having had no part in the decision. Nobody can warn them: Alice does
not know who is downstream, and showing her would expose how Bob shares.

**An application acting as Bob would share too.** A grant is resolved from the pair of verified
client and verified subject ([`SPS-GRANT-002`](../spec/core/grants.md#SPS-GRANT-002)), and an
application acts as the person. If reading is enough to pass access on and the application reads,
then it may issue grants — which is precisely the spread the delegation ceiling exists to bound.
Saying otherwise means separating *Bob acting* from *Bob's application acting* for this one
operation. The pair makes that expressible; what it does not do is decide it, and left undecided it
falls the application's way.
