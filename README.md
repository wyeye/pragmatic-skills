# Pragmatic Skills Pack

A pragmatic, phase-routed, evidence-first skill pack for coding agents.

Users describe tasks normally. Agents start from the entry skill, route explicit active-only intents directly when applicable, otherwise triage the task, choose one primary mode, and load support skills only when phase triggers are reached.

## User contract

Users do not call individual skills. They only ask for work normally.

The agent starts from `AGENTS.md`, loads `skills/using-pragmatic-skills/SKILL.md`, uses an explicit active-only direct route when applicable, otherwise routes through `triage`, and then loads mode/support skills automatically by phase trigger.

Internal skill names are implementation details, not user commands.

## Install or upgrade with one command

From the target repository:

```bash
sh /path/to/pragmatic-skills-pack/install.sh
```

Or from anywhere:

```bash
sh /path/to/pragmatic-skills-pack/install.sh --target /path/to/repo
```

The same command is safe to re-run. It installs PSP when absent and upgrades PSP when an existing installation is detected.

Check the unpacked package:

```bash
sh /path/to/pragmatic-skills-pack/install.sh --check
```

Verify an installed repository:

```bash
sh /path/to/pragmatic-skills-pack/install.sh --verify --target /path/to/repo
```

After installation, a verifier is copied into the target repository:

```bash
python3 .psp/bin/psp.py verify --target .
```

`install.sh` is the public entrypoint. It delegates to the dependency-free implementation in `tools/psp.py`.

## Agent-based install

If you want an agent to install PSP, give it the unpacked package and ask:

```text
Install Pragmatic Skills Pack into the current repository using the package's install.sh. Verify the installation afterward. Preserve existing AGENTS.md content outside the PSP managed block and report any conflicts.
```

Agent-specific guidance is in `AGENT-INSTALL.md` and `reference/AGENT-INSTALL.md`.

## Upgrade safety

The installer manages `skills/`, `reference/`, and the PSP block in `AGENTS.md` with `.psp/install.json` hashes. It updates only unchanged managed files, backs up replaced files, and reports conflicts instead of overwriting user edits. It does not overwrite the project README. See `reference/INSTALL-UPGRADE.md`.

## Why this shape

A monolithic workflow makes every task pay the context cost of every rule. This pack keeps the always-loaded entry small, then progressively exposes only the relevant rules:

```text
AGENTS.md
  -> skills/using-pragmatic-skills/SKILL.md
       -> skills/triage/SKILL.md
            -> one mode skill: fast-patch | exploration | standard-change | strict-change
                 -> requirements-and-design when its phase trigger applies
                 -> other support skills only when the current phase triggers them
```


## Requirements clarification and design

PSP includes `skills/requirements-and-design/SKILL.md` for brainstorming, requirement clarification, acceptance criteria, design comparison, and confirmation before planning or implementation.

- Users ask normally; they do not invoke the skill name.
- Triage first selects Exploration, Standard Change, or Strict Change. The selected mode activates the skill only when the requirements phase is needed.
- Exploration discovers repository facts; Requirements and Design settles intended behavior, scope, non-goals, acceptance criteria, and design choices.
- It is skipped for tiny, fully specified, low-risk work.
- It asks one decision-critical question at a time and can continue with documented safe assumptions only for low-risk, reversible defaults.
- Its confirmation state is one of `confirmed`, `conditionally confirmed`, `safe assumptions used`, or `blocked on user decision`. Implementation does not proceed from the blocked state.
- Requirement confirmation is separate from safety approval.

The resulting Requirement Brief flows into planning, TDD, verification, review, and handoff. Detailed rules and eval fixtures are in `reference/REQUIREMENTS-AND-DESIGN.md`.

## Project AGENTS.md generation and refactoring

PSP now includes `skills/project-agents-md/SKILL.md` for maintaining the current repository's project-specific `AGENTS.md`.

- Active trigger: the user asks to create, update, migrate, improve, or refactor AGENTS.md or agent instructions.
- Passive trigger: during repository discovery, the agent notices there is no AGENTS.md, or only a generic PSP block with no project-specific guidance.
- Passive trigger asks the user before writing; it never silently creates/refactors AGENTS.md.
- Existing PSP-managed blocks are preserved and updated only by the installer.

## Active-only workflow retrospective

PSP includes `skills/workflow-retrospective/SKILL.md` for learning from a completed or recent task and improving the skill pack itself.

- It is triggered only when the user explicitly asks to retrospect on PSP, its routing, its skills, or workflow friction.
- It is never run or routinely offered after ordinary task completion.
- It uses observable evidence only and distinguishes observed facts, inferences, unknowns, and evidence gaps.
- It produces prioritized findings with exact target files and an eval fixture for every material change.
- It is read-only by default. If the user asks to apply the findings, the workflow completes the retrospective first and then re-enters triage for implementation.
- A normal implementation summary still belongs to `handoff`.

Optional saved records use `psp.retrospective/v1` and may be written to `.psp/retrospectives/` only when the user explicitly asks. See `reference/WORKFLOW-RETROSPECTIVE.md`.

## Universal commands

This pack does not ask you to fill fixed commands in the generic `AGENTS.md`.

When a task needs test/lint/typecheck/build/install/run-local commands, the workflow loads `skills/command-discovery/SKILL.md` and resolves commands from the actual repository: docs, package scripts, task runners, CI files, config files, lockfiles, and ecosystem markers.

Project-specific overrides are optional. Use `.psp/project-profile.md` in a concrete repository when you want to pin known commands or extra strict triggers. See `reference/PROJECT-PROFILE.template.md`.

## Machine-readable skills

Every `SKILL.md` starts with YAML frontmatter, including automatic activation metadata:

```yaml
schema: psp.skill/v1
name: standard-change
kind: mode
version: 1.8.0
summary: ...
triggers: [...]
loads: ...
activation: ...
outputs: [...]
```

A generated index is available at `skills/MANIFEST.json` for tools that want to inspect skill metadata without reading every skill body.

## Structure

```text
AGENTS.md
AGENT-INSTALL.md
README.md
README.zh.md
TREE.txt
install.sh
verify.sh
tools/
  README.md
  psp.py
skills/
  MANIFEST.json
  using-pragmatic-skills/SKILL.md
  triage/SKILL.md
  fast-patch/SKILL.md
  exploration/SKILL.md
  standard-change/SKILL.md
  strict-change/SKILL.md
  command-discovery/SKILL.md
  project-agents-md/SKILL.md
  requirements-and-design/SKILL.md
  workflow-retrospective/SKILL.md
  safety-gates/SKILL.md
  writing-plans/SKILL.md
  tdd/SKILL.md
  evidence-driven-execution/SKILL.md
  verification/SKILL.md
  review/SKILL.md
  delegation/SKILL.md
  worktree/SKILL.md
  handoff/SKILL.md
reference/
  AGENT-INSTALL.md
  AGENTS-MD-MAINTENANCE.md
  INSTALL-UPGRADE.md
  MODE-MATRIX.md
  PROJECT-PROFILE.template.md
  REQUIREMENTS-AND-DESIGN.md
  SKILL-METADATA-SCHEMA.md
  USER-CONTRACT.md
  WORKFLOW-RETROSPECTIVE.md
```

## Version

Current package version: `1.8.0`.

## Multi-agent installation

PSP is shell-first and host-adapter aware.

```bash
# From your repository root
sh /path/to/pragmatic-skills-pack/install.sh

# Install every supported adapter
sh /path/to/pragmatic-skills-pack/install.sh --hosts all

# Install only selected adapters
sh /path/to/pragmatic-skills-pack/install.sh --hosts claude,codex,opencode
```

Default `--hosts all` installs `AGENTS.md`, the `.agents/skills/using-pragmatic-skills` native entry adapter, and thin adapters for Claude Code, OpenCode, Gemini CLI, GitHub Copilot, Cursor, and other supported hosts. Use `--hosts auto` if you only want adapters detected from existing project files; use `--no-host-adapters` for canonical PSP only.

Native host adapters are thin entry points. The internal workflow remains in `skills/`, and users still only describe normal tasks.


## v1.8 changes

- Added `skills/requirements-and-design/SKILL.md` for lightweight brainstorming, requirement clarification, design convergence, acceptance criteria, and explicit confirmation states.
- Separated repository fact-finding (`exploration`) from product/design decisions (`requirements-and-design`).
- Added a requirements phase to Standard and Strict Change while preserving Fast Patch for clear low-risk work.
- Made writing plans consume the confirmed Requirement Brief and stop when a material user decision is unresolved.
- Connected acceptance criteria to TDD, verification, review, and handoff.
- Added one-question-at-a-time rules, safe-default boundaries, change-control rules, and ten eval fixtures in `reference/REQUIREMENTS-AND-DESIGN.md`.
