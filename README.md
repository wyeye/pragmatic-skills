# Pragmatic Skills Pack — Enhanced 2.0.1

A phase-routed, evidence-first workflow pack for coding agents, with a hardened
installer, auditable local traces, deterministic workflow evals, and release
checks.

This bundle is an **enhanced derivative for private engineering evaluation**.
It is based on the upstream snapshot documented in `SOURCE-BASELINE.md`; it is
not an official upstream release. Read `LICENSE` before redistribution.

## What it provides

PSP gives an agent one entry point and routes work internally:

```text
using-pragmatic-skills
  -> triage
    -> fast-patch | exploration | standard-change | strict-change
      -> phase-triggered support Skills
         requirements, planning, TDD, safety, verification, review, handoff
```

The workflow aims to keep small changes small while requiring stronger planning,
approval, evidence, and verification as scope or risk increases.

## Enhanced 2.0.1 highlights

- **Transactional installer:** bounded paths, symlink rejection, operation
  locking, staging, atomic replacement, backups, conflict reports, rollback,
  uninstall, doctor, diff, dry-run, and JSON output.
- **Portable Skill metadata:** standard `SKILL.md` frontmatter plus machine-
  readable `psp.skill.json` sidecars and a generated dependency manifest.
- **Evidence traces:** optional append-only JSONL events, expanded credential
  redaction, claim-specific evidence checks, scoped/expiring approval ordering,
  and stale-verification detection.
- **Executable eval framework:** 16 deterministic cases covering routing,
  safety, evidence, scope, re-triage, and negative controls.
- **Release engineering:** unit, integration, adversarial, trace, eval, package,
  and CI checks using only the Python standard library; GitHub Actions are
  pinned to immutable full commit SHAs.

## Requirements

- Python 3.9 or newer
- A project directory in which you can create `.psp/`, Skill files, and any
  selected host adapter files

No third-party Python dependency is required.

## Install

From the unpacked bundle:

```sh
sh install.sh --target /path/to/your/repository
```

On Windows, invoke the Python entry point directly:

```powershell
py -3 tools\psp.py install --target C:\path\to\repository
```

Host selection defaults to `auto`. The installer installs the common `agents` entry and adds only the host adapters detected from project markers. You may override it:

```sh
sh install.sh --target /path/to/repository --hosts all
sh install.sh --target /path/to/repository --hosts minimal
sh install.sh --target /path/to/repository --hosts none
sh install.sh --target /path/to/repository --hosts agents,claude,opencode
```

Useful safety options:

```sh
# Print the complete plan without writing
sh install.sh --target /path/to/repository --dry-run --json

# Install a project profile template when absent
sh install.sh --target /path/to/repository --profile

# Overwrite a modified managed file only after reviewing the backup plan
sh install.sh --target /path/to/repository --force
```

The installer writes its state to `.psp/install.json`. It preserves user-owned
content outside PSP managed blocks and does not overwrite modified managed files
unless `--force` is explicit. For inserted managed blocks it retains the original
UTF-8 BOM, newline convention, and file mode, and restores the exact original
bytes on uninstall. Licensing and provenance notices are installed under
`.psp/legal/` so managed Skill copies retain their source context.

## Operate an installed project

The project-local CLI is installed under `.psp/bin/psp.py`. A deterministic
self-contained lifecycle bundle is cached at `.psp/package.zip`, so `doctor`,
`diff`, `verify-package`, reinstall, and same-version `upgrade` do not depend on
the caller's current directory or the original unpacked archive:

```sh
python3 .psp/bin/psp.py verify --target .
python3 .psp/bin/psp.py status --target .
python3 .psp/bin/psp.py doctor --target .
```

Compare or reapply the embedded installed package without writing first:

```sh
python3 .psp/bin/psp.py diff --target .
python3 .psp/bin/psp.py upgrade --target . --dry-run
python3 .psp/bin/psp.py upgrade --target .
```

To upgrade from a newer unpacked bundle, run that bundle's CLI or pass its path
with `--package-root`. The embedded archive is hash-checked against install
state and extracted with bounded entry, size, path, duplicate, and symlink
validation.

Safely remove managed content or restore a transaction snapshot:

```sh
python3 .psp/bin/psp.py uninstall --target . --dry-run
python3 .psp/bin/psp.py uninstall --target .

python3 .psp/bin/psp.py rollback --target . --list
python3 .psp/bin/psp.py rollback --target .
python3 .psp/bin/psp.py rollback --target . --to <exact-backup-id>
```

A rollback restores the exact pre-operation snapshot and first creates a safety
snapshot of the current state.

## Optional execution traces

Traces are local append-only records under `.psp/runs/<run-id>/events.jsonl`.
They are not required for normal Skill use, but make claims and approvals easier
to audit.

```sh
python3 .psp/bin/psp.py trace start \
  --target . \
  --metadata '{"task":"Fix parser validation"}'

python3 .psp/bin/psp.py trace emit mode_selected \
  --target . \
  --data '{"mode":"standard-change"}'

python3 .psp/bin/psp.py trace emit command_finished \
  --target . \
  --event-id cmd-tests \
  --data '{"command":"pytest -q","exit_code":0,"purpose":"tests","evidence_id":"tests-ok"}'

python3 .psp/bin/psp.py trace emit verification_finished \
  --target . \
  --event-id verify-tests \
  --data '{"status":"passed","scope":"tests","evidence":["tests-ok"],"evidence_id":"verified-tests"}'

python3 .psp/bin/psp.py trace emit claim \
  --target . \
  --data '{"claim":"tests_passed","evidence":["verified-tests"]}'

python3 .psp/bin/psp.py trace finish --target . --status completed
python3 .psp/bin/psp.py trace verify --target .
```

`trace verify` rejects duplicate event IDs, claims that reference missing or
future evidence, passed verification without successful upstream evidence,
claim/evidence type mismatches, high-risk actions without a prior matching and
unexpired approval, and verification made stale by later file changes. A generic
successful command or inspected artifact cannot prove that tests or builds
passed. Sensitive-looking keys, credential-bearing URLs, DSNs, and connection
strings are redacted before persistence, but traces should still be treated as
operationally sensitive.

## Behavioral evals

Validate the case definitions and the deterministic grader:

```sh
python3 tools/psp.py eval validate --target .
python3 tools/psp.py eval self-test --target .
python3 tools/eval_runner.py --self-test --output-dir build/eval --summary
```

Grade real captured host runs:

```sh
python3 tools/eval_runner.py \
  --trace-dir path/to/captured-traces \
  --output-dir build/eval
```

The self-test proves that the case files, synthetic passing fixtures, and grader
agree. It does **not** prove that a real model or host passed the workflow. Real
compatibility claims require captured runs for the specified host, version,
model, date, and case set.

## Skill metadata model

Each `SKILL.md` keeps portable top-level fields:

```yaml
---
name: standard-change
description: Execute a bounded repository change through planning, implementation, verification, and handoff.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible host or a PSP adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: mode
  psp-version: 2.0.1
---
```

PSP-specific graph data lives in the adjacent `psp.skill.json`. The generated
`skills/MANIFEST.json` records hashes and validates that there is one entry Skill,
all references exist, and every Skill is reachable.

## Develop and verify this bundle

```sh
make check
make test
make eval
make package
```

Equivalent direct commands:

```sh
python3 -m compileall -q tools
python3 tools/build_manifest.py --check
python3 tools/psp.py verify-package --target .
python3 -m unittest discover -s tests -v
python3 tools/psp.py eval validate --target .
python3 tools/psp.py eval self-test --target .
python3 tools/eval_runner.py --self-test --summary
```

`verify-package` checks package structure, declared adapter resources, manifests,
JSON Schema instances, sidecars, captured-result shapes, and eval case syntax.
It is an integrity check, not behavioral proof.

## Repository map

```text
skills/       canonical workflow Skills and sidecars
adapters/     thin host discovery adapters
reference/    operator and workflow documentation
schemas/      trace, eval, manifest, sidecar, and installer schemas
evals/        executable cases, fixtures, runners, and deterministic graders
tools/        installer, trace, eval, manifest, and release CLI
tests/        unit, integration, adversarial, trace, eval, and package tests
.github/      CI and contribution templates
```

## Known boundaries

- Routing is prompt-mediated unless a host provides a runtime enforcement API.
- Different models and host versions can follow the same Skill differently.
- An installer integrity check cannot establish that an agent followed the
  workflow.
- A trace improves auditability but cannot independently establish that every
  external command or environment fact was truthful.
- Host labels in `compat/hosts.yaml` remain conservative until real captured
  behavioral runs are published.

## Licensing and provenance

This package is mixed-origin. The reviewed upstream snapshot did not include a
repository-level license, so upstream-derived material is **not** relicensed by
this enhanced bundle. Newly authored enhancements are offered under
Apache-2.0 only to the extent their contributor has the right to license them.
See `LICENSE`, `LICENSE-APACHE-2.0`, `NOTICE`, and `SOURCE-BASELINE.md`.
