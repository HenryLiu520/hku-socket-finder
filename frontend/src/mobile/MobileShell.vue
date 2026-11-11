<template>
  <div class="m-app">
    <div class="m-frame">
      <header class="m-bar">
        <button
          v-if="canBack"
          class="m-bar-back"
          type="button"
          :aria-label="t('mob.back')"
          @click="goBack"
        >
          <MobileIcon name="back" :size="22" />
        </button>

        <div class="m-brand">
          <span class="m-mark"><i></i></span>
          <span class="m-brand-name">{{ t('app.name') }}</span>
        </div>
      </header>

      <div ref="scroller" class="m-scroll">
        <router-view v-slot="{ Component }">
          <transition name="m-fade" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </div>

      <MobileTabBar :active="activeTab" @select="onSelect" />
    </div>
  </div>
</template>

<script setup>
/**
 * The app shell: one fixed bar at the top, one fixed four-tab bar at the bottom,
 * and a single scrolling surface between them. Screens never reach for the window
 * scroll, so the chrome cannot drift on a phone.
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import MobileIcon from './MobileIcon.vue'
import MobileTabBar from './MobileTabBar.vue'
import { lastRoom } from './lastRoom'
import './mobile.css'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const scroller = ref(null)

const activeTab = computed(() => route.meta.tab || 'find')
const canBack = computed(() => route.name === 'm-room' || route.name === 'm-report')

function goBack() {
  const previous = window.history.state && window.history.state.back
  if (previous) router.back()
  else router.push('/m')
}

function tabPath(tab) {
  if (tab === 'room') return lastRoom() ? '/m/rooms/' + lastRoom() : '/m'
  if (tab === 'report') return '/m/report'
  if (tab === 'me') return '/m/me'
  return '/m'
}

function onSelect(tab) {
  const target = tabPath(tab)
  if (route.path === target) {
    if (scroller.value) scroller.value.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }
  router.push(target)
}

watch(
  () => route.fullPath,
  () => {
    if (scroller.value) scroller.value.scrollTop = 0
  }
)

/* While a mobile route is open the window itself is painted as app paper, so the
   desktop photo backdrop and its gold rule never peek out around the frame. */
onMounted(() => document.documentElement.classList.add('m-mode'))
onBeforeUnmount(() => document.documentElement.classList.remove('m-mode'))
</script>
