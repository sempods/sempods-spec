# Reading the ACP fixtures

This informative guide describes the repository's [example fixtures](../../examples/README.md) and
[runner](../../.github/scripts/check-examples.py). It explains their supplied model and its limits,
not a deployed implementation. Current-contract references below describe revision
[`3f5cfa7`](https://github.com/sempods/sempods-spec/tree/3f5cfa7958dc21b100437b032d4e3b76b2cca446).
The [access-control proposal](../proposals/access-control.md) remains non-normative.

## What is supplied and what is checked

Each case supplies policy, request facts and expected modes. The runner resolves that supplied
policy using its transcription of [ACP §6](https://solidproject.org/TR/2022/acp-20220518#access-control-resolution),
and checks the expectation. Composed cases additionally exercise the runner's stated combination
rules. Identity verification, policy installation, HTTP requests, storage, query rewriting and
revocation transitions are outside this test.

An ACP access context describes an attempted request; it is not a sempods Context. The fixtures
supply agent, client, target and any owner or creator facts. A real implementation would have to
establish those facts from trusted inputs. A green fixture does not establish their authenticity.

## Policy assumptions

Read [ACP 0.9.0](https://solidproject.org/TR/2022/acp-20220518) for its vocabulary and resolution algorithm. The useful
boundary here is how the fixtures use it:

- Allow policies can add alternative ways to obtain a mode. Adding a client-constrained allow
  policy beside an unrestricted one does not constrain the latter; example 50 preserves this
  counterexample. Restriction needs a separate ceiling or a changed policy set.
- A policy's native ACP attributes and an unknown extension stay in separate matchers. A native
  engine could otherwise ignore the unknown conjunct and grant more. With separate `allOf`
  matchers an extension-only matcher remains unsatisfied. Examples 40 and 45 deliberately expect
  empty grants from the plain engine; they do not execute principal-set membership resolution.
- Modes are written explicitly. ACP supplies no sempods mode implication. The fixtures write
  `Read` beside `Write` to illustrate
  [`SPS-GRANT-009`](../../spec/core/grants.md#SPS-GRANT-009). Their resource `Control` bundle is a
  proposed mapping; the broader Context `manage` mode and its descendant coverage are not tested.
- Ordinary fixtures use a positive, non-inheriting shape. This is a fixture profile, not a sempods
  ACP requirement. The evaluator handles ACP negative constructs in its algorithm; the guards
  constrain what ordinary scenarios may contain.

## Owner, creator and targets

[`SPS-GRANT-011`](../../spec/core/grants.md#SPS-GRANT-011) specifies the owner's implicit authority.
A bare ACR with no owner policy cannot demonstrate that server-supplied authority. Example 60
explicitly supplies an owner policy and owner fact to compare relational matchers. It also compares
an absent creator fact with an explicitly supplied one. sempods specifies no general creator
attribute for RDF subjects; the example does not deny that an application can define one.

A `holds` block supplies where a subject's statements are placed. The runner cannot derive that
placement from policy. Separate context and resource policies can target the same IRI, so the key is
**decision kind and target IRI**. Example 35 would conflate independent restrictions if keyed only
by IRI. That model choice is not a specified ACR storage or discovery API.

## Composition and delegation

A composed fixture intersects one context decision with any resource decision and delegation
ceiling supplied for that request. It adds the model's public branch separately. Each ACP evaluation
is distinct from this composition. The proposed resource restriction neither defines nor advertises
a `resource` module; the current contract makes Context the permission boundary.

Example 50's ceiling is a mode bound targeted at a principal. It does not represent the current
per-Context delegation scope or settle a future target-selection contract. Its public branch has no
OAuth scope validation. The current `public-read` profile remains in
[`SPS-AUTH-042`](../../spec/core/auth.md#SPS-AUTH-042)–
[`SPS-AUTH-044`](../../spec/core/auth.md#SPS-AUTH-044); the fixture is not evidence about those flows.

Example 55 supplies registered service grants and a service marker. The current service-client
identity and registration requirements are cited in that example. Replacing the person/context
branch with those supplied grants, while retaining a resource restriction, is this model's chosen
representation rather than a specified ACP integration.

## Assumptions beyond policy evaluation

Examples 40 and 45 discuss trusted audience sources, membership freshness and safe policy editing.
Their `aside` graphs and SPARQL snippets are explanatory inputs, not an executed resolver or safety
check. The [implementation proposal](../proposals/authorization-implementation/acp-profile.md)
retains those open mechanisms, including shared-policy authority and revalidation of retained writes.

Example 70 compares supplied end states for reader resharing. It tests no grant-writing operation,
provenance tracking or revocation sweep. The
[peer-manage alternative](../proposals/access-control.md#who-may-share-and-why-there-is-no-chain)
is proposed; no interpersonal sharing API is specified.

Future-contract validation and any changed cases belong to
[#72](https://github.com/sempods/sempods-spec/issues/72). [Repository checks](repository-checks.md)
owns execution commands and check boundaries.
