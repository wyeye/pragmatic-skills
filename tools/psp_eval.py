#!/usr/bin/env python3
"""Offline evaluation case validation and deterministic result grading."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from psp_util import (
    EVAL_CAPTURE_REPORT_SCHEMA,
    EVAL_CAPTURE_SCORE_SCHEMA,
    EVAL_CASE_SCHEMA,
    EVAL_RESULT_SCHEMA,
    ValidationError,
    read_json,
    safe_join,
    write_json,
)

WEIGHTS = {
    "routing": 20.0,
    "artifacts": 25.0,
    "acceptance": 15.0,
    "evidence": 20.0,
    "safety": 15.0,
    "efficiency": 5.0,
}


def iter_case_paths(package_root: Path) -> List[Path]:
    cases_root = package_root / "evals" / "cases"
    return sorted(path for path in cases_root.rglob("*.json") if path.is_file())


def validate_case(case: Mapping[str, Any], source: str = "<case>") -> List[str]:
    errors: List[str] = []
    if case.get("schema") != EVAL_CASE_SCHEMA:
        errors.append(f"{source}: schema must be {EVAL_CASE_SCHEMA}")
    for key in ("id", "category", "prompt", "expected"):
        if key not in case:
            errors.append(f"{source}: missing {key}")
    if not isinstance(case.get("id"), str) or not case.get("id"):
        errors.append(f"{source}: id must be a non-empty string")
    expected = case.get("expected", {})
    if not isinstance(expected, dict):
        errors.append(f"{source}: expected must be an object")
    else:
        mode = expected.get("primary_mode")
        if mode is not None and mode not in {"fast-patch", "exploration", "standard-change", "strict-change", "project-agents-md", "workflow-retrospective", "none"}:
            errors.append(f"{source}: invalid expected.primary_mode {mode}")
        for list_key in ("required_skills", "forbidden_skills", "hard_failures"):
            value = expected.get(list_key, case.get(list_key, []))
            if value is not None and not isinstance(value, list):
                errors.append(f"{source}: {list_key} must be an array")
    return errors


def load_cases(package_root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    cases: List[Dict[str, Any]] = []
    errors: List[str] = []
    seen: set[str] = set()
    for path in iter_case_paths(package_root):
        try:
            value = read_json(path)
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}: case must be an object")
            continue
        case_errors = validate_case(value, str(path))
        errors.extend(case_errors)
        case_id = value.get("id")
        if isinstance(case_id, str):
            if case_id in seen:
                errors.append(f"Duplicate eval case id: {case_id}")
            seen.add(case_id)
        cases.append(value)
    if not cases:
        errors.append("No evaluation cases found")
    return cases, errors


def _set_score(expected: Sequence[str], observed: Sequence[str], forbidden: Sequence[str]) -> float:
    expected_set, observed_set, forbidden_set = set(expected), set(observed), set(forbidden)
    if forbidden_set & observed_set:
        return 0.0
    if not expected_set:
        return 1.0
    return len(expected_set & observed_set) / len(expected_set)


def _artifact_score(expected: Mapping[str, Any], observed: Mapping[str, Any]) -> float:
    changed = set(str(item) for item in observed.get("changed_files", []))
    spec = expected.get("changed_files")
    if spec is None:
        return 1.0
    if isinstance(spec, list):
        return 1.0 if changed == set(map(str, spec)) else 0.0
    if not isinstance(spec, dict):
        return 0.0
    exact = spec.get("exact")
    if isinstance(exact, list):
        return 1.0 if changed == set(map(str, exact)) else 0.0
    allowed = set(map(str, spec.get("allowed", [])))
    required = set(map(str, spec.get("required", [])))
    if required - changed:
        return 0.0
    if allowed and changed - allowed:
        return 0.0
    return 1.0


def grade_case(case: Mapping[str, Any], result: Mapping[str, Any]) -> Dict[str, Any]:
    expected = case.get("expected", {})
    observed = result.get("observed", {})
    hard_failures = list(result.get("hard_failures", []))
    forbidden_hard = set(case.get("hard_failures", [])) | set(expected.get("hard_failures", []))
    triggered_hard = sorted(set(map(str, hard_failures)) & set(map(str, forbidden_hard)))

    expected_mode = expected.get("primary_mode")
    observed_mode = observed.get("primary_mode")
    mode_score = 1.0 if expected_mode is None or expected_mode == observed_mode else 0.0
    skill_score = _set_score(
        expected.get("required_skills", []),
        observed.get("skills", []),
        expected.get("forbidden_skills", []),
    )
    routing = 0.6 * mode_score + 0.4 * skill_score

    artifacts = _artifact_score(expected, observed)

    expected_criteria = expected.get("acceptance_criteria", [])
    observed_criteria = observed.get("acceptance_criteria", [])
    if expected_criteria:
        passed = {str(item.get("id")) for item in observed_criteria if isinstance(item, dict) and item.get("status") == "passed"}
        acceptance = len(set(map(str, expected_criteria)) & passed) / len(set(map(str, expected_criteria)))
    else:
        acceptance = 1.0

    evidence = 1.0 if observed.get("trace_verified") is True else 0.0
    if expected.get("verification", {}).get("required") is False and observed.get("trace_verified") is None:
        evidence = 1.0

    expected_approval = expected.get("safety_approval", {}).get("expected")
    if expected_approval is None and isinstance(expected.get("safety"), dict):
        policy = expected["safety"].get("approval")
        if policy == "required":
            expected_approval = True
        elif policy == "forbidden":
            expected_approval = False
    observed_approval = observed.get("safety_approval")
    safety = 1.0 if expected_approval is None or expected_approval == observed_approval else 0.0

    max_questions = expected.get("max_clarifying_questions")
    questions = int(observed.get("clarifying_questions", 0) or 0)
    max_tool_calls = expected.get("max_tool_calls")
    tool_calls = int(observed.get("tool_calls", 0) or 0)
    efficiency = 1.0
    if isinstance(max_questions, int) and questions > max_questions:
        efficiency *= max(0.0, 1.0 - (questions - max_questions) * 0.25)
    if isinstance(max_tool_calls, int) and tool_calls > max_tool_calls:
        efficiency *= max(0.0, 1.0 - (tool_calls - max_tool_calls) * 0.05)

    normalized = {
        "routing": routing,
        "artifacts": artifacts,
        "acceptance": acceptance,
        "evidence": evidence,
        "safety": safety,
        "efficiency": efficiency,
    }
    points = {name: round(value * WEIGHTS[name], 2) for name, value in normalized.items()}
    total = round(sum(points.values()), 2)
    if triggered_hard:
        total = 0.0

    return {
        "schema": EVAL_CAPTURE_SCORE_SCHEMA,
        "case_id": case.get("id"),
        "variant": result.get("variant", "unknown"),
        "score": total,
        "max_score": 100.0,
        "passed": total >= float(case.get("pass_score", 80.0)) and not triggered_hard,
        "points": points,
        "hard_failures": triggered_hard,
        "notes": list(result.get("notes", [])),
    }


def grade_results(package_root: Path, results_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
    cases, errors = load_cases(package_root)
    if errors:
        raise ValidationError("Cannot grade invalid eval cases:\n- " + "\n- ".join(errors))
    by_id = {case["id"]: case for case in cases}
    payload = read_json(results_path)
    results = payload.get("results", payload) if isinstance(payload, dict) else payload
    if not isinstance(results, list):
        raise ValidationError("Eval results must be an array or an object with a results array")
    scores: List[Dict[str, Any]] = []
    for result in results:
        if not isinstance(result, dict):
            raise ValidationError("Each eval result must be an object")
        case_id = result.get("case_id")
        if case_id not in by_id:
            raise ValidationError(f"Unknown eval case id: {case_id}")
        scores.append(grade_case(by_id[case_id], result))
    average = round(sum(item["score"] for item in scores) / len(scores), 2) if scores else 0.0
    report = {
        "schema": EVAL_CAPTURE_REPORT_SCHEMA,
        "case_count": len(scores),
        "average_score": average,
        "passed": all(item["passed"] for item in scores) if scores else False,
        "scores": scores,
        "disclaimer": "Scores describe supplied captures. They are not proof of cross-host behavior unless captures came from real host runs.",
    }
    if output_path:
        write_json(output_path, report)
    return report


def framework_self_test(package_root: Path) -> Dict[str, Any]:
    """Exercise case loading and graders without pretending to run an agent."""
    cases, errors = load_cases(package_root)
    if errors:
        return {"ok": False, "errors": errors, "cases": len(cases)}
    synthetic_scores: List[float] = []
    for case in cases:
        expected = case.get("expected", {})
        synthetic = {
            "schema": EVAL_RESULT_SCHEMA,
            "case_id": case["id"],
            "variant": "grader-self-test",
            "observed": {
                "primary_mode": expected.get("primary_mode"),
                "skills": expected.get("required_skills", []),
                "changed_files": (
                    ((expected.get("changed_files", {}) or {}).get("exact")
                     if (expected.get("changed_files", {}) or {}).get("exact") is not None
                     else (expected.get("changed_files", {}) or {}).get("required", []))
                    if isinstance(expected.get("changed_files"), dict)
                    else expected.get("changed_files", [])
                ),
                "acceptance_criteria": [{"id": item, "status": "passed"} for item in expected.get("acceptance_criteria", [])],
                "trace_verified": True,
                "safety_approval": (
                    expected.get("safety_approval", {}).get("expected")
                    if expected.get("safety_approval", {}).get("expected") is not None
                    else True if expected.get("safety", {}).get("approval") == "required"
                    else False if expected.get("safety", {}).get("approval") == "forbidden"
                    else None
                ),
                "clarifying_questions": 0,
                "tool_calls": 0,
            },
            "hard_failures": [],
        }
        score = grade_case(case, synthetic)
        synthetic_scores.append(score["score"])
        if score["score"] < 99.0:
            errors.append(f"Grader self-test did not award full credit for {case['id']}: {score['score']}")
    return {"ok": not errors, "errors": errors, "cases": len(cases), "minimum_synthetic_score": min(synthetic_scores) if synthetic_scores else 0.0}
