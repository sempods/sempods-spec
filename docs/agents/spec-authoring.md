# Procedure: write a normative statement

How a requirement is formed, identified, numbered and withdrawn. Read
[`documentation-strategy.md`](documentation-strategy.md) first — this applies its rules to the one
document type that only exists here, and does not restate them.

Required before writing or editing anything under `spec/`.

## 1. Decide whether it is a requirement at all

Most sentences in a chapter are not. Three questions, in order:

1. **Could an implementation get this wrong?** If the behaviour follows a standard the chapter has
   already declared it profiles, and follows it exactly, it needs no requirement — rule 4 of the
   strategy. Write the deviation, not the norm.
2. **Is it testable?** A requirement that no conformance test could ever fail is a wish. "The
   server SHOULD be fast" is not a requirement; "the server MUST answer `413` above the advertised
   body limit" is.
3. **Is it one statement?** Two obligations joined by "and" are two requirements. Bundling them
   means a conformance report can only say "failed" without saying which half.

If the answer to the first is no, the sentence belongs in the chapter as plain prose or in the
concept as reasoning. Prose is not second-class here; it is what makes the requirements readable.

## 2. Write it

RFC 2119 as clarified by RFC 8174: **only the uppercase forms are normative.** `MUST`, `MUST NOT`,
`REQUIRED`, `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, `RECOMMENDED`, `MAY`, `OPTIONAL`. A
lowercase "must" in this repository is ordinary English and binds nobody, which is exactly why the
distinction is worth keeping.

Choosing the level:

- **`MUST`** — an implementation that does otherwise is not a sempods implementation. Reserve it for
  interoperability and for security. Every one of the non-negotiable invariants in the root
  `AGENTS.md` is a `MUST`.
- **`SHOULD`** — there is a real reason an implementation might deviate, and the chapter says what
  it is. A `SHOULD` with no conceivable exception is a `MUST` that somebody was nervous about.
- **`MAY`** — genuinely free. Note that a `MAY` still needs a requirement ID whenever a client is
  entitled to *rely on either outcome*, because that is a testable statement about the client's
  obligations.

Subject and voice: name the actor. "The server MUST reject…", "A client MUST NOT assume…". A
requirement in the passive voice hides who is bound by it, and in a protocol with two sides that is
the ambiguity that costs an interoperability bug.

## 3. Give it an ID

```
SPS-<AREA>-<NNN>
```

`AREA` is one of the registered areas below. `NNN` is the next unused number in that area, zero
padded to three digits, allocated in order of first appearance. Numbers are **never reused**, so the
next number is one above the highest that has *ever* existed in the area, withdrawn ones included.

Registered areas:

| Area | Chapter | Part of |
|---|---|---|
| `CORE` | conformance, addressing, discovery, the error model | core |
| `CTX` | contexts | core |
| `GRANT` | grants | core |
| `AUTH` | authorization and client identity | core |
| `CRUD` | LOD and system CRUD | core |
| `SPARQL` | the query surface | core |
| `FIND` | retrieval | core |
| `OIDC` | the OIDC bridge | module |
| `MEDIA` | pod-owned binaries | module |
| `MCP` | the MCP surface | module |

Adding an area is a change to this table and to the chapter map in
[`../../spec/README.md`](../../spec/README.md), in the same commit. Splitting an existing area is
not allowed: the IDs already issued under it would have to move, and they cannot.

### The written form

A requirement is one paragraph, opened by its ID in bold code, preceded by an explicit HTML anchor:

```markdown
<a id="SPS-CRUD-011"></a>
**`SPS-CRUD-011`** — A write request MUST name exactly one context, as a `?context=` query
parameter carrying the context's full IRI. A request that names none, or more than one, MUST be
rejected with `400`.
```

Two conventions, both load-bearing:

- **The anchor.** Heading anchors drift when heading text is edited; an explicit `id` does not, and
  it is what makes `lod-crud.md#SPS-CRUD-011` a permanent address.
- **The opening.** The ID is the first thing in the paragraph, in that exact shape. That is what
  makes the requirement index generable from the text rather than maintained beside it — and an
  index maintained beside the text is an index that is wrong.

## 4. Module requirements are conditional

A requirement in a module area binds only an implementation that **advertises** that module at the
conformance discovery endpoint. Write it as an ordinary requirement; do not hedge every sentence
with "if the media module is implemented". The chapter says once, at the top, that everything in it
is conditional on advertising the module.

What is *not* conditional: an implementation that advertises a module MUST satisfy all of it. There
is no partial module, for the same reason there is no partial core — a client that has to probe
which half it got is a client with no contract.

## 5. Withdraw, never delete

A requirement that is no longer wanted is **withdrawn**. Its ID stays out of circulation forever,
because it is cited in conformance suites, in implementation notes and in other people's test
reports.

```markdown
<a id="SPS-CRUD-007"></a>
**`SPS-CRUD-007`** — *Withdrawn in 0.3. Superseded by [`SPS-CRUD-019`](#SPS-CRUD-019).*
A write request MUST carry `Content-Type: application/ld+json`.
```

The original text stays, so a reader of an older conformance report can still find out what was
being claimed. Withdrawn requirements are not deleted at a later version either — this is the same
promise the vocabulary makes for RDF terms, and for the same reason.

A requirement whose *wording* is clarified without changing what it demands keeps its ID. A
requirement whose meaning narrows or widens gets a new ID and the old one is withdrawn. When in
doubt: if an implementation that passed before could now fail, it is a new ID.

## 6. Check

- The ID is new, and higher than every ID ever issued in its area.
- The anchor matches the ID exactly, character for character.
- The chapter declares which standards it profiles, and the requirement is not restating one of
  them.
- If the HTTP surface moved, the OpenAPI description moved with it in the same commit.
- The roadmap item is ticked.
- `lychee --offline --include-fragments --no-progress .` passes.

## Pitfalls

- **Do not write a requirement for the reference implementation's behaviour just because it is the
  behaviour.** While the specification is descriptive the implementation is the source, but the job
  is still to separate the contract from one implementation's choices. Storage layout, framework,
  error message wording, collection names: not the contract.
- **Do not let a requirement carry its own justification.** "The server MUST reject `SERVICE`,
  because federated queries are an SSRF surface" mixes the obligation with the argument, and a
  reader cannot tell whether the reason is also binding. The obligation goes in the chapter, the
  argument in `concepts/`.
- **Do not number by section.** `SPS-CRUD-3.2.1` breaks the first time a section moves, which is the
  failure the flat scheme exists to avoid.
- **Do not renumber to close a gap.** Gaps are free; renumbering is a silent break in every document
  that cites the old number.
