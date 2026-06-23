---
name: handoff
description: Delivers a compact, truthful completion report that separates changes, evidence, unverified areas, decisions, and remaining risks.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.2
---

# Handoff

A handoff should let another engineer continue without reconstructing the session.

Include:

- What changed or what was learned.
- Important paths or artifacts.
- Commands and checks actually run, with outcomes.
- Acceptance criteria covered.
- Checks not run or evidence that remains inconclusive.
- Residual risks, rollback notes, and required user decisions.

Use precise verbs: “edited,” “ran,” “observed,” and “did not run.” Do not say “complete,” “safe,” “approved,” or “all tests pass” unless the evidence supports that exact scope.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
