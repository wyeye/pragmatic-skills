---
schema: psp.skill/v1
name: command-discovery
description: Resolve install, test, lint, typecheck, build, and local-run commands from project evidence instead of hardcoding them.
kind: support
version: 1.5.0
summary: Resolve install, test, lint, typecheck, build, and local-run commands from project evidence instead of hardcoding them.
triggers:
- A workflow needs a project command and no exact command is already known.
- Verification, TDD, build, or local-run evidence is needed.
loads:
  conditional:
    high_risk_dependency_or_lockfile_action:
    - skills/safety-gates/SKILL.md
outputs:
- command map with command, cwd, source, confidence, and run policy
safety:
  requires_approval_before:
  - Mutating dependency actions when they may change lockfiles or environment state.
  - Long-running servers if they affect shared resources.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/exploration/SKILL.md#loads.conditional.command_needed
  - skills/fast-patch/SKILL.md#loads.conditional.command_needed
  - skills/standard-change/SKILL.md#loads.phased.discovery
  - skills/strict-change/SKILL.md#loads.phased.command
  - skills/tdd/SKILL.md#loads.conditional.test_command_unknown
  - skills/using-pragmatic-skills/SKILL.md#loads.conditional.command_resolution
  - skills/verification/SKILL.md#loads.conditional.command_unknown
  - skills/writing-plans/SKILL.md#loads.conditional.commands_needed_for_verify_steps
  routing_note: Users provide tasks; agents route from AGENTS.md through triage and phase triggers. Users do not manually invoke individual skills.
---
# Command Discovery

## Internal activation

This is a support skill. It is loaded by a mode, router, or another support skill when the relevant phase or condition is reached.

Users do not need to ask for this skill directly.

Use this skill whenever the workflow needs install, test, lint, typecheck, build, or run-local commands and the exact command is not already known.

This is what makes the skill pack universal: commands are resolved from the current repository instead of being hardcoded in `AGENTS.md`.

## Core rule

Do not invent project commands.

A command is usable only when it is supported by evidence from the current repository, explicit user instructions, or a clearly applicable ecosystem convention.

## Resolution priority

Resolve commands in this order:

1. Explicit user instruction in the current conversation.
2. Project-specific instructions already present in the repository, such as `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursorrules`, `README*`, `CONTRIBUTING*`, `docs/*`, `.psp/project-profile.md`, or CI configuration.
3. Package/task definitions, such as `package.json` scripts, `Makefile`, `justfile`, `Taskfile.yml`, `pyproject.toml`, `tox.ini`, `noxfile.py`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `deno.json`, `composer.json`, `Gemfile`, or similar files.
4. Conventional ecosystem fallback only when the matching project files exist and the fallback is safe and obvious.
5. If no command is discoverable, report `not discovered` and use static inspection or the next strongest available evidence.

Prefer project-defined scripts over generic commands.

## Command map output

When commands matter, produce a compact command map:

```text
Command map:
- install: <command or not discovered>
  cwd: <directory>
  source: <user | project docs | package script | config | convention | not discovered>
  confidence: <high | medium | low>
  run policy: <safe to run | ask first | do not run unless requested>
- test: ...
- lint: ...
- typecheck: ...
- build: ...
- run-local: ...
```

Only include entries relevant to the current task. Do not force all six categories.

## Monorepos and working directory

For monorepos:

- Prefer the nearest package/module root that owns the touched files.
- Use repo-wide commands only when the change affects shared behavior or the project instructions say to.
- Record `cwd` for each command.
- Do not run broad workspace commands for a tiny local change unless blast radius justifies it.

## Common detectors

Use these as candidates, not assumptions.

### JavaScript / TypeScript / Node

Evidence files: `package.json`, lockfiles, workspace files, `tsconfig.json`, test configs.

- Prefer `package.json` scripts: `test`, `lint`, `typecheck`, `build`, `dev`, `start`.
- Pick the package manager from lockfiles or project docs: `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, `bun.lockb`, `bun.lock`, or equivalent.
- Use package scripts rather than calling tools directly when scripts exist.
- Treat dependency installation as optional and potentially mutating unless the repo provides an immutable/frozen install command.

### Python

Evidence files: `pyproject.toml`, `uv.lock`, `poetry.lock`, `requirements*.txt`, `tox.ini`, `noxfile.py`, `pytest.ini`, `setup.cfg`, `Makefile`, `justfile`.

- Prefer project task runners: `make`, `just`, `tox`, `nox`, `uv`, `poetry`, or documented commands.
- Use `pytest` only when tests/config indicate pytest and dependencies are available.
- Use lint/typecheck tools only when configured, such as Ruff, mypy, Pyright, or project scripts.

### Go

Evidence files: `go.mod`, `go.work`.

- Typical test command: `go test ./...` from the module/workspace root.
- Typical build command: `go build ./...` when build verification is needed.

### Rust

Evidence files: `Cargo.toml`, `Cargo.lock`.

- Typical test command: `cargo test`.
- Typical lint command: `cargo clippy` only when clippy is available or project docs require it.
- Typical build command: `cargo build`.

### JVM

Evidence files: `pom.xml`, `mvnw`, `build.gradle`, `gradlew`, `settings.gradle`.

- Prefer wrappers: `./mvnw` or `./gradlew` when present.
- Use documented tasks before generic lifecycle commands.

### .NET

Evidence files: `*.sln`, `*.csproj`, `global.json`.

- Typical test command: `dotnet test`.
- Typical build command: `dotnet build`.

### Make / Just / Task

Evidence files: `Makefile`, `justfile`, `Taskfile.yml`.

- Prefer explicitly named targets like `test`, `lint`, `typecheck`, `build`, `check`, `dev`.
- Inspect target names before running.

## Install policy

Do not run install commands automatically just because an install command exists.

Prefer the existing environment. Run install only when:

- The task requires it,
- the project provides a safe install command, or
- the user explicitly asks.

Ask first or load `skills/safety-gates/SKILL.md` when install/dependency actions may alter lockfiles, runtime dependencies, shared caches, production state, or security posture.

## Local-run policy

`run-local` commands often start long-running servers.

Do not run them unless the task requires a live server, the environment can manage long-running processes safely, and the command source is known. Prefer documented smoke tests over ad-hoc server startup.

## Evidence rules

When you run a discovered command, record:

- Exact command.
- Working directory.
- Source of the command.
- Result.
- Relevant output summary.

If a command fails because dependencies are missing, report that directly. Do not silently switch to install unless the install policy allows it.
