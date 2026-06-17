---
schema: psp.skill/v1
name: writing-plans
description: Create executable, verifiable plans for non-trivial implementation.
kind: support
version: 1.5.0
summary: Create executable, verifiable plans for non-trivial implementation.
triggers:
- More than one file or step.
- Tests must change.
- Order matters.
- Meaningful risk or reviewability concerns.
loads:
  conditional:
    commands_needed_for_verify_steps:
    - skills/command-discovery/SKILL.md
    safety_gated_action:
    - skills/safety-gates/SKILL.md
outputs:
- goal
- assumptions
- steps with file/area/change/verify/expected result
- risks/rollback
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/standard-change/SKILL.md#loads.phased.planning
  - skills/strict-change/SKILL.md#loads.phased.planning
  routing_note: Users provide tasks; agents route from AGENTS.md through triage and phase triggers. Users do not manually invoke individual skills.
---
# Writing Plans

## Internal activation

This is a support skill. It is loaded by a mode, router, or another support skill when the relevant phase or condition is reached.

Users do not need to ask for this skill directly.

Use this skill before non-trivial implementation.

A plan should be executable and verifiable, not a design essay.

## When to use

Use when:

- More than one file or step is involved.
- Tests must be added or updated.
- Order matters.
- There is meaningful risk.
- Reviewability matters.

## Plan format

```text
Goal:
...

Assumptions:
- ...

Steps:
1. File/area: ...
   Change: ...
   Verify: ...
   Expected result: ...
2. ...

Risks / rollback:
- ...
```

## Requirements

Each step must identify:

- File or area.
- Concrete change.
- Verification method.
- Expected result.

If a step names a command, the command must come from explicit project instructions, command discovery, or a stated conventional fallback.

Avoid vague steps like:

- “Update logic.”
- “Add tests.”
- “Handle edge cases.”
- “Refactor as needed.”

## Plan size

Prefer 3–7 steps. If larger than 10 steps, split into phases.

## Approval

Ask for approval only when the plan includes a safety-gated action or the user explicitly asked to review the plan first.
