# Worked examples

Scenarios that show what the access-control model does, in cases rather than in argument. They are
the readable half of [`docs/concepts/access-control.md`](../docs/concepts/access-control.md), which
carries the reasoning and the trade-offs.

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

A `context` pairs with the next `grant` below it. Its `acp:target` selects the `acr` whose
`acp:resource` matches. A `grant` block containing only a comment means nothing is granted, which is
an ordinary outcome and the answer several scenarios turn on.

`acp:` and `acl:` prefixes are supplied by the runner, so a scenario does not open with lines a
reader already knows. Each block is parsed under a base of its own, so `<#owner>` in one block never
collides with `<#owner>` in another.

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
