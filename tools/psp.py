#!/usr/bin/env python3
"""Pragmatic Skills Pack command-line interface."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from psp_eval import framework_self_test, grade_results, load_cases  # noqa: E402
from psp_installer import (  # noqa: E402
    diff_install,
    doctor,
    install,
    list_backups,
    rollback,
    status,
    uninstall,
    verify_install,
    verify_package,
    write_manifest,
)
from psp_trace import emit_event, finish_run, list_runs, start_run, verify_run  # noqa: E402
from psp_util import ConflictError, LockError, PACKAGE_VERSION, PSPError, ValidationError, read_json, sha256_file  # noqa: E402


_RUNTIME_TEMP: Optional[tempfile.TemporaryDirectory[str]] = None
_RUNTIME_ZIP: Optional[Path] = None


def _is_package_root(candidate: Path) -> bool:
    return (
        (candidate / "skills/MANIFEST.json").is_file()
        and (candidate / "adapters/HOSTS.json").is_file()
        and (candidate / "tools/psp.py").is_file()
    )


def _extract_embedded_package(archive_path: Path) -> Optional[Path]:
    global _RUNTIME_TEMP, _RUNTIME_ZIP
    archive_path = archive_path.resolve()
    if not archive_path.is_file():
        return None
    state_path = archive_path.parent / "install.json"
    if state_path.is_file():
        state = read_json(state_path)
        entry = state.get("managed_files", {}).get(".psp/package.zip", {}) if isinstance(state, dict) else {}
        expected = entry.get("sha256") if isinstance(entry, dict) else None
        if not expected or sha256_file(archive_path) != expected:
            raise ValidationError("Embedded PSP package failed installed-state integrity verification")
    if _RUNTIME_TEMP is not None and _RUNTIME_ZIP == archive_path:
        cached = Path(_RUNTIME_TEMP.name)
        if _is_package_root(cached):
            return cached
    holder = tempfile.TemporaryDirectory(prefix="psp-runtime-")
    destination = Path(holder.name)
    try:
        with zipfile.ZipFile(archive_path) as bundle:
            members = bundle.infolist()
            if len(members) > 5000:
                raise ValidationError("Embedded PSP package contains too many entries")
            if sum(member.file_size for member in members) > 50 * 1024 * 1024:
                raise ValidationError("Embedded PSP package exceeds the 50 MiB extraction limit")
            seen: set[str] = set()
            for member in members:
                if member.filename in seen:
                    raise ValidationError(f"Duplicate path in embedded PSP package: {member.filename}")
                seen.add(member.filename)
                relative = Path(member.filename)
                if relative.is_absolute() or ".." in relative.parts or not member.filename:
                    raise ValidationError(f"Unsafe path in embedded PSP package: {member.filename}")
                file_type = (member.external_attr >> 16) & 0o170000
                if file_type == 0o120000:
                    raise ValidationError(f"Symlink is not allowed in embedded PSP package: {member.filename}")
                output = destination.joinpath(*relative.parts)
                if member.is_dir():
                    output.mkdir(parents=True, exist_ok=True)
                    continue
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(bundle.read(member))
                mode = (member.external_attr >> 16) & 0o777
                if mode:
                    os.chmod(output, mode)
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile, ValidationError):
        holder.cleanup()
        raise
    if not _is_package_root(destination):
        holder.cleanup()
        raise ValidationError(f"Embedded PSP package is incomplete: {archive_path}")
    _RUNTIME_TEMP = holder
    _RUNTIME_ZIP = archive_path
    return destination


def package_root(explicit: Optional[str] = None) -> Path:
    """Locate a source bundle without depending on the current directory."""

    candidates: List[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    if os.environ.get("PSP_PACKAGE_ROOT"):
        candidates.append(Path(os.environ["PSP_PACKAGE_ROOT"]).expanduser())
    candidates.append(HERE.parent)
    cwd = Path.cwd()
    candidates.extend((cwd, cwd / ".psp/package"))
    for candidate in candidates:
        resolved = candidate.resolve()
        if _is_package_root(resolved):
            return resolved

    embedded_candidates = [HERE.parent / "package.zip", cwd / ".psp/package.zip"]
    for archive in embedded_candidates:
        extracted = _extract_embedded_package(archive)
        if extracted is not None:
            return extracted
    if explicit:
        raise ValidationError(f"Not a valid unpacked PSP bundle: {Path(explicit).expanduser()}")
    return HERE.parent


def add_target(parser: argparse.ArgumentParser, default: str = ".") -> None:
    parser.add_argument("--target", "-t", default=default, help="Target repository or package root")


def add_package_target(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target", "-t", default=None, help="Unpacked PSP package root; defaults to the embedded/current bundle")


def add_json(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print machine-readable JSON")


def add_install_flags(parser: argparse.ArgumentParser) -> None:
    add_target(parser)
    parser.add_argument("--hosts", default=None, help="auto (default), all, minimal, none, or comma-separated hosts")
    parser.add_argument("--all-hosts", action="store_true", help="Alias for --hosts all")
    parser.add_argument("--no-host-adapters", action="store_true", help="Alias for --hosts none")
    parser.add_argument("--profile", action="store_true", help="Install .psp/project-profile.md when absent")
    parser.add_argument("--force", action="store_true", help="Overwrite modified managed files after backup")
    parser.add_argument("--dry-run", action="store_true", help="Plan without writing")
    parser.add_argument("--allow-downgrade", action="store_true")
    parser.add_argument("--package-root", help="Unpacked PSP bundle to install from; defaults to the embedded/current bundle")
    add_json(parser)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="psp", description="Pragmatic Skills Pack")
    parser.add_argument("--version", action="version", version=PACKAGE_VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    install_parser = sub.add_parser("install", help="Install or safely upgrade PSP")
    add_install_flags(install_parser)

    upgrade_parser = sub.add_parser("upgrade", help="Require an existing install, then upgrade")
    add_install_flags(upgrade_parser)

    verify_parser = sub.add_parser("verify", help="Verify an installed repository")
    add_target(verify_parser)
    add_json(verify_parser)

    status_parser = sub.add_parser("status", help="Show installation status and drift")
    add_target(status_parser)
    add_json(status_parser)

    package_parser = sub.add_parser("verify-package", help="Verify an unpacked PSP package")
    add_package_target(package_parser)
    add_json(package_parser)

    diff_parser = sub.add_parser("diff", help="Show package-to-target changes without writing")
    add_target(diff_parser)
    diff_parser.add_argument("--hosts", default=None)
    diff_parser.add_argument("--profile", action="store_true")
    diff_parser.add_argument("--package-root", help="Unpacked PSP bundle to compare against")
    add_json(diff_parser)

    doctor_parser = sub.add_parser("doctor", help="Diagnose state, markers, paths, and package integrity")
    add_target(doctor_parser)
    doctor_parser.add_argument("--repair", action="store_true", help="Apply only explicitly safe repairs")
    doctor_parser.add_argument("--package-root", help="Unpacked PSP bundle to validate; defaults to the embedded/current bundle")
    add_json(doctor_parser)

    uninstall_parser = sub.add_parser("uninstall", help="Remove PSP-managed content and preserve user content")
    add_target(uninstall_parser)
    uninstall_parser.add_argument("--force", action="store_true")
    uninstall_parser.add_argument("--dry-run", action="store_true")
    add_json(uninstall_parser)

    rollback_parser = sub.add_parser("rollback", help="Restore a PSP transaction backup")
    add_target(rollback_parser)
    rollback_parser.add_argument("--to", dest="backup_id", help="Backup id; defaults to latest")
    rollback_parser.add_argument("--list", action="store_true", dest="list_only")
    rollback_parser.add_argument("--dry-run", action="store_true")
    rollback_parser.add_argument("--force", action="store_true", help="Remove a stale operation lock")
    add_json(rollback_parser)

    manifest_parser = sub.add_parser("manifest", help="Generate or check Skill manifest and sidecars")
    add_package_target(manifest_parser)
    manifest_parser.add_argument("--write", action="store_true", help="Write generated files")
    add_json(manifest_parser)

    trace_parser = sub.add_parser("trace", help="Manage optional local execution traces")
    trace_sub = trace_parser.add_subparsers(dest="trace_command", required=True)
    trace_start = trace_sub.add_parser("start")
    add_target(trace_start)
    trace_start.add_argument("--run-id")
    trace_start.add_argument("--metadata", default="{}", help="JSON object")
    add_json(trace_start)
    trace_emit = trace_sub.add_parser("emit")
    add_target(trace_emit)
    trace_emit.add_argument("event")
    trace_emit.add_argument("--run-id")
    trace_emit.add_argument("--event-id")
    trace_emit.add_argument("--data", default="{}", help="JSON object")
    add_json(trace_emit)
    trace_finish = trace_sub.add_parser("finish")
    add_target(trace_finish)
    trace_finish.add_argument("--run-id")
    trace_finish.add_argument("--status", default="completed")
    trace_finish.add_argument("--data", default="{}")
    add_json(trace_finish)
    trace_verify = trace_sub.add_parser("verify")
    add_target(trace_verify)
    trace_verify.add_argument("--run-id")
    add_json(trace_verify)
    trace_list = trace_sub.add_parser("list")
    add_target(trace_list)
    add_json(trace_list)

    eval_parser = sub.add_parser("eval", help="Validate cases or grade captured runs")
    eval_sub = eval_parser.add_subparsers(dest="eval_command", required=True)
    eval_validate = eval_sub.add_parser("validate")
    add_package_target(eval_validate)
    add_json(eval_validate)
    eval_self = eval_sub.add_parser("self-test")
    add_package_target(eval_self)
    add_json(eval_self)
    eval_grade = eval_sub.add_parser("grade")
    add_package_target(eval_grade)
    eval_grade.add_argument("--results", required=True)
    eval_grade.add_argument("--output")
    add_json(eval_grade)
    return parser


def parse_json_object(raw: str, label: str) -> Dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{label} must be valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return value


def human_print(command: str, result: Mapping[str, Any]) -> None:
    if command in {"install", "upgrade", "uninstall", "rollback", "diff"}:
        print(f"PSP {command}: {'OK' if result.get('ok') else 'NEEDS ATTENTION'}")
        if "version" in result:
            print(f"Version: {result['version']}")
        if result.get("hosts") is not None:
            print("Hosts: " + (", ".join(result.get("hosts", [])) or "none"))
        if "change_count" in result:
            print(f"Changes: {result.get('change_count', 0)}")
        if "conflict_count" in result:
            print(f"Conflicts: {result.get('conflict_count', 0)}")
        if result.get("backup"):
            print(f"Backup: {result['backup']}")
        if result.get("conflict_path"):
            print(f"Conflict candidates: {result['conflict_path']}")
        for item in result.get("statuses", []):
            print(f"- {item.get('status')}: {item.get('path')}")
        return
    if command in {"verify", "verify-package", "doctor", "status"}:
        if command == "status" and not result.get("installed"):
            print("PSP is not installed.")
            return
        print(f"PSP {command}: {'OK' if result.get('ok') else 'FAILED'}")
        if result.get("version"):
            print(f"Version: {result['version']}")
        for issue in result.get("issues", []):
            print(f"- {issue.get('severity', 'info').upper()} [{issue.get('code', 'issue')}]: {issue.get('message')}")
        for repair in result.get("repairs", []):
            print(f"- REPAIRED: {repair}")
        return
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


def execute(args: argparse.Namespace) -> Dict[str, Any]:
    command = args.command
    if command in {"install", "upgrade"}:
        return install(
            package_root(args.package_root),
            Path(args.target),
            hosts_spec=("all" if args.all_hosts else "none" if args.no_host_adapters else args.hosts),
            profile=args.profile,
            force=args.force,
            dry_run=args.dry_run,
            require_existing=command == "upgrade",
            allow_downgrade=args.allow_downgrade,
        )
    if command == "verify":
        return verify_install(Path(args.target))
    if command == "status":
        return status(Path(args.target))
    if command == "verify-package":
        root = Path(args.target).resolve() if args.target else package_root()
        return verify_package(root)
    if command == "diff":
        return diff_install(package_root(args.package_root), Path(args.target), hosts_spec=args.hosts, profile=args.profile)
    if command == "doctor":
        return doctor(package_root(args.package_root), Path(args.target), repair=args.repair)
    if command == "uninstall":
        return uninstall(Path(args.target), force=args.force, dry_run=args.dry_run)
    if command == "rollback":
        if args.list_only:
            return {"ok": True, "backups": list_backups(Path(args.target))}
        return rollback(Path(args.target), backup_id=args.backup_id, dry_run=args.dry_run, force=args.force)
    if command == "manifest":
        root = Path(args.target).resolve() if args.target else package_root()
        if args.write:
            manifest = write_manifest(root)
            return {"ok": True, "written": True, "skill_count": len(manifest["skills"]), "manifest": "skills/MANIFEST.json"}
        result = verify_package(root)
        manifest_issues = [item for item in result["issues"] if item["code"].startswith("manifest") or item["code"].startswith("sidecar")]
        return {"ok": not manifest_issues, "written": False, "issues": manifest_issues}
    if command == "trace":
        target = Path(args.target).resolve()
        if args.trace_command == "start":
            return start_run(target, run_id=args.run_id, metadata=parse_json_object(args.metadata, "--metadata"))
        if args.trace_command == "emit":
            return emit_event(target, args.event, parse_json_object(args.data, "--data"), run_id=args.run_id, event_id=args.event_id)
        if args.trace_command == "finish":
            return finish_run(target, run_id=args.run_id, status=args.status, data=parse_json_object(args.data, "--data"))
        if args.trace_command == "verify":
            return verify_run(target, run_id=args.run_id)
        if args.trace_command == "list":
            return {"ok": True, "runs": list_runs(target)}
    if command == "eval":
        root = Path(args.target).resolve() if args.target else package_root()
        if args.eval_command == "validate":
            cases, errors = load_cases(root)
            return {"ok": not errors, "case_count": len(cases), "errors": errors}
        if args.eval_command == "self-test":
            return framework_self_test(root)
        if args.eval_command == "grade":
            output = Path(args.output).resolve() if args.output else None
            return grade_results(root, Path(args.results).resolve(), output)
    raise ValidationError(f"Unsupported command: {command}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = execute(args)
    except (ValidationError, LockError, ConflictError, PSPError, OSError) as exc:
        payload = {"ok": False, "error": str(exc), "type": exc.__class__.__name__}
        if getattr(args, "as_json", False):
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(f"PSP error: {exc}", file=sys.stderr)
        return 2
    if getattr(args, "as_json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        human_print(args.command, result)
    if not result.get("ok", True):
        if result.get("conflict_count", 0):
            return 3
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
