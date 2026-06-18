---
schema: psp.skill/v1
name: handoff
description: Final compact, factual, evidence-based response after changes, proposals, or reviews.
kind: support
version: 1.7.0
summary: Final compact, factual, evidence-based response after changes, proposals, or reviews.
triggers:
- Before final response after file/code work.
- Before final response after proposals or review findings.
loads: {}
outputs:
- changed/proposed/findings
- verified
- review
- not verified
- notes/risks
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/exploration/SKILL.md#loads.conditional.completion
  - skills/project-agents-md/SKILL.md#loads.conditional.completion
  - skills/fast-patch/SKILL.md#loads.conditional.completion
  - skills/standard-change/SKILL.md#loads.phased.completion
  - skills/strict-change/SKILL.md#loads.phased.completion
  - skills/using-pragmatic-skills/SKILL.md#loads.conditional.completion
  - skills/workflow-retrospective/SKILL.md#loads.conditional.changed_files_completion
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Handoff

## Internal activation

This is a support skill. It is loaded by a mode, router, or another support skill when the relevant phase or condition is reached.

Users do not need to ask for this skill directly.

Use this skill for the final response after making, proposing, or reviewing changes.

The final response must be compact, factual, and evidence-based.

## Retrospective boundary

Handoff is the normal end-of-task factual summary. Do not automatically turn every handoff into a workflow retrospective and do not routinely offer one.

If the user explicitly asks to evaluate PSP, its routing, its skill triggers, or its friction after the task, the entry workflow routes that new request to `skills/workflow-retrospective/SKILL.md`.

## Required sections

Use the relevant sections only:

```text
Changed:
- <file or area>: <what changed>

Verified:
- <command/check>: <result>

Review:
- <mode and evidence, if review happened>

Not verified:
- <gap or reason>

Notes / risks:
- <important caveat or follow-up>
```

If no files were changed, use `Proposed:` or `Findings:` instead of `Changed:`.

For Strict Change, also include:

```text
Risk category:
...
Safety gate status:
...
Rollback / mitigation:
...
```

## Evidence requirements

When applicable, include:

- Actual files changed or inspected.
- Exact commands/checks run, working directory, and results.
- Command source when relevant: user, project docs, package script, config, or convention.
- Review mode used: independent subagent, self-review pass, or static checklist.
- What remains unverified.

## Wording rules

Be factual:

- “Changed” only if files were actually changed.
- “Would change” if only proposing.
- “Ran” only if the command ran.
- “Passed” only if the command passed.
- “Reviewed” only if a review pass happened.
- “Approved” only if the user or a real reviewer approved it.
- “Not verified” is better than fake confidence.

## Keep it compact

Do not paste large diffs or long logs unless asked.

Prefer file names, commands, results, and concise notes.

## If blocked

Say:

- What was completed.
- What blocked the rest.
- What evidence exists.
- The next concrete step.

Do not promise future background work.
