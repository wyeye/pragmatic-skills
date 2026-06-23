---
name: exploration
description: Performs read-only repository investigation and reports facts, inferences, unknowns, and evidence gaps without silently modifying the project.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: mode
  psp-version: 2.0.2
---

# Exploration

Treat this mode as read-only unless the user explicitly changes the task.

- Inspect repository instructions, relevant files, history, configuration, tests, and generated artifacts.
- Separate observed facts from inferences and open questions.
- Cite concrete paths, symbols, commands, or trace evidence.
- Do not run destructive commands, rewrite files, install dependencies, or “fix while investigating.”
- When the answer requires implementation, summarize the evidence and re-enter triage rather than silently switching modes.

A useful exploration ends with a decision-ready result, not a pile of unranked observations.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
