# Project Profile Template

Copy this file to `.psp/project-profile.md` inside a concrete repository when project-specific overrides are useful.

This file is optional. Pragmatic Skills Pack discovers commands from repository evidence at runtime, so generic packages should not hard-code project commands.

## Commands

Use exact commands when known. Leave unknown entries blank.

```yaml
commands:
  install: ""
  test:
    narrow: ""
    full: ""
  lint: ""
  typecheck: ""
  build: ""
  run_local: ""
  format_check: ""
  format_write: ""
```

## Verification policy

```yaml
verification:
  fast_patch_default: "static inspection or targeted check"
  standard_default: "targeted test plus touched-area lint/typecheck when available"
  strict_default: "targeted tests plus broader test/build/typecheck where available"
```

## Generated, vendored, or restricted paths

```yaml
paths:
  generated: []
  vendored: []
  do_not_edit_without_approval: []
```

## Project-specific Strict Change triggers

```yaml
strict_triggers:
  - ""
```

## Permissions

```yaml
permissions:
  allow_dependency_install: "ask-first | allowed | disallowed"
  allow_lockfile_changes: "ask-first | allowed | disallowed"
  allow_commits: "ask-first | allowed | disallowed"
  allow_deployments: "ask-first | disallowed"
```

## Notes

Add project conventions, fixture notes, environment setup details, known flaky checks, or local safety rules here.
