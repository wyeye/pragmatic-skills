# Release checklist

- [ ] Project owner confirms copyright ownership, upstream permission, and final license terms.
- [ ] `python3 tools/psp.py verify-package --target .` passes.
- [ ] Unit, integration, adversarial, trace, eval-framework, and package tests pass on Linux, macOS, and Windows.
- [ ] The deterministic release archive is unpacked and re-verified.
- [ ] Every external GitHub Actions `uses:` reference is pinned to a reviewed full commit SHA.
- [ ] Behavioral eval captures have been run for every host claimed as behaviorally supported.
- [ ] Safety cases have a 100% pass rate and no evidence-fabrication hard failures.
- [ ] Compatibility dates, host versions, models, case sets, and raw-trace provenance are current.
- [ ] Changelog, upgrade notes, rollback notes, archive checksums, scorecard, and known limitations are published.
