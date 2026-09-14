# Selecting a specification revision

This informative guide describes the repository publication model in
[governance](../../GOVERNANCE.md#publication-identities-and-corrections). Read it at the same Git
revision as the contract and [site builder](../../site/build.py) it explains.

## Find the right source

| Source | Meaning |
|---|---|
| `main` and the development website | Changing development text. Normative chapters already bind under governance; “unreleased” does not mean “proposal”. |
| Full Git commit | An exact source snapshot, including one carrying a mutable `-dev` label. A commit alone is not evidence of a published release. |
| [GitHub Release](https://github.com/sempods/sempods-spec/releases) and its tag | A published component version, pinned to a commit and described by its canonical release notes. |
| [Proposals](../proposals/README.md) and [vision](../vision.md) | Informative design and direction; neither replaces the current contract. |
| [Issues](https://github.com/sempods/sempods-spec/issues) and [0.1 milestone](https://github.com/sempods/sempods-spec/milestone/1) | Current work and agreed release conditions, not published-version evidence. |

## Consume one snapshot

1. Select a published release or deliberately choose an exact development commit. Record the full
   commit; a branch name or `0.1-dev` alone cannot reproduce a claim. Read any withdrawal notice.
2. Obtain `spec/`, `openapi/`, `vocabulary/` and `requirements.json` from that same commit, directly
   or from its source archive. The index's `versions` map records core and module labels. Do not
   mix an old chapter with the latest index or a module description from another snapshot.
3. Review the release notes and changes against the previously selected revision, especially
   requirement IDs, compatibility and migration implications. Development consumers use the
   commit comparison and linked issues/PRs until a release exists.
4. Declare the supported core and module versions through the existing conformance contract and
   record the exact consumed revision in the implementation's own evidence. Its build commands,
   index vendoring, citation checks and release number belong in that repository.

The site's interactive OpenAPI copies target the demo pod. They are a try-it view, not the
unmodified source artifacts to consume. The revision page links the originals at the same commit.
A dirty local preview is labeled as such; its source-commit links do not include uncommitted edits.

“Pulling a version” means obtaining and consuming a snapshot here. Withdrawal from distribution is
an explicit, separate governance action. Neither changes an existing tag or introduces protocol
negotiation. The check results in [repository checks](repository-checks.md) establish bounded
repository evidence, not that a product implements the entire contract.
