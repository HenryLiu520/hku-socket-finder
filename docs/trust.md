# Why the state can be trusted

*What the numbers behind a state are, who may change them, and what remains unproven.*

## Contents

- [The evidence rule](#the-evidence-rule)
- [The rules in one table](#the-rules-in-one-table)
- [How a score moves](#how-a-score-moves)
- [Known limits](#known-limits)

## The evidence rule

A report is not a vote, it is a weight. Every account carries a weight between 0.5 and 1.5, computed from how its past reports were settled. To decide what a socket's state is, the API reads every report filed on that socket in the last 72 hours, keeps only each account's most recent one, groups those reports by the state they claim, and sums the three heaviest weights in each group. A state takes over when its sum reaches 1.6 **and** is at least 1.5× the sum of the runner-up. If neither test passes, the socket keeps the state it had; the report is still stored, and still counts in the next window.

The arithmetic does the governing. The ceiling of any single weight is 1.5, below 1.6, so one account can never flip a socket alone however good its record. Two accounts at the neutral weight of 1.0 sum to 2.0 — over the threshold, with a 2.0-to-0 lead. A disputed socket, say 2.0 claimed one way and 1.5 the other, fails the 1.5× test and keeps its old state until somebody else speaks.

A report that changes nothing answers with the distance travelled: "Report saved. 1.0 of 1.6 evidence needed to change the state", which is what the room view shows after a tap.

## The rules in one table

| Rule | Value in this build | What it prevents |
|---|---|---|
| Evidence to take a state | 1.6, summed over the heaviest weights behind one state | a single report moving a socket |
| Lead over the runner-up | 1.5× the second-heaviest sum | a coin toss between two claims |
| Evidence window | 72 hours, and only each account's latest report inside it | an opinion outliving the fault |
| Accounts counted | the three heaviest, and no weight above 1.5 | one person flipping a socket alone |
| Weight of a report | 0.5 + score, so 0.5 to 1.5; a new account weighs 1.0 | the loudest reporter outvoting the accurate one |
| Score of an account | (confirmed + 2.5) / (settled + 5) | one lucky report defining an account |
| Reporting limits | one report per socket per 24 h, ten per account per day, both HTTP 429 | one person sweeping a floor in an hour |

## How a score moves

The score is an error rate with a prior, not a count: `(confirmed + 2.5) / (confirmed + refuted + 5)`, the prior behind it being Beta(2.5, 2.5). A new account sits at 0.5 and weighs 1.0; an account whose settled reports were all right approaches a weight of 1.5; one that is always wrong drifts toward 0.5. `GET /api/auth/me` returns score, weight and both counters.

A settled report also leaves the evidence pool, so the reports a repair has already judged stop voting and cannot be settled a second time. Exactly one event moves those counters: a repair. Maintenance marks a socket repaired, and the API writes a repair row with the staff account, the time and an optional note, sets the socket to repaired, stamps the check time, then settles every report in the 72-hour window — reports that named the state the socket was in are counted confirmed, the rest refuted. Nothing else touches the counters: not filing a report, not a state flip, not signing in. A repair on a socket that is not loose, no power or broken settles nothing, so marking a working socket repaired hands out no credit.

## The two rate limits

Both are per account, both answer HTTP 429:

- **One report per socket per 24 hours.** A second attempt returns `TOO_SOON`, "You already reported this socket today".
- **Ten reports per day.** Counted from local midnight; the eleventh returns `DAILY_CAP`, "That is 10 reports today, come back tomorrow".

The other refusals are small and exact: an unknown socket is 404, a state outside works / loose / no power is 400 `BAD_STATE`, a missing token is 401, and the wrong role is 403.

## What is labelled stale

A check older than 30 days is stale. It is computed when a socket is read, by a pure function handed the check time and the clock, so no background job can drift from the row it describes. A stale socket keeps its state: it is tagged "old" in the room view and collected by the Old filter, while a socket nobody has checked shows "never checked" instead of an age.

## Who may close a fault

Maintenance, and only maintenance. The check sits in the controller on the write, not in the interface, so a student calling the repair endpoint gets 403 however the buttons are arranged. The server, not the browser, stamps the check time when evidence flips a state.

## Known limits

- **Tokens live in memory.** They sit in a map inside the API process and expire after eight hours; a restart signs everybody out, and a second instance would not share them.
- **The login endpoint has no rate limit.** Nothing slows a password guesser down, which is tolerable only because the accounts are demo accounts with a published password.
- **Accounts are seeded, not verified.** The application creates three on first start; nothing proves an account belongs to a HKU student.
- **The rooms are sample data.** Buildings, seats and sockets are hand-written migration rows for four buildings, not the campus.
- **Evidence stops at three accounts.** A fourth student agreeing adds nothing to the sum, so a large crowd is not more convincing than three accurate accounts.
- **Honesty is priced, not proven.** The API cannot see whether a report was true; it can only make a wrong report cost weight at the next repair.

---

← [README](../README.md) · Next: [Features](features.md)
