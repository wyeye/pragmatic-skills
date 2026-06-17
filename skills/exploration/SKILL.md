---
schema: psp.skill/v1
name: exploration
kind: mode
version: 1.2.0
summary: Investigate, diagnose, compare options, or clarify requirements before editing.
triggers:
- Ambiguous requirements.
- Diagnosis or design tasks.
- Need to inspect project before deciding whether to edit.
loads:
  conditional:
    command_needed:
    - skills/command-discovery/SKILL.md
    implementation_needed:
    - skills/triage/SKILL.md
    completion:
    - skills/handoff/SKILL.md
outputs:
- findings
- options
- recommendation
- next mode if implementation is needed
routing:
  user_exposed: false
  user_invocation_required: false
  activation: router-selected-mode
  invoked_by:
  - skills/triage/SKILL.md
  - skills/standard-change/SKILL.md
  contract: Selected internally for ambiguous, diagnostic, design, or investigation work.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
---

# Exploration
## Routing contract

This skill is an internal routing target. Users do not need to ask for this skill directly; the entry workflow, triage, mode, or phase trigger loads it when appropriate.



This mode is selected internally by triage. The user does not need to request Exploration.

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
