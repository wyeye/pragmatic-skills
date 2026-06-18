---
schema: psp.skill/v1
name: using-pragmatic-skills
description: Start here for any repository or PSP workflow task and load only the next relevant skill.
kind: entry
version: 1.7.0
summary: Start here for any repository or PSP workflow task and load only the next relevant skill.
triggers:
- Any task involving code, files, tests, debugging, review, project decisions, or PSP workflow evaluation.
loads:
  direct:
    explicit_workflow_retrospective:
    - skills/workflow-retrospective/SKILL.md
  fallback:
  - skills/triage/SKILL.md
  conditional:
    completion:
    - skills/handoff/SKILL.md
    command_resolution:
    - skills/command-discovery/SKILL.md
    project_agents_md:
    - skills/project-agents-md/SKILL.md
outputs:
- direct retrospective route or selected primary mode
- next skill path
safety:
  approval_required: Only for safety-gated actions, never just to continue ordinary low-risk work.
activation:
  automatic: true
  entrypoint: true
  user_direct: false
  invoked_by:
  - AGENTS.md#start-rule
  routing_note: Users provide tasks; agents route from AGENTS.md through an explicit direct route or triage and phase triggers. Users do not manually invoke individual skills.
---
# Using Pragmatic Skills Pack

## User contract

Users do not invoke individual skills directly.

The user-facing contract is:

```text
User gives a normal task
  -> AGENTS.md starts this entry skill
  -> explicit post-task PSP retrospective? load workflow-retrospective directly
  -> otherwise load triage
  -> triage selects one primary mode
  -> the mode skill loads support skills only when phase triggers are reached
```

Do not ask the user which skill, mode, or support workflow to use unless the user is explicitly designing, debugging, or evaluating this skill pack.

Do not expose internal skill names as required user actions. You may mention them only when useful for transparency, debugging, or handoff.

Use this skill at the start of every repository task and every explicit PSP workflow-evaluation request.

This workflow is progressive and internally routed: load only the next relevant skill, not the entire skill pack, and never require the user to call skills by name.


## Host adapter resolution

Host-native skills and rule files are thin adapters. They exist so Claude Code, Codex, OpenCode, Gemini CLI, Copilot, Cursor, Hermes, and similar tools can enter the same workflow using their normal discovery mechanisms.

Regardless of the host adapter that activated the workflow, the internal source of truth is the repository-local `skills/` directory. Resolve support skills relative to the repository root, for example `skills/triage/SKILL.md`, unless a future package version explicitly says otherwise.

Users still do not invoke support skills directly. Host adapters only start the entry skill.

## Progressive loading rule

You must not read all skill files up front.

Start with the smallest applicable route:

1. Check whether the user explicitly requests a post-task PSP/workflow retrospective.
2. If yes, load only `skills/workflow-retrospective/SKILL.md` and skip triage unless the same request also asks to apply file changes.
3. Otherwise read `skills/triage/SKILL.md`.
4. Let triage load exactly one primary mode skill:
   - `skills/fast-patch/SKILL.md`
   - `skills/exploration/SKILL.md`
   - `skills/standard-change/SKILL.md`
   - `skills/strict-change/SKILL.md`
5. Load support skills by phase, not as a bundle.
6. Re-run triage if new evidence changes the task shape.

## Active-only post-task retrospective route

Before the default triage route, detect explicit user intent to evaluate PSP itself after a completed or recent task.

Examples include requests to review which skills triggered correctly, identify workflow friction, improve routing, or produce PSP iteration items and eval fixtures.

When this intent is present:

- Load `skills/workflow-retrospective/SKILL.md` directly.
- Do not load a primary implementation mode for analysis-only retrospective work.
- Do not run or offer the retrospective automatically at ordinary completion.
- If the user asks to apply the resulting improvements, finish the retrospective first and then load `skills/triage/SKILL.md` for implementation.

A request for a normal implementation summary alone is handled by `handoff`, not by this route.

## Metadata-first rule

Each `SKILL.md` starts with machine-readable frontmatter.

When your environment supports partial file reads, you may inspect frontmatter or `skills/MANIFEST.json` for routing hints before opening a skill body. Do not use metadata as a substitute for a skill body once that skill is activated.

## Universal command rule

This skill pack does not hardcode repository commands.

When a workflow needs install, test, lint, typecheck, build, or local-run commands and the exact command is not already known from explicit project instructions, load `skills/command-discovery/SKILL.md`.

Do not invent commands. If no command can be discovered, say so and use the strongest available alternative.


## Project AGENTS.md maintenance rule

AGENTS.md is both a host entry file and the best place for project-specific coding-agent instructions.

Active trigger: when the user asks to create, update, migrate, improve, or refactor `AGENTS.md` or repository agent instructions, load `skills/project-agents-md/SKILL.md`.

Passive trigger: during repository discovery, if you notice the current project has no `AGENTS.md`, or it has only the generic PSP managed block and no project-specific guidance, load `skills/project-agents-md/SKILL.md` for the passive prompt. Do not silently create or refactor `AGENTS.md` from passive detection; ask the user once whether they want it generated or improved.

Do not edit PSP-managed blocks in `AGENTS.md` manually. Use the installer/upgrade path for PSP block changes and use `project-agents-md` only for project-owned content outside managed blocks.

## Always-active principles

These principles apply even before support skills are loaded:

- Smallest sufficient workflow.
- No fake evidence.
- No fake subagents.
- No destructive actions without an explicit safety gate.
- Prefer project-defined commands over generic conventions.
- Escalate when risk or ambiguity increases.
- Downgrade only when the evidence shows a lighter mode is safe.
- Final answer must state what was verified and what was not.

## Re-triage rule

Return to `skills/triage/SKILL.md` when you discover:

- More files, packages, services, or systems are involved than expected.
- Behavior, API, data, auth, security, payment, deployment, dependency, or compatibility impact appears.
- Tests fail for unclear reasons.
- The user request is underspecified and assumptions would be risky.
- The diff becomes hard to review.
- Investigation shows the task is simpler than expected and can safely use a lighter mode.

## When to stop and ask

Ask at most one focused question when the answer would materially change the implementation and no safe default exists.

Do not ask for confirmation just to continue ordinary low-risk work.

## Completion

Before final response, load `skills/handoff/SKILL.md` unless no code/file work was performed and the answer is purely conversational.

Do not automatically load or offer `workflow-retrospective` after handoff. It is active-only and requires explicit user intent.
