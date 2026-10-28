#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/logs"
echo "[frontend] starting ..."
( cd "$ROOT/frontend" && nohup npm run dev > "$ROOT/logs/frontend.log" 2>&1 & echo $! > "$ROOT/logs/frontend.pid" )
for _ in $(seq 1 60); do
  if curl -s -o /dev/null --max-time 1 http://localhost:5175/; then
    echo "[frontend] up on http://localhost:5175"
    exit 0
  fi
  sleep 1
done
echo "[frontend] did not come up; last lines:" >&2
tail -20 "$ROOT/logs/frontend.log" >&2
exit 1
