#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)/.."
"$ROOT/scripts/setup-db.sh"
"$ROOT/scripts/start-backend.sh"
"$ROOT/scripts/start-frontend.sh"
echo
echo "Open http://localhost:5175   (password demo1234)"
echo "Stop everything with ./scripts/stop-all.sh"
