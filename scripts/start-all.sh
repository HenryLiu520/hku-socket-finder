#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
"$ROOT/start-backend.sh"
"$ROOT/start-frontend.sh"
echo
echo "Open http://localhost:5175  (password demo1234)"
