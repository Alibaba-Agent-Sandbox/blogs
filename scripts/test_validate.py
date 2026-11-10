"""Behavior checks for optional blog publication metadata."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import validate


class PinMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.original_root = validate.ROOT
        self.addCleanup(setattr, validate, "ROOT", self.original_root)
        validate.ROOT = Path(self.directory.name)
        self.path = validate.ROOT / "example" / "index.en.md"
        self.path.parent.mkdir()

    def check_post(self, flags: str) -> list[str]:
        self.path.write_text(
            "---\ntitle: Example\nsummary: Example article\ndate: 2026-11-10\n"
            "category: case\ntags: [python]\nauthors: [anycodes]\n"
            f"{flags}---\n\nArticle content.\n",
            encoding="utf-8",
        )
        validate.errors.clear()
        validate.check_file(self.path, "example")
        return validate.errors.copy()

    def test_pin_is_optional_and_independent_of_featured(self) -> None:
        for flags in ("", "pinned: true\n", "pinned: false\n",
                      "pinned: true\nfeatured: true\n",
                      "pinned: false\nfeatured: true\n"):
            with self.subTest(flags=flags):
                self.assertEqual(self.check_post(flags), [])

    def test_pin_rejects_non_boolean_values(self) -> None:
        for value in ('"true"', '"false"', "1", "0", "null", "[]"):
            with self.subTest(value=value):
                errors = self.check_post(f"pinned: {value}\n")
                self.assertEqual(len(errors), 1)
                self.assertIn("`pinned` must be true or false", errors[0])


if __name__ == "__main__":
    unittest.main()
