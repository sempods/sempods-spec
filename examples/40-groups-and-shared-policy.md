# A space, a group, and one policy used twice

Illustrative ACP policies with proposed resource composition and trust boundaries. Membership
resolution, policy editing and query enforcement are not executed. The unknown-extension case
intentionally checks what the plain ACP engine cannot grant. See the
[fixture assumptions](../docs/guides/acp-fixtures.md).

An engineering space with a news channel, its articles, a memo for one person, and a draft nobody has
finished granting. Its members are not a list somebody maintains in the policy — they are a group,
and who is in that group changes for reasons that have nothing to do with access control.

This is the shape a deployment reaches once audiences outgrow areas. Five things it shows: where a
group lives, how a policy names one, how several resources share a single policy, what happens to a
grant that names nobody, and what a plain ACP engine does with the part that is not plain ACP.

## Where the group lives

This design places membership outside ordinary data contexts. Membership is an authorization fact,
and the proposed trust boundary keeps its source beyond ordinary data writes — otherwise a caller writes a membership triple into a context they may write
and reads it back as authority.

It lives in a graph of its own, beside the access control resources rather than among the data. Note
the address: **outside** `_system/contexts/`, because everything under that path is a context IRI and
its own management route ([`SPS-CTX-005`](../spec/modules/context-management.md#SPS-CTX-005)), and a graph holding
authorization facts must not be something a caller can name there.

```turtle aside
# {pod}/_system/identity — control plane. Not in context discovery, not selectable with
# ?context=, unreachable through LOD CRUD or SPARQL. Shown here and not evaluated: this is not
# ACP, and the vocabulary is the deployment's own rather than anything sempods fixes. Kept in
# sync with whatever the organisation actually uses.
<https://acme.example/people/erin#me>  <https://acme.example/ns/memberOf> <https://acme.example/groups/engineers> .
<https://acme.example/people/frank#me> <https://acme.example/ns/memberOf> <https://acme.example/groups/engineers> .
```

The policy below writes down only the **name** of the set. Whether Erin is in it is one question
against that graph:

```sparql
ASK {
  GRAPH <https://acme.example/pod/_system/identity> {
    <https://acme.example/people/erin#me> <https://acme.example/ns/memberOf>
                                          <https://acme.example/groups/engineers>
  }
}
```

One accessor, one answer. An implementation deciding a request at a time asks it for each accessor the
effective policies actually name — a handful, however many groups Erin turns out to be in. The cost
follows the policies, not the person.

An implementation that composes the check into a query cannot ask ahead, because it does not know
which accessors a query will touch before running it. There the same lookup is a **join**, resolved
per candidate:

```sparql
# the accessor half of a rewritten read
{ ?requirement <https://acme.example/ns/accessor> ?agent }
UNION
{ ?requirement <https://acme.example/ns/accessor> ?group .
  ?agent       <https://acme.example/ns/memberOf> ?group }
```

Both forms need the identity graph readable to the **checking** half of a query while it stays
unreachable to the **client's** half. That double role is what the trust boundary is for, and it holds
by construction rather than by remembering: the graphs a guard consults and the graphs a client's
patterns can reach are two disjoint sets, assembled from different origins.

## What sits where

Subject and context are independent, so the fixture states the arrangement a pod would know:

```turtle holds
<https://acme.example/articles/welcome>    <https://example.invalid/runner#inContext> <https://acme.example/pod/_system/contexts/spaces/engineering> .
<https://acme.example/articles/onboarding> <https://example.invalid/runner#inContext> <https://acme.example/pod/_system/contexts/spaces/engineering> .
<https://acme.example/memo>                <https://example.invalid/runner#inContext> <https://acme.example/pod/_system/contexts/spaces/engineering> .
<https://acme.example/draft>               <https://example.invalid/runner#inContext> <https://acme.example/pod/_system/contexts/spaces/engineering> .
```

## The space, admitting a group and a person

```turtle acr-context
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/pod/_system/contexts/spaces/engineering> ;
  acp:accessControl [ acp:apply <#spaceRead> ]
] .

<#spaceRead>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://acme.example/people/carol#me> ] ,
            [ a acp:Matcher ; <https://acme.example/ns/principalSet>
                              <https://acme.example/groups/engineers> ] .
```

Two matchers under `acp:anyOf`, so either satisfies: Carol by name, everybody else by membership.
The proposed resolver would change membership without changing policy and apply removal on the next
request. This takes its intended deadline from [`SPS-GRANT-003`](../spec/core/grants.md#SPS-GRANT-003) sets for a revoked grant. The fixture does not execute a membership change or verify freshness.

Two matchers rather than one, because within a single matcher the attribute types conjoin: writing
`[ acp:agent carol ; ex:principalSet engineers ]` would mean *Carol, and only while she is in the
group*.

That form is not merely unwanted here — the profile forbids it, and this is the one place where a
foreign engine answers **more**. It cannot see `ex:principalSet`, so it has one conjunct fewer to
fail and grants Carol whether or not she is in the group. A conjunction between an extension and an
ACP attribute is written as two matchers under `acp:allOf` instead, where the foreign engine leaves
the extension matcher unsatisfied and the whole conjunction fails with it.

## Carol, named directly

```turtle context
[
  acp:target <https://acme.example/pod/_system/contexts/spaces/engineering> ;
  acp:agent  <https://acme.example/people/carol#me> ;
  acp:owner  <https://acme.example/pod/owner#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

## Erin, through the group

```turtle context
[
  acp:target <https://acme.example/pod/_system/contexts/spaces/engineering> ;
  acp:agent  <https://acme.example/people/erin#me> ;
  acp:owner  <https://acme.example/pod/owner#me>
] .
```

```turtle grant
# nothing — see below
```

Erin **is** in the group, and the proposed extension-aware resolver would grant her `acl:Read` here. The expectation says nothing
because this file is run by a plain ACP engine, and that engine does not know
`ex:principalSet`: a matcher carrying none of ACP's four attributes is never satisfied, so it leaves
her out.

The IRI is illustrative. Whether sempods should publish an extension and which IRI it would use
remain open decisions — writing a name into `schema.sempods.org/` here would reserve it before that decision
is made, in a namespace whose terms cannot later be renamed.

That is the portability boundary, and it is worth seeing rather than being told. Everything else in
these examples is ACP any engine resolves identically. The group is where this example explores an extension matcher, and the price is exactly this — a foreign engine answers *less*, never more.

That direction holds because of the rule above and not on its own, which is why the rule is worth
having: a matcher carries ACP's attributes or an extension, never both.

## Two articles, one policy

The channel's articles are all for the same readers. Rather than repeating a policy per article, each
access control resource applies the **same** one.

The policy is written once, in a block of its own:

```turtle policy
<https://acme.example/policies/news-channel-read>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://acme.example/people/carol#me> ] .
```

and each access control resource names it:

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/articles/welcome> ;
  acp:accessControl [ acp:apply <https://acme.example/policies/news-channel-read> ]
] .
```

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/articles/onboarding> ;
  acp:accessControl [ acp:apply <https://acme.example/policies/news-channel-read> ]
] .
```

```turtle context
[
  acp:target <https://acme.example/articles/welcome> ;
  acp:agent  <https://acme.example/people/carol#me> ;
  acp:owner  <https://acme.example/pod/owner#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

```turtle context
[
  acp:target <https://acme.example/articles/onboarding> ;
  acp:agent  <https://acme.example/people/carol#me> ;
  acp:owner  <https://acme.example/pod/owner#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

A policy is a resource with an IRI, and `acp:apply` points at it. So one rule can govern a channel, a
document and everything under it, and changing who may read the channel is **one edit** rather than a
sweep across every article.

That reach is the feature and also its price. `manage` on a target permits managing its policy, so
whoever manages *one* of these articles can rewrite a policy deciding access on the other — authority
picked up by reference rather than granted. Both articles have the same manager here and nothing goes
wrong; the [proposal](../docs/proposals/authorization-implementation/acp-profile.md#shared-policy-editing)
records how to stop relying on that — and rules out the obvious fix, because
refusing the edit on account of a target the caller cannot see is a topology leak.

This is what a sub-document needs, and it is worth saying what it does *not* need: no containment
relation, no ancestor to resolve against, no inheritance. Two resources sharing a policy are not
parent and child — they are two things the same rule is about.

That is what the shape above demonstrates rather than asserts. Every other block in these files is
parsed alone; a `policy` block is merged into all of them, so the two resources resolve against one
artifact. Change the matcher and both answers change; delete the block and both cases fail. Two
copies that happen to agree would prove neither.

## The memo, granted to one person

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/memo> ;
  acp:accessControl [ acp:apply <#memoRead> ]
] .

<#memoRead>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ; acp:agent <https://acme.example/people/greg#me> ] .
```

```turtle context
[
  acp:target <https://acme.example/memo> ;
  acp:agent  <https://acme.example/people/greg#me> ;
  acp:owner  <https://acme.example/pod/owner#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

Greg is named on the memo and nowhere else — not on the space. **Read on its own, this policy says he
may read the memo. He may not**, because the space decides first and does not admit him, and the pod
grants what both allow.

Which is a claim, so it is a case:

```turtle decision
[
  acp:target <https://acme.example/pod/_system/contexts/spaces/engineering> ;
  acp:agent  <https://acme.example/people/greg#me> ;
  acp:owner  <https://acme.example/pod/owner#me>
] .

[
  acp:target <https://acme.example/memo> ;
  acp:agent  <https://acme.example/people/greg#me> ;
  acp:owner  <https://acme.example/pod/owner#me>
] .
```

```turtle grant
# nothing
```

Add Greg to the space policy and this case fails, which is the point of writing it down: the sentence
above stops being true the moment somebody widens the space, and now something notices.

An implementation offering this composition would need to preserve it across query strategies. A deployment can arrive at the same answer by pruning the data a
query sees, and get it right — but then the policy alone tells a reader something that is not true,
and nothing written down says otherwise.

## The draft, granted to nobody

Somebody started sharing this and stopped. The policy confers `acl:Read` and names no condition at
all.

```turtle acr-resource
[
  a acp:AccessControlResource ;
  acp:resource <https://acme.example/draft> ;
  acp:accessControl [ acp:apply <#draftRead> ]
] .

<#draftRead>
  a acp:Policy ;
  acp:allow acl:Read .
```

```turtle context
[
  acp:target <https://acme.example/draft> ;
  acp:agent  <https://acme.example/people/carol#me> ;
  acp:owner  <https://acme.example/pod/owner#me>
] .
```

```turtle grant
# nothing
```

An unfinished grant confers nothing rather than everything. That is ACP's own rule and not a
precaution somebody remembered to add: a policy is satisfied only if it references at least one
matcher through `acp:allOf` or `acp:anyOf`, and a matcher is satisfied only if it defines at least
one attribute. An empty requirement is never vacuously true, at either level.

It is the kind of rule a permission model tends to discover the hard way, and worth checking for in
one that has not adopted ACP: the same document with `authz:grants Read` and no requirements has to
be made to fail closed on purpose.

## Implementing these decisions

The [implementation proposal](../docs/proposals/authorization-implementation/authorization-state.md#computing-a-sandbox)
compares query guards, restricted datasets and pre-fetching readable areas. It also records why
positive policy algebra alone does not make reverse enumeration exact. These are design options;
this scenario executes neither queries nor a reverse index.
