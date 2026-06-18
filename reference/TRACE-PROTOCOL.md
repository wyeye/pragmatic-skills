# Trace protocol

PSP traces are optional append-only JSON Lines records stored under
`.psp/runs/<run-id>/events.jsonl`. They make routing, approvals, commands,
artifacts, verification, and final claims easier to audit.

## Start and emit events

```sh
python3 .psp/bin/psp.py trace start \
  --target . \
  --metadata '{"task":"Fix the parser"}'

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

The most recently active run is selected when `--run-id` is omitted. Use
`trace list` to enumerate run IDs and pass an explicit ID when concurrent or
historical runs exist.

## Evidence contract

A claim references evidence IDs, not merely event IDs. Evidence-producing
command, verification, review, or artifact events should include an
`evidence_id` in their data. Strong claims require semantically matching evidence:
for example, `tests_passed` needs a successful command whose `purpose` is a test
category, or a passed `verification_finished` with test scope and successful test
upstream evidence. An unrelated exit-code-zero command or inspected artifact is
not sufficient. Passed verification events must include an explicit `scope` and
an `evidence` list pointing to earlier successful source events.

## Required ordering

- Event IDs are unique within a run.
- Evidence must exist before a claim references it.
- No new events may be appended after `run_finished`.
- High-risk action events require an earlier approved event whose scope matches;
  optional approval IDs, action IDs, and expiration timestamps are enforced.
- A passed verification becomes stale after a later file-change event until
  verification is repeated.

## Redaction and storage

Keys and values resembling credentials, authorization headers, private keys,
tokens, passwords, or connection strings are redacted before persistence.
Target repositories should add `.psp/runs/`, `.psp/backups/`, `.psp/conflicts/`, and `.psp/staging/` to their Git ignore policy. Traces may still contain file paths,
commands, task descriptions, or business context and must be treated as
potentially sensitive operational records.

A valid trace improves auditability; it does not independently prove that an
external process, command output, or remote environment was truthful.
