# Changelog

## 2.0.2 — 2026-06-22

- Added a passive behavior/state matrix trigger for multi-entry or multi-authority delete, removal, synchronization, reconciliation, lifecycle, status, and query-visibility changes.
- Required the matrix to distinguish reads, local transitions, external calls, device/event effects, synchronization behavior, and final observable results without assuming reverse paths are symmetric.
- Carried changed matrix rows through planning, TDD, verification, and final review.
- Added positive and negative eval fixtures so cross-system work activates requirements modeling while fully specified local-only status work does not over-trigger it.


## 2.0.1 — 2026-06-18

- Embedded a self-contained runtime package so installed `doctor`, `diff`, reinstall, and same-version `upgrade` do not depend on the caller's working directory.
- Added real JSON Schema instance validation for manifests, sidecars, adapter declarations, eval cases, and captured results.
- Bound success claims to claim-specific evidence purposes; unrelated successful commands and inspected artifacts no longer prove tests or builds.
- Preserved managed-block file permissions, UTF-8 BOMs, and newline conventions, with exact uninstall restoration for PSP-inserted blocks.
- Verified every declared host adapter resource and expanded trace redaction for DSNs, connection strings, and credential-bearing URLs.
- Added embedded-package integrity limits and tamper detection while keeping basic installation verification available.
- Pinned every GitHub Actions dependency to an immutable full commit SHA.
- Added regression tests for all repaired defects; the local suite now contains 58 tests.

## 2.0.0 — 2026-06-18

- Replaced the legacy installer path with a dependency-free transactional installer.
- Defaulted host selection to automatic detection.
- Added bounded path resolution, symlink rejection, operation locking, conflict reports, staging, atomic writes, backups, uninstall, rollback, doctor, diff, dry-run, and JSON output.
- Added portable Agent Skills frontmatter, `psp.skill.json` sidecars, graph validation, and a deterministic manifest.
- Added append-only JSONL traces with secret redaction, claim-to-evidence validation, approval ordering, and stale-verification detection.
- Added 16 deterministic workflow eval cases, synthetic framework self-tests, real-trace graders, and JSON/Markdown/HTML reports.
- Added 44 local unit, integration, adversarial, trace, eval, and package tests at release preparation time.
- Added Linux, macOS, and Windows CI matrices, deterministic release packaging, governance files, compatibility labels, and operator documentation.
- Corrected provenance and licensing language: the package is mixed-origin, and the reviewed upstream snapshot contained no repository-level license.

The 2.0 version reflects breaking changes to installer state, metadata sidecars,
trace contracts, and release structure relative to the 1.8 upstream snapshot.
