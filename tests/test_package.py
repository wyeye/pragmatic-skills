from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from psp_installer import verify_package  # noqa: E402
from psp_util import PACKAGE_VERSION, build_skill_manifest, read_json, validate_skill_graph  # noqa: E402


class PackageTests(unittest.TestCase):
    def test_package_verifies(self) -> None:
        result = verify_package(ROOT)
        self.assertTrue(result["ok"], result["issues"])
        self.assertEqual(result["version"], "2.0.2")
        self.assertEqual(result["skill_count"], 19)
        self.assertEqual(result["eval_case_count"], 20)

    def test_manifest_is_deterministic_and_graph_is_reachable(self) -> None:
        expected = build_skill_manifest(ROOT)
        actual = read_json(ROOT / "skills" / "MANIFEST.json")
        self.assertEqual(actual, expected)
        self.assertEqual([], [item for item in validate_skill_graph(ROOT, actual) if item["severity"] == "error"])
        self.assertEqual(actual["entry_skill"], "skills/using-pragmatic-skills/SKILL.md")

    def test_public_check_script(self) -> None:
        completed = subprocess.run(
            [str(ROOT / "verify.sh"), "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])

    def test_single_version_source(self) -> None:
        self.assertEqual(PACKAGE_VERSION, "2.0.2")
        self.assertIn('version = "2.0.2"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        hosts = read_json(ROOT / "adapters" / "HOSTS.json")
        self.assertEqual(hosts["version"], PACKAGE_VERSION)
        self.assertEqual(hosts["default"], "auto")

    def test_github_actions_are_pinned_to_full_commits(self) -> None:
        action_pattern = re.compile(r"^\s*(?:-\s*)?uses:\s*([^#\s]+)", re.MULTILINE)
        for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
            for action in action_pattern.findall(workflow.read_text(encoding="utf-8")):
                if action.startswith("./"):
                    continue
                self.assertRegex(
                    action,
                    r"^[^@]+@[0-9a-f]{40}$",
                    f"{workflow.relative_to(ROOT)} uses a movable or non-SHA action reference: {action}",
                )


if __name__ == "__main__":
    unittest.main()
