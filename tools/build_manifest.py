#!/usr/bin/env python3
"""Build or check skills/MANIFEST.json from source-controlled Skill sidecars."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from psp_util import build_skill_manifest, validate_skill_graph  # noqa: E402


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=package_root())
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        manifest = build_skill_manifest(root)
        issues = [item for item in validate_skill_graph(root, manifest) if item.get("severity") == "error"]
    except Exception as exc:
        print(f"manifest error: {exc}", file=sys.stderr)
        return 2
    if issues:
        for issue in issues:
            print(f"manifest error [{issue.get('code')}]: {issue.get('message')}", file=sys.stderr)
        return 2
    output = root / "skills" / "MANIFEST.json"
    rendered = json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            print("skills/MANIFEST.json is stale; run tools/build_manifest.py", file=sys.stderr)
            return 1
        print("skills/MANIFEST.json is current")
        return 0
    output.write_text(rendered, encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
