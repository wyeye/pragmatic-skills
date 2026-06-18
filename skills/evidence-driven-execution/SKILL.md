---
schema: psp.skill/v1
name: evidence-driven-execution
description: Back every claim with actual evidence or label it as an assumption.
kind: support
version: 1.7.0
summary: Back every claim with actual evidence or label it as an assumption.
triggers:
- Non-trivial edits.
- Auditable work.
- Delegated work.
- Before claiming completion or verification.
loads: {}
outputs:
- evidence log
- precise claim wording
- unverified gaps
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/standard-change/SKILL.md#loads.phased.execution
  - skills/strict-change/SKILL.md#loads.phased.evidence
  - skills/project-agents-md/SKILL.md#loads.conditional.editing
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Evidence-Driven Execution

## Internal activation

This is a support skill. It is loaded by a mode, router, or another support skill when the relevant phase or condition is reached.

Users do not need to ask for this skill directly.

Use this skill whenever work may be audited, reviewed, delegated, or called complete.

## Rule

A claim must be backed by evidence or labeled as an assumption.

Evidence must come from actual inspection, actual file changes, actual command output, actual tool calls, or explicit user messages.

## Never fabricate

Do not fabricate:

- Test results.
- Build output.
- Lint/typecheck output.
- Subagent activity.
- Review findings.
- File changes.
- Git status.
- User approvals.
- External facts.

## Evidence sources

Prefer concrete sources:

- Files inspected.
- Files changed.
- Diff or patch summary.
- Exact commands run.
- Command sources and working directories.
- Command results.
- Tool outputs.
- User approvals.

Do not infer git status, tests, review outcome, or user approval from intent or memory.

## Claim vocabulary

Use precise language:

- “I ran `<command>` in `<cwd>` and it passed.”
- “I ran `<command>` in `<cwd>` and it failed with `<summary>`.”
- “I inspected `<file>`.”
- “I changed `<file>`.”
- “I did not run tests because `<reason>`.”
- “I performed a self-review pass.”
- “No separate subagent was available.”

Avoid unsupported language:

- “Should be fine.”
- “Fully verified.”
- “No regressions.”
- “The reviewer approved it.”

unless evidence supports it.

## Evidence log

For non-trivial work, keep a compact evidence log:

```text
Files inspected:
- ...

Files changed:
- ...

Commands run:
- command: ...
  cwd: ...
  source: ...
  result: ...

Review evidence:
- ...

Unverified:
- ...
```

## When evidence is impossible

State the limitation and the strongest available substitute:

```text
I could not run the test suite because dependencies are unavailable. I verified by static inspection of X and Y; runtime behavior remains unverified.
```
