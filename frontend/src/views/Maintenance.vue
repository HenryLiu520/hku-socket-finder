<template>
  <div>
    <div class="head">
      <div>
        <h2>Repair queue</h2>
        <p class="sf-muted">Sockets reported broken, oldest first. Marking one repaired is what students see next.</p>
      </div>
      <el-tag v-if="rows.length" type="danger" effect="plain">{{ rows.length }} open</el-tag>
    </div>

    <el-table :data="rows" v-loading="loading" class="sf-card" empty-text="Nothing reported broken right now">
      <el-table-column prop="building" label="Building" width="110" />
      <el-table-column prop="roomCode" label="Room" width="130" />
      <el-table-column prop="seat" label="Seat" width="80" />
      <el-table-column prop="code" label="Socket" width="170">
        <template #default="{ row }"><code>{{ row.code }}</code></template>
      </el-table-column>
      <el-table-column label="Fault" width="110">
        <template #default="{ row }">
          <el-tag :type="row.state === 'NO_POWER' ? 'danger' : 'warning'" effect="plain" size="small">
            {{ row.state === 'NO_POWER' ? 'No power' : 'Loose' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Broken for" width="130">
        <template #default="{ row }">
          <b :class="{ old: row.daysBroken >= 7 }">{{ row.daysBroken }} day{{ row.daysBroken === 1 ? '' : 's' }}</b>
        </template>
      </el-table-column>
      <el-table-column label="Reported by" width="120">
        <template #default="{ row }">{{ row.reporters }} student{{ row.reporters === 1 ? '' : 's' }}</template>
      </el-table-column>
      <el-table-column label="Last checked" width="180">
        <template #default="{ row }">{{ fmt(row.lastCheckedAt) }}</template>
      </el-table-column>
      <el-table-column label="">
        <template #default="{ row }">
          <el-button size="small" type="primary" plain @click="openRepair(row)">Mark repaired</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" title="Mark repaired" width="420px">
      <p class="sf-muted">A note is optional, but it is the only record of what was actually wrong.</p>
      <el-input v-model="note" type="textarea" :rows="3" placeholder="e.g. replaced the socket plate" />
      <template #footer>
        <el-button @click="dialog = false">Cancel</el-button>
        <el-button type="primary" :loading="busy" @click="confirm">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { errorText } from '../api'
import { ElMessage } from 'element-plus'

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
    ElMessage.success('Marked repaired')
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
.head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 18px; }
h2 { margin: 0 0 4px; font-size: 20px; letter-spacing: -.3px; }
.old { color: #b42318; }
</style>
