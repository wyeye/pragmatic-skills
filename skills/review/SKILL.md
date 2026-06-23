---
name: review
description: Reviews the actual final diff and evidence for correctness, regressions, security, maintainability, scope control, and acceptance-criteria coverage.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.2
---

# Review

Review the final state, not the intended plan.

Inspect changed files and relevant surrounding code. Prioritize correctness, data loss, security, concurrency, compatibility, error handling, tests, and unmet acceptance criteria. Distinguish blocking defects from improvements. Every finding should identify the path or behavior, why it matters, and a concrete remedy.

When a behavior/state matrix exists, compare the final diff and verification evidence against every `BM-*` row and cross-path invariant. Look specifically for an omitted adjacent entry point, a side effect occurring on the wrong path, a source-of-truth mismatch, synchronization that resurrects deleted state, and post-transition queries that expose the wrong records. A correct implementation of the first-named button or endpoint is insufficient when another evidenced path remains inconsistent.

Do not approve based solely on test results. Do not invent findings to appear thorough. When no defect is found, state the review scope and residual blind spots.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
