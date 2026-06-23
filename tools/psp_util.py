#!/usr/bin/env python3
"""Shared, dependency-free utilities for Pragmatic Skills Pack."""

from __future__ import annotations

import contextlib
import datetime as _dt
import hashlib
import json
import os
import re
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple, Union

PACKAGE_VERSION = "2.0.2"
PACKAGE_ID = "pragmatic-skills-pack"
INSTALL_SCHEMA = "psp.install/v2"
MANIFEST_SCHEMA = "psp.manifest/v2"
TRACE_SCHEMA = "psp.trace/v1"
EVAL_CASE_SCHEMA = "psp.eval-case/v1"
EVAL_RESULT_SCHEMA = "psp.eval-result/v1"
EVAL_GRADE_SCHEMA = "psp.eval-grade/v1"
EVAL_REPORT_SCHEMA = "psp.eval-report/v1"
EVAL_CAPTURE_SCORE_SCHEMA = "psp.eval-capture-score/v1"
EVAL_CAPTURE_REPORT_SCHEMA = "psp.eval-capture-report/v1"

SECRET_KEY_RE = re.compile(
    r"(?:password|passwd|secret|token|authorization|api[_-]?key|private[_-]?key|credential|"
    r"connection[_-]?string|connectionstring|dsn|database[_-]?url|db[_-]?url|jdbc[_-]?url|"
    r"redis[_-]?url|mongo(?:db)?[_-]?url)",
    re.I,
)
SECRET_VALUE_RES = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bglpat-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{12,}=*", re.I),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b([A-Za-z][A-Za-z0-9+.-]*://)([^/\s@]+)@", re.I),
    re.compile(r"\b(jdbc:[A-Za-z][A-Za-z0-9+.-]*://)([^/\s@]+)@", re.I),
    re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*[^\s,;]+"),
]
SECRET_VALUE_REPLACEMENTS = {
    7: lambda match: f"{match.group(1)}[REDACTED]@",
    8: lambda match: f"{match.group(1)}[REDACTED]@",
    9: lambda match: f"{match.group(1)}=[REDACTED]",
}
UTF8_BOM = b"\xef\xbb\xbf"


class PSPError(RuntimeError):
    """Base PSP failure."""


class ValidationError(PSPError):
    """Invalid package, state, path, or input."""


class ConflictError(PSPError):
    """A user-owned or modified file could not be safely overwritten."""


class LockError(PSPError):
    """A concurrent operation owns the install lock."""


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def timestamp_id() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_utf8_bytes(data: bytes, source: str = "<bytes>") -> Tuple[str, bool]:
    """Decode UTF-8 without newline translation and report whether a BOM existed."""

    has_bom = data.startswith(UTF8_BOM)
    payload = data[len(UTF8_BOM) :] if has_bom else data
    try:
        return payload.decode("utf-8"), has_bom
    except UnicodeDecodeError as exc:
        raise ValidationError(f"Managed text file is not valid UTF-8: {source}: {exc}") from exc


def encode_utf8_text(text: str, *, bom: bool = False) -> bytes:
    payload = text.encode("utf-8")
    return UTF8_BOM + payload if bom else payload


def read_utf8_preserve(path: Path) -> Tuple[str, bool]:
    return decode_utf8_bytes(path.read_bytes(), str(path))


def canonical_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def detect_newline(text: str) -> str:
    crlf = text.count("\r\n")
    lone_lf = text.count("\n") - crlf
    lone_cr = text.count("\r") - crlf
    if crlf and crlf >= lone_lf and crlf >= lone_cr:
        return "\r\n"
    if lone_cr > lone_lf:
        return "\r"
    return "\n"


def render_newlines(text: str, newline: str) -> str:
    if newline not in {"\n", "\r\n", "\r"}:
        raise ValidationError(f"Unsupported newline sequence: {newline!r}")
    return canonical_newlines(text).replace("\n", newline)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Invalid JSON file {path}: {exc}") from exc


def atomic_write_bytes(path: Path, data: bytes, mode: Optional[int] = None) -> None:
    if mode is None and path.is_file() and not path.is_symlink():
        mode = path.stat().st_mode & 0o777
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None:
            os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            temp.unlink()


def atomic_write_text(path: Path, text: str, mode: Optional[int] = None) -> None:
    atomic_write_bytes(path, text.encode("utf-8"), mode=mode)


def write_json(path: Path, value: Any, mode: Optional[int] = None) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", mode=mode)


def normalize_relpath(relative: Union[str, Path]) -> str:
    raw = str(relative).replace("\\", "/")
    if not raw or "\x00" in raw:
        raise ValidationError("Empty or NUL-containing path is not allowed")
    if re.match(r"^[A-Za-z]:", raw):
        raise ValidationError(f"Absolute path is not allowed: {raw}")
    raw_parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise ValidationError(f"Unsafe relative path: {raw}")
    pure = PurePosixPath(raw)
    if pure.is_absolute():
        raise ValidationError(f"Unsafe relative path: {raw}")
    return pure.as_posix()


def _within(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def safe_join(root: Path, relative: Union[str, Path], *, reject_final_symlink: bool = True) -> Path:
    """Resolve an untrusted relative path and reject traversal or symlink components.

    ``root`` itself may be a resolved symlink target. Every component beneath it is
    treated as installation data and therefore may not be a symlink.
    """

    rel = normalize_relpath(relative)
    resolved_root = root.resolve(strict=False)
    candidate = root.joinpath(*PurePosixPath(rel).parts)
    current = root
    parts = PurePosixPath(rel).parts
    for index, part in enumerate(parts):
        current = current / part
        is_final = index == len(parts) - 1
        if current.is_symlink():
            raise ValidationError(f"Symlink component is not allowed in managed path: {rel}")
        if current.exists() or current.is_symlink():
            resolved = current.resolve(strict=False)
            if not _within(resolved, resolved_root):
                raise ValidationError(f"Path escapes target through symlink: {rel}")
    resolved_candidate = candidate.resolve(strict=False)
    if not _within(resolved_candidate, resolved_root):
        raise ValidationError(f"Path escapes target: {rel}")
    return candidate


def copy_file_atomic(source: Path, destination: Path) -> None:
    atomic_write_bytes(destination, source.read_bytes(), mode=source.stat().st_mode & 0o777)


def remove_empty_parents(path: Path, stop: Path) -> None:
    current = path.parent
    stop_resolved = stop.resolve(strict=False)
    while current != stop and _within(current.resolve(strict=False), stop_resolved):
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def iter_files(root: Path, *, excluded_dirs: Sequence[str] = ()) -> Iterator[Path]:
    excluded = set(excluded_dirs)
    if not root.exists():
        return
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in excluded)
        for name in sorted(files):
            path = Path(current) / name
            if path.is_symlink():
                raise ValidationError(f"Package contains symlink: {path.relative_to(root)}")
            yield path


def parse_version(value: str) -> Tuple[int, int, int, str]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(.*)", value.strip())
    if not match:
        raise ValidationError(f"Invalid semantic version: {value}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3)), match.group(4)


def extract_frontmatter(text: str, source: str = "<text>") -> Tuple[str, str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValidationError(f"Missing YAML frontmatter in {source}")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1 :])
    raise ValidationError(f"Unterminated YAML frontmatter in {source}")


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_skill_metadata(path: Path) -> Dict[str, str]:
    frontmatter, _ = extract_frontmatter(path.read_text(encoding="utf-8"), str(path))
    result: Dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", line)
        if match:
            key = match.group(1)
            raw_value = match.group(2) or ""
            stripped = raw_value.strip()
            if ": " in stripped and not (
                len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}
            ):
                raise ValidationError(f"Skill {path} has YAML-ambiguous frontmatter field: {key}")
            result[key] = _unquote(raw_value)
    for required in ("name", "description"):
        if not result.get(required):
            raise ValidationError(f"Skill {path} is missing frontmatter field: {required}")
    return result


def _load_sidecar(path: Path) -> Dict[str, Any]:
    value = read_json(path)
    if not isinstance(value, dict):
        raise ValidationError(f"Skill sidecar must be a JSON object: {path}")
    required = {"schema", "name", "kind", "version", "loads", "entry"}
    missing = sorted(required - set(value))
    if missing:
        raise ValidationError(f"Skill sidecar {path} is missing: {', '.join(missing)}")
    if value.get("schema") != "psp.skill/v2":
        raise ValidationError(f"Unsupported skill sidecar schema in {path}: {value.get('schema')}")
    if not isinstance(value.get("loads"), list) or not all(isinstance(item, str) for item in value["loads"]):
        raise ValidationError(f"Skill sidecar loads must be a string array: {path}")
    if not isinstance(value.get("entry"), bool):
        raise ValidationError(f"Skill sidecar entry must be boolean: {path}")
    return value


def build_skill_manifest(package_root: Path) -> Dict[str, Any]:
    skills_root = package_root / "skills"
    entries: List[Dict[str, Any]] = []
    for sidecar_path in sorted(skills_root.glob("*/psp.skill.json")):
        sidecar = _load_sidecar(sidecar_path)
        name = str(sidecar["name"])
        skill_path = sidecar_path.with_name("SKILL.md")
        if not skill_path.is_file():
            raise ValidationError(f"Missing SKILL.md for {sidecar_path}")
        metadata = parse_skill_metadata(skill_path)
        if metadata["name"] != name:
            raise ValidationError(f"Skill name mismatch: {skill_path} says {metadata['name']!r}, sidecar says {name!r}")
        expected_dir = name
        if sidecar_path.parent.name != expected_dir:
            raise ValidationError(f"Skill directory mismatch: {sidecar_path.parent.name!r} != {name!r}")
        entries.append(
            {
                "name": name,
                "path": skill_path.relative_to(package_root).as_posix(),
                "sidecar": sidecar_path.relative_to(package_root).as_posix(),
                "kind": str(sidecar["kind"]),
                "version": str(sidecar["version"]),
                "entry": bool(sidecar["entry"]),
                "loads": list(sidecar["loads"]),
                "sha256": sha256_file(skill_path),
                "sidecar_sha256": sha256_file(sidecar_path),
            }
        )
    entry_skills = [entry for entry in entries if entry["entry"]]
    entry_path = entry_skills[0]["path"] if len(entry_skills) == 1 else None
    return {
        "schema": MANIFEST_SCHEMA,
        "package_id": PACKAGE_ID,
        "name": "Pragmatic Skills Pack — Enhanced 2.0.2",
        "version": PACKAGE_VERSION,
        "generated_at": "deterministic",
        "entry_skill": entry_path,
        "primary_modes": ["fast-patch", "exploration", "standard-change", "strict-change"],
        "payload_roots": ["skills", "reference", "schemas", "compat"],
        "skills": entries,
    }


def sidecar_for(entry: Mapping[str, Any]) -> Dict[str, Any]:
    """Return the minimal sidecar projection represented by a manifest entry.

    Rich sidecars remain source-controlled; this helper is kept for API compatibility
    and is not used to overwrite them.
    """

    return {
        "schema": "psp.skill/v2",
        "name": entry["name"],
        "kind": entry["kind"],
        "version": entry["version"],
        "entry": bool(entry["entry"]),
        "loads": list(entry.get("loads", [])),
    }


def validate_skill_graph(package_root: Path, manifest: Optional[Mapping[str, Any]] = None) -> List[Dict[str, str]]:
    manifest = manifest or build_skill_manifest(package_root)
    issues: List[Dict[str, str]] = []
    entries = list(manifest.get("skills", []))
    by_name: Dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        name = str(entry.get("name", ""))
        if not name:
            issues.append({"severity": "error", "code": "empty-name", "message": "A Skill has an empty name"})
            continue
        if name in by_name:
            issues.append({"severity": "error", "code": "duplicate-name", "message": f"Duplicate Skill name: {name}"})
        by_name[name] = entry
        if entry.get("version") != PACKAGE_VERSION:
            issues.append({"severity": "error", "code": "version-mismatch", "message": f"{name} uses version {entry.get('version')}"})
        expected_path = f"skills/{name}/SKILL.md"
        if entry.get("path") != expected_path:
            issues.append({"severity": "error", "code": "path-name-mismatch", "message": f"{name} is stored at {entry.get('path')}; expected {expected_path}"})

    entry_skills = [entry for entry in entries if entry.get("entry")]
    if len(entry_skills) != 1:
        issues.append({"severity": "error", "code": "entry-count", "message": f"Expected exactly one entry Skill, found {len(entry_skills)}"})
    elif entry_skills[0].get("name") != "using-pragmatic-skills":
        issues.append({"severity": "error", "code": "entry-name", "message": "Entry Skill must be using-pragmatic-skills"})

    required_modes = set(manifest.get("primary_modes", []))
    observed_modes = {name for name, entry in by_name.items() if entry.get("kind") == "mode"}
    if observed_modes != required_modes:
        issues.append(
            {
                "severity": "error",
                "code": "primary-modes",
                "message": f"Primary modes differ: expected {sorted(required_modes)}, observed {sorted(observed_modes)}",
            }
        )

    for name, entry in by_name.items():
        for dependency in entry.get("loads", []):
            if dependency not in by_name:
                issues.append({"severity": "error", "code": "missing-load", "message": f"{name} loads missing Skill {dependency}"})

    triage = by_name.get("triage")
    if not triage:
        issues.append({"severity": "error", "code": "missing-triage", "message": "Missing triage Skill"})
    elif set(triage.get("loads", [])) != required_modes:
        issues.append({"severity": "error", "code": "triage-modes", "message": "Triage must load exactly the four primary modes"})

    visited: set[str] = set()
    stack = ["using-pragmatic-skills"]
    while stack:
        current = stack.pop()
        if current in visited or current not in by_name:
            continue
        visited.add(current)
        stack.extend(str(item) for item in by_name[current].get("loads", []))
    for name in sorted(set(by_name) - visited):
        issues.append({"severity": "error", "code": "unreachable-skill", "message": f"Skill is not reachable from entry: {name}"})
    return issues


def _event_payload(event: Mapping[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    nested = event.get("data")
    if isinstance(nested, Mapping):
        payload.update(nested)
    payload.update({str(key): value for key, value in event.items() if key != "data"})
    return payload


def _purpose_values(payload: Mapping[str, Any]) -> set[str]:
    raw_values: List[Any] = []
    for key in ("purpose", "kind", "scope", "verification_type", "check_type"):
        value = payload.get(key)
        if isinstance(value, (list, tuple, set)):
            raw_values.extend(value)
        elif value is not None:
            raw_values.append(value)
    return {str(value).strip().lower().replace("_", "-") for value in raw_values if str(value).strip()}


def evidence_supports_claim(event: Mapping[str, Any], claim: str) -> bool:
    """Return whether one evidence event semantically supports a success claim.

    A zero exit code is not enough to prove tests/build/lint/type-check success: the
    command must declare its purpose.  This prevents unrelated commands such as
    ``echo ok`` or an inspected artifact from satisfying a verification claim.
    """

    payload = _event_payload(event)
    kind = str(payload.get("event", event.get("event", "")))
    claim = str(claim or "").strip().lower().replace("-", "_")
    purposes = _purpose_values(payload)

    if claim == "review_passed":
        return kind == "review_finished" and payload.get("status") in {"passed", "approved", "clean"}

    if kind == "verification_finished" and payload.get("status") == "passed":
        if claim in {"verification_passed", "task_completed", "work_completed"} or claim.endswith(("_complete", "_completed", "_succeeded")):
            return True
        required = {
            "tests_passed": {"test", "tests", "unit-test", "integration-test", "e2e-test", "full", "all"},
            "build_passed": {"build", "package", "compile", "full", "all"},
            "lint_passed": {"lint", "format", "static-analysis", "full", "all"},
            "typecheck_passed": {"typecheck", "type-check", "types", "full", "all"},
        }.get(claim, set())
        return bool(required & purposes)

    if kind == "command_finished" and payload.get("exit_code") == 0:
        required = {
            "tests_passed": {"test", "tests", "unit-test", "integration-test", "e2e-test"},
            "build_passed": {"build", "package", "compile"},
            "lint_passed": {"lint", "format", "static-analysis"},
            "typecheck_passed": {"typecheck", "type-check", "types"},
        }.get(claim, set())
        return bool(required & purposes)

    return False


def claim_requires_success(claim: str) -> bool:
    normalized = str(claim or "").strip().lower().replace("-", "_")
    return normalized in {
        "tests_passed",
        "build_passed",
        "lint_passed",
        "typecheck_passed",
        "verification_passed",
        "review_passed",
        "task_completed",
        "work_completed",
    } or normalized.endswith(("_passed", "_complete", "_completed", "_succeeded"))


def verification_source_succeeded(event: Mapping[str, Any], scope: Any) -> bool:
    """Whether an event can support a passed verification of the declared scope."""

    payload = _event_payload(event)
    kind = str(payload.get("event", event.get("event", "")))
    scopes = {str(scope).strip().lower().replace("_", "-")} if not isinstance(scope, (list, tuple, set)) else {
        str(item).strip().lower().replace("_", "-") for item in scope
    }
    scopes.discard("")
    purposes = _purpose_values(payload)
    if not scopes:
        return False

    test_scopes = {"test", "tests", "unit-test", "integration-test", "e2e-test"}
    build_scopes = {"build", "package", "compile"}
    lint_scopes = {"lint", "format", "static-analysis"}
    type_scopes = {"typecheck", "type-check", "types"}
    artifact_scopes = {"artifact", "artifacts", "docs", "documentation", "inspection"}
    review_scopes = {"review", "code-review"}

    if kind == "command_finished" and payload.get("exit_code") == 0:
        if scopes & {"full", "all"}:
            return bool(purposes)
        return bool(
            (scopes & test_scopes and purposes & test_scopes)
            or (scopes & build_scopes and purposes & build_scopes)
            or (scopes & lint_scopes and purposes & lint_scopes)
            or (scopes & type_scopes and purposes & type_scopes)
        )
    if kind == "review_finished":
        return bool(scopes & (review_scopes | {"full", "all"})) and payload.get("status") in {"passed", "approved", "clean"}
    if kind == "artifact_inspected":
        return bool(scopes & artifact_scopes) and payload.get("status", "inspected") in {"inspected", "passed", "clean"}
    return False


def redact(value: Any, key: str = "") -> Any:
    if key and SECRET_KEY_RE.search(key):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(k): redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        result = value
        for index, pattern in enumerate(SECRET_VALUE_RES):
            replacement = SECRET_VALUE_REPLACEMENTS.get(index, "[REDACTED]")
            result = pattern.sub(replacement, result)
        return result
    return value


@dataclass
class FileLock:
    path: Path
    stale_after_seconds: int = 6 * 60 * 60
    force_stale: bool = False
    _owned: bool = False

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"pid": os.getpid(), "created_at": utc_now(), "epoch": time.time()}
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        try:
            fd = os.open(str(self.path), flags, 0o600)
        except FileExistsError:
            try:
                existing = read_json(self.path)
                age = time.time() - float(existing.get("epoch", self.path.stat().st_mtime))
            except Exception:
                age = time.time() - self.path.stat().st_mtime
            if age > self.stale_after_seconds and self.force_stale:
                self.path.unlink(missing_ok=True)
                self.acquire()
                return
            raise LockError(f"Another PSP operation owns {self.path}. Remove it only when confirmed stale.")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        self._owned = True

    def release(self) -> None:
        if self._owned:
            with contextlib.suppress(FileNotFoundError):
                self.path.unlink()
            self._owned = False

    def __enter__(self) -> "FileLock":
        self.acquire()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.release()


def package_fingerprint(package_root: Path) -> str:
    digest = hashlib.sha256()
    for name in ("skills", "reference", "adapters", "schemas", "compat", "evals", "tools", "docs", ".github/workflows"):
        base = package_root / name
        if not base.exists():
            continue
        for path in iter_files(base, excluded_dirs=("__pycache__",)):
            rel = path.relative_to(package_root).as_posix().encode("utf-8")
            digest.update(rel + b"\0" + path.read_bytes() + b"\0")
    for rel in (
        "AGENTS.md",
        "AGENT-INSTALL.md",
        "README.md",
        "README.zh.md",
        "LICENSE",
        "LICENSE-APACHE-2.0",
        "NOTICE",
        "SOURCE-BASELINE.md",
        "CHANGELOG.md",
        "BUILD-REPORT.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "RELEASE-CHECKLIST.md",
        "Makefile",
        "pyproject.toml",
        "install.sh",
        "verify.sh",
    ):
        path = package_root / rel
        if path.is_file():
            digest.update(rel.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()
