# Mode Matrix

This file is reference material. Do not load it during normal tasks unless you need to tune the workflow.

| Mode | Best for | Phase-triggered support | Typical verification |
|---|---|---|---|
| Fast Patch | Tiny, clear, low-risk edits | `command-discovery` only if a command is needed; `handoff` at completion | targeted check or static inspection |
| Exploration | Diagnosis, design, unclear requirements | `command-discovery` if command knowledge is part of investigation; `handoff` if no implementation | findings/options/recommendation |
| Standard Change | Normal behavior changes, bug fixes, moderate refactors | `project-agents-md` when AGENTS.md/instruction files are the target; `command-discovery` when commands are needed; `writing-plans` when multi-step; `tdd` when behavior changes; `evidence`; `verification`; `review`; `handoff` by phase | targeted tests plus broader checks as needed |
| Strict Change | Security, data, payments, public API, deployment, large refactors | `safety-gates` immediately; `command-discovery` when commands are needed; `worktree` conditionally; `writing-plans`; `evidence`; `tdd`; `verification`; `review`; `handoff` by phase | targeted + broad checks, rollback/mitigation notes |

## Philosophy

- The entry point should stay small.
- The triage skill should decide the mode.
- Mode skills should load support skills by phase, not upfront as a bundle.
- Commands should be discovered from the project, not hardcoded in the generic workflow.
- Evidence beats narrative.
- Safety gates must be wired into Strict Change.
- Worktrees are conditional isolation tools, not automatic ceremony.
- Subagents must be real, or explicitly replaced by role passes.

## Active-only direct support route

`workflow-retrospective` is not a primary mode. When the user explicitly requests a post-task PSP/workflow retrospective, the entry skill routes directly to `skills/workflow-retrospective/SKILL.md` before triage.

It is never triggered or offered automatically at normal completion. If the user also asks to implement its findings, finish the retrospective and then re-enter triage for the changes.

## Re-triage summary

- Fast -> Standard when behavior, tests, or multi-file scope appears.
- Fast/Standard -> Strict when high-risk triggers appear.
- Exploration -> implementation mode after findings clarify the work.
- Strict -> Standard only after risk is proven absent.
- Any mode -> Command Discovery when command evidence is needed and not already known.

## Command discovery summary

Use `skills/command-discovery/SKILL.md` when the workflow needs commands for install/test/lint/typecheck/build/run-local and no exact command is already known.

Command evidence should include:

- command
- cwd
- source
- confidence
- run policy


## User contract summary

Users provide normal tasks. The agent starts from the entry skill and routes internally. Explicit active-only support intents may route directly; otherwise mode and support skills are selected by triage and phase triggers, not by user command.


## AGENTS.md maintenance summary

Use `skills/project-agents-md/SKILL.md` when creating, updating, migrating, improving, or refactoring project-specific agent instructions.

Passive missing-AGENTS detection should ask the user before writing. Existing PSP-managed blocks should be preserved and updated only through the installer.
