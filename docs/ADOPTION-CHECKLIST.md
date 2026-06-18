# Adoption checklist

Use this checklist before making PSP a team-wide default.

## Package

- [ ] Review `LICENSE`, `NOTICE`, and `SOURCE-BASELINE.md` for organizational acceptance.
- [ ] Run package verification and the full local test suite.
- [ ] Review target changes with `psp diff` and `install --dry-run`.
- [ ] Confirm backup, rollback, conflict, and uninstall behavior in a disposable repository.

## Workflow

- [ ] Add project-specific commands and risk triggers to `.psp/project-profile.md` when needed.
- [ ] Confirm the four primary-mode boundaries match team practice.
- [ ] Confirm high-risk approval scopes for data, production, auth, billing, secrets and shared Git history.
- [ ] Decide which trace events the chosen host can emit reliably.

## Evidence

- [ ] Capture real runs for positive, negative, failure, and prompt-injection cases.
- [ ] Run A/B tasks with and without PSP under the same host/model settings.
- [ ] Measure routing accuracy, unsupported claims, approval precision, changed-file scope, corrections and cost.
- [ ] Keep raw host logs with sanitized PSP traces where policy permits.

## Release gate

- [ ] Safety cases have no unauthorized high-risk actions.
- [ ] Successful completion claims have valid evidence.
- [ ] No user-owned content is overwritten in installer tests.
- [ ] Every host promoted to supported has current versioned live-run evidence.
- [ ] Rollback and removal instructions are included in change management.
