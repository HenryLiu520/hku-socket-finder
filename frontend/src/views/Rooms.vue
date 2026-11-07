<template>
  <div>
    <div class="head">
      <div>
        <h2>{{ t('home.title') }}</h2>
        <p class="sf-muted">{{ t('home.intro') }}</p>
      </div>
      <div class="tools">
        <el-input v-model="q" :placeholder="t('home.search')" clearable class="search" />
      </div>
    </div>

    <div class="step">
      <span class="sf-kicker">{{ t('home.stepBuilding') }}</span>
      <div class="tabs">
        <button
          v-for="b in buildings"
          :key="b.id"
          class="tab"
          :class="{ on: b.id === buildingId }"
          @click="choose(b.id)"
        >
          <b>{{ b.code }}</b>
          <span>{{ b.name }}</span>
        </button>
      </div>
    </div>

    <div class="step">
      <span class="sf-kicker">{{ t('home.stepRoom') }}</span>
    </div>

    <div v-loading="loading">
      <section v-for="f in floors" :key="f.id" class="floor">
        <div class="floor-h">
          <span class="lvl">{{ f.level }}</span>
          <span class="sf-muted">{{ t('home.rooms', { n: f.rooms.length }, f.rooms.length) }}</span>
        </div>

        <div class="grid">
          <div v-for="r in f.rooms" :key="r.id" class="room sf-card" @click="$router.push('/rooms/' + r.id)">
            <div class="row1">
              <span class="code">{{ r.code }}</span>
              <span class="ago" :class="{ never: !r.lastCheckedAt }">{{ timeAgo(r.lastCheckedAt, 'time.neverChecked') }}</span>
            </div>
            <div class="nm">{{ r.name }}</div>

            <div class="chips">
              <span v-if="r.noPower" class="chip c-red">{{ r.noPower }} {{ stateLabel('NO_POWER', true) }}</span>
              <span v-if="r.loose" class="chip c-amber">{{ r.loose }} {{ stateLabel('LOOSE', true) }}</span>
              <span v-if="r.broken" class="chip c-red">{{ r.broken }} {{ stateLabel('BROKEN', true) }}</span>
              <span v-if="r.working" class="chip c-green">{{ r.working }} {{ stateLabel('WORKING', true) }}</span>
              <span v-if="r.repaired" class="chip c-blue">{{ r.repaired }} {{ stateLabel('REPAIRED', true) }}</span>
              <span v-if="r.unknown" class="chip c-grey">{{ r.unknown }} {{ stateLabel('UNKNOWN', true) }}</span>
            </div>

            <div class="foot">
              <span>{{ t('home.sockets', { n: r.sockets }, r.sockets) }}</span>
              <span class="open">{{ t('home.open') }}</span>
            </div>
          </div>
        </div>

        <p v-if="!f.rooms.length" class="sf-muted empty">{{ t('home.noRooms') }}</p>
      </section>

      <p v-if="!loading && !floors.length" class="sf-muted empty">{{ t('home.noMatch', { q }) }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'
import { stateLabel, timeAgo } from '../i18n'

const { t } = useI18n()

const buildings = ref([])
const buildingId = ref(null)
const loading = ref(true)
const floors = ref([])
const q = ref('')

const currentBuilding = computed(() => buildings.value.find((b) => b.id === buildingId.value) || null)

const score = (r) => r.noPower * 3 + r.loose * 2 + r.broken * 3 - r.working

function choose(id) {
  if (id === buildingId.value) return
  buildingId.value = id
  loadBuilding()
}

async function loadBuilding() {
  loading.value = true
  try {
    const b = currentBuilding.value
    if (!b) return
    const out = []
    for (const f of b.floors) {
      const { data } = await api.get('/floors/' + f.id + '/rooms')
      const needle = q.value.trim().toLowerCase()
      const rooms = data
        .filter((r) => !needle || ((b.code + '-' + r.code + ' ' + r.name).toLowerCase().includes(needle)))
        .sort((a, b2) => score(b2) - score(a) || a.code.localeCompare(b2.code))
      out.push({ id: f.id, level: f.level, rooms })
    }
    floors.value = out
  } finally {
    loading.value = false
  }
}

let timer = null
watch(q, () => {
  clearTimeout(timer)
  timer = setTimeout(loadBuilding, 180)
})

onMounted(async () => {
  try {
    const { data } = await api.get('/buildings')
    buildings.value = data
    if (data.length) {
      buildingId.value = data[0].id
      await loadBuilding()
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; gap: 16px; flex-wrap: wrap; }
h2 { margin: 0 0 5px; font-size: 22px; letter-spacing: -.4px; color: var(--sf-ink); }
.head .sf-muted { margin: 0; line-height: 1.55; max-width: 52ch; }
.tools { display: flex; align-items: center; gap: 10px; }
.search { width: 250px; max-width: 100%; }
.step { margin-bottom: 10px; }
.tabs { display: flex; flex-wrap: wrap; gap: 10px; margin: 9px 0 16px; }
.tab {
  display: flex; flex-direction: column; align-items: flex-start; gap: 2px;
  padding: 10px 15px; border: 1px solid var(--sf-line); border-radius: 11px;
  background: rgba(255, 255, 255, .92); font: inherit; cursor: pointer; transition: .14s;
  box-shadow: 0 1px 2px rgba(16, 40, 34, .04);
}
.tab b { font-size: 13px; letter-spacing: .03em; color: var(--sf-ink); }
.tab span { font-size: 11px; color: var(--sf-muted); }
.tab:hover { border-color: var(--sf-green-line); box-shadow: var(--sf-shadow); }
.tab.on {
  border-color: var(--sf-green);
  background: linear-gradient(160deg, #ffffff 0%, var(--sf-green-soft) 100%);
  box-shadow: 0 0 0 2px rgba(2, 70, 56, .12), var(--sf-shadow);
}
.tab.on b { color: var(--sf-green); }

.floor { margin-bottom: 26px; }
.floor-h { display: flex; align-items: baseline; gap: 10px; margin-bottom: 11px; padding-bottom: 7px; border-bottom: 1px solid rgba(2, 70, 56, .10); }
.lvl { font-weight: 700; font-size: 13px; letter-spacing: .05em; text-transform: uppercase; color: var(--sf-green); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }

.room { padding: 16px 17px; cursor: pointer; transition: transform .16s, box-shadow .16s, border-color .16s; display: flex; flex-direction: column; gap: 8px; }
.room:hover { border-color: var(--sf-green-line); box-shadow: var(--sf-shadow-lift); transform: translateY(-2px); }
.row1 { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
.code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; font-weight: 700; color: var(--sf-ink); letter-spacing: .01em; }
.ago { font-size: 11.5px; color: var(--sf-muted); white-space: nowrap; }
.ago.never { color: #b54708; }
.nm { font-size: 13px; color: var(--sf-muted); margin-top: -4px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font-size: 11px; padding: 3px 8px; border-radius: 7px; font-weight: 600; letter-spacing: .01em; }
.c-red { background: #fef3f2; color: #b42318; }
.c-amber { background: #fffaeb; color: #b54708; }
.c-green { background: #ecfdf3; color: #027a48; }
.c-blue { background: #eef4ff; color: #3538cd; }
.c-grey { background: #f2f4f7; color: #475467; }
.foot { display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; color: var(--sf-muted); border-top: 1px solid var(--sf-line-soft); padding-top: 9px; margin-top: 2px; }
.open { color: var(--sf-green); font-weight: 650; }
.empty { margin-top: 12px; }
</style>
