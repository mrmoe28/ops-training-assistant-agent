#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-all}"

cd "$SCRIPT_DIR"

case "$TARGET" in
  all)
    python3 ingest_local_sources.py
    python3 import_private_ops_data.py all
    ;;
  local)
    python3 ingest_local_sources.py
    ;;
  private)
    python3 import_private_ops_data.py all
    ;;
  jobs|clients|invoices|stats)
    python3 import_private_ops_data.py "$TARGET"
    ;;
  *)
    echo "Usage: $0 [all|local|private|jobs|clients|invoices|stats]" >&2
    exit 1
    ;;
esac

printf 'Refreshed %s at %s\n' "$TARGET" "$(date -Iseconds)"
