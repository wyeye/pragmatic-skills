# Mode Matrix

This file is reference material. Do not load it during normal tasks unless you need to tune the workflow.

| Mode | Best for | Phase-triggered support | Typical verification |
|---|---|---|---|
| Fast Patch | Tiny, clear, low-risk edits | `command-discovery` only if a command is needed; `handoff` at completion | targeted check or static inspection |
| Exploration | Diagnosis, project-fact discovery, brainstorming/design-only requests | `requirements-and-design` after facts are known when intent/scope/design must be settled; `command-discovery` if commands are part of investigation; `handoff` if no implementation | findings, Requirement Brief when used, recommendation |
| Standard Change | Normal behavior changes, bug fixes, moderate refactors | `exploration` for missing facts; `requirements-and-design` when scope/criteria/design are unresolved; `project-agents-md` for instruction targets; `command-discovery`; `writing-plans`; `tdd`; `evidence`; `verification`; `review`; `handoff` by phase | acceptance-criteria-driven targeted tests plus broader checks as needed |
| Strict Change | Security, data, payments, public API, deployment, large refactors | `safety-gates` immediately; `exploration` when facts are unclear; `requirements-and-design` for material decisions; `command-discovery`; `worktree` conditionally; `writing-plans`; `evidence`; `tdd`; `verification`; `review`; `handoff` by phase | criteria coverage + targeted/broad checks + rollback/mitigation notes |

## Philosophy

- The entry point should stay small.
- The triage skill should decide the mode.
- Mode skills should load support skills by phase, not upfront as a bundle.
- Exploration discovers facts; Requirements and Design settles intended behavior and decisions.
- Clear, tiny work should not pay a brainstorming/confirmation tax.
- Commands should be discovered from the project, not hardcoded in the generic workflow.
- Evidence beats narrative.
- Safety gates must be wired into Strict Change.
- Requirement confirmation and safety approval are separate gates.
- Worktrees are conditional isolation tools, not automatic ceremony.
- Subagents must be real, or explicitly replaced by role passes.

## Requirements and design summary

Use `skills/requirements-and-design/SKILL.md` when:

- The user explicitly asks to brainstorm, clarify requirements, compare designs, define acceptance criteria, or confirm before coding.
- A feature/change lacks clear scope, non-goals, constraints, or observable success criteria.
- Multiple viable designs materially differ.
- Planning would depend on risky assumptions.

Skip it for tiny, fully specified, low-risk work.

Its confirmation states are:

- `confirmed`
- `conditionally confirmed`
- `safe assumptions used`
- `blocked on user decision`

Implementation must not proceed from the last state.

## Active-only direct support route

`workflow-retrospective` is not a primary mode. When the user explicitly requests a post-task PSP/workflow retrospective, the entry skill routes directly to `skills/workflow-retrospective/SKILL.md` before triage.

It is never triggered or offered automatically at normal completion. If the user also asks to implement its findings, finish the retrospective and then re-enter triage for the changes.

## Re-triage summary

- Fast -> Standard when behavior, tests, requirement decisions, or multi-file scope appears.
- Fast/Standard -> Strict when high-risk triggers appear.
- Exploration -> implementation mode after findings and requirement/design decisions clarify the work.
- Strict -> Standard only after risk is proven absent.
- Any mode -> Command Discovery when command evidence is needed and not already known.
- Any implementation mode -> Requirements and Design when material scope/design uncertainty appears before editing.

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
