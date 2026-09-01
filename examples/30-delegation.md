# The application is not the person

Alice shares a document with Bob. Bob reads it through a notes application he authorised. Later he
tries the same document through a tool he has never authorised, and it is gone.

Nothing about Bob changed between those two requests. What changed is **which application was
acting as him** — and that is a second question, asked of a second policy, because the two are
decided by different people. Alice decides who may read her document. Bob decides how much of his
own access an application receives ([`SPS-GRANT-013`](../spec/core/grants.md#SPS-GRANT-013)), and
neither can answer for the other.

This scenario is also where the examples stop covering a whole decision. The runner checks **one
evaluation at a time**, which is exactly as far as the ACP conformance claim reaches; combining two
evaluations is sempods' rule and not ACP's.

## What Alice wrote

Names only. Alice has no idea which applications Bob uses and it is not hers to say.

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/roadmap> ;
  acp:accessControl [ acp:apply <#owner>, <#bob> ]
] .

<#owner>
  a acp:Policy ;
  acp:allow acl:Read, acl:Write, acl:Control ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:OwnerAgent ] .

<#bob>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://bob.example/profile#me> ] .
```

```turtle context
[
  acp:target <https://alice.example/notes/roadmap> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

Read the client in that request again: it is a tool Bob never authorised, and Alice's policy grants
anyway. **That is correct.** Alice's policy answers her question — may Bob read this — and it has no
opinion about applications. If the decision stopped here the tool would be in.

## What Bob agreed to

His delegation is its own document with its own target: the pod, not the document. A person consents
to an application once, over a scope, and does not re-consent per resource.

The application is named by its `did:web:` identifier, which is its origin and is parsed structurally
rather than fetched ([`SPS-AUTH-003`](../spec/core/auth.md#SPS-AUTH-003)).

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/> ;
  acp:accessControl [ acp:apply <#bobToNotesApp> ]
] .

<#bobToNotesApp>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:allOf [ a acp:Matcher ; acp:agent  <https://bob.example/profile#me> ] ,
            [ a acp:Matcher ; acp:client <did:web:notes.example> ] .
```

`acp:allOf` is doing the work. Both matchers must be satisfied, so the policy speaks about a *pair* —
this person through this application — and neither half alone.

## Bob through the application he authorised

```turtle context
[
  acp:target <https://alice.example/> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

## Bob through the tool he did not

```turtle context
[
  acp:target <https://alice.example/> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example>
] .
```

```turtle grant
# nothing
```

Two evaluations, two answers. The pod grants what **both** allow, so Bob reads the document through
the notes application and reads nothing through the tool. That intersection is where the request is
finally decided, and it is a sempods rule — ACP has no operator that joins two evaluations, which is
why this file checks them one at a time.

## Why the client constraint cannot simply be added to Alice's policy

The obvious shortcut is to put `acp:client` into the document's own policy and drop the second
evaluation. It does not work, and the reason is worth seeing rather than being told.

Here is a second document where Alice tried exactly that — she kept her rule for Bob and added a
client-constrained one beside it.

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/shortcut> ;
  acp:accessControl [ acp:apply <#plainBob>, <#bobViaNotes> ]
] .

<#plainBob>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://bob.example/profile#me> ] .

<#bobViaNotes>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:allOf [ a acp:Matcher ; acp:agent  <https://bob.example/profile#me> ] ,
            [ a acp:Matcher ; acp:client <did:web:notes.example> ] .
```

```turtle context
[
  acp:target <https://alice.example/notes/shortcut> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

And through the application she meant to privilege:

```turtle context
[
  acp:target <https://alice.example/notes/shortcut> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

Both clients, one answer. The constraint Alice added is **provably inert** — it changed no outcome
it was written to change. **Policies compose by union**, so a policy that names a client adds a way
in; it never takes one away. To make the constraint bite, Alice's plain rule for Bob
would have to disappear, and then Alice would be maintaining one policy per person *per application*
and rewriting them whenever Bob adopts a new tool. A restriction that can only widen is worse than
none, because it looks like a control.

## The part that is not settled

Alice shares a second document with Bob.

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/finance> ;
  acp:accessControl [ acp:apply <#bobToo> ]
] .

<#bobToo>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://bob.example/profile#me> ] .
```

```turtle context
[
  acp:target <https://alice.example/notes/finance> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

Bob's delegation was not touched. It still says *read, as Bob, in this pod* — and this document is
now in the pod, so the notes application reaches it. Nobody asked Bob again.

Whether that is right is an open question rather than a settled rule.
[`SPS-GRANT-019`](../spec/core/grants.md#SPS-GRANT-019) says widening a person's grants must not
widen an application retroactively, and its reason is that regaining access should not silently
re-arm every application that once wanted it. No grant was widened here — Alice changed a policy,
which is a different act — so the rule is kept and its reason is walked around.

The alternative is a delegation scoped finely enough to exclude the new document, and that is a
delegation per resource, which nobody can consent to. The concept records the shape of the problem;
this scenario is what it looks like.
