## Change

Describe the user-visible behavior and affected workflow phase.

## Evidence

- [ ] `python3 tools/psp.py verify-package --target .`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `python3 tools/psp.py eval self-test --target .`
- [ ] New or changed behavior has positive, negative, and failure eval coverage.
- [ ] Safety, compatibility, upgrade, and licensing implications are documented.

## Compatibility

List tested hosts and versions. Do not promote a host support level without captured behavioral runs.
