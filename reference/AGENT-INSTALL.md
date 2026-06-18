# Installing with an agent

Give the agent the unpacked package and ask it to run `install.sh` against the target repository, preserve all content outside PSP-managed blocks, stop on conflicts, and run the installed verifier afterward.

The agent must not use `--force`, uninstall, rollback, or a non-default host set unless the user explicitly requests it or the conflict has been reviewed.
