---
name: psp-entry
description: Claude Code entry adapter for Pragmatic Skills Pack repository workflows.
license: Mixed-origin; see repository LICENSE
compatibility: Claude Code projects that discover .claude/skills.
metadata:
  psp-adapter: claude-entry
  psp-version: 2.0.2
---

# Pragmatic Skills Pack entry

Use the canonical Pragmatic Skills Pack workflow. Prefer a project-local `skills/using-pragmatic-skills/SKILL.md` only when it exists; otherwise load the PSP skills from the host-installed bundle or global PSP runtime. Preserve project instructions outside installer-managed blocks and never fabricate execution evidence. If the PSP runtime is unavailable, follow the same workflow text as far as the host can support and report that structured tracing is not enabled.
