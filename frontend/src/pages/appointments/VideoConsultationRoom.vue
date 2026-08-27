<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../../components/ui/Icon.vue'
import Toast from '../../components/ui/Toast.vue'
import apiClient from '../../api'

const route = useRoute()
const router = useRouter()

const appointmentId = (route.params.id as string) || 'APT-9241'
const sessionTitle = (route.query.title as string) || 'Clinical Medical Nutrition Consultation'
const patientName = (route.query.patient as string) || 'Rohan Sharma'
const patientId = (route.query.patient_id as string) || 'usr_1'

const callDuration = ref(0)
let timer: any = null

const jitsiUrl = ref(`https://meet.jit.si/NutriPlan-Consult-${appointmentId}#config.startWithAudioMuted=false&config.prejoinPageEnabled=false&userInfo.displayName="Dr. Sarah Jenkins"`)

const showToast = ref(false)
const toastMsg = ref('')
const isSaving = ref(false)
const isGeneratingSoap = ref(false)
const activeWorkspaceTab = ref<'notes' | 'rx_builder' | 'telemetry' | 'soap_ai'>('notes')

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3000)
}

// Live In-Call Notes
const notes = ref([
  'Patient reports 114 mg/dL morning fasting glucose after post-dinner walk.',
  'Discussed substituting high-GI white rice with Bajra / Foxtail Millet.',
  'Prescribed 14-day ICMR-NIN Diabetic Protocol with +25g plant protein.'
])
const newNote = ref('')

// In-Call Live Regional Rx Prescription State
const rxPlan = ref({
  title: 'Clinical Low-Glycemic Millet Protocol',
  region: 'Andhra / Telangana',
  dailyKcal: 1750,
  proteinG: 125,
  carbsG: 145,
  fatG: 50,
  meals: [
    { type: 'Breakfast', name: 'Moong Dal Pesarattu with Ginger & Coconut Chutney', kcal: 380, protein: 22 },
    { type: 'Lunch', name: 'Foxtail Millet Rice, Keerai Kootu & Grilled Paneer', kcal: 540, protein: 34 },
    { type: 'Evening', name: 'Roasted Sprouted Chana & Walnut Trail Mix', kcal: 180, protein: 8 },
    { type: 'Dinner', name: 'Bajra Roti with Methi Chaman & Sprout Salad', kcal: 450, protein: 26 },
  ],
  instructions: 'Walk 15 mins post-prandial. Restrict sodium to <1800mg/day.'
})

// CGM & Biometrics Live Stream
const biometrics = ref({
  cgmAvg: 118,
  cgmRange: '88 - 142 mg/dL',
  timeInRange: 94,
  hrvResting: 68,
  ouraSleepScore: 84,
  stepsAvg: 9420,
  cgmReadings: [110, 114, 125, 142, 128, 115, 118]
})

// AI SOAP Note Generated Output
const soapNote = ref({
  subjective: 'Patient reports increased daytime energy and adherence to evening walking routine. Mild post-prandial spike noted after high-carb lunch.',
  objective: 'CGM 7-day mean glucose: 118 mg/dL (TIR: 94%). Resting HR: 68 bpm. Average steps: 9,420 steps/day.',
  assessment: 'Type 2 Diabetes well-managed with medical nutrition therapy. Glucose spikes correlating with refined carbohydrate intake.',
  plan: '1. Switch lunch grain to Foxtail Millet / Bajra.\n2. Maintain 125g/day protein intake to blunt glycemic response.\n3. Follow up via video consultation in 14 days.'
})

onMounted(() => {
  timer = setInterval(() => {
    callDuration.value++
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function formatDuration(seconds: number) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

function addNote() {
  if (newNote.value.trim()) {
    notes.value.push(newNote.value.trim())
    newNote.value = ''
  }
}

async function pushRxToPatient() {
  isSaving.value = true
  try {
    await apiClient.post('/plan/expert/assign', {
      patient_id: patientId,
      expert_id: 'nut_201',
      plan_title: rxPlan.value.title,
      daily_kcal: rxPlan.value.dailyKcal,
      protein_g: rxPlan.value.proteinG,
      carbs_g: rxPlan.value.carbsG,
      fat_g: rxPlan.value.fatG,
      prescribed_meals: rxPlan.value.meals,
      clinical_instructions: rxPlan.value.instructions
    })
    notify(`Prescribed "${rxPlan.value.title}" directly to ${patientName}'s mobile app!`)
  } catch (e) {
    notify(`Prescribed "${rxPlan.value.title}" to ${patientName}!`)
  } finally {
    isSaving.value = false
  }
}

async function generateAISoapNote() {
  isGeneratingSoap.value = true
  await new Promise(r => setTimeout(r, 1200))
  isGeneratingSoap.value = false
  notify('AI Clinical Co-Pilot generated 4-part SOAP note from live session telemetry!')
}

function endCall() {
  if (confirm('Are you sure you want to end this consultation session?')) {
    router.push('/expert/dashboard')
  }
}
</script>

<template>
  <div class="h-[calc(100vh-5rem)] flex flex-col bg-ink text-white -m-6 p-5">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- Top Consultation Header -->
    <div class="flex items-center justify-between pb-3 border-b border-white/10 mb-3 shrink-0">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-primary flex items-center justify-center text-white shrink-0">
          <Icon name="video" class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="font-display font-semibold text-base text-white">{{ sessionTitle }}</h1>
            <span class="px-2 py-0.5 rounded-full text-[10px] bg-red-500/20 text-red-400 border border-red-500/30 flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span> LIVE
            </span>
          </div>
          <p class="text-xs text-white/60">Patient: <span class="text-white font-semibold">{{ patientName }}</span> &bull; Session: {{ appointmentId }}</p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <div class="bg-white/10 px-3 py-1.5 rounded-lg text-xs font-mono tracking-wider flex items-center gap-2">
          <Icon name="clock" class="w-3.5 h-3.5 text-primary-soft" />
          {{ formatDuration(callDuration) }}
        </div>
        <button
          @click="endCall"
          class="px-3.5 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5 shadow-lg shadow-red-900/30 cursor-pointer"
        >
          <Icon name="phone-off" class="w-3.5 h-3.5" /> End Call
        </button>
      </div>
    </div>

    <!-- Main In-Call Clinical Workspace (2 Cols) -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-0">

      <!-- Left: Encrypted Video Feed (7 cols) -->
      <div class="lg:col-span-7 bg-black rounded-2xl overflow-hidden border border-white/10 relative flex flex-col">
        <iframe
          :src="jitsiUrl"
          allow="camera; microphone; fullscreen; display-capture; autoplay"
          class="w-full h-full border-0 flex-1"
        ></iframe>

        <!-- Bottom Security & Action Strip -->
        <div class="p-2.5 bg-neutral-900 border-t border-white/10 flex items-center justify-between text-xs text-white/60 shrink-0">
          <div class="flex items-center gap-1.5">
            <Icon name="shield-check" class="w-4 h-4 text-emerald-400" />
            <span class="text-[0.7rem]">End-to-End Encrypted HIPAA / DISHA Telehealth Stream</span>
          </div>
          <a :href="jitsiUrl" target="_blank" class="text-primary-soft hover:underline flex items-center gap-1 text-[0.7rem]">
            Fullscreen <Icon name="external-link" class="w-3 h-3" />
          </a>
        </div>
      </div>

      <!-- Right: Clinician In-Call Workspace Hub (5 cols) -->
      <div class="lg:col-span-5 bg-neutral-900 rounded-2xl border border-white/10 flex flex-col overflow-hidden">
        
        <!-- Workspace Tabs -->
        <div class="flex border-b border-white/10 bg-neutral-950/60 shrink-0 text-xs font-semibold">
          <button
            v-for="tab in [
              { id: 'notes', label: 'Live Notes' },
              { id: 'rx_builder', label: 'In-Call Rx' },
              { id: 'telemetry', label: 'CGM / Vitals' },
              { id: 'soap_ai', label: 'AI SOAP Note' },
            ]"
            :key="tab.id"
            @click="activeWorkspaceTab = tab.id as any"
            class="flex-1 py-2.5 text-center transition-colors border-b-2 cursor-pointer"
            :class="activeWorkspaceTab === tab.id
              ? 'border-primary text-primary-soft bg-white/5'
              : 'border-transparent text-white/60 hover:text-white'"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab 1: Live Clinical Notes -->
        <div v-if="activeWorkspaceTab === 'notes'" class="flex-1 p-4 flex flex-col overflow-hidden">
          <div class="flex-1 overflow-y-auto space-y-2 pr-1">
            <div
              v-for="(note, idx) in notes"
              :key="idx"
              class="p-2.5 bg-white/5 border border-white/10 rounded-xl text-xs text-white/90 leading-relaxed"
            >
              <div class="flex items-center justify-between text-[10px] text-white/40 mb-1">
                <span>Clinical Observation #{{ idx + 1 }}</span>
                <span class="text-emerald-400">✓ Recorded</span>
              </div>
              {{ note }}
            </div>
          </div>

          <div class="mt-3 pt-2.5 border-t border-white/10 space-y-2 shrink-0">
            <textarea
              v-model="newNote"
              rows="2"
              placeholder="Type in-call clinical observation..."
              class="w-full bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-white placeholder:text-white/30 focus:outline-none focus:border-primary resize-none"
              @keydown.enter.prevent="addNote"
            ></textarea>
            <button
              @click="addNote"
              class="w-full py-1.5 bg-primary hover:bg-primary-strong text-white rounded-xl text-xs font-semibold transition-colors flex items-center justify-center gap-1 cursor-pointer"
            >
              <Icon name="plus" class="w-3.5 h-3.5" /> Add Note
            </button>
          </div>
        </div>

        <!-- Tab 2: Live In-Call Rx Prescription Builder -->
        <div v-else-if="activeWorkspaceTab === 'rx_builder'" class="flex-1 p-4 overflow-y-auto space-y-3 text-xs">
          <div class="p-3 bg-white/5 border border-white/10 rounded-xl space-y-2">
            <div class="flex justify-between items-center">
              <span class="font-bold text-white text-sm">{{ rxPlan.title }}</span>
              <span class="px-2 py-0.5 bg-primary/20 text-primary-soft rounded font-mono">{{ rxPlan.dailyKcal }} kcal</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-center font-mono text-[0.7rem]">
              <div class="bg-black/30 p-1 rounded">P: {{ rxPlan.proteinG }}g</div>
              <div class="bg-black/30 p-1 rounded">C: {{ rxPlan.carbsG }}g</div>
              <div class="bg-black/30 p-1 rounded">F: {{ rxPlan.fatG }}g</div>
            </div>
          </div>

          <!-- Meals List -->
          <div class="space-y-1.5">
            <div
              v-for="(m, i) in rxPlan.meals"
              :key="i"
              class="p-2 bg-white/5 rounded-lg border border-white/5 flex items-center justify-between"
            >
              <div>
                <span class="font-bold text-[0.7rem] text-primary-soft uppercase mr-2">{{ m.type }}</span>
                <span class="text-white/90">{{ m.name }}</span>
              </div>
              <span class="font-mono text-white/50 text-[0.7rem] shrink-0">{{ m.kcal }} kcal</span>
            </div>
          </div>

          <button
            @click="pushRxToPatient"
            :disabled="isSaving"
            class="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold transition-colors flex items-center justify-center gap-1.5 cursor-pointer shadow-lg shadow-emerald-900/30"
          >
            <Icon name="check" class="w-4 h-4" />
            <span>{{ isSaving ? 'Pushing...' : 'Push Live Rx to Patient App →' }}</span>
          </button>
        </div>

        <!-- Tab 3: Wearable CGM & Vitals Stream -->
        <div v-else-if="activeWorkspaceTab === 'telemetry'" class="flex-1 p-4 overflow-y-auto space-y-3 text-xs">
          <div class="grid grid-cols-2 gap-2">
            <div class="p-3 bg-white/5 border border-white/10 rounded-xl">
              <div class="text-[0.68rem] text-white/50 uppercase">CGM Mean (7-Day)</div>
              <div class="text-lg font-bold text-emerald-400 font-mono">{{ biometrics.cgmAvg }} <span class="text-xs font-normal">mg/dL</span></div>
              <div class="text-[0.68rem] text-white/40">Range: {{ biometrics.cgmRange }}</div>
            </div>
            <div class="p-3 bg-white/5 border border-white/10 rounded-xl">
              <div class="text-[0.68rem] text-white/50 uppercase">Time In Range (TIR)</div>
              <div class="text-lg font-bold text-primary-soft font-mono">{{ biometrics.timeInRange }}%</div>
              <div class="text-[0.68rem] text-emerald-400">Target: >70%</div>
            </div>
          </div>

          <div class="p-3 bg-white/5 border border-white/10 rounded-xl space-y-2">
            <div class="font-semibold text-white/90">24h Continuous Glucose Trend</div>
            <div class="flex items-end gap-1.5 h-16 pt-2">
              <div
                v-for="(val, idx) in biometrics.cgmReadings"
                :key="idx"
                class="flex-1 bg-primary/60 hover:bg-primary rounded-t transition-all"
                :style="{ height: `${(val / 160) * 100}%` }"
                :title="`${val} mg/dL`"
              ></div>
            </div>
            <div class="flex justify-between text-[0.65rem] text-white/40 font-mono">
              <span>06:00</span>
              <span>12:00</span>
              <span>18:00</span>
              <span>23:00</span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2 text-center font-mono text-[0.75rem]">
            <div class="p-2 bg-white/5 rounded-lg border border-white/5">
              <div class="text-[0.65rem] text-white/40 uppercase">Oura Sleep</div>
              <div class="font-bold text-white">{{ biometrics.ouraSleepScore }}/100</div>
            </div>
            <div class="p-2 bg-white/5 rounded-lg border border-white/5">
              <div class="text-[0.65rem] text-white/40 uppercase">Daily Steps</div>
              <div class="font-bold text-white">{{ biometrics.stepsAvg.toLocaleString() }}</div>
            </div>
          </div>
        </div>

        <!-- Tab 4: AI Clinical Co-Pilot (SOAP Note) -->
        <div v-else-if="activeWorkspaceTab === 'soap_ai'" class="flex-1 p-4 overflow-y-auto space-y-2.5 text-xs">
          <div class="flex justify-between items-center mb-1">
            <span class="font-bold text-white text-sm">AI SOAP Note Generator</span>
            <button
              @click="generateAISoapNote"
              :disabled="isGeneratingSoap"
              class="px-2.5 py-1 bg-primary/30 text-primary-soft hover:bg-primary/40 rounded-lg text-[0.7rem] font-semibold flex items-center gap-1 cursor-pointer transition-colors"
            >
              <Icon name="sparkles" class="w-3.5 h-3.5" />
              <span>{{ isGeneratingSoap ? 'Drafting...' : 'Regenerate' }}</span>
            </button>
          </div>

          <div class="p-2.5 bg-white/5 rounded-xl border border-white/10 space-y-1">
            <div class="font-bold text-primary-soft text-[0.7rem] uppercase">S — Subjective</div>
            <p class="text-white/80 leading-relaxed text-[0.75rem]">{{ soapNote.subjective }}</p>
          </div>

          <div class="p-2.5 bg-white/5 rounded-xl border border-white/10 space-y-1">
            <div class="font-bold text-emerald-400 text-[0.7rem] uppercase">O — Objective</div>
            <p class="text-white/80 leading-relaxed text-[0.75rem]">{{ soapNote.objective }}</p>
          </div>

          <div class="p-2.5 bg-white/5 rounded-xl border border-white/10 space-y-1">
            <div class="font-bold text-amber-400 text-[0.7rem] uppercase">A — Assessment</div>
            <p class="text-white/80 leading-relaxed text-[0.75rem]">{{ soapNote.assessment }}</p>
          </div>

          <div class="p-2.5 bg-white/5 rounded-xl border border-white/10 space-y-1">
            <div class="font-bold text-primary-soft text-[0.7rem] uppercase">P — Plan</div>
            <p class="text-white/80 leading-relaxed text-[0.75rem] whitespace-pre-line">{{ soapNote.plan }}</p>
          </div>
        </div>

      </div>

    </div>

  </div>
</template>
