---
name: fast-patch
description: Executes a tiny, fully specified, low-risk change with minimal ceremony while still preserving evidence, verification, and a truthful handoff.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: mode
  psp-version: 2.0.2
---

# Fast Patch

Use the shortest safe path without skipping evidence.

1. Inspect the target file and nearby constraints.
2. Confirm the requested outcome is unambiguous and low-risk.
3. Make the smallest coherent edit; do not opportunistically refactor unrelated code.
4. Discover and run the narrowest meaningful check, then broaden only when repository conventions or risk require it.
5. Inspect the final diff and deliver a factual handoff.

Escalate to `standard-change` when the edit expands, tests reveal broader behavior, or a design decision appears. Escalate to `strict-change` before any high-impact action.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
