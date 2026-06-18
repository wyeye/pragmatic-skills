# Contributing

Keep changes small, evidence-backed, and regression-tested.

1. Add or update a sidecar and regenerate `skills/MANIFEST.json` for skill changes.
2. Add positive and negative eval coverage for behavior changes.
3. Add an adversarial test for installer or trace-security changes.
4. Run `make check test eval`.
5. Explain compatibility and rollback impact in the pull request.

Do not add runtime dependencies without a compelling, documented portability reason.
