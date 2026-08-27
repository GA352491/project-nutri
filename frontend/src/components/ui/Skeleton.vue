<script setup lang="ts">
withDefaults(defineProps<{
 type?: 'text' | 'circle' | 'card'
 lines?: number
 width?: string
}>(), {
 type: 'text',
 lines: 1,
 width: 'full'
})
</script>

<template>
 <!-- Card skeleton -->
 <div
 v-if="type === 'card'"
 class="bg-canvas-raised rounded-md shadow-card p-3 flex gap-3 items-center animate-pulse"
 >
 <div class="w-[52px] h-[52px] rounded-sm bg-border shrink-0" />
 <div class="flex-1 space-y-2">
 <div class="h-3 bg-border rounded-sm w-2/3" />
 <div class="h-2.5 bg-border rounded-sm w-1/2" />
 </div>
 <div class="w-14 h-7 rounded-full bg-border" />
 </div>

 <!-- Circle skeleton -->
 <div
 v-else-if="type === 'circle'"
 class="w-[104px] h-[104px] rounded-full bg-border animate-pulse"
 />

 <!-- Text skeleton (default) -->
 <div v-else class="space-y-2 animate-pulse" :class="`w-${width}`">
 <div
 v-for="i in lines"
 :key="i"
 class="h-3 bg-border rounded-sm"
 :class="i === lines && lines > 1 ? 'w-4/5' : 'w-full'"
 />
 </div>
</template>
