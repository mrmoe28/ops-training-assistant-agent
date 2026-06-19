#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"
export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
./refresh_all.sh "${1:-all}"
python3 server.py
