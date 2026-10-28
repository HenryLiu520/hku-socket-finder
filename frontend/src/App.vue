<template>
  <div class="shell">
    <header class="bar">
      <div class="sf-wrap bar-inner">
        <div class="brand" @click="$router.push('/')">
          <span class="dot"></span>
          <div>
            <div class="name">Socket Finder</div>
            <div class="sub">CCST9003 · Group R21 · Chi Wah L1</div>
          </div>
        </div>

        <nav v-if="auth.signedIn" class="nav">
          <router-link to="/" class="navlink">Find a socket</router-link>
          <router-link v-if="auth.isMaintenance" to="/maintenance" class="navlink">Repair queue</router-link>
        </nav>

        <div v-if="auth.signedIn" class="who">
          <span class="pill" :class="auth.isMaintenance ? 'pill-m' : 'pill-s'">
            {{ auth.isMaintenance ? 'Maintenance' : 'Student' }}
          </span>
          <span class="sf-muted">{{ auth.user.displayName }}</span>
          <el-button link type="primary" @click="signOut">Sign out</el-button>
        </div>
      </div>
    </header>

    <main class="sf-wrap main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from './stores/auth'

const auth = useAuth()
const router = useRouter()

function signOut() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.shell { min-height: 100%; display: flex; flex-direction: column; }
.bar { background: #fff; border-bottom: 1px solid var(--sf-line); position: sticky; top: 0; z-index: 10; }
.bar-inner { display: flex; align-items: center; gap: 24px; height: 62px; }
.brand { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.dot { width: 10px; height: 10px; border-radius: 50%; background: var(--sf-green); box-shadow: 0 0 0 4px rgba(11,107,79,.12); }
.name { font-weight: 650; font-size: 15px; letter-spacing: -.2px; }
.sub { font-size: 11.5px; color: var(--sf-muted); }
.nav { display: flex; gap: 18px; margin-left: 8px; }
.navlink { color: var(--sf-muted); text-decoration: none; font-size: 13.5px; padding: 6px 2px; }
.navlink.router-link-active { color: var(--sf-ink); font-weight: 600; box-shadow: inset 0 -2px 0 var(--sf-green); }
.who { margin-left: auto; display: flex; align-items: center; gap: 10px; font-size: 13px; }
.pill { font-size: 11px; padding: 2px 8px; border-radius: 999px; font-weight: 600; }
.pill-s { background: #eef6f2; color: #0b6b4f; }
.pill-m { background: #eef2ff; color: #3538cd; }
.main { padding: 26px 20px 60px; flex: 1; }
</style>
