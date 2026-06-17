---
schema: psp.skill/v1
name: standard-change
description: Normal engineering work with planning, tests, execution evidence, verification, and review by phase.
kind: mode
version: 1.5.0
summary: Normal engineering work with planning, tests, execution evidence, verification, and review by phase.
triggers:
- Behavior changes.
- Bug fixes.
- Moderate refactors.
- Multi-file edits without Strict triggers.
loads:
  phased:
    discovery:
    - skills/exploration/SKILL.md
    - skills/command-discovery/SKILL.md
    planning:
    - skills/writing-plans/SKILL.md
    behavior:
    - skills/tdd/SKILL.md
    execution:
    - skills/evidence-driven-execution/SKILL.md
    verification:
    - skills/verification/SKILL.md
    review:
    - skills/review/SKILL.md
    completion:
    - skills/handoff/SKILL.md
  escalation:
  - skills/strict-change/SKILL.md
outputs:
- planned change
- implementation evidence
- verification results
- review findings
- handoff summary
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/triage/SKILL.md#loads.select_one
  routing_note: Users provide tasks; agents route from AGENTS.md through triage and phase triggers. Users do not manually invoke individual skills.
---
# Standard Change

## Phase-trigger contract

Do not load all support skills when entering this mode.

Load support skills only when their phase trigger is reached. The user should not be asked to invoke support skills manually.

Use this skill for normal engineering work: real behavior changes, bug fixes, moderate refactors, and multi-file edits.

Standard Change should stay progressive. Do not load every support skill at mode entry.

## Progressive support loading

Load support skills by phase:

- Discovery phase: inspect the relevant code and tests. If requirements or approach are still unclear, load `skills/exploration/SKILL.md` and re-triage afterward.
- Command phase: when install/test/lint/typecheck/build/run commands are needed and not already known from explicit project instructions, load `skills/command-discovery/SKILL.md`.
- Planning phase: load `skills/writing-plans/SKILL.md` when more than one step or file is involved, order matters, tests must change, or reviewability matters.
- Behavior phase: load `skills/tdd/SKILL.md` for behavior changes and bug fixes.
- Execution phase: load `skills/evidence-driven-execution/SKILL.md` before non-trivial edits, delegated work, or any claim that will need audit evidence.
- Verification phase: load `skills/verification/SKILL.md` before running checks or reporting validation.
- Review phase: load `skills/review/SKILL.md` before calling the work complete when behavior changed, tests changed, multiple files changed, or the diff is not tiny.
- Completion phase: load `skills/handoff/SKILL.md` before the final response.

## Workflow

1. Understand the relevant code and tests.
2. Resolve project commands only when needed.
3. Plan if the change is not trivial.
4. For behavior changes, write or update the failing test first when practical.
5. Implement the smallest change that satisfies the test or requirement.
6. Refactor only after verification passes.
7. Run targeted checks; broaden checks when blast radius justifies it.
8. Review the actual diff or changed files for accidental changes.
9. Report evidence and gaps.

## Scope control

Do not opportunistically rewrite unrelated code.

If you discover adjacent issues, mention them as follow-ups unless they block the current task.

## Escalate to Strict Change

Stop, re-triage, and load `skills/strict-change/SKILL.md` if the change touches:

- Auth, security, permissions, secrets, privacy.
- Payment, billing, quotas, subscriptions.
- Database schema, migrations, destructive data changes.
- Public API, SDK, backward compatibility.
- Deployment, infrastructure, CI/CD, production config.
- Runtime dependencies with behavior or security impact.
- Generated files, lockfiles, vendored code, or unclear ownership artifacts.
- Large or hard-to-review refactors.
