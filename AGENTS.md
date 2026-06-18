<!-- PSP:BEGIN -->
# Pragmatic Skills Pack — Progressive Entry v1.8

This repository uses a progressive skill workflow. Do **not** preload the entire workflow.

## User-facing contract

Users only provide normal tasks. They do **not** need to invoke, choose, or know individual skills.

The agent must route internally:

```text
User task
  -> AGENTS.md or host-native entry adapter
  -> skills/using-pragmatic-skills/SKILL.md
  -> explicit post-task PSP retrospective? workflow-retrospective
  -> otherwise skills/triage/SKILL.md
  -> one primary mode skill
  -> requirements/design when its phase trigger applies
  -> other support skills by phase trigger only
```

Do not ask the user which skill or mode to use unless the user is explicitly designing, debugging, or evaluating this skill system.

## Host adapter rule

Different coding agents discover instructions differently. PSP keeps one internal workflow in `skills/` and may install thin host adapters such as `.agents/skills/using-pragmatic-skills/SKILL.md`, `.claude/skills/psp-claude-entry/SKILL.md`, `CLAUDE.md`, `GEMINI.md`, or `.cursor/rules/pragmatic-skills-pack.mdc`.

Those adapters are only entry points. Once activated, always continue with the repository file:

```text
skills/using-pragmatic-skills/SKILL.md
```

## Start rule

For any task that may involve code, files, tests, project decisions, debugging, review, or PSP workflow evaluation:

1. Read only `skills/using-pragmatic-skills/SKILL.md` as the entry skill.
2. Follow that file's routing instructions.
3. Load additional `skills/*/SKILL.md` files only when an explicit direct trigger, triage, or a phase trigger activates them.

## Non-negotiables

- Do not claim tests, builds, reviews, approvals, file changes, command discovery, or subagents happened unless they actually happened.
- Do not fabricate command output, tool calls, git state, user confirmations, or external facts.
- Prefer the smallest workflow that is sufficient for the task.
- Re-run triage when risk, ambiguity, requirements, blast radius, command impact, or implementation scope changes.
- Do not perform destructive, production-affecting, or hard-to-reverse actions without the relevant safety gate.
- Final responses must distinguish verified facts from unverified assumptions.


## Project AGENTS.md maintenance

PSP may help maintain the current repository's project-specific `AGENTS.md`.

- Active trigger: if the user asks to create, update, migrate, improve, or refactor `AGENTS.md` or agent instructions, load `skills/project-agents-md/SKILL.md`.
- Passive trigger: if repository discovery shows there is no `AGENTS.md`, or `AGENTS.md` has only generic PSP entry content and no project-specific guidance, load `skills/project-agents-md/SKILL.md` and ask the user once whether to generate or improve it.
- Do not silently create/refactor `AGENTS.md` from passive detection.
- Do not manually edit PSP-managed blocks; project-specific content belongs outside managed blocks.

## Requirements clarification and design

PSP may automatically load `skills/requirements-and-design/SKILL.md` after triage selects a mode.

- Trigger it when the user asks to brainstorm, clarify requirements, compare designs, define acceptance criteria, or confirm a design before coding.
- Also trigger it when a feature/change lacks clear scope or success criteria, materially different designs exist, or planning would depend on risky assumptions.
- Do not trigger it for tiny, fully specified, low-risk work merely to create ceremony.
- Investigate repository facts through `exploration` before asking the user questions that the project can answer.
- Ask one decision-critical question at a time.
- Do not implement while its confirmation state is `blocked on user decision`.
- Requirement/design confirmation does not replace safety approval for gated actions.

## Active-only workflow retrospective

PSP includes an explicit post-task learning loop for improving the skill pack itself.

- Active trigger only: when the user explicitly asks to retrospect on a completed/recent task, evaluate PSP routing, identify skill friction, or turn the task into workflow improvements/eval cases, load `skills/workflow-retrospective/SKILL.md` directly from the entry skill.
- Do not run it automatically after ordinary task completion and do not routinely ask the user whether they want one.
- A normal implementation summary belongs to `handoff`; the retrospective evaluates the workflow itself.
- Retrospective analysis is read-only by default. If the user also asks to apply improvements, complete the retrospective first, then re-enter triage for the file changes.
- Use observable evidence only; do not claim access to hidden reasoning or unrecorded runtime state.

## Universal command resolution

Do **not** hardcode project commands in this generic entry file.

When a task needs install, test, lint, typecheck, build, or local-run commands:

1. Prefer explicit user instructions and project-local documentation.
2. Otherwise load `skills/command-discovery/SKILL.md`.
3. Resolve commands from the current repository's scripts, configs, task runners, CI files, and ecosystem markers.
4. Record each command's source and working directory before reporting it as evidence.
5. If no command is discoverable, say so. Do not invent one.

Project-specific overrides are optional. A repository may add a local section below, or create `.psp/project-profile.md`, with known commands and extra strict triggers. See `reference/PROJECT-PROFILE.template.md`.

## Generic strict triggers

Use Strict Change when work involves:

- Auth / permissions / security / secrets / privacy.
- Payment / billing / quota / subscription behavior.
- Database schema, migrations, destructive operations, or data repair.
- Public API, SDK, protocol, schema, or compatibility changes.
- Deployment, infrastructure, CI/CD, release, rollback, or production operations.
- Dependency upgrades with security, lockfile, runtime, or compatibility impact.
- Large refactors, cross-package changes, or uncertain blast radius.

## Optional local overrides

Concrete repositories may append local rules here, but the generic pack should remain command-free and project-agnostic.
<!-- PSP:END -->
