---
name: requirements-and-design
description: Clarifies intended behavior, scope, non-goals, acceptance criteria, and design decisions before planning or implementation when material ambiguity exists.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.1
---

# Requirements and Design

Produce a compact Requirement Brief containing:

- Problem and intended outcome.
- In-scope and out-of-scope behavior.
- Constraints and non-goals.
- Observable acceptance criteria.
- Design options considered and the selected rationale.
- Risks, assumptions, and unresolved decisions.

Ask one decision-critical question at a time. Safe, reversible, low-impact defaults may proceed only when explicitly documented. The confirmation state must be one of `confirmed`, `conditionally confirmed`, `safe assumptions used`, or `blocked on user decision`.

Do not begin implementation from `blocked on user decision`. Requirement confirmation is not safety approval.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
