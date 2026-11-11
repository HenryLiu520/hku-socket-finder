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
    """The logic: model, numbering, state rules, the loop, then how a report is scored."""
    clear(cell)
    label(cell, "Chairperson", "Haoran Liu")
    p = cell.add_paragraph()
    run(p, "Details", 12, True)
    run(p, " :  ", 12)
    body(cell, "Logic layer: the data model, the numbering, the rules that determine a socket's "
               "state, the loop those rules keep turning, and the scoring that decides what one "
               "report is worth.")

    heading(cell, "1. System architecture and rule enforcement")
    bullet(cell, "Three-tier separation, rules held server-side.",
           "A Vue frontend in the browser calls /api; a Spring Boot service answers; "
           "PostgreSQL holds the record. Every read and every write goes through the "
           "service, so the rules live in one file rather than in the screens: hiding a "
           "button in the browser is not a permission.")
    bullet(cell, "Schema under migration control.",
           "Eight tables (building, floor, room, seat, socket, report, repair, account), "
           "changed only by numbered migrations, V1 to V7, so a clone rebuilds the same "
           "tables, the same seed and the same socket numbers without anybody remembering "
           "a sequence of commands.")
    bullet(cell, "Two deployment paths.",
           "docker-compose brings the database, the service and the frontend up with "
           "healthchecks and a named volume; scripts/setup-db.sh does the same job on a "
           "machine with no Docker, which is how this was built.")

    heading(cell, "2. Canonical socket identification")
    bullet(cell, "Format and assignment rules.",
           "CPD-LG01-0001 reads as building, room and a four-digit position inside the "
           "room, assigned once and never reused. A report, a repair and a conversation "
           "all point at the same socket, which is what a photograph cannot do.")
    bullet(cell, "Design rationale.",
           "A map without addresses cannot be argued with. With numbers a student can say "
           "'CW-4-0002 is loose' and staff can close that exact socket, so the record "
           "becomes checkable instead of anecdotal.")

    heading(cell, "3. State model")
    bullet(cell, "Three states, each timestamped.",
           "Works, loose, no power, with the time each state changed and the date each "
           "socket was last checked. Loose is the common fault and the one a two-state map "
           "hides.")

    heading(cell, "4. The loop, end to end")
    bullet(cell, "Four steps, one direction.",
           "A student reports what he sees; the socket enters the staff queue once a second "
           "account agrees; staff repair and close it; the state and its timestamp change, "
           "and the next student reads the corrected record before choosing a seat. Nothing "
           "in the loop is edited by hand on the side.")
    bullet(cell, "Why it repeats.",
           "Each closed repair is also evidence that the report behind it was right, which "
           "is what the reputation score is built from; the score weights the next report, "
           "and the next report is what keeps the record usable. The queue is the pump: "
           "without a closure, the loop stalls at step three.")

    heading(cell, "5. Report validation")
    bullet(cell, "Corroboration threshold and daily cap.",
           "A socket enters the maintenance queue only after two different accounts report "
           "it, and no account may file more than ten reports a day. One person cannot flip "
           "a room, and the cap bounds the noise.")

    heading(cell, "6. Reputation scoring")
    bullet(cell, "The score is an error rate, not a count.",
           "A report is settled when the socket is closed or checked again: if the repair "
           "agrees with what was reported the report is confirmed; if it disagrees, or a "
           "later check contradicts it, it is refuted. The score is confirmed divided by "
           "settled, and a new account is held at neutral until it has five settled reports, "
           "so an early mistake does not follow anybody around.")
    bullet(cell, "The score is a weight, not a gate.",
           "One report counts between half and one and a half of a neutral report, in "
           "proportion to that score. Nobody is barred from reporting, and nobody can buy "
           "weight with volume, because the daily cap limits volume and only settled reports "
           "move the score.")


def fill_b2(cell):
    """The function, plus the second mechanism: what people do, and what rewards them."""
    clear(cell)
    label(cell, "Chairperson", "Chenxi Yu")
    p = cell.add_paragraph()
    run(p, "Details", 12, True)
    run(p, " :  ", 12)
    body(cell, "Function layer: the steps a student and a facilities member perform, the loop "
               "that connects them, the incentive that keeps people reporting, and how the "
               "frontend implements all of it.")

    heading(cell, "1. Student-facing navigation and reporting")
    bullet(cell, "Three-level navigation, list and plan together.",
           "Building, then room, then the socket list and the room plan side by side: the "
           "list gives number, seat, state, the time the state changed and the time of the "
           "last report; the plan puts the same colours on the desk they belong to.")
    bullet(cell, "Report form with four fields.",
           "Building, room, socket number, what is wrong. From an already open room it is "
           "three taps, and the socket turns orange or red on the spot.")

    heading(cell, "2. Facilities-facing queue and closure")
    bullet(cell, "Queue ordered by outage duration.",
           "Sorted by how long a socket has been broken, each row showing how many distinct "
           "accounts reported it, so a single frustrated report does not outrank a fault "
           "five people agree on.")
    bullet(cell, "Closure writes back to the record.",
           "Marking a repair sets the socket to repaired, stamps the time, and the room page "
           "shows the new state at once, which is what closes the loop.")

    heading(cell, "3. The incentive mechanism")
    bullet(cell, "Rewards follow confirmed reports, not reports.",
           "A badge at the first ten confirmed reports, and a campus voucher at the end of "
           "term for the accounts that kept a floor accurate. Reporting more earns nothing "
           "extra; being right does.")
    bullet(cell, "Why this keeps the loop turning.",
           "The score and the reward read the same number, so the only way to gain either is "
           "to be right about a socket that somebody later closed. That is what makes a "
           "stranger's report worth trusting, and what makes it worth his ten seconds: the "
           "loop is held up by these two mechanisms, not by goodwill.")

    heading(cell, "4. Frontend implementation")
    bullet(cell, "One application, three roles.",
           "A Vue 3 single-page application built with Vite, routed with vue-router: the "
           "building list, the room view, the report form, the maintenance queue and the "
           "sign-in screen are separate views over the same API.")
    bullet(cell, "One API client.",
           "Every screen reads and writes through a single module whose base URL is /api, so "
           "development runs behind the Vite proxy and production behind nginx without a "
           "second code path.")
    bullet(cell, "The plan is drawn, not photographed.",
           "RoomMap renders an inline SVG from the seat and socket coordinates in the "
           "database: outline, desks, and one colour block per socket labelled with the last "
           "four digits of its number. No image assets to keep in step with the data, and "
           "the labels stay legible at any zoom.")
    bullet(cell, "Three languages, one dictionary each.",
           "English, simplified and traditional Chinese ship as separate dictionaries with "
           "the same keys; the switch sits in the header and the choice persists, so a "
           "screen never mixes two languages.")
    bullet(cell, "The weight is visible, not hidden.",
           "An account shows its score and how many reports have been settled, and a report "
           "shows what it counted for once the socket is closed. A weight nobody can see is "
           "indistinguishable from a rule that does not exist.")
    bullet(cell, "The reward is a target, not a surprise.",
           "A small panel lists the badges and what earns them, so the incentive points at a "
           "number the student can watch move, which is the only way it can change behaviour.")
    bullet(cell, "Layout rules.",
           "The five states are CSS variables rather than hard-coded colours; the header is "
           "fixed and the content column is allowed to shrink, so a narrow laptop window "
           "scrolls the table instead of the page.")

    heading(cell, "5. Scope boundary")
    bullet(cell, "Explicitly out of scope.",
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


def relabel_layers(d):
    """Part 2 keeps every outline as it was; only the two technical titles gain a layer name."""
    cell = d.tables[1].rows[5].cells[0]
    names = {
        "Technical aspect (1)": "Technical aspect (1) — logic layer",
        "Technical aspect (2;  for a team with 5 members only)":
            "Technical aspect (2; for a team with 5 members only) — function layer",
    }
    chairs = {
        "Technical aspect (1)": "Chairperson : Haoran Liu",
        "Technical aspect (2;": "Chairperson : Chenxi Yu",
    }
    changed = []
    block = None
    for par in cell.paragraphs:
        s = par.text.strip()
        for old, new in names.items():
            if s.startswith(old) and "layer" not in s:
                if par.runs:
                    par.runs[0].text = new + s[len(old):]
                changed.append(new)
        for key in chairs:
            if s.startswith(key):
                block = key
        if s.startswith("Chairperson") and block in chairs:
            want = chairs[block]
            if s != want and par.runs:
                par.runs[0].text = want
                changed.append(want)
            block = None
    return changed


def main():
    if not os.path.exists(BAK):
        shutil.copy2(SRC, BAK)
        print("backup", BAK)
    shutil.copy2(SRC, DST)

    d = docx.Document(DST)
    t = d.tables[2]
    cells = {r: t.rows[r].cells[0] for r in (2, 6, 8, 15, 17, 19)}

    relabel_layers(d)
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
