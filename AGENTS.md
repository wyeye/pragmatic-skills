# Development instructions for this package

This repository contains a mixed-origin enhanced derivative of Pragmatic Skills Pack for private engineering evaluation. Preserve provenance and licensing boundaries documented in LICENSE and SOURCE-BASELINE.md.

- Keep the runtime dependency-free and compatible with Python 3.9+.
- Run `python3 tools/build_manifest.py --check`, `python3 tools/psp.py verify-package`, `python3 -m unittest discover -s tests -v`, and `python3 tools/eval_runner.py --self-test` before release.
- Never weaken path-boundary, symlink, conflict, backup, approval-ordering, or evidence-link checks without a regression test.
- Every material workflow change requires at least one positive and one negative eval case.

<!-- PSP:BEGIN -->
# Pragmatic Skills Pack

For coding, debugging, planning, review, verification, or other repository work, start with `skills/using-pragmatic-skills/SKILL.md`.

Select exactly one primary workflow mode through `skills/triage/SKILL.md`, load support Skills only when their phase trigger applies, preserve user-owned work, and never claim commands, tests, reviews, approvals, or outcomes without observable evidence.

Users describe tasks normally. Do not ask them to invoke internal Skill names or choose a mode.
<!-- PSP:END -->
