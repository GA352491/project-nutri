<script setup lang="ts">
import { watch, ref } from 'vue'

const props = defineProps<{
 title: string
 macros: string
 statusType?: 'success' | 'warning' | 'danger'
 statusText?: string
 isLogged?: boolean
}>()

const emit = defineEmits<{
 (e: 'log'): void
 (e: 'unlog'): void
 (e: 'toggle', state: boolean): void
 (e: 'swap'): void
}>()

const logged = ref(props.isLogged ?? false)

watch(() => props.isLogged, (newVal) => {
 if (newVal !== undefined) {
 logged.value = newVal
 }
})

function handleToggle(e: Event) {
 e.stopPropagation()
 logged.value = !logged.value
 if (logged.value) {
 emit('log')
 } else {
 emit('unlog')
 }
 emit('toggle', logged.value)
}

function handleSwap(e: Event) {
 e.stopPropagation()
 emit('swap')
}
</script>

<template>
 <div class="bg-canvas-raised rounded-md shadow-card flex gap-3 p-3 mb-3 items-center animate-[card-in_260ms_var(--ease-out)_both]">
 <div class="w-[52px] h-[52px] rounded-sm shrink-0 bg-primary-soft overflow-hidden">
 <slot name="thumbnail"></slot>
 </div>
 
 <div class="flex-1 min-w-0">
 <div class="font-semibold text-[0.92rem] mb-[2px] flex flex-wrap gap-2 items-center">
 {{ title }}
 <span 
 v-if="statusText" 
 class="font-data text-[0.68rem] px-[7px] py-[2px] rounded-full font-semibold whitespace-nowrap animate-[chip-fade_180ms_var(--ease-out)_both]"
 :class="{
 'bg-success-soft text-success': statusType === 'success',
 'bg-warning-soft text-warning': statusType === 'warning',
 'bg-danger-soft text-danger': statusType === 'danger'
 }"
 >
 {{ statusText }}
 </span>
 </div>
 <div class="font-data text-[0.72rem] text-ink-muted tabular-nums truncate">
 {{ macros }}
 </div>
 </div>
 
 <div class="flex items-center gap-2 shrink-0">
   <!-- Swap Button -->
   <button
     class="swap-btn"
     @click="handleSwap"
     type="button"
     title="Swap with equivalent regional dish"
     aria-label="Swap meal"
   >
     <!-- Refresh/swap arrows icon -->
     <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
       <polyline points="1 4 1 10 7 10"/>
       <polyline points="23 20 23 14 17 14"/>
       <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
     </svg>
     <span>Swap</span>
   </button>

   <!-- Log / Logged Button -->
   <button 
     class="log-btn shrink-0 inline-flex items-center gap-1.5"
     :class="{ 'done': logged }"
     :aria-label="logged ? `Unlog ${title}` : `Log ${title}`"
     :aria-pressed="logged"
     @click="handleToggle"
     type="button"
   >
     <!-- Checkmark icon (visible when logged) -->
     <svg
       v-if="logged"
       class="check-icon"
       width="12" height="12"
       viewBox="0 0 24 24"
       fill="none"
       stroke="currentColor"
       stroke-width="3"
       stroke-linecap="round"
       stroke-linejoin="round"
       aria-hidden="true"
     >
       <polyline points="20 6 9 17 4 12"/>
     </svg>
     <!-- Plus icon (visible when not logged) -->
     <svg
       v-else
       width="12" height="12"
       viewBox="0 0 24 24"
       fill="none"
       stroke="currentColor"
       stroke-width="2.5"
       stroke-linecap="round"
       stroke-linejoin="round"
       aria-hidden="true"
     >
       <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
     </svg>
     <span>{{ logged ? 'Logged' : 'Log' }}</span>
   </button>
 </div>
 </div>
</template>

<style scoped>
@keyframes card-in {
 from { opacity: 0; transform: translateY(6px); }
 to { opacity: 1; transform: translateY(0); }
}

@keyframes chip-fade {
 from { opacity: 0; }
 to { opacity: 1; }
}

@keyframes check-pop {
 from { opacity: 0; transform: scale(0.5); }
 to { opacity: 1; transform: scale(1); }
}

/* Swap Button */
.swap-btn {
 font-family: var(--font-body);
 font-weight: 600;
 font-size: 0.72rem;
 display: inline-flex;
 align-items: center;
 gap: 4px;
 color: var(--color-ink-muted);
 background: transparent;
 border: 1px solid var(--color-border);
 padding: 5px 10px;
 border-radius: var(--radius-pill);
 cursor: pointer;
 transition:
   color var(--dur-fast) var(--ease-standard),
   background var(--dur-fast) var(--ease-standard),
   border-color var(--dur-fast) var(--ease-standard);
}

.swap-btn:hover {
 color: var(--color-primary);
 background: var(--color-primary-soft);
 border-color: var(--color-primary);
}

/* Log Button */
.log-btn {
 font-family: var(--font-body);
 font-weight: 600;
 font-size: 0.75rem;
 border: 1.5px solid var(--color-primary);
 color: var(--color-primary);
 background: transparent;
 padding: 5px 12px;
 border-radius: var(--radius-pill);
 cursor: pointer;
 transition:
   background var(--dur-fast) var(--ease-standard), 
   color var(--dur-fast) var(--ease-standard),
   border-color var(--dur-fast) var(--ease-standard), 
   transform var(--dur-instant) var(--ease-standard);
}

.log-btn:hover:not(.done) {
 background: var(--color-primary-soft);
}

.log-btn:active {
 transform: scale(0.96);
}

.log-btn.done {
 background: var(--color-primary);
 color: white;
 border-color: var(--color-primary);
}

.check-icon {
 animation: check-pop var(--dur-fast) var(--ease-spring) both;
}
</style>
