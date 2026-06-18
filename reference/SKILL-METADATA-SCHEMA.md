# Skill metadata

Each `SKILL.md` uses portable top-level fields: `name`, `description`, `license`, `compatibility`, and a small `metadata` map. PSP-specific structure lives in `psp.skill.json`.

Required sidecar fields:

- `schema`: `psp.skill/v2`
- `name`, `version`, and `kind`
- `entry`: boolean
- `activation.positive` and `activation.negative`
- `loads`: referenced skill names
- `outputs`: observable outputs

`tools/build_manifest.py` generates `skills/MANIFEST.json`. `psp verify-package` checks names, paths, graph reachability, required modes, strict-mode safety routing, and handoff reachability.
