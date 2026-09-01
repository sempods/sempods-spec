# Worked examples

Scenarios that show what the access-control model does, in cases rather than in argument. They are
the readable half of [`docs/concepts/access-control.md`](../docs/concepts/access-control.md), which
carries the reasoning and the trade-offs.

**Read the first three in order.** They are the model, and each adds exactly one thing to the one
before:

| | |
|---|---|
| [`10-one-context.md`](10-one-context.md) | a pod with one place to put things — the whole model at its smallest |
| [`20-several-contexts.md`](20-several-contexts.md) | areas to choose between, one of them public. The shape most pods have |
| [`30-spaces-and-documents.md`](30-spaces-and-documents.md) | a space whose documents are not all for the same readers, so a second decision narrows inside it |
| [`40-groups-and-shared-policy.md`](40-groups-and-shared-policy.md) | the same shape at enterprise scale: an audience that is a group, one policy governing several resources, and the one place sempods adds a matcher ACP does not have |
| [`45-audiences-from-pod-data.md`](45-audiences-from-pod-data.md) | the same wish on a personal pod — "everyone tagged Family" — and why the answer there is the mechanism the enterprise case cannot use |

The rest answer a question somebody asked rather than showing the model, and are worth reading when
that question comes up:

| | |
|---|---|
| [`50-delegation.md`](50-delegation.md) | why an application is not the person acting through it, and where the ceiling leaks |
| [`60-creator.md`](60-creator.md) | why `acp:CreatorAgent` cannot match here, and what is done instead |
| [`70-resharing.md`](70-resharing.md) | an open design question: may a reader pass access on, and what a sweep would cost |

**They are fixtures, not prose about the contract.** A friendlier second description of a
specification is the copy that goes wrong and is believed anyway, which is why this repository
refuses one everywhere else. These are exempt because they are executable: every scenario is run
through ACP's own resolution algorithm, and one that stops being true fails the build.

```bash
.github/scripts/check-examples.py
```

## What a scenario looks like

Markdown, with fenced `turtle` blocks carrying a kind in the info string:

| Block | Holds |
|---|---|
| `acr` | an authorization graph — one per resource it controls, several per file where a scenario turns on a contrast |
| `context` | one attempted access, as the server would describe it |
| `grant` | the access modes that attempt must be granted |
| `policy` | one policy artifact several `acr` blocks reference. Merged into every `acr` in the file, so a scenario claiming two resources share a policy demonstrates it rather than writing two copies that agree |
| `aside` | Turtle a scenario shows without the runner evaluating it — an identity authority's membership facts, for instance, which are not ACP. Parsed, so a malformed one still fails; it takes no part in a case |

A `context` pairs with the next `grant` below it. Its `acp:target` selects the `acr` whose
`acp:resource` matches. A `grant` block containing only a comment means nothing is granted, which is
an ordinary outcome and the answer several scenarios turn on.

`acp:` and `acl:` prefixes are supplied by the runner, so a scenario does not open with lines a
reader already knows. Each block is parsed under a base of its own, so `<#owner>` in one block never
collides with `<#owner>` in another.

## Where these live

No scenario says where its access control resource is stored, and that is deliberate: the address is
an implementation's own business. The boundary around it is not.

An access control resource is **not data**. It is not a context, does not appear in context
discovery, cannot be selected with `?context=`, and is unreachable through LOD CRUD or SPARQL — which
is what stops a caller writing a triple that looks like a policy and having it read back as one. A
client reaches it through the `Link` header ACP requires of a controlled resource, and never by
constructing a path, the same way it never constructs a context IRI
([`SPS-CTX-023`](../spec/core/contexts.md#SPS-CTX-023)).

The structural half — that policy is indexed by the target it controls rather than by the context
that happens to hold that target's statements — is in
[`docs/concepts/access-control.md`](../docs/concepts/access-control.md) §"Policy location and control
plane", with the three reasons it has that shape.

## Why the runner is a plain ACP engine

`check-examples.py` transcribes the pseudocode of ACP §6.1 through §6.5 and knows nothing about
sempods. That is deliberate. The concept claims sempods access control resources are *pure* ACP —
that an independent engine, given one of them and a context graph, produces the same access grant
graph. A runner that shared sempods' reading of the vocabulary could not test that claim; this one
can, and every green run is evidence for it.

Two consequences are worth expecting rather than being surprised by.

**Mode implications must be written out.** `manage` implies `write` implies `read`
([`SPS-GRANT-009`](../spec/core/grants.md#SPS-GRANT-009)), and ACP has no such rule — so a policy
that states only `acl:Control` grants only `acl:Control` here. The implication belongs in the policy
when it is written, not in the engine when it runs.

**An attribute ACP does not define leaves its matcher unsatisfied.** A matcher carrying only a
sempods principal set has none of ACP's four attributes, and ACP's rule is that such a matcher is
never satisfied. The runner reports it as a note and the scenario's expectation has to reflect it.
That is not a defect to work around — it is the portability boundary, and a scenario is the honest
place to see it.

## Adding one

Keep the story first and short: who wants what, and why the answer is what it is. Cite a requirement
where it explains something, not as a footnote on every clause — the runner checks that every
`SPS-…` a scenario names is one a chapter actually defines.

Prefer several small cases over one large one. Two cases that end in "nothing" for different reasons
teach more than one that ends in a long list.

## Dependency

The runner needs [rdflib](https://rdflib.readthedocs.io/) to parse Turtle:

```bash
python3 -m pip install rdflib==7.6.0
```

CI installs the same pinned version and runs the scenarios on every pull request
([`.github/workflows/examples.yml`](../.github/workflows/examples.yml)). The pin is tighter than the
`pyyaml` the OpenAPI job installs because this dependency decides whether a scenario is *correct*:
a change in Turtle parsing would move results quietly rather than break loudly.

It is the specification's first RDF dependency outside `site/`, and it lives in the workflow step
rather than in a requirements file so that `site/` stays this repository's only dependency tree.
Hand-parsing the subset of Turtle these scenarios use was the alternative and was rejected: a
checker with a parser bug is worse than no checker, because it is believed.
