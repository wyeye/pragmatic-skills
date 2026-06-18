---
schema: psp.skill/v1
name: worktree
description: Use git worktree isolation only when it materially reduces risk.
kind: support
version: 1.8.0
summary: Use git worktree isolation only when it materially reduces risk.
triggers:
- Dirty tree with unrelated user changes.
- Risky/long-running/experimental/many-file change.
- Rollback or multiple attempts matter.
- User requested worktree isolation.
loads: {}
outputs:
- worktree decision
- commands run
- path/branch if created
- cleanup status
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/strict-change/SKILL.md#loads.phased.isolation
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Worktree

## Internal activation

This is a support skill. It is loaded by a mode, router, or another support skill when the relevant phase or condition is reached.

Users do not need to ask for this skill directly.

Use this skill when branch/worktree isolation materially reduces risk.

Do not create a worktree automatically just because a task is in Strict Change. Create one only when the activation conditions match.

## Activation conditions

Use a worktree when:

- The current working tree has unrelated user changes.
- The change is risky, long-running, experimental, or likely to touch many files.
- Rollback/isolation materially reduces risk.
- Multiple independent attempts may be useful.
- The user explicitly requested branch/worktree isolation.

Skip a worktree when:

- The task is read-only.
- The edit is small and local.
- The environment does not support git worktrees.
- Creating a worktree would be more disruptive than useful.

## Goal

Protect the main working tree and make rollback easier.

## Before creating a worktree

Check:

```bash
git status --short
git branch --show-current
git worktree list
```

Do not overwrite or disturb user changes.

## Create

Use a descriptive branch/worktree name:

```bash
git worktree add ../<repo>-<task> -b task/<task>
```

Work inside the new worktree.

## Cleanup

After completion or abandonment:

```bash
git worktree list
git worktree remove ../<repo>-<task>
```

Delete branches only after confirming they are no longer needed.

## Evidence

Report:

- Whether a worktree was created.
- Commands run.
- Worktree path/branch if created.
- Cleanup status if cleanup occurred.

## Do not

- Do not force-remove worktrees with unknown changes.
- Do not assume the worktree exists unless the command succeeded.
- Do not mix unrelated tasks in one worktree.
