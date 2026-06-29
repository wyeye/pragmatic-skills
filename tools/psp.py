#!/usr/bin/env python3
"""Pragmatic Skills Pack command-line interface."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

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
from psp_util import ConflictError, LockError, PACKAGE_VERSION, PSPError, ValidationError  # noqa: E402

RUNTIME_STATE = "runtime.json"
RUNTIME_EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".psp",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}
RUNTIME_EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}


def _is_package_root(candidate: Path) -> bool:
    return (
        (candidate / "skills/MANIFEST.json").is_file()
        and (candidate / "adapters/HOSTS.json").is_file()
        and (candidate / "tools/psp.py").is_file()
    )


def package_root(explicit: Optional[str] = None) -> Path:
    """Locate the PSP source/runtime bundle without using project-local vendoring."""

    candidates: List[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    if os.environ.get("PSP_HOME"):
        candidates.append(Path(os.environ["PSP_HOME"]).expanduser())
    if os.environ.get("PSP_PACKAGE_ROOT"):
        candidates.append(Path(os.environ["PSP_PACKAGE_ROOT"]).expanduser())
    candidates.append(HERE.parent)
    for candidate in candidates:
        resolved = candidate.resolve()
        if _is_package_root(resolved):
            return resolved

    if explicit:
        raise ValidationError(f"Not a valid unpacked PSP bundle: {Path(explicit).expanduser()}")
    return HERE.parent


def default_runtime_home() -> Path:
    if os.environ.get("PSP_HOME"):
        return Path(os.environ["PSP_HOME"]).expanduser()
    return Path.home() / ".local/share/pragmatic-skills-pack/current"


def iter_runtime_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(name for name in dirs if name not in RUNTIME_EXCLUDED_DIRS)
        for name in sorted(files):
            path = Path(current) / name
            rel = path.relative_to(root)
            if path.is_symlink():
                raise ValidationError(f"Runtime package may not contain symlinks: {rel.as_posix()}")
            if path.suffix.lower() in RUNTIME_EXCLUDED_SUFFIXES:
                continue
            yield path


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path, ignore_errors=True)
        return
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _move_path(source: Path, destination: Path) -> None:
    _remove_path(destination)
    source.rename(destination)


def runtime_status(home: Path) -> Dict[str, Any]:
    home = home.expanduser().resolve()
    if home.exists() and not home.is_dir():
        return {
            "ok": False,
            "installed": False,
            "home": str(home),
            "version": None,
            "source": None,
            "updated_at": None,
            "issues": [{"severity": "error", "code": "runtime-incomplete", "message": "Runtime home exists but is not a directory"}],
        }
    state_path = home / RUNTIME_STATE
    installed = _is_package_root(home) and state_path.is_file()
    state: Dict[str, Any] = {}
    if state_path.is_file():
        try:
            loaded = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                state = loaded
        except (OSError, json.JSONDecodeError) as exc:
            return {"ok": False, "installed": False, "home": str(home), "issues": [{"severity": "error", "code": "runtime-state-invalid", "message": str(exc)}]}
    issues: List[Dict[str, str]] = []
    if home.exists() and not _is_package_root(home):
        issues.append({"severity": "error", "code": "runtime-incomplete", "message": "Runtime home is not a valid PSP bundle"})
    return {
        "ok": not any(item["severity"] == "error" for item in issues),
        "installed": installed,
        "home": str(home),
        "version": state.get("version") if state else None,
        "source": state.get("source") if state else None,
        "updated_at": state.get("updated_at") if state else None,
        "issues": issues,
    }


def install_runtime(source_root: Path, home: Path, *, dry_run: bool = False, force: bool = False) -> Dict[str, Any]:
    source_root = source_root.resolve()
    home = home.expanduser().resolve()
    package_check = verify_package(source_root)
    if not package_check["ok"]:
        messages = "; ".join(item["message"] for item in package_check["issues"] if item.get("severity") == "error")
        raise ValidationError(f"Package verification failed: {messages}")
    if home == source_root or source_root in home.parents:
        raise ValidationError("Runtime home must not be inside the source package")
    if home.exists() and not force and not _is_package_root(home):
        raise ValidationError(f"Runtime home exists but is not a PSP runtime; pass --force to replace it: {home}")

    files = list(iter_runtime_files(source_root))
    state = {
        "schema": "psp.runtime/v1",
        "version": PACKAGE_VERSION,
        "source": str(source_root),
        "file_count": len(files),
    }
    if dry_run:
        return {"ok": True, "dry_run": True, "home": str(home), "version": PACKAGE_VERSION, "file_count": len(files), "changed": True}

    parent = home.parent
    parent.mkdir(parents=True, exist_ok=True)
    staging = parent / f".{home.name}.staging-{os.getpid()}"
    backup = parent / f".{home.name}.previous-{os.getpid()}"
    _remove_path(staging)
    _remove_path(backup)
    try:
        for source in files:
            rel = source.relative_to(source_root)
            destination = staging / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        state["updated_at"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        (staging / RUNTIME_STATE).write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if home.exists():
            _move_path(home, backup)
        _move_path(staging, home)
        _remove_path(backup)
    except Exception:
        _remove_path(staging)
        if backup.exists() and not home.exists():
            _move_path(backup, home)
        raise
    return {"ok": True, "dry_run": False, "home": str(home), "version": PACKAGE_VERSION, "file_count": len(files), "changed": True}


def add_target(parser: argparse.ArgumentParser, default: str = ".") -> None:
    parser.add_argument("--target", "-t", default=default, help="Target repository or package root")


def add_package_target(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target", "-t", default=None, help="Unpacked PSP package root; defaults to the current runtime bundle")


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
    parser.add_argument("--package-root", help="Unpacked PSP bundle to install from; defaults to the current runtime bundle")
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
    doctor_parser.add_argument("--package-root", help="Unpacked PSP bundle to validate; defaults to the current runtime bundle")
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

    runtime_parser = sub.add_parser("runtime", help="Manage the user-level PSP runtime")
    runtime_sub = runtime_parser.add_subparsers(dest="runtime_command", required=True)
    runtime_install = runtime_sub.add_parser("install", help="Install this PSP bundle as a user-level runtime")
    runtime_install.add_argument("--home", type=Path, default=None, help="Runtime home; defaults to PSP_HOME or ~/.local/share/pragmatic-skills-pack/current")
    runtime_install.add_argument("--package-root", help="Unpacked PSP bundle to install; defaults to the current runtime bundle")
    runtime_install.add_argument("--force", action="store_true", help="Replace an existing non-PSP runtime home")
    runtime_install.add_argument("--dry-run", action="store_true")
    add_json(runtime_install)
    runtime_status_parser = runtime_sub.add_parser("status", help="Show user-level runtime status")
    runtime_status_parser.add_argument("--home", type=Path, default=None)
    add_json(runtime_status_parser)
    runtime_path = runtime_sub.add_parser("path", help="Print the default or selected runtime home")
    runtime_path.add_argument("--home", type=Path, default=None)
    add_json(runtime_path)

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
    if command == "runtime":
        print(f"PSP runtime: {'OK' if result.get('ok') else 'FAILED'}")
        print(f"Home: {result.get('home')}")
        if result.get("version"):
            print(f"Version: {result['version']}")
        if result.get("installed") is not None:
            print(f"Installed: {bool(result.get('installed'))}")
        if result.get("file_count") is not None:
            print(f"Files: {result.get('file_count')}")
        for issue in result.get("issues", []):
            print(f"- {issue.get('severity', 'info').upper()} [{issue.get('code', 'issue')}]: {issue.get('message')}")
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
    if command == "runtime":
        home = args.home if args.home is not None else default_runtime_home()
        if args.runtime_command == "install":
            return install_runtime(package_root(args.package_root), home, dry_run=args.dry_run, force=args.force)
        if args.runtime_command == "status":
            return runtime_status(home)
        if args.runtime_command == "path":
            return {"ok": True, "home": str(home.expanduser().resolve())}
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
