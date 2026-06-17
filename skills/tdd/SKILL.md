---
schema: psp.skill/v1
name: tdd
kind: support
version: 1.2.0
summary: Use tests as the driver for behavior changes and bug fixes when practical.
triggers:
- Behavior change.
- Bug fix.
- Regression risk.
- Executable tests are practical.
loads:
  conditional:
    test_command_unknown:
    - skills/command-discovery/SKILL.md
    verification:
    - skills/verification/SKILL.md
outputs:
- failing test evidence when practical
- passing test evidence after fix
- reason when TDD is not practical
routing:
  user_exposed: false
  user_invocation_required: false
  activation: phase-triggered-support
  invoked_by:
  - skills/standard-change/SKILL.md
  - skills/strict-change/SKILL.md
  contract: Loaded automatically for behavior changes, bug fixes, and regression risk.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
---

# Test-Driven Development
## Routing contract

This skill is an internal routing target. Users do not need to ask for this skill directly; the entry workflow, triage, mode, or phase trigger loads it when appropriate.



This support skill is loaded automatically for behavior changes, bug fixes, and regression risk when executable tests are practical. Users do not need to ask for TDD by name.

Use this skill for behavior changes and bug fixes when executable tests are practical.

TDD is a tool for confidence, not ceremony. It is strongly preferred for behavior changes, but exceptions must be explicit.

## Required for

Use TDD or the closest executable equivalent for:

- Bug fixes.
- Business logic changes.
- Public behavior changes.
- Data transformation changes.
- Auth, security, billing, permissions, or compatibility changes.

## Reasonable exceptions

You may skip strict red-green TDD for:

- Documentation-only changes.
- Formatting-only changes.
- Comments.
- Pure configuration where no executable check exists.
- Throwaway prototypes.
- Generated files.
- UI polish where the project has no practical test harness.

When skipping, state why and use the strongest available verification.

## Command discovery

If the test command is not already known from explicit project instructions, load `skills/command-discovery/SKILL.md` before running tests.

Do not invent a test command just to satisfy this skill.

## Bug fix flow

1. Reproduce the bug with a failing test or strongest available check.
2. Confirm the failure represents the bug.
3. Fix the bug.
4. Confirm the check passes.

## Test quality

Good tests:

- Assert observable behavior.
- Fail without the fix.
- Pass with the fix.
- Cover the regression or edge case.
- Avoid over-mocking.

## Evidence wording

Use precise wording:

- “Added regression test X; it failed before the fix and passed after.”
- “Could not run tests because ...”
- “Used static/manual verification because no test harness exists for this area.”
