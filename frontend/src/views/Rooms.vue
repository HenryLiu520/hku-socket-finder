<template>
  <div>
    <div class="head">
      <div>
        <h2>Find a socket</h2>
        <p class="sf-muted">Pick a building, then a room. The room opens as a list of every socket in it.</p>
      </div>
      <el-select v-model="buildingId" class="pick" @change="loadBuilding">
        <el-option
          v-for="b in buildings"
          :key="b.id"
          :label="b.code + ' · ' + b.name"
          :value="b.id"
        />
      </el-select>
    </div>

    <div v-loading="loading">
      <section v-for="f in floors" :key="f.id" class="floor">
        <div class="floor-h">
          <span class="lvl">{{ f.level }}</span>
          <span class="sf-muted">{{ f.rooms.length }} rooms</span>
        </div>

        <el-row :gutter="16">
          <el-col v-for="r in f.rooms" :key="r.id" :xs="24" :sm="12" :md="8">
            <div class="room sf-card" @click="$router.push('/rooms/' + r.id)">
              <div class="code">{{ r.code }}</div>
              <div class="nm">{{ r.name }}</div>
              <div class="stat">
                <span><b>{{ r.sockets }}</b> sockets</span>
                <span class="ok">{{ r.working }} working</span>
                <span class="bad">{{ r.broken }} faulty</span>
                <span v-if="r.repaired" class="rep">{{ r.repaired }} repaired</span>
              </div>
              <div class="hint">Open room →</div>
            </div>
          </el-col>
        </el-row>

        <p v-if="!f.rooms.length" class="sf-muted">No rooms on this floor yet.</p>
      </section>

      <p v-if="!loading && !floors.length" class="sf-muted">No rooms seeded yet.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const buildings = ref([])
const buildingId = ref(null)
const loading = ref(true)
const floors = ref([])

async function loadBuilding() {
  loading.value = true
  try {
    const b = buildings.value.find((x) => x.id === buildingId.value)
    if (!b) return
    const out = []
    for (const f of b.floors) {
      const { data } = await api.get('/floors/' + f.id + '/rooms')
      out.push({ id: f.id, level: f.level, rooms: data })
    }
    floors.value = out
  } finally {
    loading.value = false
  }
}

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
.pick { width: 280px; }
.floor { margin-bottom: 22px; }
.floor-h { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; }
.lvl { font-weight: 650; font-size: 13px; letter-spacing: .4px; color: var(--sf-ink); }
.room { padding: 16px; margin-bottom: 16px; cursor: pointer; transition: .15s; }
.room:hover { border-color: #c3d2cb; box-shadow: 0 4px 14px rgba(20,40,30,.06); transform: translateY(-1px); }
.code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; color: var(--sf-muted); }
.nm { font-weight: 600; margin: 4px 0 10px; }
.stat { display: flex; flex-wrap: wrap; gap: 10px; font-size: 12px; color: var(--sf-muted); }
.ok { color: #0b6b4f; }
.bad { color: #c0392b; }
.rep { color: #3538cd; }
.hint { margin-top: 12px; font-size: 12px; color: var(--sf-muted); }
</style>
