---
schema: psp.skill/v1
name: review
kind: support
version: 1.2.0
summary: Review actual changed files, diff, patch, and behavior before calling Standard or
  Strict work complete.
triggers:
- Strict Change completion.
- Standard Change with behavior changes, tests, multiple files, or non-tiny diff.
loads:
  conditional:
    delegation_useful:
    - skills/delegation/SKILL.md
outputs:
- review mode
- evidence inspected
- blocking findings
- non-blocking findings
- unverified items
routing:
  user_exposed: false
  user_invocation_required: false
  activation: phase-triggered-support
  invoked_by:
  - skills/standard-change/SKILL.md
  - skills/strict-change/SKILL.md
  - skills/delegation/SKILL.md
  contract: Loaded automatically before calling Standard or Strict work complete.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
---

# Review
## Routing contract

This skill is an internal routing target. Users do not need to ask for this skill directly; the entry workflow, triage, mode, or phase trigger loads it when appropriate.



This support skill is loaded automatically before Standard or Strict work is called complete. Users do not need to request review unless they want extra review depth.

Use this skill before calling Standard or Strict work complete.

A review is not complete until it references actual evidence: the changed files, the diff/patch, or the behavior under review.

## Activation

Review is required for:

- Strict Change.
- Standard Change with behavior changes.
- Standard Change touching multiple files.
- Any change that updated tests, public behavior, data handling, auth, billing, dependencies, deployment, or compatibility.

For a tiny Fast Patch, a diff inspection can be reported in `handoff` without loading this full skill.

## Review evidence

Use the strongest available evidence:

- `git diff --stat` and relevant `git diff` output.
- Changed file list from the editor/tooling.
- Patch sections that were applied.
- Test changes and the behavior they assert.
- Command evidence when reviewing verification claims.

If git is unavailable, state which files or patch sections were inspected.

## Review checklist

Inspect the actual diff for:

- Intended changes only.
- No unrelated formatting churn.
- No debug logs, secrets, credentials, or private data.
- Tests/checks match changed behavior.
- Command evidence matches the claimed verification level.
- Error handling is appropriate.
- Edge cases are covered or acknowledged.
- Public API/data shape/compatibility changes are intentional.
- Documentation or comments updated when needed.

## Reviewer modes

Use the strongest available mode:

1. Real independent subagent/tool review.
2. Separate self-review pass with reviewer mindset.
3. Static checklist if execution is impossible.

Do not imply mode 1 happened if only mode 2 or 3 happened.

## Findings format

```text
Review mode: <independent subagent | self-review pass | static checklist>
Evidence inspected:
- Files: ...
- Diff/patch: ...
- Commands: ...

Findings:
- Blocking: ...
- Non-blocking: ...
- Verified: ...
- Not verified: ...
```

Fix blocking findings before saying the work is complete.
