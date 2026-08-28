# The sempods vocabulary

sempods publishes RDF terms under one namespace:

```
https://schema.sempods.org/        prefix: sps:
```

This document states who may mint terms there, what stability implementers can
rely on, and how a term gets added. It matters more than it looks: RDF terms
end up inside other people's stored data. A term that changes meaning breaks
data that was written years earlier, in systems the project never sees.

## Scope

The namespace holds terms that are **specific to sempods** and have no
established equivalent elsewhere — retrieval metadata, control-plane concepts,
conformance markers.

It deliberately holds as little as possible. Where a standard vocabulary
already says the thing, sempods uses the standard vocabulary and does not mint
a synonym:

| Purpose | Vocabulary used |
|---|---|
| General content semantics | `https://schema.org/` |
| RDF / RDFS / OWL primitives | the W3C namespaces |
| Hypermedia affordances | `http://www.w3.org/ns/hydra/core#` |
| Shapes and validation | `http://www.w3.org/ns/shacl#` |
| Provenance | `http://www.w3.org/ns/prov#` |

A term is only minted here when the alternative would be to misuse an existing
one.

## Stability guarantees

For every term published in this namespace:

1. **The IRI never changes.** URIs are permanent identifiers. A term is not
   moved, renamed or re-cased after publication.
2. **The meaning never narrows.** A term's definition may be clarified or
   extended, never redefined in a way that makes previously valid data wrong.
3. **Terms are deprecated, not deleted.** A retired term is marked
   `owl:deprecated true`, keeps resolving, and names its successor via
   `rdfs:seeAlso`. It stays in the published vocabulary document
   indefinitely.
4. **Deprecation is announced at least 12 months** before a term is removed
   from the recommended set, via the vocabulary document and the release
   notes.

The namespace IRI itself is **not versioned**. Versioning lives in the
vocabulary *document* (`dcterms:hasVersion`), not in the identifiers — a
versioned namespace would mean every schema revision invalidates stored data,
which is the outcome these guarantees exist to prevent.

## What is in it today

Three terms, defining the metadata a `find` response **may** carry about each hit:

| Term | |
|---|---|
| `sps:FindResult` | the per-hit metadata node |
| `sps:findResult` | links a matched resource to that node |
| `sps:engine` | which search engine produced the hit |

The excerpt and the rank on that node are `schema:text` and `schema:position` —
schema.org terms, reused rather than duplicated here.

**No implementation emits them yet**, including the reference implementation.
[`SPS-FIND-022`](../spec/core/find.md#SPS-FIND-022) makes them optional and
transient for that reason, and [`SPS-FIND-018`](../spec/core/find.md#SPS-FIND-018)
is what the contract actually is today: a flat graph, with no ordering and no
score.

They are published anyway, and that is a deliberate choice rather than an
oversight. The alternative is that the first implementation to want per-hit
metadata mints its own terms for it, a second one mints different terms, and the
idea has two vocabularies before it has one implementation. Publishing the names
first costs nothing that the stability guarantees above do not already cover.

The definitions live in [`sempods.ttl`](sempods.ttl).

## Dereferencing

`https://schema.sempods.org/` resolves. It negotiates on `Accept` and redirects
with 303 — the namespace IRI names a vocabulary, not a document, and 303 is what
says "here is a document about it instead":

| asked for | reaches |
|---|---|
| `text/turtle` | [`sempods.ttl`](sempods.ttl) as published by this site |
| a browser, or no preference | this page |

A term IRI is a slash away from the namespace and answers the same way, because a
term resolves to its definition *within* the document rather than to one of its
own.

**JSON-LD is not served.** An explicit request for it gets a 406 rather than a
page it cannot parse. Publishing one means generating it from the Turtle, which
this repository's build does not do yet.

The file here stays the source. What the namespace serves is this repository's
`main`, so an IRI cited from a tag resolves to the current document rather than
the one that tag carried — cite the file where that distinction matters.

## Third parties: mint in your own namespace

If you implement sempods and need a term the vocabulary does not have, define
it under a namespace **you control** — for example
`https://example.com/ns/yourfeature#`. Do not mint terms under
`https://schema.sempods.org/`.

This is not territorial. It is the only way either side stays safe:

* Your data keeps working regardless of what this project decides, because
  nobody else governs your identifiers.
* Readers of your data can tell which parts are the standard and which are
  yours.
* The project cannot accidentally redefine a term you depend on, because it
  never had the term.

Terms minted by a third party under this namespace carry no guarantee from this
project and may collide with a later official term of the same name — which is
the concrete failure this rule prevents.

## Proposing a term

Extensions that prove useful in practice are exactly how a vocabulary should
grow. If a term you defined in your own namespace turns out to be generally
useful:

1. Open an issue in this repository describing the term, its domain and range,
   and the data you already write with it. It is a specification change, so
   [`../GOVERNANCE.md`](../GOVERNANCE.md) applies: it needs a written rationale.
2. If it is adopted, it is minted here, and your original term is documented
   as an alias via `owl:equivalentProperty` / `owl:equivalentClass` so existing
   data keeps validating.
3. Nothing you already wrote has to be rewritten. Both IRIs resolve, both stay
   valid.

Adoption favours terms with running implementations over terms with good
arguments. The three terms above are the exception that shows the rule's edge:
they were minted to reserve a name rather than to describe running behaviour, and
they are marked as not-yet-emitted precisely because that is unusual here.

## Licence

The vocabulary document and these definitions are licensed **CC BY 4.0**,
consistent with the rest of the project's documentation. Using the terms in
your data requires no licence, no attribution and no permission — that is what
a vocabulary is for.
