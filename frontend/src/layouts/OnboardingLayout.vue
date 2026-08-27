<script setup lang="ts">
const props = withDefaults(defineProps<{
 currentStep: number
 totalSteps: number
 stepLabel?: string
}>(), {})
</script>

<template>
 <div class="min-h-screen bg-canvas flex flex-col">
 <!-- Top progress bar + brand -->
 <header class="sticky top-0 z-10 bg-canvas-raised border-b border-border px-4 md:px-8 py-4">
 <div class="max-w-xl mx-auto flex items-center gap-4">
 <!-- Brand -->
 <div class="w-8 h-8 rounded-md bg-primary flex items-center justify-center text-white font-display font-bold text-[0.9rem] shrink-0">N</div>

 <!-- Step progress -->
 <div class="flex-1">
 <div class="flex justify-between items-center mb-1.5">
 <span class="font-data text-[0.72rem] text-ink-muted uppercase tracking-[0.08em]">
 {{ stepLabel || `Step ${currentStep} of ${totalSteps}` }}
 </span>
 <span class="font-data text-[0.72rem] text-primary font-semibold">
 {{ Math.round((currentStep / totalSteps) * 100) }}%
 </span>
 </div>
 <!-- Progress track -->
 <div class="h-1.5 bg-border rounded-full overflow-hidden">
 <div
 class="h-full bg-primary rounded-full transition-all duration-[400ms] ease-[var(--ease-out)]"
 :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
 />
 </div>
 </div>
 </div>
 </header>

 <!-- Wizard content -->
 <main class="flex-1 flex flex-col items-center px-4 py-10">
 <div class="w-full max-w-xl">
 <!-- Step slide transition -->
 <Transition name="step-slide" mode="out-in">
 <div :key="currentStep">
 <slot />
 </div>
 </Transition>
 </div>
 </main>

 <!-- Nav buttons -->
 <footer class="sticky bottom-0 bg-canvas-raised border-t border-border px-4 md:px-8 py-4">
 <div class="max-w-xl mx-auto flex justify-between items-center gap-4">
 <slot name="nav-back" />
 <slot name="nav-next" />
 </div>
 </footer>
 </div>
</template>

<style scoped>
.step-slide-enter-active,
.step-slide-leave-active {
 transition: opacity 220ms var(--ease-out), transform 220ms var(--ease-out);
}
.step-slide-enter-from {
 opacity: 0;
 transform: translateX(16px);
}
.step-slide-leave-to {
 opacity: 0;
 transform: translateX(-16px);
}
</style>
