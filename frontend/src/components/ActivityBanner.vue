<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
 title: string
 description: string
 acceptText?: string
 dismissText?: string
}>()

const emit = defineEmits<{
 (e: 'accept'): void
 (e: 'dismiss'): void
}>()

const isVisible = ref(true)

function handleAccept() {
 emit('accept')
 isVisible.value = false
}

function handleDismiss() {
 emit('dismiss')
 isVisible.value = false
}
</script>

<template>
 <div 
 v-if="isVisible"
 class="bg-info-soft border border-info/25 rounded-md px-4 py-3 text-[0.85rem] mb-4 flex gap-3 items-start animate-[banner-in_260ms_var(--ease-out)_400ms_both]"
 >
 <div>
 <strong class="text-info block text-[0.78rem] tracking-[0.03em] mb-[2px]">
 {{ title }}
 </strong>
 {{ description }}
 <div class="flex gap-2 mt-2">
 <button 
 class="font-body font-semibold text-[0.76rem] border-none text-white bg-info px-3 py-1 rounded-full cursor-pointer transition-transform duration-[100ms] ease-[var(--ease-standard)] active:scale-95"
 @click="handleAccept"
 >
 {{ acceptText || 'Accept' }}
 </button>
 <button 
 class="font-body font-semibold text-[0.76rem] border border-info text-info bg-transparent px-2.5 py-1 rounded-full cursor-pointer transition-all duration-[180ms] ease-[var(--ease-standard)] active:scale-95 hover:bg-info/10"
 @click="handleDismiss"
 >
 {{ dismissText || 'Keep original' }}
 </button>
 </div>
 </div>
 </div>
</template>

<style scoped>
@keyframes banner-in {
 from { opacity: 0; transform: translateY(-8px); }
 to { opacity: 1; transform: translateY(0); }
}
</style>
