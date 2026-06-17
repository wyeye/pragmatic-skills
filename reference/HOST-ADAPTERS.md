# Host Adapters

Last reviewed: 2026-06-17.

Pragmatic Skills Pack uses one canonical internal workflow and thin host adapters. The canonical files are:

- `AGENTS.md`
- `skills/`
- `reference/`

Host adapters should point to that canonical workflow. They should not duplicate the entire workflow.

## Default install

`sh install.sh --target <repo>` installs all supported adapters by default:

- Common / Codex / OpenCode / Hermes: `AGENTS.md` plus `.agents/skills/using-pragmatic-skills/SKILL.md`
- Claude Code: `CLAUDE.md` plus `.claude/skills/psp-claude-entry/SKILL.md`
- Gemini CLI: `GEMINI.md`
- GitHub Copilot: `.github/copilot-instructions.md`
- Cursor: `.cursor/rules/pragmatic-skills-pack.mdc`
- OpenCode convenience command: `.opencode/commands/psp.md`

## Duplicate native skill names

Some hosts scan multiple skill directories. OpenCode can scan `.opencode/skills`, `.claude/skills`, and `.agents/skills`. To avoid duplicate native skill names when Claude and OpenCode are both used in one repo:

- `.agents/skills/using-pragmatic-skills/SKILL.md` uses `name: using-pragmatic-skills`.
- `.claude/skills/psp-claude-entry/SKILL.md` uses `name: psp-claude-entry`.
- PSP does not install `.opencode/skills/using-pragmatic-skills` by default because `.agents/skills` is already supported by OpenCode.

## Install modes

```bash
sh install.sh --target .                  # all adapters, safe default
sh install.sh --target . --hosts auto     # common entry plus adapters detected from existing project files
sh install.sh --target . --hosts minimal  # AGENTS.md + .agents native entry only
sh install.sh --target . --hosts claude,codex,opencode
sh install.sh --target . --no-host-adapters
```

## Agent usage

Users do not invoke individual PSP skills. Users describe normal tasks. Host adapters route the agent to `skills/using-pragmatic-skills/SKILL.md`, which routes through triage, one primary mode, and support skills by phase trigger.
