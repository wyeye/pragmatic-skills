---
schema: psp.skill/v1
name: handoff
kind: support
version: 1.2.0
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
routing:
  user_exposed: false
  user_invocation_required: false
  activation: completion-triggered-support
  invoked_by:
  - skills/using-pragmatic-skills/SKILL.md
  - skills/fast-patch/SKILL.md
  - skills/exploration/SKILL.md
  - skills/standard-change/SKILL.md
  - skills/strict-change/SKILL.md
  contract: Loaded automatically before final responses after code/file work, proposals, or
    reviews.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
---

# Handoff
## Routing contract

This skill is an internal routing target. Users do not need to ask for this skill directly; the entry workflow, triage, mode, or phase trigger loads it when appropriate.



This support skill is loaded automatically before final responses after code/file work, proposals, or reviews. Users do not need to request a handoff.

Use this skill for the final response after making, proposing, or reviewing changes.

The final response must be compact, factual, and evidence-based.

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
