#!/usr/bin/env sh
set -eu

COMMAND="${AGENTIC_HARNESS_COMMAND:-ah}"
PREFIX="${PREFIX:-/usr/local}"

usage() {
  cat <<EOF
Install Agentic Harness CLI.

Usage: ./install.sh [--command NAME] [--prefix DIR]

Options:
  --command NAME   Global command name (default: ${AGENTIC_HARNESS_COMMAND:-ah})
  --prefix DIR     Install prefix (default: ${PREFIX})

Environment:
  AGENTIC_HARNESS_COMMAND  Default command alias
  PREFIX                   Default install prefix
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --command)
      [ "$#" -ge 2 ] || { echo "--command requires a value" >&2; exit 2; }
      COMMAND="$2"; shift 2 ;;
    --prefix)
      [ "$#" -ge 2 ] || { echo "--prefix requires a value" >&2; exit 2; }
      PREFIX="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$COMMAND" in
  ""|*/*|*" "*) echo "Invalid command name: $COMMAND" >&2; exit 2 ;;
esac

BIN_DIR="$PREFIX/bin"
TARGET="$BIN_DIR/$COMMAND"
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

mkdir -p "$BIN_DIR"
cat > "$TARGET" <<EOF
#!/usr/bin/env sh
exec python3 "$ROOT/scripts/agentic.py" "\$@"
EOF
chmod +x "$TARGET"

echo "Installed Agentic Harness as '$COMMAND' at $TARGET"
