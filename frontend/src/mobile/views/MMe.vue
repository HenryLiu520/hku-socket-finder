<template>
  <div class="m-page">
    <div class="m-card m-profile">
      <div class="m-avatar">{{ initials }}</div>
      <div class="m-profile-main">
        <div class="m-h1 m-profile-name">{{ me ? me.displayName : t('mob.account') }}</div>
        <p class="m-sub">{{ me ? me.email : '' }}</p>
      </div>
    </div>

    <div class="m-card">
      <div class="m-sec">
        <span class="m-sec-title">{{ t('mob.role') }}</span>
      </div>
      <span class="m-role" :class="{ 'is-maint': role === 'MAINTENANCE' }">
        <i class="m-dot" :style="{ background: role === 'MAINTENANCE' ? '#b49764' : '#024638' }"></i>
        {{ role === 'MAINTENANCE' ? t('nav.maintenance') : t('nav.student') }}
      </span>
    </div>

    <div class="m-card">
      <div class="m-sec">
        <span class="m-sec-title">{{ t('mob.reputation') }}</span>
      </div>

      <div v-if="loading" class="m-loading"><span class="m-spin"></span>{{ t('mob.reputation') }}</div>

      <p v-else-if="failed" class="m-note">
        {{ t('mob.loadFailed') }}
        <button class="m-link" type="button" @click="load">{{ t('mob.retry') }}</button>
      </p>

      <template v-else-if="me">
        <div class="m-stats">
          <div class="m-stat">
            <span class="m-stat-label">{{ t('mob.score') }}</span>
            <span class="m-stat-value">{{ scoreText }}</span>
          </div>
          <div class="m-stat">
            <span class="m-stat-label">{{ t('mob.weight') }}</span>
            <span class="m-stat-value">{{ weightText }}</span>
          </div>
          <div class="m-stat">
            <span class="m-stat-label">{{ t('mob.confirmed') }}</span>
            <span class="m-stat-value">{{ me.confirmed }}</span>
          </div>
          <div class="m-stat">
            <span class="m-stat-label">{{ t('mob.refuted') }}</span>
            <span class="m-stat-value">{{ me.refuted }}</span>
          </div>
        </div>
        <p class="m-fine m-stat-note">{{ t('mob.scoreHint') }}</p>
        <p class="m-fine">{{ t('mob.weightHint') }}</p>

        <div class="m-badge">
          <div class="m-bar"><span :style="{ width: (badge.progress * 100) + '%' }"></span></div>
          <p class="m-fine" v-if="badge.next">{{ t('me.next', { n: badge.need, badge: t('me.badge.' + badge.next) }) }}</p>
          <p class="m-fine" v-else>{{ t('me.allEarned') }}</p>
        </div>
      </template>
    </div>

    <div class="m-card">
      <div class="m-sec">
        <span class="m-sec-title">{{ t('mob.language') }}</span>
      </div>
      <div class="m-langs">
        <button
          v-for="l in languages"
          :key="l.value"
          type="button"
          class="m-lang"
          :class="{ on: locale === l.value }"
          :aria-pressed="locale === l.value"
          :title="l.name"
          @click="changeLang(l.value)"
        >{{ l.label }}</button>
      </div>
    </div>

    <div class="m-card m-links">
      <button v-if="roomPath" class="m-row" type="button" @click="$router.push(roomPath)">
        <MobileIcon name="room" :size="19" class="m-row-chev" />
        <span class="m-row-label">{{ t('mob.yourRoom') }}</span>
        <MobileIcon name="chevron" :size="15" class="m-row-chev" />
      </button>
      <button v-if="role === 'MAINTENANCE'" class="m-row" type="button" @click="$router.push('/maintenance')">
        <MobileIcon name="report" :size="19" class="m-row-chev" />
        <span class="m-row-label">{{ t('mob.queueLink') }}</span>
        <MobileIcon name="chevron" :size="15" class="m-row-chev" />
      </button>
    </div>

    <button class="m-btn m-btn-ghost" type="button" @click="signOut">{{ t('nav.signOut') }}</button>
  </div>
</template>

<script setup>
/**
 * Tab four: the account. /auth/me carries the reputation numbers, so this screen
 * is the only place the score, the weight behind a report and the settled
 * confirmed/refuted counts are shown together.
 */
import { computed, onMounted, ref } from 'vue'
import { BADGES, badgeFor } from '../../lib/reputation'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import api, { errorText } from '../../api'
import { SUPPORTED, setLocale } from '../../i18n'
import { useAuth } from '../../stores/auth'
import MobileIcon from '../MobileIcon.vue'
import { lastRoom } from '../lastRoom'

const { t, locale } = useI18n()
const router = useRouter()
const auth = useAuth()

const languages = SUPPORTED
const me = ref(null)
const loading = ref(true)
const failed = ref(false)
const role = ref((auth.user && auth.user.role) || 'STUDENT')

const roomPath = computed(() => (lastRoom() ? '/m/rooms/' + lastRoom() : ''))
const initials = computed(() => {
  const name = (me.value && me.value.displayName) || (auth.user && auth.user.displayName) || ''
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('')
})
const scoreText = computed(() => (me.value ? Math.round(me.value.score * 100) + '%' : '—'))
const weightText = computed(() => (me.value ? me.value.weight.toFixed(2) + '×' : '—'))

function changeLang(value) {
  setLocale(value)
}

async function load() {
  loading.value = true
  failed.value = false
  try {
    const { data } = await api.get('/auth/me')
    me.value = data
    role.value = data.role
    auth.user = { email: data.email, displayName: data.displayName, role: data.role }
    localStorage.setItem('sf_user', JSON.stringify(auth.user))
  } catch (e) {
    failed.value = true
    errorText(e)
  } finally {
    loading.value = false
  }
}

function signOut() {
  auth.logout()
  router.push('/login')
}

onMounted(load)
</script>
