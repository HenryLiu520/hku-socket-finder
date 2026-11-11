<template>
  <div class="m-page">
    <div v-if="loading" class="m-loading"><span class="m-spin"></span>{{ t('mob.socketsHere') }}</div>

    <p v-else-if="failed" class="m-note">
      {{ t('mob.loadFailed') }}
      <button class="m-link" type="button" @click="load">{{ t('mob.retry') }}</button>
    </p>

    <template v-else>
      <div class="m-lead">
        <div class="m-lead-row">
          <h1 class="m-h1 m-mono">{{ room.code }}</h1>
          <button class="m-seg-btn" type="button" @click="gotoReport">{{ t('room.reportFault') }}</button>
        </div>
        <p class="m-sub">{{ room.name }} · {{ room.buildingName }} · {{ room.level }}</p>
      </div>

      <div class="m-card m-summary">
        <div class="m-summary-total">
          <b>{{ rows.length }}</b>
          <span>{{ t('room.sockets', { n: rows.length }, rows.length) }}</span>
        </div>
        <div class="m-chips">
          <span v-if="counts.noPower" class="m-chip">
            <i class="m-dot" :style="{ background: dotColor('NO_POWER') }"></i>{{ counts.noPower }} {{ stateLabel('NO_POWER', true) }}
          </span>
          <span v-if="counts.broken" class="m-chip">
            <i class="m-dot" :style="{ background: dotColor('BROKEN') }"></i>{{ counts.broken }} {{ stateLabel('BROKEN', true) }}
          </span>
          <span v-if="counts.loose" class="m-chip">
            <i class="m-dot" :style="{ background: dotColor('LOOSE') }"></i>{{ counts.loose }} {{ stateLabel('LOOSE', true) }}
          </span>
          <span v-if="counts.working" class="m-chip">
            <i class="m-dot" :style="{ background: dotColor('WORKING') }"></i>{{ counts.working }} {{ stateLabel('WORKING', true) }}
          </span>
          <span v-if="counts.repaired" class="m-chip">
            <i class="m-dot" :style="{ background: dotColor('REPAIRED') }"></i>{{ counts.repaired }} {{ stateLabel('REPAIRED', true) }}
          </span>
          <span v-if="counts.unknown" class="m-chip">
            <i class="m-dot" :style="{ background: dotColor('UNKNOWN') }"></i>{{ counts.unknown }} {{ stateLabel('UNKNOWN', true) }}
          </span>
          <span v-if="counts.stale" class="m-chip">{{ t('room.statOld', { n: counts.stale }) }}</span>
        </div>
      </div>

      <div class="m-card m-plan-card">
        <div class="m-sec">
          <span class="m-sec-title">{{ t('map.title') }}</span>
        </div>
        <MobilePlan v-if="room.seats && room.seats.length" :seats="room.seats" @pick="openSheet" />
        <p v-else class="m-note">{{ t('mob.noSockets') }}</p>

        <div class="m-legend">
          <span><i class="m-dot" :style="{ background: dotColor('WORKING') }"></i>{{ stateLabel('WORKING', true) }}</span>
          <span><i class="m-dot" :style="{ background: dotColor('LOOSE') }"></i>{{ stateLabel('LOOSE', true) }}</span>
          <span><i class="m-dot" :style="{ background: dotColor('NO_POWER') }"></i>{{ stateLabel('NO_POWER', true) }}</span>
          <span><i class="m-dot" :style="{ background: dotColor('REPAIRED') }"></i>{{ stateLabel('REPAIRED', true) }}</span>
          <span><i class="m-dot" :style="{ background: dotColor('UNKNOWN') }"></i>{{ stateLabel('UNKNOWN', true) }}</span>
        </div>
        <p class="m-plan-note">{{ t('mob.tapSocket') }}</p>
      </div>

      <div class="m-sec">
        <span class="m-sec-title">{{ t('room.colSocket') }}</span>
        <span class="m-count">{{ t('room.shown', { n: shown.length }) }}</span>
      </div>

      <div class="m-seg">
        <button
          v-for="f in FILTERS"
          :key="f.key"
          type="button"
          class="m-seg-btn"
          :class="{ on: filter === f.key }"
          :aria-pressed="filter === f.key"
          @click="filter = f.key"
        >{{ t(f.label) }}</button>
      </div>

      <div v-if="shown.length" class="m-card m-list">
        <button v-for="s in shown" :key="s.id" type="button" class="m-row" @click="openSheet(s)">
          <i class="m-dot" :style="{ background: dotColor(s.state) }"></i>
          <span class="m-row-main">
            <span class="m-row-code">{{ tail(s.code) }}</span>
            <span class="m-row-sub">{{ s.code }} · {{ s.seat }}</span>
          </span>
          <span class="m-row-side">
            <span class="m-row-state">{{ stateLabel(s.state) }}</span>
            <span class="m-row-ago" :class="{ stale: s.stale }">{{ timeAgo(s.lastCheckedAt, 'time.neverChecked') }}</span>
          </span>
          <MobileIcon name="chevron" :size="15" class="m-row-chev" />
        </button>
      </div>

      <p v-else class="m-note">{{ t('room.empty') }}</p>
    </template>

    <SocketSheet :socket="current" :open="sheet" @close="sheet = false" @updated="reload" />
  </div>
</template>

<script setup>
/**
 * Tab two: one room. The plan and the list are two views of the same rows —
 * tapping either opens the report sheet, and a successful report refreshes the
 * room so the colour the user just changed is the colour they see.
 */
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api'
import { stateLabel, timeAgo } from '../../i18n'
import MobileIcon from '../MobileIcon.vue'
import MobilePlan from '../MobilePlan.vue'
import SocketSheet from '../SocketSheet.vue'
import { rememberRoom } from '../lastRoom'
import { FAULTY, dotColor, socketRows, tail, tally } from '../socketState.js'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const FILTERS = [
  { key: 'all', label: 'room.filterAll' },
  { key: 'faulty', label: 'room.filterFaulty' },
  { key: 'old', label: 'room.filterOld' }
]

const room = ref({ seats: [] })
const rows = ref([])
const loading = ref(true)
const failed = ref(false)
const filter = ref('all')

const sheet = ref(false)
const current = ref(null)

const counts = computed(() => tally(rows.value))

const shown = computed(() => {
  if (filter.value === 'faulty') return rows.value.filter((r) => FAULTY.includes(r.state))
  if (filter.value === 'old') return rows.value.filter((r) => r.stale)
  return rows.value
})

async function load() {
  failed.value = false
  const { data } = await api.get('/rooms/' + route.params.id)
  room.value = data
  rows.value = socketRows(data)
  rememberRoom(data.id)
  if (sheet.value && current.value) {
    current.value = rows.value.find((r) => r.id === current.value.id) || current.value
  }
}

async function reload() {
  try {
    await load()
  } catch (e) {
    /* the sheet already shows the failure; keep the rows that are on screen */
  }
}

function openSheet(socket) {
  current.value = socket
  sheet.value = true
}

function gotoReport() {
  router.push({ path: '/m/report', query: { room: room.value.id } })
}

onMounted(async () => {
  try {
    await load()
  } catch (e) {
    failed.value = true
  } finally {
    loading.value = false
  }
})
</script>
