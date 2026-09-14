# Vision

A **pod** is one person's or one organisation's own store of linked data. sempods defines the
contract that lets applications, agents and other pods use it without knowing who built it.
This informative vision owns the direction and the test for selecting requirements. The
[normative chapters](../spec/README.md) own the current contract.

## The guiding image

> **A sempod is an RDF graph with query support, authorized per caller.**

RDF supplies the data model. Query support lets a caller ask questions about that data. The pod
authorizes each request using the caller's identity and authority, and protects data the caller
cannot access. Applications are guests in a store the person or organisation controls.

The same contract should be practical for a small embedded store and a larger hosted service.
Storage layout, policy representation and deployment architecture can differ without changing
what a client can rely on.

## What belongs in the contract

sempods is a framework composing existing standards. Name and reference those standards; add only
the interoperability choices and security guarantees needed to make them work together as a pod.
Apply this test to a proposed obligation, including one inherited through a standards reference:

- **What needs agreement?** Identify the client-visible ambiguity or security failure that would
  remain without the obligation. If the selected standard already supplies the answer, reference it.
- **Why this scope?** Core contains what every implementation needs for the authorized RDF and query
  contract. An additional client-facing capability can be an optional, discoverable module when
  clients need an interoperable contract for it. An application feature or internal mechanism does
  not acquire a specification chapter merely because it is useful.
- **What must be observable?** Specify the operation's effect, authorization boundary or failure
  outcome. Leave storage, algorithms, internal services and administrative interfaces to an
  implementation unless a concrete interoperability or security need requires agreement there.
- **Can different implementations satisfy it?** Use concrete allowed and denied cases to check the
  intended contract. A design preference or a reference implementation's existing behavior is
  insufficient reason to impose an obligation on every pod.

[Spec authoring](agents/spec-authoring.md) applies this test when selecting and identifying a
standards profile or writing a requirement. [Governance](../GOVERNANCE.md#how-a-change-is-made)
controls adoption; this vision does not adopt or override a protocol requirement.

## The current contract and proposed changes

The current core uses Contexts as its authorization boundary, per-Context grants and explicit
Context selection on writes. Only the Context lifecycle HTTP surface is optional. The
[chapter map](../spec/README.md#core) identifies the current core and modules.

[Authorized data access](proposals/data-access.md) proposes a smaller core with an optional Context
contract. Its adoption is tracked in [#68](https://github.com/sempods/sempods-spec/issues/68).
That proposal remains distinct from both this selection test and the requirements in force.
