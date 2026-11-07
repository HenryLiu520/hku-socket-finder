#!/usr/bin/env bash
# Bring up the demo in one command: database, API, web app, and a known good state.
#
#   ./scripts/demo.sh            reset the data, then start what is not running
#   ./scripts/demo.sh --no-reset start without touching the data
#   ./scripts/demo.sh --lan      also listen on the local network (phone on the same Wi-Fi)
set -euo pipefail
cd "$(dirname "$0")/.."

RESET=1
LAN=0
for arg in "$@"; do
  case "$arg" in
    --no-reset) RESET=0 ;;
    --lan) LAN=1 ;;
    *) echo "unknown option: $arg"; exit 1 ;;
  esac
done

DB_PORT="${SF_DB_PORT:-5433}"
DB_NAME="${SF_DB_NAME:-socketfinder}"
DB_USER="${SF_DB_USER:-ran}"
API_PORT="${SF_PORT:-8081}"
WEB_PORT="${SF_WEB_PORT:-5175}"

say() { printf '\033[1m%s\033[0m\n' "$*"; }

# 1. database
if ! pg_isready -h 127.0.0.1 -p "$DB_PORT" >/dev/null 2>&1; then
  say "starting the database"
  echo "db not running: start postgres on 5433 first"
fi
pg_isready -h 127.0.0.1 -p "$DB_PORT" >/dev/null || { echo "database is not up on $DB_PORT"; exit 1; }

# 2. api
if ! curl -fsS "http://127.0.0.1:$API_PORT/api/buildings" >/dev/null 2>&1; then
  say "starting the API on $API_PORT"
  (cd backend && nohup java -jar target/socket-finder-0.1.0.jar >/tmp/sf-api.log 2>&1 &) || true
  for _ in $(seq 1 40); do
    curl -fsS "http://127.0.0.1:$API_PORT/api/buildings" >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -fsS "http://127.0.0.1:$API_PORT/api/buildings" >/dev/null || { echo "API did not come up, see /tmp/sf-api.log"; exit 1; }

# 3. data
if [ "$RESET" = "1" ]; then
  say "resetting the demo data"
  psql -h 127.0.0.1 -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -q -f scripts/demo-reset.sql >/dev/null
fi

# 4. web
if ! curl -fsS "http://localhost:$WEB_PORT/" >/dev/null 2>&1; then
  say "starting the web app on $WEB_PORT"
  if [ "$LAN" = "1" ]; then
    (cd frontend && SF_WEB_PORT="$WEB_PORT" nohup npm run dev -- --host >/tmp/sf-web.log 2>&1 &) || true
  else
    (cd frontend && SF_WEB_PORT="$WEB_PORT" nohup npm run dev >/tmp/sf-web.log 2>&1 &) || true
  fi
  for _ in $(seq 1 40); do
    curl -fsS "http://localhost:$WEB_PORT/" >/dev/null 2>&1 && break
    sleep 1
  done
fi

say ""
say "demo is up"
echo "  web   http://localhost:$WEB_PORT"
echo "  api   http://127.0.0.1:$API_PORT/api/buildings"
echo ""
echo "  student1@connect.hku.hk / demo1234   (Student A)"
echo "  student2@connect.hku.hk / demo1234   (Student B)"
echo "  estates@hku.hk          / demo1234   (maintenance)"
echo ""
echo "  script: CW -> L1-B, socket 0002 is dead, 0004 is loose, 0001 works."
if [ "$LAN" = "1" ]; then
  ip=$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}')
  [ -n "${ip:-}" ] && echo "  phone (same Wi-Fi): http://$ip:$WEB_PORT"
fi
