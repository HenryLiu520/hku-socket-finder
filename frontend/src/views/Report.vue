<template>
  <div class="report">
    <div class="head">
      <h2>Report a fault</h2>
      <p class="sf-muted">
        Three steps, and the socket number does the work: pick the building, the room list narrows,
        pick the room, the socket list narrows to that room.
      </p>
    </div>

    <div class="sf-card form">
      <div class="field">
        <label>1 · Building</label>
        <el-select
          v-model="buildingId"
          placeholder="Choose a building"
          filterable
          class="wide"
          @change="onBuilding"
        >
          <el-option v-for="b in buildings" :key="b.id" :label="b.code + ' · ' + b.name" :value="b.id" />
        </el-select>
      </div>

      <div class="field">
        <label>2 · Room</label>
        <el-select
          v-model="roomId"
          :placeholder="buildingId ? 'Choose a room' : 'Pick a building first'"
          filterable
          class="wide"
          :disabled="!buildingId"
          @change="onRoom"
        >
          <el-option
            v-for="r in rooms"
            :key="r.id"
            :label="r.code + ' · ' + r.name + ' (' + r.level + ')'"
            :value="r.id"
          />
        </el-select>
      </div>

      <div class="field">
        <label>3 · Socket number</label>
        <el-select
          v-model="socketCode"
          :placeholder="roomId ? 'Pick one, or type the number from the sticker' : 'Pick a room first'"
          filterable
          allow-create
          default-first-option
          class="wide"
          :disabled="!roomId"
          @change="checkCode"
        >
          <el-option
            v-for="s in socketOptions"
            :key="s.code"
            :label="s.code + '  ·  seat ' + s.seat"
            :value="s.code"
          />
        </el-select>
        <p v-if="socketCode && !matched" class="line bad">
          No socket with that number in {{ currentRoom ? currentRoom.code : 'this room' }}.
          Type it again from the sticker, or pick from the list.
        </p>
        <p v-else-if="matched" class="line good">
          {{ matched.code }} · seat {{ matched.seat }} · now
          {{ stateLabel(matched.state) }}
        </p>
      </div>

      <div class="field">
        <label>4 · What is wrong with it?</label>
        <el-radio-group v-model="state" :disabled="!matched" class="wide">
          <el-radio-button value="WORKING">It works</el-radio-button>
          <el-radio-button value="LOOSE">Loose</el-radio-button>
          <el-radio-button value="NO_POWER">No power</el-radio-button>
        </el-radio-group>
      </div>

      <el-alert v-if="msg" :title="msg" :type="msgType" :closable="false" show-icon class="alert" />

      <div class="actions">
        <el-button type="primary" size="large" :disabled="!canSubmit" :loading="busy" @click="submit">
          Send report
        </el-button>
        <span class="sf-muted hint">
          One report per socket per day, ten a day in total.
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { errorText } from '../api'

const route = useRoute()
const router = useRouter()

const buildings = ref([])
const rooms = ref([])
const socketOptions = ref([])

const buildingId = ref(null)
const roomId = ref(null)
const socketCode = ref('')
const state = ref('')
const busy = ref(false)
const msg = ref('')
const msgType = ref('success')

const matched = computed(() => socketOptions.value.find((s) => s.code === socketCode.value) || null)
const currentRoom = computed(() => rooms.value.find((r) => r.id === roomId.value) || null)
const canSubmit = computed(() => !!matched.value && !!state.value && !busy.value)

const label = (s) => ({ WORKING: 'works', LOOSE: 'loose', NO_POWER: 'no power', BROKEN: 'broken', REPAIRED: 'repaired', UNKNOWN: 'not checked' }[s] || s)
const stateLabel = (s) => label(s)

async function load() {
  const { data } = await api.get('/buildings')
  buildings.value = data
  // arriving with ?socket=... from a room page fills the chain for you
  const preset = route.query.socket
  if (preset) {
    socketCode.value = String(preset)
  }
}

async function onBuilding() {
  roomId.value = null
  rooms.value = []
  socketOptions.value = []
  socketCode.value = ''
  state.value = ''
  if (!buildingId.value) return
  const { data } = await api.get('/buildings/' + buildingId.value + '/rooms')
  rooms.value = data
}

async function onRoom() {
  socketOptions.value = []
  socketCode.value = ''
  state.value = ''
  if (!roomId.value) return
  const { data } = await api.get('/rooms/' + roomId.value)
  socketOptions.value = (data.seats || []).flatMap((seat) =>
    (seat.sockets || []).map((s) => ({ code: s.code, seat: seat.label, state: s.state, id: s.id }))
  )
  // a number handed in by the room page, if it belongs to this room
  const preset = route.query.socket
  if (preset && socketOptions.value.some((s) => s.code === preset)) socketCode.value = String(preset)
}

function checkCode() {
  state.value = ''
}

async function submit() {
  if (!canSubmit.value) return
  busy.value = true
  msg.value = ''
  try {
    const { data } = await api.post('/sockets/' + matched.value.id + '/report', { state: state.value })
    msgType.value = data.flipped ? 'success' : 'info'
    msg.value = data.message
    // refresh what this socket looks like now
    const fresh = socketOptions.value.find((s) => s.code === matched.value.code)
    if (fresh) fresh.state = data.socket.state
    state.value = ''
  } catch (e) {
    msgType.value = 'error'
    msg.value = errorText(e)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.head { margin-bottom: 16px; }
.head h2 { margin: 0 0 4px; font-size: 20px; }
.form { padding: 22px; max-width: 560px; display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 12.5px; font-weight: 600; color: var(--sf-muted); letter-spacing: .2px; }
.wide { width: 100%; }
.line { margin: 0; font-size: 12.5px; }
.bad { color: #c0392b; }
.good { color: #0b6b4f; }
.actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hint { font-size: 12px; }
.alert { margin-top: 4px; }
</style>
