# Agent installation contract

From the unpacked package, run:

```sh
sh install.sh --target /path/to/repository
python3 /path/to/repository/.psp/bin/psp.py verify --target /path/to/repository
python3 /path/to/repository/.psp/bin/psp.py doctor --target /path/to/repository
```

Preserve all project content outside PSP-managed blocks. Stop and report the generated conflict report instead of overwriting user-modified managed files. Use `--hosts auto` unless the user explicitly requests another adapter set.

Keep `.psp/legal/` with installed managed content; it records the bundle's mixed-origin licensing and upstream provenance.

The installed CLI uses `.psp/package.zip` for package-aware lifecycle commands; do not delete it while PSP remains installed.
