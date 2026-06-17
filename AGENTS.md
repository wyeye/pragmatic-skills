# Pragmatic Skills Pack — Progressive Entry

This repository uses Pragmatic Skills Pack, a progressive, phase-routed, evidence-first skill pack for coding agents.

Users provide normal tasks. They do **not** need to invoke, choose, or know individual skills.

## Start rule

For any task that may involve code, files, tests, debugging, review, repository decisions, or project commands:

1. Read only `skills/using-pragmatic-skills/SKILL.md`.
2. Follow that entry skill's routing instructions.
3. Load `skills/triage/SKILL.md` next.
4. Select one primary mode through triage.
5. Load support skills only when their phase trigger or condition is reached.

Do **not** preload every skill body up front.

## User-facing contract

- The user states the task.
- The agent routes internally from entry -> triage -> one mode -> support skills by phase trigger.
- Do not ask the user which skill or mode to use unless the user is explicitly designing, debugging, or evaluating this skill system.
- Internal skill names may be mentioned for transparency, but they must not become required user actions.

## Non-negotiables

- Do not claim tests, builds, reviews, approvals, subagents, file edits, or command results happened unless they actually happened.
- Do not fabricate command output, tool calls, diffs, user confirmations, or approval.
- Prefer the smallest workflow that is sufficient for the task.
- Escalate when risk, ambiguity, scope, or blast radius increases.
- Final responses must distinguish verified facts from unverified assumptions.

## Universal command resolution

This generic pack does not hardcode project commands.

When a task needs install, test, lint, typecheck, build, or local-run commands and the exact command is not already known from explicit project instructions, load `skills/command-discovery/SKILL.md`.

Command rules:

- Prefer project-defined commands over ecosystem guesses.
- Do not invent commands.
- Do not run install or dependency-mutating commands automatically just because they exist.
- If no command can be discovered, say so and use the strongest available alternative.
- Record command, cwd, source, confidence, and result when reporting verification.

## Optional project profile

A repository may add local overrides in `.psp/project-profile.md` or a local section below this file. Project profiles are optional; the generic skill pack must work without fixed command placeholders.

Common local overrides:

- exact test/lint/typecheck/build commands
- generated files or directories
- files the agent must not edit automatically
- project-specific Strict Change triggers
- dependency, commit, branch, deployment, or approval policies
