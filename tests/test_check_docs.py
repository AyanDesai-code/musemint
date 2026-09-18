"""Regression tests for the dependency-free repository documentation checker."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import check_docs


class DocumentationChecksTest(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        root_patch = patch.object(check_docs, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)

    def check(self, text):
        path = self.root / "README.md"
        path.write_text(text, encoding="utf-8")
        return check_docs.check_file(path)

    def test_valid_markdown(self):
        self.assertEqual(self.check("# Project\n\nDescription.\n"), [])

    def test_empty_file(self):
        self.assertIn("README.md: empty Markdown file", self.check("\n"))

    def test_final_newline(self):
        self.assertIn("README.md: missing final newline", self.check("# Project"))

    def test_trailing_whitespace(self):
        self.assertIn("README.md:2: trailing whitespace", self.check("# Project\nText \t\n"))

    def test_missing_relative_target(self):
        self.assertEqual(
            self.check("[Guide](docs/missing.md)\n"),
            ["README.md:1: missing relative link target: docs/missing.md"],
        )

    def test_existing_encoded_target_with_fragment(self):
        (self.root / "local guide.md").write_text("# Guide\n", encoding="utf-8")
        self.assertEqual(self.check("[Guide](local%20guide.md#section)\n"), [])

    def test_external_urls_and_anchors_are_not_checked(self):
        self.assertEqual(self.check(
            "[Web](https://example.com/page) [Heading](#heading) "
            "[Email](mailto:hello@example.com) [Root](/page)\n"
        ), [])

    def test_fenced_examples_are_not_links(self):
        for fence in ("```", "~~~~"):
            with self.subTest(fence=fence):
                self.assertEqual(self.check(
                    f"{fence}md\n[Example](missing.md)\n{fence}\n"
                ), [])

    def test_checks_resume_after_fence(self):
        self.assertEqual(len(self.check(
            "```md\n[Example](ignored.md)\n```\n[Guide](missing.md)\n"
        )), 1)

    def test_invalid_utf8_reports_error(self):
        path = self.root / "README.md"
        path.write_bytes(b"\xff\n")
        self.assertIn("cannot read UTF-8 Markdown", check_docs.check_file(path)[0])

    def test_missing_file_reports_error(self):
        self.assertIn(
            "cannot read UTF-8 Markdown",
            check_docs.check_file(self.root / "missing.md")[0],
        )


if __name__ == "__main__":
    unittest.main()
