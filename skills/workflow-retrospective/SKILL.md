---
schema: psp.skill/v1
name: workflow-retrospective
description: Review an explicitly requested completed-task trace and turn workflow evidence into actionable PSP improvements and eval cases.
kind: support
version: 1.7.0
summary: Run an active-only post-task retrospective to improve routing, skills, evidence quality, safety calibration, and host compatibility.
triggers:
- User explicitly asks to retrospect, summarize, evaluate, or improve the PSP workflow after a completed or recent task.
- User asks which skills were useful, missed, redundant, too heavy, or incorrectly triggered.
- User asks to turn task feedback into concrete skill changes, metadata updates, or workflow eval cases.
loads:
  conditional:
    implementation_requested:
    - skills/triage/SKILL.md
    persistent_record_requested:
    - skills/evidence-driven-execution/SKILL.md
    changed_files_completion:
    - skills/verification/SKILL.md
    - skills/handoff/SKILL.md
outputs:
- evidence-bounded task and workflow summary
- routing and progressive-disclosure assessment
- prioritized PSP improvement findings
- exact target files or metadata fields for each proposal
- regression/eval fixture for each material change
- explicit evidence gaps and confidence
safety:
  approval_required: Retrospective analysis is read-only by default. Writing a record or changing PSP files requires explicit user intent.
  requires_approval_before:
  - Mutating installed PSP-managed files in a consumer repository.
  - Applying workflow changes when the user requested analysis only.
  - Removing or weakening safety, evidence, verification, or approval rules.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  policy: active-only
  lifecycle: post-task
  auto_after_completion: false
  invoked_by:
  - skills/using-pragmatic-skills/SKILL.md#loads.direct.explicit_workflow_retrospective
  - workflow#explicit-post-task-retrospective-request
  active:
  - User asks for a post-task workflow retrospective, PSP iteration review, or skill-system improvement summary.
  passive: []
  passive_requires_confirmation: false
  routing_note: Route here only from explicit user intent expressed in normal language. Never invoke or offer this skill automatically at ordinary task completion.
---
# Workflow Retrospective

## Internal activation

This is an **active-only, post-task support skill**.

Users do not need to call it by name. Route here when the user explicitly asks to review a completed or recent task in order to improve Pragmatic Skills Pack, its routing, its skills, or its host integration.

Do **not** invoke this skill automatically after every handoff. Do **not** ask the user whether they want a retrospective as routine ceremony.

This skill is different from `skills/handoff/SKILL.md`:

- `handoff` reports what changed, what was verified, and what remains unverified.
- `workflow-retrospective` evaluates how well PSP itself handled the task and turns evidence into iteration proposals and eval cases.

## Active trigger examples

Route here when the user says things such as:

- “复盘一下刚才的任务和工作流。”
- “总结这次哪些 skills 触发得对或不对。”
- “根据这次过程改进 PSP。”
- “这次流程哪里太重、漏了什么、该怎么迭代？”
- “Generate a post-task workflow retrospective.”
- “Turn this task into concrete skill changes and eval fixtures.”

A request to “summarize the implementation” alone is normally a handoff request, not a workflow retrospective. The request must concern the workflow, routing, skills, evidence discipline, safety, or future PSP iteration.

## Scope rule

Use the task named by the user. If the user says “这次”“刚才” or equivalent, use the most recent observable task context.

If the task is still in progress, retrospect only on the completed portion and label the scope as partial. Do not pretend later phases occurred.

If there is insufficient evidence, produce a limited retrospective and state the gaps. Do not invent an execution trace.

## Evidence boundary

Use only observable evidence, such as:

- The user's request, corrections, approvals, and feedback.
- Visible plans, updates, and final handoff.
- Files inspected, changed, or proposed.
- Diffs, patches, manifests, installer state, conflict reports, and repository artifacts.
- Commands actually run and their recorded output.
- Tests, builds, reviews, safety gates, or subagent evidence that actually occurred.
- Relevant PSP skill bodies, frontmatter, manifest entries, adapters, and reference docs.

Never claim access to hidden chain-of-thought, private scratchpads, unrecorded tool calls, or invisible host/runtime state.

Use these distinctions precisely:

- `observed`: directly supported by visible evidence.
- `inferred`: a reasonable hypothesis supported by evidence, explicitly labeled.
- `not observed`: no evidence is available; this does not prove the action did not happen.
- `unknown`: the available context cannot establish the fact.

## Retrospective workflow

### 1. Establish the baseline

Record:

- Task goal.
- User-visible result.
- Files/artifacts involved.
- Verification and review evidence.
- User corrections or friction signals.
- Evidence gaps.

Do not repeat the full implementation handoff. Capture only what is needed to assess PSP.

### 2. Reconstruct intended and observed routing

Compare the expected route with what can be observed:

```text
entry
  -> direct active route OR triage
  -> primary mode, when applicable
  -> support skills by phase/condition
  -> handoff
```

Assess:

- Was the entry route correct?
- Was the selected mode the smallest safe mode?
- Were support skills loaded only when needed?
- Was a required skill missed?
- Was an unnecessary skill loaded or exposed too early?
- Did re-triage happen when scope or risk changed?
- Did the user have to understand internal skill names or workflow mechanics?

Do not state that a skill ran unless there is evidence. Say `expected`, `observed`, `not observed`, or `unknown`.

### 3. Evaluate the workflow dimensions

Review only dimensions relevant to the task:

- **Trigger quality:** false positive, false negative, ambiguous trigger, or correct trigger.
- **Progressive disclosure:** unnecessary context loading, premature rules, or missing phase trigger.
- **Mode calibration:** Fast Patch vs Exploration vs Standard vs Strict.
- **User friction:** repeated questions, avoidable approvals, excessive ceremony, unclear prompts.
- **Evidence integrity:** claims tied to files, commands, diffs, tests, reviews, and approvals.
- **Command discovery:** correct source/cwd/confidence/run policy; no invented commands.
- **Safety calibration:** gates neither too weak nor unnecessarily blocking.
- **Verification and review:** sufficient breadth, explicit gaps, useful failure handling.
- **Handoff quality:** compact, factual, and actionable.
- **Metadata/body consistency:** triggers, loads, activation, outputs, and body agree.
- **Cross-host behavior:** adapters and native discovery do not duplicate or conflict.
- **Installer/upgrade behavior:** managed ownership, backups, conflicts, and version migration.

### 4. Produce findings, not vague advice

For each material finding, use this structure:

```text
ID: PSP-RETRO-###
Status: keep | change | investigate
Priority: P0 | P1 | P2 | P3
Confidence: high | medium | low
Observation: <what happened or was observed>
Evidence: <specific message, file, command, diff, or artifact>
Impact: <user cost, safety risk, context cost, or maintainability effect>
Root-cause hypothesis: <clearly labeled inference>
Proposed change: <concrete rule or behavior change>
Targets: <exact skill/reference/manifest/adapter files or metadata fields>
Regression risk: <what the change might break>
Eval fixture: <minimal scenario, expected route/behavior, failure signal>
```

Priority meanings:

- `P0`: evidence integrity, destructive action, security, or data-loss risk.
- `P1`: incorrect routing, missing safety/verification, or recurring major friction.
- `P2`: meaningful usability, context, maintainability, or host-compatibility improvement.
- `P3`: wording, organization, or low-impact polish.

### 5. Prefer tuning over skill proliferation

Before proposing a new skill, check whether the improvement belongs in:

- An existing trigger.
- A phase load.
- A metadata field.
- A clearer body rule.
- A reference document.
- An eval fixture.
- A host adapter or installer rule.

Add a new skill only when the capability is distinct, reusable, independently triggerable, and would otherwise overload an existing skill.

### 6. Attach an eval to every material change

Every P0-P2 proposal must include an executable or inspectable eval fixture:

```text
Scenario: <minimal user request and repository state>
Expected route: <entry/direct route/triage/mode/support skills>
Expected behavior: <observable behavior>
Must not: <forbidden behavior>
Pass evidence: <what proves success>
Failure signal: <what proves regression>
```

Prefer one narrow fixture per finding over a broad prose test.

## Default output

Use this structure unless the user requests another format:

```md
# PSP Workflow Retrospective

## Scope and evidence
- Task:
- Result:
- Evidence used:
- Evidence gaps:

## What worked
- ...

## Findings
### PSP-RETRO-001 — <title>
- Status / Priority / Confidence:
- Observation:
- Evidence:
- Impact:
- Proposed change:
- Targets:
- Regression risk:
- Eval fixture:

## Recommended iteration order
1. ...

## No-change decisions
- <rules/skills that worked and should remain unchanged>
```

Keep the narrative concise. The useful output is the evidence, exact target, and eval fixture.

## Optional machine-readable iteration record

When the user asks to save, archive, aggregate, or compare retrospectives, include a YAML record using `psp.retrospective/v1` as documented in `reference/WORKFLOW-RETROSPECTIVE.md`.

Default location when the user explicitly requests a repository record:

```text
.psp/retrospectives/YYYY-MM-DD-<task-slug>.md
```

Do not write this file by default. Do not store secrets, raw private logs, or hidden reasoning.

## Applying proposed changes

A retrospective is read-only by default.

If the user explicitly asks to apply the improvements in the same request:

1. Complete the retrospective first so the change rationale is explicit.
2. Route the implementation back through `skills/triage/SKILL.md`.
3. Use Standard Change for ordinary skill/metadata/docs changes.
4. Use Strict Change when changes weaken safety, alter installer/upgrade ownership, affect multiple host adapters, or have broad compatibility impact.
5. Verify manifest/body/path consistency and add the proposed eval fixtures.
6. Use `handoff` for the actual file changes.

Do not silently edit installed PSP-managed files in a consumer repository. Prefer changing the PSP source package and upgrading through `install.sh`, or write a retrospective record for later application.

## Completion rule

For analysis-only retrospectives, the structured retrospective itself is the final response; do not add a second generic handoff.

If files were written or PSP changes were applied, use `verification` and `handoff` for those file changes after the retrospective findings.
