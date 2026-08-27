<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
 totalKcal: number
 targetKcal: number
}>()

const remaining = computed(() => Math.max(0, props.targetKcal - props.totalKcal))
const progressPercentage = computed(() => {
 if (props.targetKcal === 0) return 0
 return Math.min(100, Math.max(0, (props.totalKcal / props.targetKcal) * 100))
})

// SVG properties
const radius = 44
const circumference = 2 * Math.PI * radius
const strokeDashoffset = computed(() => {
 return circumference - (progressPercentage.value / 100) * circumference
})

// a11y — WCAG 2.1 AA: descriptive label for screen readers
const ringAriaLabel = computed(() =>
 `${props.totalKcal} of ${props.targetKcal} kilocalories consumed, ${remaining.value} remaining`
)
</script>

<template>
 <div class="bg-canvas-raised rounded-lg p-6 shadow-card flex items-center gap-6 mb-4 animate-[card-in_260ms_var(--ease-out)_both]">
 <div class="relative w-[104px] h-[104px] shrink-0">
 <svg
 width="104" height="104" viewBox="0 0 104 104" class="-rotate-90"
 role="img"
 :aria-label="ringAriaLabel"
 >
 <circle 
 cx="52" 
 cy="52" 
 :r="radius" 
 fill="none" 
 stroke="var(--color-border)" 
 stroke-width="10"
 />
 <circle 
 cx="52" 
 cy="52" 
 :r="radius" 
 fill="none" 
 stroke="var(--color-primary)" 
 stroke-width="10" 
 stroke-linecap="round"
 class="transition-all duration-700 ease-[var(--ease-out)] delay-150"
 :style="{ strokeDasharray: circumference, strokeDashoffset }"
 />
 </svg>
 <!-- aria-hidden: info already conveyed by SVG aria-label above -->
 <div class="absolute inset-0 flex flex-col items-center justify-center" aria-hidden="true">
 <span class="font-data font-bold text-[1.35rem] tabular-nums">{{ remaining }}</span>
 <span class="text-[0.62rem] text-ink-muted tracking-[0.05em]">kcal left</span>
 </div>
 </div>
 
 <div class="text-[0.8rem] flex-1">
 <slot name="legend">
 <!-- Default legend placeholder -->
 </slot>
 </div>
 </div>
</template>

<style scoped>
@keyframes card-in {
 from { opacity: 0; transform: translateY(6px); }
 to { opacity: 1; transform: translateY(0); }
}
</style>
