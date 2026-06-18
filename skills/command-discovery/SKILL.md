---
name: command-discovery
description: Finds repository-native install, test, lint, type-check, build, run, and verification commands from actual project evidence instead of guessing.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.1
---

# Command Discovery

Resolve commands from the repository in this order:

1. Project instructions and contributor documentation.
2. Package scripts, task runners, Makefiles, and workspace configuration.
3. CI workflows and release automation.
4. Tool configuration, lockfiles, and ecosystem markers.
5. Carefully scoped conventional defaults only when no stronger evidence exists.

Record where each command came from, its working directory, required environment, and whether it mutates state. Never claim a command exists merely because it is common in the ecosystem. Avoid dependency installation unless requested or necessary and safe.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
