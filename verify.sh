#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

# With no args, verify the unpacked package. With target args, verify an install.
if [ "$#" -eq 0 ]; then
  exec sh "$SCRIPT_DIR/install.sh" verify-package
fi

case "$1" in
  --target|-t)
    exec sh "$SCRIPT_DIR/install.sh" verify "$@"
    ;;
  --package|--check|--check-package|--verify-package)
    shift
    exec sh "$SCRIPT_DIR/install.sh" verify-package "$@"
    ;;
  *)
    exec sh "$SCRIPT_DIR/install.sh" verify "$@"
    ;;
esac
