from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import sys

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from psp_util import ValidationError, normalize_relpath, safe_join  # noqa: E402


class PathSafetyTests(unittest.TestCase):
    def test_normalize_relpath_accepts_nested_path(self) -> None:
        self.assertEqual(normalize_relpath("skills/triage/SKILL.md"), "skills/triage/SKILL.md")
        self.assertEqual(normalize_relpath(r"skills\triage\SKILL.md"), "skills/triage/SKILL.md")

    def test_normalize_relpath_rejects_traversal_and_absolute_paths(self) -> None:
        for value in ("../escape", "a/../../escape", "/tmp/escape", r"C:\escape", "", "./file", "a//b"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                normalize_relpath(value)

    def test_safe_join_stays_within_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            result = safe_join(root, "a/b.txt")
            self.assertEqual(result, root / "a" / "b.txt")

    def test_safe_join_rejects_symlink_component(self) -> None:
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as outside_raw:
            root = Path(raw)
            outside = Path(outside_raw)
            link = root / "skills"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink unavailable: {exc}")
            with self.assertRaises(ValidationError):
                safe_join(root, "skills/triage/SKILL.md")

    def test_safe_join_rejects_final_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            real = root / "real.txt"
            real.write_text("x", encoding="utf-8")
            link = root / "managed.txt"
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink unavailable: {exc}")
            with self.assertRaises(ValidationError):
                safe_join(root, "managed.txt")


if __name__ == "__main__":
    unittest.main()
