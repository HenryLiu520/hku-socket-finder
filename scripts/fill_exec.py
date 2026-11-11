#!/usr/bin/env python3
"""Fill Part 3 of the project document and save it as the exec deliverable.

  python3 scripts/fill_exec.py

The technical half is split by kind rather than by screen:

  B_1  the logic   — the model, the numbering, the state rules, the report rule, and
                     where those decisions are enforced (architecture included here)
  B_2  the function— what a student does, what staff do, the walkthrough we test, and
                     where the function deliberately stops

The sentences are the same ones as before; only the grouping and the headings changed.
The problem and business cells are left exactly as their owners left them.
"""
import os
import shutil

import docx
from docx.shared import Pt

BASE = os.path.expanduser("~/Documents/课程/CCST9003/项目/交件")
SRC = os.path.join(BASE, "R21_Plan.docx")
DST = os.path.join(BASE, "R21_init_Plan_exec.docx")
BAK = os.path.join(BASE, "R21_Plan.bak-before-exec.docx")

FONT = "Times New Roman"


def clear(cell):
    for p in cell.paragraphs[1:]:
        p._element.getparent().remove(p._element)
    first = cell.paragraphs[0]
    for r in list(first.runs):
        r._element.getparent().remove(r._element)
    return first


def run(p, text, size, bold=False):
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(size)
    r.bold = bold
    return r


def label(cell, name, value):
    p = cell.paragraphs[0] if not cell.paragraphs[0].runs else cell.add_paragraph()
    run(p, name, 12, True)
    run(p, " : " + value, 12)


def heading(cell, text, first=False):
    p = cell.paragraphs[0] if first and not cell.paragraphs[0].runs else cell.add_paragraph()
    run(p, text, 10, True)


def bullet(cell, lead, rest):
    p = cell.add_paragraph()
    run(p, "- ", 10)
    run(p, lead, 10, True)
    run(p, " " + rest, 10)


def body(cell, text, size=10):
    p = cell.add_paragraph()
    run(p, text, size)


def fill_title(cell):
    clear(cell)
    run(cell.paragraphs[0], "Socket Finder: know before you sit", 14, True)
    body(cell,
         "A web app that answers one question before you sit down: is there a working "
         "power socket at this seat? A student picks a building, a room and a socket "
         "number, and sees when that socket was last checked. When something is wrong, "
         "four choices file a report and the maintenance queue picks it up. The record is "
         "the product: one socket, one number, one date, and everybody arguing about the "
         "same thing.", 12)


def fill_b1(cell):
    """The logic: model, numbering, state rules, the report rule, who may change what."""
    clear(cell)
    label(cell, "Chairperson", "Haoran Liu")
    p = cell.add_paragraph()
    run(p, "Details", 12, True)
    run(p, " :  ", 12)
    body(cell, "This half is the logic: what the record is made of, what decides a state, "
               "and where those decisions are enforced.")

    heading(cell, "1. The shape of it")
    bullet(cell, "Three parts, one place for rules.",
           "A Vue frontend in the browser calls /api; a Spring Boot service answers; "
           "PostgreSQL holds the record. Every read and every write goes through the "
           "service, so the rules live in one file rather than in the screens: hiding a "
           "button in the browser is not a permission.")
    bullet(cell, "The schema is code.",
           "Eight tables (building, floor, room, seat, socket, report, repair, account), "
           "changed only by numbered migrations, V1 to V7, so a clone rebuilds the same "
           "tables, the same seed and the same socket numbers without anybody remembering "
           "a sequence of commands.")
    bullet(cell, "Two ways to run it.",
           "docker-compose brings the database, the service and the frontend up with "
           "healthchecks and a named volume; scripts/setup-db.sh does the same job on a "
           "machine with no Docker, which is how this was built.")

    heading(cell, "2. One socket, one number")
    bullet(cell, "The address.",
           "CPD-LG01-0001 reads as building, room and a four-digit position inside the "
           "room, assigned once and never reused. A report, a repair and a conversation "
           "all point at the same socket, which is what a photograph cannot do.")
    bullet(cell, "Why this is the innovation.",
           "A map without addresses cannot be argued with. With numbers a student can say "
           "'CW-4-0002 is loose' and staff can close that exact socket, so the record "
           "becomes checkable instead of anecdotal.")

    heading(cell, "3. Three states, and an age")
    bullet(cell, "Works, loose, no power.",
           "Every state carries the time it last changed, and every socket carries the "
           "date it was last checked. Loose is the common fault and the one a two-state "
           "map hides.")
    bullet(cell, "Nothing is assumed.",
           "A socket nobody has checked for weeks is shown as not checked, not as working, "
           "so the map fails honestly instead of quietly.")

    heading(cell, "4. The rule that makes a report count")
    bullet(cell, "Two accounts, then a queue.",
           "A socket enters the maintenance queue only after two different accounts report "
           "it, and no account may file more than ten reports a day. One person cannot flip "
           "a room, and the cap bounds the noise.")
    bullet(cell, "Reputation is the history.",
           "Reports later confirmed by a repair, or by somebody else's check, raise the "
           "account; reports that did not hold up lower it. A higher score makes one report "
           "worth more, which is the only reason to keep reporting accurately.")

    heading(cell, "5. Two roles, decided by the service")
    bullet(cell, "Two roles, checked on the server.",
           "Students report and read; staff close. The check is in the service, not in the "
           "interface, and an account is a role, not a person.")
    bullet(cell, "No identity in any view.",
           "A report shows a count of distinct accounts and a timestamp. No name, no device, "
           "no history of one student's movements.")


def fill_b2(cell):
    """The function: what a student does, what staff do, what we test, where we stop."""
    clear(cell)
    label(cell, "Chairperson", "Haoran Liu")
    p = cell.add_paragraph()
    run(p, "Details", 12, True)
    run(p, " :  ", 12)
    body(cell, "This half is the function: what a student and a member of staff actually do, "
               "in order, and where that stops.")

    heading(cell, "1. The student side, step by step")
    bullet(cell, "Three levels down.",
           "Building, then room, then the socket list and the room plan side by side: the "
           "list gives number, seat, state, the time the state changed and the time of the "
           "last report; the plan puts the same colours on the desk they belong to.")
    bullet(cell, "Reporting is four choices.",
           "Building, room, socket number, what is wrong. From an already open room it is "
           "three taps, and the socket turns orange or red on the spot.")

    heading(cell, "2. The staff side, step by step")
    bullet(cell, "One queue, in order of neglect.",
           "Sorted by how long a socket has been broken, each row showing how many distinct "
           "accounts reported it, so a single frustrated report does not outrank a fault "
           "five people agree on.")
    bullet(cell, "Closing it changes the record.",
           "Marking a repair sets the socket to repaired, stamps the time, and the room page "
           "shows the new state at once, which is what closes the loop.")

    heading(cell, "3. The walkthrough we test")
    bullet(cell, "The loop, end to end.",
           "Two accounts reporting the same socket, the socket entering the queue, a repair "
           "closing it, and the room page showing the new state. Unit tests cover the state "
           "rules; the demonstration is the running system, not slides.")

    heading(cell, "4. Where the function stops")
    bullet(cell, "Deliberately missing.",
           "No photo evidence and no push notification: the queue is a page staff open, not "
           "a message they receive. Both are written down as the next iteration rather than "
           "claimed as done.")


def fill_sequence(cell):
    clear(cell)
    body(cell, "Two minutes each, ten minutes in total, in this order.", 10)
    for name, part in [
        ("Haoran Liu", "the title, the problem, and why a socket needs a number"),
        ("Yiyang Xu", "what students told us, from the survey and the interviews"),
        ("Chenxi Yu", "the technical part: the rule that makes a report count, and the build"),
        ("Lam Ying Chu", "the business part: who pays, who hosts, how it keeps running"),
        ("Deyi Wang", "the ethical part: anonymity and false reports, then the close"),
    ]:
        p = cell.add_paragraph()
        run(p, "- " + name + ": ", 10, True)
        run(p, part, 10)


def fill_video(cell):
    clear(cell)
    body(cell, "One acted minute, then the screen, then the reason, then the name.", 10)
    bullet(cell, "0:00 to 1:00, acted.",
           "A student plugs in, nothing; a friend shows him the room plan on a phone; they "
           "walk to a socket marked green and the laptop charges. Two members are on camera "
           "for the whole minute, which clears the thirty-second rule with room to spare.")
    bullet(cell, "1:00 to 2:04, screen.",
           "The buildings, a room list, the plan with numbers, a report that turns a socket "
           "orange, the staff queue, the repair, and the loop in one picture.")
    bullet(cell, "2:04 to 2:35, to camera.",
           "Why the record stays honest: a score built from reports that turned out right, a "
           "gift once there are enough of them, and the loop that keeps turning because of "
           "it.")
    bullet(cell, "2:35 to 3:00, the close.",
           "One line of value and the end card with the group and the project name.")
    bullet(cell, "The work.",
           "The script is written and the shot list fixed; the screen recording is already "
           "cut at 1:04 with English subtitles; the acted part is shot in one morning at Chi "
           "Wah; the edit takes two evenings; export H.264 at 1080p, uploaded before 29 Nov "
           "23:59.")


def fill_what_else(cell):
    clear(cell)
    bullet(cell, "If the network fails,",
           "we show the recording rather than the live system; it is the same walkthrough, so "
           "nothing in the argument changes.")
    bullet(cell, "One owner for the upload.",
           "The chairperson uploads one copy per group. Two members check the file plays "
           "before it goes in.")


def main():
    if not os.path.exists(BAK):
        shutil.copy2(SRC, BAK)
        print("backup", BAK)
    shutil.copy2(SRC, DST)

    d = docx.Document(DST)
    t = d.tables[2]
    cells = {r: t.rows[r].cells[0] for r in (2, 6, 8, 15, 17, 19)}

    fill_title(cells[2])
    fill_b1(cells[6])
    fill_b2(cells[8])
    fill_sequence(cells[15])
    fill_video(cells[17])
    fill_what_else(cells[19])
    # r4 (Problem) and r10 (Business) belong to their owners: left untouched.
    d.save(DST)
    print("wrote", DST, os.path.getsize(DST) // 1024, "KB")


if __name__ == "__main__":
    main()
