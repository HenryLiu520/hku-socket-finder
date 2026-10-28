# Socket Finder - CCST9003 Group R21

Iteration 1 of the group project: **one socket, end to end**.
Open a room, open a socket, report it broken, watch the state flip. Two different students have to
report the same thing before the state changes, and a check older than 30 days is shown as old.

Stack: same as our COMP1110 project - Spring Boot + PostgreSQL + Vue 3 (one front end, two roles).

```
backend/   Spring Boot 4, JPA, Flyway, PostgreSQL
frontend/  Vue 3 + Vite + Element Plus, single application, role decides the views
scripts/   start / stop / test / e2e
docs/      screenshots
```

## Run it

```bash
# once: create the database (PostgreSQL 17 on port 5433)
createdb -p 5433 -h 127.0.0.1 socketfinder

./scripts/start-all.sh          # backend :8081, frontend :5175
open http://localhost:5175
```

Stop with `./scripts/stop-all.sh`.

## Demo accounts (password `demo1234`)

| Email | Role | Why it exists |
|---|---|---|
| student1@connect.hku.hk | student | first reporter |
| student2@connect.hku.hk | student | second reporter, needed to flip a socket |
| estates@hku.hk | maintenance | sees the repair queue |

## What is implemented (iteration 1)

- One floor, three rooms of hand-typed data (Chi Wah Learning Commons L1), 18 sockets.
- Single front end, two roles. Students report, maintenance sees the queue and closes a repair.
- Two independent reports within 24 hours flip the state. One report is stored and shown as unconfirmed.
- One report per account per socket per day (HTTP 429 if you try again).
- A check older than 30 days is flagged as old in the interface.
- A repair resets the state to `REPAIRED` and stamps the time; students then see "repaired, checked today"
  until someone reports it working again.

## What is deliberately not here yet

No accounts by invitation (roles are seeded), no email verification, no photos, no notifications,
no whole-campus data import, no floor plan drawing. Those are iterations 2 and 3, whose scope is set
at the review after each iteration.

## Known prototype limits

- Auth tokens live in memory, so restarting the backend signs everyone out. Fine for a demo, wrong for real use.
- Passwords are BCrypt, but there is no rate limit on the login endpoint.
- The socket data is hand-typed, so it is a sample, not the truth about a real floor.
