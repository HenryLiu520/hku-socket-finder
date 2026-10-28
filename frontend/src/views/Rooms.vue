<template>
  <div>
    <div class="head">
      <div>
        <h2>Chi Wah Learning Commons</h2>
        <p class="sf-muted">Level 1 · three rooms typed in by hand for iteration 1</p>
      </div>
      <el-tag v-if="rooms.length" type="info" effect="plain">{{ totals }}</el-tag>
    </div>

    <el-row :gutter="16" v-loading="loading">
      <el-col v-for="r in rooms" :key="r.id" :xs="24" :sm="12" :md="8">
        <div class="room sf-card" @click="$router.push('/rooms/' + r.id)">
          <div class="code">{{ r.code }}</div>
          <div class="nm">{{ r.name }}</div>
          <div class="stat">
            <span><b>{{ r.sockets }}</b> sockets</span>
            <span class="ok">{{ r.working }} working</span>
            <span class="bad">{{ r.broken }} broken</span>
            <span v-if="r.repaired" class="rep">{{ r.repaired }} repaired</span>
          </div>
          <div class="hint">Open room →</div>
        </div>
      </el-col>
    </el-row>

    <p v-if="!loading && !rooms.length" class="sf-muted">No rooms seeded yet.</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../api'

const rooms = ref([])
const loading = ref(true)

const totals = computed(() => {
  const s = rooms.value.reduce((n, r) => n + r.sockets, 0)
  const b = rooms.value.reduce((n, r) => n + r.broken, 0)
  return s + ' sockets · ' + b + ' broken'
})

onMounted(async () => {
  try {
    const { data: buildings } = await api.get('/buildings')
    const floor = buildings[0].floors[0].id
    const { data } = await api.get('/floors/' + floor + '/rooms')
    rooms.value = data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 18px; }
h2 { margin: 0 0 4px; font-size: 20px; letter-spacing: -.3px; }
.room { padding: 16px; margin-bottom: 16px; cursor: pointer; transition: .15s; }
.room:hover { border-color: #c3d2cb; box-shadow: 0 4px 14px rgba(20,40,30,.06); transform: translateY(-1px); }
.code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; color: var(--sf-muted); }
.nm { font-size: 15px; font-weight: 600; margin: 6px 0 12px; }
.stat { display: flex; gap: 12px; font-size: 12.5px; }
.stat b { font-size: 15px; }
.ok { color: #0b6b4f; }
.bad { color: #b42318; }
.rep { color: #3538cd; }
.hint { margin-top: 14px; font-size: 12.5px; color: var(--sf-green); }
</style>
