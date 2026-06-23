---
name: using-pragmatic-skills
description: Entry point for repository work. Routes ordinary requests through one primary workflow mode and exposes support skills only at the phase where they are needed.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: entry
  psp-version: 2.0.2
---

# Using Pragmatic Skills

Start here for repository work. Users describe the task normally; never require them to name an internal skill.

## Routing sequence

1. Read repository-level instructions and preserve higher-priority user constraints.
2. Use a direct route only for an explicit `AGENTS.md` maintenance request or an explicit PSP workflow retrospective.
3. Otherwise activate `triage` and select exactly one primary mode.
4. Load support skills only when the current phase reaches their trigger.
5. Re-run triage when new evidence materially changes scope, ambiguity, reversibility, or impact.

## Invariants

- One primary mode is active at a time.
- Investigation is not implementation.
- Requirement confirmation and safety approval are separate decisions.
- No command, test, review, approval, or result may be invented.
- A task is not complete until its acceptance criteria and risk-appropriate verification are addressed.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
