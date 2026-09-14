# An audience the pod already knows

Proposed audience-source design and illustrative ACP alternatives. The authority declaration and
revalidation conditions are unresolved design, not implemented safeguards. The runner checks static
policy and unknown-extension behavior; it executes neither lookup nor regeneration. See the
[fixture assumptions](../docs/guides/acp-fixtures.md).

Anna keeps her address book in a contacts app she likes, and it syncs into her pod. She has tagged
some people *Family*. She would like the family context to be readable by exactly those people —
and to stay that way when she tags somebody new in the app she actually uses, without opening a
permissions screen at all.

That is a good feature and it is reachable two ways. Which one is right depends on something that
sounds unrelated: **how big the audience is and how often it changes.**

## The contacts, and what declaring them costs

```turtle aside
# {pod}/_system/contexts/contacts — an ordinary context, written by the sync and read-only to
# everybody else. Shown here, not evaluated.
<https://anna.example/contacts/ben>   <https://anna.example/ns/keyword> "Family" ;
                                      <https://anna.example/ns/webid>   <https://ben.example/profile#me> .
<https://anna.example/contacts/clara> <https://anna.example/ns/keyword> "Family" ;
                                      <https://anna.example/ns/webid>   <https://clara.example/profile#me> .
<https://anna.example/contacts/dora>  <https://anna.example/ns/keyword> "Book club" ;
                                      <https://anna.example/ns/webid>   <https://dora.example/profile#me> .
```

Reading an audience out of this makes the contacts **authorization state**. Writing a contact then
grants access, which is the thing a trust boundary exists to prevent — so the pod has to declare that
this context is an authority, and the declaring is the safeguard rather than a formality.

Be clear about what that costs. The proposal aims to ensure that authorization facts are read
only from stores no data write can reach, and this is the declared exception to it: the graph below
*is* reachable by a write. What stays topological is the declaration, which lives in control-plane
state; what the exception buys is membership only, never policy. Whether to keep it is an open
decision rather than a settled part of the model.

The proposed safety condition, which the fixture does not verify:

> A context may serve as a principal-set authority exactly when **every agent and client pair whose
> writes are still in it held at least `manage` on everything it now grants, by an authority that did
> not depend on those writes**.

The pair, not the person, and that is the part that is easy to get wrong. The contacts are written by
a sync, and a sync is an application acting as Anna — a grant is resolved from the verified client
together with the verified subject
([`SPS-GRANT-002`](../spec/core/grants.md#SPS-GRANT-002)). Anna holds `manage` on the family context;
the sync need only hold `write` on contacts. Stated over Anna alone the condition looks satisfied
while a compromised sync tags an attacker *Family* and grants access **outside its own delegation
ceiling** — the ceiling stops it writing the policy and this route lets it write the answer instead.

So the address book is an authority only where the sync is control-plane code rather than a delegated
application, or where its delegation covers `manage` on every context the contacts govern. Anything
else and the pod has moved the boundary without moving the policy.

It would also stop holding the moment Anna shared the address book for writing — a friend adding
themselves as *Family* would be granting themselves access, through a route nobody would think to
audit. Same rule, the case that is easier to see.

And note *still in it*, which is doing work. A tag outlives the permission that wrote it. Anna
uninstalls the sync, the entries it made stay, and a later policy points at *Family* from something
the sync never touched — nobody who may write the contacts today is short of anything, and the
condition reads as satisfied over an entry made by an application that is gone. Which is why the
moments to check are revocation and a new reference, rather than the write.

## The way that stays plain ACP: expand when the policy is written

The pod offers *"everyone tagged Family"* as a choice, and turns it into a policy:

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://anna.example/_system/contexts/family> ;
  acp:accessControl [ acp:apply <#familyRead> ]
] .

<#familyRead>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ;
              acp:agent <https://ben.example/profile#me>,
                        <https://clara.example/profile#me> ] .
```

```turtle context
[
  acp:target <https://anna.example/_system/contexts/family> ;
  acp:agent  <https://ben.example/profile#me> ;
  acp:owner  <https://anna.example/profile#me>
] .
```

```turtle grant
[] acp:grant acl:Read .
```

```turtle context
[
  acp:target <https://anna.example/_system/contexts/family> ;
  acp:agent  <https://dora.example/profile#me> ;
  acp:owner  <https://anna.example/profile#me>
] .
```

```turtle grant
# nothing
```

No extension, no authority consulted at request time, nothing a foreign ACP engine could fail to
resolve. Tagging somebody in the contacts app regenerates this one policy, and the regeneration is
what has to be prompt — between the tag and the rewrite, the answer is stale.

Expansion costs depend on the number of distinct policy artifacts that contain the member list.
Shared policies can reduce that number; five hundred referring documents need not require five
hundred rewrites. For this one-context example the expansion is one policy with thirty relatives.
The fixture does not benchmark either strategy or test propagation after a change.

## The way that stays live: resolve when the request arrives

Regeneration is a moment where things can be missed — a failed sync, an app that writes overnight, a
tag changed while a job was down. A pod can instead leave the question open until it is asked:

```turtle acr
[
  a acp:AccessControlResource ;
  acp:resource <https://anna.example/_system/contexts/family-live> ;
  acp:accessControl [ acp:apply <#familyLiveRead> ]
] .

<#familyLiveRead>
  a acp:Policy ;
  acp:allow acl:Read ;
  acp:anyOf [ a acp:Matcher ;
              <https://anna.example/ns/contactKeyword> "Family" ] .
```

```turtle context
[
  acp:target <https://anna.example/_system/contexts/family-live> ;
  acp:agent  <https://ben.example/profile#me> ;
  acp:owner  <https://anna.example/profile#me>
] .
```

```turtle grant
# nothing — see below
```

Ben **is** tagged *Family*, and a pod implementing this relation grants him `acl:Read`. The
expectation is empty because a plain ACP engine does not know `ex:contactKeyword`, so the matcher
carries none of ACP's four attributes and is never satisfied. The relation is named in Anna's own
namespace rather than sempods', for the same reason the group example gives: whether sempods
publishes such a relation, and its IRI, remain open decisions, and the namespace does not take names
back.

Which is the same boundary the enterprise scenario runs into, reached from the opposite direction: no
organisation, no directory, no group service — just an address book — and the moment the answer is
looked up rather than written down, the policy stops being portable.

Note what the policy does **not** contain: the query. It names a relation the pod defines
(`contactKeyword`) and a value Anna chose (`"Family"`). How the pod answers it — which context it
reads, which predicate it follows — is not written here, and must not be. A policy that carried its
own query would be evaluated with more authority than whoever wrote it has, and its answer read off
the response would be an oracle over data that person cannot see.

## Choosing between them

| | expand when written | resolve when asked |
|---|---|---|
| **Portable ACP** | yes | no |
| **Staleness** | until regeneration completes | depends on source freshness and request consistency |
| **Cost of a change** | regenerate affected policy artifacts | update authority; no policy rewrite |
| **Scales with** | how many policies name the set | how often the pod is read |

The first is a plausible choice for the small static example. Larger or frequently changing sets
may favor live resolution, subject to the unresolved authority and freshness conditions above.
Both can present the same audience choice to the person; these fixtures do not choose a required
mechanism for implementations.
