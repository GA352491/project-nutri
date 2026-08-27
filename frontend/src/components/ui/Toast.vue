<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = withDefaults(defineProps<{
 message: string
 variant?: 'success' | 'warning' | 'danger' | 'info'
 duration?: number
}>(), {
 variant: 'success',
 duration: 3500
})

const emit = defineEmits<{
 (e: 'close'): void
}>()

const visible = ref(true)

onMounted(() => {
 setTimeout(() => {
 visible.value = false
 setTimeout(() => emit('close'), 300)
 }, props.duration)
})
</script>

<template>
 <Transition name="toast">
 <div
 v-if="visible"
 role="alert"
 class="flex items-center gap-3 px-4 py-3 rounded-md shadow-card border text-[0.88rem] font-body min-w-[260px] max-w-sm"
 :class="{
 'bg-success-soft border-success/25 text-success': variant === 'success',
 'bg-warning-soft border-warning/25 text-warning': variant === 'warning',
 'bg-danger-soft border-danger/25 text-danger': variant === 'danger',
 'bg-info-soft border-info/25 text-info': variant === 'info',
 }"
 >
 <!-- Icon -->
 <span class="shrink-0 text-[1.1rem]">
 {{ variant === 'success' ? '✓' : variant === 'danger' ? '✕' : variant === 'warning' ? '▲' : 'ℹ' }}
 </span>
 <span class="flex-1">{{ message }}</span>
 <button class="shrink-0 opacity-60 hover:opacity-100 transition-opacity text-lg leading-none" @click="visible = false">×</button>
 </div>
 </Transition>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active {
 transition: opacity 260ms var(--ease-out), transform 260ms var(--ease-out);
}
.toast-enter-from {
 opacity: 0;
 transform: translateY(-8px) scale(0.96);
}
.toast-leave-to {
 opacity: 0;
 transform: translateY(-4px) scale(0.97);
}
</style>
