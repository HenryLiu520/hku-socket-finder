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
# 如果数据库是本项目自己起的集群，一并停掉
if [ -f "$ROOT/db/pgdata/PG_VERSION" ]; then
  for cand in /opt/homebrew/opt/postgresql@17/bin /opt/homebrew/bin; do
    [ -x "$cand/pg_ctl" ] && PGBIN="$cand" && break
  done
  if [ -n "${PGBIN:-}" ] && "$PGBIN/pg_ctl" -D "$ROOT/db/pgdata" status >/dev/null 2>&1; then
    "$PGBIN/pg_ctl" -D "$ROOT/db/pgdata" stop -m fast >/dev/null
    echo "[db] local cluster stopped"
  fi
fi
