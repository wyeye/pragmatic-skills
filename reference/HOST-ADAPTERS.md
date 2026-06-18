# Host adapter policy

The canonical workflow lives under `skills/`. Adapters expose only the entry
contract and should remain thin, replaceable discovery layers.

| Host | Discovery | Current label |
|---|---|---|
| Agent Skills-style | `.agents/skills` and `AGENTS.md` | Package-tested, behavioral evaluation pending |
| Codex-style | `AGENTS.md` and Agent Skills | Package-tested, behavioral evaluation pending |
| Claude Code | `CLAUDE.md` and `.claude/skills` | Experimental |
| OpenCode | `.agents/skills` and optional command | Experimental |
| Hermes | `AGENTS.md` | Adapter-only |
| Gemini CLI | `GEMINI.md` | Adapter-only |
| GitHub Copilot | `.github/copilot-instructions.md` | Adapter-only |
| Cursor | `.cursor/rules/*.mdc` | Adapter-only |

Definitions:

- **Package-tested:** installation, file layout, integrity, drift, uninstall,
  and rollback paths are covered by automated package tests.
- **Experimental:** the adapter is implemented but recurring host-version
  behavioral evaluation has not established a stable pass rate.
- **Adapter-only:** instruction injection exists; runtime-enforced routing and a
  measured behavioral pass rate are not claimed.

Do not promote a host to behaviorally supported until published runs identify
host version, model, date, case count, raw trace provenance, safety results, and
regressions relative to the previous release.
