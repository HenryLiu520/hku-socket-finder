#!/usr/bin/env node
/**
 * Key parity check for the three interface languages.
 *
 * Fails when
 *   - a key exists in one language but not another,
 *   - a key is empty,
 *   - a plural message ("{n} day | {n} days") has a different number of forms,
 *   - an interpolation placeholder ({n}, {state}, ...) is missing in a translation.
 *
 * Run with `npm run i18n:check`; it also runs first thing inside `npm run build`.
 */
import en from '../src/i18n/en.js'
import zhCN from '../src/i18n/zh-CN.js'
import zhTW from '../src/i18n/zh-TW.js'

const LOCALES = [
  ['en', en],
  ['zh-CN', zhCN],
  ['zh-TW', zhTW]
]

function flatten(obj, prefix = '', out = new Map()) {
  for (const [k, v] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${k}` : k
    if (v && typeof v === 'object') flatten(v, path, out)
    else out.set(path, String(v))
  }
  return out
}

const flat = new Map(LOCALES.map(([code, messages]) => [code, flatten(messages)]))
const union = new Set([...flat.values()].flatMap((m) => [...m.keys()]))
const sorted = [...union].sort()

let problems = 0
const rows = []

for (const key of sorted) {
  const cells = LOCALES.map(([code]) => flat.get(code).get(key))
  const missing = LOCALES.filter((_, i) => cells[i] === undefined).map(([code]) => code)
  if (missing.length) {
    console.error(`MISSING  ${key}  (${missing.join(', ')})`)
    problems++
    continue
  }

  const blank = LOCALES.filter((_, i) => cells[i].trim() === '').map(([code]) => code)
  if (blank.length) {
    console.error(`EMPTY    ${key}  (${blank.join(', ')})`)
    problems++
    continue
  }

  // Plural forms: the pipe-separated count must match across languages.
  const forms = cells.map((c) => c.split('|').length)
  if (new Set(forms).size > 1) {
    console.error(`PLURALS  ${key}  forms=${forms.join(' / ')}`)
    problems++
  }

  // Placeholders must survive translation.
  const holders = cells.map((c) => (c.match(/\{[a-zA-Z0-9_]+\}/g) || []).sort().join(','))
  if (new Set(holders).size > 1) {
    console.error(`PLACEHOLDER  ${key}  ${holders.map((h) => `[${h}]`).join(' ')}`)
    problems++
  }

  rows.push(key)
}

const width = 22
console.log('i18n key parity')
for (const [code] of LOCALES) {
  console.log(`  ${code.padEnd(6)} ${String(flat.get(code).size).padStart(3)} keys`)
}
console.log(`  ${'shared'.padEnd(6)} ${String(rows.length).padStart(3)} keys  ` +
  `(flattened: app.*, nav.*, state.*, home.*, room.*, map.*, report.*, maint.*, login.* ...)`)

if (problems) {
  console.error(`\nFAILED: ${problems} problem(s) across ${sorted.length} keys.`)
  process.exit(1)
}
console.log(`\nOK: all ${sorted.length} keys exist in ${LOCALES.map(([c]) => c).join(' / ')} with matching shape.`)
