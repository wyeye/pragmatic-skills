---
name: writing-plans
description: Turns a confirmed requirement brief into a file-oriented implementation and verification plan with dependencies, checkpoints, and rollback considerations.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.1
---

# Writing Plans

A useful plan names concrete artifacts and decision points.

For each step include the intended behavior, likely files or symbols, prerequisite evidence, implementation action, validation method, and stop condition. Map every acceptance criterion to one or more tests or inspections. Mark independent work that can be delegated and risky work that must remain serialized.

Plans are hypotheses: update them when repository evidence differs. Do not create ceremonial steps that provide no control or verification value.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
