# Agent Install Guide

This document is for coding agents asked to install Pragmatic Skills Pack into a repository.

## Default path

Use the shell installer when shell execution is available:

```bash
sh /path/to/pragmatic-skills-pack/install.sh --target /path/to/repo
```

When the agent is already operating inside the target repository:

```bash
sh /path/to/pragmatic-skills-pack/install.sh
```

The default `install` command is idempotent. It installs PSP when absent and upgrades PSP when an existing installation is detected.

## Verify after installation

```bash
sh /path/to/pragmatic-skills-pack/install.sh --verify --target /path/to/repo
```

or from the target repository after installation:

```bash
python3 .psp/bin/psp.py verify --target .
```

## Agent behavior contract

- Prefer `install.sh`; do not hand-copy files when shell is available.
- Do not ask the user which internal skill to install or call.
- Preserve existing project instructions outside the PSP managed block in `AGENTS.md`.
- If conflicts are reported, do not overwrite them silently. Report the conflict path under `.psp/conflicts/` and summarize what needs manual review.
- Report the exact command run and the verifier result.
- If shell execution is unavailable, use the manual fallback below and clearly state that the shell installer was not run.

## Manual fallback when shell is unavailable

Only use this fallback when commands cannot be executed.

1. Copy `skills/` into the target repository.
2. Copy `reference/` into the target repository.
3. Insert the PSP block from package `AGENTS.md` into target `AGENTS.md`, preserving existing content outside the block.
4. Copy `tools/psp.py` to `.psp/bin/psp.py` if file operations are available.
5. Do not claim the install is hash-managed unless `.psp/install.json` was created by the installer.
6. In the final response, say the install was manual and recommend running:

```bash
sh /path/to/pragmatic-skills-pack/install.sh --target /path/to/repo
```

for full state tracking and upgrade safety.

## Multi-agent host adapters

When a user asks an agent to install PSP, prefer the package shell entrypoint and pass hosts explicitly when the user names tools:

```bash
sh /path/to/pragmatic-skills-pack/install.sh --target . --hosts claude,codex,opencode,hermes
sh /path/to/pragmatic-skills-pack/install.sh --verify --target .
```

Do not hand-copy host adapter files unless `install.sh` is unavailable. Preserve existing content outside PSP managed blocks.
