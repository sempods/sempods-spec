# Procedure: publish a specification version

Apply [governance](../../GOVERNANCE.md#publication-identities-and-corrections). This procedure
publishes a selected component and its exact source snapshot; it does not adopt protocol changes.

1. Open a publication issue naming the component, proposed tag, previous publication and release
   conditions. For the first core release, verify the external-adopter condition and every accepted
   deliverable in the 0.1 milestone. A module release cannot bypass applicable unresolved conditions
   or turn the unreleased core into a published dependency.
2. Prepare a reviewed PR with the selected component version in the requirement checker's
   `SPEC_VERSION` or `MODULE_VERSIONS`, the matching OpenAPI `info.version`, and affected chapter,
   vocabulary and discovery examples. Regenerate `requirements.json`. Retain independent component
   versions and identify any still-unreleased components in the snapshot. Update current-status prose
   in README and governance, including the first-publication notice. Apply spec-authoring when
   normative text changes; publication is not permission to renumber frozen IDs.
3. Prepare draft GitHub Release notes using the existing release mechanism. Record the component,
   full version map, changes since the prior publication, affected IDs, compatibility and migration
   implications. The first release describes the complete published scope, not only the last PR.
   Link adoption PRs and repository-check evidence. GitHub Releases owns the final notes; do not
   create a second maintained changelog file.
4. Run [repository checks](../guides/repository-checks.md#before-requesting-review) against the
   actual base and the full strict site render. Verify artifact/version agreement and review the
   precise final diff. After merge, verify the selected commit and CI again; changed content needs
   fresh evidence. Record the exact commit and evidence in the publication issue and draft notes.
5. With maintainer authorization to publish, create the new tag at that verified commit and publish
   the draft Release against that existing tag. Verify the resolved commit, source archive, notes,
   component versions and tag-workflow results. Do not move a published tag to repair a failure;
   follow governance's correction or withdrawal rule. No publication is performed merely by running
   documentation checks or deploying the development website.
6. Record the release URL, tag, full commit and checks in the publication issue. Subsequent
   development adopts the appropriate next `-dev` label through a reviewed change. Consumer-specific
   update procedures stay with consumers; the [revision guide](../guides/specification-revisions.md)
   describes the generic path.

If source artifacts, tag and notes disagree, publication is incomplete. Record the problem and a
reviewed disposition rather than claiming a successful release from a green website build.
