---
schema: psp.skill/v1
name: writing-plans
kind: support
version: 1.2.0
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
routing:
  user_exposed: false
  user_invocation_required: false
  activation: phase-triggered-support
  invoked_by:
  - skills/standard-change/SKILL.md
  - skills/strict-change/SKILL.md
  contract: Loaded automatically during planning when sequencing or reviewability matters.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
---

# Writing Plans
## Routing contract

This skill is an internal routing target. Users do not need to ask for this skill directly; the entry workflow, triage, mode, or phase trigger loads it when appropriate.



This support skill is loaded automatically during the planning phase when the work is non-trivial. Users do not need to ask for it by name.

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
