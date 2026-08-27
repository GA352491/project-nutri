<script setup lang="ts">
const props = defineProps<{
 slots: string[]
 modelValue?: string
}>()

const emit = defineEmits<{
 (e: 'update:modelValue', value: string): void
}>()

function selectSlot(slot: string) {
 emit('update:modelValue', slot)
}
</script>

<template>
 <div class="flex gap-2 flex-wrap" role="radiogroup" aria-label="Available time slots">
 <div 
 v-for="slot in slots" 
 :key="slot"
 class="font-data text-[0.8rem] border border-border rounded-md px-[14px] py-[8px] cursor-pointer transition-colors duration-[180ms] bg-canvas-raised"
 :class="[
 modelValue === slot 
 ? 'bg-primary text-white border-primary shadow-md' 
 : 'text-ink hover:border-primary/50 hover:bg-canvas'
 ]"
 role="radio"
 :aria-checked="modelValue === slot"
 :aria-label="`Select ${slot}`"
 tabindex="0"
 @click="selectSlot(slot)"
 @keydown.space.prevent="selectSlot(slot)"
 @keydown.enter.prevent="selectSlot(slot)"
 >
 {{ slot }}
 </div>
 </div>
</template>
