<template>
  <div v-loading="loading">
    <div class="top">
      <el-button link @click="$router.push('/')">← All rooms</el-button>
      <div class="title">
        <div>
          <h2>{{ room.code }} · {{ room.name }}</h2>
          <p class="sf-muted">{{ room.buildingName }} · {{ room.level }}</p>
        </div>
        <el-button type="primary" plain @click="$router.push({ path: '/report', query: { room: room.id } })">
          Report a fault
        </el-button>
      </div>
    </div>

    <div class="summary">
      <span class="stat"><b>{{ rows.length }}</b> sockets</span>
      <span v-if="counts.noPower" class="stat c-red"><b>{{ counts.noPower }}</b> no power</span>
      <span v-if="counts.loose" class="stat c-amber"><b>{{ counts.loose }}</b> loose</span>
      <span v-if="counts.working" class="stat c-green"><b>{{ counts.working }}</b> working</span>
      <span v-if="counts.unknown" class="stat c-grey"><b>{{ counts.unknown }}</b> not checked</span>
      <span v-if="counts.stale" class="stat c-amber"><b>{{ counts.stale }}</b> old</span>
    </div>

    <div class="bar">
      <el-radio-group v-model="filter" size="small">
        <el-radio-button value="all">All</el-radio-button>
        <el-radio-button value="faulty">Faulty</el-radio-button>
        <el-radio-button value="old">Old</el-radio-button>
      </el-radio-group>
      <span class="sf-muted hint">{{ shown.length }} shown</span>
    </div>

    <el-table :data="shown" class="sf-card" empty-text="No sockets entered for this room yet">
      <el-table-column label="Socket" width="190">
        <template #default="{ row }"><code>{{ row.code }}</code></template>
      </el-table-column>

      <el-table-column label="Seat" prop="seat" width="70" />

      <el-table-column label="State" width="150">
        <template #default="{ row }">
          <span class="state" :class="'s-' + row.state.toLowerCase()">
            <i class="dot"></i>{{ pretty(row.state) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column label="Last changed" width="170">
        <template #default="{ row }">
          <span :class="{ old: row.stale }">{{ ago(row.lastCheckedAt) }}</span>
          <el-tag v-if="row.stale" type="warning" size="small" effect="plain" class="old-tag">old</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Last report" width="170">
        <template #default="{ row }">
          <span :class="{ never: !row.lastReportAt }">{{ ago(row.lastReportAt) }}</span>
        </template>
      </el-table-column>

      <el-table-column label="">
        <template #default="{ row }">
          <el-button size="small" plain @click="open(row)">Report</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" width="420px" :title="current ? current.code : ''">
      <div v-if="current" class="dlg">
        <p class="sf-muted">Seat {{ current.seat }} · {{ pretty(current.state) }}</p>
        <p v-if="current.stale" class="warn">
          Last checked {{ current.daysSinceCheck }} days ago. Treat it as old.
        </p>
        <p class="sf-muted">
          Two different students have to report the same thing within 24 hours before the state changes.
          You can report each socket once a day.
        </p>
        <div v-if="current.myReportsToday === 0" class="actions">
          <el-button type="success" plain @click="report('WORKING')">It works</el-button>
          <el-button type="warning" plain @click="report('LOOSE')">Loose</el-button>
          <el-button type="danger" plain @click="report('NO_POWER')">No power</el-button>
        </div>
        <p v-else class="sf-muted">You already reported this socket today. Thanks.</p>
        <el-alert v-if="msg" :title="msg" :type="msgType" :closable="false" show-icon class="alert" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { errorText } from '../api'

const route = useRoute()
const room = ref({ seats: [] })
const rows = ref([])
const loading = ref(true)
const dialog = ref(false)
const current = ref(null)
const msg = ref('')
const msgType = ref('success')
const filter = ref('all')

const WORDS = { WORKING: 'Works', LOOSE: 'Loose', NO_POWER: 'No power', BROKEN: 'Broken', REPAIRED: 'Repaired', UNKNOWN: 'Not checked' }
const pretty = (s) => WORDS[s] || s
const FAULTY = ['LOOSE', 'NO_POWER', 'BROKEN']

const counts = computed(() => {
  const c = { noPower: 0, loose: 0, working: 0, unknown: 0, stale: 0 }
  for (const r of rows.value) {
    if (r.state === 'NO_POWER') c.noPower++
    if (r.state === 'LOOSE') c.loose++
    if (r.state === 'WORKING') c.working++
    if (r.state === 'UNKNOWN') c.unknown++
    if (r.stale) c.stale++
  }
  return c
})

const shown = computed(() => {
  if (filter.value === 'faulty') return rows.value.filter((r) => FAULTY.includes(r.state))
  if (filter.value === 'old') return rows.value.filter((r) => r.stale)
  return rows.value
})

function ago(t) {
  if (!t) return 'never'
  const mins = Math.round((Date.now() - new Date(t).getTime()) / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return mins + ' min ago'
  const hours = Math.round(mins / 60)
  if (hours < 24) return hours + ' h ago'
  const days = Math.round(hours / 24)
  return days === 1 ? 'yesterday' : days + ' days ago'
}

async function load() {
  const { data } = await api.get('/rooms/' + route.params.id)
  room.value = data
  rows.value = (data.seats || [])
    .flatMap((seat) => (seat.sockets || []).map((s) => ({ ...s, seat: seat.label })))
    .sort((a, b) => a.code.localeCompare(b.code))
}

function open(row) {
  current.value = row
  msg.value = ''
  dialog.value = true
}

async function report(state) {
  try {
    const { data } = await api.post('/sockets/' + current.value.id + '/report', { state })
    msgType.value = data.flipped ? 'success' : 'info'
    msg.value = data.message
    await load()
    current.value = rows.value.find((r) => r.id === current.value.id) || current.value
  } catch (e) {
    msgType.value = 'error'
    msg.value = errorText(e)
  }
}

onMounted(async () => {
  try {
    await load()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.top { margin-bottom: 14px; }
.title { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-top: 4px; }
h2 { margin: 2px 0 2px; font-size: 20px; letter-spacing: -.3px; }
.summary { display: flex; flex-wrap: wrap; gap: 14px; font-size: 12.5px; margin-bottom: 12px; }
.stat { color: var(--sf-muted); }
.stat b { font-size: 13.5px; margin-right: 2px; }
.c-red b, .c-red { color: #b42318; }
.c-amber b, .c-amber { color: #b54708; }
.c-green b, .c-green { color: #027a48; }
.c-grey b, .c-grey { color: #475467; }
.bar { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.hint { font-size: 12px; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px; }
.state { display: inline-flex; align-items: center; gap: 7px; font-size: 13px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #98a2b3; display: inline-block; }
.s-working .dot { background: #12b76a; }
.s-loose .dot { background: #f79009; }
.s-no_power .dot { background: #f04438; }
.s-broken .dot { background: #f04438; }
.s-repaired .dot { background: #444ce7; }
.old { color: #b54708; }
.old-tag { margin-left: 6px; }
.never { color: #b54708; }
.warn { color: #b54708; font-size: 13px; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.alert { margin-top: 12px; }
</style>
