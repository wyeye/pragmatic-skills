#!/usr/bin/env python3
"""Create a deterministic release ZIP for Pragmatic Skills Pack."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from psp_installer import verify_package  # noqa: E402
from psp_util import PACKAGE_VERSION, ValidationError  # noqa: E402

EXCLUDED_DIRS = {
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
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}
FIXED_TIMESTAMP = (2026, 6, 18, 0, 0, 0)


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def iter_release_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(name for name in dirs if name not in EXCLUDED_DIRS)
        for name in sorted(files):
            path = Path(current) / name
            if path.is_symlink():
                raise ValidationError(f"Release package may not contain symlinks: {path.relative_to(root)}")
            if path.suffix.lower() in EXCLUDED_SUFFIXES:
                continue
            yield path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_zip(root: Path, output: Path, archive_root: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in iter_release_files(root):
                rel = path.relative_to(root).as_posix()
                info = zipfile.ZipInfo(f"{archive_root}/{rel}", date_time=FIXED_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                mode = path.stat().st_mode & 0o777
                info.external_attr = (mode or 0o644) << 16
                info.flag_bits |= 0x800
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        os.replace(temp, output)
    finally:
        temp.unlink(missing_ok=True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=package_root())
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument("--name", default=f"pragmatic-skills-pack-{PACKAGE_VERSION}-enhanced.zip")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    result = verify_package(root)
    if not result["ok"]:
        for issue in result["issues"]:
            print(f"package error [{issue.get('code')}]: {issue.get('message')}", file=sys.stderr)
        return 2

    output_dir = args.output_dir.resolve()
    output = output_dir / args.name
    archive_root = args.name[:-4] if args.name.lower().endswith(".zip") else args.name
    build_zip(root, output, archive_root)
    digest = sha256(output)
    checksum = output.with_suffix(output.suffix + ".sha256")
    checksum.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    print(output)
    print(checksum)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
