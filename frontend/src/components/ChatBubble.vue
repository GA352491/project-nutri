<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
 senderType: 'ai' | 'human' | 'user'
 senderName?: string
 message: string
}>()

const isRightAligned = computed(() => props.senderType === 'user')
</script>

<template>
 <div class="flex mb-3" :class="{ 'justify-end': isRightAligned }">
 <div 
 class="max-w-[78%] px-4 py-3 text-[0.88rem]"
 :class="{
 'bg-info-soft rounded-lg rounded-bl-sm': senderType === 'ai',
 'bg-secondary-soft rounded-lg rounded-bl-sm': senderType === 'human',
 'bg-primary text-white rounded-lg rounded-br-sm': senderType === 'user'
 }"
 >
 <div 
 v-if="senderName && senderType !== 'user'" 
 class="font-data text-[0.66rem] uppercase tracking-[0.08em] mb-[3px]"
 :class="{
 'text-info': senderType === 'ai',
 'text-[#96650f]': senderType === 'human'
 }"
 >
 {{ senderName }}
 </div>
 {{ message }}
 </div>
 </div>
</template>
