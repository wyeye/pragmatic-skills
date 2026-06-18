---
schema: psp.skill/v1
name: strict-change
description: High-risk work with safety gates, requirements confirmation, traceability, rollback thinking, verification, and review.
kind: mode
version: 1.8.0
summary: High-risk work with safety gates, requirements confirmation, traceability, rollback thinking, verification, and review.
triggers:
- Security/auth/privacy.
- Payments/billing.
- Data/migrations/destructive operations.
- Public API/compatibility.
- Deployment/infrastructure.
- Large or uncertain blast radius.
loads:
  immediate:
  - skills/safety-gates/SKILL.md
  phased:
    discovery:
    - skills/exploration/SKILL.md
    requirements:
    - skills/requirements-and-design/SKILL.md
    command:
    - skills/command-discovery/SKILL.md
    isolation:
    - skills/worktree/SKILL.md
    planning:
    - skills/writing-plans/SKILL.md
    evidence:
    - skills/evidence-driven-execution/SKILL.md
    behavior:
    - skills/tdd/SKILL.md
    delegation:
    - skills/delegation/SKILL.md
    verification:
    - skills/verification/SKILL.md
    review:
    - skills/review/SKILL.md
    completion:
    - skills/handoff/SKILL.md
outputs:
- risk category and safety gate status
- confirmed requirement/design baseline
- rollback/mitigation notes
- evidence log
- verification results
- review findings
safety:
  approval_required: Before gated actions only; read-only inspection, requirements/design work, local tests, and draft patches do not require approval.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/standard-change/SKILL.md#loads.escalation
  - skills/triage/SKILL.md#loads.select_one
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Strict Change

## Phase-trigger contract

Do not load all support skills when entering this mode.

Load support skills only when their phase trigger is reached. The user should not be asked to invoke support skills manually.

Use this skill for high-risk work.

Strict Change optimizes for correctness, traceability, reversibility, explicit requirement decisions, and evidence.

## Immediate requirement

Immediately after selecting Strict Change, load `skills/safety-gates/SKILL.md` and identify the risk category.

Loading safety gates does not mean you must ask for approval for read-only inspection, requirements/design work, local tests, or draft patches. It means you must know which actions require approval before you perform them.

## Progressive support loading

Do not load every support skill at mode entry. Load by phase:

- Risk phase: `skills/safety-gates/SKILL.md` immediately after entering Strict Change.
- Discovery phase: `skills/exploration/SKILL.md` when current behavior, project constraints, feasibility, or blast radius are unclear.
- Requirements phase: `skills/requirements-and-design/SKILL.md` when intended behavior, scope, acceptance criteria, or a material design choice is unresolved. Public compatibility, security, data, payment, privacy, and irreversible choices require explicit user decisions.
- Command phase: `skills/command-discovery/SKILL.md` when install/test/lint/typecheck/build/run commands are needed and not already known.
- Isolation phase: `skills/worktree/SKILL.md` only when isolation is useful or required.
- Planning phase: `skills/writing-plans/SKILL.md` before non-trivial implementation.
- Evidence phase: `skills/evidence-driven-execution/SKILL.md` before editing, delegating, or making audit-sensitive claims.
- Behavior phase: `skills/tdd/SKILL.md` for behavior changes and bug fixes when executable tests are practical.
- Delegation phase: `skills/delegation/SKILL.md` only if real subagents exist or explicit role-separated passes reduce risk.
- Verification phase: `skills/verification/SKILL.md` before validation and before reporting checks.
- Review phase: `skills/review/SKILL.md` before calling the work complete.
- Completion phase: `skills/handoff/SKILL.md` before the final response.

Requirement/design confirmation and safety approval are separate gates. Satisfying one does not satisfy the other.

## Worktree activation

Consider a worktree, but do not load or create one automatically just because Strict Change was selected.

Load `skills/worktree/SKILL.md` when:

- The current working tree has unrelated user changes.
- The change is broad, experimental, or long-running.
- Rollback/isolation materially reduces risk.
- Multiple independent attempts may be useful.
- The user explicitly requested branch/worktree isolation.

## Before editing

Before making high-risk edits, have:

- Risk category.
- Blast radius.
- Safety gate status.
- Requirement Brief or authoritative equivalent when requirements/design is triggered.
- Confirmation state that is not `blocked on user decision`.
- Explicit acceptance criteria.
- Rollback or mitigation strategy.
- Executable plan for non-trivial work.
- Evidence approach: which checks will prove the change.
- Command sources for verification/build steps, when commands are needed.

## Workflow

1. Identify the risk category.
2. Define blast radius and rollback/mitigation strategy.
3. Inspect current behavior and constraints when needed.
4. Resolve material requirements/design decisions and their confirmation state.
5. Check safety gates before any gated action.
6. Resolve project commands only when needed.
7. Create an executable plan tied to acceptance criteria.
8. Add/update tests before behavior changes when practical.
9. Implement in small, reversible steps.
10. Run targeted and broader verification against the accepted criteria.
11. Review the actual diff for requirement drift, security, data, compatibility, and accidental changes.
12. Final report must include residual risk and unverified criteria.

## Requirement change control

Do not silently alter a confirmed requirement or design during implementation.

If new evidence changes the decision:

1. Update the Requirement Brief.
2. Explain why the previous basis is no longer valid.
3. Obtain any newly required user decision.
4. Re-check safety gates and rollback implications.
5. Re-plan before continuing.

## Required final evidence

Include:

- Risk category.
- Safety gate status.
- Requirement/design confirmation state when used.
- Files changed.
- Commands/checks run.
- Acceptance criteria verified and not verified.
- Results and known gaps.
- Rollback or mitigation notes.

## Do not

- Do not batch unrelated changes.
- Do not silently alter public behavior or confirmed scope.
- Do not run gated actions without approval.
- Do not treat requirement confirmation as safety approval.
- Do not claim safety without evidence.
- Do not claim a worktree, review, or subagent existed unless it actually existed.
