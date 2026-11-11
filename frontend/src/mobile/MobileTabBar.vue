<template>
  <nav class="m-tabs" :aria-label="t('app.name')">
    <button
      v-for="tab in TABS"
      :key="tab.key"
      type="button"
      class="m-tab"
      :class="{ on: tab.key === active }"
      :aria-current="tab.key === active ? 'page' : undefined"
      @click="$emit('select', tab.key)"
    >
      <span class="m-tab-ic"><MobileIcon :name="tab.icon" :size="21" /></span>
      <span class="m-tab-label">{{ t(tab.label) }}</span>
    </button>
  </nav>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import MobileIcon from './MobileIcon.vue'

defineProps({
  active: { type: String, default: 'find' }
})
defineEmits(['select'])

const { t } = useI18n()

const TABS = [
  { key: 'find', icon: 'find', label: 'mob.tabFind' },
  { key: 'room', icon: 'room', label: 'mob.tabRoom' },
  { key: 'report', icon: 'report', label: 'mob.tabReport' },
  { key: 'me', icon: 'me', label: 'mob.tabMe' }
]
</script>
