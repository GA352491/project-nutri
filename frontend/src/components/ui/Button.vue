<script setup lang="ts">
const props = withDefaults(defineProps<{
 variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost'
 size?: 'sm' | 'md' | 'lg'
 disabled?: boolean
 loading?: boolean
 type?: 'button' | 'submit' | 'reset'
}>(), {
 variant: 'primary',
 size: 'md',
 disabled: false,
 loading: false,
 type: 'button'
})

const emit = defineEmits<{
 (e: 'click', event: MouseEvent): void
}>()
</script>

<template>
 <button
 :type="type"
 :disabled="disabled || loading"
 :aria-disabled="disabled || loading"
 :aria-busy="loading"
 class="inline-flex items-center justify-center gap-2 font-body font-semibold rounded-full cursor-pointer transition-all duration-[180ms] ease-[var(--ease-standard)] active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed select-none"
 :class="[
 // Variants
 variant === 'primary' && 'bg-primary text-white border-transparent hover:bg-primary-strong',
 variant === 'secondary' && 'bg-secondary text-ink border-transparent hover:brightness-95',
 variant === 'outline' && 'bg-transparent text-primary border border-primary hover:bg-primary-soft',
 variant === 'danger' && 'bg-danger text-white border-transparent hover:brightness-90',
 variant === 'ghost' && 'bg-transparent text-ink-muted border border-border hover:bg-canvas hover:text-ink',
 // Sizes
 size === 'sm' && 'text-[0.76rem] px-3 py-[5px]',
 size === 'md' && 'text-[0.88rem] px-5 py-[10px]',
 size === 'lg' && 'text-[1rem] px-6 py-3',
 ]"
 @click="emit('click', $event)"
 >
 <svg v-if="loading" class="animate-spin w-4 h-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
 <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
 <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
 </svg>
 <slot />
 </button>
</template>
