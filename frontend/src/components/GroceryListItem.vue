<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
 name: string
 quantity?: string
 initialChecked?: boolean
}>()

const emit = defineEmits<{
 (e: 'update:checked', value: boolean): void
}>()

const isChecked = ref(props.initialChecked ?? false)

function toggle() {
 isChecked.value = !isChecked.value
 emit('update:checked', isChecked.value)
}
</script>

<template>
 <div 
 class="flex items-center gap-3 py-2 border-b border-border text-[0.88rem] cursor-pointer"
 role="checkbox"
 :aria-checked="isChecked"
 :aria-label="quantity ? `${name}, ${quantity}` : name"
 tabindex="0"
 @click="toggle"
 @keydown.space.prevent="toggle"
 @keydown.enter.prevent="toggle"
 >
 <div 
 class="w-[18px] h-[18px] border-2 rounded-[5px] shrink-0 transition-colors duration-150"
 :class="[
 isChecked 
 ? 'bg-primary border-primary relative' 
 : 'border-border bg-canvas'
 ]"
 aria-hidden="true"
 >
 <!-- Custom checkmark icon SVG inside the box if checked -->
 <svg v-if="isChecked" class="w-full h-full text-white p-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
 <polyline points="20 6 9 17 4 12"></polyline>
 </svg>
 </div>
 
 <div :class="{ 'line-through text-ink-muted': isChecked }" aria-hidden="true">
 {{ name }}
 <span v-if="quantity" class="text-ink-muted">— {{ quantity }}</span>
 </div>
 </div>
</template>
