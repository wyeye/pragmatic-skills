# PSP tooling

`psp.py` is a dependency-free installer, verifier, recovery tool, and trace recorder. Project installs are lightweight: adapters and `.psp` state/traces live in the target project, while lifecycle commands run from this unpacked bundle or another global PSP runtime. `psp_schema.py` validates PSP-owned JSON Schema instances, `eval_runner.py` grades captured traces, `build_manifest.py` generates the Skill index, and `package_release.py` creates reproducible release archives.

Common commands:

```sh
python3 tools/psp.py verify-package
python3 tools/psp.py runtime install --dry-run
python3 tools/psp.py install --target /path/to/repo
python3 tools/psp.py doctor --target /path/to/repo
python3 tools/psp.py rollback --target /path/to/repo
python3 tools/eval_runner.py --self-test
```
