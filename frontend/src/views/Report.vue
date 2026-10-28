<template>
  <div class="report">
    <div class="head">
      <h2>Report a fault</h2>
      <p class="sf-muted">
        Pick the room, tap the socket. The number is on the sticker; typing it works too.
      </p>
    </div>

    <div class="sf-card form">
      <div class="step">
        <label><b>1</b> Building</label>
        <el-select v-model="buildingId" placeholder="Choose a building" filterable class="wide" @change="onBuilding">
          <el-option v-for="b in buildings" :key="b.id" :label="b.code + ' · ' + b.name" :value="b.id" />
        </el-select>
      </div>

      <div class="step">
        <label><b>2</b> Room</label>
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

      <div class="step">
        <label><b>3</b> Socket <span class="sf-muted small">— tap one, or type the number</span></label>

        <div v-if="socketOptions.length" class="chips">
          <button
            v-for="s in socketOptions"
            :key="s.code"
            class="chip"
            :class="['st-' + s.state.toLowerCase(), { on: s.code === socketCode }]"
            @click="pick(s)"
          >
            <b>{{ tail(s.code) }}</b>
            <span>{{ word(s.state) }}</span>
          </button>
        </div>

        <el-input
          v-model="socketCode"
          :disabled="!roomId"
          :placeholder="roomId ? 'CW-L1-B-0001' : 'Pick a room first'"
          class="wide typed"
        />

        <p v-if="socketCode && !matched" class="line bad">
          No socket with that number in {{ currentRoom ? currentRoom.code : 'this room' }}.
          Check the sticker, or tap one above.
        </p>
        <p v-else-if="matched" class="line good">
          {{ matched.code }} · seat {{ matched.seat }} · now {{ word(matched.state) }}
        </p>
      </div>

      <div class="step">
        <label><b>4</b> What is wrong with it?</label>
        <div class="states">
          <button class="pick-state" :class="{ on: state === 'WORKING' }" :disabled="!matched" @click="state = 'WORKING'">
            <i class="dot d-green"></i> It works
          </button>
          <button class="pick-state" :class="{ on: state === 'LOOSE' }" :disabled="!matched" @click="state = 'LOOSE'">
            <i class="dot d-amber"></i> Loose
          </button>
          <button class="pick-state" :class="{ on: state === 'NO_POWER' }" :disabled="!matched" @click="state = 'NO_POWER'">
            <i class="dot d-red"></i> No power
          </button>
        </div>
      </div>

      <el-alert v-if="msg" :title="msg" :type="msgType" :closable="false" show-icon class="alert" />

      <div class="actions">
        <el-button type="primary" size="large" :disabled="!canSubmit" :loading="busy" @click="submit">
          Send report
        </el-button>
        <span class="sf-muted hint">One report per socket per day, ten a day in total.</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { errorText } from '../api'

const route = useRoute()

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

const WORDS = { WORKING: 'works', LOOSE: 'loose', NO_POWER: 'no power', BROKEN: 'broken', REPAIRED: 'repaired', UNKNOWN: 'not checked' }
const word = (s) => WORDS[s] || s
const tail = (code) => (code ? code.split('-').pop() : '')

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
  const preset = route.query.socket
  if (preset && socketOptions.value.some((s) => s.code === preset)) socketCode.value = String(preset)
}

function pick(s) {
  socketCode.value = s.code
  state.value = ''
  msg.value = ''
}

async function submit() {
  if (!canSubmit.value) return
  busy.value = true
  msg.value = ''
  try {
    const { data } = await api.post('/sockets/' + matched.value.id + '/report', { state: state.value })
    msgType.value = data.flipped ? 'success' : 'info'
    msg.value = data.message
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

onMounted(async () => {
  const { data } = await api.get('/buildings')
  buildings.value = data

  const presetRoom = route.query.room
  if (presetRoom) {
    const { data: r } = await api.get('/rooms/' + presetRoom)
    const b = buildings.value.find((x) => x.code === r.buildingCode)
    if (b) {
      buildingId.value = b.id
      await onBuilding()
      roomId.value = Number(presetRoom)
      await onRoom()
    }
  }
})
</script>

<style scoped>
.head { margin-bottom: 16px; }
.head h2 { margin: 0 0 4px; font-size: 20px; letter-spacing: -.3px; }
.form { padding: 22px; max-width: 640px; display: flex; flex-direction: column; gap: 18px; }
.step { display: flex; flex-direction: column; gap: 8px; }
.step > label { font-size: 12.5px; font-weight: 600; color: var(--sf-muted); }
.step > label b { display: inline-block; width: 16px; height: 16px; line-height: 16px; text-align: center; border-radius: 50%; background: #eef6f2; color: #0b6b4f; font-size: 10.5px; margin-right: 6px; }
.small { font-weight: 400; }
.wide { width: 100%; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { display: flex; flex-direction: column; align-items: flex-start; gap: 1px; padding: 6px 10px; border-radius: 8px; border: 1px solid var(--sf-line); background: #fff; cursor: pointer; font: inherit; transition: .12s; }
.chip b { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px; }
.chip span { font-size: 10.5px; color: var(--sf-muted); }
.chip:hover { border-color: #c3d2cb; }
.chip.on { border-color: #0b6b4f; box-shadow: 0 0 0 2px rgba(11,107,79,.12); }
.st-working { border-left: 3px solid #12b76a; }
.st-loose { border-left: 3px solid #f79009; }
.st-no_power { border-left: 3px solid #f04438; }
.st-repaired { border-left: 3px solid #444ce7; }
.st-unknown { border-left: 3px solid #98a2b3; }
.st-broken { border-left: 3px solid #f04438; }
.typed { margin-top: 2px; }
.states { display: flex; gap: 8px; flex-wrap: wrap; }
.pick-state { display: inline-flex; align-items: center; gap: 8px; padding: 9px 14px; border-radius: 9px; border: 1px solid var(--sf-line); background: #fff; font: inherit; font-size: 13px; cursor: pointer; transition: .12s; }
.pick-state:hover:not(:disabled) { border-color: #c3d2cb; }
.pick-state.on { border-color: #0b6b4f; box-shadow: 0 0 0 2px rgba(11,107,79,.12); font-weight: 600; }
.pick-state:disabled { opacity: .45; cursor: not-allowed; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.d-green { background: #12b76a; }
.d-amber { background: #f79009; }
.d-red { background: #f04438; }
.line { margin: 0; font-size: 12.5px; }
.bad { color: #b42318; }
.good { color: #0b6b4f; }
.actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hint { font-size: 12px; }
.alert { margin-top: 2px; }
</style>
