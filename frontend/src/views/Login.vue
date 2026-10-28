<template>
  <div class="login">
    <div class="panel sf-card">
      <h1>Find a seat you can charge at.</h1>
      <p class="sf-muted">
        Sign in to report a socket. Maintenance sees the same records from the other side.
      </p>

      <el-form :model="form" label-position="top" @submit.prevent="submit">
        <el-form-item label="Email">
          <el-input v-model="form.email" placeholder="you@connect.hku.hk" size="large" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" show-password size="large" @keyup.enter="submit" />
        </el-form-item>
        <el-button type="primary" size="large" :loading="busy" class="go" @click="submit">Sign in</el-button>
        <p v-if="error" class="err">{{ error }}</p>
      </el-form>

      <div class="demo">
        <div class="sf-muted">Demo accounts (password demo1234)</div>
        <div class="chips">
          <button v-for="a in demos" :key="a.email" class="chip" @click="fill(a)">
            <b>{{ a.displayName }}</b>
            <span>{{ a.note }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { errorText } from '../api'
import { useAuth } from '../stores/auth'

const auth = useAuth()
const router = useRouter()
const form = reactive({ email: '', password: '' })
const busy = ref(false)
const error = ref('')
const demos = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/auth/demo-accounts')
    demos.value = data
  } catch (e) { /* the login form still works */ }
})

function fill(a) {
  form.email = a.email
  form.password = a.password
}

async function submit() {
  if (!form.email || !form.password) { error.value = 'Email and password, please'; return }
  busy.value = true
  error.value = ''
  try {
    await auth.login(form.email, form.password)
    router.push('/')
  } catch (e) {
    error.value = errorText(e)
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.login { display: flex; justify-content: center; padding-top: 40px; }
.panel { width: 460px; padding: 34px 34px 28px; }
h1 { font-size: 26px; margin: 0 0 8px; letter-spacing: -.6px; }
.go { width: 100%; margin-top: 4px; }
.err { color: #b42318; font-size: 13px; margin: 10px 0 0; }
.demo { margin-top: 26px; padding-top: 18px; border-top: 1px dashed var(--sf-line); }
.chips { display: grid; gap: 8px; margin-top: 10px; }
.chip { text-align: left; background: #fbfbfa; border: 1px solid var(--sf-line); border-radius: 8px; padding: 9px 11px; cursor: pointer; font: inherit; }
.chip:hover { border-color: #c9d3cd; background: #f4f8f6; }
.chip b { display: block; font-size: 13px; }
.chip span { font-size: 12px; color: var(--sf-muted); }
</style>
