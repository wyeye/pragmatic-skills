#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TOOL="$SCRIPT_DIR/tools/psp.py"

usage() {
  cat <<'EOF'
Pragmatic Skills Pack installer

Preferred one-command usage:
  # From the target repository:
  sh /path/to/pragmatic-skills-pack/install.sh

  # Or from anywhere:
  sh /path/to/pragmatic-skills-pack/install.sh --target /path/to/repo

The same install command is safe to re-run and will upgrade an existing PSP install.

Host adapters:
  --hosts all        Default. AGENTS, Codex, Claude, OpenCode, Hermes, Gemini, Copilot, Cursor.
  --hosts auto       Install AGENTS/.agents entry and detected host adapters.
  --hosts minimal    Only AGENTS.md + .agents/skills entry.
  --hosts none       Only AGENTS.md + canonical skills/reference; no host adapter files.
  --hosts claude,codex,opencode
                     Explicit comma-separated host adapters.

Supported host names:
  agents, codex, claude, opencode, hermes, gemini, copilot, cursor

Modes:
  install (default)       Install or upgrade PSP into the target repo
  upgrade                 Upgrade an existing PSP install from this package
  verify                  Verify an installed target repo
  status                  Show target install status
  verify-package          Verify this unpacked PSP package

Flag aliases:
  --upgrade               Same as: upgrade
  --verify                Same as: verify
  --status                Same as: status
  --check, --check-package Same as: verify-package
  --all-hosts             Same as: --hosts all
  --no-host-adapters      Same as: --hosts none

Examples:
  sh install.sh --target ~/src/my-repo
  sh install.sh --target ~/src/my-repo --hosts claude,codex,opencode
  sh install.sh --target ~/src/my-repo --all-hosts
  sh install.sh --target ~/src/my-repo --no-host-adapters
  cd ~/src/my-repo && sh ~/Downloads/pragmatic-skills-pack/install.sh
  sh install.sh --check
  sh install.sh --verify --target ~/src/my-repo
  sh install.sh --status --target ~/src/my-repo
  sh install.sh upgrade --target ~/src/my-repo --hosts all

Additional flags such as --force, --dry-run, --profile, and --allow-downgrade
are passed through to the underlying PSP tool.
EOF
}

if [ ! -f "$TOOL" ]; then
  echo "PSP installer error: tools/psp.py not found next to install.sh" >&2
  echo "Expected: $TOOL" >&2
  exit 2
fi

PYTHON_BIN=${PYTHON:-}
if [ -z "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN=python
  else
    echo "PSP installer error: python3 or python is required." >&2
    exit 2
  fi
fi

CMD=install
PASS_ARGS=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    install|upgrade|verify|status|verify-package)
      CMD=$1
      shift
      ;;
    --upgrade)
      CMD=upgrade
      shift
      ;;
    --verify)
      CMD=verify
      shift
      ;;
    --status)
      CMD=status
      shift
      ;;
    --check|--check-package|--verify-package)
      CMD=verify-package
      shift
      ;;
    --all-hosts)
      PASS_ARGS="$PASS_ARGS --hosts all"
      shift
      ;;
    --no-host-adapters)
      PASS_ARGS="$PASS_ARGS --hosts none"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      # Preserve arguments safely by rebuilding via set below.
      break
      ;;
  esac
done

# Safety: when the user runs ./install.sh from inside the package directory
# without a target, do not install the package into itself by accident.
HAS_TARGET=0
for arg in "$@"; do
  if [ "$arg" = "--target" ] || [ "$arg" = "-t" ]; then
    HAS_TARGET=1
  fi
done

if { [ "$CMD" = "install" ] || [ "$CMD" = "upgrade" ]; } && [ "$HAS_TARGET" -eq 0 ]; then
  PWD_REAL=$(pwd -P)
  SCRIPT_REAL=$(cd "$SCRIPT_DIR" && pwd -P)
  if [ "$PWD_REAL" = "$SCRIPT_REAL" ]; then
    echo "PSP installer refused to install into the package source directory." >&2
    echo "Run from your target repo:" >&2
    echo "  cd /path/to/repo && sh $SCRIPT_DIR/install.sh" >&2
    echo "Or pass an explicit target:" >&2
    echo "  sh $SCRIPT_DIR/install.sh --target /path/to/repo" >&2
    exit 2
  fi
fi

# shellcheck disable=SC2086
exec "$PYTHON_BIN" "$TOOL" "$CMD" $PASS_ARGS "$@"
