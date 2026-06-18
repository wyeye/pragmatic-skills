from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from psp_installer import DesiredBlock, extract_block, merge_block, remove_block  # noqa: E402


class ManagedBlockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.block = DesiredBlock(
            rel="AGENTS.md",
            text="<!-- PSP:BEGIN -->\nnew instructions\n<!-- PSP:END -->",
            begin="<!-- PSP:BEGIN -->",
            end="<!-- PSP:END -->",
            source="test",
        )

    def test_insert_preserves_existing_content(self) -> None:
        merged, status = merge_block("project instructions\n", self.block)
        self.assertEqual(status, "inserted")
        self.assertIsNotNone(merged)
        assert merged is not None
        self.assertTrue(merged.startswith("project instructions\n"))
        self.assertIn("new instructions", merged)

    def test_replace_only_managed_block(self) -> None:
        existing = "before\n\n<!-- PSP:BEGIN -->\nold\n<!-- PSP:END -->\n\nafter\n"
        merged, status = merge_block(existing, self.block)
        self.assertEqual(status, "replaced")
        assert merged is not None
        self.assertIn("before", merged)
        self.assertIn("after", merged)
        self.assertNotIn("\nold\n", merged)

    def test_duplicate_markers_are_malformed(self) -> None:
        existing = "<!-- PSP:BEGIN -->\na\n<!-- PSP:END -->\n<!-- PSP:BEGIN -->\nb\n<!-- PSP:END -->"
        _, status = extract_block(existing, self.block.begin, self.block.end)
        self.assertEqual(status, "malformed")
        merged, merge_status = merge_block(existing, self.block)
        self.assertIsNone(merged)
        self.assertEqual(merge_status, "malformed")

    def test_remove_preserves_surrounding_content(self) -> None:
        existing = "before\n\n<!-- PSP:BEGIN -->\nold\n<!-- PSP:END -->\n\nafter\n"
        updated, status = remove_block(existing, self.block.begin, self.block.end)
        self.assertEqual(status, "removed")
        self.assertEqual(updated, "before\n\nafter\n")


if __name__ == "__main__":
    unittest.main()
