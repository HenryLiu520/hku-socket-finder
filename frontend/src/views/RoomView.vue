<template>
  <div v-loading="loading">
    <div class="top">
      <el-button link @click="$router.push('/')">← All rooms</el-button>
      <div>
        <h2>{{ room.code }} · {{ room.name }}</h2>
        <p class="sf-muted">{{ room.buildingName }} · {{ room.level }} · {{ rows.length }} sockets</p>
      </div>
    </div>

    <el-table :data="rows" class="sf-card" empty-text="No sockets entered for this room yet">
      <el-table-column label="Socket" width="200">
        <template #default="{ row }"><code>{{ row.code }}</code></template>
      </el-table-column>

      <el-table-column label="Seat" prop="seat" width="80" />

      <el-table-column label="State" width="150">
        <template #default="{ row }">
          <span class="state" :class="'s-' + row.state.toLowerCase()">
            <i class="dot"></i>{{ pretty(row.state) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column label="Updated" width="180">
        <template #default="{ row }">
          <span :class="{ old: row.stale }">{{ fmt(row.lastCheckedAt) }}</span>
          <el-tag v-if="row.stale" type="warning" size="small" effect="plain" class="old-tag">old</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Latest report" width="180">
        <template #default="{ row }">{{ fmt(row.lastReportAt) }}</template>
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
import { onMounted, ref } from 'vue'
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

const WORDS = {
  WORKING: 'Works',
  LOOSE: 'Loose',
  NO_POWER: 'No power',
  BROKEN: 'Broken',
  REPAIRED: 'Repaired',
  UNKNOWN: 'Not checked'
}

const pretty = (s) => WORDS[s] || s

function fmt(t) {
  if (!t) return '—'
  const d = new Date(t)
  return d.toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

async function load() {
  const { data } = await api.get('/rooms/' + route.params.id)
  room.value = data
  rows.value = (data.seats || []).flatMap((seat) =>
    (seat.sockets || []).map((s) => ({ ...s, seat: seat.label }))
  )
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
.top { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
h2 { margin: 2px 0 2px; font-size: 20px; letter-spacing: -.3px; }
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
.warn { color: #b54708; font-size: 13px; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.alert { margin-top: 12px; }
</style>
