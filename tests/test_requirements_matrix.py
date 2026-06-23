from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RequirementsMatrixContractTests(unittest.TestCase):
    def test_requirements_skill_defines_trigger_columns_and_negative_boundary(self) -> None:
        skill = (ROOT / "skills/requirements-and-design/SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "Behavior and state matrix",
            "multiple entry points or system boundaries",
            "Reads / source of truth",
            "External platform or API effect",
            "Device or event side effect",
            "Sync / reconciliation / backfill behavior",
            "Query visibility / post-condition",
            "Every cell must be evidence-backed",
            "single, fully specified path",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

        sidecar = json.loads(
            (ROOT / "skills/requirements-and-design/psp.skill.json").read_text(encoding="utf-8")
        )
        positives = "\n".join(sidecar["activation"]["positive"])
        negatives = "\n".join(sidecar["activation"]["negative"])
        self.assertIn("multiple entry points or system boundaries", positives)
        self.assertIn("client/H5", positives)
        self.assertIn("single-path fully specified state change", negatives)
        self.assertIn("behavior/state matrix", sidecar["outputs"])
        self.assertIn("cross-path invariants", sidecar["outputs"])

    def test_matrix_contract_reaches_plan_test_verify_and_review(self) -> None:
        expected = {
            "writing-plans": ("every `bm-*` row", "explicit no-change rationale"),
            "tdd": ("effect must occur", "must not occur"),
            "verification": ("`verified`, `partially verified`, or `unverified`", "one verified row does not prove its adjacent rows"),
            "review": ("omitted adjacent entry point", "resurrects deleted state"),
        }
        for skill_name, phrases in expected.items():
            text = (ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8").lower()
            for phrase in phrases:
                with self.subTest(skill=skill_name, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_positive_and_negative_eval_boundaries_are_explicit(self) -> None:
        positive = json.loads((ROOT / "evals/cases/multi-system-contact-state-matrix.json").read_text(encoding="utf-8"))
        negative = json.loads((ROOT / "evals/cases/local-only-archive-filter.json").read_text(encoding="utf-8"))
        self.assertIn("requirements-and-design", positive["expected"]["required_skills"])
        self.assertEqual(positive["expected"]["changed_files"]["exact"], [])
        self.assertEqual(positive["expected"]["final_status"], "blocked")
        self.assertEqual(positive["expected"]["max_clarifying_questions"], 1)
        self.assertIn("requirements-and-design", negative["expected"]["forbidden_skills"])
        self.assertEqual(negative["expected"]["max_clarifying_questions"], 0)

        events = [
            json.loads(line)
            for line in (ROOT / "evals/fixtures/passing/multi-system-contact-state-matrix/events.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        matrix_events = [event for event in events if event.get("event") == "behavior_matrix_recorded"]
        self.assertEqual(len(matrix_events), 1)
        self.assertGreaterEqual(len(matrix_events[0].get("rows", [])), 3)
        self.assertGreaterEqual(len(matrix_events[0].get("unknowns", [])), 1)


if __name__ == "__main__":
    unittest.main()
