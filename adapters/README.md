# Pragmatic Skills Pack host adapters

PSP installs a common `AGENTS.md` contract and a single native entry adapter where a host has a native skill or rule location.

The internal workflow remains in `skills/`. Native adapters are intentionally thin so users only expose one entry skill to the host and the workflow continues through phase-triggered progressive disclosure.

Supported adapters:

- `agents`: `AGENTS.md` plus `.agents/skills/using-pragmatic-skills/SKILL.md`; works with Codex-style Agent Skills and OpenCode's agent-compatible skill discovery.
- `claude`: `CLAUDE.md` managed block plus `.claude/skills/psp-claude-entry/SKILL.md`.
- `opencode`: optional `.opencode/commands/psp.md`; OpenCode can use the default `.agents/skills` entry.
- `hermes`: uses the default `AGENTS.md` entry.
- `gemini`: `GEMINI.md` managed block importing `AGENTS.md`.
- `copilot`: `.github/copilot-instructions.md` managed block; Copilot can also use `AGENTS.md`.
- `cursor`: `.cursor/rules/pragmatic-skills-pack.mdc` project rule.

Use `sh install.sh --hosts all` (default), `--hosts auto`, `--hosts minimal`, `--hosts none`, or `--hosts agents,claude,opencode`.
