<template>
  <transition name="m-sheet">
    <div v-if="open && socket" class="m-sheet-host">
      <div class="m-scrim" @click="$emit('close')"></div>

      <section class="m-sheet" role="dialog" aria-modal="true" :aria-label="socket.code">
        <div class="m-sheet-grab"></div>

        <div class="m-sheet-h">
          <div>
            <div class="m-sheet-code m-mono">{{ socket.code }}</div>
            <p class="m-sub">{{ t('room.dialogSeat', { seat: socket.seat, state: stateLabel(socket.state) }) }}</p>
          </div>
          <button class="m-icon-btn" type="button" :aria-label="t('mob.close')" @click="$emit('close')">
            <MobileIcon name="close" :size="18" />
          </button>
        </div>

        <div class="m-chips">
          <span class="m-chip">
            <i class="m-dot" :style="{ background: dotColor(socket.state) }"></i>
            {{ stateLabel(socket.state) }}
          </span>
          <span class="m-chip">{{ timeAgo(socket.lastCheckedAt, 'time.neverChecked') }}</span>
          <span v-if="socket.stale" class="m-chip">{{ t('room.oldTag') }}</span>
        </div>

        <p v-if="socket.stale" class="m-warn">{{ t('room.dialogStale', { n: socket.daysSinceCheck }) }}</p>

        <template v-if="socket.myReportsToday === 0">
          <p class="m-sheet-q">{{ t('mob.sheetPick') }}</p>
          <div class="m-state-picks">
            <button
              v-for="option in OPTIONS"
              :key="option.state"
              type="button"
              class="m-state-pick"
              :disabled="!!busy"
              @click="report(option.state)"
            >
              <i class="m-dot" :style="{ background: dotColor(option.state) }"></i>
              {{ t(option.label) }}
              <span v-if="busy === option.state" class="m-spin m-check"></span>
            </button>
          </div>
        </template>

        <p v-else class="m-note">{{ t('room.alreadyReported') }}</p>

        <p v-if="msg" class="m-flash" :class="msgType">{{ msg }}</p>
        <p class="m-fine">{{ t('room.dialogRule') }}</p>
      </section>
    </div>
  </transition>
</template>

<script setup>
/**
 * Bottom sheet for one socket: its state, and the three first-hand reports a
 * person can make. The POST goes through the shared api module, and the room
 * behind the sheet is refreshed by the parent through `updated`.
 */
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api, { errorText } from '../api'
import { stateLabel, timeAgo } from '../i18n'
import MobileIcon from './MobileIcon.vue'
import { dotColor } from './socketState.js'

const props = defineProps({
  socket: { type: Object, default: null },
  open: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'updated'])

const { t } = useI18n()

const OPTIONS = [
  { state: 'WORKING', label: 'room.actWorks' },
  { state: 'LOOSE', label: 'room.actLoose' },
  { state: 'NO_POWER', label: 'room.actNoPower' }
]

const busy = ref('')
const msg = ref('')
const msgType = ref('info')

watch(
  () => props.socket && props.socket.id,
  () => {
    msg.value = ''
    msgType.value = 'info'
  }
)

async function report(state) {
  if (!props.socket || busy.value) return
  busy.value = state
  msg.value = ''
  try {
    const { data } = await api.post('/sockets/' + props.socket.id + '/report', { state })
    const next = (data.socket && data.socket.state) || props.socket.state
    msgType.value = data.flipped ? 'good' : 'info'
    msg.value = t(data.flipped ? 'room.sentFlipped' : 'room.sentPending', { state: stateLabel(next) })
    emit('updated')
  } catch (e) {
    msgType.value = 'bad'
    msg.value = errorText(e)
  } finally {
    busy.value = ''
  }
}
</script>
