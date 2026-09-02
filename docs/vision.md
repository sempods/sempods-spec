# Vision

A **pod** is one person's or one organisation's own store of linked data. What sempods adds is the
contract such a store implements, so that an application, an agent or another pod can work with it
without knowing who built it. The specification says what that contract *is*. This document says what
it is **shaped like** — and the shape is what decides whether a proposed requirement belongs in it.

## The guiding image

> **A sempod is an RDF graph with query support, authorized per caller.**

Four words carry it. *RDF graph*: the data model is not ours and is not negotiable. *Query support*:
a caller asks questions, rather than being handed a directory to walk. *Per caller*: the same
question from two identities is two different questions, and the pod — not the client — decides the
difference.

That is a higher floor than the web's, and the difference is worth naming rather than regretting. A
web server can serve files with no notion of who is asking, because the early web was public by
default. Logins arrived without a standard and the silos followed. A pod is private by default and
federated identity is part of the contract from the start, which is exactly the thing the web never
fixed.

## The comparison that fits

Not a web server. **SQL.**

A small, standard query contract; implementations from an embedded single file to a distributed
cluster; and clients that work against all of them without caring which. SQLite and a large database
server share almost no code and interoperate completely, because what they share is the contract and
not the construction.

That is the range sempods is for. The small end is an embedded store, one context, one owner, the
sharing surface present and unused — buildable in an afternoon over an off-the-shelf triple store.
The large end replaces the store entirely and keeps the contract. Neither is more of a sempod than
the other, and a client cannot tell them apart, which is the point.

## What belongs in the contract

The guiding image is only useful if it decides things, so it is written as a test:

> A requirement belongs in **core** when the contract does not hold without it. Everything a client
> could build for itself belongs in a **module**, and is announced at the conformance endpoint so a
> client knows before it asks.

Applied, it gives the shape the specification already has: linked data over HTTP, one context per
statement, server-resolved grants, sandboxed reads and writes, query, and federated authentication
are core, because a client cannot supply any of them. Media, agent tooling and the OIDC provider are
modules.

It also decides what the specification does **not** say. The contract describes **what is decided**,
never **how**. Two pods that answer every request alike are equally conformant, whether one
evaluates a policy language and the other has the rules in its code. A permission model is therefore
an implementation's design, and appears here only where a client would otherwise be unable to rely
on something — in which case it is behaviour, and gets written as behaviour.

## Where this is going

The direction is the old promise of the web, for knowledge rather than for pages: data that is
linked, queryable and owned by the person or organisation it is about, with applications as guests
that ask permission. Adoption of a contract is a numbers game, and numbers come from a low floor. So
the specification grows by *deciding* more, not by *requiring* more — and every requirement it does
not need is one an implementation does not have to meet.
