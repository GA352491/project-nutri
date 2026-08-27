<script setup lang="ts">
import { onMounted, onUnmounted, useId, ref, nextTick } from 'vue'

const props = withDefaults(defineProps<{
 modelValue: boolean
 title?: string
 size?: 'sm' | 'md' | 'lg'
 closeOnBackdrop?: boolean
}>(), {
 size: 'md',
 closeOnBackdrop: true
})

const emit = defineEmits<{
 (e: 'update:modelValue', val: boolean): void
}>()

// Unique id for aria-labelledby
const titleId = useId ? useId() : `modal-title-${Math.random().toString(36).slice(2)}`
const panelRef = ref<HTMLElement | null>(null)
let triggerEl: Element | null = null

const FOCUSABLE = [
 'a[href]', 'button:not([disabled])', 'textarea:not([disabled])',
 'input:not([disabled])', 'select:not([disabled])', '[tabindex]:not([tabindex="-1"])'
].join(',')

function getFocusable(): HTMLElement[] {
 return Array.from(panelRef.value?.querySelectorAll<HTMLElement>(FOCUSABLE) ?? [])
}

function trapFocus(e: KeyboardEvent) {
 if (e.key !== 'Tab') return
 const focusable = getFocusable()
 if (!focusable.length) return
 const first = focusable[0]
 const last = focusable[focusable.length - 1]
 if (e.shiftKey && document.activeElement === first) {
 e.preventDefault(); last.focus()
 } else if (!e.shiftKey && document.activeElement === last) {
 e.preventDefault(); first.focus()
 }
}

function close() {
 emit('update:modelValue', false)
 nextTick(() => (triggerEl as HTMLElement | null)?.focus())
}

function handleKey(e: KeyboardEvent) {
 if (e.key === 'Escape') close()
 trapFocus(e)
}

async function focusFirst() {
 await nextTick()
 getFocusable()[0]?.focus()
}

onMounted(() => {
 triggerEl = document.activeElement
 document.addEventListener('keydown', handleKey)
})
onUnmounted(() => document.removeEventListener('keydown', handleKey))
</script>

<template>
 <Teleport to="body">
 <Transition name="modal-overlay">
 <div
 v-if="modelValue"
 class="fixed inset-0 z-50 flex items-center justify-center p-4"
 aria-modal="true"
 role="dialog"
 :aria-labelledby="titleId"
 @vue:mounted="focusFirst"
 >
 <!-- Backdrop -->
 <div
 class="absolute inset-0 bg-ink/40 backdrop-blur-sm"
 @click="closeOnBackdrop && close()"
 />

 <!-- Panel -->
 <Transition name="modal-panel">
 <div
 v-if="modelValue"
 ref="panelRef"
 class="relative z-10 bg-canvas-raised rounded-lg shadow-[0_20px_60px_rgba(28,38,32,.2)] w-full overflow-hidden"
 :class="{
 'max-w-sm': size === 'sm',
 'max-w-md': size === 'md',
 'max-w-2xl': size === 'lg',
 }"
 >
 <!-- Header -->
 <div v-if="title || $slots.header" class="flex items-center justify-between px-6 pt-5 pb-4 border-b border-border">
 <slot name="header">
 <h2 :id="titleId" class="font-display font-semibold text-[1.1rem] text-ink m-0">{{ title }}</h2>
 </slot>
 <button
 class="w-8 h-8 flex items-center justify-center rounded-sm text-ink-muted hover:text-ink hover:bg-canvas transition-colors cursor-pointer text-xl leading-none"
 aria-label="Close"
 @click="close"
 >×</button>
 </div>

 <!-- Body -->
 <div class="px-6 py-5">
 <slot />
 </div>

 <!-- Footer -->
 <div v-if="$slots.footer" class="px-6 pb-5 flex justify-end gap-3">
 <slot name="footer" />
 </div>
 </div>
 </Transition>
 </div>
 </Transition>
 </Teleport>
</template>

<style scoped>
.modal-overlay-enter-active,
.modal-overlay-leave-active {
 transition: opacity 260ms var(--ease-out);
}
.modal-overlay-enter-from,
.modal-overlay-leave-to { opacity: 0; }

.modal-panel-enter-active,
.modal-panel-leave-active {
 transition: opacity 260ms var(--ease-out), transform 260ms var(--ease-out);
}
.modal-panel-enter-from {
 opacity: 0;
 transform: translateY(12px) scale(0.97);
}
.modal-panel-leave-to {
 opacity: 0;
 transform: translateY(6px) scale(0.98);
}
</style>
