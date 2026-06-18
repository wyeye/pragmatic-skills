from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from _support import ROOT

TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from eval_runner import aggregate, discover_cases, grade_case, load_events, trace_path_for  # noqa: E402
from psp_eval import grade_results  # noqa: E402
from psp_schema import validation_errors  # noqa: E402
from psp_util import read_json  # noqa: E402


class SchemaContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schemas = {
            path.name: read_json(path)
            for path in sorted((ROOT / "schemas").glob("*.json"))
        }

    def assert_valid(self, schema_name: str, value: object, label: str) -> None:
        errors = validation_errors(value, self.schemas[schema_name])
        self.assertEqual(errors, [], f"{label}: {errors}")

    def test_manifest_and_all_sidecars_validate_against_declared_schemas(self) -> None:
        self.assert_valid("manifest.schema.json", read_json(ROOT / "skills/MANIFEST.json"), "manifest")
        sidecars = sorted((ROOT / "skills").glob("*/psp.skill.json"))
        self.assertEqual(len(sidecars), 19)
        for path in sidecars:
            with self.subTest(sidecar=path.parent.name):
                self.assert_valid("skill-sidecar.schema.json", read_json(path), path.as_posix())

    def test_eval_inputs_and_both_output_families_validate(self) -> None:
        cases = discover_cases(ROOT)
        for path, case in cases:
            with self.subTest(case=case["id"]):
                self.assert_valid("eval-case.schema.json", case, path.as_posix())

        captures = read_json(ROOT / "evals/samples/captures.json")
        for index, result in enumerate(captures["results"]):
            self.assert_valid("eval-result.schema.json", result, f"capture[{index}]")
        capture_report = grade_results(ROOT, ROOT / "evals/samples/captures.json")
        self.assert_valid("eval-capture-report.schema.json", capture_report, "capture report")
        for score in capture_report["scores"]:
            self.assert_valid("eval-capture-score.schema.json", score, "capture score")

        fixture_root = ROOT / "evals/fixtures/passing"
        grades = [
            grade_case(case, load_events(trace_path_for(fixture_root, str(case["id"]))))
            for _, case in cases
        ]
        for grade in grades:
            self.assert_valid("eval-grade.schema.json", grade.as_dict(), f"grade {grade.case_id}")
        self.assert_valid("eval-report.schema.json", aggregate(grades), "deterministic report")

    def test_corrupt_manifest_and_sidecar_are_rejected(self) -> None:
        manifest = json.loads((ROOT / "skills/MANIFEST.json").read_text(encoding="utf-8"))
        manifest.pop("entry_skill")
        self.assertTrue(validation_errors(manifest, self.schemas["manifest.schema.json"]))

        sidecar = read_json(ROOT / "skills/triage/psp.skill.json")
        sidecar["schema"] = "psp.skill-sidecar/v1"
        self.assertTrue(validation_errors(sidecar, self.schemas["skill-sidecar.schema.json"]))

    def test_schema_identifiers_are_unique(self) -> None:
        identifiers = [schema.get("$id") for schema in self.schemas.values()]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(all(isinstance(item, str) and item for item in identifiers))


if __name__ == "__main__":
    unittest.main()
