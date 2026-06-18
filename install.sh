#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3}

case "${1:-}" in
  --check)
    shift
    exec "$PYTHON" "$ROOT/tools/psp.py" verify-package --target "$ROOT" "$@"
    ;;
  --verify)
    shift
    exec "$PYTHON" "$ROOT/tools/psp.py" verify "$@"
    ;;
  *)
    exec "$PYTHON" "$ROOT/tools/psp.py" install "$@"
    ;;
esac
