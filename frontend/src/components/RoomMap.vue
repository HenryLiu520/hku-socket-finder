<template>
  <div class="map-card" :class="{ 'sf-card': !flat, flat }">
    <div class="map-h">
      <span class="t">{{ t('map.title') }}</span>
      <span class="sf-muted legend">
        <i class="d green"></i> {{ stateLabel('WORKING', true) }}
        <i class="d amber"></i> {{ stateLabel('LOOSE', true) }}
        <i class="d red"></i> {{ stateLabel('NO_POWER', true) }}
        <i class="d grey"></i> {{ stateLabel('UNKNOWN', true) }}
      </span>
    </div>

    <svg :viewBox="`0 0 ${W} ${H}`" class="plan" role="img" :aria-label="t('map.aria')">
      <rect x="6" y="6" :width="W - 12" :height="H - 12" rx="14" class="room" />
      <text x="20" y="26" class="edge">{{ t('map.windowWall') }}</text>
      <text :x="W - 20" :y="H - 12" class="edge end">{{ t('map.entrance') }}</text>

      <g v-for="d in desks" :key="d.key">
        <rect :x="d.x" :y="d.y" :width="DESK_W" :height="DESK_H" rx="7" class="desk" />
        <text :x="d.x + 10" :y="d.y + 16" class="seat">{{ t('map.seat', { label: d.label }) }}</text>

        <g v-for="(s, i) in d.sockets" :key="s.id" class="sock" @click="$emit('pick', s)">
          <title>{{ s.code }}</title>
          <rect :x="d.x + 10 + (i % 3) * 46" :y="d.y + 26 + Math.floor(i / 3) * 26"
                width="42" height="19" rx="5" :class="'box ' + s.state.toLowerCase()" />
          <text :x="d.x + 31 + (i % 3) * 46" :y="d.y + 40 + Math.floor(i / 3) * 26"
                class="num" :class="{ onlight: s.state === 'UNKNOWN' || s.state === 'REPAIRED' }">{{ tail(s.code) }}</text>
        </g>

        <text v-if="!d.sockets.length" :x="d.x + 10" :y="d.y + 38" class="none">{{ t('map.noSocket') }}</text>
      </g>
    </svg>

    <p class="sf-muted note">{{ t('map.note') }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { stateLabel } from '../i18n'

const { t } = useI18n()

const props = defineProps({
  seats: { type: Array, default: () => [] },
  flat: { type: Boolean, default: false }
})
defineEmits(['pick'])

const W = 660
const COLS = 3
const GAP_X = 30
const GAP_Y = 26
const START_X = 34
const START_Y = 52
const DESK_W = 186
const DESK_H = 78

const tail = (code) => (code ? code.split('-').pop() : '')
const rows = computed(() => Math.max(1, Math.ceil((props.seats || []).length / COLS)))
const H = computed(() => START_Y + rows.value * (DESK_H + GAP_Y) - GAP_Y + 40)

/** A tidy schematic, three desks a row, rather than a projection of raw coordinates. */
const desks = computed(() => {
  const seats = (props.seats || []).filter((s) => s.label)
  return seats.map((s, i) => ({
    key: s.id || i,
    label: s.label,
    sockets: s.sockets || [],
    x: START_X + (i % COLS) * (DESK_W + GAP_X),
    y: START_Y + Math.floor(i / COLS) * (DESK_H + GAP_Y)
  }))
})
</script>

<style scoped>
.map-card { padding: 15px 17px 11px; margin-bottom: 16px; }
.map-card.flat { padding: 0; margin-bottom: 0; border: 0; box-shadow: none; background: transparent; }
.map-h { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 5px; }
.t { font-size: 12px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--sf-muted); }
.legend { display: inline-flex; align-items: center; gap: 10px; font-size: 11.5px; flex-wrap: wrap; }
.d { width: 8px; height: 8px; border-radius: 2px; display: inline-block; margin-right: 4px; }
.green { background: #12b76a; }
.amber { background: #f79009; }
.red { background: #f04438; }
.grey { background: #98a2b3; }
.plan { width: 100%; max-width: 640px; height: auto; display: block; margin: 2px auto 0; }
/* Semantic socket colours are unchanged; only the paper underneath them warms up. */
.room { fill: #fbfdfb; stroke: #cfdad5; stroke-width: 1.5; stroke-dasharray: 7 5; }
.edge { font-size: 9.5px; fill: #a6afaa; letter-spacing: .4px; }
.edge.end { text-anchor: end; }
.desk { fill: #ffffff; stroke: #dde5e1; stroke-width: 1; }
.seat { font-size: 9.5px; fill: #8a938e; letter-spacing: .3px; }
.none { font-size: 9px; fill: #c3cbc7; }
.sock { cursor: pointer; }
.sock:hover .box { stroke: var(--sf-green); stroke-width: 1.6; }
.box { stroke: none; }
.box.working { fill: #12b76a; }
.box.loose { fill: #f79009; }
.box.no_power { fill: #f04438; }
.box.broken { fill: #f04438; }
.box.repaired { fill: #e4e7ff; }
.box.unknown { fill: #eceff1; }
.num { font-size: 9px; fill: #fff; text-anchor: middle; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .2px; }
.num.onlight { fill: #6b7280; }
.note { margin: 6px 0 0; font-size: 11.5px; }
</style>
