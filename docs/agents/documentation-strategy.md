# Documentation strategy

How writing is organised in this repository, and — more importantly — when something should **not**
be written at all. Read this before writing or editing any `*.md`, which here means before writing
anything.

## Document ownership

| Information | Canonical home |
|---|---|
| Normative contract | `spec/`, with `openapi/` and `vocabulary/`; [governance](../../GOVERNANCE.md#contract-sources) defines their roles |
| Requirement lookup | Generated `requirements.json` |
| Direction and requirement selection | [docs/vision.md](../vision.md) |
| Substantial proposed changes | [docs/proposals/](../proposals/README.md), explicitly non-normative |
| Maintained informative explanations | `docs/guides/`, stating the specification version/revision or repository inputs they describe |
| Tasks, decisions, dependencies and progress | GitHub issues and their native relationships |
| Decision, adoption and publication rules | [GOVERNANCE.md](../../GOVERNANCE.md) |
| Published changes | GitHub Release notes, pinned to tag and commit under governance; no parallel maintained changelog |

Alongside the vision, informative documents are **proposals** or **maintained guides**. “Concept”
may name a topic; it is not a separate lifecycle. Instructions under `docs/agents/` govern work
and link to its subject documentation. Write at the narrowest scope that owns the subject, and
make every document reachable through an `AGENTS.md` pointer.

A proposal states its owning issue, non-normative status and disposition: proposed, adopted,
partly adopted, rejected or superseded. Link discussion and adoption PRs; for partial adoption,
identify the adopted scope and the issue owning the remainder. A merged proposal records design;
[governance](../../GOVERNANCE.md#how-a-change-is-made) determines normative adoption and publication.
After disposition, retain links and reduce redundant detail once useful explanation and required
evidence have a maintained owner. A guide earns its place by explaining something useful beyond
the contract and its referenced standards; do not create a replacement merely to preserve a file.

Implementation architecture, delivery, releases and implementation-specific conformance reports
belong with the implementation. “Implemented” and “verified against an implementation” are not
specification lifecycle states. Informative examples and pseudocode can illustrate a possible
realization without prescribing it or asserting it exists. The
[repository-checks guide](../guides/repository-checks.md) owns the boundaries of repository evidence.

## The writing rules

These rules apply to specification prose, informative documents, docstrings and code comments.
Normative statements also follow [spec authoring](spec-authoring.md).

**1. Normative text is prescriptive.** Proposals state proposed behavior; maintained guides explain
the revision they reference. Keep proposed and current claims distinct, including in retained
implementation proposal support. An implementation's behavior does not establish the contract.

**2. Apply the canonical selection test.** [The vision](../vision.md#what-belongs-in-the-contract)
owns the framework direction. Use [spec authoring](spec-authoring.md#standards-incorporation) to
select and declare standards profiles; implementation documentation is not a source of obligations.

**3. Short, direct, plain.** Use familiar words and short sentences, with one main point per sentence.
Keep the detail an implementer needs. Use defined protocol terms consistently.

- **Name the actor and action.** "The server rejects the request" is clearer than "Rejection of
  the request is performed". For normative wording, follow [spec authoring](spec-authoring.md#2-write-it).
- **Say what the thing is.** Use "Make context management optional" instead of "Stop requiring
  context management". This applies to headings, prose, test names and commit subjects. Keep real
  prohibitions such as `MUST NOT`.
- **Keep useful rationale.** Put history in commit messages. Keep a reason a reader needs to
  maintain the contract in a guide or proposal.

**4. Check inherited obligations before assigning IDs.** Follow
[spec authoring](spec-authoring.md#standards-incorporation) for profile scope and
[the chapter reading rules](../../spec/README.md) for what an incorporated standard already supplies.

**5. Remove explanations that no longer help.** When an adopted contract change removes a special
case, delete its obsolete explanation. For example, remove a note about a separate request format
once the operation uses the chapter's shared format. Requirements follow
[governance's withdrawal and deletion rules](../../GOVERNANCE.md#withdrawing-a-requirement), applied
in [spec authoring](spec-authoring.md#5-withdraw-never-delete); becoming ordinary does not itself
remove an obligation.

**6. Every sempods-authored obligation has a requirement ID.** Obligations inherited from an
explicitly incorporated standard retain that standard's identifiers; informative references create
no obligations. [Spec authoring](spec-authoring.md#standards-incorporation) defines how a chapter
identifies its profile. Explanatory prose remains informative.

**7. No stub chapters.** A chapter exists when it is written. Until then it is a row with a status
in `spec/README.md`. An empty file that says "TBD" is a promise the repository cannot keep and a
link target that lies.

**8. This repository is public.** Nothing strategic, commercial or personal goes into it — roadmaps
included. Technical milestones are public; the business around them is not.

**9. Show the case.** Give a concrete input and outcome when readers would otherwise have to derive
a consequence. Use a list or table for several cases. For example, these informative write-request
cases illustrate [SPS-CRUD-007](../../spec/core/lod-crud.md#SPS-CRUD-007) and
[SPS-CRUD-008](../../spec/core/lod-crud.md#SPS-CRUD-008):

| Request | Outcome |
|---|---|
| A write without `?context=` | `400` |
| A write with `?context=valid&context=` | `400`: two occurrences, even though one value is empty |

Keep examples informative and link their requirements. Put them in the chapter's explanatory prose,
a guide or proposal; use [worked fixtures](../../examples/README.md) for executable access-control
cases. Conditions and exceptions stay in the requirement, as in
[SPS-MEDIA-002](../../spec/modules/media.md#SPS-MEDIA-002) and
[SPS-CTX-030](../../spec/core/contexts.md#SPS-CTX-030). Keep rationale separate under
[spec authoring](spec-authoring.md#pitfalls).

**10. Length is a budget.** Replace outdated prose when the described behavior changes, including
in review fixes. When adding a paragraph, remove text it makes redundant. Review a growing section
for repetition; retain explanations and examples readers need. A section's length is never a reason
to remove a requirement. Rule 5 governs requirement removal; [spec authoring](spec-authoring.md#2-write-it)
governs wording changes.

**11. Link the source of a contract.** When explaining protocol behavior in guides, examples or
code comments, cite the requirement ID or incorporated standards profile. A request-validation
comment can link `SPS-CRUD-008` and explain how the checker counts parameters. Keep protocol obligations in the
[contract sources](../../GOVERNANCE.md#contract-sources). Maintain their required OpenAPI and
vocabulary views together; removing duplicate prose does not permit omitting a contract view.

## Issue planning

Use an issue plus a PR for actionable specification, design, maintenance and publication work.
Small changes may use a standalone issue; only substantial design that benefits from reviewable
prose needs a proposal document. Link it to its issue without a second task list.

Parent issues own the problem, target, scope, decisions and overall acceptance. Native sub-issues
own bounded iterations and progress; native dependencies express prerequisites. Do not duplicate
sub-issue state in body checklists. Incorporate actionable discussion results into the owning
issue's description. Read the parent, relevant decisions and blockers before starting, and record
observable acceptance, applicable checks and documentation completion.

Filers supply scope and related issue links. Maintainers or triagers set native relationships,
reuse existing category/area labels and assign milestones only for agreed release scope.
Specification and implementation versions are independent; Git tags identify published revisions
under [governance](../../GOVERNANCE.md). An optional organization Project may show priority and
iterations over those same issues; it is not another status owner or a prerequisite for work.

Every PR completes the definition of done for its own diff before review, including partial work.
Use `Refs #N` for partial work; use `Closes #N` only when merging the PR satisfies all acceptance
and required follow-up actions. Close an issue only after its deliverable, required merged PRs,
checks and documentation evidence are verified. A proposal deliverable asserts neither normative
adoption nor publication. A parent also needs its own acceptance and required children complete;
a child closed as not planned requires an explicit scope decision, not a claim of delivery.

### Automated dependency updates

A routine bot dependency-update PR may be its own work record when it identifies the update,
compatibility impact and validation. Checks, review and documentation duties still apply. Broader
manual dependency or architecture work uses an issue; do not create duplicate public issues for
routine bot updates.

### Security fixes

Follow the inherited [security policy](https://github.com/sempods/.github/blob/main/SECURITY.md).
Embargoed work uses the private advisory/fix record for scope, decisions, acceptance, fix PRs and
verification. Keep sensitive details and evidence private; no duplicate public issue is required.
Applicable checks and documentation duties remain. Coordinate public documentation with disclosure.

### Retained design material

[Authorization implementation proposal support](../proposals/authorization-implementation/README.md)
is a temporary exception to these document types, retained solely for
[#64](https://github.com/sempods/sempods-spec/issues/64)'s disposition. It is proposed design, not
current implementation documentation. The issue owns the intended recipient, source mapping and
immutable revisions. sempods-kotlin is a candidate, not an automatic destination.

The exception ends with verified receiving changes and source cleanup, or an explicit
maintainer-approved no-transfer disposition and cleanup. A release tag or an open handoff issue
alone is insufficient grounds for removing still-needed material. Useful implementation-neutral
fixture explanations retain their own guide or example home independently of that transfer.

## Definition of done

Every PR completes the following for its own diff before review:

- every new sempods-authored obligation carries a requirement ID, and no ID was reused or renumbered —
  unless the pre-`0.1` window is open and the change says so out loud;
- a withdrawn requirement is marked withdrawn rather than removed, and names its successor;
- the chapters, incorporated standards profile, OpenAPI, vocabulary and generated index agree;
  review semantic effects explicitly, including inherited obligations, not only unchanged IDs;
- the applicable work record is linked and contains completion and check evidence, with unfinished
  acceptance kept open under [Issue planning](#issue-planning);
- affected documentation is updated or reduced, or a specific no-change reason is recorded;
- proposal disposition and guide revision references agree with the delivered scope;
- `spec/README.md`'s chapter table still reflects reality;
- every relative link resolves, and any new document is reachable from an `AGENTS.md`;
- where the change leaves an implementation behind, an issue is open in that repository — this text
  decides, so one that no longer matches it is the defect; and where an identifier was deleted,
  renumbered or redefined, the pull request re-vendoring the index there is open too. Neither fits
  in this commit, which is why this is the item that gets forgotten.

[`documentation-sync.md`](documentation-sync.md) is the procedure that walks this list.

Run the applicable [repository checks](../guides/repository-checks.md), including links/anchors
and full site rendering, and report skipped checks. Their success does not replace semantic review.
