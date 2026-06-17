---
schema: psp.skill/v1
name: triage
description: Choose the smallest safe primary mode and re-route when evidence changes.
kind: router
version: 1.6.0
summary: Choose the smallest safe primary mode and re-route when evidence changes.
triggers:
- Immediately after using-pragmatic-skills.
- Whenever risk, scope, ambiguity, or blast radius changes.
loads:
  select_one:
  - skills/fast-patch/SKILL.md
  - skills/exploration/SKILL.md
  - skills/standard-change/SKILL.md
  - skills/strict-change/SKILL.md
outputs:
- Mode
- Reason
- Next skill
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/exploration/SKILL.md#loads.conditional.implementation_needed
  - skills/fast-patch/SKILL.md#loads.conditional.scope_or_risk_increase
  - skills/using-pragmatic-skills/SKILL.md#loads.immediate
  - workflow#re-triage-triggers
  routing_note: Users provide tasks; agents route from AGENTS.md through triage and phase triggers. Users do not manually invoke individual skills.
---
# Triage

## Invocation contract

Triage is an internal router, not a user-facing command.

The user does not choose the mode. The agent selects the smallest safe mode, loads only that mode skill, and re-runs triage when evidence changes.

Use this skill to choose the smallest safe workflow for the task.

Triage is provisional. Re-run it whenever new evidence changes risk, scope, ambiguity, or blast radius.

## Output of triage

Pick one primary mode:

- Fast Patch
- Exploration
- Standard Change
- Strict Change

Then load only that mode's `SKILL.md`.

Use this internal shape:

```text
Mode: <Fast Patch | Exploration | Standard Change | Strict Change>
Reason: <why this is the smallest safe mode>
Next skill: <path>
```

## Fast Patch

Choose Fast Patch when all are true:

- The task is clear.
- The change is small and localized.
- No meaningful behavior change, or behavior is trivial.
- Low blast radius.
- No high-risk trigger is present.

Examples:

- Typo or copy fix.
- Small docs update.
- One-line config correction.
- Obvious local bug fix.
- Local refactor with no behavior change.

Load: `skills/fast-patch/SKILL.md`

## Exploration

Choose Exploration when any is true:

- The task is investigative or diagnostic.
- Requirements are ambiguous.
- The user asks for options, architecture, comparison, or recommendation.
- You need to inspect the project before deciding whether to edit.
- Multiple reasonable implementations exist.

Load: `skills/exploration/SKILL.md`

## Standard Change

Choose Standard Change when any is true and no Strict trigger applies:

- The task changes behavior.
- Multiple files are likely involved.
- Tests should be added or updated.
- The change needs a plan or review before it is done.
- The user expects a real implementation, not only investigation.

Load: `skills/standard-change/SKILL.md`

## Strict Change

Choose Strict Change when any high-risk trigger appears:

- Auth, permissions, sessions, security, secrets, cryptography.
- Privacy, PII, compliance, audit logs.
- Payments, billing, credits, quotas, subscriptions.
- Database schema, migrations, backfills, destructive data changes.
- Public API, SDK, wire format, backward compatibility.
- Deployment, release, infrastructure, CI/CD, production config.
- Runtime dependency upgrades or security dependency changes.
- Large refactor, many-file rewrite, uncertain blast radius.
- Generated files, lockfiles, vendored code, or build artifacts whose ownership is unclear.

Load: `skills/strict-change/SKILL.md`


## AGENTS.md and project-instruction tasks

If the user explicitly asks to create, update, migrate, improve, or refactor `AGENTS.md` or repository agent instructions, load `skills/project-agents-md/SKILL.md` as the project-instruction support skill.

Default mode selection:

- Use Exploration when the user only wants an assessment or recommendation.
- Use Standard Change when creating or editing project-owned instruction content.
- Use Strict Change only if the instruction change weakens or changes safety-critical policy around production, deployment, secrets, auth, billing, destructive operations, dependencies, or data handling.

Passive missing-AGENTS detection does not authorize writing. The support skill must ask the user before creating or refactoring from a passive trigger.

## Re-triage triggers

Re-run triage when any of these happen:

- More files, packages, services, or systems are affected than expected.
- Behavior impact becomes non-trivial.
- Tests reveal a broader regression or unknown failure mode.
- Security, data, auth, billing, public API, dependency, deployment, or production risk appears.
- Requirements become clearer and the task can safely be simplified.
- Implementation turns out to be exploratory rather than mechanical.
- The diff becomes large or hard to review.
- Command discovery shows the intended verification/build path has broader impact than expected.

## Allowed transitions

- `fast-patch` -> `standard-change` when behavior, tests, or multi-file scope appears.
- `fast-patch` -> `strict-change` when any high-risk trigger appears.
- `standard-change` -> `strict-change` when high-risk impact appears.
- `exploration` -> `fast-patch | standard-change | strict-change` after findings clarify the work.
- `strict-change` -> `standard-change` only after explicitly stating why the high-risk trigger does not actually apply.
- Any mode -> `exploration` when implementation cannot safely continue without investigation.

## Tie-breakers

- When unclear between Fast Patch and Standard, choose Standard.
- When unclear between Standard and Strict, choose Strict.
- When unclear whether to edit, choose Exploration first.
- Downgrade only after stating why the lighter mode is safe.
