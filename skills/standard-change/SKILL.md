---
schema: psp.skill/v1
name: standard-change
description: Normal engineering work with requirements, planning, tests, evidence, verification, and review loaded by phase.
kind: mode
version: 1.8.0
summary: Normal engineering work with requirements, planning, tests, evidence, verification, and review loaded by phase.
triggers:
- Behavior changes.
- Bug fixes.
- Moderate refactors.
- Multi-file edits without Strict triggers.
loads:
  phased:
    discovery:
    - skills/exploration/SKILL.md
    command:
    - skills/command-discovery/SKILL.md
    project_instructions:
    - skills/project-agents-md/SKILL.md
    requirements:
    - skills/requirements-and-design/SKILL.md
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
- requirement/design baseline when needed
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
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Standard Change

## Phase-trigger contract

Do not load all support skills when entering this mode.

Load support skills only when their phase trigger is reached. The user should not be asked to invoke support skills manually.

Use this skill for normal engineering work: real behavior changes, bug fixes, moderate refactors, and multi-file edits.

Standard Change should stay progressive. Do not load every support skill at mode entry.

## Progressive support loading

Load support skills by phase:

- Discovery phase: inspect relevant code/tests. Load `skills/exploration/SKILL.md` when project facts, current behavior, root cause, or feasibility are unclear.
- Command phase: load `skills/command-discovery/SKILL.md` only when install/test/lint/typecheck/build/run commands are needed and not already known from explicit project instructions.
- Project-instructions phase: load `skills/project-agents-md/SKILL.md` when the target is `AGENTS.md` or repository agent instruction files.
- Requirements phase: load `skills/requirements-and-design/SKILL.md` when the user asks to brainstorm/confirm requirements, a feature lacks scope or acceptance criteria, multiple designs materially differ, or planning would rely on risky assumptions.
- Planning phase: load `skills/writing-plans/SKILL.md` when more than one step/file is involved, order matters, tests must change, or reviewability matters.
- Behavior phase: load `skills/tdd/SKILL.md` for behavior changes and bug fixes.
- Execution phase: load `skills/evidence-driven-execution/SKILL.md` before non-trivial edits, delegated work, or any claim that will need audit evidence.
- Verification phase: load `skills/verification/SKILL.md` before running checks or reporting validation.
- Review phase: load `skills/review/SKILL.md` before calling the work complete when behavior changed, tests changed, multiple files changed, or the diff is not tiny.
- Completion phase: load `skills/handoff/SKILL.md` before the final response.

Do not load requirements-and-design for a tiny, fully specified, low-risk change merely to create a formality.

## Workflow

1. Understand current behavior, relevant code, tests, and constraints.
2. Resolve project commands only when needed.
3. If requirements/design is triggered, produce a Requirement Brief and establish its confirmation state.
4. If the state is `blocked on user decision`, stop before implementation planning or editing.
5. Plan if the change is not trivial, using the confirmed brief as input.
6. For behavior changes, write/update the failing test first when practical and map tests to acceptance criteria.
7. Implement the smallest change that satisfies the accepted requirement.
8. Refactor only after verification passes.
9. Run targeted checks; broaden checks when blast radius justifies it.
10. Review the actual diff against intended scope and acceptance criteria.
11. Report evidence, unverified criteria, assumptions, and gaps.

## Requirement change control

Do not silently change a confirmed scope, non-goal, acceptance criterion, or recommended design during implementation.

If new evidence invalidates the brief:

1. State the new evidence.
2. Update the Requirement Brief.
3. Re-establish its confirmation state.
4. Re-triage if risk or scope changed.

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
