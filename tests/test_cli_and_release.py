from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import Dict, Optional

from _support import ROOT


class CliAndReleaseTests(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Path = ROOT, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "tools/psp.py"), *args],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_version_and_package_check(self) -> None:
        version = self.run_cli("--version")
        self.assertEqual(version.returncode, 0)
        self.assertEqual(version.stdout.strip(), "2.0.2")
        checked = self.run_cli("verify-package", "--target", str(ROOT), "--json")
        self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)
        self.assertIn('"ok": true', checked.stdout)

    def test_package_root_uses_global_runtime_env_not_project_vendored_package(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            (project / ".psp").mkdir()
            (project / ".psp/package.zip").write_bytes(b"not a runtime package")
            env = {**os.environ, "PSP_HOME": str(ROOT)}
            checked = self.run_cli("verify-package", "--json", cwd=project, env=env)
            self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)
            self.assertIn('"ok": true', checked.stdout)

    def test_runtime_install_status_and_env_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw) / "project"
            runtime_home = Path(raw) / "runtime-current"
            project.mkdir()

            dry = self.run_cli("runtime", "install", "--home", str(runtime_home), "--dry-run", "--json")
            self.assertEqual(dry.returncode, 0, dry.stderr + dry.stdout)
            self.assertFalse(runtime_home.exists())
            self.assertTrue(json.loads(dry.stdout)["dry_run"])

            installed = self.run_cli("runtime", "install", "--home", str(runtime_home), "--json")
            self.assertEqual(installed.returncode, 0, installed.stderr + installed.stdout)
            payload = json.loads(installed.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["home"], str(runtime_home.resolve()))
            self.assertTrue((runtime_home / "tools/psp.py").is_file())
            self.assertTrue((runtime_home / "runtime.json").is_file())
            self.assertFalse((runtime_home / ".psp").exists())

            status = self.run_cli("runtime", "status", "--home", str(runtime_home), "--json")
            self.assertEqual(status.returncode, 0, status.stderr + status.stdout)
            status_payload = json.loads(status.stdout)
            self.assertTrue(status_payload["installed"])
            self.assertEqual(status_payload["version"], "2.0.2")

            env = {**os.environ, "PSP_HOME": str(runtime_home)}
            checked = self.run_cli("verify-package", "--json", cwd=project, env=env)
            self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)
            self.assertIn('"ok": true', checked.stdout)

    def test_runtime_install_rejects_source_nested_home(self) -> None:
        nested_home = ROOT / "build/runtime-under-source"
        result = self.run_cli("runtime", "install", "--home", str(nested_home), "--json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("must not be inside the source package", result.stdout)

    def test_runtime_install_force_replaces_existing_non_psp_home(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            runtime_home = Path(raw) / "runtime-current"
            runtime_home.mkdir()
            (runtime_home / "old.txt").write_text("user content\n", encoding="utf-8")

            rejected = self.run_cli("runtime", "install", "--home", str(runtime_home), "--json")
            self.assertEqual(rejected.returncode, 2)
            self.assertIn("pass --force to replace it", rejected.stdout)
            self.assertTrue((runtime_home / "old.txt").is_file())

            installed = self.run_cli("runtime", "install", "--home", str(runtime_home), "--force", "--json")
            self.assertEqual(installed.returncode, 0, installed.stderr + installed.stdout)
            payload = json.loads(installed.stdout)
            self.assertTrue(payload["ok"])
            self.assertTrue((runtime_home / "tools/psp.py").is_file())
            self.assertTrue((runtime_home / "runtime.json").is_file())
            self.assertFalse((runtime_home / "old.txt").exists())

    def test_runtime_status_reports_file_home_as_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            runtime_home = Path(raw) / "runtime-current"
            runtime_home.write_text("not a directory\n", encoding="utf-8")

            status = self.run_cli("runtime", "status", "--home", str(runtime_home), "--json")
            self.assertEqual(status.returncode, 1, status.stderr + status.stdout)
            payload = json.loads(status.stdout)
            self.assertFalse(payload["ok"])
            self.assertFalse(payload["installed"])
            self.assertEqual(payload["issues"][0]["code"], "runtime-incomplete")

    def test_runtime_install_force_replaces_existing_file_home_without_leftover_backup(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            parent = Path(raw)
            runtime_home = parent / "runtime-current"
            runtime_home.write_text("not a directory\n", encoding="utf-8")

            installed = self.run_cli("runtime", "install", "--home", str(runtime_home), "--force", "--json")
            self.assertEqual(installed.returncode, 0, installed.stderr + installed.stdout)
            self.assertTrue((runtime_home / "tools/psp.py").is_file())
            self.assertFalse(list(parent.glob(".runtime-current.previous-*")))

    def test_release_zip_is_deterministic_and_self_verifying(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)
            command = [
                sys.executable,
                str(ROOT / "tools/package_release.py"),
                "--root",
                str(ROOT),
                "--output-dir",
                str(output),
                "--name",
                "test-release.zip",
            ]
            first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
            archive = output / "test-release.zip"
            first_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
            self.assertEqual(first_digest, hashlib.sha256(archive.read_bytes()).hexdigest())
            self.assertEqual((output / "test-release.zip.sha256").read_text().split()[0], first_digest)

            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                self.assertIn("test-release/README.md", names)
                self.assertIn("test-release/tools/psp.py", names)
                self.assertNotIn("test-release/.psp/install.json", names)
                self.assertFalse(any("__pycache__" in name for name in names))
                bundle.extractall(output / "unpacked")
            unpacked = output / "unpacked/test-release"
            checked = subprocess.run(
                [sys.executable, str(unpacked / "tools/psp.py"), "verify-package", "--target", str(unpacked), "--json"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)


if __name__ == "__main__":
    unittest.main()
