"""Check navigation when repository documents move during staging."""

import unittest
import json
from unittest.mock import patch

import build


REVISION = "a" * 40


class StagedNavigationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(build, "source_revision", return_value=(REVISION, False)):
            cls.staged = build.staged_content()

    def test_vision_links_follow_the_relocated_source(self):
        vision = self.staged["vision.md"].decode()
        self.assertIn("](spec/README.md)", vision)
        self.assertIn("](GOVERNANCE.md#how-a-change-is-made)", vision)
        self.assertIn(f"](https://github.com/sempods/sempods-spec/blob/{REVISION}/docs/proposals/data-access.md)", vision)
        self.assertIn(f"](https://github.com/sempods/sempods-spec/blob/{REVISION}/docs/agents/spec-authoring.md)", vision)

    def test_landing_page_keeps_its_staged_paths(self):
        index = self.staged["index.md"].decode()
        self.assertIn("](spec/core/index.md)", index)
        self.assertIn("](GOVERNANCE.md)", index)
        self.assertNotIn("/main/site/spec/", index)

    def test_inbound_link_follows_a_relocated_document(self):
        result = build.with_repository_links(
            "[Vision](../../docs/vision.md#the-guiding-image)",
            "spec/core/index.md", "spec/core/index.md", {"docs/vision.md": "vision.md"}, REVISION)
        self.assertEqual("[Vision](../../vision.md#the-guiding-image)", result)

    def test_offsite_directory_and_local_anchor_keep_their_targets(self):
        result = build.with_repository_links(
            "[Examples](../examples/) [Here](#section) [Web](https://example.org/page)",
            "docs/vision.md", "vision.md", {}, REVISION)
        self.assertEqual(
            f"[Examples](https://github.com/sempods/sempods-spec/tree/{REVISION}/examples) "
            "[Here](#section) [Web](https://example.org/page)", result)

    def test_every_chapter_identifies_its_snapshot_without_rewriting_sources(self):
        for name, content in self.staged.items():
            if name.endswith(".md") and name != "revision.md":
                text = content.decode()
                self.assertIn("Development snapshot — not a release", text, name)
                self.assertIn("Source revision and matching artifacts", text, name)
                self.assertNotIn("/blob/main/", text, name)
                self.assertNotIn("/tree/main/", text, name)
        self.assertNotIn("Development snapshot — not a release",
                         (build.ROOT / "spec/core/auth.md").read_text())

    def test_artifacts_share_the_source_revision_and_keep_independent_versions(self):
        metadata = json.loads(self.staged["revision.json"])
        self.assertEqual(REVISION, metadata["commit"])
        self.assertFalse(metadata["dirty"])
        page = build.revision_page(REVISION, False, {"core": "0.1", "media": "0.2-dev"})
        self.assertIn("| core | `0.1` |", page)
        self.assertIn("| media | `0.2-dev` |", page)
        for path in ["spec", "openapi", "vocabulary", "requirements.json"]:
            self.assertIn(f"/{REVISION}/{path}", page)
        self.assertNotIn("published release 0.1", page)

    def test_dirty_preview_does_not_claim_to_be_reproduced_by_the_base_commit(self):
        with patch.object(build, "source_revision", return_value=(REVISION, True)):
            staged = build.staged_content()
        self.assertIn("uncommitted changes", staged["index.md"].decode())
        self.assertIn("does not include those edits", staged["revision.md"].decode())
        self.assertTrue(json.loads(staged["revision.json"])["dirty"])
        self.assertIn("uncommitted changes", staged["api/index.html"].decode())

    def test_interactive_api_identifies_the_original_source_artifacts(self):
        page = self.staged["api/index.html"].decode()
        self.assertIn("Development snapshot — not a release", page)
        self.assertIn('href="../revision/"', page)
        self.assertIn("Interactive copies target the demo pod", page)
        original = (build.ROOT / "openapi/sempods-core.yaml").read_text()
        self.assertIn(build.PLACEHOLDER_POD, original)
        self.assertNotIn(build.DEMO_POD_BASE_URL, original)

    def test_publication_build_refuses_dirty_input_before_rendering(self):
        with patch.object(build.sys, "argv", ["build.py", "--require-clean"]), \
             patch.object(build, "source_revision", return_value=(REVISION, True)):
            with self.assertRaisesRegex(SystemExit, "requires a clean checkout"):
                build.main()

    def test_mcp_origin_routes_stage_without_rewriting_metadata_examples(self):
        original = (build.ROOT / "openapi/module-mcp.yaml").read_text()
        staged = build.with_demo_pod(original)
        self.assertTrue(build.unchanged_outside_servers(original, staged))
        addresses = build.server_addresses(staged)
        self.assertEqual({build.DEMO_POD_BASE_URL, build.DEMO_POD_ORIGIN},
                         {resolved for _, resolved, _ in addresses})
        self.assertIn("resource: https://example.org/alice/_system/mcp", staged)
        self.assertNotIn("https://example.org/alice/_system/auth/token'", staged)

    def test_origin_substitution_does_not_allow_another_origin_or_extra_path(self):
        original = (build.ROOT / "openapi/module-mcp.yaml").read_text()
        for wrong in ["https://other.example", "https://example.org/wrong"]:
            changed = original.replace("default: 'https://example.org'", f"default: '{wrong}'")
            addresses = build.server_addresses(build.with_demo_pod(changed))
            self.assertIn(wrong, {resolved for _, resolved, _ in addresses})
            self.assertNotIn(wrong, build.ALLOWED_ADDRESSES)


if __name__ == "__main__":
    unittest.main()
