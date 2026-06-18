# User Contract

This file is reference material for integrating Pragmatic Skills Pack into agents, editors, or runtimes.

## Contract

Users do not invoke individual skills directly.

The user only provides the task. The agent/runtime is responsible for routing:

```text
User task
  -> AGENTS.md
  -> skills/using-pragmatic-skills/SKILL.md
  -> explicit post-task PSP retrospective? workflow-retrospective
  -> otherwise skills/triage/SKILL.md
  -> one primary mode skill
  -> requirements/design when its phase trigger applies
  -> other support skills by phase trigger
```

## Do

- Start every development task from the entry skill named in `AGENTS.md`.
- Route an explicit post-task PSP retrospective directly to `workflow-retrospective`; otherwise use `triage` to pick the smallest safe mode.
- Let the selected mode activate `requirements-and-design` when brainstorming, scope, acceptance, or material design decisions need resolution.
- Load support skills only when the current phase or condition activates them.
- Re-run triage when risk, requirements, ambiguity, scope, or command impact changes.
- Report final evidence through `handoff`.

## Do not

- Ask the user to choose `fast-patch`, `standard-change`, `strict-change`, `requirements-and-design`, `tdd`, `verification`, or other internal skills.
- Preload all skill bodies up front.
- Force a Requirement Brief onto tiny, fully specified work.
- Treat metadata as a replacement for an activated skill body.
- Claim a skill, command, review, subagent, approval, confirmation, or test happened without evidence.

## When skill names may be shown

Skill names may be mentioned when the user is designing, debugging, evaluating, or customizing the workflow. They should not be presented as required user actions during normal coding tasks.

## Requirements and design contract

Users may ask in normal language to brainstorm, clarify requirements, compare options, define acceptance criteria, or confirm a design. They do not need to know the internal skill name.

The workflow routes through triage first:

- Exploration for analysis/design-only work.
- Standard Change for implementation without Strict triggers.
- Strict Change for security, data, public compatibility, payments, deployment, or other high-risk work.

The mode then activates `skills/requirements-and-design/SKILL.md` at the appropriate phase.

The skill must:

- Inspect discoverable project facts before asking the user.
- Ask one decision-critical question at a time.
- Produce a concise Requirement Brief with observable acceptance criteria.
- Distinguish facts, assumptions, and open questions.
- Use exactly one confirmation state: `confirmed`, `conditionally confirmed`, `safe assumptions used`, or `blocked on user decision`.
- Stop before implementation when blocked.
- Avoid ceremonial confirmation for low-risk, reversible defaults.

Requirement confirmation is not safety approval. Gated actions still require `safety-gates` approval.

## Workflow retrospective contract

Users may explicitly ask in normal language to review a completed or recent task in order to improve PSP. They do not need to know the internal skill name.

The workflow routes that request to `skills/workflow-retrospective/SKILL.md` before normal triage.

- The retrospective is active-only.
- It is not run or offered automatically after ordinary task completion.
- It uses observable evidence and labels inferences and gaps.
- It does not claim access to hidden reasoning or unrecorded runtime state.
- It is read-only by default.
- If the user asks to apply improvements, the retrospective completes first, then implementation re-enters triage.

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
