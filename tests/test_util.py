from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from _support import ROOT  # noqa: F401
from psp_util import (
    PACKAGE_VERSION,
    ValidationError,
    build_skill_manifest,
    normalize_relpath,
    redact,
    safe_join,
    validate_skill_graph,
)


class PathSafetyTests(unittest.TestCase):
    def test_normalize_relpath_accepts_safe_path(self) -> None:
        self.assertEqual(normalize_relpath("skills/triage/SKILL.md"), "skills/triage/SKILL.md")

    def test_normalize_relpath_rejects_traversal_and_absolute_paths(self) -> None:
        for value in ("../escape", "a/../../escape", "/tmp/escape", "C:\\escape", "", "a/./b"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    normalize_relpath(value)

    def test_safe_join_rejects_symlink_component(self) -> None:
        with tempfile.TemporaryDirectory() as root_raw, tempfile.TemporaryDirectory() as outside_raw:
            root = Path(root_raw)
            outside = Path(outside_raw)
            try:
                os.symlink(outside, root / "skills", target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            with self.assertRaises(ValidationError):
                safe_join(root, "skills/triage/SKILL.md")


class MetadataTests(unittest.TestCase):
    def test_manifest_and_graph_are_current(self) -> None:
        manifest = build_skill_manifest(ROOT)
        stored = json.loads((ROOT / "skills/MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest, stored)
        self.assertEqual(manifest["version"], PACKAGE_VERSION)
        self.assertEqual(len(manifest["skills"]), 19)
        self.assertEqual(validate_skill_graph(ROOT, manifest), [])

    def test_skill_frontmatter_uses_standard_top_level_fields(self) -> None:
        permitted = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
        for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], "---")
            end = lines.index("---", 1)
            top_level = {
                line.split(":", 1)[0]
                for line in lines[1:end]
                if line and not line[0].isspace() and ":" in line
            }
            with self.subTest(skill=path.parent.name):
                self.assertTrue(top_level <= permitted, top_level - permitted)

    def test_redaction_hides_secret_keys_and_token_patterns(self) -> None:
        value = {
            "api_key": "secret-value",
            "message": "Authorization: Bearer abcdefghijklmnopqrstuvwxyz",
            "nested": {"token": "ghp_abcdefghijklmnopqrstuvwxyz123456"},
            "connection_string": "postgres://user:secret@db/prod",
            "text": "dsn=mysql://root:password@localhost/app",
        }
        cleaned = redact(value)
        self.assertEqual(cleaned["api_key"], "[REDACTED]")
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", cleaned["message"])
        self.assertEqual(cleaned["nested"]["token"], "[REDACTED]")
        self.assertEqual(cleaned["connection_string"], "[REDACTED]")
        self.assertNotIn("root:password", cleaned["text"])
        self.assertIn("[REDACTED]", cleaned["text"])


if __name__ == "__main__":
    unittest.main()
