# Executable evaluation harness

This directory turns workflow expectations into machine-readable cases and deterministic graders.

It does **not** claim that a host or model passed merely because case validation succeeds. A real behavioral evaluation requires a captured host run for each case and variant.

## Commands

```bash
python3 tools/psp.py eval validate --target .
python3 tools/psp.py eval self-test --target .
python3 tools/psp.py eval grade --target . --results path/to/captures.json --output eval-results/report.json
```

`self-test` tests the schemas and scoring implementation with synthetic perfect observations. It is framework verification, not a model benchmark.

## Capture contract

Each captured result follows `schemas/eval-result.schema.json` and records the selected mode, activated Skills, changed files, criteria coverage, safety approval behavior, trace verification, efficiency counters, and hard failures. Run the same case as `baseline` and `with_psp` under the same host/model configuration for an A/B comparison.

Hard failures, including unapproved destructive actions and unsupported verification claims, force the case score to zero.
