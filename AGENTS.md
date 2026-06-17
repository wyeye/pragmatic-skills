<!-- PSP:BEGIN -->
# Pragmatic Skills Pack — Progressive Entry v1.5

This repository uses a progressive skill workflow. Do **not** preload the entire workflow.

## User-facing contract

Users only provide normal tasks. They do **not** need to invoke, choose, or know individual skills.

The agent must route internally:

```text
User task
  -> AGENTS.md or host-native entry adapter
  -> skills/using-pragmatic-skills/SKILL.md
  -> skills/triage/SKILL.md
  -> one primary mode skill
  -> support skills by phase trigger only
```

Do not ask the user which skill or mode to use unless the user is explicitly designing, debugging, or evaluating this skill system.

## Host adapter rule

Different coding agents discover instructions differently. PSP keeps one internal workflow in `skills/` and may install thin host adapters such as `.agents/skills/using-pragmatic-skills/SKILL.md`, `.claude/skills/psp-claude-entry/SKILL.md`, `CLAUDE.md`, `GEMINI.md`, or `.cursor/rules/pragmatic-skills-pack.mdc`.

Those adapters are only entry points. Once activated, always continue with the repository file:

```text
skills/using-pragmatic-skills/SKILL.md
```

## Start rule

For any task that may involve code, files, tests, project decisions, debugging, or review:

1. Read only `skills/using-pragmatic-skills/SKILL.md` as the entry skill.
2. Follow that file's routing instructions.
3. Load additional `skills/*/SKILL.md` files only when triage or phase triggers activate them.

## Non-negotiables

- Do not claim tests, builds, reviews, approvals, file changes, command discovery, or subagents happened unless they actually happened.
- Do not fabricate command output, tool calls, git state, user confirmations, or external facts.
- Prefer the smallest workflow that is sufficient for the task.
- Re-run triage when risk, ambiguity, blast radius, command impact, or implementation scope changes.
- Do not perform destructive, production-affecting, or hard-to-reverse actions without the relevant safety gate.
- Final responses must distinguish verified facts from unverified assumptions.

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
