<template>
  <el-config-provider :locale="epLocale">
    <div class="shell">
      <header class="bar">
        <div class="sf-wrap bar-inner">
          <div class="brand" @click="$router.push('/')">
            <span class="mark"><i class="dot"></i></span>
            <div>
              <div class="name">Socket Finder</div>
              <div class="sub">{{ t('app.subtitle') }}</div>
            </div>
          </div>

          <nav v-if="auth.signedIn" class="nav">
            <router-link to="/" class="navlink">{{ t('nav.find') }}</router-link>
            <router-link to="/report" class="navlink">{{ t('nav.report') }}</router-link>
            <router-link v-if="auth.isMaintenance" to="/maintenance" class="navlink">{{ t('nav.queue') }}</router-link>
          </nav>

          <div class="tail">
            <!-- Language switch: three buttons, one tap each, no page reload. -->
            <div v-if="!hideLang" class="langs" role="group" :aria-label="t('lang.label')">
              <button
                v-for="l in languages"
                :key="l.value"
                type="button"
                class="lang"
                :class="{ on: locale === l.value }"
                :title="l.name"
                :aria-pressed="locale === l.value"
                @click="changeLang(l.value)"
              >{{ l.label }}</button>
            </div>

            <div v-if="auth.signedIn" class="who">
              <span class="pill" :class="auth.isMaintenance ? 'pill-m' : 'pill-s'">
                {{ auth.isMaintenance ? t('nav.maintenance') : t('nav.student') }}
              </span>
              <span class="who-name">{{ auth.user.displayName }}</span>
              <el-button link type="primary" @click="signOut">{{ t('nav.signOut') }}</el-button>
            </div>
          </div>
        </div>
      </header>

      <main class="sf-wrap main">
        <div class="page-paper">
          <router-view />
        </div>
      </main>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuth } from './stores/auth'
import { SUPPORTED, setLocale } from './i18n'
import en from 'element-plus/es/locale/lang/en'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import zhTw from 'element-plus/es/locale/lang/zh-tw'

const { t, locale } = useI18n()
const auth = useAuth()
const router = useRouter()

const languages = SUPPORTED
// The demo recording sets localStorage sf_hide_lang = '1' so the switch never appears on camera.
const hideLang = localStorage.getItem('sf_hide_lang') === '1'
const epLocales = { en, 'zh-CN': zhCn, 'zh-TW': zhTw }
const epLocale = computed(() => epLocales[locale.value] || en)

function changeLang(value) {
  setLocale(value)
}

function signOut() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.shell { min-height: 100%; display: flex; flex-direction: column; min-width: 0; }

/* Header: translucent white over the textured background, with a warm hairline. */
.bar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, .88);
  -webkit-backdrop-filter: saturate(1.4) blur(12px);
  backdrop-filter: saturate(1.4) blur(12px);
  border-bottom: 1px solid rgba(2, 70, 56, .10);
  box-shadow: 0 1px 2px rgba(16, 40, 34, .04), 0 12px 24px -22px rgba(16, 40, 34, .55);
}
.bar-inner { display: flex; align-items: center; gap: 22px; height: 66px; }

.brand { display: flex; align-items: center; gap: 11px; cursor: pointer; min-width: 0; }
.mark {
  width: 30px; height: 30px; border-radius: 9px; flex: 0 0 auto;
  display: grid; place-items: center;
  background: linear-gradient(160deg, var(--sf-green) 0%, var(--sf-green-deep) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .18), 0 6px 14px -8px rgba(2, 70, 56, .9);
}
.dot {
  width: 8px; height: 8px; border-radius: 50%; background: var(--sf-gold-soft);
  box-shadow: 0 0 0 3px rgba(180, 151, 100, .35);
}
.name { font-weight: 700; font-size: 15px; letter-spacing: -.01em; color: var(--sf-green); }
.sub { font-size: 11.5px; color: var(--sf-muted); letter-spacing: .01em; }

.nav { display: flex; gap: 4px; margin-left: 6px; flex-wrap: wrap; }
.navlink {
  color: var(--sf-muted); text-decoration: none; font-size: 13.5px;
  padding: 8px 11px; border-radius: 8px; white-space: nowrap; transition: .14s;
}
.navlink:hover { color: var(--sf-ink); background: rgba(2, 70, 56, .055); }
.navlink.router-link-active {
  color: var(--sf-green); font-weight: 650; background: var(--sf-green-soft);
}

.tail { margin-left: auto; display: flex; align-items: center; gap: 14px; min-width: 0; }

/* Segmented language control: a paper pill holding three buttons. */
.langs {
  display: inline-flex; padding: 3px; gap: 2px;
  background: rgba(2, 70, 56, .06);
  border: 1px solid rgba(2, 70, 56, .08);
  border-radius: 999px;
}
.lang {
  border: 0; background: transparent; font: inherit; font-size: 12px; font-weight: 600;
  color: var(--sf-muted); padding: 4px 10px; border-radius: 999px; cursor: pointer;
  line-height: 1.4; transition: .14s;
}
.lang:hover { color: var(--sf-green); }
.lang.on {
  background: #fff; color: var(--sf-green);
  box-shadow: 0 1px 2px rgba(16, 40, 34, .12), 0 0 0 1px rgba(2, 70, 56, .06);
}

.who { display: flex; align-items: center; gap: 10px; font-size: 13px; min-width: 0; }
.who-name { color: var(--sf-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 160px; }
.pill { font-size: 11px; padding: 3px 9px; border-radius: 999px; font-weight: 650; letter-spacing: .02em; }
.pill-s { background: var(--sf-green-soft); color: var(--sf-green); box-shadow: inset 0 0 0 1px var(--sf-green-line); }
.pill-m { background: var(--sf-gold-wash); color: #7d6132; box-shadow: inset 0 0 0 1px var(--sf-gold-soft); }

.main { padding: 18px 20px 56px; flex: 1; min-width: 0; width: 100%; }
.page-paper {
  background: rgba(252, 253, 252, .95);
  border: 1px solid rgba(226, 233, 230, .85);
  border-radius: 20px;
  padding: 22px 24px 26px;
  box-shadow: 0 30px 70px -52px rgba(2, 70, 56, .6);
}

/* Narrow windows: the header stacks instead of pushing the page sideways. */
@media (max-width: 820px) {
  .bar-inner { height: auto; padding-top: 10px; padding-bottom: 10px; flex-wrap: wrap; row-gap: 8px; }
  .nav { order: 3; width: 100%; margin-left: 0; gap: 2px; }
  .navlink { padding: 6px 9px; }
  .tail { gap: 8px; }
  .who-name { display: none; }
  .main { padding: 18px 16px 48px; }
}
@media (max-width: 560px) {
  .sub { display: none; }
}
</style>
