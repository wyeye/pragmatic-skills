---
schema: psp.skill/v1
name: exploration
description: Investigate, diagnose, compare options, or clarify requirements before editing.
kind: mode
version: 1.7.0
summary: Investigate, diagnose, compare options, or clarify requirements before editing.
triggers:
- Ambiguous requirements.
- Diagnosis or design tasks.
- Need to inspect project before deciding whether to edit.
loads:
  conditional:
    command_needed:
    - skills/command-discovery/SKILL.md
    project_instructions:
    - skills/project-agents-md/SKILL.md
    implementation_needed:
    - skills/triage/SKILL.md
    completion:
    - skills/handoff/SKILL.md
outputs:
- findings
- options
- recommendation
- next mode if implementation is needed
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/standard-change/SKILL.md#loads.phased.discovery
  - skills/triage/SKILL.md#loads.select_one
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Exploration

## Phase-trigger contract

Do not load all support skills when entering this mode.

Load support skills only when their phase trigger is reached. The user should not be asked to invoke support skills manually.

Use this skill for investigation, diagnosis, design, or unclear requirements.

## Goal

Learn enough to choose the right next step without prematurely editing files.

## Workflow

1. State the exploration target in one sentence.
2. Inspect only the relevant files, tests, logs, docs, or configuration.
3. Separate facts from assumptions.
4. If design is involved, produce 2–3 viable options.
5. Recommend one path with tradeoffs.
6. Route to the next mode if implementation is needed.


## Project instruction exploration

If exploration discovers that the repository lacks `AGENTS.md`, has only generic PSP entry content, or has stale/contradictory agent instructions, load `skills/project-agents-md/SKILL.md`.

Passive discovery should not silently create or refactor `AGENTS.md`; the project-instruction skill must ask the user first.

## Command discovery during exploration

If exploration requires understanding available project commands, load `skills/command-discovery/SKILL.md` and record command sources.

Do not run long-running local servers or install dependencies just to explore unless the user asked for that and the action is safe.

## Clarifying questions

Ask at most one focused question when the answer materially changes the implementation and no safe assumption exists.

If safe defaults exist, state them and continue.

## Output shape

```text
Findings:
- ...

Options:
1. ...
2. ...
3. ...

Recommendation:
...

Next skill:
...
```

## Do not

- Do not make code changes during Exploration unless the user already asked for implementation and you route into a mode skill.
- Do not inspect unrelated areas just because they are interesting.
- Do not present guesses as verified facts.
