# A space whose documents are not all for the same readers

An engineering team shares a space. Everyone on the team may read and write in it — except for one
document about the salary round, which is for the people running it.

Anna's pod could not express that with areas alone. She would have to make a second space just for
the one document, and moving a document between audiences would mean moving data instead of editing a
rule. So this deployment declares the **resource module**, and a second decision applies inside the
space.

**Both must allow.** The space decides which statements are reachable at all; the resource decision
narrows further, per subject, within them.

## The space

Exactly the kind of access control resource the previous scenario used. Nothing about the base
decision changes when the module is added.

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/_system/contexts/spaces/eng> ;
  acp:accessControl [ acp:apply <#spaceOwner>, <#spaceMembers> ]
] .

<#spaceOwner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#spaceMembers>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write ;
  acp:anyOf [ a acp:Matcher ;
              acp:agent <https://dana.example/profile#me>,
                        <https://frank.example/profile#me> ] .
```

## Dana is on the team

```turtle context
[
  acp:target <https://acme.example/_system/contexts/spaces/eng> ;
  acp:agent  <https://dana.example/profile#me> ;
  acp:owner  <https://acme.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write .
```

## Erik runs the salary round, and is not on the team

```turtle context
[
  acp:target <https://acme.example/_system/contexts/spaces/eng> ;
  acp:agent  <https://erik.example/profile#me> ;
  acp:owner  <https://acme.example/profile#me>
] .
```

```turtle grant
# nothing
```

Hold on to that answer. Erik is about to be named in a document policy, and it will not help him.

## The ordinary document

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/docs/roadmap> ;
  acp:accessControl [ acp:apply <#roadmapTeam> ]
] .

<#roadmapTeam>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write ;
  acp:anyOf [ a acp:Matcher ;
              acp:agent <https://dana.example/profile#me>,
                        <https://frank.example/profile#me> ] .
```

```turtle context
[
  acp:target <https://acme.example/docs/roadmap> ;
  acp:agent  <https://dana.example/profile#me> ;
  acp:owner  <https://acme.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write .
```

## The one that is not

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/docs/salary-round> ;
  acp:accessControl [ acp:apply <#salaryOwners> ]
] .

<#salaryOwners>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://erik.example/profile#me> ] .
```

```turtle context
[
  acp:target <https://acme.example/docs/salary-round> ;
  acp:agent  <https://dana.example/profile#me> ;
  acp:owner  <https://acme.example/profile#me>
] .
```

```turtle grant
# nothing
```

```turtle context
[
  acp:target <https://acme.example/docs/salary-round> ;
  acp:agent  <https://erik.example/profile#me> ;
  acp:owner  <https://acme.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

## Putting the two together

Each block above is one decision. The pod asks both and grants what both allow:

| | space `eng` | document | the pod grants |
|---|---|---|---|
| **Dana** on `roadmap` | `read`, `write` | `read`, `write` | `read`, `write` |
| **Dana** on `salary-round` | `read`, `write` | — | **nothing** |
| **Erik** on `salary-round` | — | `read` | **nothing** |

**Erik is the row that matters.** A document policy names him, and he still gets nothing, because he
cannot see the space that holds the document. The finer decision can only take away — it never lets
somebody in through a door the space kept shut.

That is why the two compose by intersection and not by union. A document policy that appeared to
restrict a broad space grant, but could also widen it, would be a control that is not one.

## What this file cannot check for you

The runner evaluates one access control resource against one request, which is exactly as far as the
ACP conformance claim goes: each block above is ordinary ACP that any engine would resolve the same
way. Joining two of them is sempods' composition rule — ACP has no operator for it — so the table is
the part you have to read rather than run.
