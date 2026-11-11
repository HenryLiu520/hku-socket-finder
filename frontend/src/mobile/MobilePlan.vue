<template>
  <svg class="m-plan" :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('map.aria')">
    <rect x="3" y="3" :width="W - 6" :height="H - 6" rx="12" class="m-plan-room" />
    <text x="14" y="18" class="m-plan-edge">{{ t('map.windowWall') }}</text>
    <text :x="W - 14" :y="H - 9" class="m-plan-edge end">{{ t('map.entrance') }}</text>

    <g v-for="d in desks" :key="d.key">
      <rect :x="d.x" :y="d.y" :width="DESK_W" :height="deskH" rx="9" class="m-plan-desk" />
      <text :x="d.x + 9" :y="d.y + 15" class="m-plan-seat">
        {{ t('map.seat', { label: d.label }) }}
      </text>

      <g
        v-for="(s, i) in d.sockets"
        :key="s.id"
        class="m-plan-sock"
        role="button"
        tabindex="0"
        :aria-label="s.code"
        @click="$emit('pick', s)"
        @keydown.enter.prevent="$emit('pick', s)"
        @keydown.space.prevent="$emit('pick', s)"
      >
        <title>{{ s.code }}</title>
        <rect
          :x="chipX(d, i)"
          :y="chipY(d, i)"
          :width="CHIP_W"
          :height="CHIP_H"
          rx="7"
          :fill="fillColor(s.state)"
        />
        <text :x="chipX(d, i) + CHIP_W / 2" :y="chipY(d, i) + CHIP_H / 2 + 3.3" class="m-plan-num" :class="{ dark: isPale(s.state) }">
          {{ tail(s.code) }}
        </text>
      </g>

      <text v-if="!d.sockets.length" :x="d.x + 9" :y="d.y + 38" class="m-plan-none">{{ t('map.noSocket') }}</text>
    </g>
  </svg>
</template>

<script setup>
/**
 * The floor plan, redrawn for a narrow screen: two desks a row, sockets as
 * coloured tags with the four sticker digits on them. Tapping one opens the
 * report sheet, exactly like the desktop plan.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { fillColor, isPale, tail } from './socketState.js'

const { t } = useI18n()

const props = defineProps({
  seats: { type: Array, default: () => [] }
})
defineEmits(['pick'])

const W = 330
const COLS = 2
const START_X = 10
const START_Y = 30
const GAP_X = 10
const GAP_Y = 12
const DESK_W = 150
const HEAD = 22
const CHIP_W = 40
const CHIP_H = 30
const CHIP_GAP_X = 5
const CHIP_GAP_Y = 6
const PER_ROW = 3

const seats = computed(() => (props.seats || []).filter((s) => s && s.label))

/** Every desk is as tall as the busiest one, so the grid stays even. */
const rows = computed(() => {
  let most = 1
  for (const s of seats.value) {
    const n = (s.sockets || []).length
    if (n > 0) most = Math.max(most, Math.ceil(n / PER_ROW))
  }
  return most
})

const deskH = computed(() => HEAD + rows.value * CHIP_H + (rows.value - 1) * CHIP_GAP_Y + 10)

const desks = computed(() =>
  seats.value.map((s, i) => ({
    key: s.id || i,
    label: s.label,
    // Carry the seat label on the socket, so the report sheet can show "seat B" too.
    sockets: (s.sockets || []).map((x) => ({ ...x, seat: s.label })),
    x: START_X + (i % COLS) * (DESK_W + GAP_X),
    y: START_Y + Math.floor(i / COLS) * (deskH.value + GAP_Y)
  }))
)

const H = computed(() => {
  const lines = Math.max(1, Math.ceil(seats.value.length / COLS))
  return START_Y + lines * (deskH.value + GAP_Y) - GAP_Y + 24
})

const chipX = (d, i) => d.x + 8 + (i % PER_ROW) * (CHIP_W + CHIP_GAP_X)
const chipY = (d, i) => d.y + HEAD + Math.floor(i / PER_ROW) * (CHIP_H + CHIP_GAP_Y)
</script>
