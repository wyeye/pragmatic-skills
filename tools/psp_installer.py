#!/usr/bin/env python3
"""Transactional, dependency-free installer for Pragmatic Skills Pack."""

from __future__ import annotations

import contextlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple, Union

from psp_eval import load_cases
from psp_schema import validate_instance, validation_errors
from psp_util import (
    INSTALL_SCHEMA,
    MANIFEST_SCHEMA,
    PACKAGE_VERSION,
    FileLock,
    ValidationError,
    atomic_write_bytes,
    build_skill_manifest,
    canonical_newlines,
    copy_file_atomic,
    detect_newline,
    encode_utf8_text,
    package_fingerprint,
    parse_version,
    read_json,
    read_utf8_preserve,
    remove_empty_parents,
    render_newlines,
    safe_join,
    sha256_bytes,
    sha256_file,
    sha256_text,
    sidecar_for,
    timestamp_id,
    utc_now,
    validate_skill_graph,
    write_json,
)

STATE_REL = ".psp/install.json"
LOCK_REL = ".psp/install.lock"
BACKUPS_REL = ".psp/backups"
CONFLICTS_REL = ".psp/conflicts"
STAGING_REL = ".psp/staging"

AGENTS_BEGIN = "<!-- PSP:BEGIN -->"
AGENTS_END = "<!-- PSP:END -->"
CLAUDE_BEGIN = "<!-- PSP-CLAUDE:BEGIN -->"
CLAUDE_END = "<!-- PSP-CLAUDE:END -->"
GEMINI_BEGIN = "<!-- PSP-GEMINI:BEGIN -->"
GEMINI_END = "<!-- PSP-GEMINI:END -->"
COPILOT_BEGIN = "<!-- PSP-COPILOT:BEGIN -->"
COPILOT_END = "<!-- PSP-COPILOT:END -->"

ALL_HOSTS = {"agents", "codex", "claude", "opencode", "hermes", "gemini", "copilot", "cursor"}

ADAPTER_FILE_SOURCES = {
    ".agents/skills/using-pragmatic-skills/SKILL.md": "adapters/native-entry/SKILL.md",
    ".claude/skills/psp-claude-entry/SKILL.md": "adapters/claude-entry/SKILL.md",
    ".opencode/commands/psp.md": "adapters/opencode/commands/psp.md",
    ".cursor/rules/pragmatic-skills-pack.mdc": "adapters/cursor/rules/pragmatic-skills-pack.mdc",
}
GENERATED_ADAPTER_FILES = {"AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md"}

@dataclass(frozen=True)
class DesiredFile:
    rel: str
    data: bytes
    source: str
    mode: int = 0o644

    @property
    def digest(self) -> str:
        return sha256_bytes(self.data)


@dataclass(frozen=True)
class DesiredBlock:
    rel: str
    text: str
    begin: str
    end: str
    source: str

    @property
    def digest(self) -> str:
        return sha256_text(canonical_newlines(self.text))


@dataclass
class Change:
    rel: str
    data: Optional[bytes]
    mode: int
    action: str
    reason: str


@dataclass
class Conflict:
    rel: str
    desired: Optional[bytes]
    reason: str


def package_root_from(module_file: Union[str, Path]) -> Path:
    return Path(module_file).resolve().parent.parent


def load_state(target: Path, *, required: bool = False) -> Optional[Dict[str, Any]]:
    path = safe_join(target, STATE_REL, reject_final_symlink=True)
    if not path.exists():
        if required:
            raise ValidationError(f"PSP is not installed: missing {STATE_REL}")
        return None
    value = read_json(path)
    if not isinstance(value, dict):
        raise ValidationError(f"Invalid PSP state: {STATE_REL} must contain an object")
    schema = value.get("schema")
    if schema not in {INSTALL_SCHEMA, "psp.install/v1"}:
        raise ValidationError(f"Unsupported install state schema: {schema}")
    source_state_schema_path = package_root_from(__file__) / "schemas/install-state.schema.json"
    if schema == INSTALL_SCHEMA and source_state_schema_path.is_file():
        state_schema = read_json(source_state_schema_path)
        if not isinstance(state_schema, dict):
            raise ValidationError(f"Invalid install state schema: {source_state_schema_path}")
        validate_instance(value, state_schema, STATE_REL)
    for section in ("managed_files", "managed_blocks"):
        raw = value.get(section, {})
        if not isinstance(raw, dict):
            raise ValidationError(f"Invalid PSP state: {section} must be an object")
        for rel in raw:
            safe_join(target, str(rel), reject_final_symlink=False)
    return value


def _read_block_source(path: Path, begin: str, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    block, status = extract_block(text, begin, end)
    if status != "ok" or block is None:
        raise ValidationError(f"Package source {path} does not contain one valid managed block")
    return block


def extract_block(text: str, begin: str, end: str) -> Tuple[Optional[str], str]:
    begin_count = text.count(begin)
    end_count = text.count(end)
    if begin_count == 0 and end_count == 0:
        return None, "missing"
    if begin_count != 1 or end_count != 1:
        return None, "malformed"
    start = text.find(begin)
    finish = text.find(end, start + len(begin))
    if finish < 0 or finish < start:
        return None, "malformed"
    finish += len(end)
    return text[start:finish], "ok"


def _merge_block_details(existing: str, block: DesiredBlock) -> Tuple[Optional[str], str, Dict[str, Any]]:
    current, status = extract_block(existing, block.begin, block.end)
    if status == "malformed":
        return None, status, {}
    newline = detect_newline(existing)
    rendered = render_newlines(block.text, newline)
    if status == "ok" and current is not None:
        start = existing.find(block.begin)
        finish = existing.find(block.end, start) + len(block.end)
        return existing[:start] + rendered + existing[finish:], "replaced", {"newline": newline}

    if not existing:
        insert_prefix = ""
    elif existing.endswith(newline * 2):
        insert_prefix = ""
    elif existing.endswith(newline):
        insert_prefix = newline
    else:
        insert_prefix = newline * 2
    insert_suffix = newline
    merged = existing + insert_prefix + rendered.rstrip("\r\n") + insert_suffix
    return merged, "inserted", {
        "newline": newline,
        "insert_prefix": insert_prefix,
        "insert_suffix": insert_suffix,
    }


def _block_digest(text: str) -> str:
    return sha256_text(canonical_newlines(text))


def _block_matches_entry(text: str, entry: Mapping[str, Any]) -> bool:
    expected = entry.get("sha256")
    return expected in {_block_digest(text), sha256_text(text)}


def _line_ending_suffix(text: str) -> str:
    if text.endswith("\r\n"):
        return "\r\n"
    if text.endswith("\n"):
        return "\n"
    if text.endswith("\r"):
        return "\r"
    return ""


def merge_block_detailed(
    existing: str,
    block: DesiredBlock,
    *,
    previous_metadata: Optional[Mapping[str, Any]] = None,
) -> Tuple[Optional[str], str, Dict[str, Any]]:
    """Merge a managed block while preserving the host file's newline convention.

    ``prefix_added`` and ``suffix_added`` record exactly what PSP inserted around a
    newly-created block.  Uninstall can therefore restore the original bytes rather
    than heuristically reformatting the whole file.
    """

    current, status = extract_block(existing, block.begin, block.end)
    if status == "malformed":
        return None, status, {}
    newline = detect_newline(existing) if existing else "\n"
    rendered = render_newlines(block.text, newline).rstrip("\r\n")
    if status == "ok" and current is not None:
        start = existing.find(block.begin)
        finish = existing.find(block.end, start) + len(block.end)
        metadata = dict(previous_metadata or {})
        metadata.setdefault("placement", "existing")
        metadata["newline"] = newline
        return existing[:start] + rendered + existing[finish:], "replaced", metadata

    prefix_added = ""
    if existing:
        if not _line_ending_suffix(existing):
            prefix_added += newline
        probe = existing + prefix_added
        if not probe.endswith(newline + newline):
            prefix_added += newline
    suffix_added = newline
    metadata = {
        "placement": "inserted",
        "newline": newline,
        "prefix_added": prefix_added,
        "suffix_added": suffix_added,
    }
    return existing + prefix_added + rendered + suffix_added, "inserted", metadata


def merge_block(existing: str, block: DesiredBlock) -> Tuple[Optional[str], str]:
    merged, status, _ = merge_block_detailed(existing, block)
    return merged, status


def remove_block_detailed(
    existing: str,
    begin: str,
    end: str,
    *,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Tuple[Optional[str], str]:
    current, status = extract_block(existing, begin, end)
    if status != "ok" or current is None:
        return None, status
    start = existing.find(begin)
    finish = existing.find(end, start) + len(end)
    meta = dict(metadata or {})
    if meta.get("placement") == "inserted":
        prefix_added = str(meta.get("prefix_added", ""))
        suffix_added = str(meta.get("suffix_added", ""))
        prefix_start = start - len(prefix_added)
        suffix_finish = finish + len(suffix_added)
        if (
            prefix_start >= 0
            and existing[prefix_start:start] == prefix_added
            and existing[finish:suffix_finish] == suffix_added
        ):
            return existing[:prefix_start] + existing[suffix_finish:], "removed"

    # Legacy and pre-existing blocks have no exact insertion metadata.  Keep the
    # conservative historical cleanup behavior, but operate in canonical newlines
    # and restore the original newline convention afterwards.
    newline = detect_newline(existing)
    canonical = canonical_newlines(existing)
    canonical_begin = canonical.find(begin)
    canonical_finish = canonical.find(end, canonical_begin) + len(end)
    result = canonical[:canonical_begin] + canonical[canonical_finish:]
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")
    result = result.strip("\n")
    normalized = (result + "\n") if result else ""
    return render_newlines(normalized, newline), "removed"


def remove_block(existing: str, begin: str, end: str) -> Tuple[Optional[str], str]:
    return remove_block_detailed(existing, begin, end)


def parse_hosts(target: Path, spec: Optional[str]) -> Tuple[str, Set[str]]:
    mode = (spec or "auto").strip().lower()
    if mode == "none":
        return mode, set()
    if mode == "minimal":
        return mode, {"agents"}
    if mode == "all":
        return mode, set(ALL_HOSTS)
    if mode == "auto":
        selected: Set[str] = {"agents"}
        detectors = {
            "claude": ["CLAUDE.md", ".claude"],
            "opencode": ["opencode.json", "opencode.jsonc", ".opencode"],
            "gemini": ["GEMINI.md", ".gemini"],
            "copilot": [".github/copilot-instructions.md"],
            "cursor": [".cursor"],
        }
        for host, markers in detectors.items():
            if any((target / marker).exists() for marker in markers):
                selected.add(host)
        return mode, selected
    selected = {item.strip().lower() for item in mode.split(",") if item.strip()}
    unknown = sorted(selected - ALL_HOSTS)
    if unknown:
        raise ValidationError(f"Unknown host adapter(s): {', '.join(unknown)}")
    if selected & {"codex", "opencode", "hermes"}:
        selected.add("agents")
    return "explicit", selected


def _generated_adapter_block(host: str) -> DesiredBlock:
    if host == "claude":
        begin, end, rel = CLAUDE_BEGIN, CLAUDE_END, "CLAUDE.md"
        body = """# Pragmatic Skills Pack — Claude entry\n\nFor repository coding, debugging, planning, review, or verification, use the installed PSP entry adapter and route through the Pragmatic Skills Pack workflow. Prefer a project-local `skills/using-pragmatic-skills/SKILL.md` only when it exists; otherwise use the PSP runtime or host-installed skill bundle. Do not ask the user to choose individual Skills. Treat `.claude/skills/psp-claude-entry/SKILL.md` as a thin entry adapter only.\n"""
    elif host == "gemini":
        begin, end, rel = GEMINI_BEGIN, GEMINI_END, "GEMINI.md"
        body = """# Pragmatic Skills Pack — Gemini entry\n\nFor repository work, follow the PSP managed block in `AGENTS.md`, then use the Pragmatic Skills Pack entry workflow from a project-local `skills/` directory when present, or from the PSP runtime / host-installed skill bundle otherwise. Route internally and load support Skills only at their phase triggers.\n"""
    elif host == "copilot":
        begin, end, rel = COPILOT_BEGIN, COPILOT_END, ".github/copilot-instructions.md"
        body = """# Pragmatic Skills Pack — Copilot entry\n\nUse `AGENTS.md` and the Pragmatic Skills Pack entry workflow for coding, debugging, planning, review, and verification. Prefer project-local PSP skills only when present; otherwise use the host-installed or runtime PSP skills. Select the smallest safe mode internally; do not ask the user to invoke individual Skills. Never claim tests, builds, reviews, approvals, or command output without evidence.\n"""
    else:
        raise ValidationError(f"No shared adapter block for {host}")
    text = f"{begin}\n{body.rstrip()}\n{end}"
    return DesiredBlock(rel=rel, text=text, begin=begin, end=end, source=f"generated:{host}")


def build_desired(package_root: Path, target: Path, hosts_spec: Optional[str], profile: bool = False) -> Tuple[str, Set[str], Dict[str, DesiredFile], Dict[str, DesiredBlock]]:
    mode, hosts = parse_hosts(target, hosts_spec)
    files: Dict[str, DesiredFile] = {}
    blocks: Dict[str, DesiredBlock] = {}

    if "agents" in hosts:
        agents_source = package_root / "AGENTS.md"
        agents_block = _read_block_source(agents_source, AGENTS_BEGIN, AGENTS_END)
        blocks["AGENTS.md"] = DesiredBlock("AGENTS.md", agents_block, AGENTS_BEGIN, AGENTS_END, "AGENTS.md")
        source = package_root / "adapters/native-entry/SKILL.md"
        rel = ".agents/skills/using-pragmatic-skills/SKILL.md"
        files[rel] = DesiredFile(rel, source.read_bytes(), "adapters/native-entry/SKILL.md", 0o644)
    if "claude" in hosts:
        blocks["CLAUDE.md"] = _generated_adapter_block("claude")
        source = package_root / "adapters/claude-entry/SKILL.md"
        rel = ".claude/skills/psp-claude-entry/SKILL.md"
        files[rel] = DesiredFile(rel, source.read_bytes(), "adapters/claude-entry/SKILL.md", 0o644)
    if "opencode" in hosts:
        source = package_root / "adapters/opencode/commands/psp.md"
        rel = ".opencode/commands/psp.md"
        files[rel] = DesiredFile(rel, source.read_bytes(), "adapters/opencode/commands/psp.md", 0o644)
    if "gemini" in hosts:
        blocks["GEMINI.md"] = _generated_adapter_block("gemini")
    if "copilot" in hosts:
        blocks[".github/copilot-instructions.md"] = _generated_adapter_block("copilot")
    if "cursor" in hosts:
        source = package_root / "adapters/cursor/rules/pragmatic-skills-pack.mdc"
        rel = ".cursor/rules/pragmatic-skills-pack.mdc"
        files[rel] = DesiredFile(rel, source.read_bytes(), "adapters/cursor/rules/pragmatic-skills-pack.mdc", 0o644)

    if profile:
        source = package_root / "reference/PROJECT-PROFILE.template.md"
        rel = ".psp/project-profile.md"
        files.setdefault(rel, DesiredFile(rel, source.read_bytes(), "reference/PROJECT-PROFILE.template.md", 0o644))

    for rel in list(files) + list(blocks):
        safe_join(target, rel, reject_final_symlink=False)
    return mode, hosts, files, blocks


def _state_file_entry(desired: DesiredFile) -> Dict[str, Any]:
    return {"sha256": desired.digest, "source": desired.source, "mode": oct(desired.mode)}


def _state_block_entry(desired: DesiredBlock, metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "sha256": desired.digest,
        "source": desired.source,
        "begin": desired.begin,
        "end": desired.end,
    }
    if metadata:
        entry["file"] = dict(metadata)
    return entry


def _backup_snapshot(target: Path, rels: Iterable[str], backup_id: str, old_state: Optional[Mapping[str, Any]]) -> Path:
    backup_root = safe_join(target, f"{BACKUPS_REL}/{backup_id}", reject_final_symlink=False)
    files_root = backup_root / "files"
    snapshot: Dict[str, Any] = {"schema": "psp.backup/v1", "created_at": utc_now(), "paths": {}}
    for rel in sorted(set(rels)):
        path = safe_join(target, rel, reject_final_symlink=True)
        entry: Dict[str, Any] = {"existed": path.is_file()}
        if path.exists() and not path.is_file():
            raise ValidationError(f"Cannot back up non-file managed path: {rel}")
        if path.is_file():
            backup_path = safe_join(files_root, rel, reject_final_symlink=False)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_path)
            entry["sha256"] = sha256_file(path)
            entry["mode"] = oct(path.stat().st_mode & 0o777)
        snapshot["paths"][rel] = entry
    backup_root.mkdir(parents=True, exist_ok=True)
    write_json(backup_root / "snapshot.json", snapshot, mode=0o600)
    if old_state is not None:
        write_json(backup_root / "state.before.json", old_state, mode=0o600)
    else:
        (backup_root / "state.absent").write_text("\n", encoding="utf-8")
    return backup_root


def _restore_snapshot(target: Path, backup_root: Path) -> None:
    snapshot = read_json(backup_root / "snapshot.json")
    for rel, info in snapshot.get("paths", {}).items():
        path = safe_join(target, rel, reject_final_symlink=False)
        if info.get("existed"):
            source = safe_join(backup_root / "files", rel, reject_final_symlink=True)
            path.parent.mkdir(parents=True, exist_ok=True)
            copy_file_atomic(source, path)
        else:
            if path.is_file() or path.is_symlink():
                path.unlink()
                remove_empty_parents(path, target)
    state_path = safe_join(target, STATE_REL, reject_final_symlink=False)
    before = backup_root / "state.before.json"
    if before.is_file():
        copy_file_atomic(before, state_path)
    else:
        state_path.unlink(missing_ok=True)


def _write_conflicts(target: Path, conflicts: Sequence[Conflict], conflict_id: str) -> Optional[Path]:
    if not conflicts:
        return None
    root = safe_join(target, f"{CONFLICTS_REL}/{conflict_id}", reject_final_symlink=False)
    for conflict in conflicts:
        if conflict.desired is not None:
            path = safe_join(root, conflict.rel, reject_final_symlink=False)
            atomic_write_bytes(path, conflict.desired)
    write_json(root / "conflicts.json", {
        "schema": "psp.conflicts/v1",
        "created_at": utc_now(),
        "conflicts": [{"path": item.rel, "reason": item.reason, "candidate": item.desired is not None} for item in conflicts],
    }, mode=0o600)
    return root


def _apply_changes(target: Path, changes: Sequence[Change], state: Optional[Mapping[str, Any]], new_state: Mapping[str, Any], *, dry_run: bool) -> Optional[str]:
    if dry_run:
        return None
    operation_id = timestamp_id()
    rels = [change.rel for change in changes]
    rels.append(STATE_REL)
    backup_root = _backup_snapshot(target, rels, operation_id, state)
    staging_root = safe_join(target, f"{STAGING_REL}/{operation_id}", reject_final_symlink=False)
    try:
        for change in changes:
            if change.data is not None:
                staged = safe_join(staging_root, change.rel, reject_final_symlink=False)
                atomic_write_bytes(staged, change.data, mode=change.mode)
        for change in changes:
            path = safe_join(target, change.rel, reject_final_symlink=True)
            if change.data is None:
                if path.is_file():
                    path.unlink()
                    remove_empty_parents(path, target)
                continue
            staged = safe_join(staging_root, change.rel, reject_final_symlink=True)
            path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged, path)
            with contextlib.suppress(OSError):
                os.chmod(path, change.mode)
        state_path = safe_join(target, STATE_REL, reject_final_symlink=False)
        write_json(state_path, new_state, mode=0o600)
    except Exception:
        _restore_snapshot(target, backup_root)
        raise
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
    return operation_id


def plan_install(
    package_root: Path,
    target: Path,
    *,
    hosts_spec: Optional[str],
    profile: bool,
    force: bool,
    require_existing: bool,
    allow_downgrade: bool,
) -> Dict[str, Any]:
    old_state = load_state(target, required=require_existing)
    if old_state and hosts_spec is None:
        previous_mode = str(old_state.get("host_mode") or "auto")
        hosts_spec = ",".join(old_state.get("hosts", [])) if previous_mode == "explicit" else previous_mode
    if old_state and not allow_downgrade:
        old_version = str(old_state.get("version", "0.0.0"))
        if parse_version(PACKAGE_VERSION) < parse_version(old_version):
            raise ValidationError(f"Refusing downgrade from {old_version} to {PACKAGE_VERSION}; pass --allow-downgrade")
    mode, hosts, desired_files, desired_blocks = build_desired(package_root, target, hosts_spec, profile=profile)
    old_files = dict((old_state or {}).get("managed_files", {}))
    old_blocks = dict((old_state or {}).get("managed_blocks", {}))
    new_files: Dict[str, Any] = dict(old_files)
    new_blocks: Dict[str, Any] = dict(old_blocks)
    changes: List[Change] = []
    conflicts: List[Conflict] = []
    statuses: List[Dict[str, str]] = []

    for rel, desired in sorted(desired_files.items()):
        path = safe_join(target, rel, reject_final_symlink=True)
        current_hash = sha256_file(path) if path.is_file() else None
        old_entry = old_files.get(rel)
        if path.exists() and not path.is_file():
            raise ValidationError(f"Managed path is not a regular file: {rel}")
        if current_hash == desired.digest:
            statuses.append({"path": rel, "status": "current"})
            new_files[rel] = _state_file_entry(desired)
        elif current_hash is None:
            changes.append(Change(rel, desired.data, desired.mode, "create", "missing"))
            statuses.append({"path": rel, "status": "create"})
            new_files[rel] = _state_file_entry(desired)
        elif old_entry and current_hash == old_entry.get("sha256"):
            changes.append(Change(rel, desired.data, desired.mode, "update", "managed file unchanged since previous install"))
            statuses.append({"path": rel, "status": "update"})
            new_files[rel] = _state_file_entry(desired)
        elif force:
            changes.append(Change(rel, desired.data, desired.mode, "overwrite", "forced overwrite of modified or unowned file"))
            statuses.append({"path": rel, "status": "force-overwrite"})
            new_files[rel] = _state_file_entry(desired)
        else:
            conflicts.append(Conflict(rel, desired.data, "existing file is user-modified or was not previously managed"))
            statuses.append({"path": rel, "status": "conflict"})

    for rel, old_entry in sorted(old_files.items()):
        if rel in desired_files:
            continue
        path = safe_join(target, rel, reject_final_symlink=True)
        if not path.exists():
            new_files.pop(rel, None)
            statuses.append({"path": rel, "status": "obsolete-already-absent"})
        elif path.is_file() and sha256_file(path) == old_entry.get("sha256"):
            changes.append(Change(rel, None, 0o644, "remove", "obsolete managed file"))
            new_files.pop(rel, None)
            statuses.append({"path": rel, "status": "remove-obsolete"})
        elif force:
            changes.append(Change(rel, None, 0o644, "remove", "forced removal of obsolete modified file"))
            new_files.pop(rel, None)
            statuses.append({"path": rel, "status": "force-remove-obsolete"})
        else:
            conflicts.append(Conflict(rel, None, "obsolete managed file was modified; retained"))
            statuses.append({"path": rel, "status": "conflict-obsolete"})

    for rel, desired in sorted(desired_blocks.items()):
        path = safe_join(target, rel, reject_final_symlink=True)
        if path.exists() and not path.is_file():
            raise ValidationError(f"Managed block target is not a regular file: {rel}")
        file_existed_now = path.is_file()
        if file_existed_now:
            existing, bom = read_utf8_preserve(path)
            current_mode = path.stat().st_mode & 0o777
        else:
            existing, bom, current_mode = "", False, 0o644
        current_block, block_status = extract_block(existing, desired.begin, desired.end)
        old_entry = old_blocks.get(rel)
        old_metadata = dict(old_entry.get("file", {})) if isinstance(old_entry, dict) and isinstance(old_entry.get("file"), dict) else {}
        newline = detect_newline(existing) if existing else "\n"
        desired_rendered = render_newlines(desired.text, newline)

        if block_status == "malformed":
            if force:
                raise ValidationError(f"Refusing to guess malformed managed markers even with --force: {rel}")
            conflicts.append(Conflict(rel, encode_utf8_text(desired_rendered, bom=bom), "managed block markers are malformed or duplicated"))
            statuses.append({"path": rel, "status": "conflict-malformed-block"})
            continue

        if current_block is not None and canonical_newlines(current_block) == canonical_newlines(desired.text):
            metadata = old_metadata or {
                "placement": "existing",
                "file_existed": True,
                "original_mode": oct(current_mode),
                "bom": bom,
                "newline": newline,
            }
            new_blocks[rel] = _state_block_entry(desired, metadata)
            statuses.append({"path": rel, "status": "current-block"})
            continue

        if current_block is not None and old_entry and not _block_matches_entry(current_block, old_entry) and not force:
            candidate, _, _ = merge_block_detailed(existing, desired, previous_metadata=old_metadata)
            conflicts.append(
                Conflict(
                    rel,
                    encode_utf8_text(candidate, bom=bom) if candidate is not None else encode_utf8_text(desired_rendered, bom=bom),
                    "managed block was modified",
                )
            )
            statuses.append({"path": rel, "status": "conflict-block"})
            continue
        if current_block is not None and not old_entry and not force:
            candidate, _, _ = merge_block_detailed(existing, desired)
            conflicts.append(
                Conflict(
                    rel,
                    encode_utf8_text(candidate, bom=bom) if candidate is not None else encode_utf8_text(desired_rendered, bom=bom),
                    "unowned managed markers already exist",
                )
            )
            statuses.append({"path": rel, "status": "conflict-unowned-block"})
            continue

        merged, merge_status, metadata = merge_block_detailed(existing, desired, previous_metadata=old_metadata)
        if merged is None:
            raise ValidationError(f"Could not merge managed block: {rel}")
        if old_metadata:
            # Keep the original restoration contract across upgrades.
            for key in ("placement", "file_existed", "original_mode", "bom", "prefix_added", "suffix_added"):
                if key in old_metadata:
                    metadata[key] = old_metadata[key]
        else:
            metadata.update({
                "file_existed": file_existed_now,
                "original_mode": oct(current_mode),
                "bom": bom,
            })
        metadata["newline"] = newline
        changes.append(Change(rel, encode_utf8_text(merged, bom=bom), current_mode, "update-block", merge_status))
        new_blocks[rel] = _state_block_entry(desired, metadata)
        statuses.append({"path": rel, "status": merge_status})

    for rel, old_entry in sorted(old_blocks.items()):
        if rel in desired_blocks:
            continue
        path = safe_join(target, rel, reject_final_symlink=True)
        if not path.is_file():
            new_blocks.pop(rel, None)
            statuses.append({"path": rel, "status": "obsolete-block-absent"})
            continue
        existing, bom = read_utf8_preserve(path)
        current_mode = path.stat().st_mode & 0o777
        current, block_status = extract_block(existing, str(old_entry.get("begin", "")), str(old_entry.get("end", "")))
        if block_status == "missing":
            new_blocks.pop(rel, None)
            statuses.append({"path": rel, "status": "obsolete-block-absent"})
        elif block_status == "malformed":
            conflicts.append(Conflict(rel, None, "obsolete managed block markers are malformed"))
            statuses.append({"path": rel, "status": "conflict-obsolete-block"})
        elif current is not None and (_block_matches_entry(current, old_entry) or force):
            metadata = old_entry.get("file", {}) if isinstance(old_entry.get("file"), dict) else {}
            updated, _ = remove_block_detailed(
                existing,
                str(old_entry["begin"]),
                str(old_entry["end"]),
                metadata=metadata,
            )
            original_existed = bool(metadata.get("file_existed", True))
            original_bom = bool(metadata.get("bom", bom))
            try:
                original_mode = int(str(metadata.get("original_mode", oct(current_mode))), 8)
            except (TypeError, ValueError):
                original_mode = current_mode
            data = None if updated == "" and not original_existed else encode_utf8_text(updated or "", bom=original_bom)
            changes.append(Change(rel, data, original_mode, "remove-block", "adapter no longer selected"))
            new_blocks.pop(rel, None)
            statuses.append({"path": rel, "status": "remove-obsolete-block"})
        else:
            conflicts.append(Conflict(rel, None, "obsolete managed block was modified; retained"))
            statuses.append({"path": rel, "status": "conflict-obsolete-block"})

    new_state = {
        "schema": INSTALL_SCHEMA,
        "version": PACKAGE_VERSION,
        "installed_at": (old_state or {}).get("installed_at", utc_now()),
        "updated_at": utc_now(),
        "package_fingerprint": package_fingerprint(package_root),
        "host_mode": mode,
        "hosts": sorted(hosts),
        "managed_files": dict(sorted(new_files.items())),
        "managed_blocks": dict(sorted(new_blocks.items())),
        "last_operation": "upgrade" if old_state else "install",
        "last_backup": None,
        "conflicts": len(conflicts),
    }
    state_schema_path = package_root / "schemas/install-state.schema.json"
    if state_schema_path.is_file():
        state_schema = read_json(state_schema_path)
        if not isinstance(state_schema, dict):
            raise ValidationError(f"Install state schema root must be an object: {state_schema_path}")
        validate_instance(new_state, state_schema, "generated install state")
    return {
        "old_state": old_state,
        "new_state": new_state,
        "changes": changes,
        "conflicts": conflicts,
        "statuses": statuses,
        "hosts": sorted(hosts),
        "host_mode": mode,
    }


def install(
    package_root: Path,
    target: Path,
    *,
    hosts_spec: Optional[str] = None,
    profile: bool = False,
    force: bool = False,
    dry_run: bool = False,
    require_existing: bool = False,
    allow_downgrade: bool = False,
) -> Dict[str, Any]:
    package_root = package_root.resolve()
    package_check = verify_package(package_root)
    if not package_check["ok"]:
        messages = "; ".join(item["message"] for item in package_check["issues"] if item.get("severity") == "error")
        raise ValidationError(f"Package verification failed: {messages}")

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
    target = target.resolve()
    if dry_run:
        plan = plan_install(
            package_root,
            target,
            hosts_spec=hosts_spec,
            profile=profile,
            force=force,
            require_existing=require_existing,
            allow_downgrade=allow_downgrade,
        )
        return {
            "ok": not plan["conflicts"],
            "dry_run": True,
            "version": PACKAGE_VERSION,
            "host_mode": plan["host_mode"],
            "hosts": plan["hosts"],
            "change_count": len(plan["changes"]) if not plan["conflicts"] else 0,
            "planned_change_count": len(plan["changes"]),
            "conflict_count": len(plan["conflicts"]),
            "backup": None,
            "conflict_path": None,
            "statuses": plan["statuses"],
        }
    lock_path = safe_join(target, LOCK_REL)
    with FileLock(lock_path, force_stale=force):
        plan = plan_install(
            package_root,
            target,
            hosts_spec=hosts_spec,
            profile=profile,
            force=force,
            require_existing=require_existing,
            allow_downgrade=allow_downgrade,
        )

        conflict_id: Optional[str] = None
        conflict_root: Optional[Path] = None
        if plan["conflicts"]:
            if not dry_run:
                conflict_id = timestamp_id()
                conflict_root = _write_conflicts(target, plan["conflicts"], conflict_id)
            return {
                "ok": False,
                "dry_run": dry_run,
                "version": PACKAGE_VERSION,
                "host_mode": plan["host_mode"],
                "hosts": plan["hosts"],
                "change_count": 0,
                "planned_change_count": len(plan["changes"]),
                "conflict_count": len(plan["conflicts"]),
                "backup": None,
                "conflict_path": str(conflict_root.relative_to(target)) if conflict_root else None,
                "statuses": plan["statuses"],
            }

        old_state = plan["old_state"]
        state_is_current = bool(
            old_state
            and not plan["changes"]
            and old_state.get("version") == PACKAGE_VERSION
            and old_state.get("host_mode") == plan["host_mode"]
            and old_state.get("hosts", []) == plan["hosts"]
            and old_state.get("managed_files", {}) == plan["new_state"].get("managed_files", {})
            and old_state.get("managed_blocks", {}) == plan["new_state"].get("managed_blocks", {})
            and old_state.get("package_fingerprint") == plan["new_state"].get("package_fingerprint")
        )
        if state_is_current:
            return {
                "ok": True,
                "dry_run": dry_run,
                "version": PACKAGE_VERSION,
                "host_mode": plan["host_mode"],
                "hosts": plan["hosts"],
                "change_count": 0,
                "conflict_count": 0,
                "backup": None,
                "conflict_path": None,
                "statuses": plan["statuses"],
            }

        operation_id = _apply_changes(target, plan["changes"], old_state, plan["new_state"], dry_run=dry_run)
        if operation_id and not dry_run:
            state = load_state(target, required=True)
            assert state is not None
            state["last_backup"] = operation_id
            state["last_conflict"] = None
            write_json(safe_join(target, STATE_REL), state, mode=0o600)
        return {
            "ok": True,
            "dry_run": dry_run,
            "version": PACKAGE_VERSION,
            "host_mode": plan["host_mode"],
            "hosts": plan["hosts"],
            "change_count": len(plan["changes"]),
            "conflict_count": 0,
            "backup": operation_id,
            "conflict_path": None,
            "statuses": plan["statuses"],
        }


def _verify_manifest_at(root: Path) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    try:
        expected = build_skill_manifest(root)
    except (ValidationError, OSError, UnicodeError) as exc:
        return [{"severity": "error", "code": "manifest-source-invalid", "message": str(exc)}]

    manifest_path = root / "skills/MANIFEST.json"
    if not manifest_path.is_file():
        issues.append({"severity": "error", "code": "manifest-missing", "message": "Missing skills/MANIFEST.json"})
    else:
        try:
            actual = read_json(manifest_path)
            if actual != expected:
                issues.append({"severity": "error", "code": "manifest-drift", "message": "skills/MANIFEST.json is not generated from current Skill files and sidecars"})
        except ValidationError as exc:
            issues.append({"severity": "error", "code": "manifest-invalid", "message": str(exc)})
    issues.extend(validate_skill_graph(root, expected))
    return issues


def verify_install(target: Path) -> Dict[str, Any]:
    target = target.resolve()
    state = load_state(target, required=True)
    assert state is not None
    issues: List[Dict[str, str]] = []
    for rel, entry in state.get("managed_files", {}).items():
        try:
            path = safe_join(target, rel, reject_final_symlink=True)
        except ValidationError as exc:
            issues.append({"severity": "error", "code": "unsafe-path", "message": str(exc)})
            continue
        if not path.is_file():
            issues.append({"severity": "error", "code": "missing-file", "message": f"Missing managed file: {rel}"})
        elif sha256_file(path) != entry.get("sha256"):
            issues.append({"severity": "error", "code": "file-drift", "message": f"Managed file changed: {rel}"})
    for rel, entry in state.get("managed_blocks", {}).items():
        try:
            path = safe_join(target, rel, reject_final_symlink=True)
        except ValidationError as exc:
            issues.append({"severity": "error", "code": "unsafe-path", "message": str(exc)})
            continue
        if not path.is_file():
            issues.append({"severity": "error", "code": "missing-block-file", "message": f"Missing managed block target: {rel}"})
            continue
        text, _ = read_utf8_preserve(path)
        block, status = extract_block(text, str(entry.get("begin", "")), str(entry.get("end", "")))
        if status != "ok" or block is None:
            issues.append({"severity": "error", "code": "block-missing", "message": f"Managed block missing or malformed: {rel}"})
        elif not _block_matches_entry(block, entry):
            issues.append({"severity": "error", "code": "block-drift", "message": f"Managed block changed: {rel}"})
    if (target / "skills").is_dir():
        issues.extend(_verify_manifest_at(target))
    errors = [item for item in issues if item["severity"] == "error"]
    return {
        "ok": not errors,
        "version": state.get("version"),
        "hosts": state.get("hosts", []),
        "managed_file_count": len(state.get("managed_files", {})),
        "managed_block_count": len(state.get("managed_blocks", {})),
        "issues": issues,
    }


def status(target: Path) -> Dict[str, Any]:
    target = target.resolve()
    state = load_state(target, required=False)
    if state is None:
        return {"installed": False, "ok": True, "target": str(target)}
    verification = verify_install(target)
    return {
        "installed": True,
        "ok": verification["ok"],
        "target": str(target),
        "version": state.get("version"),
        "updated_at": state.get("updated_at"),
        "host_mode": state.get("host_mode"),
        "hosts": state.get("hosts", []),
        "last_backup": state.get("last_backup"),
        "last_conflict": state.get("last_conflict"),
        "issues": verification["issues"],
    }


def diff_install(package_root: Path, target: Path, *, hosts_spec: Optional[str] = None, profile: bool = False) -> Dict[str, Any]:
    target = target.resolve()
    old_state = load_state(target, required=False)
    if hosts_spec is None and old_state:
        mode = old_state.get("host_mode")
        hosts_spec = ",".join(old_state.get("hosts", [])) if mode == "explicit" else str(mode or "auto")
    plan = plan_install(package_root, target, hosts_spec=hosts_spec, profile=profile, force=False, require_existing=False, allow_downgrade=True)
    return {
        "ok": not plan["conflicts"],
        "target": str(target),
        "version": PACKAGE_VERSION,
        "change_count": len(plan["changes"]),
        "conflict_count": len(plan["conflicts"]),
        "statuses": plan["statuses"],
    }


def doctor(package_root: Path, target: Path, *, repair: bool = False) -> Dict[str, Any]:
    target = target.resolve()
    issues: List[Dict[str, str]] = []
    repairs: List[str] = []
    try:
        state = load_state(target, required=False)
    except ValidationError as exc:
        state = None
        issues.append({"severity": "error", "code": "state-invalid", "message": str(exc)})
    lock_path = safe_join(target, LOCK_REL, reject_final_symlink=False)
    if lock_path.exists():
        age = max(0.0, __import__("time").time() - lock_path.stat().st_mtime)
        if age > 24 * 60 * 60:
            issues.append({"severity": "warning", "code": "stale-lock", "message": f"Install lock is {int(age)} seconds old"})
            if repair:
                lock_path.unlink(missing_ok=True)
                repairs.append(f"Removed stale {LOCK_REL}")
        else:
            issues.append({"severity": "warning", "code": "active-lock", "message": "Install lock exists; another process may be active"})
    for rel, begin, end in [
        ("AGENTS.md", AGENTS_BEGIN, AGENTS_END),
        ("CLAUDE.md", CLAUDE_BEGIN, CLAUDE_END),
        ("GEMINI.md", GEMINI_BEGIN, GEMINI_END),
        (".github/copilot-instructions.md", COPILOT_BEGIN, COPILOT_END),
    ]:
        path = safe_join(target, rel, reject_final_symlink=False)
        if path.is_file():
            text, _ = read_utf8_preserve(path)
            _, block_status = extract_block(text, begin, end)
            if block_status == "malformed":
                issues.append({"severity": "error", "code": "malformed-markers", "message": f"Malformed or duplicate managed markers in {rel}"})
    if state:
        verification = verify_install(target)
        issues.extend(verification["issues"])
    is_source_package = (
        (package_root / "tools/psp.py").is_file()
        and (package_root / "adapters/HOSTS.json").is_file()
        and (package_root / "skills/MANIFEST.json").is_file()
    )
    if is_source_package:
        package_check = verify_package(package_root)
        if not package_check["ok"]:
            issues.extend(
                {"severity": "error", "code": "package-invalid", "message": item["message"]}
                for item in package_check["issues"]
                if item["severity"] == "error"
            )
    else:
        issues.append({
            "severity": "info",
            "code": "source-package-unavailable",
            "message": "Source bundle is not available to this installed CLI; package-level checks were skipped.",
        })
    errors = [item for item in issues if item["severity"] == "error"]
    return {"ok": not errors, "installed": state is not None, "issues": issues, "repairs": repairs}


def uninstall(target: Path, *, force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    target = target.resolve()
    lock_path = safe_join(target, LOCK_REL)
    with FileLock(lock_path, force_stale=force):
        state = load_state(target, required=True)
        assert state is not None
        changes: List[Change] = []
        conflicts: List[Conflict] = []
        statuses: List[Dict[str, str]] = []

        for rel, entry in sorted(state.get("managed_files", {}).items()):
            path = safe_join(target, rel, reject_final_symlink=True)
            if not path.exists():
                statuses.append({"path": rel, "status": "already-absent"})
            elif path.is_file() and (sha256_file(path) == entry.get("sha256") or force):
                changes.append(Change(rel, None, 0o644, "remove", "uninstall"))
                statuses.append({"path": rel, "status": "remove"})
            else:
                conflicts.append(Conflict(rel, None, "managed file was modified; retained"))
                statuses.append({"path": rel, "status": "conflict"})

        for rel, entry in sorted(state.get("managed_blocks", {}).items()):
            path = safe_join(target, rel, reject_final_symlink=True)
            if not path.is_file():
                statuses.append({"path": rel, "status": "block-already-absent"})
                continue
            existing, current_bom = read_utf8_preserve(path)
            current, block_status = extract_block(existing, str(entry.get("begin", "")), str(entry.get("end", "")))
            if block_status == "missing":
                statuses.append({"path": rel, "status": "block-already-absent"})
            elif block_status == "ok" and current is not None and (_block_matches_entry(current, entry) or force):
                metadata = entry.get("file", {}) if isinstance(entry.get("file"), dict) else {}
                updated, _ = remove_block_detailed(
                    existing,
                    str(entry["begin"]),
                    str(entry["end"]),
                    metadata=metadata,
                )
                original_existed = bool(metadata.get("file_existed", True))
                original_bom = bool(metadata.get("bom", current_bom))
                try:
                    original_mode = int(str(metadata.get("original_mode", oct(path.stat().st_mode & 0o777))), 8)
                except (TypeError, ValueError):
                    original_mode = path.stat().st_mode & 0o777
                data = None if updated == "" and not original_existed else encode_utf8_text(updated or "", bom=original_bom)
                changes.append(Change(rel, data, original_mode, "remove-block", "uninstall"))
                statuses.append({"path": rel, "status": "remove-block"})
            else:
                conflicts.append(Conflict(rel, None, "managed block was modified or malformed; retained"))
                statuses.append({"path": rel, "status": "conflict-block"})

        conflict_root: Optional[Path] = None
        if conflicts:
            if not dry_run:
                conflict_root = _write_conflicts(target, conflicts, timestamp_id())
            return {
                "ok": False,
                "dry_run": dry_run,
                "change_count": 0,
                "planned_change_count": len(changes),
                "conflict_count": len(conflicts),
                "backup": None,
                "conflict_path": str(conflict_root.relative_to(target)) if conflict_root else None,
                "statuses": statuses,
            }

        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "change_count": len(changes),
                "conflict_count": 0,
                "backup": None,
                "conflict_path": None,
                "statuses": statuses,
            }

        operation_id = timestamp_id()
        rels = [change.rel for change in changes] + [STATE_REL]
        backup_root = _backup_snapshot(target, rels, operation_id, state)
        try:
            for change in changes:
                path = safe_join(target, change.rel, reject_final_symlink=True)
                if change.data is None:
                    if path.is_file():
                        path.unlink()
                        remove_empty_parents(path, target)
                else:
                    atomic_write_bytes(path, change.data, mode=change.mode)
            safe_join(target, STATE_REL).unlink(missing_ok=True)
        except Exception:
            _restore_snapshot(target, backup_root)
            raise
        return {
            "ok": True,
            "dry_run": False,
            "change_count": len(changes),
            "conflict_count": 0,
            "backup": operation_id,
            "conflict_path": None,
            "statuses": statuses,
        }


def list_backups(target: Path) -> List[Dict[str, Any]]:
    root = safe_join(target, BACKUPS_REL, reject_final_symlink=False)
    if not root.is_dir():
        return []
    result: List[Dict[str, Any]] = []
    for path in sorted((p for p in root.iterdir() if p.is_dir()), reverse=True):
        snapshot = path / "snapshot.json"
        if snapshot.is_file():
            try:
                data = read_json(snapshot)
                result.append({"id": path.name, "created_at": data.get("created_at"), "path_count": len(data.get("paths", {}))})
            except ValidationError:
                result.append({"id": path.name, "invalid": True})
    return result


def rollback(target: Path, *, backup_id: Optional[str] = None, dry_run: bool = False, force: bool = False) -> Dict[str, Any]:
    target = target.resolve()
    backups = list_backups(target)
    if not backups:
        raise ValidationError("No PSP backups are available")
    selected = backup_id or backups[0]["id"]
    if selected not in {item["id"] for item in backups}:
        raise ValidationError(f"Unknown backup id: {selected}")
    backup_root = safe_join(target, f"{BACKUPS_REL}/{selected}", reject_final_symlink=True)
    snapshot = read_json(backup_root / "snapshot.json")
    paths = sorted(snapshot.get("paths", {}).keys())
    if dry_run:
        return {"ok": True, "dry_run": True, "backup": selected, "paths": paths}
    lock_path = safe_join(target, LOCK_REL, reject_final_symlink=False)
    with FileLock(lock_path, force_stale=force):
        pre_id = "pre-rollback-" + timestamp_id()
        current_state = load_state(target, required=False)
        pre_backup = _backup_snapshot(target, paths + [STATE_REL], pre_id, current_state)
        try:
            _restore_snapshot(target, backup_root)
        except Exception:
            _restore_snapshot(target, pre_backup)
            raise
    return {"ok": True, "dry_run": False, "backup": selected, "pre_rollback_backup": pre_id, "paths": paths}


def write_manifest(package_root: Path) -> Dict[str, Any]:
    manifest = build_skill_manifest(package_root)
    graph_errors = [item for item in validate_skill_graph(package_root, manifest) if item.get("severity") == "error"]
    if graph_errors:
        raise ValidationError("; ".join(item["message"] for item in graph_errors))
    write_json(package_root / "skills/MANIFEST.json", manifest)
    return manifest


def _append_schema_issues(
    issues: List[Dict[str, str]],
    instance: Any,
    schema: Mapping[str, Any],
    *,
    source: str,
    code: str,
) -> None:
    for message in validation_errors(instance, schema):
        issues.append({"severity": "error", "code": code, "message": f"{source}: {message}"})


def verify_package(package_root: Path) -> Dict[str, Any]:
    package_root = package_root.resolve()
    issues: List[Dict[str, str]] = []
    required = [
        "AGENTS.md", "README.md", "README.zh.md", "LICENSE", "LICENSE-APACHE-2.0", "NOTICE",
        "SOURCE-BASELINE.md", "CHANGELOG.md", "BUILD-REPORT.md", "SECURITY.md", "CONTRIBUTING.md",
        "reference/LICENSING-AND-PROVENANCE.md", "install.sh", "verify.sh",
        "tools/psp.py", "tools/psp_util.py", "tools/psp_installer.py", "tools/psp_trace.py",
        "tools/psp_eval.py", "tools/psp_schema.py", "tools/build_manifest.py", "tools/eval_runner.py",
        "tools/package_release.py", "skills/MANIFEST.json", "adapters/HOSTS.json", "compat/hosts.yaml",
        "schemas/manifest.schema.json", "schemas/skill-sidecar.schema.json",
        "schemas/install-state.schema.json", "schemas/host-adapters.schema.json",
        "schemas/run-trace.schema.json", "schemas/eval-case.schema.json",
        "schemas/eval-result.schema.json", "schemas/eval-grade.schema.json",
        "schemas/eval-report.schema.json", "schemas/eval-capture-score.schema.json",
        "schemas/eval-capture-report.schema.json",
        ".github/workflows/ci.yml", ".github/workflows/nightly-eval.yml", ".github/workflows/release.yml",
    ]
    for rel in required:
        if not (package_root / rel).is_file():
            issues.append({"severity": "error", "code": "required-missing", "message": f"Missing package file: {rel}"})

    schemas: Dict[str, Mapping[str, Any]] = {}
    schemas_root = package_root / "schemas"
    if schemas_root.is_dir():
        for schema_path in sorted(schemas_root.glob("*.json")):
            try:
                value = read_json(schema_path)
                if not isinstance(value, dict):
                    raise ValidationError("schema root must be an object")
                if value.get("type") is None:
                    raise ValidationError("schema must declare a root type")
                schemas[schema_path.name] = value
            except (ValidationError, OSError) as exc:
                issues.append({"severity": "error", "code": "schema-invalid", "message": f"{schema_path}: {exc}"})

    if (package_root / "skills").is_dir():
        issues.extend(_verify_manifest_at(package_root))

    manifest_path = package_root / "skills/MANIFEST.json"
    manifest_schema = schemas.get("manifest.schema.json")
    if manifest_path.is_file() and manifest_schema:
        try:
            _append_schema_issues(
                issues, read_json(manifest_path), manifest_schema,
                source="skills/MANIFEST.json", code="manifest-schema",
            )
        except ValidationError as exc:
            issues.append({"severity": "error", "code": "manifest-invalid", "message": str(exc)})

    sidecar_schema = schemas.get("skill-sidecar.schema.json")
    if sidecar_schema:
        for sidecar_path in sorted((package_root / "skills").glob("*/psp.skill.json")):
            try:
                _append_schema_issues(
                    issues, read_json(sidecar_path), sidecar_schema,
                    source=sidecar_path.relative_to(package_root).as_posix(), code="sidecar-schema",
                )
            except ValidationError as exc:
                issues.append({"severity": "error", "code": "sidecar-invalid", "message": str(exc)})

    hosts: Dict[str, Any] = {}
    try:
        raw_hosts = read_json(package_root / "adapters/HOSTS.json")
        if not isinstance(raw_hosts, dict):
            raise ValidationError("adapters/HOSTS.json must contain an object")
        hosts = raw_hosts
        host_schema = schemas.get("host-adapters.schema.json")
        if host_schema:
            _append_schema_issues(
                issues, hosts, host_schema,
                source="adapters/HOSTS.json", code="hosts-schema",
            )
        if hosts.get("default") != "auto":
            issues.append({"severity": "error", "code": "host-default", "message": "adapters/HOSTS.json default must be auto"})
        if hosts.get("version") != PACKAGE_VERSION:
            issues.append({"severity": "error", "code": "host-version", "message": "adapters/HOSTS.json version mismatch"})
        host_entries = hosts.get("hosts", {})
        if isinstance(host_entries, dict):
            declared_hosts = set(map(str, host_entries))
            if declared_hosts != ALL_HOSTS:
                issues.append({
                    "severity": "error", "code": "host-set",
                    "message": f"Host manifest must declare exactly {sorted(ALL_HOSTS)}; found {sorted(declared_hosts)}",
                })
            declared_destinations: Set[str] = set()
            for host_name, config in host_entries.items():
                if not isinstance(config, dict):
                    continue
                for used in config.get("uses", []):
                    if used not in host_entries:
                        issues.append({
                            "severity": "error", "code": "host-reference",
                            "message": f"Host {host_name} uses unknown host adapter {used}",
                        })
                for destination in config.get("files", []):
                    destination = str(destination)
                    declared_destinations.add(destination)
                    if destination in GENERATED_ADAPTER_FILES:
                        continue
                    source_rel = ADAPTER_FILE_SOURCES.get(destination)
                    if source_rel is None:
                        issues.append({
                            "severity": "error", "code": "adapter-source-unknown",
                            "message": f"No package source mapping exists for declared adapter file {destination}",
                        })
                    elif not (package_root / source_rel).is_file():
                        issues.append({
                            "severity": "error", "code": "adapter-source-missing",
                            "message": f"Missing adapter source {source_rel} for {destination}",
                        })
            for destination, source_rel in ADAPTER_FILE_SOURCES.items():
                if destination not in declared_destinations:
                    issues.append({
                        "severity": "error", "code": "adapter-source-unlisted",
                        "message": f"Adapter source {source_rel} is not declared by adapters/HOSTS.json",
                    })
                elif not (package_root / source_rel).is_file():
                    issues.append({
                        "severity": "error", "code": "adapter-source-missing",
                        "message": f"Missing adapter source {source_rel} for {destination}",
                    })
    except (FileNotFoundError, ValidationError) as exc:
        issues.append({"severity": "error", "code": "hosts-invalid", "message": str(exc)})

    case_schema = schemas.get("eval-case.schema.json")
    if case_schema:
        for case_path in sorted((package_root / "evals/cases").glob("*.json")):
            try:
                _append_schema_issues(
                    issues, read_json(case_path), case_schema,
                    source=case_path.relative_to(package_root).as_posix(), code="eval-case-schema",
                )
            except ValidationError as exc:
                issues.append({"severity": "error", "code": "eval-case-invalid", "message": str(exc)})

    result_schema = schemas.get("eval-result.schema.json")
    captures_path = package_root / "evals/samples/captures.json"
    if result_schema and captures_path.is_file():
        try:
            captures = read_json(captures_path)
            results = captures.get("results", []) if isinstance(captures, dict) else []
            if not isinstance(results, list):
                raise ValidationError("evals/samples/captures.json results must be an array")
            for index, result in enumerate(results):
                _append_schema_issues(
                    issues, result, result_schema,
                    source=f"evals/samples/captures.json/results[{index}]", code="eval-result-schema",
                )
        except ValidationError as exc:
            issues.append({"severity": "error", "code": "eval-result-invalid", "message": str(exc)})

    _, eval_errors = load_cases(package_root)
    for error in eval_errors:
        issues.append({"severity": "error", "code": "eval-case-invalid", "message": error})

    errors = [item for item in issues if item["severity"] == "error"]
    try:
        fingerprint = package_fingerprint(package_root)
    except (OSError, ValidationError) as exc:
        fingerprint = None
        issues.append({"severity": "error", "code": "fingerprint-failed", "message": str(exc)})
        errors = [item for item in issues if item["severity"] == "error"]
    return {
        "ok": not errors,
        "version": PACKAGE_VERSION,
        "fingerprint": fingerprint,
        "skill_count": len(list((package_root / "skills").glob("*/SKILL.md"))) if (package_root / "skills").exists() else 0,
        "eval_case_count": len(list((package_root / "evals/cases").glob("*.json"))) if (package_root / "evals/cases").exists() else 0,
        "issues": issues,
    }
