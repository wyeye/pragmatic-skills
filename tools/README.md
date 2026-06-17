# PSP Tooling

`tools/psp.py` is the dependency-free implementation behind the public shell installer.

Most users should call:

```bash
sh install.sh --target /path/to/repo
```

or, from the target repository:

```bash
sh /path/to/pragmatic-skills-pack/install.sh
```

Direct Python commands are still available for automation:

```bash
python3 tools/psp.py verify-package
python3 tools/psp.py install --target /path/to/repo
python3 tools/psp.py verify --target /path/to/repo
python3 tools/psp.py status --target /path/to/repo
python3 tools/psp.py upgrade --target /path/to/repo
```

After installation, a copy of the verifier is installed at:

```text
.psp/bin/psp.py
```

You can then run from the target repository:

```bash
python3 .psp/bin/psp.py verify --target .
```

## Upgrade behavior

- Manages `skills/` and `reference/` files with hashes in `.psp/install.json`.
- Updates only the PSP managed block in `AGENTS.md`, or appends it to a project-owned `AGENTS.md`.
- Does not overwrite project README files.
- Backs up overwritten files under `.psp/backups/<timestamp>/`.
- Writes conflicts under `.psp/conflicts/<timestamp>/` and refuses to clobber user edits unless `--force` is used.
- Never overwrites `.psp/project-profile.md`.

The tool uses only the Python standard library.
