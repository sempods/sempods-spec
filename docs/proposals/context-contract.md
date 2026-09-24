# Discoverable Contexts and RDF registry descriptions

Status: **Partly adopted in this revision; remaining recommendations are non-normative.**
RDF registry adoption: [#92](https://github.com/sempods/sempods-spec/issues/92), implemented by
[PR #93](https://github.com/sempods/sempods-spec/pull/93), owns descriptions, catalogues and creation
response representations in the linked normative chapters. [#90](https://github.com/sempods/sempods-spec/issues/90)
is the completed recommendation source.
Empty-registry lifecycle: [#37](https://github.com/sempods/sempods-spec/issues/37) /
[PR #104](https://github.com/sempods/sempods-spec/pull/104) permits empty registries with the current
context-management module; deletion remains destructive.
Remaining proposal: [#69](https://github.com/sempods/sempods-spec/issues/69) owns the module/default-access
and full lifecycle decisions; [#68](https://github.com/sempods/sempods-spec/issues/68), through #69–#74,
owns their coordinated normative adoption. This document retains those non-normative recommendations.

## Scope and standards

Applications describe resources and their relationships in RDF. A Context identifies a logical
view of that data; membership may be stored or computed. It does not define the application's
vocabulary, a folder for a resource, or a physical store. The same resource IRI can occur across Contexts without changing
what it identifies. Ordinary clients use the
[implicit data-scope recommendation](data-access.md#logical-dataset-and-operation-scope) without discovering or selecting a Context.

The [vision's selection test](../vision.md#what-belongs-in-the-contract) separates three concerns:

| Concern | Contract boundary |
|---|---|
| Semantic data | RDF identities, assertions and stored/computed views; a native named graph need not be a registered sempods Context. |
| Context access profile | An advertised Context has registry RDF, a caller-authorized projection and an access summary. Its SPARQL projection is a logical named graph, including when computed over a store with no physical named graphs. |
| Lifecycle | Optional context-management supplies authorized creation/deletion. External provisioning and administration remain implementation choices; core discovery/selection works without the module. |

In the first RDF delivery, retain the current Context-mode implications for compatibility. In the
full view contract, read, data-write and view-management authority are independent. A manager can
register or remove a computed view without authority to edit, or even read, its sources. Where a
membership-based policy profile implies read/write from manage, report the resulting modes;
do not extend that implication to every view. Slash-bounded management limits administrative
authority, not RDF containment or domain relationships. Neither wire-level grant parsing nor a
particular policy representation follows from a Context's identity.

The baseline is the proposal and current contract at
[`303d8aa`](https://github.com/sempods/sempods-spec/tree/303d8aa3acf3d7838e7c1a7062a705ab958d7954).
Reuse the existing canonical JSON-LD/N-Quads read profile and RFC 9110 for negotiation, validators
and conditional reads. Creation retains the current lifecycle contract as described below.
[RDF Schema 1.1](https://www.w3.org/TR/2014/REC-rdf-schema-20140225/)
supplies `rdfs:label` and `rdfs:seeAlso`;
[DCMI Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)
supplies `dcterms:description` and `dcterms:created`.
[SPARQL Service Description, 21 March 2013](https://www.w3.org/TR/2013/REC-sparql11-service-description-20130321/#vocab)
supplies the graph-description vocabulary only. Reusing its terms does not add a SPARQL service
endpoint or assert that the registry is the caller's query dataset. HTTP cache directives retain
[RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html)'s meanings.

## Core selection and optional management

Recommend Context catalogue/description reads, caller-access summaries and selection as core,
with client-facing creation/deletion in optional `https://schema.sempods.org/module/context-management`.
Every implementation supports the core contract; ordinary clients need no Context-related requests.
A single-graph pod can expose no Contexts and return an empty catalogue. CMS-derived spaces can
appear as selectable Contexts without a sempods lifecycle API.

Keep `spec/core/contexts.md`, `spec/modules/context-management.md` and their corresponding OpenAPI
ownership. Retain the existing management module identity and allocate no `module/contexts` IRI.
Historical revisions retain their meaning; changes to lifecycle effects need explicit version and
compatibility treatment under [governance](../../GOVERNANCE.md#versioning).

For this boundary there are two conformance configurations: core, or core plus context-management.
After coordinated adoption, an implementation with CMS-derived Contexts and no other modules can
describe itself using the existing conformance fields:

```json
{
  "specVersion": "0.1-dev",
  "modules": []
}
```

No `supportsContexts` or default-context flag is needed. A missing management declaration means
that clients cannot rely on sempods creation/deletion; an owner's CMS administration rights do not
supply that API. Advertising management commits to its specified successful operations when
supported targets and authority allow them. Universal `403` does not implement an advertised module.
A deployment may also contain externally managed Contexts whose lifecycle is unavailable through
that module; their catalogue modes follow the [access summary](#caller-access-summary).

### Ordinary bootstrap

The pod supplies the [implicit D scope](data-access.md#recommended-implicit-scope) even with no
exposed Contexts. An authorized ordinary creation writes there without registry setup. D can use an
internal default Context or storage with no Context concept; its public Context IRI is optional.
Registering another Context does not change D. Read, find and the ordinary SPARQL default graph
use that same scope within current authority; source writes can change dependent computed views.
The [default-access sequences](data-access.md#default-access-acceptance-sequences) and
[authorization cases](access-control.md#authorization-without-context-setup) own those guarantees.
Choosing D grants nothing; permission on independent A does not authorize a write to D.

The current contract still requires explicit Context selection on data writes. Its minimum count
applies without context-management ([`SPS-CTX-028`](../../spec/core/contexts.md#SPS-CTX-028)); an empty
registry with that module permits Context creation, not Context-free data writes. The recommendation
changes both restrictions only through coordinated normative adoption.

### Stored and computed views

A registered Context names an addressable RDF view; a registry is a logical catalogue, not a
required physical table. Membership may be stored or computed from CMS spaces, user membership or
source facts. Expose canonical Context IRIs supplied by the pod; a client never constructs them
from CMS identifiers. The view definition and policy language need no public query or management API.

Context-selected reads, find expansion and `GRAPH <C>` use C's same authorized projection.
`sd:NamedGraph` describes that projection, not physical storage or a separately owned copy.
Projections can overlap; the same triple occurs once in their RDF union, while SPARQL retains its
normal solution multiplicities. A materialized view cannot broaden access or supply a stale
successful projection. The [dataset contract](data-access.md#logical-dataset-and-operation-scope)
owns term identity, named-graph visibility and selected-read/write effects.

### Caller access summary

Recommend reusing the RDF catalogue relationships with defined scope-level meanings. These are
proposed changes to the current grant-based [`SPS-CTX-034`](../../spec/core/contexts.md#SPS-CTX-034),
not an assertion that the adopted contract already supports arbitrary policy models.

The catalogue lists every Context for which this caller/client has at least one mode below. Each
mode reports current eligibility for that class of operation on C. Eligibility is a necessary
condition, not a claim that every resource, payload or precondition passes. Resolve it from the
applicable delegation or service assignment and current policy, including applicable public read,
independently of whether C contains data. Do not infer it from a successful request to one resource
or inspect hidden resource existence to decide the summary. Storage of grants or a separate policy layer is not required.

| Relationship from the catalogue to C | Proposed meaning |
|---|---|
| `readableContext` | The caller may select C's authorized data projection, possibly empty. Resource rules still filter that projection. It does not promise access to all of C's sources. |
| `writableContext` | C supports the membership-write contract and the caller has scope-level authority for selected data writes. Additional target, payload and complete-effect checks can refuse an individual mutation. |
| `manageableContext` | The management module provides lifecycle for C and the caller has authority to manage that view. External CMS administration alone does not qualify; without the module this set is empty. Data access is independent. |

Absence of a mode means that operation class is unavailable to this caller at the represented state;
it is not permission to try a broader fallback. A model with only resource-dependent rules still
has to define this bounded eligibility for any Context it exposes. It can instead expose those
resources through ordinary D access, without inventing Context-level permissions. Eligibility may
be established for an empty view or for a view whose resource rules currently hide every assertion.
A catalogue need not reveal hidden resources to be complete.

Keep the current RDF shape, negotiation and authorization/cache isolation. No new permission fields
or universal grant catalogue are needed. The server authorizes each later request again. The
catalogue's validator changes when represented membership or modes change; resource/view validators
follow their own representations. Reading a stale summary never restores authority. A Context's
public-read setting likewise permits an anonymous projection subject to applicable data rules; it
does not label every source assertion public. Public access retains the separate
[public-read rules](access-control.md#public-access-and-public-read).

### Selected-write boundary

The [membership-write contract](data-access.md#writes-within-the-addressed-scope) permits independently
mutable assertions, however implemented. A computed view lacking that contract is read-only through
selected CRUD, even when its manager can edit the definition or separately write the sources.
Omit `writableContext`; valid selected writes uniformly give `403`, including no-ops and absent
targets. No source/default-scope fallback or implicit selection-rule change is allowed.

A listed writable Context can still refuse a target under document or payload policy. Such denial
uses the [complete-effect and non-disclosure guarantees](access-control.md#complete-scope-authority-and-non-disclosure),
including hidden collisions and conditional requests. Managing a view grants neither read nor
source-write authority. General write-through computed views remain deferred until a discoverable
contract defines insertion, overlap, source updates and updates that leave the view.

### Externally changing spaces

A CMS may change a view's data membership or remove its public Context without a sempods management
request. Core specifies the resulting observations, not a CMS administration or sync protocol.
After a completed source or authorization change, the next request uses the updated authorized
projection; a stale materialization or cache cannot justify old access. Data growth within an
approved dynamic boundary differs from withdrawing authority or broadening the selection rule;
[delegation](access-control.md#request-selection-and-delegation) fixes those limits.

After C disappears, omit it from the catalogue. Its description returns the same `404` as a hidden
or absent Context, including for a conditional request with its old validator. Explicit C-selected
reads contribute no data; writes give uniform `403`. Never redirect to D or expose the old name as
a native-graph fallback. Core removal of the projection does not itself delete source assertions
or redirect ordinary writes. Independent current source authority still governs D and other views;
it must not be inferred from C's disappearance. A separate CMS data deletion has its own effects.

If C is later recreated, old C-bound authority does not revive. An unchanged IRI is insufficient to
establish the same authorization basis. Re-establish the relevant authority explicitly, including
fresh app consent where its ceiling or revoked authority requires it. Implementations choose how to
track that boundary; the public API adds no generation identifier.

## Adopted RDF surface and proposed lifecycle

The RDF registry surface from #90 is adopted separately under
[#92](https://github.com/sempods/sempods-spec/issues/92). Its normative owners are
[`SPS-CTX-031`](../../spec/core/contexts.md#SPS-CTX-031)–
[`SPS-CTX-036`](../../spec/core/contexts.md#SPS-CTX-036) and
[`SPS-CTX-037`](../../spec/modules/context-management.md#SPS-CTX-037), with
[representations and HTTP verification cases](../guides/context-registry.md).
Current grant implications, creation input/effects and destructive deletion remain in force.
The independent read/write/manage modes above and the optional lifecycle effects below remain
recommendations under #69. Keeping management optional does not settle its deletion semantics.

Current context-management permits deletion of the last Context and owner creation in an empty
registry under [`SPS-CTX-017`](../../spec/modules/context-management.md#SPS-CTX-017) and
[`SPS-CTX-019`](../../spec/modules/context-management.md#SPS-CTX-019). The proposed non-destructive
deletion below remains separate from that contract.

### View removal and source retention

Recommend separating three effects: removing an advertised view, changing its source data and
collecting unreferenced media. A manager may be allowed to do the first without either of the
others. This is a sempods choice about the addressed resource, not a consequence of RDF graph
semantics. It fits the vision's independent authorization and storage freedom: implementations
choose their storage and policy representation, while clients can rely on the same effects.

Deleting C unregisters its view and withdraws its published Context projection. It does not delete
source assertions, clear an underlying graph, drop source media associations or remove independent
views. This also applies to explicit membership-backed C, including assertions reachable only
through C before deletion. Retaining them does not move them into D, publish them or grant access.
The old Context IRI cannot remain exposed as a native-graph fallback.

Independent current authority still governs retained data in D or another view E. A rule shared
with E remains effective there only on its independent basis; a reference to a shared rule is not
itself independent authority. Remove C's authorization effect without deleting shared policy state
or unrelated delegations. Old C-bound grants, consent and service assignments authorize neither
retained sources nor a later recreation of C. Credentials with other authority remain usable under
the [revocation contract](access-control.md#consent-and-credential-races).

A computed view over retained sources continues to evaluate its unchanged definition. An explicit
dependency on C's *published projection* instead sees that input disappear; retaining source facts
does not promise that every dependent result remains identical. Neither case rewrites the view's
rule or substitutes D. Source-data deletion is a separate operation, authorized for its complete
effect, which can then change all dependent projections.

Data reachable only through the removed view can become inaccessible through the sempods API.
It remains retained; lack of a readable projection is not evidence that it is disposable. An
implementation may offer separately authorized source administration for recovery or deletion.
This proposal adds no recovery endpoint, mandatory archive, retention timer or storage schema.
A new view over those sources needs explicit provisioning and fresh authority; ordinary Context
creation at the old IRI is not recovery. This retention cost is intentional: view-management
permission alone must not destroy source data. Storage reclamation without changing these logical
outcomes remains an implementation choice.

### Lifecycle authorization and completion

After authentication and syntax checks, authorize unregistration independently of hidden source
contents. Existing authorized C gives `204`, absent C gives `404`; outside management authority
both give `403`. A successful response completes C's removal and withdrawal of its authority.
Each retry checks current management authority. A caller whose only authority was bound to C
receives `403` after removal, whether C stays absent or is recreated without new authority for that
caller. Only independently retained management authority, such as owner or covering parent-prefix
authority, permits the absent-target `404`.

A rejected operation leaves both unchanged. An interrupted request may have committed or not.
With retained management authority and no intervening recreation, a retry distinguishes an existing
C (`204`, now removed) from an already removed C (`404`). A `403` does not establish which outcome
occurred. A lost response does not imply rollback, and an unconditional retry is not guaranteed to
address the same view after recreation. This proposal adds no generation identifier or new
conditional lifecycle API. No storage transaction or policy-deletion order is prescribed.

Apply the existing proposed revocation boundary to in-flight requests. A request whose authorization
decision follows completed removal cannot use C's former authority, even with a cached catalogue,
old description validator or still-valid credential. Earlier-authorized reads may have disclosed
data that cannot be recalled. A selected write that races removal either commits wholly before
removal or makes no source/assignment change; it cannot recreate C, attach to a new C at the same
IRI or redirect to D. If removal wins after admission, return `409` for that conflict. These outcomes
cover RDF mutation and media upload, assignment and unassignment. A losing unassignment leaves its
source association and collection eligibility unchanged; ensure-absent success applies only after
admission to a live writable source scope. It cannot report success through a retired projection.
Upload preparation that loses this race follows the [cleanup rule](#media-associations-and-collection)
below, including any new bytes and media-registry state.

A new data/media write selecting the now absent C gives `403` under the proposed
[unknown-write-selector rule](data-access.md#core-context-selection), even with independently retained
owner or prefix authority. The selected membership-write surface is unavailable; that authority
cannot create it through a data operation. This deliberately replaces the current `404` for
authorized RDF/media writes to an unknown Context under
[`SPS-CORE-018`](../../spec/core/index.md#SPS-CORE-018) and their OpenAPI responses. It does not
change the lifecycle DELETE distinction above: independently authorized removal of an absent
Context still gives `404`. A missing resource inside a live writable scope retains its own operation's
response. Current normative behavior remains binding until coordinated adoption.

There is no minimum registered Context count or replacement requirement. Removing the last Context,
including a public name for D, leaves D's identity and placement unchanged. Ordinary operations
continue subject to independent current authority. A client whose only authority depended on C
loses that access; retaining D does not promise that every previous caller remains authorized.
A context-unaware client with independent D authority can still read, create, update and delete.

Creation with the existing ContextCreate fields creates an empty membership-capable view. Existing
C retains its idempotent creation behavior; a genuinely recreated C has no former membership,
metadata, public setting or C-bound authority unless newly supplied or explicitly established.
The supplied creation setting may authorize the new view; it never republishes retained sources
by matching their former IRI. Creation does not redirect D. Provisioning computed definitions or
recovering retained sources belongs to separately authorized administration, without adding a
view-definition language to this contract.

### Media associations and collection

This recommendation applies only when the optional media module is advertised. Core discovery or
management does not imply that module. Keep its byte identity, pod isolation and separation from
RDF: deleting an RDF link to media does not remove an assignment, and mentioning a media IRI in a
readable computed RDF view does not itself authorize fetching the bytes.

Treat an assignment as an association of a media object and declared content type with a source
scope. Its exposed Context name is a way to address that scope, not its lifetime. Ordinary media
upload, assignment and unassignment use D without a Context parameter. Explicit selection addresses
one membership-writable Context, with the same no-fallback and read-only-view limits as RDF writes.
For media writes, C's projection and mutations address one fixed, independently mutable logical
assignment scope, with at most one association per media object. Its source scope does not depend
on the media ID, current assignments or caller visibility. A Context alias of D can satisfy this
contract; RDF writability alone does not establish it.

A projection combining independent assignment scopes is read-only for media upload, assignment and
unassignment. Return uniform `403`, including when zero or one association is currently present or
visible, when projected metadata entries coincide, and for ensure-absent/no-op requests. Do not
choose one projected source, delete all sources or write a separate direct C association behind
the projection. This restriction adds no source identifier or write-through protocol.

An explicit empty or multiple write target is invalid; omitting the target means D. Assigning an
existing object still needs target-write authority and current read authority through an existing
assignment; knowledge of its content hash or a retired C assignment is insufficient. Uploading the
bytes remains a separate path and keeps the same response for new and deduplicated content.

Media reads have no new selector. Authorize through at least one currently readable assignment in
D or an exposed Context, subject to the caller's delegation and applicable data policy. An
implementation exposing media through a computed view needs an explicit authorized projection of
source assignments; RDF view membership alone does not supply one. This adds no media-specific
permission language. A computed view without membership-write support cannot accept assignments.

Unregistering C retires its public assignment projection and C-bound access, while retaining the
source associations and bytes. Independent D/E associations and their declared types survive.
When C was the sole access path, both media metadata and content return the usual indistinguishable
`404`, including conditional requests with old validators. Retained associations keep the object
referenced for collection; disappearance of the last readable or named projection does not start
a grace period. Recreating C at its former IRI exposes none of those associations automatically.

Metadata uses the existing `Media.assignments` array. Include the readable D association as one
entry with `context` **omitted**, its `contentType`, and `filename` if recorded. Absence of `context`
means D; neither `null`, an empty string nor a synthetic Context IRI represents it. There is at most
one logical association of an object with D, irrespective of internal storage. D-only access thus
produces one context-less assignment, not an empty assignments array. For example, its assignments
member can be:

```json
{
  "assignments": [
    { "contentType": "image/png", "filename": "photo.png" }
  ]
}
```

A readable named projection contributes entries with its actual `context` IRI and the projected
source assignments' `contentType` and recorded `filename`. If several sources project into C,
include each distinct exposed metadata entry once; differing metadata can produce multiple entries
with the same Context IRI. Omit hidden assignments and retired names. If C aliases D, include both
the context-less D entry and the C entry only when each is independently readable; C access alone
does not reveal a D association. This proposes a wire meaning for the existing fields and requires
coordinated media schema/example changes.

Choose the declared type from the readable D association first, if present; otherwise use the
lowest readable Context IRI as today. A computed projection carries its source assignment's type;
if multiple source assignments appear under one name, choose the lexicographically lowest declared
type among the readable candidates. These deterministic tie-breaks use no hidden or retired
assignment. Conditional responses use the newly authorized representation and selected type; no
old `ETag` authorizes a read. Existing content-type defaults, disposition rules, private caching,
`Vary`, `nosniff`, sandbox and fetched-source protections continue to apply.

Explicit authorized media unassignment removes the object's association in that one writable
source scope, or succeeds without a change if it is already absent there. A C-selected deletion
therefore removes C's projection of that association and any other aliases of the same association.
Independent associations of the same object in E survive; metadata equality does not merge their
identity or collection effects. An ordinary D unassignment likewise leaves independent E intact.
Removing a computed projection is not source unassignment. Only when no source association remains, including retained associations
without an exposed view, does removal of an association make the object unreferenced and begin its
grace period. Reassignment clears that state. Separately authorized source disposal may remove
retained associations, but view removal and reconciliation cannot do so implicitly. Preserve delayed collection, retryability
and pod-local unavailability after collection; this proposal does not redesign the collector's
storage order or solve its independently documented upload/collection race.

An upload may prepare bytes or media-registry state before committing its association. If Context
removal wins, leave no assignment from that upload. Roll back newly prepared state, or put any new
durable object left without source associations into the unreferenced collection lifecycle, with
its grace period starting when the attempt is abandoned. This includes objects that never had an
association: eligibility cannot depend on an earlier unassignment. An interrupted failed attempt
needs recoverable cleanup rather than an untracked object that only report-only reconciliation
could find. Neither the failed upload nor retained preparation state grants read access.

Cleanup applies only to the failed attempt's disposable state. It must not delete shared bytes,
remove another operation's committed association, mark a referenced object unreferenced or reset an
existing collection deadline merely because a deduplicated upload failed. Disposal respects current
source associations, including retained ones; a newly committed association clears unreferenced state. The implementation chooses staging, rollback or retryable collection bookkeeping.
This closes orphan creation by a losing upload without selecting a general collector algorithm.

### Lifecycle acceptance cases

These are proposed HTTP/model expectations for coordinated adoption, not executed tests. Credentials
are valid and requests well-formed. Management and media cases assume their respective modules.
Independent D/E authority and source associations are stated explicitly; they never follow merely
from a surviving name. Each row begins from its stated setup.

| Setup and operation | Expected observation |
|---|---|
| Manager can remove C but cannot read or edit its sources; delete C with and without hidden data | Both `204`; C disappears and source data stays. Catalogue omits C, description `404`, C-selected resource read `404`, find empty, selected writes `403`. |
| After deletion, a manager with retained independent owner/parent-prefix authority retries absent C; a former manager whose only authority was C-bound retries absent or recreated C without new authority | Independently authorized manager gets `404`; former manager gets `403` in both states, with no source or policy change. |
| C and C/sub project the same sources independently; remove C | C/sub's definition, independently authorized data and management remain. The path does not cause cascading deletion. |
| E reads C's published projection, while F independently reads C's retained sources; remove C | E loses that input, F retains its authorized result; neither rule is rewritten and D is not substituted. |
| C is a membership-backed view outside D and is the only access path to R; remove C | R survives but is not accessible through C or ordinary D. No implicit public, native-graph or recovery fallback. |
| C exposes D and is the last Context; a different client has independent D authority | Deletion `204`, catalogue empty; ordinary GET/PUT/PATCH/DELETE and default-graph query continue in the same D. No Context setup is required. |
| Same setup, but an app's authority depends only on C | Its C access ends; it gains no D authority. A still-valid credential with independent E authority retains only that applicable access. |
| C used a policy also independently applied to E; remove C and recreate its IRI | E remains authorized; old C consent/grants/service assignments authorize neither the new C nor retained sources. New C starts empty with its newly supplied metadata/settings. |
| Removal is denied, interrupted before commit, or its response is lost after commit; no intervening recreation | Denial changes nothing; interruption exposes either complete state. With retained independent management authority, retry gives `204` if still present or `404` if removed. Without current authority it gives `403`, which does not disclose the outcome; no partial authority withdrawal. |
| A selected RDF write or media upload/assignment/unassignment races C removal | Commit wholly before removal, or reject the admitted conflict with `409` and no source/assignment change. Failed upload preparation follows the cleanup rule; no write to D or recreated C. |
| After removal, caller with former C-only authority or retained independent owner/prefix authority makes a new C-selected RDF/media write | Both get `403` under the proposed unknown-write-selector rule. Separately, an independently authorized lifecycle DELETE gets `404`. No data-write registration or fallback. |
| Upload of new bytes loses to C removal after storing bytes or creating media-registry state | `409`, no new association or access; prepared state is rolled back or durably tracked as unreferenced from abandonment and eligible for delayed cleanup even though it never had an association. Repeat with an interrupted attempt. |
| Deduplicated upload loses to C removal; object is referenced by another current/retained association, or was already unreferenced before this attempt | `409`; in the referenced case, shared bytes and other associations survive without marking the object unreferenced. In the already-unreferenced case, the original grace deadline remains unchanged. |
| Selected media unassignment races removal of its C projection; C addresses the final source association | Unassignment commits first: remove the association and start the grace period. Removal wins after admission: `409`, retain the association and do not start collection. No ensure-absent success through the retired projection. |
| Empty catalogue and no management; media client has D read/write authority | Upload without Context returns `201`, including deduplication; metadata contains one D assignment with `context` omitted and its recorded type/filename, content is readable, ordinary unassignment addresses D and succeeds on repetition. Media operations need no registry bootstrap. |
| Media M has independent assignments in C and E; remove C | E's authorized metadata/content remain readable with E's type. C is omitted; no source association is deleted and no collection timer starts. |
| M is assigned only through C; remove C, wait longer than the collection grace period | Metadata/content `404`, including old conditional reads; bytes and association remain retained. Recreating C does not expose M, and knowing M's hash cannot authorize assignment elsewhere. |
| C is a public name for D; M has one source assignment in D, also visible through C; remove C | Independent D authority still reads M with the same declared type, but metadata retains the context-less D entry with its type/filename and omits C. Ordinary unassignment can remove that retained D association. |
| M has D and C assignments with different types; caller reads both, then only C | Type first comes from D, then from C; content validators/disposition follow the chosen type. Metadata includes D with `context` omitted and C with its IRI while both are readable, then only C. Hidden assignments never supply metadata or the type. |
| Computed C projects two readable source assignments for M with different types, and no D assignment is readable | Select the lowest readable Context IRI, then the lowest declared type within it. Hiding one source removes its type from consideration; hidden state never breaks a tie. |
| C combines assignments from independent A/B scopes; selected media upload/PUT/DELETE, with zero, one or two current/visible assignments for M | Uniform `403`, including identical projected metadata and absent-assignment DELETE. A/B associations, bytes and collection eligibility remain unchanged; hiding one source does not make C writable. |
| C exposes one writable source scope A; M has associations in A and independent E; delete M's assignment through C, then repeat | Remove only A's association; C and other aliases of A no longer project it. E survives and prevents collection. Repetition succeeds without a change after normal admission, even if only E's association remains readable. |
| Readable computed C contains an RDF link to M but exposes no authorized media assignment | Metadata/content `404`; selected assignment/unassignment `403` when C lacks membership-write support. |
| Ordinary RDF deletion removes the last link to M | Source media assignments and bytes remain; RDF references do not control collection. |
| Authorized unassignment removes the last source association, versus leaving one retained after view removal | First starts the grace period; second does not. Reassignment before collection cancels the unreferenced state. |

Repeat removal/recreation with catalogue and description caches, conditional media reads and a
still-valid credential issued before removal. Run source-retention cases with stored membership and
computed views. Implementations supply policy/storage setup and source-retention inspection; the
observable HTTP results and no-authority-revival expectations stay the same. Collector race coverage
beyond the stated view-removal boundary remains separate work.

## Request cases

These are proposed HTTP expectations, not executed conformance tests. Unless stated otherwise,
credentials are valid, requests are well-formed, C is a private registered membership-capable view,
and policies allow the stated operation. The [lifecycle cases](#lifecycle-acceptance-cases) cover
removal and media separately; computed-view rows state their distinct setup and modes. Repeat
discovery cases with empty and nonempty graphs.

| Setup and request | Expected response/effect |
|---|---|
| Single graph, no management, no exposed Contexts; ordinary PUT/GET/PATCH/DELETE | The [ordinary sequence](data-access.md#one-rdf-graph) succeeds without any catalogue request or Context field; query sees D. |
| Same pod; catalogue GET before and after an allowed ordinary creation | Both `200` with an empty RDF collection; creation does not register a Context. |
| Same pod; resource GET and find selecting unknown C, or explicit empty selection | Resource `404`, find successful empty result; never D or unsupported-feature `400`. Malformed selectors remain `400`. |
| Empty registry, with or without management; consented ordinary resource PUT | Write to D `201`, registry still empty. Storage may use an internal default Context. No consent: write `403`. |
| CMS spaces C/E over D; no management; catalogue GET and selected reads | Visible spaces have readable relationships and descriptions, no manageable relationships. Selection works through core; no Context creation/setup is needed. |
| Same CMS pod; CMS owner requests conformance and catalogue | Both `200`; no management module declaration or manageable relationships. CMS ownership does not supply a sempods lifecycle API. |
| Management advertised; permitted Context creation, then ordinary data creation | Context PUT `201`; ordinary PUT still writes D. Context creation neither redirects D nor becomes a prerequisite for the data write. |
| No physical named graphs; computed C selects Alice's tasks from D; ordinary creation and then assignee update | C includes the matching task, then drops it when it no longer matches. No Context-membership write was needed. |
| C has child path C/sub and both views select the same task | No domain relation or RDF containment is inferred from the path; updates to shared source data can change both projections. |
| Caller manages computed C but cannot read or edit its sources | Catalogue links C through `manageableContext` only; registry GET `200`, data projection empty, selected writes `403`. No read/write implication from manage. |
| Readable computed C has no membership-write contract; selected PATCH/PUT/DELETE, including no-op requests | Uniform `403`; source facts, rules and grants unchanged. Authorized ordinary writes address sources inside D; no implicit write-through to sources outside D. |
| C has scope-level write eligibility; target-specific policy denies R | Catalogue includes `writableContext C`; R write gives `403`, including with a matching validator or hidden collision, without any mutation. A permitted target write succeeds under its normal contract. |
| C supports membership writes, but the caller lacks scope-level write authority | No `writableContext C`; selected writes give `403` even if the payload is empty or identical. |
| Caller may select C; all its assertions are hidden by document rules | C remains readable/discoverable with an empty projection; GET of R is `404`, find is empty and `GRAPH <C>` contains no triples. |
| C and E are read-only views over D selecting Alice's tasks and open tasks; R is both | Each selected GET and fixed-graph query returns R; C/E-union reads contain each triple once. Find uses the same authorized union for matching and expansion. |
| Same views; authorized ordinary PATCH changes R's assignee to Bob | Ordinary GET shows Bob; C no longer contains R, E still does. No independent copy or selected write is created. |
| Caller loses C access, while independent D and E authority remains | Catalogue loses C's modes; conditional C-description GET with an old tag gives `404`, never `304`; selected R GET is `404`. Ordinary D and E reads retain their independent results. |
| CMS removes C without removing its sources | Catalogue omits C; description `404`; selected R GET `404`, find empty and selected writes `403`. Independently authorized D/E results remain; no fallback to D under C's name. |
| CMS recreates C at the same IRI after removal | Old C-bound authority remains ineffective. Explicitly re-established authority is required; independent D authority is unaffected. |

Repeat the projection cases with a completed source/membership change followed by conditional reads
and cached catalogue access. Compare each selected read and query against the same authorized RDF
fixture; compare find against the same engine on that fixture, without prescribing its ranking.
These cases complement the [request-filter/delegation cases](access-control.md#request-selection-and-delegation).
They are proposed HTTP/model expectations, not evidence that a CMS adapter, cache or policy engine
has implemented them.

## Remaining adoption boundary

The RDF descriptions, catalogue and creation responses are adopted by #92 on the current Context
model. Their vocabulary properties and representations are owned by the normative chapters and
[guide](../guides/context-registry.md). Server/client/MCP migration is tracked in
[Kotlin #180](https://github.com/sempods/sempods-kotlin/issues/180), coordinating #166/#176.

Full adoption of ordinary access without Context setup, core discovery/selection and optional
context-management remains under #69–#74/#68.
It must review the default-access resolution and settle authentication/delegation decisions, then
align core/module versions, stored/computed projections, membership-write limits, independent
modes, Context-free data writes and the [lifecycle/media cases](#lifecycle-acceptance-cases).
Retention without a public recovery API and the changed media assignment/type rules require explicit
review and compatibility treatment; they are not corrections to the current destructive contract. The adopted RDF slice
advertises no new module and does not satisfy #68's adoption gate. The
[data-access inventory](data-access.md#requirement-changes-to-prepare) owns the wider impact.
