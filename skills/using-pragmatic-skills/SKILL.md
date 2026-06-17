---
schema: psp.skill/v1
name: using-pragmatic-skills
kind: entry
version: 1.2.0
summary: Start here for any development task and load only the next relevant skill.
triggers:
- Any task involving code, files, tests, debugging, review, or project decisions.
loads:
  immediate:
  - skills/triage/SKILL.md
  conditional:
    completion:
    - skills/handoff/SKILL.md
    command_resolution:
    - skills/command-discovery/SKILL.md
outputs:
- selected primary mode
- next skill path
safety:
  approval_required: Only for safety-gated actions, never just to continue ordinary low-risk
    work.
activation:
  automatic: true
  entrypoint: true
  user_direct: false
user_facing: entrypoint_only
routing:
  user_exposed: false
  user_invocation_required: false
  activation: entrypoint
  invoked_by:
  - AGENTS.md start rule
  contract: Entry skill loaded by AGENTS.md; users provide tasks and do not invoke internal
    skills manually.
---
# Using Pragmatic Skills Pack

## User contract

Users do not invoke individual skills directly.

The user-facing contract is:

```text
User gives a normal task
  -> AGENTS.md starts this entry skill
  -> this skill loads triage
  -> triage selects one primary mode
  -> the mode skill loads support skills only when phase triggers are reached
```

Do not ask the user which skill, mode, or support workflow to use unless the user is explicitly designing, debugging, or evaluating this skill pack.

Do not expose internal skill names as required user actions. You may mention them only when useful for transparency, debugging, or handoff.

Use this skill at the start of every development task.

This workflow is progressive and internally routed: load only the next relevant skill, not the entire skill pack, and never require the user to call skills by name.

## Progressive loading rule

You must not read all skill files up front.

Start with:

1. Read `skills/triage/SKILL.md`.
2. Classify the task.
3. Load exactly one primary mode skill:
   - `skills/fast-patch/SKILL.md`
   - `skills/exploration/SKILL.md`
   - `skills/standard-change/SKILL.md`
   - `skills/strict-change/SKILL.md`
4. Load support skills by phase, not as a bundle.
5. Re-run triage if new evidence changes the task shape.

## Metadata-first rule

Each `SKILL.md` starts with machine-readable frontmatter.

When your environment supports partial file reads, you may inspect frontmatter or `skills/MANIFEST.json` for routing hints before opening a skill body. Do not use metadata as a substitute for a skill body once that skill is activated.

## Universal command rule

This skill pack does not hardcode repository commands.

When a workflow needs install, test, lint, typecheck, build, or local-run commands and the exact command is not already known from explicit project instructions, load `skills/command-discovery/SKILL.md`.

Do not invent commands. If no command can be discovered, say so and use the strongest available alternative.

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
