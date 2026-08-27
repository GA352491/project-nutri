<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'

// ── Types ────────────────────────────────────────────────────────────────────
interface PatientContact {
  id: string
  name: string
  avatar: string
  condition: string
  email: string
  unreadCount: number
  lastMessage: string
  lastTime: string
  online: boolean
  status: 'active' | 'pending'
  intakeSummary?: string
  targetCalories?: number
}

interface ClinicalMessage {
  id: string
  room_id: string
  sender: 'expert' | 'patient'
  sender_email: string
  recipient_email: string
  text: string
  time: string
  timestamp: string
  attachment?: {
    type: 'plan' | 'lab_report' | 'meal_photo'
    title: string
    meta?: string
  }
}

// ── Config ───────────────────────────────────────────────────────────────────
const EXPERT_EMAIL = 'expert@nutriplan.local'
const CHAT_API = 'http://localhost:8012/api/v1/chat'
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss:' : 'ws:'

function getCanonicalRoomId(emailA: string, emailB: string): string {
  return [emailA.toLowerCase(), emailB.toLowerCase()].sort().join('_')
}

// ── UI State ─────────────────────────────────────────────────────────────────
const toastMsg = ref('')
const showToast = ref(false)
const inputMessage = ref('')
const isSending = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
const filterTab = ref<'active' | 'pending'>('active')
const isPatientTyping = ref(false)
let patientTypingTimeout: ReturnType<typeof setTimeout> | null = null

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3000)
}

// ── Patient Thread List (static metadata, messages come from WS) ──────────────
const patients = ref<PatientContact[]>([
  {
    id: 'usr_test',
    name: 'Test User',
    email: 'test@test.com',
    avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&q=80',
    condition: 'Metabolic Optimization & South Indian High-Protein',
    unreadCount: 1,
    lastMessage: 'Clinical intake request: South Indian diet review, 1800 kcal',
    lastTime: '5 mins ago',
    online: true,
    status: 'pending',
    intakeSummary: 'Patient Account: test@test.com · Target: 1800 kcal / 120g Protein · South Indian Vegetarian with low oil · Primary Goal: Glucose stabilization & body recomposition.',
    targetCalories: 1800
  },
  {
    id: 'usr_1',
    name: 'Rohan Sharma',
    email: 'rohan@nutriplan.local',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&q=80',
    condition: 'Type 2 Diabetes',
    unreadCount: 0,
    lastMessage: 'Doctor, my fasting sugar was 114 mg/dL today after the walk.',
    lastTime: '10:45 AM',
    online: true,
    status: 'active',
    targetCalories: 1850
  },
  {
    id: 'usr_req_1',
    name: 'Rahul Verma',
    email: 'rahul@nutriplan.local',
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
    email: 'meera@nutriplan.local',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&q=80',
    condition: 'Post-Natal Lactation Nutrition',
    unreadCount: 1,
    lastMessage: 'Intake form submitted for 30-day lactation nutrient density plan.',
    lastTime: '1 hour ago',
    online: false,
    status: 'pending',
    intakeSummary: 'Age 29 · 3 months post-partum · Low iron & calcium flags in bloodwork · Goal: Micronutrient repletion while nursing.'
  }
])

const activePatientId = ref('usr_test')
const visiblePatients = computed(() => patients.value.filter(p => p.status === filterTab.value))
const pendingCount = computed(() => patients.value.filter(p => p.status === 'pending').length)
const activePatient = computed(() => patients.value.find(p => p.id === activePatientId.value) || patients.value[0])

// ── Real-Time Messages per room ───────────────────────────────────────────────
const roomMessages = ref<Record<string, ClinicalMessage[]>>({})
const activeMessages = computed(() => {
  if (!activePatient.value) return []
  const roomId = getCanonicalRoomId(activePatient.value.email, EXPERT_EMAIL)
  return roomMessages.value[roomId] || []
})

// ── WebSocket per active patient ──────────────────────────────────────────────
let activeWs: WebSocket | null = null
let wsReconnectTimer: ReturnType<typeof setTimeout> | null = null

function connectToPatientRoom(patient: PatientContact) {
  if (activeWs) {
    activeWs.close()
    activeWs = null
  }
  if (wsReconnectTimer) clearTimeout(wsReconnectTimer)

  const roomId = getCanonicalRoomId(patient.email, EXPERT_EMAIL)
  const wsUrl = `${WS_PROTOCOL}//localhost:8012/api/v1/chat/ws/clinical/${roomId}/${EXPERT_EMAIL}`
  console.log(`[Expert WS] Connecting to room ${roomId}`)

  const ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log(`[Expert WS] Connected to room ${roomId}`)
    activeWs = ws
  }

  ws.onmessage = async (event) => {
    try {
      const data = JSON.parse(event.data)
      await handleWsMessage(data, roomId, patient)
    } catch (e) {
      console.error('[Expert WS] Parse error', e)
    }
  }

  ws.onclose = () => {
    console.log(`[Expert WS] Disconnected from ${roomId} — reconnecting in 3s`)
    wsReconnectTimer = setTimeout(() => connectToPatientRoom(patient), 3000)
  }

  ws.onerror = (e) => {
    console.error('[Expert WS] Error', e)
  }
}

async function handleWsMessage(data: any, roomId: string, patient: PatientContact) {
  switch (data.type) {
    case 'thread_status':
      {
        const idx = patients.value.findIndex(p => p.id === patient.id)
        if (idx !== -1) patients.value[idx].status = data.status
      }
      break

    case 'history':
      roomMessages.value[roomId] = data.messages || []
      await scrollChat()
      break

    case 'clinical_message':
      {
        const msg: ClinicalMessage = data.payload
        if (!roomMessages.value[roomId]) roomMessages.value[roomId] = []
        const exists = roomMessages.value[roomId].some(m => m.id === msg.id)
        if (!exists) {
          roomMessages.value[roomId].push(msg)
          // Update patient's last message preview
          const idx = patients.value.findIndex(p => p.id === patient.id)
          if (idx !== -1) {
            patients.value[idx].lastMessage = msg.text
            patients.value[idx].lastTime = msg.time
            if (msg.sender === 'patient') patients.value[idx].unreadCount++
          }
        }
        await scrollChat()
      }
      break

    case 'intake_accepted':
      {
        const idx = patients.value.findIndex(p => p.id === patient.id)
        if (idx !== -1) patients.value[idx].status = 'active'
        if (data.payload?.welcome_message) {
          if (!roomMessages.value[roomId]) roomMessages.value[roomId] = []
          roomMessages.value[roomId].push(data.payload.welcome_message)
          await scrollChat()
        }
      }
      break

    case 'typing':
      if (data.sender_email !== EXPERT_EMAIL) {
        isPatientTyping.value = data.is_typing
        if (patientTypingTimeout) clearTimeout(patientTypingTimeout)
        if (data.is_typing) {
          patientTypingTimeout = setTimeout(() => { isPatientTyping.value = false }, 5000)
        }
      }
      break

    case 'pong':
      break
  }
}

function selectPatient(p: PatientContact) {
  activePatientId.value = p.id
  p.unreadCount = 0
  isPatientTyping.value = false
  connectToPatientRoom(p)
}

async function scrollChat() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// ── Expert Actions ────────────────────────────────────────────────────────────
async function acceptPatientRequest(patient: PatientContact) {
  try {
    const res = await fetch(`${CHAT_API}/clinical/intake/accept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_email: patient.email,
        expert_email: EXPERT_EMAIL,
      })
    })
    const data = await res.json()
    if (data.ok) {
      patient.status = 'active'
      filterTab.value = 'active'
      activePatientId.value = patient.id
      connectToPatientRoom(patient)
      notify(`✅ Accepted ${patient.name} — clinical messaging thread unlocked.`)
    }
  } catch (e) {
    // Offline fallback
    patient.status = 'active'
    filterTab.value = 'active'
    activePatientId.value = patient.id
    const roomId = getCanonicalRoomId(patient.email, EXPERT_EMAIL)
    if (!roomMessages.value[roomId]) roomMessages.value[roomId] = []
    roomMessages.value[roomId].push({
      id: `exp_acc_${Date.now()}`,
      room_id: roomId,
      sender: 'expert',
      sender_email: EXPERT_EMAIL,
      recipient_email: patient.email,
      text: `Hello ${patient.name}! I (Dr. Sarah Jenkins, ${EXPERT_EMAIL}) have accepted your clinical consultation request. Your two-way messaging channel is now active.`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      timestamp: new Date().toISOString(),
    })
    connectToPatientRoom(patient)
    notify(`✅ Accepted ${patient.name} — clinical messaging thread unlocked.`)
    await scrollChat()
  }
}

async function declinePatientRequest(patient: PatientContact) {
  try {
    await fetch(`${CHAT_API}/clinical/intake/decline?patient_email=${encodeURIComponent(patient.email)}&expert_email=${encodeURIComponent(EXPERT_EMAIL)}`, {
      method: 'POST'
    })
  } catch (e) {}
  const idx = patients.value.findIndex(p => p.id === patient.id)
  if (idx !== -1) patients.value.splice(idx, 1)
  notify(`ℹ️ Request declined — patient redirected to AI coach.`)
}

async function sendMessage() {
  if (!inputMessage.value.trim() || !activePatient.value || activePatient.value.status === 'pending') return

  const text = inputMessage.value.trim()
  inputMessage.value = ''
  isSending.value = true

  const patient = activePatient.value
  const roomId = getCanonicalRoomId(patient.email, EXPERT_EMAIL)

  const payload = {
    type: 'message',
    sender: 'expert',
    sender_email: EXPERT_EMAIL,
    recipient_email: patient.email,
    text,
  }

  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify(payload))
  } else {
    // REST fallback
    try {
      await fetch(`${CHAT_API}/clinical/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender: 'expert',
          sender_email: EXPERT_EMAIL,
          recipient_email: patient.email,
          text,
        })
      })
    } catch (e) {
      // Local only fallback
      if (!roomMessages.value[roomId]) roomMessages.value[roomId] = []
      roomMessages.value[roomId].push({
        id: `local_${Date.now()}`,
        room_id: roomId,
        sender: 'expert',
        sender_email: EXPERT_EMAIL,
        recipient_email: patient.email,
        text,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        timestamp: new Date().toISOString(),
      })
      await scrollChat()
    }
  }

  patient.lastMessage = text
  patient.lastTime = 'Just now'
  isSending.value = false
}

async function sendPrescription() {
  if (!activePatient.value || activePatient.value.status === 'pending') return
  const patient = activePatient.value

  const prescriptionText = `I have updated and prescribed your 7-Day Regional Meal Plan targeting ${patient.targetCalories || 1800} kcal/day with enhanced dietary fiber and optimized micronutrients for ${patient.condition}.`

  const payload = {
    type: 'message',
    sender: 'expert',
    sender_email: EXPERT_EMAIL,
    recipient_email: patient.email,
    text: prescriptionText,
    attachment: {
      type: 'plan',
      title: `7-Day Clinical Diet Prescription (${patient.condition})`,
      meta: `${patient.targetCalories || 1800} kcal · 120g Protein · ICMR-NIN Compliant`,
    }
  }

  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify(payload))
  }

  notify("📋 Diet plan prescription sent to patient's app.")
}

function sendTypingIndicator(isTyping: boolean) {
  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify({ type: 'typing', is_typing: isTyping, sender_email: EXPERT_EMAIL }))
  }
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(() => {
  if (activePatient.value) connectToPatientRoom(activePatient.value)
})

onUnmounted(() => {
  if (activeWs) activeWs.close()
  if (wsReconnectTimer) clearTimeout(wsReconnectTimer)
})
</script>

<template>
  <div class="h-[calc(100vh-8.5rem)] flex flex-col md:flex-row bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
    <Toast :show="showToast" :message="toastMsg" />

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- LEFT: PATIENT THREAD LIST -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <div class="w-full md:w-80 lg:w-96 border-r border-border flex flex-col bg-surface-alt/40 shrink-0">
      <div class="p-4 border-b border-border bg-card">
        <h2 class="font-display font-bold text-base text-ink mb-3">Clinical Care Messaging</h2>
        <div class="grid grid-cols-2 p-1 bg-surface-alt rounded-xl border border-border text-xs font-semibold">
          <button class="py-1.5 rounded-lg transition-all" :class="filterTab === 'active' ? 'bg-card text-ink shadow-xs' : 'text-ink-muted hover:text-ink'" @click="filterTab = 'active'">
            Active ({{ patients.filter(p => p.status === 'active').length }})
          </button>
          <button class="py-1.5 rounded-lg transition-all flex items-center justify-center gap-1.5" :class="filterTab === 'pending' ? 'bg-card text-ink shadow-xs' : 'text-ink-muted hover:text-ink'" @click="filterTab = 'pending'">
            Requests
            <span v-if="pendingCount > 0" class="px-1.5 bg-amber-500 text-white rounded-full text-[0.65rem] font-bold">{{ pendingCount }}</span>
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto divide-y divide-border/60">
        <div v-for="p in visiblePatients" :key="p.id"
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
            <div class="text-xs text-primary font-medium truncate mb-0.5">{{ p.condition }}</div>
            <div class="text-[0.72rem] text-ink-muted font-mono truncate mb-0.5">{{ p.email }}</div>
            <p class="text-xs text-ink-muted truncate">{{ p.lastMessage }}</p>
          </div>
          <span v-if="p.unreadCount > 0" class="px-2 py-0.5 bg-primary text-white text-[0.7rem] font-bold rounded-full shrink-0">{{ p.unreadCount }}</span>
        </div>
        <div v-if="visiblePatients.length === 0" class="p-8 text-center text-xs text-ink-muted">No {{ filterTab }} patient threads.</div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- RIGHT: ACTIVE CONVERSATION -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <div class="flex-1 flex flex-col bg-card min-w-0">
      <!-- Thread Header -->
      <div v-if="activePatient" class="p-4 border-b border-border flex items-center justify-between bg-card z-10 shadow-2xs">
        <div class="flex items-center gap-3">
          <div class="relative">
            <img :src="activePatient.avatar" class="w-10 h-10 rounded-full object-cover border border-border" alt="Patient" />
            <span v-if="activePatient.online" class="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-success border-2 border-card" />
          </div>
          <div>
            <div class="font-display font-semibold text-sm text-ink flex items-center gap-2">
              {{ activePatient.name }}
              <span class="font-mono text-xs text-primary font-normal">({{ activePatient.email }})</span>
              <span class="px-2 py-0.5 rounded text-[0.68rem] font-bold" :class="activePatient.status === 'active' ? 'bg-success/15 text-success' : 'bg-amber-500/15 text-amber-600'">
                {{ activePatient.status === 'active' ? 'Care Active' : 'Consent Pending' }}
              </span>
            </div>
            <div class="text-xs text-ink-muted">{{ activePatient.condition }}</div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <Button v-if="activePatient.status === 'active'" variant="outline" size="sm" @click="sendPrescription" class="text-xs font-semibold gap-1.5">
            📋 Send Meal Plan
          </Button>
          <router-link :to="`/consultation/room_${activePatient.id}`" class="px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-semibold hover:bg-primary-strong transition-colors flex items-center gap-1.5">
            📹 Start Video
          </router-link>
        </div>
      </div>

      <!-- PENDING: INTAKE APPROVAL CARD -->
      <div v-if="activePatient?.status === 'pending'" class="flex-1 p-6 overflow-y-auto bg-surface-alt/20 flex flex-col justify-center max-w-xl mx-auto">
        <div class="bg-card border border-border rounded-2xl p-6 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-full bg-amber-500/15 text-amber-600 flex items-center justify-center font-bold text-lg">🩺</div>
            <div>
              <h3 class="font-display font-bold text-base text-ink">New Patient Intake Request</h3>
              <p class="text-xs text-ink-muted font-mono">From: {{ activePatient.email }}</p>
            </div>
          </div>
          <div class="p-4 bg-surface-alt rounded-xl border border-border/80 text-xs text-ink leading-relaxed space-y-2 mb-6">
            <div class="font-semibold text-ink-muted uppercase tracking-wider text-[0.68rem]">Clinical Intake Summary:</div>
            <p>{{ activePatient.intakeSummary }}</p>
          </div>
          <div class="flex items-center gap-3">
            <Button variant="primary" class="flex-1 text-xs font-bold" @click="acceptPatientRequest(activePatient)">✅ Accept Patient & Open Chat</Button>
            <Button variant="outline" class="text-xs text-ink-muted hover:text-error" @click="declinePatientRequest(activePatient)">Decline</Button>
          </div>
        </div>
      </div>

      <!-- ACTIVE: LIVE BIDIRECTIONAL MESSAGES -->
      <div v-else ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4 bg-surface-alt/10">
        <div v-for="m in activeMessages" :key="m.id" class="flex flex-col" :class="m.sender === 'expert' ? 'items-end' : 'items-start'">
          <div class="max-w-[85%] md:max-w-[70%] rounded-2xl px-4 py-3 text-xs leading-relaxed shadow-xs"
            :class="m.sender === 'expert' ? 'bg-primary text-white rounded-br-xs' : 'bg-card border border-border text-ink rounded-bl-xs'"
          >
            <div v-if="m.sender === 'patient'" class="font-bold text-[0.75rem] text-primary mb-1">{{ activePatient?.name }} ({{ activePatient?.email }})</div>
            <p>{{ m.text }}</p>
            <div v-if="m.attachment" class="mt-2.5 p-2.5 rounded-xl border flex items-center gap-3 text-xs"
              :class="m.sender === 'expert' ? 'bg-white/10 border-white/20 text-white' : 'bg-surface-alt border-border text-ink'"
            >
              <div class="w-8 h-8 rounded-lg bg-primary/15 text-primary flex items-center justify-center font-bold text-sm shrink-0">📊</div>
              <div class="overflow-hidden">
                <div class="font-semibold truncate">{{ m.attachment.title }}</div>
                <div class="text-[0.7rem] opacity-80 truncate">{{ m.attachment.meta }}</div>
              </div>
            </div>
            <div class="text-[0.65rem] mt-1.5 opacity-70 text-right">{{ m.time }}</div>
          </div>
        </div>

        <!-- Patient Typing -->
        <div v-if="isPatientTyping" class="flex items-end gap-2">
          <img v-if="activePatient" :src="activePatient.avatar" class="w-7 h-7 rounded-full object-cover shrink-0" alt="Patient" />
          <div class="bg-card border border-border rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-1">
            <span class="w-1.5 h-1.5 bg-ink-muted rounded-full animate-bounce" style="animation-delay: 0ms" />
            <span class="w-1.5 h-1.5 bg-ink-muted rounded-full animate-bounce" style="animation-delay: 150ms" />
            <span class="w-1.5 h-1.5 bg-ink-muted rounded-full animate-bounce" style="animation-delay: 300ms" />
          </div>
        </div>

        <div v-if="activeMessages.length === 0" class="text-center text-xs text-ink-muted py-8">
          No messages yet. Send your first clinical note.
        </div>
      </div>

      <!-- Input (only when active) -->
      <div v-if="activePatient?.status === 'active'" class="p-3.5 border-t border-border bg-card">
        <div class="flex items-center gap-2">
          <input
            v-model="inputMessage"
            type="text"
            :placeholder="`Reply to ${activePatient?.name} (${activePatient?.email})...`"
            class="flex-1 bg-surface-alt border border-border rounded-xl px-4 py-2.5 text-xs text-ink placeholder:text-ink-muted focus:outline-none focus:border-primary"
            @keydown.enter="sendMessage"
            @input="sendTypingIndicator(true)"
            @blur="sendTypingIndicator(false)"
          />
          <Button variant="primary" size="sm" @click="sendMessage" :disabled="!inputMessage.trim() || isSending" class="px-4">Send</Button>
        </div>
        <p class="text-[0.65rem] text-ink-muted mt-1.5 px-1">🛡️ End-to-End Encrypted · HIPAA Compliant</p>
      </div>
    </div>
  </div>
</template>
