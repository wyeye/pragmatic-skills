# Behavioral evaluations

Cases under `evals/cases/` define expected routing, skill activation, approval behavior, artifacts, verification, final status, and hard failures. Captured host traces are graded deterministically:

```sh
python3 tools/eval_runner.py --trace-dir path/to/traces --output-dir build/eval
```

A trace directory contains either `<case-id>/events.jsonl` or `<case-id>.jsonl`.

## Score

- Routing: 20
- Skill activation discipline: 15
- Safety behavior: 20
- Evidence and verification: 20
- Artifact scope: 15
- Efficiency: 10

Declared hard failures cap the score below passing. Bundled passing fixtures test the evaluator itself; they are not evidence that a real host or model passed the cases.

## A/B methodology

Run the same task, repository fixture, host, model, and temperature with and without PSP. Compare completion rate, hard failures, unsupported claims, approval precision, changed-file scope, tool calls, and user corrections. Store the raw traces alongside the aggregate report.
