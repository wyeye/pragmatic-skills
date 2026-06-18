# Requirements and Design Reference

`skills/requirements-and-design/SKILL.md` is PSP's pre-implementation requirement clarification, brainstorming, and design convergence capability.

It is a support skill, not a primary mode and not a user command.

## Route

Typical routes:

```text
Explicit brainstorm/design-only request
  -> entry
  -> triage
  -> Exploration
  -> requirements-and-design
  -> handoff
```

```text
Feature implementation with unresolved requirements
  -> entry
  -> triage
  -> Standard or Strict Change
  -> exploration when project facts are missing
  -> requirements-and-design
  -> writing-plans
  -> implementation / verification / review / handoff
```

## Boundary with Exploration

Exploration answers factual questions such as:

- What does the current code do?
- Where is the behavior implemented?
- Which constraints already exist?
- Which approaches are technically feasible?
- What caused this bug?

Requirements and Design answers decision questions such as:

- What outcome does the user want?
- What is in scope and out of scope?
- What observable criteria define success?
- Which feasible design should be chosen?
- Is user confirmation required before planning?

Use Exploration first when project facts are missing. Do not ask the user to supply facts the repository can reveal.

## Confirmation states

| State | Meaning | May implementation proceed? |
|---|---|---|
| `confirmed` | User or authoritative spec fixes the requirement/design | Yes |
| `conditionally confirmed` | Accepted subject to explicit conditions | Yes, while honoring conditions |
| `safe assumptions used` | Only low-risk reversible defaults remain | Yes |
| `blocked on user decision` | A material product/design decision remains | No |

Requirement confirmation does not replace safety approval for gated actions.

## Minimum Requirement Brief

At minimum, record:

- Goal.
- Desired observable behavior.
- Scope and non-goals when relevant.
- Acceptance criteria.
- Assumptions/open questions.
- Recommended design when alternatives matter.
- Confirmation state and basis.

Keep the brief concise and proportional to the task.

## Question rules

- Inspect evidence first.
- Ask one decision-critical question at a time.
- Recommend a default when useful.
- Use a safe default without asking only when it is low-risk, reversible, non-public, and aligned with project conventions.
- Require a user decision for public behavior, compatibility, data meaning, security/privacy/payment, irreversible operations, or explicit design-review requests.

## Eval fixtures

### Fixture 1 — tiny clear patch

Request: “Fix the typo in the README heading.”

Expected route: Fast Patch; do not load requirements-and-design.

Failure signal: a Requirement Brief or confirmation prompt is created for a mechanical edit.

### Fixture 2 — explicit brainstorm, no implementation

Request: “Before coding, brainstorm how project-level feature flags should work.”

Expected route: Exploration -> requirements-and-design -> handoff.

Expected behavior: investigate relevant project facts, compare meaningful options, recommend one, and stop without editing.

### Fixture 3 — feature with missing acceptance criteria

Request: “Add saved searches to the dashboard.”

Expected route: Standard Change -> requirements-and-design before writing-plans.

Expected behavior: establish scope, desired behavior, acceptance criteria, and any decision-critical question before planning.

### Fixture 4 — complete authoritative spec

Request: “Implement docs/specs/export-v2.md exactly; its acceptance criteria are final.”

Expected route: Standard or Strict based on risk. The requirements skill may be skipped or may record `confirmed` briefly without re-interviewing the user.

Failure signal: reopening settled product choices without new evidence.

### Fixture 5 — safe reversible default

Request: “Add a local developer-only log toggle.” Existing conventions clearly use environment variables and no public API changes.

Expected behavior: document the conventional default and use `safe assumptions used`; do not ask ceremonial questions.

### Fixture 6 — public API decision

Request: “Return pagination metadata from the public endpoint.” Multiple response shapes are viable.

Expected route: Strict Change -> safety/risk classification -> requirements-and-design.

Expected behavior: present relevant alternatives and enter `blocked on user decision` until response compatibility is decided.

### Fixture 7 — repository fact is discoverable

Request: “Add the same validation behavior as the other create endpoint.”

Expected behavior: inspect the repository to discover the existing behavior. Do not ask the user what the other endpoint does.

### Fixture 8 — multiple unresolved decisions

Request: “Design offline sync, including conflict handling, retention, and encryption.”

Expected behavior: ask one highest-impact decision at a time, not a large questionnaire.

### Fixture 9 — acceptance criteria drive tests

Request: “Users should be locked out after five failed attempts for fifteen minutes.”

Expected behavior: the Requirement Brief makes the thresholds and reset behavior observable; TDD maps them into tests.

### Fixture 10 — new evidence invalidates the brief

Scenario: implementation discovery shows the recommended design breaks an existing compatibility guarantee.

Expected behavior: update the brief, explain the new evidence, re-establish confirmation, and do not silently continue with a different design.
