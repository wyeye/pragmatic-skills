---
schema: psp.skill/v1
name: exploration
description: Investigate repository facts, diagnose issues, and establish feasible options before deciding or editing.
kind: mode
version: 1.8.0
summary: Investigate repository facts, diagnose issues, and establish feasible options before deciding or editing.
triggers:
- Investigation or diagnosis.
- Explicit brainstorming/design-only request.
- Need to inspect project facts before selecting or implementing an approach.
loads:
  conditional:
    command_needed:
    - skills/command-discovery/SKILL.md
    project_instructions:
    - skills/project-agents-md/SKILL.md
    requirements_or_design:
    - skills/requirements-and-design/SKILL.md
    implementation_needed:
    - skills/triage/SKILL.md
    completion:
    - skills/handoff/SKILL.md
outputs:
- findings and constraints
- feasible options when relevant
- requirement brief when requirements/design is activated
- recommendation
- next mode if implementation is needed
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/requirements-and-design/SKILL.md#loads.conditional.project_facts_missing
  - skills/standard-change/SKILL.md#loads.phased.discovery
  - skills/strict-change/SKILL.md#loads.phased.discovery
  - skills/triage/SKILL.md#loads.select_one
  - skills/project-agents-md/SKILL.md#loads.conditional.project_context
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Exploration

## Phase-trigger contract

Do not load all support skills when entering this mode.

Load support skills only when their condition is reached. The user should not be asked to invoke support skills manually.

Use this mode for investigation, diagnosis, feasibility work, or explicit brainstorming/design work that should not immediately edit files.

## Goal

Learn the relevant project facts and constraints, then either:

- hand factual findings into requirements/design,
- recommend a next step,
- or re-triage into an implementation mode.

Do not prematurely edit files.

## Workflow

1. State the exploration target in one sentence.
2. Inspect only relevant files, tests, logs, docs, configuration, and history available in the environment.
3. Separate observed facts from assumptions and unknowns.
4. Identify technical constraints and feasible approaches.
5. When intended behavior, scope, acceptance criteria, or a design decision must be settled, load `skills/requirements-and-design/SKILL.md`.
6. If implementation is requested after the work is clarified, re-run triage and enter the appropriate implementation mode.
7. Otherwise present findings/recommendation through `handoff`.

## Boundary with requirements and design

Exploration answers factual questions:

- What does the project do now?
- Where is the behavior implemented?
- What constraints and conventions already exist?
- Which approaches are technically feasible?
- What caused the observed issue?

`requirements-and-design` answers decision questions:

- What outcome should be delivered?
- What is in scope or out of scope?
- What acceptance criteria define success?
- Which feasible design should be selected?
- Does implementation need a user decision first?

Do not ask the user for repository facts that can be discovered. Do not let Exploration silently decide material product requirements.

## Project instruction exploration

If exploration discovers that the repository lacks `AGENTS.md`, has only generic PSP entry content, or has stale/contradictory agent instructions, load `skills/project-agents-md/SKILL.md`.

Passive discovery should not silently create or refactor `AGENTS.md`; the project-instruction skill must ask the user first.

## Command discovery during exploration

If exploration requires understanding available project commands, load `skills/command-discovery/SKILL.md` and record command sources.

Do not run long-running local servers or install dependencies just to explore unless the user asked for that and the action is safe.

## Clarifying questions

Investigate discoverable facts first.

When a requirement/design decision remains, let `skills/requirements-and-design/SKILL.md` apply its one-question-at-a-time and confirmation rules.

For a purely factual blocker that cannot be discovered, ask at most one focused question when no safe assumption exists.

## Output shape

```text
Findings:
- ...

Constraints:
- ...

Feasible options (when relevant):
1. ...
2. ...

Requirement Brief:
- <included only if requirements-and-design was activated>

Recommendation:
- ...

Next route:
- <handoff | re-triage to implementation>
```

## Do not

- Do not make code changes during Exploration unless the user already asked for implementation and you re-route into a mode skill.
- Do not inspect unrelated areas just because they are interesting.
- Do not present guesses as verified facts.
- Do not duplicate a full design/confirmation process inside Exploration; load the dedicated support skill.
