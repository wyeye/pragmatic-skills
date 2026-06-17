---
schema: psp.skill/v1
name: project-agents-md
description: Create, update, or refactor project-specific AGENTS.md instructions while preserving PSP and other managed blocks.
kind: support
version: 1.6.0
summary: Maintain the current repository's project-specific AGENTS.md, including generation, cleanup, refactoring, and evidence-based command sections.
triggers:
- User explicitly asks to create, write, generate, update, improve, migrate, or refactor AGENTS.md or repository agent instructions.
- Passive detection finds no AGENTS.md in the current repository and a coding agent workflow is being used.
- Passive detection finds AGENTS.md exists but contains only generic PSP-managed content and no project-specific guidance.
- Existing AGENTS.md is stale, duplicated, contradictory, hard to scan, missing command evidence, or unsafe to use as-is.
loads:
  conditional:
    project_context:
    - skills/exploration/SKILL.md
    command_evidence:
    - skills/command-discovery/SKILL.md
    editing:
    - skills/evidence-driven-execution/SKILL.md
    verification:
    - skills/verification/SKILL.md
    review:
    - skills/review/SKILL.md
    completion:
    - skills/handoff/SKILL.md
outputs:
- AGENTS.md create/update/refactor plan or patch
- preserved managed-block inventory
- project command evidence with sources
- final changed/proposed/verified/not-verified summary
safety:
  approval_required: Passive generation or major refactor requires explicit user confirmation before writing.
  requires_approval_before:
  - Creating AGENTS.md only because it was passively missing.
  - Removing or materially changing existing project-owned constraints.
  - Changing instructions that affect production, deployment, secrets, destructive operations, or safety gates.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/using-pragmatic-skills/SKILL.md#loads.conditional.project_agents_md
  - skills/standard-change/SKILL.md#loads.phased.project_instructions
  - skills/exploration/SKILL.md#loads.conditional.project_instructions
  - workflow#passive-agents-md-detection
  active:
  - User asks for AGENTS.md generation, update, cleanup, migration, or refactor.
  passive:
  - Current repository has no AGENTS.md.
  - Current repository has AGENTS.md but it is PSP-only or lacks project-specific content.
  passive_requires_confirmation: true
  routing_note: Users provide normal tasks. The agent may route here automatically, but passive writes require asking the user first.
---
# Project AGENTS.md Maintenance

## Internal activation

This is a support skill for maintaining the **current repository's** `AGENTS.md`.

It is not the PSP package entry file. It creates, updates, or refactors project-specific agent instructions that live alongside the PSP managed block.

Users do not need to call this skill by name. It is activated either by an explicit AGENTS.md task or by passive repository-instruction detection.

## What this skill owns

This skill owns project-specific guidance such as:

- Repository purpose and architecture map.
- Important paths and ownership boundaries.
- Project-defined install/test/lint/typecheck/build/run commands.
- Validation expectations and command sources.
- Local coding conventions.
- Generated files, vendored files, and do-not-edit paths.
- Project-specific Strict Change triggers.
- Secrets, environment, deployment, and data handling cautions.
- Known review requirements and handoff expectations.

It does **not** own PSP installer-managed blocks.

## Managed block rules

Never edit these blocks manually:

- `<!-- PSP:BEGIN -->` ... `<!-- PSP:END -->`
- `<!-- PSP:CLAUDE:BEGIN -->` ... `<!-- PSP:CLAUDE:END -->`
- `<!-- PSP:GEMINI:BEGIN -->` ... `<!-- PSP:GEMINI:END -->`
- `<!-- PSP:COPILOT:BEGIN -->` ... `<!-- PSP:COPILOT:END -->`
- Any other clearly tool-managed block unless the user explicitly asks to modify that tool's block.

If a PSP block is missing or stale, recommend the installer/upgrade path rather than hand-editing the block:

```bash
sh /path/to/pragmatic-skills-pack/install.sh --target <repo>
```

Project-owned AGENTS.md content should be outside managed blocks.

## Active trigger

Use this skill immediately when the user asks for any of these:

- Create or generate `AGENTS.md`.
- Improve, update, clean up, or refactor `AGENTS.md`.
- Migrate rules from `CLAUDE.md`, `GEMINI.md`, Cursor rules, Copilot instructions, or other agent docs into `AGENTS.md`.
- Add project-specific agent instructions.
- Make the repository easier for coding agents to work in.

An explicit active request is permission to edit low-risk project instruction content, but not permission to remove safety constraints, change production/deployment policy, or overwrite managed blocks.

## Passive trigger

During repository discovery, if you observe that the current repository has no `AGENTS.md`, ask once:

```text
I do not see a project-specific AGENTS.md for this repository. Would you like me to generate one from the current project evidence?
```

If `AGENTS.md` exists but appears to contain only PSP/generic managed content and no project-specific guidance, ask once:

```text
AGENTS.md exists, but I only see generic PSP entry instructions and no project-specific guidance. Would you like me to add a project-specific section?
```

Passive trigger rules:

- Do not silently create or refactor `AGENTS.md` from a passive observation.
- Do not block the user's current task unless the missing instructions create real ambiguity or risk.
- If the user declines, continue the current task and do not repeat the prompt in the same conversation unless circumstances materially change.
- If the user accepts, proceed with the active workflow below.

## Repository evidence to inspect

Inspect only relevant local evidence before drafting:

- Existing `AGENTS.md` and managed block locations.
- `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/`, `.opencode/`, and other agent instruction files.
- `README*`, `CONTRIBUTING*`, `docs/`, architecture notes, package READMEs.
- `.psp/project-profile.md` if present.
- Package/workspace/config files such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Makefile`, `justfile`, `Taskfile*`, CI workflows, and lockfiles.
- Existing tests, generated-code markers, schema/migration directories, and deployment/infrastructure files.

Load `skills/exploration/SKILL.md` if the project structure or expected instructions are unclear.

Load `skills/command-discovery/SKILL.md` before writing command sections unless exact commands are already known from explicit project instructions.

## Creation workflow

When creating `AGENTS.md` or adding a project-specific section:

1. Identify the repository root and instruction files.
2. Preserve or insert the PSP managed block through the installer when PSP is installed.
3. Collect project facts from local evidence only.
4. Discover commands and record their source/cwd/confidence.
5. Draft concise project-owned sections outside managed blocks.
6. Include unknowns explicitly instead of guessing.
7. Write the smallest useful `AGENTS.md` change.
8. Review the result for contradictions, stale commands, and unsafe permissions.
9. Handoff with changed files, evidence used, and unverified gaps.

Recommended structure:

```md
# Project Agent Instructions

<!-- PSP:BEGIN -->
... installer-managed PSP entry block ...
<!-- PSP:END -->

## Project profile
- Purpose:
- Main languages/frameworks:
- Important paths:

## Commands
- Install: <command or "not discovered">  # source/cwd
- Test: <command or "not discovered">     # source/cwd
- Lint: <command or "not discovered">     # source/cwd
- Typecheck: <command or "not discovered"># source/cwd
- Build: <command or "not discovered">    # source/cwd
- Run locally: <command or "not discovered"># source/cwd

## Working rules
- Scope control:
- Generated/do-not-edit paths:
- Secrets/env cautions:
- Project-specific Strict triggers:

## Verification expectations
- Fast checks:
- Broader checks:
- What to report if checks cannot run:
```

Use only sections that are supported by evidence and useful for this project.

## Refactor workflow for existing AGENTS.md

When refactoring an existing `AGENTS.md`:

1. Inventory blocks:
   - PSP-managed blocks.
   - Other tool-managed blocks.
   - Project-owned sections.
2. Preserve managed blocks exactly unless the user is explicitly asking to update that managed block through the proper tool.
3. Identify duplicate, stale, conflicting, or unverifiable instructions.
4. Keep safety constraints unless they are clearly obsolete and the user confirms removal.
5. Normalize the document around stable project facts:
   - Project profile.
   - Commands with sources.
   - Path rules.
   - Validation expectations.
   - Strict triggers.
6. Avoid expanding AGENTS.md into a long policy manual. Link to project docs when possible.
7. For major rewrites, produce a short plan or patch summary before writing.
8. After editing, review the final file for contradictions and managed-block damage.

## Command section rules

Commands must be evidence-based.

Each command entry should include:

```text
Command: <exact command>
Cwd: <directory>
Source: <user | project docs | package script | config | CI | convention>
Confidence: high | medium | low
Run policy: safe to run | ask first | do not run automatically
```

Do not invent missing commands. Write `not discovered` or omit the section if discovery fails.

Install commands are not automatically safe. Follow `skills/command-discovery/SKILL.md` install policy.

## Safety and approval rules

Ask before writing when:

- The trigger was passive.
- You would remove or materially change existing constraints.
- You would change instructions about production, deployment, data, secrets, auth, billing, dependencies, or destructive actions.
- You would overwrite content outside PSP-managed blocks that appears user-authored and important.

You may proceed without another confirmation when:

- The user explicitly asked to create/update/refactor `AGENTS.md`.
- The edit only adds evidence-backed project guidance.
- Managed blocks are preserved.
- No safety constraints are weakened.

## Verification

After editing:

- Confirm `AGENTS.md` exists.
- Confirm PSP managed block markers are preserved if they existed before.
- Confirm no other managed blocks were damaged.
- Confirm referenced skill paths still exist if PSP is installed.
- Confirm command entries have sources or are marked as not discovered.
- Prefer static validation over running project tests unless the user requested a broader repo check.

Load `skills/verification/SKILL.md` if executable checks or PSP installer verification are needed.

## Review checklist

Before completion, load `skills/review/SKILL.md` for non-trivial edits and check:

- Did we preserve managed blocks?
- Did we avoid invented project facts?
- Are commands sourced?
- Are safety constraints preserved or explicitly approved for change?
- Is the resulting AGENTS.md shorter and clearer than before?
- Are unknowns reported as unknowns?

## Handoff

Load `skills/handoff/SKILL.md` and report:

```text
Changed:
- AGENTS.md: <created/updated/refactored>

Verified:
- Managed blocks preserved: <yes/no/not applicable>
- Command sources checked: <files inspected>
- PSP verify: <command/result or not run>

Not verified:
- <missing commands / unknown project facts>

Notes / risks:
- <remaining caveats>
```
