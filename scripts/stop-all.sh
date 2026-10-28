#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for name in frontend backend; do
  pidfile="$ROOT/logs/$name.pid"
  if [ -f "$pidfile" ]; then
    pid="$(cat "$pidfile")"
    if kill -0 "$pid" 2>/dev/null; then
      pkill -P "$pid" 2>/dev/null || true
      kill "$pid" 2>/dev/null || true
      echo "[$name] stopped (pid $pid)"
    fi
    rm -f "$pidfile"
  fi
done
