---
name: tdd
description: Uses test-first development when it improves behavioral confidence, while documenting justified exceptions for unsuitable or already-covered changes.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.1
---

# Test-Driven Development

Prefer a red–green–refactor loop for observable behavioral changes:

1. Add or identify the smallest test that expresses an acceptance criterion.
2. Run it and confirm the failure is relevant, not an environmental accident.
3. Implement the smallest coherent behavior.
4. Run the targeted test, then the appropriate broader suite.
5. Refactor only while tests remain green.

When test-first work is unsuitable, state why and choose another concrete verification method. Never manufacture a “red” result or weaken tests merely to make them pass.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
