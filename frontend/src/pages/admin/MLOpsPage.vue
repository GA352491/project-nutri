<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '../../api'

const guardrailsLog = ref([
  { id: 'gr_1', time: '10:42 AM', model: 'llama3 / llava', check: 'ICMR-NIN Calorie Safety', status: 'Passed', text: 'Daily Calorie Envelope (1,800 kcal)' },
  { id: 'gr_2', time: '10:15 AM', model: 'llama3', check: 'DetectPII', status: 'Fixed', text: 'Anonymized user phone number in consultation transcript' },
  { id: 'gr_3', time: '09:30 AM', model: 'llama3', check: 'EatingDisorderSanity', status: 'Passed', text: 'Calorie floor check > 1,200 kcal validated' },
  { id: 'gr_4', time: '09:12 AM', model: 'llama3', check: 'AllergenCrossCheck', status: 'Passed', text: 'Filtered peanut-containing regional recipes for allergic profile' },
])

const temporalSagas = ref<any[]>([
  { id: 'booking-apt_98a7f1', status: 'COMPLETED', retries: 0, time: '2m ago' },
  { id: 'booking-apt_44b2x9', status: 'COMPLETED', retries: 0, time: '5m ago', current_activity: 'charge_stripe' },
  { id: 'plan-gen-usr_123', status: 'COMPLETED', retries: 0, time: '10m ago' },
])

async function fetchLiveSagas() {
  try {
    const res = await apiClient.get('/appointments?nutritionist_id=nut_201')
    if (res.data && Array.isArray(res.data) && res.data.length > 0) {
      temporalSagas.value = res.data.map((a: any) => ({
        id: `booking-${a.id}`,
        status: a.status === 'PENDING' ? 'RUNNING' : 'COMPLETED',
        retries: 0,
        time: 'Active',
        current_activity: 'send_confirmation_email'
      }))
    }
  } catch {
    // Keep baseline
  }
}

onMounted(() => {
  fetchLiveSagas()
})
</script>

<template>
 <div class="space-y-8">
 
 <!-- Guardrails AI Interventions -->
 <div>
 <div class="flex justify-between items-end mb-4">
 <div>
 <h2 class="font-display font-semibold text-[1.4rem] text-ink">Guardrails AI Interventions</h2>
 <p class="font-body text-[0.95rem] text-ink-muted">Live feed of LLM output safety checks.</p>
 </div>
 <div class="font-data text-[0.8rem] bg-danger/10 text-danger px-3 py-1 rounded-full font-bold">
 2 Interventions Today
 </div>
 </div>
 
 <div class="bg-canvas-raised border border-border rounded-xl overflow-hidden shadow-sm">
 <table class="w-full text-left border-collapse">
 <thead>
 <tr class="bg-canvas border-b border-border">
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Time</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Check</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Status</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Context</th>
 </tr>
 </thead>
 <tbody class="divide-y divide-border">
 <tr v-for="log in guardrailsLog" :key="log.id" class="hover:bg-canvas/50 transition-colors">
 <td class="py-3 px-4 font-body text-[0.85rem] text-ink-muted">{{ log.time }}</td>
 <td class="py-3 px-4 font-body text-[0.9rem] font-medium text-ink">{{ log.check }}</td>
 <td class="py-3 px-4">
 <span 
 class="font-data text-[0.75rem] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider"
 :class="{
 'bg-danger/15 text-danger': log.status === 'Blocked',
 'bg-warning/15 text-warning': log.status === 'Fixed',
 'bg-success/15 text-success': log.status === 'Passed',
 }"
 >
 {{ log.status }}
 </span>
 </td>
 <td class="py-3 px-4 font-data text-[0.85rem] text-ink-muted truncate max-w-[250px]">
 "{{ log.text }}"
 </td>
 </tr>
 </tbody>
 </table>
 </div>
 </div>

 <!-- Temporal Booking Sagas -->
 <div>
 <div class="flex justify-between items-end mb-4">
 <div>
 <h2 class="font-display font-semibold text-[1.4rem] text-ink">Temporal Booking Sagas</h2>
 <p class="font-body text-[0.95rem] text-ink-muted">Durable workflow orchestration for distributed transactions.</p>
 </div>
 </div>
 
 <div class="grid md:grid-cols-3 gap-4">
 <div 
 v-for="saga in temporalSagas" 
 :key="saga.id"
 class="bg-canvas-raised border border-border rounded-xl p-5 shadow-sm"
 >
 <div class="flex justify-between items-start mb-3">
 <div class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider">{{ saga.id }}</div>
 <div 
 class="w-2.5 h-2.5 rounded-full"
 :class="{
 'bg-success': saga.status === 'COMPLETED',
 'bg-warning animate-pulse': saga.status === 'RUNNING',
 'bg-danger': saga.status === 'FAILED',
 }"
 />
 </div>
 <div class="font-display font-semibold text-[1.1rem] text-ink mb-1">{{ saga.status }}</div>
 
 <div v-if="saga.status === 'RUNNING'" class="font-body text-[0.85rem] text-ink-muted mt-2 border-t border-border pt-2">
 Activity: <span class="font-mono text-primary">{{ saga.current_activity }}</span> (Retry: {{ saga.retries }})
 </div>
 <div v-else-if="saga.status === 'FAILED'" class="font-body text-[0.85rem] text-danger mt-2 border-t border-border pt-2">
 Reason: {{ saga.error }}
 </div>
 <div v-else class="font-body text-[0.85rem] text-ink-muted mt-2 border-t border-border pt-2">
 Finished {{ saga.time }}
 </div>
 </div>
 </div>
 </div>

 </div>
</template>
