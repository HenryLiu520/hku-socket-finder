<template>
  <div>
    <div class="head">
      <div>
        <h2>{{ t('me.title') }}</h2>
        <p class="sf-muted">{{ t('me.intro') }}</p>
      </div>
      <el-tag v-if="badge.earned" type="success" effect="plain">{{ t('me.badge.' + badge.earned) }}</el-tag>
    </div>

    <div class="grid">
      <div class="sf-card pad">
        <div class="sf-kicker">{{ t('me.score') }}</div>
        <div class="big">{{ score }}</div>
        <p class="sf-muted">{{ t('me.scoreNote') }}</p>

        <div class="row">
          <span class="sf-muted">{{ t('me.weight') }}</span>
          <b>{{ weight }}×</b>
        </div>
        <div class="row">
          <span class="sf-muted">{{ t('me.confirmed') }}</span>
          <b>{{ me ? me.confirmed : 0 }}</b>
        </div>
        <div class="row">
          <span class="sf-muted">{{ t('me.refuted') }}</span>
          <b>{{ me ? me.refuted : 0 }}</b>
        </div>
      </div>

      <div class="sf-card pad">
        <div class="sf-kicker">{{ t('me.incentive') }}</div>
        <p class="sf-muted">{{ t('me.incentiveNote') }}</p>

        <div class="bar" role="progressbar" :aria-valuenow="Math.round(badge.progress * 100)"
             aria-valuemin="0" aria-valuemax="100">
          <span :style="{ width: (badge.progress * 100) + '%' }"></span>
        </div>

        <p v-if="badge.next" class="next">
          {{ t('me.next', { n: badge.need, badge: t('me.badge.' + badge.next) }) }}
        </p>
        <p v-else class="next">{{ t('me.allEarned') }}</p>

        <ul class="tiers">
          <li v-for="b in BADGES" :key="b.key" :class="{ on: me && me.confirmed >= b.at }">
            <span class="tick">{{ me && me.confirmed >= b.at ? '✓' : '·' }}</span>
            <span>{{ t('me.badge.' + b.key) }}</span>
            <span class="sf-muted">{{ b.at }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'
import { BADGES, badgeFor } from '../lib/reputation'

const { t } = useI18n()
const me = ref(null)

const score = computed(() => (me.value ? Math.round(me.value.score * 100) : '—'))
const weight = computed(() => (me.value ? me.value.weight.toFixed(2) : '—'))
const badge = computed(() => badgeFor(me.value ? me.value.confirmed : 0))

onMounted(async () => {
  try {
    const { data } = await api.get('/auth/me')
    me.value = data
  } catch (e) {
    me.value = null
  }
})
</script>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 16px; }
.head h2 { margin: 0 0 4px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.pad { padding: 20px 22px; }
.big { font-size: 44px; font-weight: 700; color: var(--sf-green, #024638); line-height: 1.1; margin: 6px 0 4px; }
.row { display: flex; justify-content: space-between; border-top: 1px solid var(--sf-line, #e6ebe9); padding: 8px 0; font-size: 14px; }
.bar { height: 10px; border-radius: 999px; background: rgba(2, 70, 56, .10); overflow: hidden; margin: 14px 0 8px; }
.bar span { display: block; height: 100%; background: linear-gradient(90deg, #024638, #4d7e74); }
.next { font-size: 13px; color: var(--sf-muted, #6b7b77); margin: 0 0 12px; }
.tiers { list-style: none; padding: 0; margin: 0; }
.tiers li { display: flex; align-items: center; gap: 10px; padding: 6px 0; font-size: 13.5px; color: var(--sf-muted, #6b7b77); }
.tiers li.on { color: var(--sf-ink, #1f2d2a); font-weight: 600; }
.tiers li .sf-muted { margin-left: auto; }
.tick { width: 16px; text-align: center; color: var(--sf-gold, #b49764); }
</style>
