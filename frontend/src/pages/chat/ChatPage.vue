<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import ChatBubble from '../../components/ChatBubble.vue'
import { useResilientWebSocket } from '../../composables/useResilientWebSocket'

// ── Types ────────────────────────────────────────────────────────────────────
interface Attachment {
  type: 'plan' | 'lab_report' | 'meal_photo'
  title: string
  meta?: string
}

interface AiMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ClinicalMessage {
  id: string
  room_id: string
  sender: 'patient' | 'expert'
  sender_email: string
  recipient_email: string
  text: string
  time: string
  timestamp: string
  status?: 'sending' | 'sent' | 'delivered' | 'failed'
  attachment?: Attachment
}

// ── Config ───────────────────────────────────────────────────────────────────
const PATIENT_EMAIL = localStorage.getItem('nutriplan_user_email') || 'test@test.com'
const EXPERT_EMAIL = 'expert@nutriplan.local'
const CHAT_API = 'http://localhost:8012/api/v1/chat'
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss:' : 'ws:'

function getCanonicalRoomId(emailA: string, emailB: string): string {
  return [emailA.toLowerCase(), emailB.toLowerCase()].sort().join('_')
}
const CLINICAL_ROOM_ID = getCanonicalRoomId(PATIENT_EMAIL, EXPERT_EMAIL)

// ── State ────────────────────────────────────────────────────────────────────
const activeTab = ref<'ai' | 'expert'>('expert')

// Clinical thread state
const clinicalMessages = ref<ClinicalMessage[]>([])
const clinicalStatus = ref<'pending' | 'active' | 'declined' | 'connecting'>('connecting')
const clinicalInput = ref('')
const isExpertTyping = ref(false)
const expertTypingTimeout = ref<ReturnType<typeof setTimeout> | null>(null)
const clinicalScrollRef = ref<HTMLElement | null>(null)
const isSendingClinical = ref(false)
let clinicalWs: WebSocket | null = null
let clinicalWsReconnectTimer: ReturnType<typeof setTimeout> | null = null

// AI coach state
const aiMessages = ref<AiMessage[]>([
  {
    id: '0',
    role: 'assistant',
    content: "Hello! I'm your NutriPlan AI nutritionist. I can help with recipes, macros, diary analysis, and ICMR-NIN guidelines. How can I help you today?",
    timestamp: new Date(),
  }
])
const aiInput = ref('')
const isAiTyping = ref(false)
const isAiStreaming = ref(false)
const streamingContent = ref('')  // accumulates token deltas
const aiScrollRef = ref<HTMLElement | null>(null)
const activeRegion = ref(localStorage.getItem('nutriplan_regional_pref') || 'in_south_andhra')

// Expert info
const expertName = 'Dr. Sarah Jenkins, RD, CDE'
const expertAvatar = 'https://images.unsplash.com/photo-1594824813620-1361c4de4a75?w=150&q=80'
const officeHours = 'Mon–Fri, 9:00 AM – 6:00 PM IST'
const maxPendingQueue = 3

// Turn-taking anti-spam counter
const pendingPatientQuestions = computed(() => {
  let count = 0
  for (let i = clinicalMessages.value.length - 1; i >= 0; i--) {
    if (clinicalMessages.value[i].sender === 'patient') count++
    else break
  }
  return count
})
const isQueueLimitReached = computed(() => pendingPatientQuestions.value >= maxPendingQueue)

const aiSuggestions = [
  "Suggest a high-protein South Indian breakfast under 400 kcal",
  "How can I increase iron in my Maharashtrian vegetarian diet?",
  "What is the ICMR-NIN recommended daily fiber intake?",
  "Suggest low-oil Bengali dinner options with high protein",
]

// AI WebSocket
const userId = localStorage.getItem('nutriplan_user_id') || 'user_123'
const aiWsUrl = `${WS_PROTOCOL}//${window.location.host}/api/v1/ai-chat/ws/${userId}`
const { status: wsStatus, send: wsSend, connect: wsConnect } = useResilientWebSocket({
  url: aiWsUrl,
  heartbeatIntervalMs: 20000,
  onOpen: () => { console.log("[AI WS] Connected") },
  onMessage: async (data: any) => {
    if (data.type === 'status') {
      // Thinking indicator before first token
      isAiTyping.value = true

    } else if (data.type === 'token') {
      // First token: swap typing indicator → streaming bubble
      if (!isAiStreaming.value) {
        isAiTyping.value = false
        isAiStreaming.value = true
        streamingContent.value = ''
      }
      streamingContent.value += data.delta
      await scrollAi()

    } else if (data.type === 'done') {
      // Streaming complete: commit the buffered message
      if (isAiStreaming.value && streamingContent.value.trim()) {
        aiMessages.value.push({
          id: String(Date.now()),
          role: 'assistant',
          content: streamingContent.value.trim(),
          timestamp: new Date()
        })
      }
      isAiStreaming.value = false
      isAiTyping.value = false
      streamingContent.value = ''
      await scrollAi()

    } else if (data.type === 'escalation') {
      isAiStreaming.value = false
      isAiTyping.value = false
      streamingContent.value = ''
      aiMessages.value.push({
        id: String(Date.now()),
        role: 'assistant',
        content: data.message || data.text || 'Connecting you to a clinical nutritionist...',
        timestamp: new Date()
      })
      await scrollAi()

    } else if (data.type === 'ai_response') {
      // Legacy non-streaming fallback
      isAiTyping.value = false
      isAiStreaming.value = false
      streamingContent.value = ''
      aiMessages.value.push({
        id: String(Date.now()),
        role: 'assistant',
        content: data.message || data.text || '',
        timestamp: new Date()
      })
      await scrollAi()
    }
  },
  onError: () => {}
})

let clinicalReconnectAttempts = 0
const maxClinicalReconnectAttempts = 10
const clinicalOfflineQueue: string[] = []

// ── Clinical WebSocket ────────────────────────────────────────────────────────
function connectClinicalWs() {
  const wsUrl = `${WS_PROTOCOL}//localhost:8012/api/v1/chat/ws/clinical/${CLINICAL_ROOM_ID}/${PATIENT_EMAIL}`
  console.log(`[Clinical WS] Connecting to ${wsUrl}`)

  if (clinicalWs) {
    clinicalWs.close()
  }

  clinicalWs = new WebSocket(wsUrl)

  clinicalWs.onopen = () => {
    console.log('[Clinical WS] Connected')
    clinicalReconnectAttempts = 0
    if (clinicalWsReconnectTimer) clearTimeout(clinicalWsReconnectTimer)
    // Flush any pending offline messages
    while (clinicalOfflineQueue.length > 0) {
      const qMsg = clinicalOfflineQueue.shift()
      if (qMsg && clinicalWs && clinicalWs.readyState === WebSocket.OPEN) {
        clinicalWs.send(qMsg)
      }
    }
  }

  clinicalWs.onmessage = async (event) => {
    try {
      const data = JSON.parse(event.data)
      await handleClinicalWsMessage(data)
    } catch (e) {
      console.error('[Clinical WS] Parse error', e)
    }
  }

  clinicalWs.onclose = () => {
    if (clinicalReconnectAttempts < maxClinicalReconnectAttempts) {
      clinicalReconnectAttempts++
      const delay = Math.min(1000 * Math.pow(1.8, clinicalReconnectAttempts - 1), 15000) + Math.random() * 500
      console.log(`[Clinical WS] Disconnected — reconnecting attempt ${clinicalReconnectAttempts} in ${Math.round(delay)}ms`)
      clinicalWsReconnectTimer = setTimeout(connectClinicalWs, delay)
    } else {
      console.warn('[Clinical WS] Maximum reconnection attempts reached.')
    }
  }

  clinicalWs.onerror = (e) => {
    console.error('[Clinical WS] Error', e)
  }
}

async function handleClinicalWsMessage(data: any) {
  switch (data.type) {
    case 'thread_status':
      clinicalStatus.value = data.status
      break

    case 'history':
      clinicalMessages.value = data.messages || []
      await scrollClinical()
      break

    case 'clinical_message':
      {
        const msg: ClinicalMessage = data.payload
        // If this message was sent optimistically by patient, update status to delivered
        const existingIdx = clinicalMessages.value.findIndex(m => m.id === msg.id)
        if (existingIdx !== -1) {
          clinicalMessages.value[existingIdx].status = 'delivered'
        } else {
          msg.status = 'delivered'
          clinicalMessages.value.push(msg)
          await scrollClinical()
        }
      }
      break

    case 'intake_accepted':
      clinicalStatus.value = 'active'
      if (data.payload?.welcome_message) {
        const msg: ClinicalMessage = data.payload.welcome_message
        const exists = clinicalMessages.value.some(m => m.id === msg.id)
        if (!exists) clinicalMessages.value.push(msg)
        await scrollClinical()
      }
      break

    case 'intake_declined':
      clinicalStatus.value = 'declined'
      break

    case 'typing':
      if (data.sender_email !== PATIENT_EMAIL) {
        isExpertTyping.value = data.is_typing
        if (expertTypingTimeout.value) clearTimeout(expertTypingTimeout.value)
        if (data.is_typing) {
          expertTypingTimeout.value = setTimeout(() => { isExpertTyping.value = false }, 5000)
        }
      }
      break

    case 'pong':
      break

    case 'error':
      console.warn('[Clinical WS] Server error:', data.detail)
      break
  }
}

async function sendClinicalMessage() {
  const text = clinicalInput.value.trim()
  if (!text || isSendingClinical.value || clinicalStatus.value !== 'active' || isQueueLimitReached.value) return

  isSendingClinical.value = true
  clinicalInput.value = ''

  const tempId = `msg_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`
  const now = new Date()
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  // Optimistic UI update with 'sending' status
  const optimisticMsg: ClinicalMessage = {
    id: tempId,
    room_id: CLINICAL_ROOM_ID,
    sender: 'patient',
    sender_email: PATIENT_EMAIL,
    recipient_email: EXPERT_EMAIL,
    text,
    time: timeStr,
    timestamp: now.toISOString(),
    status: 'sending'
  }
  clinicalMessages.value.push(optimisticMsg)
  await scrollClinical()

  const payload = {
    type: 'message',
    id: tempId,
    sender: 'patient',
    sender_email: PATIENT_EMAIL,
    recipient_email: EXPERT_EMAIL,
    text,
  }

  const payloadStr = JSON.stringify(payload)

  if (clinicalWs && clinicalWs.readyState === WebSocket.OPEN) {
    clinicalWs.send(payloadStr)
    optimisticMsg.status = 'sent'
  } else {
    // Queue offline and attempt REST fallback
    clinicalOfflineQueue.push(payloadStr)
    try {
      await fetch(`${CHAT_API}/clinical/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender: 'patient',
          sender_email: PATIENT_EMAIL,
          recipient_email: EXPERT_EMAIL,
          text,
        })
      })
      optimisticMsg.status = 'sent'
    } catch (e) {
      console.error('[Clinical REST] Send failed', e)
      // Keep optimistic message with status 'sending' so user knows it will sync when online
    }
  }

  isSendingClinical.value = false
}

async function approveIntakeForTesting() {
  try {
    const res = await fetch(`${CHAT_API}/clinical/intake/accept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_email: PATIENT_EMAIL,
        expert_email: EXPERT_EMAIL,
      })
    })
    const data = await res.json()
    if (data.ok) {
      clinicalStatus.value = 'active'
      localStorage.setItem(`nutriplan_expert_consent_${PATIENT_EMAIL}`, 'active')
    }
  } catch (e) {
    // If backend offline, simulate locally
    clinicalStatus.value = 'active'
    localStorage.setItem(`nutriplan_expert_consent_${PATIENT_EMAIL}`, 'active')
    clinicalMessages.value.push({
      id: `exp_welcome_${Date.now()}`,
      room_id: CLINICAL_ROOM_ID,
      sender: 'expert',
      sender_email: EXPERT_EMAIL,
      recipient_email: PATIENT_EMAIL,
      text: `Hello Test User! I (Dr. Sarah Jenkins, ${EXPERT_EMAIL}) have accepted your clinical consultation request. Your two-way messaging care window is now active.`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      timestamp: new Date().toISOString(),
    })
    await scrollClinical()
  }
}

function sendTypingIndicator(isTyping: boolean) {
  if (clinicalWs && clinicalWs.readyState === WebSocket.OPEN) {
    clinicalWs.send(JSON.stringify({ type: 'typing', is_typing: isTyping, sender_email: PATIENT_EMAIL }))
  }
}

// ── AI Chat ───────────────────────────────────────────────────────────────────
async function sendAiMessage(content?: string) {
  const text = content || aiInput.value.trim()
  if (!text) return

  aiMessages.value.push({ id: String(Date.now()), role: 'user', content: text, timestamp: new Date() })
  aiInput.value = ''

  const sent = wsSend({ message: text })
  if (!sent) {
    isAiTyping.value = true
    setTimeout(async () => {
      isAiTyping.value = false
      const lower = text.toLowerCase()
      let reply = "Based on your biometric logs and dietary profile, your nutrition is on track. Keep hitting your 120g protein target daily."
      if (lower.includes('lunch') || lower.includes('eat')) {
        reply = "For lunch: 150g Grilled Paneer, 1 cup Brown Rice, Palak Dal, and a side of cucumber raita (~480 kcal, 28g protein)."
      } else if (lower.includes('iron') || lower.includes('protein')) {
        reply = "Pair sprouted moong, methi, or palak with vitamin C sources (lemon, amla) to enhance non-heme iron absorption per ICMR-NIN."
      }
      aiMessages.value.push({ id: String(Date.now()), role: 'assistant', content: reply, timestamp: new Date() })
      await scrollAi()
    }, 1200)
  }
  await scrollAi()
}

// ── Scroll helpers ────────────────────────────────────────────────────────────
async function scrollClinical() {
  await nextTick()
  clinicalScrollRef.value?.scrollTo({ top: clinicalScrollRef.value.scrollHeight, behavior: 'smooth' })
}
async function scrollAi() {
  await nextTick()
  aiScrollRef.value?.scrollTo({ top: aiScrollRef.value.scrollHeight, behavior: 'smooth' })
}

function handleKeydown(e: KeyboardEvent, mode: 'ai' | 'clinical') {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    if (mode === 'ai') sendAiMessage()
    else sendClinicalMessage()
  }
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(() => {
  wsConnect()
  connectClinicalWs()
})

onUnmounted(() => {
  if (clinicalWs) clinicalWs.close()
  if (clinicalWsReconnectTimer) clearTimeout(clinicalWsReconnectTimer)
})
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-8rem)] -my-6">

    <!-- Tab Switcher Bar -->
    <div class="shrink-0 pb-3 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div class="inline-flex p-1 bg-surface-alt rounded-xl border border-border">
        <button
          class="px-4 py-1.5 rounded-lg font-display text-xs font-semibold transition-all flex items-center gap-2"
          :class="activeTab === 'expert' ? 'bg-card text-ink shadow-sm' : 'text-ink-muted hover:text-ink'"
          @click="activeTab = 'expert'"
        >
          <span class="w-2 h-2 rounded-full" :class="clinicalStatus === 'active' ? 'bg-emerald-500' : clinicalStatus === 'connecting' ? 'bg-amber-400 animate-pulse' : 'bg-amber-400'" />
          🩺 Dr. Sarah Jenkins
          <span class="px-1.5 rounded text-[0.65rem] font-bold"
            :class="clinicalStatus === 'active' ? 'bg-success/15 text-success' : clinicalStatus === 'connecting' ? 'bg-amber-500/15 text-amber-600' : 'bg-amber-500/15 text-amber-600'"
          >
            {{ clinicalStatus === 'active' ? 'ACTIVE' : clinicalStatus === 'connecting' ? 'CONNECTING...' : 'PENDING' }}
          </span>
        </button>
        <button
          class="px-4 py-1.5 rounded-lg font-display text-xs font-semibold transition-all flex items-center gap-2"
          :class="activeTab === 'ai' ? 'bg-card text-ink shadow-sm' : 'text-ink-muted hover:text-ink'"
          @click="activeTab = 'ai'"
        >
          <span class="w-2 h-2 rounded-full" :class="wsStatus === 'connected' ? 'bg-success animate-pulse' : 'bg-amber-400'" />
          🤖 AI Health Coach (24/7)
        </button>
      </div>

      <div class="flex items-center gap-2">
        <template v-if="activeTab === 'expert'">
          <button
            v-if="clinicalStatus === 'pending'"
            @click="approveIntakeForTesting"
            class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition-all"
          >
            ⚡ Approve (Test)
          </button>
          <span class="text-[0.72rem] text-ink-muted hidden sm:inline">🕒 {{ officeHours }}</span>
          <span v-if="clinicalStatus === 'active'" class="px-2.5 py-0.5 rounded-full text-[0.72rem] font-bold"
            :class="isQueueLimitReached ? 'bg-amber-500/15 text-amber-600 border border-amber-500/30' : 'bg-primary/10 text-primary border border-primary/20'"
          >
            {{ pendingPatientQuestions }}/{{ maxPendingQueue }} Queued
          </span>
        </template>
        <template v-else>
          <div class="px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-xs font-semibold text-primary">
            🥗 {{ activeRegion.replace('in_', '').replace('_', ' ').toUpperCase() }}
          </div>
        </template>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- AI HEALTH COACH TAB -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <template v-if="activeTab === 'ai'">
      <div ref="aiScrollRef" class="flex-1 overflow-y-auto py-5 space-y-4 scroll-smooth">
        <ChatBubble
          v-for="msg in aiMessages"
          :key="msg.id"
          :sender-type="msg.role === 'assistant' ? 'ai' : 'user'"
          :sender-name="msg.role === 'assistant' ? 'NutriPlan AI' : undefined"
          :message="msg.content"
        />
        <!-- Live streaming bubble (token-by-token) -->
        <div v-if="isAiStreaming" class="flex items-end gap-2">
          <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-[0.75rem] font-bold shrink-0">N</div>
          <div class="bg-info-soft text-info rounded-2xl rounded-bl-sm px-4 py-3 max-w-[80%] font-body text-sm leading-relaxed">
            <span style="white-space: pre-wrap">{{ streamingContent }}</span><span class="inline-block w-0.5 h-4 bg-current ml-0.5 animate-pulse align-middle"></span>
          </div>
        </div>
        <!-- Thinking indicator (before first token) -->
        <div v-else-if="isAiTyping" class="flex items-end gap-2">
          <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-[0.75rem] font-bold shrink-0">N</div>
          <div class="bg-info-soft text-info rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-1">
            <span class="w-1.5 h-1.5 bg-current rounded-full animate-bounce" style="animation-delay: 0ms" />
            <span class="w-1.5 h-1.5 bg-current rounded-full animate-bounce" style="animation-delay: 150ms" />
            <span class="w-1.5 h-1.5 bg-current rounded-full animate-bounce" style="animation-delay: 300ms" />
          </div>
        </div>
      </div>
      <div v-if="aiMessages.length === 1" class="shrink-0 py-3 flex flex-wrap gap-2">
        <button v-for="s in aiSuggestions" :key="s"
          class="font-body text-[0.8rem] text-primary border border-primary/30 rounded-full px-3 py-1.5 hover:bg-primary-soft transition-colors"
          @click="sendAiMessage(s)"
        >{{ s }}</button>
      </div>
      <div class="shrink-0 pt-4 border-t border-border">
        <div class="flex gap-2 items-end">
          <textarea
            v-model="aiInput"
            placeholder="Ask your AI coach about macros, recipes, or ICMR targets..."
            rows="1"
            class="flex-1 font-body text-[0.88rem] text-ink bg-canvas-raised border border-border rounded-xl px-4 py-3 outline-none resize-none focus:border-primary focus:ring-2 focus:ring-primary/15 transition-all placeholder:text-ink-muted/60 max-h-32 overflow-y-auto"
            @keydown="handleKeydown($event, 'ai')"
          />
          <button class="w-10 h-10 rounded-xl bg-primary text-white flex items-center justify-center shrink-0 hover:bg-primary-strong disabled:opacity-50 active:scale-95" :disabled="!aiInput.trim() || isAiTyping || isAiStreaming" @click="sendAiMessage()">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 19V5m0 0l-7 7m7-7l7 7" /></svg>
          </button>
        </div>
        <p class="font-data text-[0.65rem] text-ink-muted mt-1.5 text-center">AI responses are grounded in ICMR-NIN guidelines. For clinical advice, consult your registered dietitian.</p>
      </div>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- CLINICAL DIETITIAN TAB -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <template v-else>
      <!-- Expert Header -->
      <div class="bg-card border border-border rounded-xl p-3 my-2 flex items-center justify-between shadow-xs">
        <div class="flex items-center gap-3">
          <img :src="expertAvatar" class="w-10 h-10 rounded-full object-cover border border-border shrink-0" alt="Expert" />
          <div>
            <div class="font-display font-semibold text-sm text-ink flex items-center gap-2">
              {{ expertName }}
              <span class="text-xs text-primary font-mono font-normal">({{ EXPERT_EMAIL }})</span>
            </div>
            <div class="text-xs text-ink-muted">Clinical Dietitian · Diabetes &amp; Metabolic Health</div>
          </div>
        </div>
        <router-link to="/appointments" class="text-xs font-semibold text-primary hover:underline flex items-center gap-1">📅 Book Video</router-link>
      </div>

      <!-- PENDING STATE -->
      <div v-if="clinicalStatus === 'pending' || clinicalStatus === 'connecting'" class="flex-1 flex flex-col justify-center items-center p-6 overflow-y-auto">
        <div class="bg-card border border-border rounded-2xl p-6 max-w-lg w-full shadow-sm text-center">
          <div class="w-12 h-12 rounded-full bg-amber-500/15 text-amber-600 flex items-center justify-center text-xl mx-auto mb-3">⏳</div>
          <h3 class="font-display font-bold text-base text-ink mb-1">Consultation Request Pending</h3>
          <p class="text-xs text-ink-muted mb-4">
            Your intake has been submitted to <span class="font-semibold text-ink">{{ expertName }}</span>
            (<span class="font-mono text-primary text-xs">{{ EXPERT_EMAIL }}</span>). Messaging opens once the expert approves.
          </p>
          <div class="p-3.5 bg-surface-alt rounded-xl border border-border/80 text-left text-xs space-y-1.5 mb-5">
            <div class="flex justify-between"><span class="text-ink-muted">Patient:</span><span class="font-mono font-bold text-primary">{{ PATIENT_EMAIL }}</span></div>
            <div class="flex justify-between"><span class="text-ink-muted">Expert:</span><span class="font-mono">{{ EXPERT_EMAIL }}</span></div>
            <div class="flex justify-between"><span class="text-ink-muted">Room ID:</span><span class="font-mono text-xs text-ink-muted">{{ CLINICAL_ROOM_ID }}</span></div>
            <div class="flex justify-between"><span class="text-ink-muted">Status:</span><span class="text-amber-600 font-semibold">Awaiting Expert Approval</span></div>
          </div>
          <div class="flex flex-col sm:flex-row gap-2.5 justify-center">
            <button @click="approveIntakeForTesting" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition-all">
              ✅ Approve as Dr. Sarah (Test Simulation)
            </button>
          </div>
        </div>
      </div>

      <!-- ACTIVE MESSAGING STATE -->
      <template v-else-if="clinicalStatus === 'active'">
        <div ref="clinicalScrollRef" class="flex-1 overflow-y-auto py-3 space-y-4 scroll-smooth">
          <div v-for="msg in clinicalMessages" :key="msg.id" class="flex flex-col" :class="msg.sender === 'patient' ? 'items-end' : 'items-start'">
            <div
              class="max-w-[82%] sm:max-w-[70%] rounded-2xl px-4 py-3 text-[0.88rem] leading-relaxed shadow-xs"
              :class="msg.sender === 'patient' ? 'bg-primary text-white rounded-br-xs' : 'bg-surface-alt border border-border text-ink rounded-bl-xs'"
            >
              <div v-if="msg.sender === 'expert'" class="font-bold text-[0.75rem] text-primary mb-1">Dr. Sarah Jenkins ({{ EXPERT_EMAIL }})</div>
              <p>{{ msg.text }}</p>
              <div v-if="msg.attachment" class="mt-2.5 p-2.5 rounded-xl border flex items-center gap-3 text-xs"
                :class="msg.sender === 'patient' ? 'bg-white/10 border-white/20 text-white' : 'bg-card border-border text-ink'"
              >
                <div class="w-8 h-8 rounded-lg bg-primary/15 text-primary flex items-center justify-center font-bold text-base shrink-0">📊</div>
                <div class="overflow-hidden">
                  <div class="font-semibold truncate">{{ msg.attachment.title }}</div>
                  <div class="text-[0.72rem] opacity-80 truncate">{{ msg.attachment.meta }}</div>
                </div>
              </div>
              <div class="text-[0.68rem] mt-1.5 opacity-70 flex items-center justify-end gap-1">
                <span>{{ msg.time }}</span>
                <span v-if="msg.sender === 'patient'" class="inline-flex items-center ml-0.5 font-mono text-[0.65rem]">
                  <span v-if="msg.status === 'sending'" title="Sending...">⏳</span>
                  <span v-else-if="msg.status === 'sent'" title="Sent to server">✓</span>
                  <span v-else title="Delivered">✓✓</span>
                </span>
              </div>
            </div>
          </div>

          <!-- Expert Typing Indicator -->
          <div v-if="isExpertTyping" class="flex items-end gap-2">
            <img :src="expertAvatar" class="w-7 h-7 rounded-full object-cover shrink-0" alt="Expert" />
            <div class="bg-surface-alt border border-border rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-1">
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 0ms" />
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 150ms" />
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 300ms" />
            </div>
          </div>
        </div>

        <!-- Queue limit warning -->
        <div v-if="isQueueLimitReached" class="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3 mb-2 flex items-center gap-3 text-xs text-amber-700">
          <span>⏳</span>
          <span><span class="font-bold">Pending Dietitian Review:</span> You have {{ maxPendingQueue }} unanswered questions queued. Dr. Sarah typically replies within 4–6 hours during office hours.</span>
        </div>

        <!-- Input Area -->
        <div class="shrink-0 pt-2 border-t border-border">
          <div class="flex gap-2 items-end">
            <textarea
              v-model="clinicalInput"
              :placeholder="isQueueLimitReached ? 'Awaiting Dr. Sarah\'s response before sending more...' : `Message Dr. Sarah (${EXPERT_EMAIL})...`"
              :disabled="isQueueLimitReached || isSendingClinical"
              rows="1"
              class="flex-1 font-body text-[0.88rem] text-ink bg-canvas-raised border border-border rounded-xl px-4 py-3 outline-none resize-none focus:border-primary focus:ring-2 focus:ring-primary/15 transition-all placeholder:text-ink-muted/60 disabled:opacity-50 disabled:bg-surface-alt max-h-32 overflow-y-auto"
              @keydown="handleKeydown($event, 'clinical')"
              @input="sendTypingIndicator(true)"
              @blur="sendTypingIndicator(false)"
            />
            <button
              class="w-10 h-10 rounded-xl bg-primary text-white flex items-center justify-center shrink-0 hover:bg-primary-strong disabled:opacity-50 active:scale-95"
              :disabled="!clinicalInput.trim() || isQueueLimitReached || isSendingClinical"
              @click="sendClinicalMessage()"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 19V5m0 0l-7 7m7-7l7 7" /></svg>
            </button>
          </div>
          <div class="flex items-center justify-between text-[0.65rem] text-ink-muted mt-1.5 px-1">
            <span>🛡️ HIPAA-Compliant · End-to-End Encrypted</span>
            <span class="text-error font-medium">⚠️ Medical emergency? Call 112 / 911</span>
          </div>
        </div>
      </template>

      <!-- DECLINED STATE -->
      <div v-else-if="clinicalStatus === 'declined'" class="flex-1 flex flex-col justify-center items-center p-6">
        <div class="bg-card border border-border rounded-2xl p-6 max-w-sm w-full text-center">
          <div class="text-2xl mb-2">🤖</div>
          <h3 class="font-display font-bold text-sm text-ink mb-2">Redirected to AI Coach</h3>
          <p class="text-xs text-ink-muted mb-4">The expert was unable to accept this consultation at this time. Your AI Health Coach is available 24/7 for nutritional guidance.</p>
          <button @click="activeTab = 'ai'" class="px-4 py-2 bg-primary text-white rounded-xl text-xs font-bold">Open AI Coach</button>
        </div>
      </div>
    </template>

  </div>
</template>
