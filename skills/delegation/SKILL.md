---
schema: psp.skill/v1
name: delegation
description: Use real subagents or explicit role-separated passes without pretending subagents exist.
kind: support
version: 1.6.0
summary: Use real subagents or explicit role-separated passes without pretending subagents exist.
triggers:
- Large task split.
- Independent implementation/test/review reduces risk.
- Strict Change benefits from second perspective.
loads:
  conditional:
    integration_verification:
    - skills/verification/SKILL.md
    final_review:
    - skills/review/SKILL.md
outputs:
- subagent task/evidence or role-pass evidence
- integration checklist
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/review/SKILL.md#loads.conditional.delegation_useful
  - skills/strict-change/SKILL.md#loads.phased.delegation
  routing_note: Users provide tasks; agents route from AGENTS.md through triage and phase triggers. Users do not manually invoke individual skills.
---
# Delegation

## Internal activation

This is a support skill. It is loaded by a mode, router, or another support skill when the relevant phase or condition is reached.

Users do not need to ask for this skill directly.

Use this skill for real subagents or explicit role-separated passes.

The main rule: never fake subagents.

## When to use

Use when:

- The task is large enough to split.
- Independent implementation, testing, or review would reduce risk.
- Strict Change would benefit from a second perspective.

Do not use for tiny edits.

## Real subagent mode

If actual subagent/tool support exists:

1. Give each subagent one clear task.
2. Require concrete evidence:
   - Files inspected.
   - Files changed.
   - Commands run.
   - Results.
   - Risks or open questions.
3. Verify the evidence before integrating.
4. Run final integrated verification.

## Role-pass fallback

If no real subagent exists, say so and perform separate passes:

- Implementer pass.
- Tester pass.
- Reviewer pass.

Use this wording:

```text
No separate subagent was available, so I used separate implementer/tester/reviewer passes.
```

## Anti-fabrication rules

Do not invent:

- Subagent names.
- Subagent conversations.
- Tool calls.
- Test output.
- Review approvals.
- User confirmations.

## Integration checklist

- Confirm patches apply cleanly.
- Check for conflicting assumptions.
- Run relevant tests in the integrated tree.
- Review the final diff.
