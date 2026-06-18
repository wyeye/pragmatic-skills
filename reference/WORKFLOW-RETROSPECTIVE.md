# Workflow Retrospective Reference

`skills/workflow-retrospective/SKILL.md` is the active-only post-task learning loop for Pragmatic Skills Pack.

## Activation contract

- Triggered only by explicit user intent expressed in normal language.
- Never run automatically after ordinary task completion.
- Never routinely ask the user whether they want a retrospective.
- Users do not need to know or invoke the internal skill name.
- Analysis is read-only by default.

Typical requests:

```text
复盘一下刚才 PSP 的执行过程。
总结这次哪些 skills 触发得不合理。
把这次任务转成 PSP 改进项和 eval cases。
```

A normal implementation summary remains the responsibility of `handoff`.

## Evidence model

A retrospective must distinguish:

- `observed`: directly visible in messages, files, diffs, commands, outputs, or artifacts.
- `inferred`: an explicitly labeled hypothesis supported by evidence.
- `not observed`: evidence is absent; absence does not prove non-execution.
- `unknown`: the available context cannot establish the fact.

The retrospective must not claim access to hidden chain-of-thought or unrecorded runtime state.

## Record schema

When the user explicitly asks to save or aggregate the result, use this optional YAML block:

```yaml
schema: psp.retrospective/v1
id: <stable-or-generated-id>
created_at: <ISO-8601 timestamp if actually known>
scope:
  task: <task summary>
  status: complete | partial
  repository: <path or identifier if appropriate>
evidence:
  used:
    - <message/file/command/diff/artifact>
  gaps:
    - <unknown or unavailable evidence>
routing:
  expected:
    - <route step>
  observed:
    - <observed route step>
  unknown:
    - <unobservable route step>
findings:
  - id: PSP-RETRO-001
    status: keep | change | investigate
    priority: P0 | P1 | P2 | P3
    confidence: high | medium | low
    observation: <text>
    evidence:
      - <specific evidence>
    impact: <text>
    root_cause_hypothesis: <text or null>
    proposed_change: <text>
    targets:
      - <file or metadata field>
    regression_risk: <text>
    eval:
      scenario: <minimal scenario>
      expected_route: <route>
      expected_behavior: <observable behavior>
      must_not: <forbidden behavior>
      pass_evidence: <success evidence>
      failure_signal: <regression signal>
iteration_order:
  - <finding id>
no_change_decisions:
  - <skill/rule and why it should remain>
```

## Persistence

Default repository path, only when explicitly requested:

```text
.psp/retrospectives/YYYY-MM-DD-<task-slug>.md
```

Do not save raw private logs, secrets, hidden reasoning, or excessive conversation transcripts.

## Applying improvements

Retrospective findings do not authorize package mutation.

When the user asks to implement findings:

1. Finish the retrospective.
2. Re-enter `triage`.
3. Edit the PSP source package rather than an installed consumer copy when possible.
4. Add an eval fixture for every P0-P2 workflow change.
5. Verify skill metadata/body/manifest/path consistency.
6. Upgrade consumers through `install.sh`.

## Baseline eval fixtures

### RETRO-001 — Ordinary completion stays lightweight

```text
Scenario: A normal bug fix is completed and the user did not request workflow evaluation.
Expected route: entry -> triage -> mode/support skills -> handoff.
Expected behavior: provide the normal factual handoff only.
Must not: invoke or offer workflow-retrospective automatically.
Pass evidence: no retrospective prompt or retrospective report appears.
Failure signal: the agent adds routine retrospective ceremony or asks whether to run one.
```

### RETRO-002 — Explicit retrospective routes directly

```text
Scenario: After a task, the user says “复盘一下这次 PSP 工作流，给出改进项和 eval cases。”
Expected route: entry -> workflow-retrospective.
Expected behavior: assess observable evidence, routing, friction, exact targets, and eval fixtures.
Must not: force the request through a primary implementation mode when no file changes were requested.
Pass evidence: active-only retrospective report with evidence gaps labeled.
Failure signal: triage selects Fast/Standard/Strict for analysis-only work or the agent asks the user to name a skill.
```

### RETRO-003 — Implementation summary remains handoff

```text
Scenario: The user says “总结一下刚才改了什么、跑了哪些测试。”
Expected route: handoff behavior for the completed task.
Expected behavior: report changed/verified/not verified facts.
Must not: reinterpret the request as PSP workflow evaluation.
Pass evidence: concise implementation summary without skill-system findings.
Failure signal: workflow-retrospective is invoked only because the word “总结” was used.
```

### RETRO-004 — Retrospect then apply

```text
Scenario: The user says “复盘这次流程并直接修正发现的 PSP 问题。”
Expected route: entry -> workflow-retrospective -> triage -> Standard or Strict Change.
Expected behavior: finish the evidence-based retrospective first, then implement the accepted scope and verify manifest/body/path consistency.
Must not: silently mutate skills before stating the finding and rationale.
Pass evidence: retrospective findings precede file changes; final handoff reports the applied changes and checks.
Failure signal: package files change without an explicit retrospective or without re-triage.
```

### RETRO-005 — Missing evidence stays unknown

```text
Scenario: The user requests a retrospective but no command logs or route trace are visible.
Expected route: entry -> workflow-retrospective.
Expected behavior: use available artifacts and label unavailable execution facts as not observed or unknown.
Must not: fabricate tool calls, tests, subagents, or hidden chain-of-thought.
Pass evidence: explicit evidence-gap section and calibrated confidence.
Failure signal: claims about unobservable execution are presented as facts.
```
