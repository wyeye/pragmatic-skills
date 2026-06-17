# Pragmatic Skills Pack Project Profile Template

This file is optional. Copy it to `.psp/project-profile.md` in a concrete repository when local overrides are useful.

## Commands

Record only commands that are actually supported by the project.

```yaml
commands:
  install:
    command: ""
    cwd: "."
    run_policy: "ask-before-running"
    source: "project profile"
  test:
    command: ""
    cwd: "."
    run_policy: "safe-to-run"
    source: "project profile"
  lint:
    command: ""
    cwd: "."
    run_policy: "safe-to-run"
    source: "project profile"
  typecheck:
    command: ""
    cwd: "."
    run_policy: "safe-to-run"
    source: "project profile"
  build:
    command: ""
    cwd: "."
    run_policy: "safe-to-run"
    source: "project profile"
  run_local:
    command: ""
    cwd: "."
    run_policy: "ask-before-running"
    source: "project profile"
```

## Strict triggers

```yaml
strict_triggers:
  - auth or permission changes
  - payment, billing, quota, or plan changes
  - database migrations, backfills, or destructive operations
  - public API, SDK, or wire format changes
  - production deployment or infrastructure changes
```

## No-edit zones

```yaml
no_edit:
  - path/to/generated/files
  - path/to/vendor/files
```

## Generated files

```yaml
generated:
  - path/to/generated/files
```

## Dependency policy

```yaml
dependencies:
  add_runtime_dependency: ask-first
  update_lockfile: ask-first
  install_command: ask-first
```

## Git policy

```yaml
git:
  auto_commit: false
  force_push: never
  worktree_when_dirty: true
```
