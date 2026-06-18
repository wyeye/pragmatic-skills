---
schema: psp.skill/v1
name: fast-patch
description: Small, clear, low-risk edits with narrow verification.
kind: mode
version: 1.8.0
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
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/triage/SKILL.md#loads.select_one
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Fast Patch

## Phase-trigger contract

Do not load all support skills when entering this mode.

Load support skills only when their phase trigger is reached. The user should not be asked to invoke support skills manually.

Use this skill for small, clear, low-risk edits.

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

If the relevant command is not already known, load `skills/command-discovery/SKILL.md`. Do not invent a test/lint/build command.

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
