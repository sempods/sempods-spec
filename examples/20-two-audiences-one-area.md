# Two audiences in one area

Alice has an assistant, Carla. Carla should see the business contacts and keep the calendar tidy. She
should not see the therapist.

Both contacts sit in the same place. That is the point of this example: **the audience is a property
of the resource, not of where it is stored.** Without per-resource policy Alice would need two
separate areas, and changing who may see a contact would mean moving data rather than editing a rule.

Demonstrates [`SPS-CRUD-001`](../spec/core/lod-crud.md#SPS-CRUD-001) — a resource's identity is its
own IRI, which is what makes it addressable by a policy at all.

## Two policies, side by side

Each resource carries its own access control resource. They are independent documents; neither
inherits from the other and neither is affected by where the statements happen to be stored.

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/contacts/bob-smith> ;
  acp:accessControl [ acp:apply <#bobOwner>, <#bobAssistant> ]
] .

<#bobOwner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#bobAssistant>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://carla.example/profile#me> ] .
```

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/contacts/therapist> ;
  acp:accessControl [ acp:apply <#therapistOwner> ]
] .

<#therapistOwner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .
```

Carla appears in one document and not in the other. That is the whole mechanism — there is no rule
excluding her from the therapist, and there does not need to be one.

## Carla opens the business contact

```turtle context
[
  acp:target <https://alice.example/contacts/bob-smith> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

Two policies control this resource and both were considered. The owner policy was not satisfied —
Carla does not own it — and contributed nothing. The assistant policy was satisfied and contributed
`acl:Read`. **Policies accumulate; they never cancel each other.** Alice can widen Carla's access by
adding a policy and never has to rewrite the one that is already there.

## Carla opens the therapist contact

```turtle context
[
  acp:target <https://alice.example/contacts/therapist> ;
  acp:agent  <https://carla.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
# nothing
```

The engine looked only at this resource's own access control resource. Carla's access to the contact
next to it is not visible from here and does not reach across.

Carla cannot tell the difference between this and a contact that does not exist — both are simply
absent for her, and the read surface is required to keep them indistinguishable
([`SPS-CRUD-017`](../spec/core/lod-crud.md#SPS-CRUD-017)).

## Alice edits the therapist contact

```turtle context
[
  acp:target <https://alice.example/contacts/therapist> ;
  acp:agent  <https://alice.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write, acl:Control .
```

## What this would cost without per-resource policy

If permission could only attach to the storage area, Alice would need one area for contacts Carla may
see and another for contacts she may not. Two consequences follow, and both are why the resource
layer exists:

- moving a contact between audiences becomes a **data migration** rather than a policy edit, and
- every new audience — "shared with the accountant", "shared with my sister" — needs another area,
  so the number of areas grows with the number of distinct audiences rather than with how Alice
  actually wants to organise her pod.
