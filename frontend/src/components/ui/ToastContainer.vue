<script setup lang="ts">
import { useToastStore } from '../../stores/toast'
import Icon from './Icon.vue'

const toastStore = useToastStore()
</script>

<template>
 <div class="fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none">
 <TransitionGroup name="toast-list">
 <div
 v-for="t in toastStore.toasts"
 :key="t.id"
 class="pointer-events-auto p-4 rounded-xl border shadow-xl flex items-start gap-3 backdrop-blur-md transition-all duration-300"
 :class="{
 'bg-emerald-50/95 border-emerald-300 text-emerald-950': t.variant === 'success',
 'bg-rose-50/95 border-rose-300 text-rose-950': t.variant === 'danger',
 'bg-amber-50/95 border-amber-300 text-amber-950': t.variant === 'warning',
 'bg-sky-50/95 border-sky-300 text-sky-950': t.variant === 'info',
 }"
 >
 <!-- Icon -->
 <div class="shrink-0 mt-0.5">
 <div
 v-if="t.variant === 'success'"
 class="w-5 h-5 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold"
 >
 ✓
 </div>
 <div
 v-else-if="t.variant === 'danger'"
 class="w-5 h-5 rounded-full bg-rose-600 text-white flex items-center justify-center text-xs font-bold"
 >
 ✕
 </div>
 <div
 v-else-if="t.variant === 'warning'"
 class="w-5 h-5 rounded-full bg-amber-600 text-white flex items-center justify-center text-xs font-bold"
 >
 !
 </div>
 <div
 v-else
 class="w-5 h-5 rounded-full bg-sky-600 text-white flex items-center justify-center text-xs font-bold"
 >
 i
 </div>
 </div>

 <!-- Text -->
 <div class="flex-1 min-w-0">
 <h4 v-if="t.title" class="font-bold text-xs leading-tight mb-0.5">{{ t.title }}</h4>
 <p class="text-xs leading-relaxed opacity-90 break-words">{{ t.message }}</p>
 </div>

 <!-- Close Button -->
 <button
 class="shrink-0 opacity-50 hover:opacity-100 p-0.5 rounded transition-opacity"
 @click="toastStore.remove(t.id)"
 >
 <Icon name="x" class="w-4 h-4" />
 </button>
 </div>
 </TransitionGroup>
 </div>
</template>

<style scoped>
.toast-list-enter-active,
.toast-list-leave-active {
 transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-list-enter-from {
 opacity: 0;
 transform: translateX(30px) scale(0.95);
}
.toast-list-leave-to {
 opacity: 0;
 transform: translateY(20px) scale(0.95);
}
</style>
