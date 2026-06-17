# AGENTS.md Maintenance

This reference explains how PSP maintains project-specific `AGENTS.md` content.

## Separation of ownership

PSP has two kinds of AGENTS.md content:

1. PSP-managed entry block, between `<!-- PSP:BEGIN -->` and `<!-- PSP:END -->`.
2. Project-owned instructions outside managed blocks.

The installer owns the PSP-managed block. The `project-agents-md` skill owns project-specific content outside managed blocks.

## Active trigger

Use `skills/project-agents-md/SKILL.md` when the user asks to create, update, migrate, improve, or refactor AGENTS.md or repository agent instructions.

## Passive trigger

If a coding agent workflow discovers no AGENTS.md, or only a generic PSP block with no project-specific guidance, it should ask once whether the user wants project-specific AGENTS.md content generated.

Passive detection must not silently write files.

## Refactor rules

- Preserve PSP and other tool-managed blocks.
- Preserve safety constraints unless the user explicitly approves their removal.
- Replace guessed commands with evidence-based commands or `not discovered`.
- Keep the file short; link to project docs when possible.
- Report all unverifiable project facts.
