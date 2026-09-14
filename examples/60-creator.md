# The creator this pod cannot name

Illustrative ACP request facts. sempods specifies no generic creator attribute for RDF subjects.
This example compares absent and supplied facts; it specifies neither a creator API nor ACP discovery. See the
[fixture assumptions](../docs/guides/acp-fixtures.md).

Bob writes a draft into Alice's pod. He would like to keep editing it, and the obvious way to say so
is the one ACP provides: *whoever created this may change it.*

It does not work here, and the reason is worth more than the feature. **The current specification
provides no generic creator fact for an RDF subject.**

Demonstrates [`SPS-CRUD-003`](../spec/core/lod-crud.md#SPS-CRUD-003),
[`SPS-CRUD-011`](../spec/core/lod-crud.md#SPS-CRUD-011) and
[`SPS-GRANT-011`](../spec/core/grants.md#SPS-GRANT-011).

## Why the fact does not exist

Creating stored data does not identify the creator of the thing its subject names. Defining such
an authorization fact needs answers the current contract does not supply:

- Who created it — whoever wrote the first statement? In which context? A subject may hold statements
  in several, written by different people at different times
  ([`SPS-CRUD-011`](../spec/core/lod-crud.md#SPS-CRUD-011)).
- If every statement is deleted and new ones written later, was it created again, and by whom?
- And the one that settles it: a pod may hold statements about **any** IRI —
  `did:web:bob.example`, another pod's resources, anything
  ([`SPS-CRUD-003`](../spec/core/lod-crud.md#SPS-CRUD-003)). Writing
  `<did:web:bob.example> foaf:name "Bob"` would make the writer the *creator* of Bob's identifier.

A pod routinely holds statements about things nobody in it created. A new local occurrence of a
subject does not establish authorship of the thing it identifies.

Ownership does not have this problem, and the difference is the whole of it:

> **Owning is a fact about the pod. Creating would be a fact about the resource.**

[`SPS-GRANT-011`](../spec/core/grants.md#SPS-GRANT-011) gives the pod owner authority over everything
in the pod, whatever the statements happen to be about. Alice owns the pod, not the subject — so
`acp:OwnerAgent` always has something to compare against, and `acp:CreatorAgent` does not.

## The policy Bob would like to write

Both policies below are perfectly good ACP. Nothing here is malformed, unsupported or discouraged.

The owner policy is written out here, which the other scenarios deliberately do not do — a pod gives
its owner authority without storing it
([`SPS-GRANT-011`](../spec/core/grants.md#SPS-GRANT-011)). It appears because this file is about
comparing two relational matchers, and a fixture can only evaluate what is in front of it.

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/draft> ;
  acp:accessControl [ acp:apply <#owner>, <#creator> ]
] .

<#owner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#creator>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:CreatorAgent ] .
```

## Bob asks for his own draft

The pod describes the request. It states an owner, because it knows one. It states no creator,
because this case assumes no application-defined creator fact.

```turtle context
[
  acp:target <https://alice.example/notes/draft> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
# nothing
```

`acp:CreatorAgent` compares the requesting agent against the creators the request names, and this
request names none — so the comparison has nothing to succeed against. That is not sempods declining
to honour ACP. Any conforming ACP engine answers the same way, which is why this file passes its own
checker.

## Alice asks for the same draft

```turtle context
[
  acp:target <https://alice.example/notes/draft> ;
  acp:agent  <https://alice.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write, acl:Control .
```

Same two policies, same file. The owner one fires because the pod can say who the owner is. Side by
side, the two make the point better than either alone: the matcher is not the problem, the missing
fact is.

## The same policy, where the fact does exist

An implementation built around documents — one where creating a document *is* an operation somebody
performs — can state a creator, and then the policy Bob wanted works unchanged.

```turtle context
[
  acp:target  <https://alice.example/notes/draft> ;
  acp:agent   <https://bob.example/profile#me> ;
  acp:owner   <https://alice.example/profile#me> ;
  acp:creator <https://bob.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write, acl:Control .
```

Nothing about the access control resource changed. The result changes because the supplied request
facts changed. ACP server discovery is outside this fixture and is not adopted by sempods;
`acp:CreatorAgent` is simply unsatisfied where this case supplies no creator.

## What Bob does instead

The application that knows what a document is writes the policy when the document is made, naming
Bob outright.

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/draft-named> ;
  acp:accessControl [ acp:apply <#ownerToo>, <#bob> ]
] .

<#ownerToo>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#bob>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://bob.example/profile#me> ] .
```

```turtle context
[
  acp:target <https://alice.example/notes/draft-named> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read, acl:Write, acl:Control .
```

This is a fair trade rather than a workaround, and the reason is that **who created something never
changes.** Writing Bob's name is a statement that stays true, which is exactly what could not be said
of the pod owner — ownership transfers, and a policy naming Alice would become a lie the day the pod
changes hands. Constant-folding a relation into a value is sound when the value really is constant.

Two things are given up, and both are small:

- the policy records *that* Bob may edit, not *why*, so somebody tidying up later cannot tell his
  access from any other grant; and,
- if Bob starts using a different WebID, the policy does not follow him and he loses his own draft.

An application can define document semantics beyond the generic RDF contract and record a creator
when it creates a document. That is an application-defined fact, not an authorization attribute
implicitly established by storing statements about a subject.
