# The share Alice did not make

Alice shares a plan with Bob. Bob shares it on with Carla. Then Alice withdraws Bob's access.

What happens to Carla turned on a rule that was not obvious, and this file is the measurement that
decided it. **There is no interpersonal sharing operation in the specification at all.** Grants for a
person are durable stored policy
([`SPS-GRANT-012`](../spec/core/grants.md#SPS-GRANT-012)) and no requirement says who may write one;
what the chapters do define is delegation to an *application*, where holding a grant is enough to
pass a subset of it on ([`SPS-GRANT-030`](../spec/core/grants.md#SPS-GRANT-030)). Sharing a context
is not that, and neither is `manage` as the chapters use it, which governs creating and deleting
contexts ([`SPS-CTX-019`](../spec/modules/context-management.md#SPS-CTX-019)).

So the question was never whether to relax an existing rule. It was which rule to write, and there
were two candidates: **reading is enough**, where every reader may pass on what they can already see
and revocation sweeps the shares made under an access that is now gone — or **`manage` is required**,
which is the answer the concept now carries
([`../docs/concepts/access-control.md`](../docs/concepts/access-control.md) §"Who may share, and why
there is no chain").

**This scenario works the branch that was refused.** The graphs are ordinary ACP either way; what
changes between them is which policies exist, which is exactly what the design decides.

## How three moments fit in a file

A fixture has no notion of time. So the same plan appears under three IRIs, one per state, and the
names say which:

| | |
|---|---|
| `…/plan` | after Alice shared with Bob and Bob shared on with Carla |
| `…/plan-swept` | after Alice withdrew Bob, with the sweep |
| `…/plan-kept` | after Alice withdrew Bob, with Carla still there |

## While the chain stands

```turtle holds
<https://alice.example/notes/plan>       <https://example.invalid/runner#inContext> <https://alice.example/_system/contexts/notes> .
<https://alice.example/notes/plan-swept> <https://example.invalid/runner#inContext> <https://alice.example/_system/contexts/notes> .
<https://alice.example/notes/plan-kept>  <https://example.invalid/runner#inContext> <https://alice.example/_system/contexts/notes> .
```

Alice's notes are a context, and it decides first — every one of the states below is a read that has
to pass it before any policy on a plan is consulted.

```turtle acr-context
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/_system/contexts/notes> ;
  acp:accessControl [ acp:apply <#notesReaders> ]
] .

<#notesReaders>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ;
              acp:agent <https://bob.example/profile#me>,
                        <https://carla.example/profile#me> ] .
```

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/plan> ;
  acp:accessControl [ acp:apply <#bob>, <#carla> ]
] .

<#bob>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://bob.example/profile#me> ] .

<#carla>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://carla.example/profile#me> ] .
```

```turtle decision
[
  acp:target <https://alice.example/_system/contexts/notes> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://alice.example/notes/plan> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

Both halves are in that block. If Carla could not read the context, no policy Bob wrote on the plan
would reach her — the resharing question only arises inside a context she is already in, and stating
it that way is what keeps this file from certifying a read that skipped the sandbox.

Look at what Carla's policy does **not** say: that Bob put it there. Every policy here is a flat
statement that somebody may read, and they are indistinguishable in origin. That is not a gap in the
example — a policy is a rule rather than a record of who wrote it.

Be exact about what is missing, because ACP does have an issuer: `acp:issuer` is one of its four
matcher attributes, and a policy may perfectly well ask who issued the credential a request carries.
What no ACP vocabulary records is **who wrote the policy** — its provenance rather than the request's.
An implementer reading "ACP has no issuer" would drop a matcher that exists; what they need is a
place to keep authorship, and that is not in the ACR.

## After Alice withdraws Bob, if the sweep ran

Carla's access existed only because Bob's did. It goes with it.

Read that heading carefully, because the runner cannot check the sweep and it would be worth saying
so even if it could. What the blocks below hold is an **end state**, supplied rather than derived: an
implementation whose sweep wrongly kept Carla would produce the other end state further down, and no
fixture here would notice, because the two are told apart by which policies exist and not by how they
came to. That is not a gap this file works around — it is the file's finding, and the closing section
is where it lands.

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/plan-swept>
] .
```

Nothing is left. Alice still reaches her own plan, but that is the pod giving its owner authority
without storing it ([`SPS-GRANT-011`](../spec/core/grants.md#SPS-GRANT-011)) rather than anything
written here.

```turtle decision
[
  acp:target <https://alice.example/_system/contexts/notes> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://alice.example/notes/plan-swept> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
# nothing
```

This is what [`SPS-GRANT-016`](../spec/core/grants.md#SPS-GRANT-016) already demands for
applications, in a shape one step deeper: revocation is a **recomputation** and not a string match,
because what has to go is derived rather than named. Extending it from *what an application received*
to *what a person passed on* is the same instruction with a longer chain to walk.

## The same withdrawal, if Carla was granted directly too

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/plan-kept> ;
  acp:accessControl [ acp:apply <#carlaKept> ]
] .

<#carlaKept>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://carla.example/profile#me> ] .
```

```turtle decision
[
  acp:target <https://alice.example/_system/contexts/notes> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://alice.example/notes/plan-kept> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

## What the file measures

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


## What was decided

`manage`, not reading. A share is issued directly by somebody who holds it, every holder is a peer of
every other, and any of them may remove what another granted — so none of the above is reachable:
there is no chain to walk, no provenance to keep beside the access control resource, and no blast
radius travelling further than the person who acted.

The three states stay in this file as they are. What they measure is the price of the branch nobody
took, and a refused alternative is worth more with its cost attached than as a sentence saying it was
refused.
