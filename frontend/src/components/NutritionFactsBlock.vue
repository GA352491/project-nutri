<script setup lang="ts">
export interface NutrientRow {
 label: string
 value: string
 dv?: string
 indent?: boolean
 thick?: boolean
}

const props = defineProps<{
 title: string
 rows: NutrientRow[]
}>()
</script>

<template>
 <div class="bg-canvas-raised border-[3px] border-ink rounded-sm p-4 font-data mb-4">
 <div class="font-display font-black text-[1.5rem] border-b-[8px] border-ink pb-2 mb-2">
 {{ title }}
 </div>
 
 <div 
 v-for="(row, idx) in rows" 
 :key="idx"
 class="flex justify-between text-[0.82rem] border-b border-border py-[5px]"
 :class="{
 'border-b-[4px] border-b-ink font-bold py-[8px]': row.thick,
 'pl-4 text-ink-muted': row.indent
 }"
 >
 <span>{{ row.label }}</span>
 <span>
 {{ row.value }}
 <span v-if="row.dv" class="text-ink-muted ml-1">{{ row.dv }}</span>
 </span>
 </div>
 </div>
</template>
