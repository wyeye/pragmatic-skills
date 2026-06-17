# Skill Metadata Schema

Every `skills/*/SKILL.md` file starts with YAML frontmatter.

The schema is intentionally small. It is a routing aid, not a replacement for the skill body.

## Required fields

```yaml
schema: psp.skill/v1
name: <skill-name>
kind: <entry | router | mode | support>
version: <semver-like version>
activation:
  automatic: true
  entrypoint: <true | false>
  user_direct: false
  invoked_by:
    - <AGENTS.md#start-rule | skills/...#loads... | workflow#re-triage-triggers>
  routing_note: <short note>
summary: <one-line purpose>
triggers:
  - <activation condition>
loads: {}
outputs:
  - <expected output>
```

## Optional fields

```yaml
safety:
  approval_required: <text>
  approval_required_for:
    - <gated action>
  requires_approval_before:
    - <gated action>
```

## `kind` values

- `entry`: the first skill loaded by `AGENTS.md`.
- `router`: selects a primary mode.
- `mode`: owns the main workflow for a task class.
- `support`: loaded by phase or condition to provide a specific capability.

## `loads` shape

Common keys:

```yaml
loads:
  immediate:
    - skills/example/SKILL.md
  select_one:
    - skills/fast-patch/SKILL.md
    - skills/standard-change/SKILL.md
  conditional:
    condition_name:
      - skills/example/SKILL.md
  phased:
    phase_name:
      - skills/example/SKILL.md
  escalation:
    - skills/strict-change/SKILL.md
```

## Interpretation rules

- Metadata helps route and index skills.
- The skill body is authoritative for procedure once the skill is activated.
- If metadata and body disagree, follow the safer path and treat the inconsistency as a workflow bug to fix.
- Do not preload every skill body just to read metadata. Prefer `skills/MANIFEST.json` or partial frontmatter reads when available.


## `activation` shape

`activation` makes the user contract machine-readable.

```yaml
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
    - skills/standard-change/SKILL.md#loads.phased.verification
  routing_note: Users provide tasks; agents route from AGENTS.md through triage and phase triggers. Users do not manually invoke individual skills.
```

Interpretation:

- `automatic: true`: the agent/runtime loads the skill when routing conditions match.
- `entrypoint: true`: this is the only skill started directly from `AGENTS.md`.
- `user_direct: false`: users should not be asked to call this skill by name.
- `invoked_by`: machine-readable upstream trigger hints.

Only `skills/using-pragmatic-skills/SKILL.md` should have `entrypoint: true`.

## Manifest tooling fields

"
"`skills/MANIFEST.json` may include package-level installation metadata. The public installer should be shell-first; lower-level tools can be listed as implementation details:

"
"```json
"
"{
"
"  "installer": {
"
"    "path": "install.sh",
"
"    "kind": "shell-wrapper",
"
"    "implementation": "tools/psp.py",
"
"    "commands": ["install", "upgrade", "verify", "status", "verify-package"],
"
"    "one_command": "sh /path/to/pragmatic-skills-pack/install.sh --target <repo>",
"
"    "state_file": ".psp/install.json",
"
"    "installed_tool_path": ".psp/bin/psp.py",
"
"    "backup_dir": ".psp/backups",
"
"    "conflict_dir": ".psp/conflicts"
"
"  },
"
"  "tooling": {
"
"    "public_installer": "install.sh",
"
"    "implementation": "tools/psp.py",
"
"    "commands": {
"
"      "install_or_upgrade": "sh install.sh --target <repo>",
"
"      "upgrade_existing": "sh install.sh upgrade --target <repo>",
"
"      "verify": "sh install.sh --verify --target <repo>",
"
"      "status": "sh install.sh --status --target <repo>",
"
"      "verify_package": "sh install.sh --check"
"
"    },
"
"    "agent_install_guide": "AGENT-INSTALL.md"
"
"  }
"
"}
"
"```

"
"This metadata is package-level, not skill-level. It helps installers, runtimes, and release tooling find the correct local management command without hardcoding paths outside the manifest.

## Package installer metadata

The package manifest should expose the public shell-first installer separately from the implementation tool:

```json
{
  "installer": {
    "path": "install.sh",
    "kind": "shell-wrapper",
    "implementation": "tools/psp.py",
    "one_command": "sh /path/to/pragmatic-skills-pack/install.sh --target <repo>",
    "state_file": ".psp/install.json",
    "installed_tool_path": ".psp/bin/psp.py"
  },
  "tooling": {
    "public_installer": "install.sh",
    "implementation": "tools/psp.py",
    "agent_install_guide": "AGENT-INSTALL.md"
  }
}
```

Users should not need to call `tools/psp.py` directly. Agents should prefer `install.sh` and only use the Python implementation as a fallback or for installed verification.
