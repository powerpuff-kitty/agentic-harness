#!/usr/bin/env sh
set -eu

COMMAND="${AGENTIC_HARNESS_COMMAND:-ah}"
PREFIX="${PREFIX:-/usr/local}"
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

usage() {
  cat <<EOF
Install Agentic Harness CLI.

Usage: ./install.sh [--command NAME] [--prefix DIR] [--binary PATH]

Options:
  --command NAME   Global command name (default: ${AGENTIC_HARNESS_COMMAND:-ah})
  --prefix DIR     Install prefix (default: ${PREFIX})
  --binary PATH    Install an existing precompiled ah binary

If --binary is omitted, the installer uses target/release/ah when present,
otherwise it builds the Rust binary with cargo.
EOF
}

BINARY=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --command) [ "$#" -ge 2 ] || { echo "--command requires a value" >&2; exit 2; }; COMMAND="$2"; shift 2 ;;
    --prefix) [ "$#" -ge 2 ] || { echo "--prefix requires a value" >&2; exit 2; }; PREFIX="$2"; shift 2 ;;
    --binary) [ "$#" -ge 2 ] || { echo "--binary requires a value" >&2; exit 2; }; BINARY="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$COMMAND" in ""|*/*|*" "*) echo "Invalid command name: $COMMAND" >&2; exit 2 ;; esac

if [ -z "$BINARY" ]; then
  if [ -x "$ROOT/target/release/ah" ]; then
    BINARY="$ROOT/target/release/ah"
  else
    command -v cargo >/dev/null 2>&1 || { echo "No precompiled binary found and cargo is not installed. Download an Agentic Harness release binary and pass --binary PATH." >&2; exit 127; }
    cargo build --release --manifest-path "$ROOT/Cargo.toml"
    BINARY="$ROOT/target/release/ah"
  fi
fi

[ -f "$BINARY" ] || { echo "Binary not found: $BINARY" >&2; exit 2; }
mkdir -p "$PREFIX/bin"
cp "$BINARY" "$PREFIX/bin/$COMMAND"
chmod +x "$PREFIX/bin/$COMMAND"
echo "Installed Agentic Harness as '$COMMAND' at $PREFIX/bin/$COMMAND"
