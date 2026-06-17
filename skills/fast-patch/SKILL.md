---
schema: psp.skill/v1
name: fast-patch
kind: mode
version: 1.2.0
summary: Small, clear, low-risk edits with narrow verification.
triggers:
- Tiny localized edits with low blast radius and no high-risk trigger.
loads:
  conditional:
    command_needed:
    - skills/command-discovery/SKILL.md
    completion:
    - skills/handoff/SKILL.md
    scope_or_risk_increase:
    - skills/triage/SKILL.md
outputs:
- minimal change
- narrow verification evidence
- handoff summary
routing:
  user_exposed: false
  user_invocation_required: false
  activation: router-selected-mode
  invoked_by:
  - skills/triage/SKILL.md
  contract: Selected internally for tiny low-risk edits.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
---

# Fast Patch
## Routing contract

This skill is an internal routing target. Users do not need to ask for this skill directly; the entry workflow, triage, mode, or phase trigger loads it when appropriate.



Use this skill for small, clear, low-risk edits.

This mode is selected internally by triage. The user does not need to request Fast Patch.

## Goal

Make the smallest useful change with the narrowest meaningful verification.

## Workflow

1. Identify the minimal relevant file set.
2. Make the minimal edit.
3. Run the narrowest meaningful check available.
4. Inspect the diff.
5. Load `skills/handoff/SKILL.md` for the final response.

## Verification preference

Use the strongest practical check, in this order:

1. Targeted test for the touched behavior.
2. Typecheck or lint for the touched area.
3. Build or compile check.
4. Static inspection when no executable check exists.

If the relevant command is not already known, load `skills/command-discovery/SKILL.md` automatically. Do not invent a test/lint/build command.

Do not claim full test coverage unless full tests actually ran.

## Escalate

Escalate to Standard Change if:

- More than a tiny local edit is required.
- Behavior changes in a non-trivial way.
- Tests need to be created or updated.
- The diff becomes hard to review.

Escalate to Strict Change if high-risk triggers appear.

## Final evidence

Report:

- What changed.
- What verification ran.
- What was not verified.
