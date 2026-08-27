<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'

interface PatientContact {
  id: string
  name: string
  avatar: string
  condition: string
  unreadCount: number
  lastMessage: string
  lastTime: string
  online: boolean
  status: 'active' | 'pending'
  intakeSummary?: string
  targetCalories?: number
}

interface Message {
  id: string
  sender: 'expert' | 'patient'
  text: string
  time: string
  status?: 'sent' | 'delivered' | 'read'
  attachment?: {
    type: 'plan' | 'lab_report' | 'meal_photo'
    title: string
    meta?: string
  }
}

const toastMsg = ref('')
const showToast = ref(false)
const inputMessage = ref('')
const isSending = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
const filterTab = ref<'active' | 'pending'>('active')

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3000)
}

const patients = ref<PatientContact[]>([
  {
    id: 'usr_1',
    name: 'Rohan Sharma',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&q=80',
    condition: 'Type 2 Diabetes',
    unreadCount: 2,
    lastMessage: 'Doctor, my fasting sugar was 114 mg/dL today after the walk.',
    lastTime: '10:45 AM',
    online: true,
    status: 'active',
    targetCalories: 1850
  },
  {
    id: 'usr_2',
    name: 'Priya Patel',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&q=80',
    condition: 'PCOS & Insulin Resistance',
    unreadCount: 0,
    lastMessage: 'Got the new cooked veggie plan. Feeling much less bloated!',
    lastTime: 'Yesterday',
    online: false,
    status: 'active',
    targetCalories: 1600
  },
  {
    id: 'usr_3',
    name: 'Amit Kumar',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&q=80',
    condition: 'Sports Hypertrophy',
    unreadCount: 0,
    lastMessage: 'Hit 140g protein yesterday with the paneer + sattu shake.',
    lastTime: '2 days ago',
    online: true,
    status: 'active',
    targetCalories: 2600
  },
  {
    id: 'usr_4',
    name: 'Sneha Desai',
    avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&q=80',
    condition: 'Cardiovascular / DASH Diet',
    unreadCount: 0,
    lastMessage: 'Uploaded my 7-day sodium diary report for review.',
    lastTime: '3 days ago',
    online: false,
    status: 'active',
    targetCalories: 1900
  },
  // Pending Consent & Intake Requests (Anti-Spam Filtered)
  {
    id: 'usr_test',
    name: 'Test User (test@test.com)',
    avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&q=80',
    condition: 'Metabolic Optimization & South Indian High-Protein',
    unreadCount: 1,
    lastMessage: 'Consultation intake request from test@test.com: Requesting South Indian diet review.',
    lastTime: '5 mins ago',
    online: true,
    status: (localStorage.getItem('nutriplan_expert_consent_test@test.com') as any) || 'pending',
    intakeSummary: 'Patient Account: test@test.com · Target: 1800 kcal / 120g Protein · South Indian Vegetarian with low oil · Primary Goal: Glucose stabilization & body recomposition.'
  },
  {
    id: 'usr_req_1',
    name: 'Rahul Verma',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&q=80',
    condition: 'Metabolic Syndrome & Fatty Liver',
    unreadCount: 1,
    lastMessage: 'Requesting personalized South Indian low-oil diet consultation.',
    lastTime: '20 mins ago',
    online: true,
    status: 'pending',
    intakeSummary: 'Age 38 · HbA1c 7.2% · BMI 28.4 · Vegetarian (No eggs) · Goal: Reverse NAFLD Grade 1 with regional meal modifications.'
  },
  {
    id: 'usr_req_2',
    name: 'Meera Nair',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&q=80',
    condition: 'Post-Natal Lactation Nutrition',
    unreadCount: 1,
    lastMessage: 'Intake form submitted for 30-day lactation nutrient density plan.',
    lastTime: '1 hour ago',
    online: false,
    status: 'pending',
    intakeSummary: 'Age 29 · 3 months post-partum · Low iron & calcium flags in bloodwork · Goal: Micronutrient repletion while nursing.'
  }
])

const activePatientId = ref(localStorage.getItem('nutriplan_expert_consent_test@test.com') === 'active' ? 'usr_test' : 'usr_1')

const visiblePatients = computed(() => {
  return patients.value.filter(p => p.status === filterTab.value)
})

const pendingCount = computed(() => {
  return patients.value.filter(p => p.status === 'pending').length
})

const activePatient = computed(() => {
  return patients.value.find(p => p.id === activePatientId.value) || visiblePatients.value[0] || patients.value[0]
})

const conversations = ref<Record<string, Message[]>>({
  usr_1: [
    {
      id: 'm1',
      sender: 'patient',
      text: 'Good morning Dr. Sarah! Here is my morning fasting glucose reading.',
      time: '09:15 AM'
    },
    {
      id: 'm2',
      sender: 'expert',
      text: 'Good morning Rohan! That looks well within our target range (<120 mg/dL). How did you feel after the 15-minute walk yesterday evening?',
      time: '09:25 AM'
    },
    {
      id: 'm3',
      sender: 'patient',
      text: 'Doctor, my fasting sugar was 114 mg/dL today after the walk. Energy levels are much better.',
      time: '10:45 AM',
      attachment: {
        type: 'lab_report',
        title: 'Continuous Glucose Monitor (CGM) 24h Log',
        meta: 'Avg: 118 mg/dL · TIR: 94%'
      }
    }
  ],
  usr_2: [
    {
      id: 'm201',
      sender: 'patient',
      text: 'Got the new cooked veggie plan. Feeling much less bloated!',
      time: 'Yesterday'
    }
  ],
  usr_3: [
    {
      id: 'm301',
      sender: 'patient',
      text: 'Hit 140g protein yesterday with the paneer + sattu shake.',
      time: '2 days ago'
    }
  ],
  usr_4: [
    {
      id: 'm401',
      sender: 'patient',
      text: 'Uploaded my 7-day sodium diary report for review.',
      time: '3 days ago'
    }
  ],
  usr_test: [
    {
      id: 'req_test_1',
      sender: 'patient',
      text: 'Hello Dr. Sarah (expert@nutriplan.local), I am submitting my clinical intake request. I would like your guidance on optimizing my macros for energy and fat loss with South Indian regional foods (1800 kcal / 120g Protein).',
      time: '5 mins ago',
      attachment: {
        type: 'lab_report',
        title: 'Intake Health Bio & Macro Target Form (test@test.com)',
        meta: '1800 kcal · Fasting Glucose 114 mg/dL · 8,400 daily steps'
      }
    }
  ],
  usr_req_1: [
    {
      id: 'req_m1',
      sender: 'patient',
      text: 'Hello Dr. Sarah, I was referred to you for metabolic health and fatty liver reversal. I have submitted my intake form and recent lipid panel. Looking forward to your guidance.',
      time: '20 mins ago'
    }
  ],
  usr_req_2: [
    {
      id: 'req_m2',
      sender: 'patient',
      text: 'Hello Dr. Sarah, I would like to request your review for my post-natal lactation diet plan. My complete blood count and iron levels are attached in my health bio.',
      time: '1 hour ago'
    }
  ]
})

function selectPatient(p: PatientContact) {
  activePatientId.value = p.id
  p.unreadCount = 0
}

function acceptPatientRequest(patient: PatientContact) {
  patient.status = 'active'
  filterTab.value = 'active'
  activePatientId.value = patient.id

  if (patient.id === 'usr_test') {
    localStorage.setItem('nutriplan_expert_consent_test@test.com', 'active')
  }

  // Add welcome clinical acknowledgment message
  if (!conversations.value[patient.id]) {
    conversations.value[patient.id] = []
  }
  conversations.value[patient.id].push({
    id: `exp_acc_${Date.now()}`,
    sender: 'expert',
    text: `Hello ${patient.name}! I (Dr. Sarah Jenkins, expert@nutriplan.local) have accepted your clinical consultation request and reviewed your health bio. Your two-way messaging channel is now active. How can I assist you with your diet plan today?`,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })

  notify(`✅ Accepted ${patient.name} — Clinical messaging thread unlocked.`)
}

function declinePatientRequest(patient: PatientContact) {
  const idx = patients.value.findIndex(p => p.id === patient.id)
  if (idx !== -1) {
    patients.value.splice(idx, 1)
  }
  notify(`ℹ️ Request declined with automated AI coach triage referral.`)
}

async function sendMessage() {
  if (!inputMessage.value.trim() || !activePatient.value || activePatient.value.status === 'pending') return

  const text = inputMessage.value.trim()
  inputMessage.value = ''
  isSending.value = true

  const newMsg: Message = {
    id: `m_${Date.now()}`,
    sender: 'expert',
    text,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    status: 'sent'
  }

  if (!conversations.value[activePatient.value.id]) {
    conversations.value[activePatient.value.id] = []
  }
  conversations.value[activePatient.value.id].push(newMsg)

  activePatient.value.lastMessage = text
  activePatient.value.lastTime = 'Just now'

  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }

  isSending.value = false
  notify("Message sent to patient.")
}

function sendPrescription() {
  if (!activePatient.value || activePatient.value.status === 'pending') return

  const planMsg: Message = {
    id: `m_plan_${Date.now()}`,
    sender: 'expert',
    text: `I have updated and prescribed your 7-Day Regional Meal Plan targeting ${activePatient.value.targetCalories || 1800} kcal/day with enhanced dietary fiber and optimized micronutrients.`,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    attachment: {
      type: 'plan',
      title: `7-Day Clinical Diet Prescription (${activePatient.value.condition})`,
      meta: `${activePatient.value.targetCalories || 1800} kcal · 120g Protein · ICMR-NIN Compliant`
    }
  }

  conversations.value[activePatient.value.id].push(planMsg)
  notify("Diet plan prescription sent directly into patient's app.")
}
</script>

<template>
  <div class="h-[calc(100vh-8.5rem)] flex flex-col md:flex-row bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
    <Toast :show="showToast" :message="toastMsg" />

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- LEFT PANEL: PATIENT THREADS & CONSENT FILTER -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <div class="w-full md:w-80 lg:w-96 border-r border-border flex flex-col bg-surface-alt/40 shrink-0">
      <!-- Search & Tab Filter -->
      <div class="p-4 border-b border-border bg-card">
        <h2 class="font-display font-bold text-base text-ink mb-3">Clinical Care Messaging</h2>
        
        <!-- Filter Tabs -->
        <div class="grid grid-cols-2 p-1 bg-surface-alt rounded-xl border border-border text-xs font-semibold">
          <button
            class="py-1.5 rounded-lg transition-all"
            :class="filterTab === 'active' ? 'bg-card text-ink shadow-xs' : 'text-ink-muted hover:text-ink'"
            @click="filterTab = 'active'"
          >
            Active ({{ patients.filter(p => p.status === 'active').length }})
          </button>
          <button
            class="py-1.5 rounded-lg transition-all flex items-center justify-center gap-1.5"
            :class="filterTab === 'pending' ? 'bg-card text-ink shadow-xs' : 'text-ink-muted hover:text-ink'"
            @click="filterTab = 'pending'"
          >
            Requests
            <span v-if="pendingCount > 0" class="px-1.5 py-0.2 bg-amber-500 text-white rounded-full text-[0.65rem] font-bold">
              {{ pendingCount }}
            </span>
          </button>
        </div>
      </div>

      <!-- Patients List -->
      <div class="flex-1 overflow-y-auto divide-y divide-border/60">
        <div
          v-for="p in visiblePatients"
          :key="p.id"
          @click="selectPatient(p)"
          class="p-3.5 flex items-start gap-3 cursor-pointer transition-colors"
          :class="activePatientId === p.id ? 'bg-primary/5 border-l-4 border-primary' : 'hover:bg-surface-alt/80'"
        >
          <div class="relative shrink-0">
            <img :src="p.avatar" class="w-11 h-11 rounded-full object-cover border border-border" alt="Avatar" />
            <span v-if="p.online" class="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-success border-2 border-card" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-0.5">
              <span class="font-semibold text-sm text-ink truncate">{{ p.name }}</span>
              <span class="text-[0.7rem] text-ink-muted font-data shrink-0">{{ p.lastTime }}</span>
            </div>
            <div class="text-xs text-primary font-medium truncate mb-1">{{ p.condition }}</div>
            <p class="text-xs text-ink-muted truncate">{{ p.lastMessage }}</p>
          </div>
          <span v-if="p.unreadCount > 0" class="px-2 py-0.5 bg-primary text-white text-[0.7rem] font-bold rounded-full">
            {{ p.unreadCount }}
          </span>
        </div>

        <div v-if="visiblePatients.length === 0" class="p-8 text-center text-xs text-ink-muted">
          No {{ filterTab }} patient threads at this time.
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- RIGHT PANEL: ACTIVE CONVERSATION & CLINICAL CONTROLS -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <div class="flex-1 flex flex-col bg-card min-w-0">
      
      <!-- Thread Header -->
      <div v-if="activePatient" class="p-4 border-b border-border flex items-center justify-between bg-card z-10 shadow-2xs">
        <div class="flex items-center gap-3">
          <div class="relative">
            <img :src="activePatient.avatar" class="w-10 h-10 rounded-full object-cover border border-border" alt="Active Patient" />
            <span v-if="activePatient.online" class="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-success border-2 border-card" />
          </div>
          <div>
            <div class="font-display font-semibold text-sm text-ink flex items-center gap-2">
              {{ activePatient.name }}
              <span
                class="px-2 py-0.5 rounded text-[0.68rem] font-bold"
                :class="activePatient.status === 'active' ? 'bg-success/15 text-success' : 'bg-amber-500/15 text-amber-600'"
              >
                {{ activePatient.status === 'active' ? 'Care Active' : 'Consent Pending' }}
              </span>
            </div>
            <div class="text-xs text-ink-muted">{{ activePatient.condition }}</div>
          </div>
        </div>

        <!-- Header Actions -->
        <div class="flex items-center gap-2">
          <Button
            v-if="activePatient.status === 'active'"
            variant="outline"
            size="sm"
            @click="sendPrescription"
            class="text-xs font-semibold gap-1.5"
          >
            📋 Send Meal Plan
          </Button>
          <router-link
            :to="`/consultation/room_${activePatient.id}`"
            class="px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-semibold hover:bg-primary-strong transition-colors flex items-center gap-1.5"
          >
            📹 Start Video
          </router-link>
        </div>
      </div>

      <!-- ── CASE A: INTAKE CONSENT REQUEST VIEW ─────────────────────────────── -->
      <div v-if="activePatient?.status === 'pending'" class="flex-1 p-6 overflow-y-auto bg-surface-alt/20 flex flex-col justify-center max-w-xl mx-auto">
        <div class="bg-card border border-border rounded-2xl p-6 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-full bg-amber-500/15 text-amber-600 flex items-center justify-center font-bold text-lg">
              🩺
            </div>
            <div>
              <h3 class="font-display font-bold text-base text-ink">New Patient Intake Request</h3>
              <p class="text-xs text-ink-muted">Review patient clinical goals before opening 2-way communication.</p>
            </div>
          </div>

          <div class="p-4 bg-surface-alt rounded-xl border border-border/80 text-xs text-ink leading-relaxed space-y-2 mb-6">
            <div class="font-semibold text-ink-muted uppercase tracking-wider text-[0.68rem]">Clinical Intake Summary:</div>
            <p>{{ activePatient.intakeSummary }}</p>
          </div>

          <div class="flex items-center gap-3">
            <Button
              variant="primary"
              class="flex-1 text-xs font-bold"
              @click="acceptPatientRequest(activePatient)"
            >
              ✅ Accept Patient & Open Chat
            </Button>
            <Button
              variant="outline"
              class="text-xs text-ink-muted hover:text-error"
              @click="declinePatientRequest(activePatient)"
            >
              Decline
            </Button>
          </div>
        </div>
      </div>

      <!-- ── CASE B: ACTIVE BIDIRECTIONAL MESSAGES ────────────────────────────── -->
      <div v-else ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4 bg-surface-alt/10">
        <div
          v-for="m in (conversations[activePatient?.id || ''] || [])"
          :key="m.id"
          class="flex flex-col"
          :class="m.sender === 'expert' ? 'items-end' : 'items-start'"
        >
          <div
            class="max-w-[85%] md:max-w-[70%] rounded-2xl px-4 py-3 text-xs leading-relaxed shadow-xs"
            :class="m.sender === 'expert' ? 'bg-primary text-white rounded-br-xs' : 'bg-card border border-border text-ink rounded-bl-xs'"
          >
            <p>{{ m.text }}</p>

            <!-- Attachment Card -->
            <div
              v-if="m.attachment"
              class="mt-2.5 p-2.5 rounded-xl border flex items-center gap-3 text-xs"
              :class="m.sender === 'expert' ? 'bg-white/10 border-white/20 text-white' : 'bg-surface-alt border-border text-ink'"
            >
              <div class="w-8 h-8 rounded-lg bg-primary/15 text-primary flex items-center justify-center font-bold text-sm shrink-0">
                📊
              </div>
              <div class="overflow-hidden">
                <div class="font-semibold truncate">{{ m.attachment.title }}</div>
                <div class="text-[0.7rem] opacity-80 truncate">{{ m.attachment.meta }}</div>
              </div>
            </div>

            <div class="text-[0.65rem] mt-1.5 opacity-70 text-right">
              {{ m.time }}
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area (Only active if accepted) -->
      <div v-if="activePatient?.status === 'active'" class="p-3.5 border-t border-border bg-card">
        <div class="flex items-center gap-2">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Type clinical advice or meal response..."
            class="flex-1 bg-surface-alt border border-border rounded-xl px-4 py-2.5 text-xs text-ink placeholder:text-ink-muted focus:outline-none focus:border-primary"
            @keydown.enter="sendMessage"
          />
          <Button
            variant="primary"
            size="sm"
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isSending"
            class="px-4"
          >
            Send
          </Button>
        </div>
      </div>

    </div>
  </div>
</template>
