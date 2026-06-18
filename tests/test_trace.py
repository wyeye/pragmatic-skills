from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from psp_trace import emit_event, finish_run, read_events, resolve_run, start_run, verify_run  # noqa: E402
from psp_util import ValidationError  # noqa: E402


class TraceTests(unittest.TestCase):
    def make_target(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        holder: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        return holder, Path(holder.name)

    def test_evidence_linked_success_trace_verifies(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-good")
        emit_event(target, "mode_selected", {"mode": "fast-patch"}, run_id="run-good")
        emit_event(target, "file_changed", {"path": "README.md"}, run_id="run-good")
        command = emit_event(
            target,
            "command_finished",
            {"command": "python -m unittest", "exit_code": 0, "purpose": "tests", "evidence_id": "ev-tests"},
            run_id="run-good",
        )
        emit_event(
            target,
            "verification_finished",
            {"status": "passed", "scope": "tests", "evidence": [command["id"]], "evidence_id": "ev-verify"},
            run_id="run-good",
        )
        emit_event(
            target,
            "claim",
            {"claim": "task_completed", "evidence": ["ev-verify"]},
            run_id="run-good",
        )
        summary = finish_run(target, run_id="run-good", status="completed")
        self.assertEqual(summary["verification"], "passed", summary)
        self.assertTrue(verify_run(target, run_id="run-good")["ok"])

    def test_claim_with_missing_evidence_fails(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-missing")
        emit_event(
            target,
            "claim",
            {"claim": "tests_passed", "evidence": ["missing"]},
            run_id="run-missing",
        )
        finish_run(target, run_id="run-missing", status="partial")
        result = verify_run(target, run_id="run-missing")
        self.assertFalse(result["ok"])
        self.assertTrue(any("missing evidence" in item for item in result["errors"]))

    def test_high_risk_action_requires_prior_scoped_approval(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-risk")
        emit_event(
            target,
            "high_risk_action_started",
            {"scope": "database:production"},
            run_id="run-risk",
        )
        finish_run(target, run_id="run-risk", status="failed")
        result = verify_run(target, run_id="run-risk")
        self.assertFalse(result["ok"])
        self.assertTrue(any("without prior matching approval" in item for item in result["errors"]))

    def test_prior_matching_approval_allows_high_risk_action(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-approved")
        emit_event(
            target,
            "safety_approval",
            {"scope": "database:staging", "approved": True},
            run_id="run-approved",
        )
        emit_event(
            target,
            "high_risk_action_started",
            {"scope": "database:staging"},
            run_id="run-approved",
        )
        finish_run(target, run_id="run-approved", status="completed")
        result = verify_run(target, run_id="run-approved")
        self.assertTrue(result["ok"], result["errors"])

    def test_later_change_makes_success_evidence_stale(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-stale")
        command = emit_event(
            target,
            "command_finished",
            {"command": "pytest", "exit_code": 0, "purpose": "tests"},
            run_id="run-stale",
        )
        verification = emit_event(
            target,
            "verification_finished",
            {"status": "passed", "scope": "tests", "evidence": [command["id"]]},
            run_id="run-stale",
        )
        emit_event(target, "file_changed", {"path": "src/app.py"}, run_id="run-stale")
        emit_event(
            target,
            "claim",
            {"claim": "task_completed", "evidence": [verification["id"]]},
            run_id="run-stale",
        )
        finish_run(target, run_id="run-stale", status="completed")
        result = verify_run(target, run_id="run-stale")
        self.assertFalse(result["ok"])
        self.assertTrue(any("stale" in item for item in result["errors"]))

    def test_sensitive_values_are_redacted_before_write(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-redact", metadata={"api_key": "super-secret"})
        emit_event(
            target,
            "artifact_inspected",
            {
                "authorization": "Bearer abcdefghijklmnopqrstuvwxyz",
                "text": "sk-abcdefghijklmnop postgres://user:db-password@db/prod",
                "dsn": "mysql://root:another-password@localhost/app",
            },
            run_id="run-redact",
        )
        _, run_path = resolve_run(target, "run-redact")
        raw = (run_path / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("super-secret", raw)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", raw)
        self.assertNotIn("sk-abcdefghijklmnop", raw)
        self.assertNotIn("db-password", raw)
        self.assertNotIn("another-password", raw)
        self.assertIn("[REDACTED]", raw)


    def test_artifact_or_untyped_success_command_cannot_prove_tests_passed(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-semantic-evidence")
        artifact = emit_event(
            target,
            "artifact_inspected",
            {"path": "README.md", "status": "passed"},
            run_id="run-semantic-evidence",
        )
        echo = emit_event(
            target,
            "command_finished",
            {"command": "echo ok", "exit_code": 0},
            run_id="run-semantic-evidence",
        )
        emit_event(
            target,
            "claim",
            {"claim": "tests_passed", "evidence": [artifact["id"], echo["id"]]},
            run_id="run-semantic-evidence",
        )
        finish_run(target, run_id="run-semantic-evidence", status="partial")
        result = verify_run(target, run_id="run-semantic-evidence")
        self.assertFalse(result["ok"])
        self.assertTrue(any("semantically matching" in item for item in result["errors"]))

    def test_typed_test_command_can_prove_tests_passed(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-typed-test")
        command = emit_event(
            target,
            "command_finished",
            {"command": "pytest -q", "exit_code": 0, "purpose": "tests"},
            run_id="run-typed-test",
        )
        emit_event(
            target,
            "claim",
            {"claim": "tests_passed", "evidence": [command["id"]]},
            run_id="run-typed-test",
        )
        finish_run(target, run_id="run-typed-test", status="completed")
        result = verify_run(target, run_id="run-typed-test")
        self.assertTrue(result["ok"], result["errors"])

    def test_verification_cannot_launder_wrong_evidence_type(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-launder")
        artifact = emit_event(
            target,
            "artifact_inspected",
            {"path": "README.md", "status": "passed"},
            run_id="run-launder",
        )
        verification = emit_event(
            target,
            "verification_finished",
            {"status": "passed", "scope": "tests", "evidence": [artifact["id"]]},
            run_id="run-launder",
        )
        emit_event(
            target,
            "claim",
            {"claim": "tests_passed", "evidence": [verification["id"]]},
            run_id="run-launder",
        )
        finish_run(target, run_id="run-launder", status="partial")
        result = verify_run(target, run_id="run-launder")
        self.assertFalse(result["ok"])
        self.assertTrue(any("upstream evidence" in item for item in result["errors"]))

    def test_latest_rejection_invalidates_earlier_approval(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-revoked")
        emit_event(target, "safety_approval", {"scope": "deploy:production", "approved": True}, run_id="run-revoked")
        emit_event(target, "safety_approval", {"scope": "deploy:production", "approved": False}, run_id="run-revoked")
        emit_event(target, "production_action_started", {"scope": "deploy:production"}, run_id="run-revoked")
        finish_run(target, run_id="run-revoked", status="failed")
        result = verify_run(target, run_id="run-revoked")
        self.assertFalse(result["ok"])
        self.assertTrue(any("rejected approval" in item for item in result["errors"]))

    def test_expired_approval_is_rejected(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-expired")
        emit_event(
            target,
            "safety_approval",
            {"scope": "database:production", "approved": True, "expires_at": "2000-01-01T00:00:00Z"},
            run_id="run-expired",
        )
        emit_event(target, "high_risk_action_started", {"scope": "database:production"}, run_id="run-expired")
        finish_run(target, run_id="run-expired", status="failed")
        result = verify_run(target, run_id="run-expired")
        self.assertFalse(result["ok"])
        self.assertTrue(any("expired approval" in item for item in result["errors"]))

    def test_duplicate_event_id_is_rejected(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-duplicate")
        emit_event(target, "mode_selected", {"mode": "fast-patch"}, run_id="run-duplicate", event_id="evt-custom")
        with self.assertRaises(ValidationError):
            emit_event(target, "skill_activated", {"skill": "fast-patch"}, run_id="run-duplicate", event_id="evt-custom")

    def test_finished_run_rejects_new_events(self) -> None:
        holder, target = self.make_target()
        self.addCleanup(holder.cleanup)
        start_run(target, run_id="run-finished")
        finish_run(target, run_id="run-finished", status="blocked")
        with self.assertRaises(ValidationError):
            emit_event(target, "mode_selected", {"mode": "exploration"}, run_id="run-finished")


if __name__ == "__main__":
    unittest.main()
