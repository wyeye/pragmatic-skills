# Host adapters

Adapters expose only the canonical PSP entry contract. The workflow remains under `skills/` so host-specific files stay thin and replaceable.

The installer defaults to `--hosts auto`. `--hosts all`, `minimal`, `none`, and explicit comma-separated host names are also supported.
