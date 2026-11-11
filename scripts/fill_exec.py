#!/usr/bin/env python3
"""Fill Part 3 of the project document and save it as the exec deliverable.

  python3 scripts/fill_exec.py

Reads 交件/R21_Plan.docx, writes 交件/R21_init_Plan_exec.docx. Only the technical
sections, the presentation order and the video plan are written; the problem and the
business sections stay as their owners left them. Formatting copies what is already
in the table: bold "Chairperson"/"Details" labels at 12pt, numbered headings and
bullets at 10pt, Times New Roman throughout.
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
    """Keep the first paragraph, drop the rest, so we can refill the cell."""
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
    clear(cell)
    label(cell, "Chairperson", "Haoran Liu")
    p = cell.add_paragraph()
    run(p, "Details", 12, True)
    run(p, " :  ", 12)

    heading(cell, "1. The socket number")
    bullet(cell, "One socket, one address.",
           "CPD-LG01-0001 reads as building, room and a four-digit position inside the "
           "room. It is assigned once and never reused, so a report, a repair and a "
           "conversation all point at the same socket.")
    bullet(cell, "Why this is the innovation.",
           "A map without addresses cannot be argued with. With numbers, a student can say "
           "'CW-4-0002 is loose' and staff can close that exact socket, which turns an "
           "anecdote into a record that can be checked.")

    heading(cell, "2. Three states, and an age")
    bullet(cell, "Works, loose, no power.",
           "Every state carries the time it last changed and every socket carries the date "
           "it was last checked. Loose is the common fault, and it is the one a two-state "
           "map hides.")
    bullet(cell, "Nothing is assumed.",
           "A socket nobody has checked for weeks shows as not checked, not as working, so "
           "the map fails honestly instead of quietly.")

    heading(cell, "3. The rule that makes a report count")
    bullet(cell, "Two accounts, one queue.",
           "A socket enters the maintenance queue only after two different accounts report "
           "it, and one account cannot file more than ten reports a day. One person cannot "
           "flip a room, and the cap bounds the noise.")
    bullet(cell, "Reputation is the history.",
           "Reports later confirmed by a repair, or by somebody else's check, raise the "
           "account; reports that did not hold up lower it. A higher score makes one report "
           "worth more, which is why an accurate reporter is worth having.")


def fill_b2(cell):
    clear(cell)
    label(cell, "Chairperson", "Haoran Liu")
    p = cell.add_paragraph()
    run(p, "Details", 12, True)
    run(p, " :  ", 12)

    heading(cell, "1. What is built")
    bullet(cell, "Three parts.",
           "A Spring Boot service, a PostgreSQL database and a Vue frontend, over eight "
           "tables: building, floor, room, seat, socket, report, repair, account.")
    bullet(cell, "Versioned schema.",
           "Every change is a migration, V1 to V7, so a clone rebuilds the same tables, the "
           "same seed and the same socket numbers without anybody remembering a sequence of "
           "commands.")

    heading(cell, "2. What a student does")
    bullet(cell, "Three levels down.",
           "Building, then room, then the socket list and the room plan, colour-coded, with "
           "the date each socket was last checked.")
    bullet(cell, "Four choices.",
           "Building, room, socket number, what is wrong. From an already open room it is "
           "three taps.")

    heading(cell, "3. What staff do")
    bullet(cell, "One queue.",
           "Ordered by how long a socket has been broken, with the number of distinct "
           "accounts behind each row, so a single frustrated report does not outrank a fault "
           "five people agree on.")
    bullet(cell, "Closing it changes the record.",
           "Marking a repair sets the socket to repaired, stamps the time, and the room page "
           "shows the new state at once.")

    heading(cell, "4. How it runs")
    bullet(cell, "One command.",
           "docker-compose brings up the database, the API and the frontend with healthchecks "
           "and a named volume; scripts/setup-db.sh does the same job without Docker.")
    bullet(cell, "Repeatable demo.",
           "The demo data is a script, so the same four buildings and the same broken sockets "
           "come back before every presentation.")

    heading(cell, "5. What is deliberately not there")
    bullet(cell, "No photos, no push.",
           "The queue is a page staff open, not a message they receive. Photo evidence and "
           "notifications are written down as the next iteration, not claimed as done.")


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
    cells = {r: t.rows[r].cells[0] for r in (2, 6, 8, 10, 15, 17, 19)}

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
