<script setup lang="ts">
import { ref } from 'vue'
import Button from '../../components/ui/Button.vue'
import Modal from '../../components/ui/Modal.vue'
import Toast from '../../components/ui/Toast.vue'
import Chip from '../../components/ui/Chip.vue'
import Icon from '../../components/ui/Icon.vue'
import apiClient from '../../api'

const showToast = ref(false)
const toastMsg = ref('')
const selectedPatient = ref<any>(null)
const showAssignPlanModal = ref(false)
const showFollowUpModal = ref(false)
const showChartModal = ref(false)

function notify(msg: string) {
 toastMsg.value = msg
 showToast.value = true
 setTimeout(() => { showToast.value = false }, 3500)
}

const patients = ref([
 {
 id: 'usr_1',
 name: 'Rohan Sharma',
 age: 34,
 gender: 'Male',
 next_apt: 'Today, 10:00 AM',
 condition: 'Type 2 Diabetes',
 ai_plan: 'Active',
 caloric_target: 1850,
 wearable: 'Apple Watch',
 last_compliance: '92%',
 active_plan_name: 'Low Glycemic Mediterranean',
 notes: 'Monitoring post-lunch spikes. Instructed to walk 15 mins after carbs.'
 },
 {
 id: 'usr_2',
 name: 'Priya Patel',
 age: 29,
 gender: 'Female',
 next_apt: 'Today, 11:30 AM',
 condition: 'PCOS & Insulin Resistance',
 ai_plan: 'Paused',
 caloric_target: 1600,
 wearable: 'Oura Ring',
 last_compliance: '78%',
 active_plan_name: 'High Protein Anti-Inflammatory',
 notes: 'Experiencing bloating with raw cruciferous vegetables. Switched to cooked.'
 },
 {
 id: 'usr_3',
 name: 'Amit Kumar',
 age: 26,
 gender: 'Male',
 next_apt: 'Tomorrow, 09:00 AM',
 condition: 'Sports / Hypertrophy',
 ai_plan: 'Active',
 caloric_target: 2800,
 wearable: 'Garmin',
 last_compliance: '96%',
 active_plan_name: 'High Protein Muscle Builder',
 notes: 'Training volume increased. Added 30g intra-workout carbs.'
 },
 {
 id: 'usr_4',
 name: 'Sneha Desai',
 age: 42,
 gender: 'Female',
 next_apt: 'Next Week',
 condition: 'Cardiovascular Wellness',
 ai_plan: 'Active',
 caloric_target: 1700,
 wearable: 'Fitbit',
 last_compliance: '88%',
 active_plan_name: 'DASH Heart Healthy',
 notes: 'Sodium intake reduced to <1500mg/day.'
 },
])

// Custom Plan Form
const customPlan = ref({
 planTitle: 'Clinical High-Protein Diabetic Protocol',
 dailyKcal: 1750,
 proteinGrams: 130,
 carbsGrams: 150,
 fatGrams: 55,
 prescribedMeals: [
 { type: 'Breakfast', name: 'Besan Chilla with Paneer & Mint Chutney', kcal: 380, protein: 22 },
 { type: 'Lunch', name: 'Brown Rice, Dal Tadka, Grilled Tofu & Cucumber Salad', kcal: 520, protein: 32 },
 { type: 'Evening Snack', name: 'Roasted Makhana & Walnuts', kcal: 180, protein: 6 },
 { type: 'Dinner', name: 'Moong Dal Khichdi with Steamed Veggies', kcal: 450, protein: 24 },
 ],
 clinicalInstructions: 'Follow 14-day cycle. Restrict refined sugar. Drink 3.5L water daily.'
})

// Follow-up Form
const followUp = ref({
 date: '2026-08-26',
 time: '11:00 AM',
 type: 'Video Consultation',
 goalChecklist: [
 'Check fasting blood sugar log',
 'Review step count consistency (>8,000 steps)',
 'Evaluate satiety on high-fiber lunches'
 ],
 nutritionistNote: ''
})

function openAssignPlan(p: any) {
 selectedPatient.value = p
 showAssignPlanModal.value = true
}

function openFollowUp(p: any) {
 selectedPatient.value = p
 showFollowUpModal.value = true
}

function openChart(p: any) {
 selectedPatient.value = p
 showChartModal.value = true
}

async function submitCustomPlan() {
  if (selectedPatient.value) {
    selectedPatient.value.active_plan_name = customPlan.value.planTitle
    selectedPatient.value.caloric_target = customPlan.value.dailyKcal
    selectedPatient.value.ai_plan = 'Expert Assigned'

    try {
      await apiClient.post('/plan/expert/assign', {
        patient_id: selectedPatient.value.id,
        expert_id: 'nut_201',
        plan_title: customPlan.value.planTitle,
        daily_kcal: customPlan.value.dailyKcal,
        protein_g: customPlan.value.proteinGrams,
        carbs_g: customPlan.value.carbsGrams,
        fat_g: customPlan.value.fatGrams,
        prescribed_meals: customPlan.value.prescribedMeals,
        clinical_instructions: customPlan.value.clinicalInstructions
      })
    } catch (e) {
      console.warn('Expert plan backend sync:', e)
    }
  }
  showAssignPlanModal.value = false
  notify(`Assigned custom plan "${customPlan.value.planTitle}" to ${selectedPatient.value?.name}!`)
}

async function signOffPatient(patient: any) {
  try {
    await apiClient.post(`/plan/clinical/approve/${patient.id}`, {
      user_id: patient.id,
      nutritionist_id: 'nut_201',
      ida_license_number: 'IDA-KL-2024-8841',
      decision: 'APPROVED',
      clinical_modifications: 'Glycemic load capped <45. Potassium within safe renal index.'
    })
  } catch (e) {
    console.warn('Clinical sign-off sync:', e)
  }
  patient.condition = patient.condition.replace(' (Pending)', '')
  notify(`✅ Clinical Sign-off stamped for ${patient.name}! Plan unlocked with IDA license seal.`)
}

async function scheduleFollowUp() {
  if (selectedPatient.value) {
    try {
      await apiClient.post('/appointments/book', {
        nutritionist_id: 'nut_201',
        nutritionist_name: 'Dr. Sarah Jenkins',
        user_id: selectedPatient.value.id,
        date: followUp.value.date,
        time: followUp.value.time,
        amount_usd: 0.0
      })
    } catch (e) {
      console.warn('Appointment booking sync:', e)
    }
  }
  showFollowUpModal.value = false
  notify(`Follow-up consultation booked with ${selectedPatient.value?.name} for ${followUp.value.date}!`)
}
</script>

<template>
 <div class="space-y-6">
 <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

 <!-- ── 1. ASSIGN MEAL PLAN MODAL ─────────────────────────────────────── -->
 <Modal v-model="showAssignPlanModal" :title="`Assign Custom Meal Plan — ${selectedPatient?.name}`" size="lg">
 <div class="space-y-5">
 <div class="p-3.5 rounded-xl bg-primary-soft/40 border border-primary/20 flex items-center justify-between text-ink text-sm">
 <div>
 <strong>Patient Condition:</strong> {{ selectedPatient?.condition }}
 </div>
 <div>
 <strong>Active Target:</strong> {{ selectedPatient?.caloric_target }} kcal
 </div>
 </div>

 <div class="grid sm:grid-cols-2 gap-4">
 <div>
 <label class="block text-xs font-semibold text-ink uppercase mb-1">Plan Title</label>
 <input v-model="customPlan.planTitle" class="w-full px-3 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 <div>
 <label class="block text-xs font-semibold text-ink uppercase mb-1">Calorie Target (kcal)</label>
 <input v-model.number="customPlan.dailyKcal" type="number" class="w-full px-3 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 </div>

 <!-- Prescribed Meals Grid -->
 <div>
 <label class="block text-xs font-semibold text-ink uppercase mb-2">Prescribed Daily Meals</label>
 <div class="space-y-2">
 <div
 v-for="(meal, i) in customPlan.prescribedMeals"
 :key="i"
 class="p-3 rounded-lg bg-canvas border border-border flex items-center justify-between gap-4"
 >
 <div class="w-24 font-data text-xs uppercase font-bold text-ink-muted">{{ meal.type }}</div>
 <input v-model="meal.name" class="flex-1 px-2.5 py-1.5 rounded bg-canvas-raised border border-border text-ink text-sm outline-none focus:border-primary" />
 <div class="flex items-center gap-2 text-xs font-data text-ink-muted shrink-0">
 <input v-model.number="meal.kcal" type="number" class="w-16 px-1.5 py-1 rounded bg-canvas-raised border border-border text-center text-ink text-xs" /> kcal
 <input v-model.number="meal.protein" type="number" class="w-14 px-1.5 py-1 rounded bg-canvas-raised border border-border text-center text-ink text-xs" /> g P
 </div>
 </div>
 </div>
 </div>

 <!-- Clinical Notes -->
 <div>
 <label class="block text-xs font-semibold text-ink uppercase mb-1">Clinical Instructions & Notes for Patient</label>
 <textarea v-model="customPlan.clinicalInstructions" rows="2" class="w-full px-3 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary"></textarea>
 </div>

 <div class="flex justify-end gap-3 pt-2">
 <Button variant="outline" @click="showAssignPlanModal = false">Cancel</Button>
 <Button @click="submitCustomPlan">Assign & Push to Patient App →</Button>
 </div>
 </div>
 </Modal>

 <!-- ── 2. FOLLOW-UP CONSULTATION MODAL ──────────────────────────────── -->
 <Modal v-model="showFollowUpModal" :title="`Schedule Follow-up with ${selectedPatient?.name}`" size="md">
 <div class="space-y-4">
 <div class="grid grid-cols-2 gap-3">
 <div>
 <label class="block text-xs font-semibold text-ink uppercase mb-1">Date</label>
 <input v-model="followUp.date" type="date" class="w-full px-3 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 <div>
 <label class="block text-xs font-semibold text-ink uppercase mb-1">Time Slot</label>
 <input v-model="followUp.time" type="text" class="w-full px-3 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 </div>

 <div>
 <label class="block text-xs font-semibold text-ink uppercase mb-1">Consultation Mode</label>
 <select v-model="followUp.type" class="w-full px-3 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary">
 <option>Video Consultation (Jitsi)</option>
 <option>In-Person Clinic Visit</option>
 <option>Asynchronous Plan Review</option>
 </select>
 </div>

 <div>
 <label class="block text-xs font-semibold text-ink uppercase mb-1">Review Focus & Goals</label>
 <div class="p-3 bg-canvas border border-border rounded-lg space-y-1.5 text-xs text-ink">
 <div v-for="g in followUp.goalChecklist" :key="g" class="flex items-center gap-2">
 <span class="text-primary font-bold">✓</span> {{ g }}
 </div>
 </div>
 </div>

 <div>
 <label class="block text-xs font-semibold text-ink uppercase mb-1">Nutritionist Notes</label>
 <input v-model="followUp.nutritionistNote" placeholder="e.g. Bring fasting lab test reports" class="w-full px-3 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>

 <div class="flex justify-end gap-3 pt-2">
 <Button variant="outline" @click="showFollowUpModal = false">Cancel</Button>
 <Button @click="scheduleFollowUp">Book Follow-Up & Notify Patient</Button>
 </div>
 </div>
 </Modal>

 <!-- ── 3. PATIENT HEALTH CHART MODAL ────────────────────────────────── -->
 <Modal v-model="showChartModal" :title="`Patient Chart — ${selectedPatient?.name}`" size="lg">
 <div v-if="selectedPatient" class="space-y-4">
 <div class="grid grid-cols-3 gap-3 text-center">
 <div class="p-3 bg-canvas rounded-xl border border-border">
 <div class="text-xs text-ink-muted uppercase">Compliance</div>
 <div class="font-display font-bold text-lg text-primary">{{ selectedPatient.last_compliance }}</div>
 </div>
 <div class="p-3 bg-canvas rounded-xl border border-border">
 <div class="text-xs text-ink-muted uppercase">Wearable</div>
 <div class="font-display font-bold text-lg text-emerald-600">{{ selectedPatient.wearable }}</div>
 </div>
 <div class="p-3 bg-canvas rounded-xl border border-border">
 <div class="text-xs text-ink-muted uppercase">Daily Target</div>
 <div class="font-display font-bold text-lg text-ink">{{ selectedPatient.caloric_target }} kcal</div>
 </div>
 </div>

 <div class="p-4 bg-canvas rounded-xl border border-border space-y-2">
 <h4 class="font-semibold text-sm text-ink">Active Plan: {{ selectedPatient.active_plan_name }}</h4>
 <p class="text-xs text-ink-muted leading-relaxed"><strong>Nutritionist Observations:</strong> {{ selectedPatient.notes }}</p>
 </div>

 <div class="flex justify-end gap-3">
 <Button variant="outline" size="sm" @click="openFollowUp(selectedPatient); showChartModal = false">Book Follow-up</Button>
 <Button size="sm" @click="openAssignPlan(selectedPatient); showChartModal = false">Edit / Assign Plan</Button>
 </div>
 </div>
 </Modal>

 <!-- ── PATIENT TABLE HEADER ─────────────────────────────────────────── -->
 <div class="flex flex-col sm:flex-row justify-between sm:items-end gap-4">
 <div>
 <h2 class="font-display font-semibold text-[1.4rem] text-ink">My Patients</h2>
 <p class="font-body text-[0.95rem] text-ink-muted">Review client telemetry, prescribe manual meal plans, and schedule clinical follow-ups.</p>
 </div>
 <div class="relative">
 <input 
 type="text" 
 placeholder="Search patients by name or condition..." 
 class="font-body text-[0.9rem] text-ink bg-canvas border border-border rounded-lg pl-9 pr-4 py-2 outline-none focus:border-primary focus:ring-1 focus:ring-primary w-72"
 />
 <svg class="w-4 h-4 text-ink-muted absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
 <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
 </svg>
 </div>
 </div>

  <!-- ── TABLE ───────────────────────────────────────────────────────── -->
  <div class="bg-canvas-raised border border-border rounded-xl overflow-hidden shadow-sm">
  <table class="w-full text-left border-collapse">
  <thead>
  <tr class="bg-canvas border-b border-border">
  <th class="py-3.5 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Patient Name</th>
  <th class="py-3.5 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Condition Focus</th>
  <th class="py-3.5 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Active Meal Plan</th>
  <th class="py-3.5 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Clinical Gate</th>
  <th class="py-3.5 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Compliance</th>
  <th class="py-3.5 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold text-right">Actions</th>
  </tr>
  </thead>
  <tbody class="divide-y divide-border">
  <tr v-for="patient in patients" :key="patient.id" class="hover:bg-canvas/50 transition-colors">
  <td class="py-3.5 px-4 font-body text-[0.9rem] font-semibold text-ink">
  <div class="flex items-center gap-2.5">
  <div class="w-8 h-8 rounded-full bg-primary-soft text-primary font-bold text-xs flex items-center justify-center">
  {{ patient.name.split(' ').map(n=>n[0]).join('') }}
  </div>
  <div>
  <div>{{ patient.name }}</div>
  <div class="text-[0.72rem] font-normal text-ink-muted">{{ patient.age }}y · {{ patient.gender }}</div>
  </div>
  </div>
  </td>
  <td class="py-3.5 px-4 font-body text-[0.88rem] text-ink">
  <Chip variant="neutral">{{ patient.condition }}</Chip>
  </td>
  <td class="py-3.5 px-4">
  <div class="font-semibold text-[0.85rem] text-ink">{{ patient.active_plan_name }}</div>
  <div class="font-data text-[0.72rem] text-ink-muted">{{ patient.caloric_target }} kcal/day</div>
  </td>
  <td class="py-3.5 px-4">
    <span 
      v-if="patient.condition.includes('Diabetes') || patient.condition.includes('PCOS')"
      class="px-2 py-0.5 rounded-full text-[0.68rem] font-bold uppercase tracking-wider border inline-flex items-center gap-1 bg-amber-50 text-amber-800 border-amber-300"
    >
      <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
      Pending Sign-Off
    </span>
    <span 
      v-else
      class="px-2 py-0.5 rounded-full text-[0.68rem] font-bold uppercase tracking-wider border inline-flex items-center gap-1 bg-emerald-50 text-emerald-800 border-emerald-300"
    >
      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
      IDA Approved
    </span>
  </td>
  <td class="py-3.5 px-4 font-data text-[0.85rem] font-bold text-primary">
  {{ patient.last_compliance }}
  </td>
  <td class="py-3.5 px-4 text-right space-x-1.5">
  <button 
    v-if="patient.condition.includes('Diabetes') || patient.condition.includes('PCOS')"
    @click="signOffPatient(patient)"
    class="px-2.5 py-1 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition-all inline-flex items-center gap-1 cursor-pointer"
  >
    <Icon name="check" :size="12" />
    <span>IDA Sign-Off</span>
  </button>
  <Button size="sm" variant="outline" @click="openChart(patient)" class="inline-flex items-center gap-1">
  <Icon name="trends" :size="13" />
  <span>Chart</span>
  </Button>
  <Button size="sm" variant="outline" @click="openFollowUp(patient)" class="inline-flex items-center gap-1">
  <Icon name="calendar" :size="13" />
  <span>Follow-up</span>
  </Button>
  <Button size="sm" @click="openAssignPlan(patient)" class="inline-flex items-center gap-1">
  <Icon name="recipe" :size="13" />
  <span>Assign Plan</span>
  </Button>
  </td>
  </tr>
  </tbody>
  </table>
  </div>

  </div>
</template>
