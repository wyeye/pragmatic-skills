from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from _support import ROOT


class CliAndReleaseTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "tools/psp.py"), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_version_and_package_check(self) -> None:
        version = self.run_cli("--version")
        self.assertEqual(version.returncode, 0)
        self.assertEqual(version.stdout.strip(), "2.0.1")
        checked = self.run_cli("verify-package", "--target", str(ROOT), "--json")
        self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)
        self.assertIn('"ok": true', checked.stdout)

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
