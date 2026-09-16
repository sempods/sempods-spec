# The application is not the person

Proposed ACP composition illustrating delegation bounds. The generic mode ceiling and public
branch do not implement the current per-Context delegation and OAuth scope contracts. Their gaps
are preserved for future validation, not resolved by this example. See the
[fixture assumptions](../docs/guides/acp-fixtures.md).

Alice shares a document with Bob. Bob reads it through a notes application he authorised. Later he
tries the same document through a tool he has never authorised, and it is gone.

Nothing about Bob changed between those two requests. What changed is **which application was
acting as him** — and that is a second question, asked of a second policy, because the two are
decided by different people. Alice decides who may read her document. Bob decides how much of his
own access an application receives ([`SPS-GRANT-013`](../spec/core/grants.md#SPS-GRANT-013)), and
neither can answer for the other.

Two evaluations, and the pod grants what both allow. That composition belongs to this model rather than
ACP — ACP has no operator for it — so the runner applies it outside the ACP engine rather than
inside, and this file checks both the halves and the whole.

Alice's notes live in one context, which the fixture states because no policy does:

```turtle holds
<https://alice.example/notes/roadmap>  <https://example.invalid/runner#inContext> <https://alice.example/_system/contexts/notes> .
<https://alice.example/notes/finance>  <https://example.invalid/runner#inContext> <https://alice.example/_system/contexts/notes> .
<https://alice.example/notes/shortcut> <https://example.invalid/runner#inContext> <https://alice.example/_system/contexts/notes> .
```

## What Alice wrote

Two things in the proposed composition. First, the context her notes live in:

```turtle acr-context
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/_system/contexts/notes> ;
  acp:accessControl [ acp:apply <#notesReaders> ]
] .

<#notesReaders>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://bob.example/profile#me> ] .
```

and the document, named only. Alice has no idea which applications Bob uses and it is not hers to
say.

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/roadmap> ;
  acp:accessControl [ acp:apply <#bob> ]
] .

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

His delegation is its own document with its own target — **Bob himself**, not the pod and not the
document. A person consents to an application once and does not re-consent per resource, so the
question this evaluation answers is about him: how much of Bob's authority did this application
receive?

The target has to be the principal rather than the pod. Carla's delegation would otherwise declare
the same target, two canonical documents would claim one IRI, and whichever loaded second would
silently replace the first — so Bob would lose access because Carla authorised an application.

The application is named by its `did:web:` identifier, which is its origin and is parsed structurally
rather than fetched ([`SPS-AUTH-003`](../spec/core/auth.md#SPS-AUTH-003)).

```turtle acr-delegation
[
  a acp:AccessControlResource ;
  acp:resource <https://bob.example/profile#me> ;
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
  acp:target <https://bob.example/profile#me> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

## Bob through the tool he did not

```turtle context
[
  acp:target <https://bob.example/profile#me> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
# nothing
```

What this scenario does **not** settle is what the ceiling is scoped to. Naming Bob as the target
says whose authority is being bounded, not how far the bounding reaches — whether a person delegates
over the whole pod, over a set of contexts, or over something narrower is an open decision, and
encoding an answer in the target would have decided it by accident.

It is worth seeing why that leaves a narrower ceiling not merely unwritten but currently
inexpressible. Because `acp:target` names Bob, this evaluation is the same one for every request he
makes; nothing in it mentions the document. So *"read, as Bob, but only in this context"* has nowhere
to go — it needs a second artifact that carries the target, or a rule choosing between several
delegation policies, and both are decisions rather than spellings. What the shape above does express
is a ceiling on **modes**, which is what these two cases exercise.

Three evaluations, three answers. The pod grants what **all** allow — and that is the sentence this
scenario is about, so it is checked rather than asserted. A `decision` block puts one request to both
access control resources at once, and the grant below it is the expected model result:

```turtle decision
[
  acp:target <https://alice.example/_system/contexts/notes> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://alice.example/notes/roadmap> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://bob.example/profile#me> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

```turtle decision
[
  acp:target <https://alice.example/_system/contexts/notes> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://alice.example/notes/roadmap> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://bob.example/profile#me> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
# nothing
```

The second is the document opening in one application and being gone in the other, which is where
this file started. Alice's policy still grants `acl:Read` on its own — that evaluation is unchanged
above — and the pod returns nothing, because another half refuses.

The context half is in both, and it is not decoration. Every resource access passes its containing
context first; leaving it out would let this file certify a read that never met the sandbox every pod
enforces. Make the context unreadable to Bob and both cases go empty, however generous Alice's
document policy is.

Both halves are resolved by the plain ACP engine; the intersection is applied to their answers
afterwards. That separation is the point. ACP has no operator joining two evaluations, so the runner
does not pretend it has one — it composes outside the engine, exactly where this model places it, and a
`decision` case fails if that composition is ever changed to something wider.

## What the ceiling cannot take away

Alice also publishes a reading list. It is public, and that changes what the tool Bob never
authorised can see.

```turtle acr-context
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/_system/contexts/published> ;
  acp:accessControl [ acp:apply <#anyone> ]
] .

<#anyone>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:PublicAgent ] .
```

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://alice.example/notes/reading-list> ;
  acp:accessControl [ acp:apply <#anyoneToo> ]
] .

<#anyoneToo>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent acp:PublicAgent ] .
```

```turtle holds
<https://alice.example/notes/reading-list>
  <https://example.invalid/runner#inContext> <https://alice.example/_system/contexts/published> .
```

```turtle decision
[
  acp:target <https://alice.example/_system/contexts/published> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://alice.example/notes/reading-list> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://bob.example/profile#me> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:spamtool.example> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

Bob's ceiling grants this tool nothing, and the tool reads anyway. That is not a leak in the ceiling —
it is what a ceiling is for. It bounds **Bob's** authority, and this document needs none of it: an
anonymous request reads the list perfectly well, so this fixture adds the public branch independently. It does not model OAuth scopes or validate
tokens; the current `public-read` rules remain those in the authorization chapter.

Which is why the two combine by union rather than by intersection: the ceiling narrows what Bob was
delegated, and the public branch is added to whatever that leaves. Take the public policy away and
this case goes empty, because then there is nothing to add.

## Why the client constraint cannot simply be added to Alice's policy

The obvious shortcut is to put `acp:client` into the document's own policy and drop the second
evaluation. It does not work, and the reason is worth seeing rather than being told.

Here is a second document where Alice tried exactly that — she kept her rule for Bob and added a
client-constrained one beside it.

```turtle acr-resource
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

```turtle acr-resource
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

```turtle decision
[
  acp:target <https://alice.example/_system/contexts/notes> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://alice.example/notes/finance> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example> ;
  acp:owner  <https://alice.example/profile#me>
] .

[
  acp:target <https://bob.example/profile#me> ;
  acp:agent  <https://bob.example/profile#me> ;
  acp:client <did:web:notes.example> ;
  acp:owner  <https://alice.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

Bob's delegation was not touched. It still says *read, as Bob, in this pod* — and this document is
now in the pod, so the notes application reaches it. Nobody asked Bob again.

All three decisions are in that block, which is what makes the claim a claim. Revoke the notes
application's delegation, or shut Bob out of the context, and this case goes empty — so the sentence
above is about a delegation that is genuinely still standing rather than one nothing checks.

The fixture supplies a delegation described only as *read, as Bob, in this pod*. It does not model
what Bob approved about future data. The [proposal's delegation recommendation](../docs/proposals/access-control.md#delegation-and-revocation)
distinguishes a fixed resource selection from an explicitly approved dynamic data space. In its fixed
case, this newly shared document is excluded. A dynamic selection can include future members only
inside its described delegable boundary; access to one document does not authorize all future
shares. Narrowed or withdrawn authority does not return without fresh consent.

[`SPS-GRANT-019`](../spec/core/grants.md#SPS-GRANT-019) remains the current contract. The proposal
requires coordinated adoption; this static fixture checks its supplied broad policy, not consent,
future-membership approval or revocation transitions. It demonstrates the ambiguity the proposed
boundary addresses, rather than testing that boundary.
