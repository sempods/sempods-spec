# Worked examples

These informative fixtures illustrate an ACP-based authorization model. They combine references to
the current specification, proposed behavior and counterexamples. The
[fixture guide](../docs/guides/acp-fixtures.md) explains the supplied assumptions and their sources;
the [access-control proposal](../docs/proposals/access-control.md) owns the proposed guarantees.
ACP is neither required nor established as implemented by these examples.

| Scenario | Status and purpose |
|---|---|
| [10: one context](10-one-context.md) | Illustrative ACP representation of specified Context selection and implicit owner authority |
| [20: several contexts](20-several-contexts.md) | Illustrative representation of specified grants, public reads and discovery |
| [30: spaces and documents](30-spaces-and-documents.md) | Proposed area/resource intersection; no resource module is specified |
| [35: subject equals context](35-subject-is-a-context.md) | Proposed two-decision model over the specified independence of subject and context |
| [40: groups and shared policies](40-groups-and-shared-policy.md) | Illustrative shared policies and unknown-extension counterexample; proposed trust and editing boundaries |
| [45: audiences from data](45-audiences-from-pod-data.md) | Proposed authority exception; static expansion and an unknown-extension case |
| [50: delegation](50-delegation.md) | Proposed composition and mode ceiling, preserving counterexamples and unresolved target scope |
| [55: service token](55-service-token.md) | Specified service identity represented in the proposed composition model |
| [60: creator](60-creator.md) | Supplied versus absent ACP request facts and direct-agent alternatives |
| [70: resharing](70-resharing.md) | Supplied end states illustrating the cost of reader resharing; peer-manage is only a proposal |

A successful run checks supplied fixture expectations. It does not adopt a proposal, validate every
sentence in a scenario, or establish HTTP behavior or conformance of a running pod. Future candidate
validation belongs to [#72](https://github.com/sempods/sempods-spec/issues/72).

## What a scenario looks like

Markdown, with fenced `turtle` blocks carrying a kind in the info string:

| Block | Holds |
|---|---|
| `acr` | an authorization graph — one per resource it controls, several per file where a scenario turns on a contrast |
| `context` | one attempted access, as the server would describe it |
| `grant` | the access modes that attempt must be granted |
| `acr-context`, `acr-resource`, `acr-delegation` | the same block, qualified. `acr-delegation` is the ceiling — how much of a person's authority an application received — and is named rather than inferred, because its target is the principal and an ordinary resource decision can be about the requester's own WebID too. Policy is keyed by the pair — which decision, and which IRI — because a subject IRI and a context IRI can be the same string with two separate decisions on it. Plain `acr` is the unqualified form, for the files where only one decision is in play. A `context` block naming an IRI that carries both is the subject-equals-context case and puts the request to each; naming it as one half of a larger `decision` is refused, because a half means one of the two and cannot say which |
| `policy` | one policy artifact several `acr` blocks reference. Merged into every `acr` in the file, so a scenario claiming two resources share a policy demonstrates it rather than writing two copies that agree |
| `decision` | one request put to the qualified ACRs. The runner intersects the applicable restrictions, then adds the model's public branch. OAuth scope and credential validation are not modeled; see the fixture guide. |
| `registered` | supplied service grants. A request uses `runner#serviceToken` and matching subject/client identities, illustrating [`SPS-AUTH-017`](../spec/core/auth.md#SPS-AUTH-017). In this model these grants replace the person/context branch; a resource restriction may still narrow them. |
| `holds` | which context a subject's statements are in, stated because nothing derives it — subject and context are independent by [`SPS-CRUD-011`](../spec/core/lod-crud.md#SPS-CRUD-011). A composed `decision` needs it: without it the context half could be any context at all, and a fixture could certify a read that never met the sandbox |
| `aside` | Turtle a scenario shows without the runner evaluating it — an identity authority's membership facts, for instance, which are not ACP. Parsed, so a malformed one still fails; it takes no part in a case |

Two rules about the files themselves, which is why this runner is a runner and not a Markdown
parser. **A fixture fence starts at column zero, with exactly three backticks, outside any block
quote, list or other fence, and an examples file holds no HTML comment.** These restrictions keep rendered and executed fixture blocks aligned.
**And a requirement is cited as an inline link**, `[SPS-…](chapter#SPS-…)`: a reference-style link
needs the same block structure to resolve, and the runner accepts inline citations only.

A `context` or `decision` pairs with the next `grant` below it. A composed `decision` carries the
dimensions the model has: exactly one context decision, and at most one resource decision and one
ceiling — so files with `decision` blocks qualify every `acr`, and plain `acr` stays for the files
where one decision is in play. Its `acp:target` selects the `acr` whose
`acp:resource` matches. A `grant` block containing only a comment means nothing is granted, which is
an ordinary outcome and the answer several scenarios turn on.

`acp:` and `acl:` prefixes are supplied by the runner, so a scenario does not open with lines a
reader already knows. Each block is parsed under a base of its own, so `<#owner>` in one block never
collides with `<#owner>` in another.

## Source and evaluation boundaries

The [fixture guide](../docs/guides/acp-fixtures.md) explains native ACP resolution, mode expansion,
unknown extensions and the composition performed outside that algorithm. Policy location and a
possible management/discovery surface remain an
[implementation proposal](../docs/proposals/authorization-implementation/acp-profile.md#policy-location-and-control-plane).
These fixtures do not specify ACR routes, link headers, a storage layout or a client discovery API.

## Adding one

Keep the story first and short: who wants what, and why the answer is what it is. State proposed and illustrative assumptions explicitly. Cite a requirement
where it explains something, not as a footnote on every clause — the runner checks that every
`SPS-…` a scenario names is one a chapter actually defines.

Prefer several small cases over one large one. Two cases that end in "nothing" for different reasons
teach more than one that ends in a long list.

## Dependency

The runner needs [rdflib](https://rdflib.readthedocs.io/) to parse Turtle:

```bash
python3 -m pip install rdflib==7.6.0 pyparsing==3.3.2
```

Both names, because pinning only the first leaves the parser stack resolving fresh on every machine
and a contributor can then be running a different one from CI. CI installs the same pinned version
and runs the scenarios on every pull request
([`.github/workflows/examples.yml`](../.github/workflows/examples.yml)). The pin is tighter than the
`pyyaml` the OpenAPI job installs because this dependency decides whether a scenario is *correct*:
a change in Turtle parsing would move results quietly rather than break loudly.

The pins live in the workflow step; `site/` remains the repository's only dependency tree.
