---
name: using-pragmatic-skills
description: Entry point for Pragmatic Skills Pack. Use for coding, debugging, review, planning, verification, or repository work; loads the internal workflow progressively from skills/using-pragmatic-skills/SKILL.md.
---

# Pragmatic Skills Pack — Native Entry Adapter

This is a thin host-native adapter, not the full workflow.

When this skill is activated:

1. Read the repository file `skills/using-pragmatic-skills/SKILL.md`.
2. Follow that entry skill exactly.
3. Continue routing through `skills/triage/SKILL.md`, then one primary mode, then support skills by phase trigger.
4. Do not ask the user to choose a skill or mode unless they are explicitly designing, debugging, or evaluating the skill system itself.
5. If `skills/using-pragmatic-skills/SKILL.md` is missing, report that the Pragmatic Skills Pack installation is incomplete and ask the user to run `sh install.sh --verify` from the package or `python3 .psp/bin/psp.py verify --target .` from the repository.

Users describe normal tasks. The agent performs internal routing.
