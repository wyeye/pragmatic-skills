# Installation, upgrade, uninstall, and rollback

## Install

```sh
sh install.sh --target /path/to/repository
```

Host adapters default to `auto`. Use `--hosts all`, `minimal`, `none`, or an
explicit list such as `agents,claude,opencode`.

The installer validates source and target paths, rejects symlink components,
computes the complete plan before mutation, stages payloads under
`.psp/staging/`, creates a transaction backup, atomically replaces files, and
writes `.psp/install.json` last. It also writes a deterministic self-contained
`.psp/package.zip` used by the project-local CLI for package-aware lifecycle
commands. Mixed-origin licensing and provenance notices are copied to
`.psp/legal/` with the managed payload.

Preview the operation first:

```sh
sh install.sh --target /path/to/repository --dry-run --json
```

## Upgrade

An install command safely upgrades an existing PSP state. The explicit upgrade
command refuses to run when no prior state exists:

```sh
python3 /path/to/package/tools/psp.py upgrade --target /path/to/repository
# Or, using the installed self-contained lifecycle package:
python3 /path/to/repository/.psp/bin/psp.py upgrade --target /path/to/repository
```

Downgrades are rejected unless `--allow-downgrade` is explicit.

## Conflicts

A user-owned or modified managed file is never overwritten by default. The
operation stops and writes:

```text
.psp/conflicts/<timestamp>/conflicts.json
.psp/conflicts/<timestamp>/<candidate-paths...>
```

Review the conflict manifest and candidate content. Use `--force` only when the
intended overwrite or removal is understood and the generated backup is
acceptable. Malformed or duplicated managed-block markers are never guessed,
even with `--force`.

## Verify and diagnose

```sh
python3 .psp/bin/psp.py verify --target .
python3 .psp/bin/psp.py status --target .
python3 .psp/bin/psp.py doctor --target .
python3 .psp/bin/psp.py diff --target .
```

Use `--json` for automation. `doctor --repair` applies only explicitly safe
repairs; it does not silently overwrite drift.

`verify` checks installation integrity. It does not claim that an agent followed
the workflow; behavioral claims require captured traces and evals.

## Uninstall

```sh
python3 .psp/bin/psp.py uninstall --target . --dry-run
python3 .psp/bin/psp.py uninstall --target .
```

Uninstall removes unchanged managed files and PSP managed blocks while
preserving surrounding user content. For blocks inserted into existing UTF-8
files, the original bytes, BOM, newline convention, and file mode are restored
when the file has not otherwise drifted. Modified managed files are retained
unless `--force` is explicit.

## Rollback

```sh
python3 .psp/bin/psp.py rollback --target . --list
python3 .psp/bin/psp.py rollback --target .
python3 .psp/bin/psp.py rollback --target . --to <exact-backup-id>
```

Rollback restores the exact pre-operation snapshot. Before restoring, it creates
a `pre-rollback-*` safety snapshot of the current state. Backup IDs must match
exactly; prefixes are not accepted.
