<template>
  <div class="report">
    <div class="head">
      <h2>{{ t('report.title') }}</h2>
      <p class="sf-muted">{{ t('report.intro') }}</p>
    </div>

    <div class="sf-card form">
      <div class="step">
        <label><b>1</b> {{ t('report.step1') }}</label>
        <el-select v-model="buildingId" :placeholder="t('report.buildingPlaceholder')" filterable class="wide" @change="onBuilding">
          <el-option v-for="b in buildings" :key="b.id" :label="b.code + ' · ' + b.name" :value="b.id" />
        </el-select>
      </div>

      <div class="step">
        <label><b>2</b> {{ t('report.step2') }}</label>
        <el-select
          v-model="roomId"
          :placeholder="buildingId ? t('report.roomPlaceholder') : t('report.roomPlaceholderNoBuilding')"
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
        <label>
          <b>3</b> {{ t('report.step3') }}
          <span class="sf-muted small">{{ t('report.step3hint') }}</span>
        </label>

        <RoomMap v-if="roomSeats.length" flat :seats="roomSeats" @pick="pick" />

        <el-input
          v-model="socketCode"
          :disabled="!roomId"
          :placeholder="roomId ? t('report.socketPlaceholder') : t('report.socketPlaceholderNoRoom')"
          class="wide typed"
        />

        <p v-if="socketCode && !matched" class="line bad">
          {{ t('report.notFound', { room: currentRoom ? currentRoom.code : '—' }) }}
        </p>
        <p v-else-if="matched" class="line good">
          {{ t('report.summary', { code: matched.code, seat: matched.seat, state: stateLabel(matched.state) }) }}
        </p>
      </div>

      <div class="step">
        <label><b>4</b> {{ t('report.step4') }}</label>
        <div class="states">
          <button class="pick-state" :class="{ on: state === 'WORKING' }" :disabled="!matched" @click="state = 'WORKING'">
            <i class="dot d-green"></i> {{ t('room.actWorks') }}
          </button>
          <button class="pick-state" :class="{ on: state === 'LOOSE' }" :disabled="!matched" @click="state = 'LOOSE'">
            <i class="dot d-amber"></i> {{ t('room.actLoose') }}
          </button>
          <button class="pick-state" :class="{ on: state === 'NO_POWER' }" :disabled="!matched" @click="state = 'NO_POWER'">
            <i class="dot d-red"></i> {{ t('room.actNoPower') }}
          </button>
        </div>
      </div>

      <el-alert v-if="msg" :title="msg" :type="msgType" :closable="false" show-icon class="alert" />

      <div class="actions">
        <el-button type="primary" size="large" :disabled="!canSubmit" :loading="busy" @click="submit">
          {{ t('report.submit') }}
        </el-button>
        <span class="sf-muted hint">{{ t('report.quota') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import api, { errorText } from '../api'
import { stateLabel } from '../i18n'
import RoomMap from '../components/RoomMap.vue'

const { t } = useI18n()
const route = useRoute()

const buildings = ref([])
const rooms = ref([])
const socketOptions = ref([])
const roomSeats = ref([])

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
  roomSeats.value = []
  socketCode.value = ''
  state.value = ''
  if (!roomId.value) return
  const { data } = await api.get('/rooms/' + roomId.value)
  roomSeats.value = data.seats || []
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
    const nextState = (data.socket && data.socket.state) || state.value
    msg.value = t(data.flipped ? 'report.sentFlipped' : 'report.sentPending', { state: stateLabel(nextState) })
    const fresh = socketOptions.value.find((s) => s.code === matched.value.code)
    if (fresh) fresh.state = nextState
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
.head { margin-bottom: 18px; }
.head h2 { margin: 0 0 5px; font-size: 22px; letter-spacing: -.4px; }
.head .sf-muted { margin: 0; max-width: 60ch; line-height: 1.55; }
.form { padding: 24px; max-width: 640px; display: flex; flex-direction: column; gap: 20px; }
.step { display: flex; flex-direction: column; gap: 8px; }
.step > label { font-size: 12.5px; font-weight: 650; color: var(--sf-muted); letter-spacing: .02em; }
.step > label b {
  display: inline-block; width: 17px; height: 17px; line-height: 17px; text-align: center;
  border-radius: 50%; background: var(--sf-green-soft); color: var(--sf-green);
  font-size: 10.5px; margin-right: 6px; box-shadow: inset 0 0 0 1px var(--sf-green-line);
}
.small { font-weight: 400; }
.wide { width: 100%; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { display: flex; flex-direction: column; align-items: flex-start; gap: 1px; padding: 6px 10px; border-radius: 8px; border: 1px solid var(--sf-line); background: #fff; cursor: pointer; font: inherit; transition: .12s; }
.chip b { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px; }
.chip span { font-size: 10.5px; color: var(--sf-muted); }
.chip:hover { border-color: var(--sf-green-line); }
.chip.on { border-color: var(--sf-green); box-shadow: 0 0 0 2px rgba(2, 70, 56, .12); }
.typed { margin-top: 2px; }
.states { display: flex; gap: 8px; flex-wrap: wrap; }
.pick-state {
  display: inline-flex; align-items: center; gap: 8px; padding: 10px 15px;
  border-radius: 10px; border: 1px solid var(--sf-line); background: #fff;
  font: inherit; font-size: 13px; cursor: pointer; transition: .13s;
  box-shadow: 0 1px 2px rgba(16, 40, 34, .04);
}
.pick-state:hover:not(:disabled) { border-color: var(--sf-green-line); box-shadow: var(--sf-shadow); }
.pick-state.on { border-color: var(--sf-green); box-shadow: 0 0 0 2px rgba(2, 70, 56, .12); font-weight: 650; color: var(--sf-green); }
.pick-state:disabled { opacity: .45; cursor: not-allowed; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.d-green { background: #12b76a; }
.d-amber { background: #f79009; }
.d-red { background: #f04438; }
.line { margin: 0; font-size: 12.5px; line-height: 1.55; }
.bad { color: #b42318; }
.good { color: var(--sf-green); }
.actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hint { font-size: 12px; }
.alert { margin-top: 2px; }
@media (max-width: 820px) {
  .form { padding: 18px; }
  .head h2 { font-size: 19px; }
}
</style>
