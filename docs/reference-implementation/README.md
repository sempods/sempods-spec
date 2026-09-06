# The reference implementation, documented here for now

The specification says what a pod decides. It never says how, and
[`../vision.md`](../vision.md) states why: two pods that answer every request alike are equally
conformant, whether one evaluates a policy language and the other has the rules in its code.

That leaves a real design with no obvious home. While this text can still move
([`../../GOVERNANCE.md`](../../GOVERNANCE.md)) the two are worked out together, and separating the
documents would hide the seam that matters: whether a design can actually deliver the behaviour the
contract asks for.

So the design lives here, one directory, clearly marked. **At `0.1` it moves to the implementation
repository**, and nothing under [`../../spec/`](../../spec/README.md) moves with it.

| | |
|---|---|
| [`acp-profile.md`](acp-profile.md) | Expressing every deployment in one small ACP profile: the primitive, what the profile excludes and why, what is guaranteed against what rests on convention, matchers for groups and audiences, and where policy lives |
| [`authorization-state.md`](authorization-state.md) | Where that state is actually held and what it costs to answer from it: native storage with ACP as a projection, what a read renders and a write accepts, service clients as ordinary rows, the sandbox before a query, and audience resolution |

Read a document here as **SOLL for the implementation**, never as a requirement. Nothing in it has a
requirement ID, and that is not an oversight.
