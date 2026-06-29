from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from _support import ROOT
from psp_installer import install, load_state, rollback, uninstall, verify_install, verify_package
from psp_util import ValidationError


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.target = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def install_minimal(self, **kwargs):
        return install(ROOT, self.target, hosts_spec="minimal", **kwargs)

    def test_package_verification(self) -> None:
        result = verify_package(ROOT)
        self.assertTrue(result["ok"], result["issues"])
        self.assertEqual(result["version"], "2.0.2")
        self.assertEqual(result["skill_count"], 19)
        self.assertGreaterEqual(result["eval_case_count"], 18)

    def test_fresh_install_is_idempotent_and_uninstall_preserves_user_content(self) -> None:
        original = "# Project instructions\n\nKeep this user-owned line.\n"
        (self.target / "AGENTS.md").write_text(original, encoding="utf-8")

        first = self.install_minimal()
        self.assertTrue(first["ok"])
        self.assertGreater(first["change_count"], 0)
        self.assertIn("Keep this user-owned line.", (self.target / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertTrue(verify_install(self.target)["ok"])
        managed_files = load_state(self.target, required=True)["managed_files"]
        self.assertEqual(set(managed_files), {".agents/skills/using-pragmatic-skills/SKILL.md"})
        self.assertTrue((self.target / ".agents/skills/using-pragmatic-skills/SKILL.md").is_file())
        self.assertFalse((self.target / "skills").exists())
        self.assertFalse((self.target / "reference").exists())
        self.assertFalse((self.target / ".psp/bin").exists())
        self.assertFalse((self.target / ".psp/package.zip").exists())
        self.assertFalse((self.target / ".psp/legal").exists())
        self.assertFalse((self.target / ".psp/schemas").exists())

        second = self.install_minimal()
        self.assertTrue(second["ok"])
        self.assertEqual(second["change_count"], 0)
        self.assertIsNone(second["backup"])

        diagnosis = verify_install(self.target)
        self.assertTrue(diagnosis["ok"], diagnosis.get("issues"))

        removed = uninstall(self.target)
        self.assertTrue(removed["ok"])
        self.assertFalse((self.target / ".psp/install.json").exists())
        self.assertEqual((self.target / "AGENTS.md").read_text(encoding="utf-8"), original)
        self.assertFalse((self.target / ".agents/skills/using-pragmatic-skills/SKILL.md").exists())

    def test_dry_run_has_no_managed_writes(self) -> None:
        result = self.install_minimal(dry_run=True)
        self.assertTrue(result["ok"])
        self.assertGreater(result["change_count"], 0)
        self.assertFalse((self.target / ".psp").exists())
        self.assertFalse((self.target / ".psp/install.json").exists())
        self.assertFalse((self.target / ".agents").exists())
        self.assertFalse((self.target / "skills").exists())
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_dry_run_does_not_create_missing_target_directory(self) -> None:
        missing = self.target / "missing"
        result = install(ROOT, missing, hosts_spec="minimal", dry_run=True)
        self.assertTrue(result["ok"])
        self.assertGreater(result["change_count"], 0)
        self.assertFalse(missing.exists())

    def test_user_modified_managed_file_creates_conflict_then_force_recovers(self) -> None:
        self.install_minimal()
        managed = self.target / ".agents/skills/using-pragmatic-skills/SKILL.md"
        managed.write_text(managed.read_text(encoding="utf-8") + "\nUSER CHANGE\n", encoding="utf-8")

        conflicted = self.install_minimal()
        self.assertFalse(conflicted["ok"])
        self.assertGreaterEqual(conflicted["conflict_count"], 1)
        self.assertIn("USER CHANGE", managed.read_text(encoding="utf-8"))
        self.assertIsNotNone(conflicted["conflict_path"])
        conflict_dir = self.target / str(conflicted["conflict_path"])
        self.assertTrue((conflict_dir / "conflicts.json").is_file())

        forced = self.install_minimal(force=True)
        self.assertTrue(forced["ok"])
        self.assertNotIn("USER CHANGE", managed.read_text(encoding="utf-8"))
        self.assertTrue(verify_install(self.target)["ok"])

    def test_rollback_restores_exact_pre_transaction_content(self) -> None:
        self.install_minimal()
        managed = self.target / ".agents/skills/using-pragmatic-skills/SKILL.md"
        modified = managed.read_text(encoding="utf-8") + "\nLOCAL PATCH BEFORE FORCE\n"
        managed.write_text(modified, encoding="utf-8")

        forced = self.install_minimal(force=True)
        self.assertTrue(forced["ok"])
        backup_id = forced["backup"]
        self.assertIsNotNone(backup_id)
        self.assertNotEqual(managed.read_text(encoding="utf-8"), modified)

        restored = rollback(self.target, backup_id=backup_id)
        self.assertTrue(restored["ok"])
        self.assertEqual(managed.read_text(encoding="utf-8"), modified)

    def test_auto_detects_only_present_host_markers(self) -> None:
        (self.target / ".claude").mkdir()
        (self.target / ".cursor").mkdir()
        result = install(ROOT, self.target, hosts_spec="auto")
        self.assertTrue(result["ok"])
        self.assertEqual(set(result["hosts"]), {"agents", "claude", "cursor"})
        self.assertTrue((self.target / "CLAUDE.md").is_file())
        self.assertTrue((self.target / ".cursor/rules/pragmatic-skills-pack.mdc").is_file())
        self.assertFalse((self.target / "GEMINI.md").exists())

    def test_malformed_managed_markers_are_not_guessed(self) -> None:
        (self.target / "AGENTS.md").write_text(
            "<!-- PSP:BEGIN -->\nfirst\n<!-- PSP:BEGIN -->\nsecond\n<!-- PSP:END -->\n",
            encoding="utf-8",
        )
        result = self.install_minimal()
        self.assertFalse(result["ok"])
        self.assertTrue(any(item["status"] == "conflict-malformed-block" for item in result["statuses"]))
        self.assertFalse((self.target / ".psp/install.json").exists())

    def test_symlink_escape_is_rejected_without_touching_outside(self) -> None:
        with tempfile.TemporaryDirectory() as outside_raw:
            outside = Path(outside_raw)
            try:
                (self.target / ".agents").mkdir()
                os.symlink(outside, self.target / ".agents/skills", target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            with self.assertRaises(ValidationError):
                self.install_minimal()
            self.assertEqual(list(outside.iterdir()), [])


    def test_managed_block_preserves_crlf_bom_mode_and_exact_uninstall_bytes(self) -> None:
        original = b"\xef\xbb\xbf# Private instructions\r\n\r\nKeep this line.\r\n"
        path = self.target / "AGENTS.md"
        path.write_bytes(original)
        path.chmod(0o600)

        installed = self.install_minimal()
        self.assertTrue(installed["ok"])
        installed_bytes = path.read_bytes()
        self.assertTrue(installed_bytes.startswith(b"\xef\xbb\xbf"))
        self.assertIn(b"<!-- PSP:BEGIN -->\r\n", installed_bytes)
        self.assertEqual(installed_bytes.replace(b"\r\n", b"").count(b"\n"), 0)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

        removed = uninstall(self.target)
        self.assertTrue(removed["ok"])
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_verify_package_rejects_missing_declared_adapter_resource(self) -> None:
        package_copy = self.target / "package-copy"
        shutil.copytree(ROOT, package_copy, ignore=shutil.ignore_patterns("__pycache__", "build", ".psp"))
        (package_copy / "adapters/cursor/rules/pragmatic-skills-pack.mdc").unlink()
        result = verify_package(package_copy)
        self.assertFalse(result["ok"])
        self.assertTrue(any(item["code"] == "adapter-source-missing" for item in result["issues"]))

    def test_upgrade_without_hosts_preserves_explicit_host_selection(self) -> None:
        first = install(ROOT, self.target, hosts_spec="claude,cursor")
        self.assertTrue(first["ok"])
        second = install(ROOT, self.target, hosts_spec=None, require_existing=True)
        self.assertTrue(second["ok"])
        self.assertEqual(set(second["hosts"]), {"claude", "cursor"})
        self.assertTrue((self.target / ".cursor/rules/pragmatic-skills-pack.mdc").is_file())

    def test_upgrade_removes_legacy_project_vendored_runtime_files(self) -> None:
        installed = self.install_minimal()
        self.assertTrue(installed["ok"])
        state = load_state(self.target, required=True)
        assert state is not None
        legacy_paths = {
            ".psp/bin/psp.py": b"legacy cli\n",
            ".psp/package.zip": b"legacy package\n",
            ".psp/legal/LICENSE": b"legacy license\n",
            ".psp/schemas/install-state.schema.json": b"{}\n",
            "skills/triage/SKILL.md": b"legacy skill\n",
            "reference/PROJECT-PROFILE.template.md": b"legacy reference\n",
        }
        for rel, data in legacy_paths.items():
            path = self.target / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            state["managed_files"][rel] = {
                "sha256": hashlib.sha256(data).hexdigest(),
                "source": "legacy",
                "mode": "0o644",
            }
        (self.target / ".psp/install.json").write_text(json.dumps(state), encoding="utf-8")

        upgraded = self.install_minimal()
        self.assertTrue(upgraded["ok"])
        for rel in legacy_paths:
            self.assertFalse((self.target / rel).exists(), rel)
        current_state = load_state(self.target, required=True)
        assert current_state is not None
        self.assertFalse(any(rel in current_state["managed_files"] for rel in legacy_paths))

    def test_malicious_state_path_is_rejected(self) -> None:
        state_dir = self.target / ".psp"
        state_dir.mkdir()
        (state_dir / "install.json").write_text(
            json.dumps(
                {
                    "schema": "psp.install/v2",
                    "version": "2.0.2",
                    "managed_files": {"../escape": {"sha256": "x"}},
                    "managed_blocks": {},
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaises(ValidationError):
            load_state(self.target, required=True)


if __name__ == "__main__":
    unittest.main()
