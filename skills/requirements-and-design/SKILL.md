---
name: requirements-and-design
description: Clarifies intended behavior, scope, non-goals, acceptance criteria, cross-system state semantics, and design decisions before planning or implementation when material ambiguity exists.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts or a PSP host adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: support
  psp-version: 2.0.2
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

## Behavior and state matrix

Before planning or implementation, create a behavior/state matrix when state-changing work spans multiple entry points or system boundaries and the semantics can differ by path. Common signals include delete, remove, sync, reconcile, restore, status, lifecycle, retry, or backfill flows involving combinations such as an admin/platform action, a local service or database, an external platform, a device or event channel, and a client/H5 synchronization path.

Do not activate this matrix merely because one of those words appears. A single, fully specified path with no cross-boundary side effect, reconciliation behavior, or adjacent entry point does not need it.

Give each row a stable ID such as `BM-1` and record:

| ID | Entry or trigger | Reads / source of truth | Local writes / state transition | External platform or API effect | Device or event side effect | Sync / reconciliation / backfill behavior | Query visibility / post-condition |
|---|---|---|---|---|---|---|---|

Include every adjacent entry point supported by repository or user evidence, not only the button or endpoint named first. Consider platform/admin actions, device-originated events, client/H5 sync, bulk operations, scheduled jobs, retries, restore, and recovery paths when they exist in the domain.

Every cell must be evidence-backed or explicitly marked `none`, `not applicable`, or `unknown`. Never invent a side effect or source of truth. A material `unknown` becomes an open decision and may change the confirmation state to `blocked on user decision`.

Derive cross-path invariants and acceptance criteria from the completed rows, including when relevant:

- Which source is authoritative for each transition.
- Which external or device side effect must occur and which must not occur.
- Whether deleted or tombstoned state can be restored by synchronization.
- What remains queryable after each transition.
- Retry, ordering, idempotency, and partial-failure semantics.

The matrix is a requirement artifact. Planning, tests, verification, and review must preserve its row IDs and invariants so omitted adjacent paths remain visible.

## Operating rule

Use this skill only while its trigger is active. Keep conclusions proportional to observed evidence, preserve user-owned work, and stop when a required decision or approval is unavailable.

## Trace contract

When PSP tracing is enabled, record mode selection, skill activation, commands, file changes, approvals, verification, and claims as structured events. Every strong completion claim must reference earlier evidence event IDs.
