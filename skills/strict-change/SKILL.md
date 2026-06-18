---
name: strict-change
description: Controls high-impact or hard-to-reverse changes with explicit risk analysis, scoped approval, rollback preparation, stronger verification, and auditable evidence.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: mode
  psp-version: 2.0.1
---

# Strict Change

High impact changes require stronger control, not just more prose.

1. Identify assets, affected environments, blast radius, reversibility, and failure modes.
2. Settle requirements and acceptance criteria before implementation.
3. Prepare a rollback or containment plan and validate prerequisites without executing the risky action.
4. Request explicit, scoped user approval immediately before each high-risk execution boundary.
5. Record approval and action ordering in the trace.
6. Execute the smallest approved scope; stop if actual conditions differ from the approved assumptions.
7. Verify both success behavior and rollback/containment behavior where feasible.
8. Perform an independent final review and disclose every residual risk.

Approval never transfers across materially different environments, commands, data scopes, or time windows.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
