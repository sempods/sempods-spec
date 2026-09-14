"""Check navigation when repository documents move during staging."""

import unittest

import build


class StagedNavigationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.staged = build.staged_content()

    def test_vision_links_follow_the_relocated_source(self):
        vision = self.staged["vision.md"].decode()
        self.assertIn("](spec/README.md)", vision)
        self.assertIn("](GOVERNANCE.md#how-a-change-is-made)", vision)
        self.assertIn("](https://github.com/sempods/sempods-spec/blob/main/docs/proposals/data-access.md)", vision)
        self.assertIn("](https://github.com/sempods/sempods-spec/blob/main/docs/agents/spec-authoring.md)", vision)

    def test_landing_page_keeps_its_staged_paths(self):
        index = self.staged["index.md"].decode()
        self.assertIn("](spec/core/index.md)", index)
        self.assertIn("](GOVERNANCE.md)", index)
        self.assertNotIn("/main/site/spec/", index)

    def test_inbound_link_follows_a_relocated_document(self):
        result = build.with_repository_links(
            "[Vision](../../docs/vision.md#the-guiding-image)",
            "spec/core/index.md", "spec/core/index.md", {"docs/vision.md": "vision.md"})
        self.assertEqual("[Vision](../../vision.md#the-guiding-image)", result)

    def test_offsite_directory_and_local_anchor_keep_their_targets(self):
        result = build.with_repository_links(
            "[Examples](../examples/) [Here](#section) [Web](https://example.org/page)",
            "docs/vision.md", "vision.md", {})
        self.assertEqual(
            "[Examples](https://github.com/sempods/sempods-spec/tree/main/examples) "
            "[Here](#section) [Web](https://example.org/page)", result)


if __name__ == "__main__":
    unittest.main()
