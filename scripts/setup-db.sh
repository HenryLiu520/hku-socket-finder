#!/usr/bin/env bash
# 确保有一个可用的 PostgreSQL，并建好 socketfinder 库。可以重复运行（幂等）。
#   1) 已经设置了 SF_DB_URL       -> 只检查能不能连上
#   2) 有 .env 且能连上           -> 直接返回
#   3) 有 docker                 -> docker compose up -d db
#   4) 否则                      -> 在 ./db/pgdata 起一个本项目专属的集群
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

say() { printf '[db] %s\n' "$*"; }
fail() { printf '[db] %s\n' "$*" >&2; exit 1; }
port_busy() { lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }
reachable() { pg_isready -h 127.0.0.1 -p "$1" >/dev/null 2>&1; }

# --- 1) 外部数据库 ---
if [ -n "${SF_DB_URL:-}" ]; then
  say "using SF_DB_URL=$SF_DB_URL"
  pg_isready -d "$SF_DB_URL" >/dev/null 2>&1 || fail "SF_DB_URL is set but the server is not reachable"
  say "reachable"
  exit 0
fi

# --- 2) 之前已经配好的本地库 ---
if [ -f .env ]; then
  # shellcheck disable=SC1091
  set -a; . ./.env; set +a
  PORT_FROM_ENV="${SF_DB_URL##*:}"; PORT_FROM_ENV="${PORT_FROM_ENV%%/*}"
  if reachable "$PORT_FROM_ENV"; then
    say "already up on port $PORT_FROM_ENV"
    exit 0
  fi
fi

# --- 3) Docker ---
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  say "starting postgres in docker"
  docker compose up -d db >/dev/null
  for _ in $(seq 1 60); do
    docker compose exec -T db pg_isready -U socketfinder -d socketfinder >/dev/null 2>&1 && break
    sleep 1
  done
  cat > .env <<'ENV'
SF_DB_URL=jdbc:postgresql://localhost:5433/socketfinder
SF_DB_USER=socketfinder
SF_DB_PASSWORD=socketfinder
ENV
  say "postgres is up on localhost:5433 (user socketfinder)"
  exit 0
fi

# --- 4) 本机 PostgreSQL，专属集群 ---
PGBIN=""
for cand in /opt/homebrew/opt/postgresql@17/bin /opt/homebrew/bin /usr/local/opt/postgresql@17/bin /usr/lib/postgresql/17/bin; do
  [ -x "$cand/initdb" ] && PGBIN="$cand" && break
done
if [ -z "$PGBIN" ] && command -v initdb >/dev/null 2>&1; then PGBIN="$(dirname "$(command -v initdb)")"; fi
[ -n "$PGBIN" ] || fail "no PostgreSQL found. Install postgresql@17 or Docker, or set SF_DB_URL"
export PATH="$PGBIN:$PATH"

DATA="$ROOT/db/pgdata"
LOG="$ROOT/db/pg.log"
mkdir -p "$ROOT/db"

if [ ! -f "$DATA/PG_VERSION" ]; then
  say "creating a cluster in db/pgdata"
  export LC_ALL="${LC_ALL:-C}" LANG="${LANG:-C}"
  initdb -D "$DATA" -U "$(whoami)" --auth=trust --encoding=UTF8 >/dev/null
fi

# 选一个端口：优先 SF_DB_PORT，其次 5433，被占就往后找
PORT="${SF_DB_PORT:-5433}"
for _ in 1 2 3 4 5 6; do
  if ! port_busy "$PORT" || pg_ctl -D "$DATA" status >/dev/null 2>&1; then break; fi
  say "port $PORT is taken by something else, trying $((PORT+1))"
  PORT=$((PORT+1))
done

if ! pg_ctl -D "$DATA" status >/dev/null 2>&1; then
  say "starting the cluster on port $PORT"
  pg_ctl -D "$DATA" -l "$LOG" -o "-p $PORT -h 127.0.0.1" start >/dev/null
fi
for _ in $(seq 1 30); do reachable "$PORT" && break; sleep 1; done
reachable "$PORT" || { tail -20 "$LOG" >&2 || true; fail "cluster did not start"; }

DBUSER="$(whoami)"
psql -h 127.0.0.1 -p "$PORT" -d postgres -tAc "select 1 from pg_database where datname='socketfinder'" | grep -q 1 \
  || createdb -h 127.0.0.1 -p "$PORT" socketfinder

cat > .env <<ENV
SF_DB_URL=jdbc:postgresql://localhost:$PORT/socketfinder
SF_DB_USER=$DBUSER
SF_DB_PASSWORD=
ENV
say "postgres is up on localhost:$PORT, database socketfinder, user $DBUSER"
