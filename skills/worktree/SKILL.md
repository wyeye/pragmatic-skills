---
name: worktree
description: Uses an isolated Git worktree when it materially reduces collision or rollback risk, while preserving existing uncommitted user work.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.2
---

# Worktree Isolation

Before creating a worktree, inspect repository status and current instructions. Never discard or move user changes. Choose a new branch and directory that do not collide with existing worktrees, verify the baseline, and record the relationship to the source repository.

After implementation, report where the work lives and whether cleanup is safe. Do not delete a worktree containing uncommitted or unmerged work without explicit approval.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
