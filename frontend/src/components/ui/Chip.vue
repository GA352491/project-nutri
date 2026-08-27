<script setup lang="ts">
withDefaults(defineProps<{
 variant?: 'success' | 'warning' | 'danger' | 'info' | 'primary' | 'neutral'
}>(), {
 variant: 'neutral'
})
</script>

<template>
 <span
 class="font-data text-[0.68rem] font-semibold px-[7px] py-[2px] rounded-full whitespace-nowrap inline-flex items-center gap-1 animate-[chip-fade_180ms_var(--ease-out)_both]"
 :class="{
 'bg-success-soft text-success': variant === 'success',
 'bg-warning-soft text-warning': variant === 'warning',
 'bg-danger-soft text-danger': variant === 'danger',
 'bg-info-soft text-info': variant === 'info',
 'bg-primary-soft text-primary': variant === 'primary',
 'bg-canvas text-ink-muted border border-border': variant === 'neutral',
 }"
 >
 <slot />
 </span>
</template>

<style scoped>
@keyframes chip-fade {
 from { opacity: 0; }
 to { opacity: 1; }
}
</style>
