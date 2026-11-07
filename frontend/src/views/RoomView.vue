<template>
  <div v-loading="loading">
    <div class="top">
      <el-button link @click="$router.push('/')">{{ t('room.back') }}</el-button>
      <div class="title">
        <div>
          <h2>{{ room.code }} · {{ room.name }}</h2>
          <p class="sf-muted">{{ room.buildingName }} · {{ room.level }}</p>
        </div>
        <el-button type="primary" plain @click="$router.push({ path: '/report', query: { room: room.id } })">
          {{ t('room.reportFault') }}
        </el-button>
      </div>
    </div>

    <div class="summary">
      <span class="stat total">{{ t('room.sockets', { n: rows.length }, rows.length) }}</span>
      <span v-if="counts.noPower" class="stat c-red"><b>{{ counts.noPower }}</b> {{ stateLabel('NO_POWER', true) }}</span>
      <span v-if="counts.loose" class="stat c-amber"><b>{{ counts.loose }}</b> {{ stateLabel('LOOSE', true) }}</span>
      <span v-if="counts.working" class="stat c-green"><b>{{ counts.working }}</b> {{ stateLabel('WORKING', true) }}</span>
      <span v-if="counts.unknown" class="stat c-grey"><b>{{ counts.unknown }}</b> {{ stateLabel('UNKNOWN', true) }}</span>
      <span v-if="counts.stale" class="stat c-amber"><b>{{ counts.stale }}</b> {{ t('common.old') }}</span>
    </div>

    <RoomMap :seats="room.seats" @pick="open" />

    <div class="bar">
      <el-radio-group v-model="filter" size="small">
        <el-radio-button value="all">{{ t('room.filterAll') }}</el-radio-button>
        <el-radio-button value="faulty">{{ t('room.filterFaulty') }}</el-radio-button>
        <el-radio-button value="old">{{ t('room.filterOld') }}</el-radio-button>
      </el-radio-group>
      <span class="sf-muted hint">{{ t('room.shown', { n: shown.length }) }}</span>
    </div>

    <div class="table-wrap sf-card">
    <el-table :data="shown" style="width: 100%" :empty-text="t('room.empty')">
      <el-table-column :label="t('room.colSocket')" min-width="150">
        <template #default="{ row }"><code>{{ row.code }}</code></template>
      </el-table-column>

      <el-table-column :label="t('room.colSeat')" prop="seat" width="58" />

      <el-table-column :label="t('room.colState')" min-width="118">
        <template #default="{ row }">
          <span class="state" :class="'s-' + row.state.toLowerCase()">
            <i class="dot"></i>{{ stateLabel(row.state) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column :label="t('room.colLastChanged')" min-width="130">
        <template #default="{ row }">
          <span :class="{ old: row.stale }">{{ timeAgo(row.lastCheckedAt) }}</span>
          <el-tag v-if="row.stale" type="warning" size="small" effect="plain" class="old-tag">{{ t('room.oldTag') }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column :label="t('room.colLastReport')" min-width="128">
        <template #default="{ row }">
          <span :class="{ never: !row.lastReportAt }">{{ timeAgo(row.lastReportAt) }}</span>
        </template>
      </el-table-column>

      <el-table-column :label="''" width="92" align="right">
        <template #default="{ row }">
          <el-button size="small" plain @click="open(row)">{{ t('room.colAction') }}</el-button>
        </template>
      </el-table-column>
    </el-table>
    </div>

    <el-dialog v-model="dialog" width="440px" :title="current ? current.code : ''">
      <div v-if="current" class="dlg">
        <p class="sf-muted">{{ t('room.dialogSeat', { seat: current.seat, state: stateLabel(current.state) }) }}</p>
        <p v-if="current.stale" class="warn">
          {{ t('room.dialogStale', { n: current.daysSinceCheck }) }}
        </p>
        <p class="sf-muted">{{ t('room.dialogRule') }}</p>
        <div v-if="current.myReportsToday === 0" class="actions">
          <el-button type="success" plain @click="report('WORKING')">{{ t('room.actWorks') }}</el-button>
          <el-button type="warning" plain @click="report('LOOSE')">{{ t('room.actLoose') }}</el-button>
          <el-button type="danger" plain @click="report('NO_POWER')">{{ t('room.actNoPower') }}</el-button>
        </div>
        <p v-else class="sf-muted">{{ t('room.alreadyReported') }}</p>
        <el-alert v-if="msg" :title="msg" :type="msgType" :closable="false" show-icon class="alert" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import api, { errorText } from '../api'
import { stateLabel, timeAgo } from '../i18n'
import RoomMap from '../components/RoomMap.vue'

const { t } = useI18n()
const route = useRoute()
const room = ref({ seats: [] })
const rows = ref([])
const loading = ref(true)
const dialog = ref(false)
const current = ref(null)
const msg = ref('')
const msgType = ref('success')
const filter = ref('all')

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
    const nextState = (data.socket && data.socket.state) || current.value.state
    msg.value = t(data.flipped ? 'room.sentFlipped' : 'room.sentPending', { state: stateLabel(nextState) })
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
.top { margin-bottom: 16px; }
.title { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-top: 4px; flex-wrap: wrap; }
.title > div { min-width: 0; }
.title .el-button { flex: 0 0 auto; }
.table-wrap { width: 100%; max-width: 100%; min-width: 0; overflow-x: auto; border-radius: var(--sf-radius); }
.table-wrap :deep(.el-table) { border-radius: var(--sf-radius); }
h2 { margin: 2px 0 3px; font-size: 22px; letter-spacing: -.4px; }
.summary {
  display: flex; flex-wrap: wrap; gap: 8px 14px; font-size: 12.5px;
  margin-bottom: 14px; padding: 11px 15px;
  background: rgba(255, 255, 255, .78); border: 1px solid var(--sf-line);
  border-radius: var(--sf-radius-sm); box-shadow: 0 1px 2px rgba(16, 40, 34, .04);
}
.stat { color: var(--sf-muted); }
.stat.total { color: var(--sf-ink); font-weight: 650; }
.stat b { font-size: 13.5px; margin-right: 3px; font-weight: 700; }
.c-red b, .c-red { color: #b42318; }
.c-amber b, .c-amber { color: #b54708; }
.c-green b, .c-green { color: #027a48; }
.c-grey b, .c-grey { color: #475467; }
.bar { display: flex; align-items: center; gap: 12px; margin-bottom: 11px; flex-wrap: wrap; }
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
.dlg p { line-height: 1.6; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.alert { margin-top: 12px; }
@media (max-width: 820px) {
  h2 { font-size: 19px; }
}
</style>
