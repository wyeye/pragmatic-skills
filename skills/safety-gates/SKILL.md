---
schema: psp.skill/v1
name: safety-gates
description: Require explicit approval before destructive, production-affecting, security-sensitive, or hard-to-reverse actions.
kind: support
version: 1.6.0
summary: Require explicit approval before destructive, production-affecting, security-sensitive, or hard-to-reverse actions.
triggers:
- Any gated action is about to occur.
- Strict Change risk phase.
loads: {}
outputs:
- risk category
- approval prompt when needed
- safety gate status
safety:
  approval_required_for:
  - data deletion/migration/backfill
  - production config/deployments
  - secrets/credentials
  - shared git history rewrite
  - runtime dependency changes with behavior/security impact
  - auth/billing/public API contract changes
activation:
  automatic: true
  entrypoint: false
  user_direct: false
  invoked_by:
  - skills/command-discovery/SKILL.md#loads.conditional.high_risk_dependency_or_lockfile_action
  - skills/strict-change/SKILL.md#loads.immediate
  - skills/writing-plans/SKILL.md#loads.conditional.safety_gated_action
  routing_note: Users provide tasks; agents route from AGENTS.md through triage and phase triggers. Users do not manually invoke individual skills.
---
# Safety Gates

## Internal activation

This is a support skill. It is loaded by a mode, router, or another support skill when the relevant phase or condition is reached.

Users do not need to ask for this skill directly.

Use this skill before actions that may be destructive, production-affecting, security-sensitive, or hard to reverse.

Loading this skill is not the same as asking for approval. Approval is required only when a gated action is about to happen.

## Approval required

Require explicit user approval before:

- Deleting, truncating, overwriting, or migrating real data.
- Running database migrations, backfills, destructive scripts, or production jobs.
- Changing production configuration or deployment state.
- Modifying secrets, credentials, keys, tokens, or secret storage.
- Force-pushing, rewriting shared git history, deleting shared branches/tags.
- Adding/upgrading/removing runtime dependencies with behavior or security impact.
- Changing auth, permissions, billing, quotas, or public API contracts.
- Running install/dependency commands that may mutate lockfiles or shared environment state when that mutation is not already requested.

## Approval prompt

Use this shape:

```text
This triggers a safety gate: <risk>.
Planned action: <specific action>.
Expected impact: <impact>.
Rollback/mitigation: <plan>.
Please confirm before I proceed.
```

## No approval needed

Do not ask for approval for:

- Reading files.
- Inspecting diffs.
- Running local non-destructive tests.
- Drafting patches.
- Static analysis.
- Explaining a plan.

unless the environment or user instructions make these actions risky.

## Safety gate status

Track one of:

```text
Safety gate: not triggered
Safety gate: triggered, approval required before <action>
Safety gate: approved by user for <action>
Safety gate: blocked; approval not provided
```

Do not treat silence as approval.
