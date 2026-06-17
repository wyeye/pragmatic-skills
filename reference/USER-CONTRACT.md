# User Contract

This file is reference material for integrating Pragmatic Skills Pack into agents, editors, or runtimes.

## Contract

Users do not invoke individual skills directly.

The user only provides the task. The agent/runtime is responsible for routing:

```text
User task
  -> AGENTS.md
  -> skills/using-pragmatic-skills/SKILL.md
  -> skills/triage/SKILL.md
  -> one primary mode skill
  -> support skills by phase trigger
```

## Do

- Start every development task from the entry skill named in `AGENTS.md`.
- Use `triage` to pick the smallest safe mode.
- Load support skills only when the current phase or condition activates them.
- Re-run triage when risk, ambiguity, scope, or command impact changes.
- Report final evidence through `handoff`.

## Do not

- Ask the user to choose `fast-patch`, `standard-change`, `strict-change`, `tdd`, `verification`, or other internal skills.
- Preload all skill bodies up front.
- Treat metadata as a replacement for an activated skill body.
- Claim a skill, command, review, subagent, approval, or test happened without evidence.

## When skill names may be shown

Skill names may be mentioned when the user is designing, debugging, evaluating, or customizing the workflow. They should not be presented as required user actions during normal coding tasks.


## Project AGENTS.md contract

Users do not need to manually invoke the AGENTS.md maintenance skill.

The workflow may route to `skills/project-agents-md/SKILL.md` when the user explicitly asks to create, update, migrate, improve, or refactor repository agent instructions.

The workflow may also passively detect that the current repository lacks a project-specific `AGENTS.md`. In that case the agent should ask once whether the user wants one generated. Passive detection never authorizes silent file creation or major refactoring.

PSP-managed blocks are maintained by the installer. Project-specific AGENTS.md content belongs outside managed blocks.

## Installation contract

Users of a concrete repository should not manually copy individual skill files when an installer is available. Use the shell installer:

```bash
sh /path/to/pragmatic-skills-pack/install.sh --target /path/to/repo
```

The same command installs when absent and upgrades when present. The installer preserves project-owned `AGENTS.md` content and `.psp/project-profile.md`.
