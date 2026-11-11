/**
 * One place that turns a socket state into a colour, so the plan, the list, the
 * legend and the report picker always agree.
 *
 * green = works, amber = loose, red = no power (or broken), blue = repaired,
 * grey = not checked. The same mapping the desktop table uses.
 */
const TONE = {
  WORKING: 'green',
  LOOSE: 'amber',
  NO_POWER: 'red',
  BROKEN: 'red',
  REPAIRED: 'blue',
  UNKNOWN: 'grey'
}

const DOT = {
  green: '#12b76a',
  amber: '#f79009',
  red: '#f04438',
  blue: '#444ce7',
  grey: '#98a2b3'
}

/** Fills are flatter than dots; a map should not shout. */
const FILL = {
  green: '#12b76a',
  amber: '#f79009',
  red: '#f04438',
  blue: '#444ce7',
  grey: '#d8e0dc'
}

const tone = (state) => TONE[String(state || '').toUpperCase()] || 'grey'

export const dotColor = (state) => DOT[tone(state)]
export const fillColor = (state) => FILL[tone(state)]
export const isPale = (state) => tone(state) === 'grey'
export const toneOf = tone

/** Last segment of a socket code — the four digits on the sticker. */
export const tail = (code) => String(code || '').split('-').pop()

/** Flatten a room's seats into socket rows, each carrying its seat label. */
export function socketRows(room) {
  const seats = (room && room.seats) || []
  return seats
    .flatMap((seat) => (seat.sockets || []).map((s) => ({ ...s, seat: seat.label })))
    .sort((a, b) => String(a.code).localeCompare(String(b.code)))
}

/** Counts per state, plus how many checks are stale. */
export function tally(rows) {
  const out = { noPower: 0, loose: 0, broken: 0, working: 0, repaired: 0, unknown: 0, stale: 0 }
  for (const r of rows || []) {
    if (r.state === 'NO_POWER') out.noPower++
    else if (r.state === 'LOOSE') out.loose++
    else if (r.state === 'BROKEN') out.broken++
    else if (r.state === 'WORKING') out.working++
    else if (r.state === 'REPAIRED') out.repaired++
    else out.unknown++
    if (r.stale) out.stale++
  }
  return out
}

/** Faults first, then the rest by code — the ordering the find screen uses. */
export const roomScore = (r) => (r.noPower || 0) * 3 + (r.loose || 0) * 2 + (r.broken || 0) * 3 - (r.working || 0)

export const FAULTY = ['LOOSE', 'NO_POWER', 'BROKEN']
