from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from eval_runner import aggregate, discover_cases, grade_case, load_events  # noqa: E402
from psp_eval import framework_self_test, load_cases  # noqa: E402


class EvalTests(unittest.TestCase):
    def test_case_set_is_valid_and_unique(self) -> None:
        cases, errors = load_cases(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(len(cases), 20)
        self.assertEqual(len({case["id"] for case in cases}), 20)

    def test_framework_self_test(self) -> None:
        result = framework_self_test(ROOT)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["cases"], 20)
        self.assertEqual(result["minimum_synthetic_score"], 100.0)

    def test_known_good_fixture_traces_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOLS / "eval_runner.py"), "--root", str(ROOT), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        report = json.loads(completed.stdout)
        self.assertEqual(report["case_count"], 20)
        self.assertEqual(report["failed"], 0)
        self.assertEqual(report["average_score"], 100.0)

    def test_eval_runner_summary_omits_per_case_payload(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOLS / "eval_runner.py"), "--root", str(ROOT), "--self-test", "--summary"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        report = json.loads(completed.stdout)
        self.assertEqual(report["case_count"], 20)
        self.assertEqual(report["failed"], 0)
        self.assertNotIn("results", report)

    def test_bad_trace_cannot_pass_evidence_case(self) -> None:
        case_path = ROOT / "evals" / "cases" / "fast-patch-readme-typo.json"
        case = json.loads(case_path.read_text(encoding="utf-8"))
        events = [
            {"event": "mode_selected", "mode": "fast-patch", "event_id": "e1"},
            {"event": "skill_activated", "skill": "using-pragmatic-skills", "event_id": "e2"},
            {"event": "skill_activated", "skill": "triage", "event_id": "e3"},
            {"event": "skill_activated", "skill": "fast-patch", "event_id": "e4"},
            {"event": "file_changed", "path": "README.md", "event_id": "e5"},
            {"event": "claim", "claim_type": "task_completed", "evidence": [], "event_id": "e6"},
            {"event": "run_finished", "status": "completed", "event_id": "e7"},
        ]
        grade = grade_case(case, events, minimum_score=80.0)
        self.assertFalse(grade.passed)
        self.assertLess(grade.score, 80.0)

    def test_eval_runner_writes_json_markdown_and_html(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(TOOLS / "eval_runner.py"),
                    "--root",
                    str(ROOT),
                    "--self-test",
                    "--output-dir",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
            self.assertTrue((out / "eval-results.json").is_file())
            self.assertTrue((out / "eval-report.md").is_file())
            self.assertTrue((out / "eval-report.html").is_file())


if __name__ == "__main__":
    unittest.main()
