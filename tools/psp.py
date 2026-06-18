#!/usr/bin/env python3
"""Pragmatic Skills Pack installer, verifier, and upgrader.

Shell-first installer backend with host adapters:
- never downloads anything;
- never runs project install/test/build commands;
- preserves existing instruction files outside PSP managed blocks;
- overwrites only PSP-managed files that are unchanged since the last install;
- backs up replaced files and writes conflicts for manual review;
- supports AGENTS.md plus host adapters for Claude Code, Codex, OpenCode,
  Hermes Agent, Gemini CLI, GitHub Copilot, Cursor, and similar tools.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

PACKAGE_ID = "pragmatic-skills-pack"
STATE_DIR = ".psp"
STATE_FILE = "install.json"
TOOL_DEST = Path(STATE_DIR) / "bin" / "psp.py"
ENTRY_SKILL = "skills/using-pragmatic-skills/SKILL.md"
NATIVE_ENTRY_SRC = "adapters/native-entry/SKILL.md"
CLAUDE_ENTRY_SRC = "adapters/claude-entry/SKILL.md"
NATIVE_ENTRY_DEST_AGENTS = ".agents/skills/using-pragmatic-skills/SKILL.md"
NATIVE_ENTRY_DEST_CLAUDE = ".claude/skills/psp-claude-entry/SKILL.md"
BEGIN = "<!-- PSP:BEGIN -->"
END = "<!-- PSP:END -->"
BEGIN_RE = re.compile(r"<!--\s*PSP:BEGIN[^>]*-->", re.IGNORECASE)
END_RE = re.compile(r"<!--\s*PSP:END\s*-->", re.IGNORECASE)

HOST_ALIASES = {
    "default": "auto",
    "agent": "agents",
    "agents-md": "agents",
    "agent-skills": "agents",
    "openai": "codex",
    "openai-codex": "codex",
    "claude-code": "claude",
    "anthropic": "claude",
    "open-code": "opencode",
    "open_code": "opencode",
    "hermes-agent": "hermes",
    "nous-hermes": "hermes",
    "gemini-cli": "gemini",
    "github-copilot": "copilot",
    "copilot-coding-agent": "copilot",
}
KNOWN_HOSTS = {"agents", "codex", "claude", "opencode", "hermes", "gemini", "copilot", "cursor"}
ALL_HOSTS = {"agents", "codex", "claude", "opencode", "hermes", "gemini", "copilot", "cursor"}


def stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_manifest(root: Path) -> Dict[str, Any]:
    p = root / "skills" / "MANIFEST.json"
    if not p.exists():
        raise RuntimeError(f"missing package manifest: {p}")
    m = read_json(p)
    if m.get("package_id") != PACKAGE_ID and m.get("id") != PACKAGE_ID:
        raise RuntimeError(f"not a {PACKAGE_ID} manifest: {p}")
    return m


def pkg_version(root: Path) -> str:
    return str(load_manifest(root).get("version", "unknown"))


def rel_to(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_core_payload_files(root: Path) -> List[str]:
    """Core managed files copied to the target root.

    The root `skills/` directory remains the internal workflow source of truth.
    Host-native skill files are thin entry adapters installed separately.
    """
    out: List[str] = []
    for base in ("skills", "reference"):
        b = root / base
        if b.exists():
            for p in b.rglob("*"):
                if p.is_file():
                    out.append(rel_to(p, root))
    return sorted(set(out))


def managed_file_mappings(root: Path, hosts: Set[str]) -> List[Tuple[str, str]]:
    """Return (source-relative, target-relative) mappings for hash-managed files."""
    mappings: List[Tuple[str, str]] = [(r, r) for r in iter_core_payload_files(root)]
    if "agents" in hosts:
        mappings.append((NATIVE_ENTRY_SRC, NATIVE_ENTRY_DEST_AGENTS))
    if "claude" in hosts:
        mappings.append((CLAUDE_ENTRY_SRC, NATIVE_ENTRY_DEST_CLAUDE))
    if "opencode" in hosts:
        mappings.append(("adapters/opencode/commands/psp.md", ".opencode/commands/psp.md"))
    if "cursor" in hosts:
        mappings.append(("adapters/cursor/rules/pragmatic-skills-pack.mdc", ".cursor/rules/pragmatic-skills-pack.mdc"))
    # Preserve order while deduping by destination; later entries do not override earlier.
    seen: Set[str] = set()
    deduped: List[Tuple[str, str]] = []
    for src, dst in mappings:
        if dst in seen:
            continue
        seen.add(dst)
        deduped.append((src, dst))
    return deduped


def normalize_host_name(h: str) -> str:
    h = h.strip().lower()
    return HOST_ALIASES.get(h, h)


def detect_hosts(target: Path) -> Set[str]:
    hosts: Set[str] = {"agents", "codex", "hermes"}
    if (target / "CLAUDE.md").exists() or (target / ".claude").exists():
        hosts.add("claude")
    if (target / "GEMINI.md").exists() or (target / ".gemini").exists():
        hosts.add("gemini")
    if (target / ".opencode").exists() or (target / "opencode.json").exists() or (target / "opencode.jsonc").exists():
        hosts.add("opencode")
    if (target / ".cursor").exists() or (target / ".cursorrules").exists():
        hosts.add("cursor")
    if (target / ".github" / "copilot-instructions.md").exists() or (target / ".github" / "instructions").exists():
        hosts.add("copilot")
    return hosts


def parse_hosts(value: str, target: Path) -> Set[str]:
    raw = (value or "all").strip().lower()
    if raw in {"auto", "detect"}:
        return detect_hosts(target)
    if raw in {"none", "core", "no-hosts", "no-host-adapters"}:
        return set()
    if raw in {"all", "everything"}:
        return set(ALL_HOSTS)
    if raw in {"minimal", "agents"}:
        return {"agents", "codex", "hermes"}
    hosts: Set[str] = set()
    for part in re.split(r"[,\s]+", raw):
        if not part:
            continue
        h = normalize_host_name(part)
        if h == "auto":
            hosts |= detect_hosts(target)
            continue
        if h == "all":
            hosts |= ALL_HOSTS
            continue
        if h not in KNOWN_HOSTS:
            raise RuntimeError(f"unknown host adapter: {part}. Known: {', '.join(sorted(KNOWN_HOSTS | set(HOST_ALIASES)))}")
        hosts.add(h)
    # Codex, OpenCode, Hermes, Copilot, Gemini, Cursor all benefit from AGENTS.md/common entry.
    hosts.add("agents")
    if "codex" in hosts:
        hosts.add("agents")
    if "opencode" in hosts:
        hosts.add("agents")
    if "hermes" in hosts:
        hosts.add("agents")
    if "gemini" in hosts:
        hosts.add("agents")
    if "copilot" in hosts:
        hosts.add("agents")
    if "cursor" in hosts:
        hosts.add("agents")
    return hosts


def find_agents_block(text: str) -> Optional[Tuple[int, int]]:
    start = BEGIN_RE.search(text)
    if not start:
        return None
    end = END_RE.search(text, start.end())
    if not end:
        return None
    return start.start(), end.end()


def block_bounds(text: str, begin: str, end: str) -> Optional[Tuple[int, int]]:
    s = text.find(begin)
    if s < 0:
        return None
    e = text.find(end, s + len(begin))
    if e < 0:
        return None
    return s, e + len(end)


def extract_agents_block(root: Path) -> str:
    p = root / "AGENTS.md"
    if not p.exists():
        raise RuntimeError("package AGENTS.md missing")
    text = p.read_text(encoding="utf-8")
    bounds = find_agents_block(text)
    if bounds:
        block = text[bounds[0]:bounds[1]]
        block = BEGIN_RE.sub(BEGIN, block, count=1)
    else:
        block = f"{BEGIN}\n{text.strip()}\n{END}"
    if ENTRY_SKILL not in block:
        raise RuntimeError(f"AGENTS block does not reference {ENTRY_SKILL}")
    return block.strip() + "\n"


def claude_block() -> str:
    return """<!-- PSP:CLAUDE:BEGIN -->
# Pragmatic Skills Pack — Claude Code adapter

@AGENTS.md

Claude Code may also discover the native entry skill at `.claude/skills/psp-claude-entry/SKILL.md`.

Use the PSP entry contract for coding, debugging, review, planning, verification, or repository work. Users provide normal tasks; the agent routes internally from `skills/using-pragmatic-skills/SKILL.md` through an explicit direct route when applicable, otherwise through triage and phase triggers. Do not ask the user to choose individual PSP skills.
<!-- PSP:CLAUDE:END -->
"""


def gemini_block() -> str:
    return """<!-- PSP:GEMINI:BEGIN -->
# Pragmatic Skills Pack — Gemini CLI adapter

@AGENTS.md

Use the PSP entry contract for coding, debugging, review, planning, verification, or repository work. Users provide normal tasks; the agent routes internally from `skills/using-pragmatic-skills/SKILL.md` through an explicit direct route when applicable, otherwise through triage and phase triggers. Do not ask the user to choose individual PSP skills.
<!-- PSP:GEMINI:END -->
"""


def copilot_block() -> str:
    return """<!-- PSP:COPILOT:BEGIN -->
# Pragmatic Skills Pack — GitHub Copilot adapter

This repository also has `AGENTS.md`. For agentic coding work, follow the PSP managed block there.

Start from `skills/using-pragmatic-skills/SKILL.md`; use an explicit direct route when applicable, otherwise route through triage, select one primary mode, and load support skills only by phase trigger. Do not claim tests, builds, reviews, approvals, or command output happened unless they actually happened.
<!-- PSP:COPILOT:END -->
"""


def backup(target: Path, rel_path: str, ts: str, reason: str) -> None:
    src = target / rel_path
    if not src.exists():
        return
    dst = target / STATE_DIR / "backups" / ts / reason / rel_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def update_managed_block(target: Path, rel: str, block: str, begin: str, end: str, title: str, dry_run: bool, ts: str) -> str:
    p = target / rel
    if not p.exists():
        if not dry_run:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"# {title}\n\n" + block.strip() + "\n", encoding="utf-8")
        return "created"
    old = p.read_text(encoding="utf-8")
    bounds = block_bounds(old, begin, end)
    if bounds:
        new = old[:bounds[0]] + block.strip() + old[bounds[1]:]
        if not new.endswith("\n"):
            new += "\n"
        if new == old:
            return "unchanged"
        if not dry_run:
            backup(target, rel, ts, f"{rel.replace('/', '-')}-block-update")
            p.write_text(new, encoding="utf-8")
        return "updated-block"
    new = old.rstrip() + "\n\n" + block.strip() + "\n"
    if not dry_run:
        backup(target, rel, ts, f"{rel.replace('/', '-')}-block-insert")
        p.write_text(new, encoding="utf-8")
    return "inserted-block"


def update_agents(target: Path, root: Path, dry_run: bool, ts: str) -> str:
    return update_managed_block(target, "AGENTS.md", extract_agents_block(root), BEGIN, END, "Project Agent Instructions", dry_run, ts)


def update_host_blocks(target: Path, hosts: Set[str], dry_run: bool, ts: str) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    if "claude" in hosts:
        out["claude"] = {"path": "CLAUDE.md", "action": update_managed_block(target, "CLAUDE.md", claude_block(), "<!-- PSP:CLAUDE:BEGIN -->", "<!-- PSP:CLAUDE:END -->", "Claude Code Instructions", dry_run, ts)}
    if "gemini" in hosts:
        out["gemini"] = {"path": "GEMINI.md", "action": update_managed_block(target, "GEMINI.md", gemini_block(), "<!-- PSP:GEMINI:BEGIN -->", "<!-- PSP:GEMINI:END -->", "Gemini CLI Instructions", dry_run, ts)}
    if "copilot" in hosts:
        out["copilot"] = {"path": ".github/copilot-instructions.md", "action": update_managed_block(target, ".github/copilot-instructions.md", copilot_block(), "<!-- PSP:COPILOT:BEGIN -->", "<!-- PSP:COPILOT:END -->", "GitHub Copilot Instructions", dry_run, ts)}
    return out


def load_state(target: Path) -> Dict[str, Any]:
    p = target / STATE_DIR / STATE_FILE
    if not p.exists():
        return {}
    return read_json(p)


def parse_version(v: str) -> Tuple[int, int, int]:
    parts = str(v).split(".")[:3]
    nums: List[int] = []
    for x in parts:
        nums.append(int("".join(ch for ch in x if ch.isdigit()) or "0"))
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)  # type: ignore[return-value]


def referenced_paths(obj: Any) -> Iterable[str]:
    if isinstance(obj, str):
        if (obj.startswith("skills/") or obj.startswith("reference/") or obj.startswith("adapters/")) and "*" not in obj:
            yield obj.split("#", 1)[0]
    elif isinstance(obj, list):
        for x in obj:
            yield from referenced_paths(x)
    elif isinstance(obj, dict):
        for x in obj.values():
            yield from referenced_paths(x)


def skill_frontmatter_ok(text: str) -> bool:
    if not text.startswith("---"):
        return False
    head = text[:4096]
    return "name:" in head and "description:" in head


def validate_package(root: Path) -> List[str]:
    errors: List[str] = []
    try:
        m = load_manifest(root)
    except Exception as e:
        return [str(e)]
    entry = m.get("entry_skill", ENTRY_SKILL)
    if not (root / entry).exists():
        errors.append(f"entry skill missing: {entry}")
    if not (root / "AGENTS.md").exists():
        errors.append("AGENTS.md missing")
    else:
        text = (root / "AGENTS.md").read_text(encoding="utf-8")
        if ENTRY_SKILL not in text:
            errors.append(f"AGENTS.md does not reference {ENTRY_SKILL}")
    for skill in m.get("skills", []):
        path = skill.get("path")
        if not path:
            errors.append(f"skill without path: {skill.get('name')}")
            continue
        p = root / path
        if not p.exists():
            errors.append(f"skill missing: {path}")
            continue
        head = p.read_text(encoding="utf-8")[:4096]
        if not head.startswith("---") or "schema: psp.skill/v1" not in head or "description:" not in head:
            errors.append(f"skill frontmatter missing schema/name/description: {path}")
    for src in [NATIVE_ENTRY_SRC, CLAUDE_ENTRY_SRC, "adapters/HOSTS.json", "adapters/opencode/commands/psp.md", "adapters/cursor/rules/pragmatic-skills-pack.mdc"]:
        if not (root / src).exists():
            errors.append(f"adapter missing: {src}")
    if not skill_frontmatter_ok((root / NATIVE_ENTRY_SRC).read_text(encoding="utf-8")):
        errors.append(f"native entry adapter frontmatter invalid: {NATIVE_ENTRY_SRC}")
    for path in sorted(set(referenced_paths(m))):
        if not (root / path).exists():
            errors.append(f"manifest references missing path: {path}")
    if not (root / "tools" / "psp.py").exists():
        errors.append("tools/psp.py missing")
    if not (root / "install.sh").exists():
        errors.append("install.sh missing")
    return errors


def find_conflicts(target: Path, root: Path, mappings: List[Tuple[str, str]], state: Dict[str, Any], force: bool) -> List[str]:
    if force:
        return []
    old = state.get("managed_files", {}) if state else {}
    conflicts: List[str] = []
    for src_rel, dst_rel in mappings:
        src = root / src_rel
        dst = target / dst_rel
        if not dst.exists():
            continue
        new_hash = sha256_file(src)
        current_hash = sha256_file(dst)
        if current_hash == new_hash:
            continue
        old_hash = old.get(dst_rel, {}).get("sha256")
        if old_hash and current_hash == old_hash:
            continue
        conflicts.append(dst_rel)
    return conflicts


def write_conflicts(target: Path, root: Path, conflicts: List[str], mappings: List[Tuple[str, str]], ts: str, action: str) -> Path:
    by_dst = {dst: src for src, dst in mappings}
    base = target / STATE_DIR / "conflicts" / ts
    base.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pragmatic Skills Pack conflict report",
        "",
        f"action: {action}",
        f"package_version: {pkg_version(root)}",
        "",
        "The installer did not overwrite these files.",
        "Review the .new candidates, merge manually, then re-run install/upgrade.",
        "",
    ]
    for dst_rel in conflicts:
        src_rel = by_dst[dst_rel]
        src = root / src_rel
        dst = base / (dst_rel + ".new")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        lines.append(f"- {dst_rel} -> {dst.relative_to(target).as_posix()}")
    (base / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return base


def copy_mappings(target: Path, root: Path, mappings: List[Tuple[str, str]], state: Dict[str, Any], dry_run: bool, ts: str) -> Dict[str, Dict[str, str]]:
    old = state.get("managed_files", {}) if state else {}
    result: Dict[str, Dict[str, str]] = {}
    for src_rel, dst_rel in mappings:
        src = root / src_rel
        dst = target / dst_rel
        new_hash = sha256_file(src)
        action = "copy"
        if dst.exists():
            current_hash = sha256_file(dst)
            if current_hash == new_hash:
                action = "adopt-current"
            elif old.get(dst_rel, {}).get("sha256") == current_hash:
                action = "upgrade-managed"
            else:
                action = "overwrite-forced"
            if action != "adopt-current" and not dry_run:
                backup(target, dst_rel, ts, action)
        if action != "adopt-current" and not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        result[dst_rel] = {"sha256": new_hash, "action": action, "source": src_rel}
    return result


def install_tool(target: Path, root: Path, dry_run: bool, ts: str) -> Dict[str, str]:
    src = root / "tools" / "psp.py"
    if not src.exists():
        return {}
    if (target / TOOL_DEST).exists() and not dry_run:
        backup(target, TOOL_DEST.as_posix(), ts, "tool-upgrade")
    if not dry_run:
        (target / TOOL_DEST).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target / TOOL_DEST)
        try:
            (target / TOOL_DEST).chmod((target / TOOL_DEST).stat().st_mode | 0o111)
        except Exception:
            pass
    return {"path": TOOL_DEST.as_posix(), "sha256": sha256_file(src)}


def remove_obsolete(target: Path, state: Dict[str, Any], new_dsts: Sequence[str], dry_run: bool, ts: str) -> List[str]:
    removed: List[str] = []
    old = state.get("managed_files", {}) if state else {}
    new_set = set(new_dsts)
    for r, meta in old.items():
        if r in new_set:
            continue
        p = target / r
        old_hash = meta.get("sha256")
        if p.exists() and old_hash and sha256_file(p) == old_hash:
            if not dry_run:
                backup(target, r, ts, "obsolete")
                p.unlink()
            removed.append(r)
    return removed


def do_install(args: argparse.Namespace, require_existing: bool) -> int:
    root = package_root()
    target = Path(args.target).resolve()
    target.mkdir(parents=True, exist_ok=True)
    errors = validate_package(root)
    if errors:
        print("Package validation failed:", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 2
    try:
        hosts_arg = "none" if getattr(args, "no_host_adapters", False) else ("all" if getattr(args, "all_hosts", False) else args.hosts)
        hosts = parse_hosts(hosts_arg, target)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 2
    manifest = load_manifest(root)
    new_version = str(manifest.get("version", "unknown"))
    state = load_state(target)
    old_version = state.get("package", {}).get("version")
    if require_existing and not state:
        print(f"No existing PSP installation found in {target}. Use install first.", file=sys.stderr)
        return 2
    if old_version and parse_version(new_version) < parse_version(old_version) and not args.allow_downgrade:
        print(f"Refusing downgrade {old_version} -> {new_version}. Use --allow-downgrade to override.", file=sys.stderr)
        return 2
    mappings = managed_file_mappings(root, hosts)
    conflicts = find_conflicts(target, root, mappings, state, args.force)
    ts = stamp()
    action = "upgrade" if state else "install"
    if conflicts and not args.force:
        conflict_dir = write_conflicts(target, root, conflicts, mappings, ts, action)
        print("PSP install/upgrade stopped to avoid overwriting user-modified files.")
        print(f"Target: {target}")
        print(f"Package: {new_version}")
        print(f"Hosts: {', '.join(sorted(hosts))}")
        print(f"Conflicts: {len(conflicts)}")
        print(f"Conflict report: {conflict_dir.relative_to(target).as_posix()}/REPORT.md")
        print("Resolve conflicts manually or re-run with --force to overwrite after backup.")
        return 3
    if args.dry_run:
        print(f"Dry run: would {action} PSP {new_version} into {target}")
        print(f"Hosts: {', '.join(sorted(hosts))}")
        print(f"Managed files: {len(mappings)}")
        print("AGENTS.md: would insert/update managed block")
        print(f"Tool: would install to {TOOL_DEST.as_posix()}")
        return 0
    agents_action = update_agents(target, root, dry_run=False, ts=ts)
    block_actions = update_host_blocks(target, hosts, dry_run=False, ts=ts)
    managed = copy_mappings(target, root, mappings, state, dry_run=False, ts=ts)
    removed = remove_obsolete(target, state, list(managed.keys()), dry_run=False, ts=ts)
    tool = install_tool(target, root, dry_run=False, ts=ts)
    if args.profile:
        profile_src = root / "reference" / "PROJECT-PROFILE.template.md"
        profile_dst = target / STATE_DIR / "project-profile.md"
        if profile_src.exists() and not profile_dst.exists():
            profile_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(profile_src, profile_dst)
    state_new = {
        "schema": "psp.install/v1",
        "package": {
            "id": PACKAGE_ID,
            "name": manifest.get("name", "Pragmatic Skills Pack"),
            "version": new_version,
            "entry_skill": manifest.get("entry_skill", ENTRY_SKILL),
            "source_root": str(root),
        },
        "installed_at": state.get("installed_at") or ts,
        "updated_at": ts,
        "host_adapters": {
            "requested": "none" if getattr(args, "no_host_adapters", False) else args.hosts,
            "installed": sorted(hosts),
            "native_entry": {
                "agents": NATIVE_ENTRY_DEST_AGENTS if "agents" in hosts else None,
                "claude": NATIVE_ENTRY_DEST_CLAUDE if "claude" in hosts else None,
            },
            "blocks": block_actions,
        },
        "agents": {
            "path": "AGENTS.md",
            "mode": "managed-block",
            "marker_begin": BEGIN,
            "marker_end": END,
            "action": agents_action,
            "block_sha256": sha256_bytes(extract_agents_block(root).encode("utf-8")),
        },
        "managed_files": managed,
        "tool": tool,
        "obsolete_removed": removed,
    }
    write_json(target / STATE_DIR / STATE_FILE, state_new)
    print(f"Installed PSP {new_version} into {target}")
    if old_version:
        print(f"Previous version: {old_version}")
    print(f"Hosts: {', '.join(sorted(hosts))}")
    print(f"AGENTS.md: {agents_action}")
    for host, meta in block_actions.items():
        print(f"{meta['path']}: {meta['action']}")
    print(f"Managed files: {len(managed)}")
    if removed:
        print(f"Removed obsolete files: {len(removed)}")
    print(f"Verifier: python3 {TOOL_DEST.as_posix()} verify --target .")
    return 0


def verify_target(target: Path, strict: bool) -> Tuple[int, List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    agents = target / "AGENTS.md"
    if not agents.exists():
        errors.append("AGENTS.md missing")
    else:
        text = agents.read_text(encoding="utf-8")
        if ENTRY_SKILL not in text:
            errors.append(f"AGENTS.md does not reference {ENTRY_SKILL}")
        if not find_agents_block(text):
            warnings.append("AGENTS.md has no PSP managed block markers")
    manifest_path = target / "skills" / "MANIFEST.json"
    if not manifest_path.exists():
        errors.append("skills/MANIFEST.json missing")
    else:
        try:
            manifest = read_json(manifest_path)
            entry = manifest.get("entry_skill", ENTRY_SKILL)
            if not (target / entry).exists():
                errors.append(f"entry skill missing: {entry}")
            for skill in manifest.get("skills", []):
                p = skill.get("path")
                if p and not (target / p).exists():
                    errors.append(f"skill missing: {p}")
                elif p:
                    txt=(target/p).read_text(encoding="utf-8")[:2048]
                    if "description:" not in txt:
                        warnings.append(f"skill missing native-compatible description: {p}")
            for p in sorted(set(referenced_paths(manifest))):
                if not (target / p).exists():
                    errors.append(f"manifest references missing path: {p}")
        except Exception as e:
            errors.append(f"could not parse skills/MANIFEST.json: {e}")
    state = load_state(target)
    if not state:
        warnings.append(".psp/install.json missing; installation is not hash-managed")
    else:
        for r, meta in state.get("managed_files", {}).items():
            p = target / r
            if not p.exists():
                errors.append(f"managed file missing: {r}")
                continue
            expected = meta.get("sha256")
            if expected and sha256_file(p) != expected:
                msg = f"managed file modified: {r}"
                (errors if strict else warnings).append(msg)
        tool_path = state.get("tool", {}).get("path")
        if tool_path and not (target / tool_path).exists():
            warnings.append(f"installed verifier missing: {tool_path}")
        installed_hosts=set(state.get("host_adapters",{}).get("installed",[]))
        if "agents" in installed_hosts and not (target / NATIVE_ENTRY_DEST_AGENTS).exists():
            errors.append(f"agents native entry missing: {NATIVE_ENTRY_DEST_AGENTS}")
        if "claude" in installed_hosts:
            if not (target / "CLAUDE.md").exists():
                errors.append("CLAUDE.md missing for claude adapter")
            if not (target / NATIVE_ENTRY_DEST_CLAUDE).exists():
                errors.append(f"claude native entry missing: {NATIVE_ENTRY_DEST_CLAUDE}")
        if "gemini" in installed_hosts and not (target / "GEMINI.md").exists():
            errors.append("GEMINI.md missing for gemini adapter")
        if "copilot" in installed_hosts and not (target / ".github" / "copilot-instructions.md").exists():
            errors.append(".github/copilot-instructions.md missing for copilot adapter")
        if "opencode" in installed_hosts and not (target / ".opencode" / "commands" / "psp.md").exists():
            errors.append(".opencode/commands/psp.md missing for opencode adapter")
        if "cursor" in installed_hosts and not (target / ".cursor" / "rules" / "pragmatic-skills-pack.mdc").exists():
            errors.append(".cursor/rules/pragmatic-skills-pack.mdc missing for cursor adapter")
    return (1 if errors else 0), errors, warnings


def cmd_verify_package(args: argparse.Namespace) -> int:
    root = package_root()
    errors = validate_package(root)
    if errors:
        print(f"Package check failed: {root}")
        for e in errors:
            print(f"- {e}")
        return 1
    m = load_manifest(root)
    adapters = read_json(root / "adapters" / "HOSTS.json") if (root / "adapters" / "HOSTS.json").exists() else {}
    print(f"Package OK: {m.get('name')} {m.get('version')}")
    print(f"Root: {root}")
    print(f"Managed core files: {len(iter_core_payload_files(root))}")
    print(f"Entry skill: {m.get('entry_skill')}")
    print(f"Host adapters: {', '.join(sorted(adapters.get('hosts', {}).keys()))}")
    print("Installer: install.sh")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    code, errors, warnings = verify_target(target, strict=args.strict)
    state = load_state(target)
    version = state.get("package", {}).get("version", "unmanaged") if state else "unmanaged"
    hosts = ", ".join(state.get("host_adapters", {}).get("installed", [])) if state else "unknown"
    print(f"PSP target check: {target}")
    print(f"Installed version: {version}")
    print(f"Host adapters: {hosts}")
    if errors:
        print("Errors:")
        for e in errors:
            print(f"- {e}")
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"- {w}")
    if not errors and not warnings:
        print("OK: installation is complete and managed files are unchanged.")
    elif not errors:
        print("OK with warnings.")
    return code


def cmd_status(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    state = load_state(target)
    if not state:
        print(f"No PSP install state found in {target}")
        return cmd_verify(args)
    pkg = state.get("package", {})
    print(f"Target: {target}")
    print(f"Package: {pkg.get('name', 'Pragmatic Skills Pack')} {pkg.get('version', 'unknown')}")
    print(f"Entry skill: {pkg.get('entry_skill', ENTRY_SKILL)}")
    print(f"Host adapters: {', '.join(state.get('host_adapters', {}).get('installed', []))}")
    print(f"Installed at: {state.get('installed_at')}")
    print(f"Updated at: {state.get('updated_at')}")
    print(f"Managed files: {len(state.get('managed_files', {}))}")
    return cmd_verify(args)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Install, verify, and upgrade Pragmatic Skills Pack. Shell-first entrypoint: install.sh.")
    sub = p.add_subparsers(dest="command", required=True)

    def target_flags(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--target", "-t", default=".", help="Target repository root. Default: current directory.")

    def install_flags(sp: argparse.ArgumentParser) -> None:
        target_flags(sp)
        sp.add_argument("--hosts", default="all", help="Host adapters: all, auto, minimal, none, or comma-separated: agents,codex,claude,opencode,hermes,gemini,copilot,cursor. Default: all.")
        sp.add_argument("--no-host-adapters", action="store_true", help="Install only AGENTS.md plus canonical skills/reference; do not create host adapter files.")
        sp.add_argument("--all-hosts", action="store_true", help="Install all supported host adapters.")
        sp.add_argument("--force", action="store_true", help="Overwrite conflicts after backing them up.")
        sp.add_argument("--dry-run", action="store_true", help="Show planned actions without writing files.")
        sp.add_argument("--profile", action="store_true", help="Create .psp/project-profile.md from the template if absent.")
        sp.add_argument("--allow-downgrade", action="store_true", help="Allow installing a lower version over a higher one.")

    install = sub.add_parser("install", help="Install PSP into a repository; upgrades if already installed.")
    install_flags(install)
    install.set_defaults(func=lambda a: do_install(a, require_existing=False))

    upgrade = sub.add_parser("upgrade", help="Upgrade an existing PSP installation from this package.")
    install_flags(upgrade)
    upgrade.set_defaults(func=lambda a: do_install(a, require_existing=True))

    verify = sub.add_parser("verify", help="Verify an installed repository.")
    target_flags(verify)
    verify.add_argument("--strict", action="store_true", help="Treat modified managed files as errors.")
    verify.set_defaults(func=cmd_verify)

    status = sub.add_parser("status", help="Show installation status and verification summary.")
    target_flags(status)
    status.add_argument("--strict", action="store_true", help=argparse.SUPPRESS)
    status.set_defaults(func=cmd_status)

    vp = sub.add_parser("verify-package", help="Verify this unpacked package before installing.")
    vp.set_defaults(func=cmd_verify_package)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
