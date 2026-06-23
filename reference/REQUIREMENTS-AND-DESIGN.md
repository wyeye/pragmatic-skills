# Requirements and design guide

A Requirement Brief records problem, outcome, scope, non-goals, constraints, acceptance criteria, design rationale, assumptions, risks, and confirmation state. Questions should be decision-critical and asked one at a time.

## Passive behavior/state matrix trigger

The agent should create a behavior/state matrix without asking the user to name this Skill when both conditions hold:

1. The task changes state through more than one entry point or crosses more than one system boundary.
2. Reads, writes, external calls, device/event effects, synchronization, or query visibility may differ by path.

Typical signals include delete, remove, sync, reconcile, restore, status, lifecycle, retry, or backfill behavior across an admin/platform action, local service or database, external platform, device/event path, client/H5 sync, bulk job, scheduler, retry, or recovery flow.

A matching keyword alone is not enough. Do not create the matrix for a single, fully specified local path with no adjacent entry point, cross-boundary side effect, or reconciliation behavior.

## Matrix template

Use stable row IDs so planning and verification can refer to the same paths.

| ID | Entry or trigger | Reads / source of truth | Local writes / state transition | External platform or API effect | Device or event side effect | Sync / reconciliation / backfill behavior | Query visibility / post-condition |
|---|---|---|---|---|---|---|---|
| BM-1 |  |  |  |  |  |  |  |
| BM-2 |  |  |  |  |  |  |  |

Populate rows from repository or user evidence. Consider adjacent paths that exist in the domain, including:

- Platform or admin action.
- Device-originated action or callback.
- Client or H5 synchronization.
- Bulk operation or scheduled reconciliation.
- Retry, restore, replay, or recovery path.

Every cell must contain an evidence-backed statement or one of `none`, `not applicable`, or `unknown`. Never guess a side effect. A material `unknown` becomes an open decision; ask only the highest-impact question and set the Requirement Brief confirmation state accordingly.

## Cross-path invariants

After completing the rows, derive explicit invariants such as:

- Which source is authoritative for each transition.
- An external or device side effect occurs only on the intended entry path.
- A neighboring path does not perform that side effect.
- Synchronization does not resurrect deleted or tombstoned state unless restoration is explicitly required.
- Queries hide, retain, or expose the record as specified after each transition.
- Retries and partial failures preserve ordering and idempotency where relevant.

Convert matrix rows and invariants into observable acceptance criteria. Preserve their IDs through planning, TDD, verification, and review.

## Example shape

For a platform/local/device/client flow, a brief may establish separate rows for:

- Platform removal: external platform update, local transition, and device notification.
- Device-originated removal: device/local transition without deleting external platform state.
- Client or H5 synchronization: reads only eligible local state and does not restore tombstoned records.

These are examples, not defaults. Actual semantics must come from user or repository evidence.

## Downstream contract

- `writing-plans` maps every row and invariant to implementation and test/inspection work, or records why no change is needed.
- `tdd` covers paths where a side effect must occur and neighboring paths where it must not occur.
- `verification` reports each row as verified, partially verified, or unverified.
- `review` checks the final diff for omitted adjacent paths, wrong-path side effects, source-of-truth mismatches, synchronization resurrection, and incorrect query visibility.

Machine-readable regression cases live under `evals/cases/`; requirements behavior includes ambiguous-auth, multi-system behavior-matrix, and single-path negative-control fixtures.
