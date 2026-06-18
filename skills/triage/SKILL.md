---
name: triage
description: Classifies a repository task into exactly one primary mode using scope, ambiguity, reversibility, and impact, and reclassifies when evidence changes.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: router
  psp-version: 2.0.1
---

# Triage

Select one primary mode before substantive work.

| Mode | Use when |
|---|---|
| `fast-patch` | Tiny, fully specified, low-risk, local, reversible change. |
| `exploration` | The user asks for investigation, explanation, comparison, or diagnosis without implementation. |
| `standard-change` | Implementation spans meaningful behavior, multiple files, tests, or design choices but remains normally reversible. |
| `strict-change` | Production, data, authentication, authorization, billing, secrets, destructive commands, shared history, or difficult rollback is involved. |

Prefer the more conservative mode when uncertainty changes the safe execution path. Do not choose strict mode merely because a task is large; choose it when impact or reversibility demands explicit controls.

Record the selected mode and a concise evidence-based reason. Re-triage after discovering hidden migrations, production coupling, ambiguous acceptance criteria, a much smaller scope, or a non-reversible operation.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
