<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
 label?: string
 placeholder?: string
 type?: string
 modelValue?: string
 error?: string
 hint?: string
 required?: boolean
 disabled?: boolean
 id?: string
}>(), {
 type: 'text',
 required: false,
 disabled: false
})

// WCAG 2.1 SC 1.3.1: label must always be programmatically linked to its input.
// Generate a stable fallback id when the consumer doesn't provide one.
const inputId = computed(() => props.id ?? `input-${Math.random().toString(36).slice(2, 8)}`)

const emit = defineEmits<{
 (e: 'update:modelValue', value: string): void
}>()
</script>

<template>
 <div class="flex flex-col gap-1">
 <label
 v-if="label"
 :for="inputId"
 class="font-body text-[0.82rem] font-semibold text-ink"
 >
 {{ label }}
 <span v-if="required" class="text-danger ml-0.5" aria-hidden="true">*</span>
 </label>

 <input
 :id="inputId"
 :type="type"
 :value="modelValue"
 :placeholder="placeholder"
 :required="required"
 :disabled="disabled"
 class="font-body text-[0.88rem] text-ink bg-canvas-raised border rounded-md px-3 py-[10px] w-full outline-none transition-all duration-[180ms] ease-[var(--ease-standard)] placeholder:text-ink-muted/60 disabled:opacity-50 disabled:cursor-not-allowed"
 :class="[
 error
 ? 'border-danger focus:ring-2 focus:ring-danger/20'
 : 'border-border focus:border-primary focus:ring-2 focus:ring-primary/15'
 ]"
 @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
 />

 <p v-if="error" class="text-[0.76rem] text-danger font-body" role="alert">{{ error }}</p>
 <p v-else-if="hint" class="text-[0.76rem] text-ink-muted font-body">{{ hint }}</p>
 </div>
</template>
