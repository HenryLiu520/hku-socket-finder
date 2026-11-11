# Features

*Every capability in the running build, the role that holds it, and the screen that proves it.*

Two roles, one build. A student finds a room, reads the state of each socket and reports a fault; the estates office works a queue and closes repairs. Nothing below is a mock-up: each row is a request the API answers today.

| Capability | Role | Where to see it |
|---|---|---|
| Pick a building, then a room, floor by floor | Student | Find a socket (`/`) — building tabs, one block per floor |
| Search rooms by code or name | Student | the search field on Find a socket |
| Rooms ordered so the faulty ones come first | Student | Find a socket — the state chips on each room card |
| See every socket in a room on a plan, coloured by state | Student | Room view — an SVG plan drawn from the room's seats and sockets |
| Read how old the last check is | Student | Room view — "last changed" column, with the "old" tag |
| Filter the list to All / Faulty / Old | Student | Room view — the filter above the table |
| Report works, loose or no power in one tap | Student | tap a socket on the plan, or `POST /api/sockets/{id}/report` |
| Report by typing the socket number instead of tapping | Student | Report a fault (`/report`), step 3 |
| See how far a claim got toward the 1.6 threshold | Student | the message returned after sending a report |
| Sign in and be routed by role | Both | Login (`/login`); `/maintenance` sends a student home |
| Switch the interface language, English / 简体中文 / 繁體中文 | Both | the three language buttons in the header |
| Try the demo accounts without typing credentials | Both | login page chips, from `GET /api/auth/demo-accounts` |
| Work the repair queue, oldest check first, with the number of accounts behind each row | Maintenance | Repair queue (`/maintenance`) |
| Close a fault, with an optional note | Maintenance | Mark repaired on the queue; `POST /api/sockets/{id}/repair` |
| See your own record: score, weight, confirmed and refuted counts, and the badge you are working towards | Student | Your record (`/me`, and the fourth tab of the handset build) |

## Deliberately absent

- **Photo evidence.** A rule would have to read the photo to change a state; the evidence rule only counts accounts.
- **Notifications.** Nothing emails or pushes, because the loop works on the next visit rather than on an alert.
- **Self sign-up.** Accounts are seeded so that every report already has an owner whose weight can move.
- **Comments and threads.** A state, a count and a date are what the next reader needs at the desk.
- **Badges and vouchers.** They appear on the poster; no code issues one.
- **Offline mode and editing.** A socket's code is written once by migration and never edited in the interface.

## Rows that need the seed

Three rows depend on the seeded data rather than on a rule. The queue has entries only because migration V6 marks `MW-T1-0003` loose and `CPD-LG01-0007` without power, and V7 leaves two dead sockets in Study room 4. The stale tag shows on first load only because `KK-101-0004` is stamped 45 days back. The report and repair rows cannot be demonstrated at all until someone signs in, and both demo students start at weight 1.0 with no settled reports behind them.

---

← [README](../README.md) · Next: [Architecture](architecture.md)
