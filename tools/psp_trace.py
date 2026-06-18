#!/usr/bin/env python3
"""Local, opt-in JSONL traces with evidence and safety-order verification."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from psp_util import (
    TRACE_SCHEMA,
    FileLock,
    ValidationError,
    claim_requires_success,
    evidence_supports_claim,
    read_json,
    redact,
    safe_join,
    timestamp_id,
    utc_now,
    verification_source_succeeded,
    write_json,
)

TRACE_DIR = ".psp/runs"
EVENTS_FILE = "events.jsonl"
SUMMARY_FILE = "summary.json"
EVENT_LOCK_FILE = ".events.lock"
EVENT_NAME_RE = re.compile(r"[a-z][a-z0-9_]{0,99}")
ID_RE = re.compile(r"[A-Za-z0-9._-]{1,100}")

CHANGE_EVENTS = {"file_changed", "files_changed", "artifact_changed", "patch_applied"}
APPROVAL_EVENTS = {"safety_approval", "user_approval"}
HIGH_RISK_EVENTS = {"high_risk_action_started", "destructive_action_started", "production_action_started"}


def _runs_root(target: Path) -> Path:
    return safe_join(target, TRACE_DIR, reject_final_symlink=False)


def list_runs(target: Path) -> List[str]:
    root = _runs_root(target)
    if not root.exists():
        return []
    return sorted(
        (path.name for path in root.iterdir() if path.is_dir() and not path.is_symlink() and ID_RE.fullmatch(path.name)),
        reverse=True,
    )


def resolve_run(target: Path, run_id: Optional[str]) -> Tuple[str, Path]:
    if run_id:
        if not ID_RE.fullmatch(run_id):
            raise ValidationError(f"Invalid run id: {run_id}")
        return run_id, safe_join(target, f"{TRACE_DIR}/{run_id}", reject_final_symlink=True)
    runs = list_runs(target)
    if not runs:
        raise ValidationError("No PSP trace runs found")
    return runs[0], safe_join(target, f"{TRACE_DIR}/{runs[0]}", reject_final_symlink=True)


def _append_event(run_path: Path, event: Mapping[str, Any]) -> None:
    events_path = run_path / EVENTS_FILE
    line = json.dumps(redact(dict(event)), ensure_ascii=False, sort_keys=True) + "\n"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(events_path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def _validate_event_name(event_name: str) -> None:
    if not EVENT_NAME_RE.fullmatch(event_name):
        raise ValidationError(f"Invalid event name: {event_name}")


def _validate_event_id(event_id: str) -> None:
    if not ID_RE.fullmatch(event_id):
        raise ValidationError(f"Invalid event id: {event_id}")


def start_run(target: Path, run_id: Optional[str] = None, metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    target = target.resolve()
    run_id = run_id or timestamp_id()
    _validate_event_id(run_id)
    _, run_path = resolve_run(target, run_id)
    if run_path.exists():
        raise ValidationError(f"Trace run already exists: {run_id}")
    run_path.mkdir(parents=True, mode=0o700)
    event = {
        "schema": TRACE_SCHEMA,
        "id": "evt-000001",
        "event": "run_started",
        "timestamp": utc_now(),
        "run_id": run_id,
        "data": redact(dict(metadata or {})),
    }
    _append_event(run_path, event)
    summary = {
        "schema": TRACE_SCHEMA,
        "run_id": run_id,
        "status": "running",
        "started_at": event["timestamp"],
        "event_count": 1,
        "verification": "not-run",
    }
    write_json(run_path / SUMMARY_FILE, summary, mode=0o600)
    return summary


def read_events(run_path: Path) -> List[Dict[str, Any]]:
    path = run_path / EVENTS_FILE
    if not path.is_file():
        raise ValidationError(f"Missing trace events file: {path}")
    events: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"Invalid JSON at {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValidationError(f"Trace event at {path}:{line_number} must be an object")
            events.append(value)
    return events


def emit_event(
    target: Path,
    event_name: str,
    data: Optional[Mapping[str, Any]] = None,
    *,
    run_id: Optional[str] = None,
    event_id: Optional[str] = None,
) -> Dict[str, Any]:
    _validate_event_name(event_name)
    target = target.resolve()
    resolved_id, run_path = resolve_run(target, run_id)
    if not run_path.is_dir():
        raise ValidationError(f"Unknown trace run: {resolved_id}")
    lock = run_path / EVENT_LOCK_FILE
    with FileLock(lock, stale_after_seconds=5 * 60):
        events = read_events(run_path)
        if any(event.get("event") == "run_finished" for event in events):
            raise ValidationError(f"Trace run is already finished: {resolved_id}")
        sequence = len(events) + 1
        resolved_event_id = event_id or f"evt-{sequence:06d}"
        _validate_event_id(resolved_event_id)
        if any(event.get("id") == resolved_event_id for event in events):
            raise ValidationError(f"Duplicate event id: {resolved_event_id}")
        event = {
            "schema": TRACE_SCHEMA,
            "id": resolved_event_id,
            "event": event_name,
            "timestamp": utc_now(),
            "run_id": resolved_id,
            "data": redact(dict(data or {})),
        }
        _append_event(run_path, event)
        summary_path = run_path / SUMMARY_FILE
        summary = read_json(summary_path) if summary_path.exists() else {"schema": TRACE_SCHEMA, "run_id": resolved_id}
        summary["event_count"] = sequence
        summary["updated_at"] = event["timestamp"]
        write_json(summary_path, summary, mode=0o600)
        return event


def finish_run(
    target: Path,
    *,
    run_id: Optional[str] = None,
    status: str = "completed",
    data: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    if status not in {"completed", "blocked", "failed", "cancelled", "partial"}:
        raise ValidationError(f"Invalid run status: {status}")
    event = emit_event(target, "run_finished", {"status": status, **dict(data or {})}, run_id=run_id)
    resolved_id, run_path = resolve_run(target.resolve(), run_id)
    result = verify_run(target.resolve(), run_id=resolved_id)
    summary = {
        "schema": TRACE_SCHEMA,
        "run_id": resolved_id,
        "status": status,
        "started_at": result.get("started_at"),
        "finished_at": event["timestamp"],
        "event_count": result["event_count"],
        "verification": "passed" if result["ok"] else "failed",
        "errors": result["errors"],
        "warnings": result["warnings"],
    }
    write_json(run_path / SUMMARY_FILE, summary, mode=0o600)
    return summary


def _parse_timestamp(raw: Any) -> Optional[dt.datetime]:
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def verify_run(target: Path, *, run_id: Optional[str] = None) -> Dict[str, Any]:
    target = target.resolve()
    resolved_id, run_path = resolve_run(target, run_id)
    events = read_events(run_path)
    errors: List[str] = []
    warnings: List[str] = []
    by_id: Dict[str, Tuple[int, Dict[str, Any]]] = {}
    evidence_ids: Dict[str, Tuple[int, Dict[str, Any]]] = {}
    previous_time: Optional[dt.datetime] = None

    if not events:
        errors.append("Trace contains no events")

    for index, event in enumerate(events):
        position = index + 1
        if event.get("schema") != TRACE_SCHEMA:
            errors.append(f"Event {position} has invalid schema")
        if event.get("run_id") != resolved_id:
            errors.append(f"Event {position} belongs to a different run")
        event_id = event.get("id")
        if not isinstance(event_id, str) or not event_id:
            errors.append(f"Event {position} has no id")
        elif not ID_RE.fullmatch(event_id):
            errors.append(f"Event {position} has invalid id: {event_id}")
        elif event_id in by_id:
            errors.append(f"Duplicate event id: {event_id}")
        else:
            by_id[event_id] = (index, event)

        timestamp = _parse_timestamp(event.get("timestamp"))
        if timestamp is None:
            errors.append(f"Event {event_id or position} has invalid timestamp")
        elif previous_time is not None and timestamp < previous_time:
            errors.append(f"Event timestamps are not monotonic at {event_id or position}")
        else:
            previous_time = timestamp

        event_name = event.get("event")
        if not isinstance(event_name, str) or not EVENT_NAME_RE.fullmatch(event_name):
            errors.append(f"Event {event_id or position} has invalid event name")

        data = event.get("data", {})
        if not isinstance(data, dict):
            errors.append(f"Event {event_id or position} data must be an object")
            continue
        evidence_id = data.get("evidence_id")
        if evidence_id is not None:
            if not isinstance(evidence_id, str) or not ID_RE.fullmatch(evidence_id):
                errors.append(f"Event {event_id or position} has invalid evidence_id")
            elif evidence_id in evidence_ids or evidence_id in by_id:
                errors.append(f"Duplicate evidence id: {evidence_id}")
            else:
                evidence_ids[evidence_id] = (index, event)
        if event_name == "command_finished":
            if not isinstance(data.get("command"), str) or not data.get("command"):
                errors.append(f"Command event {event_id} is missing command")
            if not isinstance(data.get("exit_code"), int):
                errors.append(f"Command event {event_id} is missing integer exit_code")

    if events:
        if events[0].get("event") != "run_started":
            errors.append("First trace event must be run_started")
        started_count = sum(event.get("event") == "run_started" for event in events)
        if started_count != 1:
            errors.append(f"Trace must contain exactly one run_started event; found {started_count}")
        finished_positions = [index for index, event in enumerate(events) if event.get("event") == "run_finished"]
        if not finished_positions:
            warnings.append("Trace has not emitted run_finished")
        elif len(finished_positions) != 1:
            errors.append(f"Trace must contain at most one run_finished event; found {len(finished_positions)}")
        elif finished_positions[0] != len(events) - 1:
            errors.append("run_finished must be the final trace event")

    valid_refs: Dict[str, Tuple[int, Dict[str, Any]]] = {**by_id, **evidence_ids}

    # A passed verification is itself a claim. Ensure it has earlier, successful
    # source evidence so completion claims cannot launder an unrelated event through
    # an unsupported ``verification_finished`` record.
    for index, event in enumerate(events):
        if event.get("event") != "verification_finished":
            continue
        data = event.get("data", {})
        if not isinstance(data, dict) or data.get("status") != "passed":
            continue
        if not data.get("scope"):
            errors.append(f"Passed verification {event.get('id')} is missing an explicit scope")
        refs = data.get("evidence", [])
        if not isinstance(refs, list) or not refs:
            errors.append(f"Passed verification {event.get('id')} has no upstream evidence")
            continue
        referenced_sources: List[Tuple[int, Dict[str, Any]]] = []
        for raw_ref in refs:
            ref = str(raw_ref)
            entry = valid_refs.get(ref)
            if entry is None:
                errors.append(f"Passed verification {event.get('id')} references missing evidence: {ref}")
                continue
            if entry[0] >= index:
                errors.append(f"Passed verification {event.get('id')} references evidence that is not earlier: {ref}")
                continue
            referenced_sources.append(entry)
        successful_sources = [entry for entry in referenced_sources if verification_source_succeeded(entry[1], data.get("scope"))]
        if not successful_sources:
            errors.append(f"Passed verification {event.get('id')} lacks successful upstream evidence")
            continue
        latest_change_before = max(
            (position for position, candidate in enumerate(events[:index]) if candidate.get("event") in CHANGE_EVENTS),
            default=-1,
        )
        if latest_change_before >= 0 and max(entry[0] for entry in successful_sources) < latest_change_before:
            errors.append(f"Passed verification {event.get('id')} relies on evidence made stale by a later file change")

    for index, event in enumerate(events):
        if event.get("event") != "claim":
            continue
        data = event.get("data", {})
        if not isinstance(data, dict):
            continue
        claim = data.get("claim") or data.get("type")
        refs = data.get("evidence", [])
        if not isinstance(refs, list) or not refs:
            errors.append(f"Claim {event.get('id')} ({claim or 'unknown'}) has no evidence")
            continue
        referenced: List[Tuple[int, Dict[str, Any]]] = []
        for raw_ref in refs:
            ref = str(raw_ref)
            entry = valid_refs.get(ref)
            if entry is None:
                errors.append(f"Claim {event.get('id')} references missing evidence: {ref}")
                continue
            if entry[0] >= index:
                errors.append(f"Claim {event.get('id')} references evidence that is not earlier: {ref}")
                continue
            referenced.append(entry)
        if claim_requires_success(str(claim or "")):
            successful = [entry for entry in referenced if evidence_supports_claim(entry[1], str(claim))]
            if not successful:
                errors.append(f"Claim {event.get('id')} ({claim}) lacks semantically matching successful evidence")
            else:
                latest_change_before = max(
                    (position for position, candidate in enumerate(events[:index]) if candidate.get("event") in CHANGE_EVENTS),
                    default=-1,
                )
                if latest_change_before >= 0 and max(entry[0] for entry in successful) < latest_change_before:
                    errors.append(f"Claim {event.get('id')} ({claim}) relies on verification made stale by a later file change")

    approvals: List[Tuple[int, Mapping[str, Any], Mapping[str, Any]]] = []
    for index, event in enumerate(events):
        data = event.get("data", {})
        if not isinstance(data, dict):
            continue
        if event.get("event") in APPROVAL_EVENTS:
            approvals.append((index, data, event))
        if event.get("event") in HIGH_RISK_EVENTS:
            scope = data.get("scope")
            if not scope:
                errors.append(f"High-risk event {event.get('id')} is missing scope")
                continue
            requested_approval = data.get("approval_id")
            candidates = []
            for approval_index, approval, approval_event in approvals:
                if approval_index >= index or approval.get("scope") not in {scope, "*"}:
                    continue
                approval_id = approval.get("approval_id") or approval_event.get("id")
                if requested_approval and approval_id != requested_approval:
                    continue
                candidates.append((approval_index, approval, approval_event))
            if not candidates:
                errors.append(f"High-risk event {event.get('id')} started without prior matching approval for scope {scope}")
                continue
            _, decision, decision_event = candidates[-1]
            if decision.get("approved") is not True:
                errors.append(f"High-risk event {event.get('id')} follows a rejected approval for scope {scope}")
                continue
            expires_at = _parse_timestamp(decision.get("expires_at") or decision.get("valid_until"))
            action_time = _parse_timestamp(event.get("timestamp"))
            if expires_at is not None and action_time is not None and action_time > expires_at:
                errors.append(f"High-risk event {event.get('id')} uses expired approval {decision_event.get('id')}")
            bound_action = decision.get("action_id")
            if bound_action and bound_action != event.get("id"):
                errors.append(f"High-risk event {event.get('id')} does not match approval action_id {bound_action}")

    completed = next(
        (
            event.get("data", {}).get("status")
            for event in reversed(events)
            if event.get("event") == "run_finished" and isinstance(event.get("data"), dict)
        ),
        None,
    )
    if completed == "completed" and not any(event.get("event") == "claim" for event in events):
        warnings.append("Completed run has no evidence-linked completion claim")

    return {
        "schema": TRACE_SCHEMA,
        "run_id": resolved_id,
        "ok": not errors,
        "event_count": len(events),
        "started_at": events[0].get("timestamp") if events else None,
        "finished_at": next((event.get("timestamp") for event in reversed(events) if event.get("event") == "run_finished"), None),
        "errors": errors,
        "warnings": warnings,
    }
