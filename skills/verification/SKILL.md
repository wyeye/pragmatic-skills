---
name: verification
description: Builds a risk-based verification ladder, executes current checks, and maps results to acceptance criteria without overclaiming coverage.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.1
---

# Verification

Use the narrowest-to-broadest ladder justified by risk:

1. Static inspection and focused diff review.
2. Targeted unit or behavior test.
3. Relevant lint, type-check, integration, or contract checks.
4. Build, packaging, migration dry-run, or local runtime check.
5. Broader regression suite when impact warrants it.

Map each acceptance criterion to actual evidence. Check that generated artifacts, documentation, and configuration remain consistent. Verification becomes stale after later changes; rerun the affected layer. Report skipped checks and their consequences.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
