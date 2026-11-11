<template>
  <div class="m-page">
    <div class="m-lead">
      <h1 class="m-h1">{{ t('report.title') }}</h1>
      <p class="m-sub">{{ t('report.intro') }}</p>
    </div>

    <div class="m-card m-form-card">
      <!-- 1 · building -->
      <div class="m-step">
        <span class="m-step-h"><b>1</b>{{ t('report.step1') }}</span>
        <div class="m-seg">
          <button
            v-for="b in buildings"
            :key="b.id"
            type="button"
            class="m-bseg"
            :class="{ on: b.id === buildingId }"
            :aria-pressed="b.id === buildingId"
            @click="chooseBuilding(b.id)"
          >
            <b>{{ b.code }}</b>
            <span>{{ b.name }}</span>
          </button>
        </div>
      </div>

      <!-- 2 · room -->
      <div class="m-step">
        <span class="m-step-h"><b>2</b>{{ t('report.step2') }}</span>
        <p v-if="!buildingId" class="m-fine">{{ t('report.roomPlaceholderNoBuilding') }}</p>
        <template v-else>
          <p v-if="!rooms.length" class="m-fine">{{ t('home.noRooms') }}</p>
          <div v-else class="m-pick-list">
            <button
              v-for="r in rooms"
              :key="r.id"
              type="button"
              class="m-pick"
              :class="{ on: r.id === roomId }"
              :aria-pressed="r.id === roomId"
              @click="chooseRoom(r.id)"
            >
              <b>{{ r.code }}</b>
              <span>{{ r.name }}</span>
              <span class="m-pick-lvl">{{ r.level }}</span>
            </button>
          </div>
        </template>
      </div>

      <!-- 3 · socket -->
      <div class="m-step">
        <span class="m-step-h">
          <b>3</b>{{ t('report.step3') }}<em class="m-fine">{{ t('report.step3hint') }}</em>
        </span>
        <p v-if="!roomId" class="m-fine">{{ t('report.socketPlaceholderNoRoom') }}</p>
        <template v-else>
          <p v-if="!sockets.length" class="m-fine">{{ t('mob.noSockets') }}</p>
          <div v-else class="m-pick-grid">
            <button
              v-for="s in sockets"
              :key="s.id"
              type="button"
              class="m-sock-pick"
              :class="{ on: s.id === pickId }"
              :aria-pressed="s.id === pickId"
              :title="s.code"
              @click="pick(s)"
            >
              <i class="m-dot" :style="{ background: dotColor(s.state) }"></i>
              <span class="m-mono">{{ tail(s.code) }}</span>
            </button>
          </div>

          <input
            class="m-input m-mono"
            type="text"
            inputmode="text"
            autocapitalize="characters"
            autocomplete="off"
            :value="typed"
            :placeholder="t('report.socketPlaceholder')"
            :aria-label="t('report.step3')"
            @input="onType"
          />

          <p v-if="typed && !selected" class="m-bad">
            {{ t('report.notFound', { room: currentRoom ? currentRoom.code : '—' }) }}
          </p>
          <p v-else-if="selected" class="m-good">
            {{ t('report.summary', { code: selected.code, seat: selected.seat, state: stateLabel(selected.state) }) }}
          </p>
        </template>
      </div>

      <!-- 4 · what is wrong -->
      <div class="m-step">
        <span class="m-step-h"><b>4</b>{{ t('report.step4') }}</span>
        <div class="m-state-picks">
          <button
            v-for="option in OPTIONS"
            :key="option.state"
            type="button"
            class="m-state-pick"
            :class="{ on: state === option.state }"
            :disabled="!selected"
            :aria-pressed="state === option.state"
            @click="state = option.state"
          >
            <i class="m-dot" :style="{ background: dotColor(option.state) }"></i>
            {{ t(option.label) }}
            <MobileIcon v-if="state === option.state" name="check" :size="17" class="m-check" />
          </button>
        </div>
        <p v-if="!selected" class="m-fine">{{ t('mob.pickStateFirst') }}</p>
      </div>
    </div>

    <p v-if="msg" class="m-flash" :class="msgType">{{ msg }}</p>

    <div class="m-sticky">
      <button class="m-btn m-btn-primary" type="button" :disabled="!canSubmit" @click="submit">
        <span v-if="busy" class="m-spin"></span>
        {{ t('report.submit') }}
      </button>
      <span class="m-fine m-center">{{ t('report.quota') }}</span>
    </div>
  </div>
</template>

<script setup>
/**
 * Tab three: the four-field report — building, room, socket, fault. The socket
 * can be tapped from a colour-coded grid or typed (full code, or just the four
 * digits from the sticker). The send button is pinned to the bottom of the screen
 * so the last thing a person taps never scrolls away.
 */
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import api, { errorText } from '../../api'
import { stateLabel } from '../../i18n'
import MobileIcon from '../MobileIcon.vue'
import { dotColor, socketRows, tail } from '../socketState.js'

const { t } = useI18n()
const route = useRoute()

const OPTIONS = [
  { state: 'WORKING', label: 'room.actWorks' },
  { state: 'LOOSE', label: 'room.actLoose' },
  { state: 'NO_POWER', label: 'room.actNoPower' }
]

const buildings = ref([])
const rooms = ref([])
const sockets = ref([])

const buildingId = ref(null)
const roomId = ref(null)
const pickId = ref(null)
const typed = ref('')
const state = ref('')

const busy = ref(false)
const msg = ref('')
const msgType = ref('info')

const currentRoom = computed(() => rooms.value.find((r) => r.id === roomId.value) || null)
const selected = computed(() => sockets.value.find((s) => s.id === pickId.value) || null)
const canSubmit = computed(() => !!selected.value && !!state.value && !busy.value)

function reset() {
  pickId.value = null
  typed.value = ''
  state.value = ''
  msg.value = ''
}

async function loadRooms(id) {
  rooms.value = []
  const { data } = await api.get('/buildings/' + id + '/rooms')
  rooms.value = data
}

function applyRoom(data) {
  sockets.value = socketRows(data)
  reset()
}

async function chooseBuilding(id) {
  if (id === buildingId.value) return
  buildingId.value = id
  roomId.value = null
  sockets.value = []
  reset()
  await loadRooms(id)
}

async function chooseRoom(id) {
  if (id === roomId.value) return
  roomId.value = id
  sockets.value = []
  reset()
  const { data } = await api.get('/rooms/' + id)
  applyRoom(data)
}

function matchCode(value) {
  const q = String(value || '').trim().toUpperCase()
  if (!q) return null
  return (
    sockets.value.find((s) => String(s.code).toUpperCase() === q) ||
    sockets.value.find((s) => tail(s.code) === q) ||
    (q.length >= 3 ? sockets.value.find((s) => String(s.code).toUpperCase().endsWith(q)) : null) ||
    null
  )
}

function onType(e) {
  typed.value = e.target.value
  const hit = matchCode(typed.value)
  pickId.value = hit ? hit.id : null
}

function pick(socket) {
  pickId.value = socket.id
  typed.value = socket.code
  state.value = ''
  msg.value = ''
}

async function submit() {
  if (!canSubmit.value) return
  busy.value = true
  msg.value = ''
  try {
    const { data } = await api.post('/sockets/' + pickId.value + '/report', { state: state.value })
    const next = (data.socket && data.socket.state) || state.value
    msgType.value = data.flipped ? 'good' : 'info'
    msg.value = t(data.flipped ? 'report.sentFlipped' : 'report.sentPending', { state: stateLabel(next) })
    const row = sockets.value.find((s) => s.id === pickId.value)
    if (row) row.state = next
    state.value = ''
  } catch (e) {
    msgType.value = 'bad'
    msg.value = errorText(e)
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/buildings')
    buildings.value = data

    const presetRoom = Number(route.query.room)
    if (!presetRoom) return

    const { data: roomData } = await api.get('/rooms/' + presetRoom)
    const b = data.find((x) => x.code === roomData.buildingCode)
    if (!b) return

    buildingId.value = b.id
    await loadRooms(b.id)
    roomId.value = presetRoom
    applyRoom(roomData)

    const presetSocket = String(route.query.socket || '')
    if (presetSocket) {
      const hit = sockets.value.find((s) => s.code === presetSocket) || matchCode(presetSocket)
      if (hit) pick(hit)
    }
  } catch (e) {
    msgType.value = 'bad'
    msg.value = errorText(e)
  }
})
</script>
