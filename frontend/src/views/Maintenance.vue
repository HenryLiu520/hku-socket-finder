<template>
  <div>
    <div class="head">
      <div>
        <h2>{{ t('maint.title') }}</h2>
        <p class="sf-muted">{{ t('maint.intro') }}</p>
      </div>
      <el-tag v-if="rows.length" type="danger" effect="plain">{{ t('maint.open', { n: rows.length }) }}</el-tag>
    </div>

    <div class="table-wrap sf-card">
      <el-table :data="rows" v-loading="loading" :empty-text="t('maint.empty')">
        <el-table-column prop="building" :label="t('maint.colBuilding')" width="86" />
        <el-table-column prop="roomCode" :label="t('maint.colRoom')" width="108" />
        <el-table-column prop="seat" :label="t('maint.colSeat')" width="64" />
        <el-table-column prop="code" :label="t('maint.colSocket')" width="140">
          <template #default="{ row }"><code>{{ row.code }}</code></template>
        </el-table-column>
        <el-table-column :label="t('maint.colFault')" width="112">
          <template #default="{ row }">
            <el-tag :type="row.state === 'NO_POWER' ? 'danger' : 'warning'" effect="plain" size="small">
              {{ stateLabel(row.state) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('maint.colBrokenFor')" width="106">
          <template #default="{ row }">
            <b :class="{ old: row.daysBroken >= 7 }">{{ t('maint.day', { n: row.daysBroken }, row.daysBroken) }}</b>
          </template>
        </el-table-column>
        <el-table-column :label="t('maint.colReportedBy')" width="106">
          <template #default="{ row }">{{ t('maint.student', { n: row.reporters }, row.reporters) }}</template>
        </el-table-column>
        <el-table-column :label="t('maint.colLastChecked')" width="154">
          <template #default="{ row }">{{ fmt(row.lastCheckedAt) }}</template>
        </el-table-column>
        <el-table-column :label="''" min-width="126" align="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openRepair(row)">{{ t('maint.markRepaired') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="t('maint.dialogTitle')" width="440px">
      <p class="sf-muted">{{ t('maint.dialogNote') }}</p>
      <el-input v-model="note" type="textarea" :rows="3" :placeholder="t('maint.notePlaceholder')" />
      <template #footer>
        <el-button @click="dialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="busy" @click="confirm">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api, { errorText } from '../api'
import { stateLabel } from '../i18n'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const rows = ref([])
const loading = ref(true)
const dialog = ref(false)
const busy = ref(false)
const note = ref('')
const target = ref(null)

function fmt(v) {
  if (!v) return '—'
  return v.replace('T', ' ').slice(0, 16)
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/maintenance/queue')
    rows.value = data
  } finally {
    loading.value = false
  }
}

function openRepair(row) {
  target.value = row
  note.value = ''
  dialog.value = true
}

async function confirm() {
  busy.value = true
  try {
    await api.post('/sockets/' + target.value.socketId + '/repair', { note: note.value })
    dialog.value = false
    ElMessage.success(t('maint.repaired'))
    await load()
  } catch (e) {
    ElMessage.error(errorText(e))
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 18px; gap: 14px; flex-wrap: wrap; }
h2 { margin: 0 0 5px; font-size: 22px; letter-spacing: -.4px; }
.head .sf-muted { margin: 0; max-width: 58ch; line-height: 1.55; }
.table-wrap { width: 100%; max-width: 100%; min-width: 0; overflow-x: auto; border-radius: var(--sf-radius); }
.old { color: #b42318; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px; }
@media (max-width: 820px) {
  .head h2 { font-size: 19px; }
}
</style>
