# PSP tooling

`psp.py` is a dependency-free installer, verifier, recovery tool, and trace recorder. Installed projects retain a deterministic `.psp/package.zip`, allowing package-aware lifecycle commands to run without the original archive. `psp_schema.py` validates PSP-owned JSON Schema instances, `eval_runner.py` grades captured traces, `build_manifest.py` generates the Skill index, and `package_release.py` creates reproducible release archives.

Common commands:

```sh
python3 tools/psp.py verify-package
python3 tools/psp.py install --target /path/to/repo
python3 tools/psp.py doctor --target /path/to/repo
python3 tools/psp.py rollback --target /path/to/repo
python3 tools/eval_runner.py --self-test
```
