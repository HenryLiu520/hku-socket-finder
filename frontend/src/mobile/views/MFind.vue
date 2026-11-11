<template>
  <div class="m-page">
    <div class="m-lead">
      <h1 class="m-h1">{{ t('home.title') }}</h1>
      <p class="m-sub">{{ t('home.intro') }}</p>
    </div>

    <div class="m-search">
      <MobileIcon name="find" :size="17" />
      <input
        v-model="q"
        type="search"
        autocomplete="off"
        :placeholder="t('home.search')"
        :aria-label="t('home.search')"
      />
    </div>

    <div class="m-sec">
      <span class="m-sec-title">{{ t('home.stepBuilding') }}</span>
    </div>

    <div class="m-seg">
      <button
        v-for="b in buildings"
        :key="b.id"
        type="button"
        class="m-bseg"
        :class="{ on: b.id === buildingId }"
        :aria-pressed="b.id === buildingId"
        @click="choose(b.id)"
      >
        <b>{{ b.code }}</b>
        <span>{{ b.name }}</span>
      </button>
    </div>

    <div v-if="loading" class="m-loading"><span class="m-spin"></span>{{ t('home.stepRoom') }}</div>

    <p v-else-if="failed" class="m-note">
      {{ t('mob.loadFailed') }}
      <button class="m-link" type="button" @click="load(true)">{{ t('mob.retry') }}</button>
    </p>

    <template v-else-if="building">
      <div class="m-sec">
        <span class="m-sec-title">{{ t('home.stepRoom') }}</span>
        <span class="m-count">{{ t('mob.rooms', { n: rooms.length }, rooms.length) }}</span>
      </div>

      <div v-if="building.floors.length > 1" class="m-seg">
        <button class="m-seg-btn" :class="{ on: level === 'all' }" type="button" @click="level = 'all'">
          {{ t('mob.floorAll') }}
        </button>
        <button
          v-for="f in building.floors"
          :key="f.id"
          class="m-seg-btn"
          :class="{ on: level === String(f.id) }"
          type="button"
          @click="level = String(f.id)"
        >{{ f.level }}</button>
      </div>

      <div class="m-roomlist">
        <button v-for="r in visible" :key="r.id" type="button" class="m-card m-roomcard" @click="openRoom(r)">
          <div class="m-roomcard-top">
            <span class="m-roomcard-code m-mono">{{ r.code }}</span>
            <span class="m-roomcard-ago" :class="{ stale: !r.lastCheckedAt }">
              {{ timeAgo(r.lastCheckedAt, 'time.neverChecked') }}
            </span>
          </div>
          <div class="m-roomcard-name">{{ r.name }} · {{ r.level }}</div>

          <div class="m-chips">
            <span v-if="r.noPower" class="m-chip">
              <i class="m-dot" :style="{ background: dotColor('NO_POWER') }"></i>{{ r.noPower }} {{ stateLabel('NO_POWER', true) }}
            </span>
            <span v-if="r.broken" class="m-chip">
              <i class="m-dot" :style="{ background: dotColor('BROKEN') }"></i>{{ r.broken }} {{ stateLabel('BROKEN', true) }}
            </span>
            <span v-if="r.loose" class="m-chip">
              <i class="m-dot" :style="{ background: dotColor('LOOSE') }"></i>{{ r.loose }} {{ stateLabel('LOOSE', true) }}
            </span>
            <span v-if="r.working" class="m-chip">
              <i class="m-dot" :style="{ background: dotColor('WORKING') }"></i>{{ r.working }} {{ stateLabel('WORKING', true) }}
            </span>
            <span v-if="r.repaired" class="m-chip">
              <i class="m-dot" :style="{ background: dotColor('REPAIRED') }"></i>{{ r.repaired }} {{ stateLabel('REPAIRED', true) }}
            </span>
            <span v-if="r.unknown" class="m-chip">
              <i class="m-dot" :style="{ background: dotColor('UNKNOWN') }"></i>{{ r.unknown }} {{ stateLabel('UNKNOWN', true) }}
            </span>
          </div>

          <div class="m-roomcard-foot">
            <span>{{ t('home.sockets', { n: r.sockets }, r.sockets) }}</span>
            <span class="m-roomcard-open">{{ t('home.open') }}</span>
          </div>
        </button>
      </div>

      <p v-if="!visible.length" class="m-note">
        {{ q ? t('home.noMatch', { q }) : t('home.noRooms') }}
      </p>
    </template>
  </div>
</template>

<script setup>
/**
 * Tab one: pick a building, then a room. The rooms of a building arrive one
 * floor at a time from /floors/{id}/rooms, and each answer is cached per session
 * so flicking between buildings on a phone stays instant.
 */
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import api from '../../api'
import { stateLabel, timeAgo } from '../../i18n'
import MobileIcon from '../MobileIcon.vue'
import { dotColor, roomScore } from '../socketState.js'

const { t } = useI18n()
const router = useRouter()

const cache = new Map()

const buildings = ref([])
const buildingId = ref(null)
const rooms = ref([])
const level = ref('all')
const q = ref('')
const loading = ref(true)
const failed = ref(false)

const building = computed(() => buildings.value.find((b) => b.id === buildingId.value) || null)

const visible = computed(() => {
  const needle = q.value.trim().toLowerCase()
  return rooms.value.filter((r) => {
    if (level.value !== 'all' && String(r.floorId) !== level.value) return false
    if (!needle) return true
    const b = building.value
    const hay = ((b ? b.code : '') + '-' + r.code + ' ' + r.name).toLowerCase()
    return hay.includes(needle)
  })
})

async function loadRooms(id, force = false) {
  const b = buildings.value.find((x) => x.id === id)
  if (!b) return
  if (!force && cache.has(id)) {
    rooms.value = cache.get(id)
    loading.value = false
    return
  }
  loading.value = true
  failed.value = false
  try {
    const out = []
    for (const f of b.floors) {
      const { data } = await api.get('/floors/' + f.id + '/rooms')
      for (const r of data) out.push({ ...r, level: f.level, floorId: f.id })
    }
    out.sort((a, c) => roomScore(c) - roomScore(a) || String(a.code).localeCompare(String(c.code)))
    cache.set(id, out)
    rooms.value = out
  } catch (e) {
    failed.value = true
    rooms.value = []
  } finally {
    loading.value = false
  }
}

function choose(id) {
  if (id === buildingId.value) return
  buildingId.value = id
  level.value = 'all'
  loadRooms(id)
}

function openRoom(r) {
  router.push('/m/rooms/' + r.id)
}

async function load(force = false) {
  loading.value = true
  failed.value = false
  try {
    if (force) cache.clear()
    const { data } = await api.get('/buildings')
    buildings.value = data
    if (!data.length) return
    if (!data.some((b) => b.id === buildingId.value)) buildingId.value = data[0].id
    await loadRooms(buildingId.value, force)
  } catch (e) {
    failed.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => load())
</script>
