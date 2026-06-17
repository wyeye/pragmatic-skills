---
schema: psp.skill/v1
name: verification
description: Choose and run the right level of validation before claiming completion.
kind: support
version: 1.5.0
summary: Choose and run the right level of validation before claiming completion.
triggers:
- After implementation.
- Before reporting checks as passed or failed.
loads:
  conditional:
    command_unknown:
    - skills/command-discovery/SKILL.md
outputs:
- verification level
- commands log
- failures and gaps
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/delegation/SKILL.md#loads.conditional.integration_verification
  - skills/standard-change/SKILL.md#loads.phased.verification
  - skills/strict-change/SKILL.md#loads.phased.verification
  - skills/tdd/SKILL.md#loads.conditional.verification
  routing_note: Users provide tasks; agents route from AGENTS.md through triage and phase triggers. Users do not manually invoke individual skills.
---
# Verification

## Internal activation

This is a support skill. It is loaded by a mode, router, or another support skill when the relevant phase or condition is reached.

Users do not need to ask for this skill directly.

Use this skill after implementation and before claiming completion.

## Command resolution

Before choosing verification commands, load `skills/command-discovery/SKILL.md` unless the exact relevant commands are already known from explicit project instructions or earlier command discovery.

Do not invent test, lint, typecheck, build, or smoke-test commands.

## Choose verification level

### Narrow verification

Use for Fast Patch and localized Standard changes:

- Targeted test.
- Touched package test.
- Typecheck/lint for the touched area.
- Build or compile check.
- Static inspection when no executable check exists.

### Broad verification

Use for wider Standard changes and Strict changes:

- Full relevant test suite.
- Full typecheck.
- Build.
- Integration or smoke test.
- Migration dry run or fixture-based validation.

## Failure handling

If a check fails:

1. Determine whether the failure is caused by your change.
2. Fix if in scope.
3. Re-run the relevant check.
4. If unrelated or blocked, report evidence and do not claim success.

## Commands log

Record:

```text
Command: <exact command>
Cwd: <directory>
Source: <user | project docs | package script | config | convention>
Result: passed | failed | not run
Summary: <short result or reason>
```

## Do not

- Do not hide failing checks.
- Do not summarize a failed command as passed.
- Do not claim full verification from narrow checks.
- Do not install dependencies just to make verification possible unless install policy allows it.
