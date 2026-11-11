# Screens

Every screen in this build, in the order a student meets them, plus the two phone layouts.
All pictures are taken from the running app with `scripts/capture_screens.py`, so they show the
product and not a mock-up.

## Find a socket

The first screen is a three-step picker — building, then room — and every room card carries its
own counts of what is wrong before you walk over.

![Find a socket](screens/desktop/01-find-a-socket.jpg)

## Room and floor plan

One room opened: a floor plan drawn from the seats, each socket a chip showing the last four
digits of the number printed on its sticker, with the same sockets listed underneath.

![Room and floor plan](screens/desktop/02-room-and-plan.jpg)

## Report a fault

The report form asks for a building, a room, a socket and a state, and refuses to go further
until the step above it is answered.

![Report a fault](screens/desktop/03-report-a-fault.jpg)

## Repair queue

The staff side of the same records: broken sockets oldest first, the number of students who
agreed, how long it has been broken, and one button per row to close it.

![Repair queue](screens/desktop/04-repair-queue.jpg)

## Room on a phone

The same room at phone width — plan, colour key and socket table stacked in a single column so
the number you read off the desk stays on screen.

![Room on a phone](screens/mobile/05-phone-room.jpg)

## Report a fault on a phone

The report form on a phone: one field per row, the state buttons wrapping onto two lines, and
the same four steps the desktop form asks for.

![Report a fault on a phone](screens/mobile/06-phone-report.jpg)

## Running the demo data

The pictures above were taken against the demo dataset, and `scripts/demo-reset.sql` puts a
database back into exactly that state: it clears every report and repair, resets every socket to
`UNKNOWN`, then writes two agreeing reports for a hand-picked set of sockets so that colours,
ages and reporter counts all mean something. Run it against the demo database after seeding:

```bash
psql -h 127.0.0.1 -p 5433 -d socketfinder -v ON_ERROR_STOP=1 -f scripts/demo-reset.sql
```

It is safe to run repeatedly — it deletes before it inserts, and it leaves one socket unchecked on
purpose so the demo can report it live and watch the state flip.
