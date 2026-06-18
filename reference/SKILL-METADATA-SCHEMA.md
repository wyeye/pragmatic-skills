# Skill Metadata Schema

Every `skills/*/SKILL.md` file starts with YAML frontmatter.

The schema is intentionally small. It is a routing aid, not a replacement for the skill body.

## Required fields

```yaml
schema: psp.skill/v1
name: <skill-name>
description: <native-host-compatible one-line description>
kind: <entry | router | mode | support>
version: <semver-like version>
summary: <one-line purpose>
triggers:
  - <activation condition>
loads: {}
outputs:
  - <expected output>
activation:
  automatic: true
  entrypoint: <true | false>
  user_direct: false
  invoked_by:
    - <AGENTS.md#start-rule | skills/...#loads... | workflow#...>
  routing_note: <short note>
```

## Optional fields

```yaml
safety:
  approval_required: <text>
  approval_required_for:
    - <gated action>
  requires_approval_before:
    - <gated action>
activation:
  policy: <automatic | active-only | passive-capable>
  lifecycle: <any | pre-task | in-task | post-task>
  auto_after_completion: false
  active:
    - <explicit user/task trigger>
  passive:
    - <condition observed by the workflow>
  passive_requires_confirmation: true
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
  direct:
    explicit_intent:
      - skills/example/SKILL.md
  fallback:
    - skills/triage/SKILL.md
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
- The skill body is authoritative once the skill is activated.
- If metadata and body disagree, follow the safer path and treat the inconsistency as a workflow bug.
- Do not preload every skill body just to read metadata. Prefer `skills/MANIFEST.json` or partial frontmatter reads when available.

## Activation contract

```yaml
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
    - skills/standard-change/SKILL.md#loads.phased.verification
  policy: passive-capable
  lifecycle: any
  auto_after_completion: false
  active:
    - User explicitly asks for this capability.
  passive:
    - Workflow observes a condition that may benefit from this skill.
  passive_requires_confirmation: true
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers.
```

- `automatic: true`: the agent/runtime loads the skill when routing conditions match.
- `entrypoint: true`: this is the only skill started directly from `AGENTS.md`.
- `user_direct: false`: users should not be asked to call this skill by name.
- `policy`: activation policy. `active-only` means explicit user intent is required; it does not mean the user must know the skill name.
- `lifecycle`: where the capability belongs, such as `post-task` for a retrospective.
- `auto_after_completion: false`: completion alone must not trigger or offer the skill.
- `active`: explicit user/task triggers.
- `passive`: observed conditions that may trigger a prompt or internal routing.
- `passive_requires_confirmation: true`: the skill may be loaded automatically, but must ask before writing from a passive observation.

For an active-only capability, use:

```yaml
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  policy: active-only
  lifecycle: post-task
  auto_after_completion: false
  active:
    - User explicitly requests the capability in normal language.
  passive: []
```

Here `automatic: true` means the agent routes automatically after recognizing explicit intent. It does not authorize passive invocation.

Only `skills/using-pragmatic-skills/SKILL.md` should have `entrypoint: true`.

## Package installer metadata

The package manifest exposes the public shell-first installer separately from the implementation tool:

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

Current schema documentation version: `1.7.0`.
