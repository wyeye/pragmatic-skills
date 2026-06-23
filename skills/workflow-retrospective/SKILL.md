---
name: workflow-retrospective
description: Analyzes an explicitly requested PSP workflow retrospective using observable evidence and produces prioritized changes plus regression eval cases.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: direct
  psp-version: 2.0.2
---

# Workflow Retrospective

Run only on an explicit retrospective request.

1. Collect the task prompt, selected modes, activated skills, trace events, corrections, verification, and outcome.
2. Separate observed facts, inferences, unknowns, and missing evidence.
3. Identify the smallest rule, route, tool, or documentation change that would prevent each material failure.
4. Give every proposed behavior change at least one positive and one negative regression case.
5. Rank findings by safety, correctness, frequency, and implementation cost.

The retrospective is read-only by default. When the user asks to apply it, finish the analysis first and re-enter triage for implementation.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
