# Pragmatic Skills Pack v1.2

A pragmatic, phase-routed, evidence-first skill pack for coding agents.

Users describe tasks normally. The agent starts from a thin entry rule, triages the task, chooses one primary mode, and loads support skills only when phase triggers are reached.

## Identity

```text
Project name: Pragmatic Skills Pack
Short name: PSP
Repo name: pragmatic-skills
Package id: pragmatic-skills-pack
Manifest id: psp
Version: 1.2.0
Entry skill: skills/using-pragmatic-skills/SKILL.md
```

## Why this shape

A monolithic workflow makes every task pay the context cost of every rule. PSP keeps the always-loaded entry small, then progressively exposes only the relevant rules:

```text
AGENTS.md
  -> skills/using-pragmatic-skills/SKILL.md
       -> skills/triage/SKILL.md
            -> one mode skill: fast-patch | exploration | standard-change | strict-change
                 -> support skills only when the current phase triggers them
```

## User contract

Users do not manually select skills.

They should simply ask for the work they want done. The agent/runtime is responsible for routing internally from the entry skill.

Do not ask users to choose `tdd`, `verification`, `review`, `strict-change`, `command-discovery`, or any other internal skill unless they are explicitly designing, debugging, or evaluating the skill system itself.

## Universal commands

The generic pack does not contain fixed placeholders such as `Install`, `Test`, `Lint`, `Typecheck`, `Build`, or `Run locally`.

When a workflow needs a command, it loads `skills/command-discovery/SKILL.md` and resolves commands from the actual repository: user instructions, docs, package scripts, task runners, CI files, config files, lockfiles, and ecosystem markers.

Install and dependency-mutating commands are treated carefully: they are not run automatically just because they exist.

## Machine-readable skills

Every `SKILL.md` starts with YAML frontmatter:

```yaml
schema: psp.skill/v1
name: standard-change
kind: mode
version: 1.2.0
summary: ...
triggers: [...]
loads: ...
outputs: [...]
routing:
  user_exposed: false
  user_invocation_required: false
  activation: router-selected-mode
  invoked_by:
    - skills/triage/SKILL.md
  contract: Selected internally; users do not invoke this skill directly.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
```

A generated index is available at `skills/MANIFEST.json` for tools that want to inspect skill metadata without reading every skill body.

## Structure

```text
AGENTS.md
README.md
README.zh.md
TREE.txt
skills/
  MANIFEST.json
  using-pragmatic-skills/SKILL.md
  triage/SKILL.md
  fast-patch/SKILL.md
  exploration/SKILL.md
  standard-change/SKILL.md
  strict-change/SKILL.md
  command-discovery/SKILL.md
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
  MODE-MATRIX.md
  SKILL-METADATA-SCHEMA.md
  USER-CONTRACT.md
  PROJECT-PROFILE.template.md
```

## Install

Copy `AGENTS.md` and `skills/` into your repository root:

```bash
cp -R pragmatic-skills-pack/AGENTS.md pragmatic-skills-pack/skills .
```

Optional reference files may also be copied if you want local documentation:

```bash
cp -R pragmatic-skills-pack/reference .
```

Then tell your coding agent once:

```text
Follow AGENTS.md. Use progressive skill loading. Do not preload all skills.
Route internally from the entry skill; do not ask the user which skill to invoke.
```

## Customization

Most projects should customize only `.psp/project-profile.md` or a local section in `AGENTS.md`.

Good project-local overrides include exact commands, generated files, no-edit zones, strict triggers, dependency policy, and deployment/approval policy.

## v1.2 changes

- Renamed the project to Pragmatic Skills Pack.
- Renamed the entry skill to `skills/using-pragmatic-skills/SKILL.md`.
- Updated manifest identity, README files, tree, user contract, schema examples, and internal paths.
- Removed remaining generic command placeholders from the entry file.
- Added stronger machine-readable activation metadata consistently across skills.

## License / attribution note

PSP is a standalone pragmatic skill pack design. It is not tied to a specific agent host or editor runtime.
