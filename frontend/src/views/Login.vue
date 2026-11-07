<template>
  <div class="login">
    <div class="panel sf-card">
      <span class="sf-kicker">CCST9003 · R21</span>
      <h1>{{ t('login.title') }}</h1>
      <p class="sf-muted intro">{{ t('login.intro') }}</p>

      <el-form :model="form" label-position="top" @submit.prevent="submit">
        <el-form-item :label="t('login.email')">
          <el-input v-model="form.email" :placeholder="t('login.emailPlaceholder')" size="large" />
        </el-form-item>
        <el-form-item :label="t('login.password')">
          <el-input v-model="form.password" type="password" show-password size="large" @keyup.enter="submit" />
        </el-form-item>
        <el-button type="primary" size="large" :loading="busy" class="go" @click="submit">{{ t('login.signIn') }}</el-button>
        <p v-if="error" class="err">{{ error }}</p>
      </el-form>

      <div class="demo">
        <div class="sf-muted">{{ t('login.demoNote') }}</div>
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
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import api, { errorText } from '../api'
import { useAuth } from '../stores/auth'

const { t } = useI18n()
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
  if (!form.email || !form.password) { error.value = t('login.needFields'); return }
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
.login { display: flex; justify-content: center; padding: 42px 0 20px; }
.panel {
  width: 468px;
  max-width: 100%;
  padding: 34px 34px 28px;
  border-radius: 18px;
  box-shadow: 0 2px 4px rgba(16, 40, 34, .05), 0 30px 60px -30px rgba(16, 40, 34, .55);
  position: relative;
  overflow: hidden;
}
/* a thin green→gold rule at the top of the panel, echoing the header line */
.panel::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--sf-green) 0%, var(--sf-green-mid) 45%, var(--sf-gold) 100%);
}
h1 { font-size: 26px; margin: 10px 0 8px; letter-spacing: -.6px; line-height: 1.25; color: var(--sf-ink); }
.intro { margin: 0 0 20px; line-height: 1.6; }
.go { width: 100%; margin-top: 4px; }
.err { color: #b42318; font-size: 13px; margin: 10px 0 0; }
.demo { margin-top: 26px; padding-top: 18px; border-top: 1px dashed var(--sf-line); }
.chips { display: grid; gap: 8px; margin-top: 10px; }
.chip {
  text-align: left; background: #fbfdfc; border: 1px solid var(--sf-line);
  border-radius: 10px; padding: 10px 12px; cursor: pointer; font: inherit; transition: .13s;
}
.chip:hover { border-color: var(--sf-green-line); background: var(--sf-green-soft); box-shadow: 0 6px 16px -12px rgba(2, 70, 56, .8); }
.chip b { display: block; font-size: 13px; color: var(--sf-ink); }
.chip span { font-size: 12px; color: var(--sf-muted); }
@media (max-width: 820px) {
  .login { padding: 20px 0 10px; }
  .panel { padding: 26px 22px 22px; }
  h1 { font-size: 22px; }
}
</style>
