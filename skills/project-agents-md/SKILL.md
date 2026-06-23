---
name: project-agents-md
description: Creates or refactors project-specific AGENTS.md instructions while preserving installer-managed blocks and asking before passive creation.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: direct
  psp-version: 2.0.2
---

# Project AGENTS.md

This is a direct route only when the user explicitly requests instruction maintenance. Passive discovery requires permission before writing.

- Inspect the repository and derive only durable, project-specific guidance.
- Preserve every PSP-managed block byte-for-byte; installers own those regions.
- Prefer commands, boundaries, generated-file rules, architecture constraints, and verification expectations over generic advice.
- Keep instructions testable and avoid duplicating material already enforced by tooling.
- Validate references and run a final diff review.

Never replace a project-owned `AGENTS.md` wholesale when a focused edit is sufficient.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
