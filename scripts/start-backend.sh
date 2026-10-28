#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/logs"
[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a
PORT="${SF_PORT:-8081}"
if curl -s -o /dev/null --max-time 1 "http://127.0.0.1:$PORT/api/buildings"; then
  echo "[backend] already running on $PORT"
  exit 0
fi
echo "[backend] starting on $PORT ..."
( cd "$ROOT/backend" && nohup mvn -q spring-boot:run > "$ROOT/logs/backend.log" 2>&1 & echo $! > "$ROOT/logs/backend.pid" )
for _ in $(seq 1 120); do
  if curl -s -o /dev/null --max-time 1 "http://127.0.0.1:$PORT/api/buildings"; then
    echo "[backend] up on http://127.0.0.1:$PORT"
    exit 0
  fi
  sleep 1
done
echo "[backend] did not come up; last lines:" >&2
tail -25 "$ROOT/logs/backend.log" >&2
exit 1
