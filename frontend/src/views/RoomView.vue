<template>
  <div v-loading="loading">
    <div class="top">
      <el-button link @click="$router.push('/')">← All rooms</el-button>
      <h2>{{ room.code }} · {{ room.name }}</h2>
      <p class="sf-muted">{{ room.buildingName }} · {{ room.level }} · tap a socket to report it</p>
    </div>

    <div class="floor">
      <div v-for="row in rows" :key="row.key" class="row">
        <div v-for="seat in row.seats" :key="seat.id" class="seat sf-card">
          <div class="seat-h">
            <span class="label">Seat {{ seat.label }}</span>
            <span v-if="!seat.sockets.length" class="sf-muted">no socket</span>
          </div>
          <div class="sockets">
            <button
              v-for="s in seat.sockets"
              :key="s.id"
              class="socket"
              :class="'st-' + s.state.toLowerCase()"
              @click="open(s, seat)"
            >
              <span class="ico">⏻{{ shortCode(s.code) }}</span>
              <span class="txt">{{ pretty(s.state) }}</span>
              <span class="age">{{ age(s) }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialog" width="420px" :title="'Seat ' + (current.seat ? current.seat.label : '')">
      <div v-if="current.socket" class="dlg">
        <p class="sf-muted code-line">Socket {{ current.socket.code }}</p>
        <div class="state-line">
          <el-tag :type="tagType(current.socket.state)" effect="light">{{ pretty(current.socket.state) }}</el-tag>
          <span class="sf-muted">{{ age(current.socket) }}</span>
        </div>
        <p v-if="current.socket.stale" class="warn">
          Last checked {{ current.socket.daysSinceCheck }} days ago. Treat it as old.
        </p>
        <p class="sf-muted">
          Two different students have to report the same thing within 24 hours before the state changes.
          You can report each socket once a day.
        </p>
        <div v-if="canReport" class="actions">
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
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { errorText } from '../api'
import { useAuth } from '../stores/auth'

const route = useRoute()
const auth = useAuth()
const room = ref({ seats: [] })
const loading = ref(true)
const dialog = ref(false)
const msg = ref('')
const msgType = ref('success')
const current = reactive({ socket: null, seat: null })

const shortCode = (code) => (code ? code.split('-').pop() : '')

const rows = computed(() => {
  const byY = {}
  for (const s of room.value.seats || []) {
    const k = s.y || 0
    ;(byY[k] = byY[k] || []).push(s)
  }
  return Object.keys(byY).sort().map((k) => ({
    key: k,
    seats: byY[k].sort((a, b) => (a.x || 0) - (b.x || 0))
  }))
})

const canReport = computed(() => current.socket && current.socket.myReportsToday === 0)

const WORDS = {
  WORKING: 'works',
  LOOSE: 'loose',
  NO_POWER: 'no power',
  BROKEN: 'broken',
  REPAIRED: 'repaired',
  UNKNOWN: 'not checked'
}

function pretty(state) {
  return WORDS[state] || state.toLowerCase()
}

function tagType(state) {
  return { WORKING: 'success', LOOSE: 'warning', NO_POWER: 'danger', BROKEN: 'danger', REPAIRED: 'info', UNKNOWN: 'info' }[state] || 'info'
}

function age(s) {
  if (!s.lastCheckedAt) return 'never checked'
  if (s.daysSinceCheck === 0) return 'checked today'
  return 'checked ' + s.daysSinceCheck + 'd ago'
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/rooms/' + route.params.id)
    room.value = data
  } finally {
    loading.value = false
  }
}

function open(socket, seat) {
  current.socket = socket
  current.seat = seat
  msg.value = ''
  dialog.value = true
}

async function report(state) {
  try {
    const { data } = await api.post('/sockets/' + current.socket.id + '/report', { state })
    current.socket = data.socket
    msg.value = data.message
    msgType.value = data.flipped ? 'success' : 'info'
    await load()
  } catch (e) {
    msg.value = errorText(e)
    msgType.value = 'error'
  }
}

onMounted(load)
</script>

<style scoped>
.top { margin-bottom: 18px; }
h2 { margin: 6px 0 4px; font-size: 20px; letter-spacing: -.3px; }
.floor { display: grid; gap: 14px; }
.row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.seat { padding: 12px 12px 14px; }
.seat-h { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.label { font-size: 12px; color: var(--sf-muted); font-weight: 600; letter-spacing: .02em; }
.sockets { display: grid; gap: 8px; }
.socket { display: grid; grid-template-columns: 16px 1fr auto; align-items: center; gap: 8px;
  text-align: left; padding: 9px 10px; border-radius: 8px; border: 1px solid var(--sf-line);
  background: #fff; cursor: pointer; font: inherit; }
.socket:hover { border-color: #c3d2cb; }
.ico { font-size: 13px; }
.txt { font-size: 13px; font-weight: 600; }
.age { font-size: 11.5px; color: var(--sf-muted); }
.st-working { border-left: 3px solid #12b76a; }
.st-loose { border-left: 3px solid #f79009; }
.st-no_power { border-left: 3px solid #f04438; }
.st-broken { border-left: 3px solid #f04438; }
.st-repaired { border-left: 3px solid #444ce7; }
.st-unknown { border-left: 3px solid #98a2b3; }
.dlg { display: grid; gap: 10px; }
.state-line { display: flex; align-items: center; gap: 10px; }
.warn { color: #b54708; background: #fffaeb; border: 1px solid #fedf89; padding: 8px 10px; border-radius: 8px; font-size: 12.5px; margin: 0; }
.actions { display: flex; gap: 10px; margin-top: 4px; }
.alert { margin-top: 6px; }
</style>
