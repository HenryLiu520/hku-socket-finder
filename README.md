# Socket Finder

**Find a seat you can charge at.** A web app that tells a student, before they sit down, whether the power socket at that desk works.

English · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

![Rooms](docs/screens/01-rooms.png)

## What this is

A HKU CCST9003 group project (Group R21). This repository is **iteration 1**: one socket, end to end.
Open a room, open a socket, report it broken, watch the state flip.

The unit of the design is the socket, not the room. Booking systems count rooms and desks, repair systems
count faults, and neither of them knows whether you can actually charge your laptop there.

## Screens

| Room page | Repair queue |
|---|---|
| ![Room](docs/screens/02-room.png) | ![Queue](docs/screens/03-queue.png) |

## Stack

Built with:

- **Backend**: Spring Boot 4.1, Java 21, Spring Data JPA, Flyway, PostgreSQL 17
- **Frontend**: Vue 3 + Vite + Element Plus, one application for both roles
- **Auth**: email + password (BCrypt), token in memory, role checked on every write

## Run it

Requirements: Java 21, Maven, Node 18+, PostgreSQL running locally.

```bash
# once: create the database (this project assumes PostgreSQL on port 5433)
createdb -p 5433 -h 127.0.0.1 socketfinder

./scripts/start-all.sh      # backend on :8081, frontend on :5175
open http://localhost:5175
```

Stop everything with `./scripts/stop-all.sh`.

## Demo accounts (password `demo1234`)

| Email | Role | Why it exists |
|---|---|---|
| student1@connect.hku.hk | student | first reporter |
| student2@connect.hku.hk | student | second reporter, needed to flip a socket |
| estates@hku.hk | maintenance | sees the repair queue |

Two different accounts have to report the same thing before a state changes, so you need both students
to see a flip.

## API

| Method | Path | Who | What |
|---|---|---|---|
| POST | `/api/auth/login` | anyone | email + password, returns a token |
| GET | `/api/auth/demo-accounts` | anyone | the three demo logins, for the sign-in page |
| GET | `/api/buildings` | anyone | buildings with their floors |
| GET | `/api/floors/{id}/rooms` | anyone | rooms on a floor with socket counts |
| GET | `/api/rooms/{id}` | anyone | seats and sockets in a room |
| POST | `/api/sockets/{id}/report` | student | report `WORKING` or `BROKEN` |
| POST | `/api/sockets/{id}/repair` | maintenance | mark repaired, with an optional note |
| GET | `/api/maintenance/queue` | maintenance | sockets reported broken, oldest first |

## Rules this version implements

- **Two reports flip a socket.** Two different accounts, same state, within 24 hours. One report on its
  own is stored and shown as unconfirmed.
- **One report per account per socket per day.** A second attempt returns HTTP 429.
- **Old checks are labelled old.** Anything past 30 days is flagged in the interface instead of being
  trusted as fresh.
- **Only maintenance can close a repair.** A repair sets the state to `REPAIRED` and stamps the time,
  which is what students see next.
- **Role separation is enforced by the API**, not by hiding buttons in the front end.

## Planned next

- A floor plan per level, so a room is a drawing instead of a list.
- Photos on reports, a notification when a socket you use changes state, and an offline view for the basement.
- Room and socket data for the whole campus, imported one building at a time.
- Email verification and self-registration for students.
- A phone build, once the web app is used enough to justify it.

The scope of each step is set at the review after the previous iteration.

## Known prototype limits

- Tokens live in memory, so restarting the backend signs everyone out.
- Passwords are BCrypt, but the login endpoint has no rate limit.
- The seed data is a sample, not a survey of a real floor.

## Repository layout

```
backend/   Spring Boot API, Flyway migrations, seed data, unit tests
frontend/  Vue 3 application (one build, two roles)
scripts/   start / stop / test / end-to-end
docs/      screenshots
```

---

**Keeping the READMEs in sync.** This project has three READMEs: English, Simplified Chinese and
Traditional Chinese. Any change to one must be made in all three in the same commit. `scripts/check-readmes.sh`
verifies that the three still have the same structure, and it runs before every push.
