# The ninety-second tour

*What this is, in the order a reader meets it.*

## The problem, in one sentence

You walk into a study room, sit down, open the laptop, plug in — and nothing happens. The socket is dead, and
nothing on the desk, the door or the university's own systems told you before you sat down.

## The unit is the socket, not the room

Booking systems count rooms. Repair systems count faults. Neither of them answers the question you actually
have, which is about the desk in front of you. A room can be "available" and the one free desk in it can be
useless, so Sure Socket gives every socket its own identity:

```
CPD-LG01-0001     building · room · four-digit position
```

The number is assigned once and never reused. A student says it out loud, staff read the same string in the
queue, and the database refuses two sockets with the same one — the number is the thing everybody argues
about, so it has to be the same thing everywhere.

![A room's desks, each socket coloured by its last known state](screens/desktop/02-room-and-plan.jpg)

## Three moments the product is built around

1. **Find.** Pick a building, pick a room, and see every socket coloured by its last known state, with the
   date of the last check beside it. The plan of the room puts the colours on the desks they belong to, so
   you can look at the desk rather than at a list.
2. **Report.** Four choices — building, room, socket number, what is wrong — and from an open room it is three
   taps. The socket changes colour on the spot, so you can see your report land.
3. **Repair.** Staff get one queue, ordered by the oldest check first, with the number of accounts behind each
   row. Closing a repair stamps the time, the room shows the new state, and the next student reads it.

![The room plan: one colour block per socket, labelled with its number](screens/mobile/05-phone-room.jpg)

## What a reviewer sees first

The room picker: four buildings, the rooms under them, and for each room the counts of working, loose, dead
and unchecked sockets. One click and a stranger is looking at a specific room, on a specific floor, with a
specific socket coloured red — no sign-in wall, no setup, no explanation needed.

---

← [README](../README.md) · Next: [The loop](loop.md)
