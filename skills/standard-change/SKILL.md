---
name: standard-change
description: Runs the normal end-to-end implementation workflow: clarify requirements, plan, implement, test, verify acceptance criteria, review the diff, and hand off.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: mode
  psp-version: 2.0.1
---

# Standard Change

Use a complete but proportionate implementation loop.

1. Discover repository facts and commands.
2. Activate requirements and design only when intended behavior, scope, or acceptance criteria are not already settled.
3. Produce a file-oriented plan for non-trivial work.
4. Implement in small coherent increments; use test-first development where it improves confidence.
5. Run risk-appropriate verification and map results to every acceptance criterion.
6. Review the actual final diff for correctness, regressions, security, maintainability, and scope control.
7. Deliver a handoff that distinguishes verified facts, unverified areas, and remaining risks.

Do not treat passing tests as proof that every requirement is met. Re-triage immediately when the work gains production, data, access-control, billing, or destructive impact.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
