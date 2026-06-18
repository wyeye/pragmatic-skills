---
name: evidence-driven-execution
description: Binds commands, file changes, approvals, reviews, and completion claims to observable evidence so the workflow cannot rely on fabricated progress.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.1
---

# Evidence-Driven Execution

Treat evidence as typed records, not narrative confidence.

- Command evidence includes command, working directory, relevant environment, exit code, and concise output.
- File evidence includes path, change type, and final content or diff inspection.
- Approval evidence includes approver, exact scope, decision, and ordering before execution.
- Review evidence identifies the actual diff or artifacts reviewed and the resulting findings.
- Claims reference earlier evidence IDs.

A successful command proves only what that command checks. Re-run stale verification after subsequent file changes. Explicitly mark unavailable, skipped, or inconclusive checks.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
