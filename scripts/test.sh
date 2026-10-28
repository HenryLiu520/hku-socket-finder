#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "== backend unit tests =="
( cd "$ROOT/backend" && mvn -q test )
echo "== end to end over HTTP (needs the backend running) =="
python3 "$ROOT/scripts/e2e.py"
