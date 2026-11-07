import { createI18n } from 'vue-i18n'
import en from './en'
import zhCN from './zh-CN'
import zhTW from './zh-TW'

/** The three languages the interface ships with. `label` is what the header shows. */
export const SUPPORTED = [
  { value: 'en', label: 'EN', name: 'English' },
  { value: 'zh-CN', label: '简', name: '简体中文' },
  { value: 'zh-TW', label: '繁', name: '繁體中文' }
]

export const STORAGE_KEY = 'sf_lang'
export const FALLBACK = 'en'

const VALUES = SUPPORTED.map((l) => l.value)

/** Saved choice first, then the browser's language, then English. */
export function detectLocale() {
  let saved = null
  try {
    saved = localStorage.getItem(STORAGE_KEY)
  } catch (e) {
    saved = null
  }
  if (VALUES.includes(saved)) return saved

  const tags = []
  if (typeof navigator !== 'undefined') {
    if (Array.isArray(navigator.languages)) tags.push(...navigator.languages)
    if (navigator.language) tags.push(navigator.language)
  }
  for (const tag of tags) {
    const low = String(tag).toLowerCase()
    if (!low.startsWith('zh')) continue
    // Hant scripts and HK/TW/MO regions read Traditional; everything else Simplified.
    if (/hant|-tw|-hk|-mo/.test(low)) return 'zh-TW'
    return 'zh-CN'
  }
  return FALLBACK
}

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: detectLocale(),
  fallbackLocale: FALLBACK,
  messages: { en, 'zh-CN': zhCN, 'zh-TW': zhTW }
})

function applyDocumentLang(value) {
  if (typeof document !== 'undefined') document.documentElement.lang = value
}
applyDocumentLang(i18n.global.locale.value)

/** Switch language without a reload, and remember the choice. */
export function setLocale(value) {
  const next = VALUES.includes(value) ? value : FALLBACK
  i18n.global.locale.value = next
  try {
    localStorage.setItem(STORAGE_KEY, next)
  } catch (e) {
    /* private mode: the session still switches, it just is not remembered */
  }
  applyDocumentLang(next)
  return next
}

export function currentLocale() {
  return i18n.global.locale.value
}

/** For code outside a component (api.js, formatters): translate through the global instance. */
export function tt(key, named) {
  return named === undefined ? i18n.global.t(key) : i18n.global.t(key, named)
}

/** Translate a socket state code, falling back to the raw code if a state is unknown. */
export function stateLabel(code, lower = false) {
  const key = (lower ? 'stateLower.' : 'state.') + code
  return i18n.global.te(key) ? i18n.global.t(key) : code
}

/**
 * Relative time in the current language.
 * Returns a translated string; `neverKey` lets callers say "never" or "never checked".
 */
export function timeAgo(iso, neverKey = 'common.never') {
  const t = i18n.global.t
  if (!iso) return t(neverKey)
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000)
  if (mins < 1) return t('time.justNow')
  if (mins < 60) return t('time.minAgo', { n: mins })
  const hours = Math.round(mins / 60)
  if (hours < 24) return t('time.hourAgo', { n: hours })
  const days = Math.round(hours / 24)
  return days === 1 ? t('time.yesterday') : t('time.daysAgo', { n: days })
}

export default i18n
