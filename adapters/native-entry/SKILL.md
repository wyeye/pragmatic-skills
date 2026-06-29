---
name: using-pragmatic-skills
description: Native host entry adapter for Pragmatic Skills Pack repository workflows.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible hosts that discover .agents/skills.
metadata:
  psp-adapter: native-entry
  psp-version: 2.0.2
---

# Pragmatic Skills Pack entry

Use the Pragmatic Skills Pack entry workflow. Prefer a project-local `skills/using-pragmatic-skills/SKILL.md` only when it exists; otherwise load the PSP skills from the host-installed bundle or global PSP runtime. Users describe tasks normally; route internally, choose exactly one primary mode, and load support skills by phase trigger. Do not ask users to choose internal skills. If the PSP runtime is unavailable, follow the same workflow text as far as the host can support and report that structured tracing is not enabled.
