# Architecture

## Control plane and content plane

PSP separates the workflow content from the operational controls around it.

```text
Content plane
  skills/*/SKILL.md       human-readable instructions
  skills/*/psp.skill.json machine-readable PSP contract
  skills/MANIFEST.json    generated graph and content index

Control plane
  tools/psp_installer.py  installation, drift, recovery
  tools/psp_trace.py      append-only evidence events
  tools/psp_eval.py       deterministic workflow grading
  tools/psp.py            stable command-line interface
```

Host adapters are intentionally thin. They point to the canonical entry Skill rather than duplicating the full workflow.

## Routing state

The logical state machine is:

```text
entry
  → direct route (only for explicit AGENTS.md maintenance or PSP retrospective)
  → otherwise triage
      → fast-patch | exploration | standard-change | strict-change
      → support Skills loaded by phase trigger
      → re-triage on material evidence change
      → handoff
```

This is a prompt-level state machine unless a host provides native enforcement hooks. The trace and evaluator make behavior observable; they do not grant powers the host runtime does not expose.

## Installation transaction

```text
validate package and target
  → resolve host adapters
  → compute full desired state
  → detect all conflicts
  → acquire target lock
  → snapshot affected paths and prior state
  → stage bytes, including a deterministic `.psp/package.zip` lifecycle cache
  → atomic replacements/removals
  → write install state last
  → verify
```

The embedded lifecycle archive is verified against its installed-state hash and
extracted only after enforcing entry-count, uncompressed-size, duplicate-path,
path-boundary, and symlink limits.

An exception during mutation restores the pre-operation snapshot. Conflict reports are written without partially applying the managed payload.

## Trust boundaries

Untrusted inputs include target paths, prior install state, existing managed markers, sidecars, trace JSON and eval captures. The implementation therefore validates relative paths, rejects symlink components, validates PSP-owned instances against declared JSON Schemas, checks event ordering and evidence semantics, and treats every completion claim as untrusted until its claim-specific evidence chain validates.
