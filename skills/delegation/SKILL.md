---
name: delegation
description: Delegates independent, bounded work with explicit inputs, outputs, constraints, and evidence requirements, then verifies integration centrally.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.1
---

# Delegation

Delegate only bounded work. Each subtask contract must include the objective, allowed files, prohibited actions, required evidence, expected output, and completion criteria. Avoid assigning overlapping writable scopes.

The primary workflow remains responsible for reconciling assumptions, reviewing contributions, resolving conflicts, running integrated verification, and making the final claim. A delegated report is evidence to inspect, not proof by itself.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
