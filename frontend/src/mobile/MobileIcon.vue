<template>
  <svg
    class="m-icon"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="stroke"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <template v-if="name === 'find'">
      <circle cx="10.6" cy="10.4" r="6.1" />
      <path d="M15.3 15.3 20 20" />
      <circle cx="10.6" cy="10.4" r="1.5" fill="currentColor" stroke="none" />
    </template>

    <template v-else-if="name === 'room'">
      <rect x="3.4" y="4.6" width="17.2" height="14.8" rx="3.2" />
      <path d="M3.4 9.4h17.2" />
      <circle cx="8.5" cy="14.6" r="1.35" fill="currentColor" stroke="none" />
      <circle cx="15.5" cy="14.6" r="1.35" fill="currentColor" stroke="none" />
    </template>

    <template v-else-if="name === 'report'">
      <path d="M12 4.4 21 19.8H3z" />
      <path d="M12 9.9v4.2" />
      <circle cx="12" cy="16.9" r=".95" fill="currentColor" stroke="none" />
    </template>

    <template v-else-if="name === 'me'">
      <circle cx="12" cy="8.3" r="3.5" />
      <path d="M4.9 19.9c1-3.5 3.7-5.3 7.1-5.3s6.1 1.8 7.1 5.3" />
    </template>

    <template v-else-if="name === 'back'"><path d="M15 5 8 12l7 7" /></template>

    <template v-else-if="name === 'chevron'"><path d="M9.5 6l6 6-6 6" /></template>

    <template v-else-if="name === 'check'"><path d="M5 12.6 9.6 17 19 7.4" /></template>

    <template v-else-if="name === 'close'"><path d="M6.2 6.2 17.8 17.8M17.8 6.2 6.2 17.8" /></template>
  </svg>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 22 },
  stroke: { type: [Number, String], default: 1.7 }
})
</script>

<style scoped>
.m-icon { display: block; flex: 0 0 auto; }
</style>
