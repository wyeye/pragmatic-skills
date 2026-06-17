---
schema: psp.skill/v1
name: strict-change
description: High-risk work with safety gates, traceability, rollback thinking, evidence, verification, and review.
kind: mode
version: 1.6.0
summary: High-risk work with safety gates, traceability, rollback thinking, evidence, verification, and review.
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
- risk category
- safety gate status
- rollback/mitigation notes
- evidence log
- verification results
- review findings
safety:
  approval_required: Before gated actions only; read-only inspection, local tests, and draft patches do not require approval.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/standard-change/SKILL.md#loads.escalation
  - skills/triage/SKILL.md#loads.select_one
  routing_note: Users provide tasks; agents route from AGENTS.md through triage and phase triggers. Users do not manually invoke individual skills.
---
# Strict Change

## Phase-trigger contract

Do not load all support skills when entering this mode.

Load support skills only when their phase trigger is reached. The user should not be asked to invoke support skills manually.

Use this skill for high-risk work.

Strict Change optimizes for correctness, traceability, reversibility, and explicit evidence.

## Immediate requirement

Immediately after selecting Strict Change, load `skills/safety-gates/SKILL.md` and identify the risk category.

Loading safety gates does not mean you must ask for approval for read-only inspection, local tests, or draft patches. It means you must know which actions require approval before you perform them.

## Progressive support loading

Do not load every support skill at mode entry. Load by phase:

- Risk phase: `skills/safety-gates/SKILL.md` immediately after entering Strict Change.
- Command phase: `skills/command-discovery/SKILL.md` when install/test/lint/typecheck/build/run commands are needed and not already known from explicit project instructions.
- Isolation phase: `skills/worktree/SKILL.md` only when isolation is useful or required.
- Planning phase: `skills/writing-plans/SKILL.md` before non-trivial implementation.
- Evidence phase: `skills/evidence-driven-execution/SKILL.md` before editing, delegating, or making audit-sensitive claims.
- Behavior phase: `skills/tdd/SKILL.md` for behavior changes and bug fixes when executable tests are practical.
- Delegation phase: `skills/delegation/SKILL.md` only if real subagents exist or explicit role-separated passes reduce risk.
- Verification phase: `skills/verification/SKILL.md` before validation and before reporting checks.
- Review phase: `skills/review/SKILL.md` before calling the work complete.
- Completion phase: `skills/handoff/SKILL.md` before the final response.

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
- Rollback or mitigation strategy.
- Executable plan for non-trivial work.
- Evidence approach: which checks will prove the change.
- Command sources for verification/build steps, when commands are needed.

## Workflow

1. Identify the risk category.
2. Define blast radius and rollback/mitigation strategy.
3. Check safety gates before any gated action.
4. Resolve project commands only when needed.
5. Create an executable plan.
6. Add or update tests before behavior changes when practical.
7. Implement in small, reversible steps.
8. Run targeted and broader verification.
9. Review the actual diff for security, data, compatibility, and accidental changes.
10. Final report must include residual risk.

## Required final evidence

Include:

- Risk category.
- Safety gate status.
- Files changed.
- Commands/checks run.
- Results.
- Known gaps.
- Rollback or mitigation notes.

## Do not

- Do not batch unrelated changes.
- Do not silently alter public behavior.
- Do not run gated actions without approval.
- Do not claim safety without evidence.
- Do not claim a worktree, review, or subagent existed unless it actually existed.
