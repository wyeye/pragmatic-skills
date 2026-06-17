# Install, Verify, and Upgrade

Pragmatic Skills Pack is shell-first for users and agent installers.

## One command

From the target repository:

```bash
sh /path/to/pragmatic-skills-pack/install.sh
```

Or from anywhere:

```bash
sh /path/to/pragmatic-skills-pack/install.sh --target /path/to/repo
```

The default `install` command is idempotent. It installs PSP when absent and upgrades PSP when an existing installation is detected.

## Commands

```bash
# Check the unpacked package before using it
sh /path/to/pragmatic-skills-pack/install.sh --check

# Install or upgrade into a repository
sh /path/to/pragmatic-skills-pack/install.sh --target /path/to/repo

# Install and create an optional project profile template
sh /path/to/pragmatic-skills-pack/install.sh --target /path/to/repo --profile

# Verify an installed repository
sh /path/to/pragmatic-skills-pack/install.sh --verify --target /path/to/repo

# Show installed version and drift
sh /path/to/pragmatic-skills-pack/install.sh --status --target /path/to/repo

# Require an existing install before upgrading
sh /path/to/pragmatic-skills-pack/install.sh upgrade --target /path/to/repo
```

After installation, the verifier is also copied into the target repository:

```bash
python3 .psp/bin/psp.py verify --target .
```

`install.sh` delegates to `tools/psp.py`, which is dependency-free and uses only the Python standard library.

## Agent install

Give the agent the unpacked package and ask it to use the shell installer:

```text
Install Pragmatic Skills Pack into the current repository using the package's install.sh. Verify afterward. Preserve existing AGENTS.md content outside the PSP managed block and report conflicts instead of overwriting them.
```

Detailed agent instructions are in `AGENT-INSTALL.md` and `reference/AGENT-INSTALL.md`.

## What gets installed

The installer manages:

- `skills/`
- `reference/`
- a managed PSP block in `AGENTS.md`
- `.psp/install.json`
- `.psp/bin/psp.py`

Package docs such as the release `README.md`, `README.zh.md`, and `TREE.txt` remain in the zip and are not copied over project-owned files.

`AGENTS.md` is handled as a managed block between markers:

```text
<!-- PSP:BEGIN -->
...
<!-- PSP:END -->
```

Existing project instructions outside that block are preserved.

## Upgrade policy

Upgrade is safe by default.

The tool records hashes for installed PSP-managed files in `.psp/install.json`. During upgrade:

- files that are missing are copied;
- files that are PSP-managed and unchanged are replaced with the new package version;
- files that already match the new package are adopted;
- files modified by the user are not overwritten;
- conflicting new versions are written under `.psp/conflicts/<timestamp>/` for manual review;
- replaced files are backed up under `.psp/backups/<timestamp>/`;
- obsolete managed files are removed only when unchanged from the previous managed version.

Use `--force` only when you intentionally want to overwrite conflicts. Even then, the previous files are backed up first.

## Exit codes

- `0`: success
- `1`: verification failed
- `2`: invalid command, invalid package, missing runtime, or refused downgrade
- `3`: conflict detected; no overwrite performed

## Notes

The installer never downloads dependencies, never contacts the network, and never runs project install/test/build commands. It only installs and validates the skill pack files.

## Host adapters

Use `--hosts` to choose which coding-agent integrations are installed.

```bash
sh install.sh --hosts all      # default: Claude, Codex, OpenCode, Hermes, Gemini, Copilot, Cursor
sh install.sh --hosts auto     # AGENTS + .agents entry + detected adapters
sh install.sh --hosts minimal  # only AGENTS + .agents entry
sh install.sh --hosts none     # canonical PSP only, no host adapter files
sh install.sh --hosts claude,codex,opencode
```

Installed adapter files are managed like other PSP files when they are dedicated PSP files. Shared instruction files such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md` use PSP managed blocks so existing project content outside the block is preserved.

Upgrade keeps the same safety behavior: unchanged managed adapter files are replaced, user-modified adapter files become conflicts unless `--force` is used, and shared instruction files only update the PSP block.
