<template>
  <div>
    <div class="head">
      <div>
        <h2>Find a socket</h2>
        <p class="sf-muted">Rooms are sorted by how much is wrong with them. Faulty sockets first.</p>
      </div>
      <div class="tools">
        <el-input v-model="q" placeholder="Search, e.g. CW-L1-B" clearable class="search" />
      </div>
    </div>

    <div class="step">
      <span class="step-label">1 · Building</span>
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
      <span class="step-label">2 · Room</span>
    </div>

    <div v-loading="loading">
      <section v-for="f in floors" :key="f.id" class="floor">
        <div class="floor-h">
          <span class="lvl">{{ f.level }}</span>
          <span class="sf-muted">{{ f.rooms.length }} rooms</span>
        </div>

        <div class="grid">
          <div v-for="r in f.rooms" :key="r.id" class="room sf-card" @click="$router.push('/rooms/' + r.id)">
            <div class="row1">
              <span class="code">{{ r.code }}</span>
              <span class="ago" :class="{ never: !r.lastCheckedAt }">{{ ago(r.lastCheckedAt) }}</span>
            </div>
            <div class="nm">{{ r.name }}</div>

            <div class="chips">
              <span v-if="r.noPower" class="chip c-red">{{ r.noPower }} no power</span>
              <span v-if="r.loose" class="chip c-amber">{{ r.loose }} loose</span>
              <span v-if="r.broken" class="chip c-red">{{ r.broken }} broken</span>
              <span v-if="r.working" class="chip c-green">{{ r.working }} working</span>
              <span v-if="r.repaired" class="chip c-blue">{{ r.repaired }} repaired</span>
              <span v-if="r.unknown" class="chip c-grey">{{ r.unknown }} not checked</span>
            </div>

            <div class="foot">
              <span>{{ r.sockets }} sockets</span>
              <span class="open">Open →</span>
            </div>
          </div>
        </div>

        <p v-if="!f.rooms.length" class="sf-muted empty">No rooms on this floor yet.</p>
      </section>

      <p v-if="!loading && !floors.length" class="sf-muted empty">No rooms match “{{ q }}”.</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import api from '../api'

const buildings = ref([])
const buildingId = ref(null)
const loading = ref(true)
const floors = ref([])
const q = ref('')

const currentBuilding = computed(() => buildings.value.find((b) => b.id === buildingId.value) || null)

function ago(t) {
  if (!t) return 'never checked'
  const mins = Math.round((Date.now() - new Date(t).getTime()) / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return mins + ' min ago'
  const hours = Math.round(mins / 60)
  if (hours < 24) return hours + ' h ago'
  const days = Math.round(hours / 24)
  return days === 1 ? 'yesterday' : days + ' days ago'
}

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
.head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 18px; gap: 16px; flex-wrap: wrap; }
h2 { margin: 0 0 4px; font-size: 20px; letter-spacing: -.3px; }
.tools { display: flex; align-items: center; gap: 10px; }
.search { width: 240px; }
.step { margin-bottom: 8px; }
.step-label { display: block; font-size: 12px; font-weight: 650; letter-spacing: .3px; color: var(--sf-muted); margin-bottom: 8px; }
.tabs { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; }
.tab { display: flex; flex-direction: column; align-items: flex-start; gap: 1px; padding: 9px 14px; border: 1px solid var(--sf-line); border-radius: 10px; background: #fff; font: inherit; cursor: pointer; transition: .12s; }
.tab b { font-size: 13px; letter-spacing: .3px; }
.tab span { font-size: 11px; color: var(--sf-muted); }
.tab:hover { border-color: #c3d2cb; }
.tab.on { border-color: #0b6b4f; box-shadow: 0 0 0 2px rgba(11,107,79,.12); }
.tab.on b { color: #0b6b4f; }
.floor { margin-bottom: 24px; }
.floor-h { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; }
.lvl { font-weight: 650; font-size: 13px; letter-spacing: .4px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.room { padding: 15px 16px; cursor: pointer; transition: .15s; display: flex; flex-direction: column; gap: 8px; }
.room:hover { border-color: #c3d2cb; box-shadow: 0 6px 18px rgba(20,40,30,.07); transform: translateY(-1px); }
.row1 { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
.code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; font-weight: 600; }
.ago { font-size: 11.5px; color: var(--sf-muted); }
.ago.never { color: #b54708; }
.nm { font-size: 13px; color: var(--sf-muted); margin-top: -4px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font-size: 11px; padding: 2px 7px; border-radius: 6px; font-weight: 550; }
.c-red { background: #fef3f2; color: #b42318; }
.c-amber { background: #fffaeb; color: #b54708; }
.c-green { background: #ecfdf3; color: #027a48; }
.c-blue { background: #eef4ff; color: #3538cd; }
.c-grey { background: #f2f4f7; color: #475467; }
.foot { display: flex; justify-content: space-between; font-size: 11.5px; color: var(--sf-muted); border-top: 1px solid var(--sf-line); padding-top: 8px; }
.open { color: var(--sf-ink); }
.empty { margin-top: 12px; }
</style>
