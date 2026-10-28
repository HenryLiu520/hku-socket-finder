# Deployment

How to run this somewhere other than the machine it was written on: what comes up, what to set, and what to do when it does not.

## What you are deploying

| Service | Image | Port | Depends on |
|---|---|---|---|
| `db` | postgres:17-alpine | internal 5432 | nothing |
| `backend` | built from `backend/` | 8081 | `db` healthy |
| `frontend` | built from `frontend/` (nginx + built SPA) | 8080 → 80 | `backend` |

The database is not published to the host. Only 8080 and 8081 are reachable.

## Requirements

- Docker Engine 24 or newer, with Compose v2 (`docker compose version` must work)
- 2 GB free disk (the images come to roughly 600 MB), 1 GB RAM
- Nothing else. Java, Node and PostgreSQL are inside the images.

## Deploy in one command

```bash
git clone https://github.com/HenryLiu520/hku-socket-finder.git
cd hku-socket-finder
docker compose up --build -d
docker compose ps
```

What happens on the first boot: `db` starts and passes its `pg_isready` healthcheck, `backend` waits for that and then runs the Flyway migrations (9 tables) and seeds the three demo accounts, `frontend` serves the built files and forwards `/api` to the backend.

## Check that it worked

```bash
curl -s http://localhost:8081/api/buildings
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080
```

Then open `http://localhost:8080` and sign in as `student1@connect.hku.hk` with `demo1234`. Two accounts are needed to flip a socket: `student1` and `student2`.

## Configuration

| Variable | Default | What it does |
|---|---|---|
| `SF_DB_URL` | `jdbc:postgresql://localhost:5433/socketfinder` | JDBC URL; compose sets it to the `db` service |
| `SF_DB_USER` | current OS user | database user |
| `SF_DB_PASSWORD` | empty | database password |
| `SF_BIND` | `127.0.0.1` | address the API listens on; must be `0.0.0.0` inside a container |
| `SF_PORT` | `8081` | API port |
| `SF_CORS_ORIGIN` | `http://localhost:5175` | the only origin allowed to call the API cross-origin |

With the nginx front end the browser calls `/api` on the same origin, so CORS is not in play. Change it only if you call the API directly from another site.

To override without editing the repo, add a `docker-compose.override.yml`:

```yaml
services:
  backend:
    environment:
      SF_CORS_ORIGIN: https://socketfinder.example.com
```

## Data, backup and reset

The database lives in the named volume `socketfinder-data`.

```bash
# backup
docker compose exec -T db pg_dump -U socketfinder socketfinder > backup.sql

# restore into a running stack
cat backup.sql | docker compose exec -T db psql -U socketfinder -d socketfinder

# start over, deleting everything
docker compose down -v
```

Back up before any upgrade. Migrations only move forward; there is no down script.

## Logs and health

```bash
docker compose ps                    # states and health
docker compose logs -f backend       # Spring Boot output, migrations, errors
```

There is no Actuator endpoint. Health is `GET /api/buildings` returning 200.

## When it does not work

| Symptom | Cause | What to do |
|---|---|---|
| `port is already allocated` | 8080 or 8081 taken | change the left side of the port mapping |
| backend exits with a connection error | database never became healthy | `docker compose logs db`, check the volume permissions |
| nginx answers 502 | backend is not up | `docker compose logs backend`, wait for the first build |
| `403 Invalid CORS request` | calling the API from a different origin | set `SF_CORS_ORIGIN`, or go through the nginx front end |
| everyone is signed out after a restart | tokens are held in memory | known limit of this build, sign in again |
| page loads, API returns 404 | `/api` proxy path or backend down | check `docker compose ps`, then `curl localhost:8081/api/buildings` |

## Without Docker

```bash
./scripts/start-all.sh      # database, API :8081, web :5175
```

`scripts/setup-db.sh` uses an existing server if `SF_DB_URL` is set, Docker if it is available, and otherwise creates its own PostgreSQL cluster under `db/pgdata`.

For a plain server without Docker: build the jar with `mvn -DskipTests package`, run `java -jar backend/target/socket-finder-0.1.0.jar` under systemd, serve `frontend/dist` with any web server, and point nginx's `/api` at the jar's port.

## Before this faces real users

- Replace the seeded demo accounts and add a real sign-up and verification path.
- Move tokens out of memory, otherwise every deploy signs everyone out.
- Terminate TLS in front (Caddy or nginx) and do not expose 8081 publicly.
- Keep database credentials in a secret store, not in the compose file.
- Schedule the database backup above and test a restore once.
- Decide where the room and socket data comes from, because the seed data is a sample of one floor.

## Deployment checklist

- [ ] `docker compose ps` shows three services up, `db` healthy
- [ ] `GET /api/buildings` returns 200 with one building
- [ ] sign in works and the room list loads
- [ ] two accounts can flip a socket and it appears in the repair queue
- [ ] one backup file has been produced and restored into a scratch database
