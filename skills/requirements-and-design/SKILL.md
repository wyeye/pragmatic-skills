---
schema: psp.skill/v1
name: requirements-and-design
description: Clarify goals, scope, acceptance criteria, and design choices before planning or implementation.
kind: support
version: 1.8.0
summary: Turn ambiguous or design-sensitive work into a concise, confirmed requirement brief without adding ceremony to clear tasks.
triggers:
- The user asks to brainstorm, clarify requirements, compare designs, or confirm acceptance criteria.
- A new feature or behavior change has unclear scope, non-goals, constraints, or success criteria.
- Multiple reasonable designs would produce materially different behavior or maintenance tradeoffs.
- Implementation planning would otherwise depend on risky assumptions.
loads:
  conditional:
    project_facts_missing:
    - skills/exploration/SKILL.md
    safety_sensitive_decision:
    - skills/safety-gates/SKILL.md
    design_only_completion:
    - skills/handoff/SKILL.md
outputs:
- requirement brief
- options and recommendation when alternatives matter
- acceptance criteria
- assumptions and open questions
- confirmation state
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  policy: passive-capable
  lifecycle: pre-task
  auto_after_completion: false
  active:
  - User asks in normal language to brainstorm, clarify requirements, compare designs, define acceptance criteria, or confirm a design before coding.
  passive:
  - A mode observes unresolved requirements or materially different design choices before planning or implementation.
  passive_requires_confirmation: false
  invoked_by:
  - skills/exploration/SKILL.md#loads.conditional.requirements_or_design
  - skills/standard-change/SKILL.md#loads.phased.requirements
  - skills/strict-change/SKILL.md#loads.phased.requirements
  - skills/writing-plans/SKILL.md#loads.conditional.requirements_unresolved
  - skills/tdd/SKILL.md#loads.conditional.requirements_or_criteria_conflict
  - skills/review/SKILL.md#loads.conditional.requirement_drift_decision
  routing_note: Users describe the task normally. Modes load this skill when requirement or design decisions must be made; users are not asked to invoke it by name.
---
# Requirements and Design

## Internal activation

This is a support skill. Users do not invoke it by name.

Load it when explicit brainstorming/requirements intent is recognized, or when the selected mode reaches a requirements phase and implementation would otherwise depend on unresolved product or design decisions.

Do not load it for every change. Skip it when the task is already clear, low-risk, and fully specified enough to plan and verify.

## Purpose

Convert an idea, ambiguous request, or design-sensitive change into a compact requirement baseline that downstream planning, TDD, implementation, review, and handoff can use.

Keep two concerns separate:

- `exploration` discovers repository facts, current behavior, constraints, and feasibility.
- `requirements-and-design` decides intended behavior, scope, acceptance criteria, and design direction.

If essential project facts are missing, load `skills/exploration/SKILL.md`, collect the evidence, then resume this skill. Avoid cycling between the two without new evidence.

## When to use

Use when any of these are true:

- The user explicitly asks to brainstorm, clarify, compare, or confirm before implementation.
- The task describes a goal but not observable success criteria.
- Scope or non-goals are unclear.
- Multiple reasonable approaches create materially different user behavior, compatibility, complexity, cost, or maintenance burden.
- An API, data model, interaction flow, architecture boundary, or operational behavior must be chosen.
- A plan would otherwise contain assumptions that are expensive, public, risky, or hard to reverse.

Usually skip when all of these are true:

- The requested outcome is unambiguous.
- The edit is tiny or mechanical.
- Existing tests/specs already define acceptance.
- There is one obvious, reversible implementation path.
- No security, data, compatibility, public behavior, or irreversible decision is hidden in the task.

## Operating model

Use a short diverge/converge loop.

### 1. Establish evidence

Inspect available user statements and relevant project evidence before asking questions.

Record separately:

- Observed facts.
- User-stated requirements.
- Reasonable assumptions.
- Unknowns that affect the result.

Do not turn missing repository facts into product questions. Investigate facts first when possible.

### 2. Frame the requirement

State concisely:

- Goal: the problem or outcome being pursued.
- Current behavior: what happens now, when known.
- Desired behavior: what should be observably different.
- Scope: what this task includes.
- Non-goals: adjacent work intentionally excluded.
- Constraints: compatibility, performance, security, usability, time, ecosystem, or operational limits.
- Acceptance criteria: observable conditions that prove success.

Do not invent requirements. Label inferred items as assumptions.

### 3. Diverge only when alternatives matter

When there are materially different designs, present 2–3 viable options. For each option include only decision-relevant tradeoffs:

- User-visible behavior.
- Compatibility or migration impact.
- Complexity and maintainability.
- Security/data/operational risk.
- Verification burden.

Do not manufacture alternatives for a mechanical task merely to appear thorough.

### 4. Recommend and converge

Recommend one approach and explain why it best fits the evidence and constraints.

Resolve minor reversible details with documented safe defaults. Escalate decision-critical uncertainty to the user.

### 5. Establish confirmation state

End with exactly one of these states:

- `confirmed`: the user explicitly accepted the requirement/design, or an authoritative project spec already fixes it.
- `conditionally confirmed`: the user accepted it subject to stated conditions that downstream work can honor.
- `safe assumptions used`: no user confirmation was necessary because remaining defaults are low-risk, reversible, and documented.
- `blocked on user decision`: implementation must not proceed until a material decision is answered.

A design discussion being complete is not the same as safety approval. Safety-gated actions still follow `skills/safety-gates/SKILL.md`.

## Question policy

Ask only when the answer materially changes the result and no safe default exists.

- Ask one decision-critical question at a time.
- Explain the decision boundary briefly and recommend a default when helpful.
- Do not ask questions whose answers can be discovered from the repository.
- Do not ask the user to approve routine low-risk details merely to create ceremony.
- If several decisions are blocked, sequence them from highest impact to lowest.

You may continue with `safe assumptions used` only when every unresolved choice is:

- Low-risk and easy to reverse.
- Not a public API, compatibility, security, privacy, payment, or data-semantics decision.
- Consistent with existing project behavior or conventions.
- Explicitly recorded for later review.

You must obtain a user decision before implementation when a choice materially affects:

- User-visible behavior or product scope.
- Public APIs, schemas, protocols, or backward compatibility.
- Data meaning, migration, deletion, retention, or privacy.
- Auth, permissions, secrets, security posture, payment, or compliance.
- Irreversible or expensive operational behavior.
- A tradeoff the user explicitly asked to review before coding.

## Requirement Brief

Use this compact output shape. Omit sections that truly do not apply, but do not omit acceptance criteria or confirmation state.

```text
Requirement Brief

Goal:
- ...

Current behavior:
- ...

Desired behavior:
- ...

Scope:
- ...

Non-goals:
- ...

Constraints:
- ...

Acceptance criteria:
1. ...
2. ...

Assumptions:
- ...

Open questions:
- ...

Options considered:
1. Option A — ...
2. Option B — ...

Recommended design:
- ...

Confirmation state:
- confirmed | conditionally confirmed | safe assumptions used | blocked on user decision
- Basis: ...
```

Keep the brief proportionate. A moderate feature often needs 10–25 lines, not a long design document.

## Downstream contract

For implementation work:

- `writing-plans` consumes the latest Requirement Brief and must not silently change confirmed scope or design.
- `tdd` maps acceptance criteria to executable tests where practical.
- `review` checks the actual diff against the accepted criteria and calls out divergence.
- `handoff` reports any criteria not verified and any assumptions that remain.

If the confirmation state is `blocked on user decision`, do not enter implementation planning or editing.

If new evidence invalidates the brief, update the brief, state what changed, and obtain any newly required confirmation before continuing.

For brainstorming/design-only requests, load `skills/handoff/SKILL.md` after presenting the brief and recommendation. Do not enter implementation mode unless the user also asked for implementation.

## Do not

- Do not confuse repository investigation with user requirement decisions.
- Do not ask a long questionnaire before inspecting available evidence.
- Do not force 2–3 options when only one sensible approach exists.
- Do not treat silence as confirmation for material decisions.
- Do not use a vague goal as an acceptance criterion.
- Do not reopen a confirmed design without new evidence or an explicit user request.
- Do not create a design document file unless the user asks or the project requires one.
