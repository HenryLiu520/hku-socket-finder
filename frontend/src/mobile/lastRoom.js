/**
 * The tab bar needs somewhere for "Room" to go before a room has been opened in
 * this session, so the last room a person looked at is remembered between visits.
 */
const KEY = 'sf_m_last_room'

export function rememberRoom(id) {
  try {
    if (id) localStorage.setItem(KEY, String(id))
  } catch (e) {
    /* private mode: the tab simply falls back to the find screen */
  }
}

export function lastRoom() {
  try {
    return localStorage.getItem(KEY) || ''
  } catch (e) {
    return ''
  }
}
