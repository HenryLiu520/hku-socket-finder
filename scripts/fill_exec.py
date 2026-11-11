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

    heading(cell, "3. Functional design")
    bullet(cell, "Find a socket.",
           "Building, then room, then the list and the plan together; every row carries the "
           "number, the seat, the state and the date of the last check, so the question is "
           "answered on one screen without opening anything else.")
    bullet(cell, "Report a fault.",
           "Four choices: building, room, socket number, what is wrong. Three taps from an "
           "open room, and the colour of that socket changes on the spot.")
    bullet(cell, "Read the queue.",
           "Staff see one list ordered by how long a socket has been broken, with the number "
           "of distinct accounts behind each row, so the list is a priority rather than an "
           "inbox.")
    bullet(cell, "Close a repair.",
           "One action writes the repair, sets the socket to repaired and stamps the time, "
           "which returns the room to a known state and closes the loop.")
    bullet(cell, "Keep score.",
           "Every settled report moves the account's score, the score weights the next "
           "report, and badges mark the milestones, so the two mechanisms of the loop are "
           "visible as functions rather than as rules.")

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
    bullet(cell, "Credibility is the sum of the reporters' scores.",
           "A state does not change because two people clicked; it changes when the weights of "
           "the accounts behind it add up to 1.6 and lead every competing state by half again. "
           "Only the three heaviest accounts in the last 72 hours are counted, a new account "
           "carries weight 1.0, and the ceiling is 1.5, so no single account can move a socket "
           "alone however good its score is.")
    bullet(cell, "Disagreement is kept, not averaged.",
           "If the reports name different faults and neither side clears the threshold, the "
           "socket keeps the state it had and both reports stay on the record as disputed, "
           "until a repair or a later check settles them. No account may file more than ten "
           "reports a day, which bounds the noise.")

    heading(cell, "6. Reputation scoring")
    bullet(cell, "The score is a settled ratio with a prior.",
           "A settled report is a yes or a no. The score is (confirmed + 2.5) divided by "
           "(settled + 5), so a new account sits at 0.5 rather than at zero or at one, and only "
           "moves once reports are settled; the student sees it as a number out of 100.")
    bullet(cell, "The score is the weight, and the weight sets the bar.",
           "Weight is 0.5 plus the score, so it runs from 0.5 to 1.5, and the corroboration "
           "threshold of 1.6 is deliberately above that ceiling: two fresh accounts can change "
           "a socket, one trusted account cannot. A score is therefore an influence on the "
           "record, never a permission to edit it.")
    bullet(cell, "Only settlement moves it.",
           "Unsettled reports count for nothing, so filing more of them earns nothing. A repair "
           "that agrees with a report confirms it, one that disagrees refutes it, and a repair "
           "closed as no fault found refutes everybody who reported one, which is what keeps the "
           "scores honest when nothing was wrong.")


def fill_b2(cell):
    """Organize the five functions and show how each is implemented."""
    clear(cell)
    label(cell, "Chairperson", "Chenxi Yu")
    p = cell.add_paragraph()
    run(p, "Details", 12, True)
    run(p, " :  ", 12)
    body(cell, "Function layer: how the functions designed above are organized into screens, how "
               "each one is implemented, the incentive that keeps people reporting, and how the "
               "frontend carries all of it.")

    heading(cell, "1. Function organization")
    bullet(cell, "Three roles, five functions.",
           "Students use find and report; staff use the queue and the closure; both see the "
           "score. Each function owns one screen and one endpoint, so the navigation follows "
           "the work rather than the database.")
    bullet(cell, "One screen, one job.",
           "Find, report, queue, close, score: five screens, none doing two jobs, so a URL can "
           "be quoted in a conversation and a fault can be located by screen before anybody "
           "reads the code.")

    heading(cell, "2. Implementation of find and report")
    bullet(cell, "Browse without arithmetic.",
           "The building list and the room list answer with the counts already summed "
           "(sockets, working, broken), so the browser renders a room card without fetching "
           "its sockets first.")
    bullet(cell, "One room, one request.",
           "The room endpoint returns every seat and socket with its state, the time the state "
           "changed and the time of the last report in a single response, which is what lets "
           "the list and the plan draw from the same numbers.")
    bullet(cell, "A report that cannot be malformed.",
           "The three dropdowns are filled from the server, so an impossible combination "
           "cannot be selected in the first place; the endpoint re-checks the socket code and "
           "refuses one that does not exist.")
    bullet(cell, "Corroboration counted, not assumed.",
           "A second report from the same account on the same socket is ignored; the second "
           "distinct account is what changes the state and puts the socket in the queue.")

    heading(cell, "3. Implementation of the queue and the closure")
    bullet(cell, "The queue is built from the record.",
           "Ordered by how long a socket has been broken, each row showing how many distinct "
           "accounts reported it, so a single frustrated report does not outrank a fault five "
           "people agree on.")
    bullet(cell, "Closure in one transaction.",
           "Closing a repair writes the repair row, sets the socket to repaired and stamps "
           "both times together, so a half-closed socket cannot exist.")
    bullet(cell, "Sign-in and roles.",
           "Sign-in returns a token held in memory; the account row carries the role and the "
           "service checks it on every write, so the staff queue and the student screens are "
           "the same application behind one check.")
    bullet(cell, "A demo that starts from zero.",
           "scripts/demo-reset.sql empties reports and repairs, returns every socket to not "
           "checked and replays a fixed set of reports through a small function, so the "
           "demonstration begins from the same state every time.")

    heading(cell, "4. The incentive mechanism")
    bullet(cell, "Rewards follow confirmed reports, not reports.",
           "A badge at the first ten confirmed reports, and a campus voucher at the end of "
           "term for the accounts that kept a floor accurate. Reporting more earns nothing "
           "extra; being right does.")
    bullet(cell, "Why this keeps the loop turning.",
           "The score and the reward read the same number, so the only way to gain either is "
           "to be right about a socket that somebody later closed. That is what makes a "
           "stranger's report worth trusting, and what makes it worth his ten seconds: the "
           "loop is held up by these two mechanisms, not by goodwill.")

    heading(cell, "5. Frontend implementation")
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
           "four digits of its number. No image assets to keep in step with the data, and the "
           "labels stay legible at any zoom.")
    bullet(cell, "Three languages, one dictionary each.",
           "English, simplified and traditional Chinese ship as separate dictionaries with the "
           "same keys; the switch sits in the header and the choice persists, so a screen "
           "never mixes two languages.")
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
