---
name: safety-gates
description: Requires explicit, scoped, timely approval before high-impact execution and verifies that the approved scope matches the actual action.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.1
---

# Safety Gates

Ask for approval only at an actual execution boundary. The request must state:

- Exact command or operation.
- Target environment, repository, branch, account, or data scope.
- Expected effect and blast radius.
- Recovery or rollback path.
- What will not be changed.

Approval must be explicit and scoped. A vague “go ahead” does not authorize a materially broader operation. Record approval before the action starts. Stop on rejection, ambiguity, changed preconditions, expired context, or any scope mismatch.

Never interpret requirement confirmation, plan approval, or prior unrelated approval as permission for a high-risk action.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
