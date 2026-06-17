# Skill Metadata Schema

Every `skills/*/SKILL.md` file starts with YAML frontmatter.

The schema is intentionally small. It is a routing aid, not a replacement for the skill body.

## Required fields

```yaml
schema: psp.skill/v1
name: <skill-name>
kind: <entry | router | mode | support>
version: <semver-like version>
summary: <one-line purpose>
triggers:
  - <activation condition>
loads: {}
outputs:
  - <expected output>
routing:
  user_exposed: false
  user_invocation_required: false
  activation: <entrypoint | automatic-router | router-selected-mode | phase-triggered-support | condition-triggered-support>
  invoked_by:
    - <entry file, router, mode, phase, or condition>
  contract: <short routing contract>
activation:
  automatic: true
  entrypoint: <true for the entry skill only>
  user_direct: false
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

- Users do not directly invoke non-entry skills.
- Metadata helps route and index skills.
- The skill body is authoritative for procedure once the skill is activated.
- If metadata and body disagree, follow the safer path and treat the inconsistency as a workflow bug to fix.
- Do not preload every skill body just to read metadata. Prefer `skills/MANIFEST.json` or partial frontmatter reads when available.
