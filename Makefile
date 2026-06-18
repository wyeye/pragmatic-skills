.PHONY: check test eval package clean

PYTHON ?= python3

check:
	$(PYTHON) -m compileall -q tools
	$(PYTHON) tools/build_manifest.py --check
	$(PYTHON) tools/psp.py verify-package --target .
	sh -n install.sh verify.sh

test:
	$(PYTHON) -m unittest discover -s tests -v

eval:
	$(PYTHON) tools/psp.py eval validate --target .
	$(PYTHON) tools/psp.py eval self-test --target .
	$(PYTHON) tools/eval_runner.py --self-test --summary

package: check test eval
	$(PYTHON) tools/package_release.py --output-dir dist

clean:
	rm -rf build dist .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
