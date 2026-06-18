---
schema: psp.skill/v1
name: writing-plans
description: Create executable, verifiable plans from confirmed requirements for non-trivial implementation.
kind: support
version: 1.8.0
summary: Create executable, verifiable plans from confirmed requirements for non-trivial implementation.
triggers:
- More than one file or step.
- Tests must change.
- Order matters.
- Meaningful risk or reviewability concerns.
loads:
  conditional:
    requirements_unresolved:
    - skills/requirements-and-design/SKILL.md
    commands_needed_for_verify_steps:
    - skills/command-discovery/SKILL.md
    safety_gated_action:
    - skills/safety-gates/SKILL.md
outputs:
- requirement/design basis
- goal and assumptions
- steps with file/area/change/verify/expected result
- risks/rollback
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/standard-change/SKILL.md#loads.phased.planning
  - skills/strict-change/SKILL.md#loads.phased.planning
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Writing Plans

## Internal activation

This is a support skill. It is loaded by a mode, router, or another support skill when the relevant phase or condition is reached.

Users do not need to ask for this skill directly.

Use this skill before non-trivial implementation.

A plan should be executable and verifiable, not a design essay.

## Input contract

When `requirements-and-design` was activated, the latest Requirement Brief is the plan's baseline.

Before planning:

- Confirm the state is `confirmed`, `conditionally confirmed`, or `safe assumptions used`.
- Do not plan implementation while the state is `blocked on user decision`.
- Preserve accepted scope, non-goals, constraints, design decisions, and acceptance criteria.
- If those inputs are missing or unresolved and materially affect implementation, load `skills/requirements-and-design/SKILL.md` first.
- Do not silently reopen confirmed decisions without new evidence.

When the task is already fully specified by an authoritative project spec or tests, cite that as the requirement basis instead of creating unnecessary ceremony.

## When to use

Use when:

- More than one file or step is involved.
- Tests must be added or updated.
- Order matters.
- There is meaningful risk.
- Reviewability matters.

## Plan format

```text
Requirement/design basis:
- <Requirement Brief, authoritative spec, test, or explicit user instruction>
- Confirmation state: <confirmed | conditionally confirmed | safe assumptions used | not applicable>

Goal:
...

Assumptions:
- ...

Acceptance criteria covered:
- AC1 -> steps/tests ...
- AC2 -> steps/tests ...

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
- Relevant acceptance criterion when one exists.

If a step names a command, the command must come from explicit project instructions, command discovery, or a stated conventional fallback.

Avoid vague steps like:

- “Update logic.”
- “Add tests.”
- “Handle edge cases.”
- “Refactor as needed.”

## Requirement drift

If planning reveals that the accepted design is infeasible, unsafe, or materially more expensive than expected:

1. Stop planning.
2. Record the new evidence.
3. Return to `requirements-and-design`.
4. Re-establish confirmation before continuing.

## Plan size

Prefer 3–7 steps. If larger than 10 steps, split into phases.

## Approval

Ask for approval only when:

- The Requirement Brief is blocked on a material user decision.
- The plan includes a safety-gated action.
- The user explicitly asked to review the plan first.

Do not ask for ceremonial approval of routine low-risk plans.
