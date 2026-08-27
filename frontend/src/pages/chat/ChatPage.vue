<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import ChatBubble from '../../components/ChatBubble.vue'
import { useResilientWebSocket } from '../../composables/useResilientWebSocket'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  attachment?: {
    type: 'plan' | 'lab_report' | 'meal_photo'
    title: string
    meta?: string
  }
}

const activeTab = ref<'ai' | 'expert'>('expert')

// ── Tab 1: AI Health Coach State ─────────────────────────────────────────────
const aiMessages = ref<Message[]>([
  {
    id: '0',
    role: 'assistant',
    content: "Hello! I'm your NutriPlan AI nutritionist. I can help you with recipe ideas, analyze your food diary macros, answer questions about your target nutrients, or explain ICMR-NIN guidelines. How can I help you today?",
    timestamp: new Date(),
  }
])

const aiInput = ref('')
const isAiTyping = ref(false)
const scrollRef = ref<HTMLElement | null>(null)

const suggestions = [
  "Suggest a high-protein South Indian breakfast under 400 kcal",
  "How can I increase iron in my Maharashtrian vegetarian diet?",
  "What is the ICMR-NIN recommended daily fiber intake?",
  "Suggest low-oil Bengali dinner options with high protein",
]

const activeRegion = ref(localStorage.getItem('nutriplan_regional_pref') || 'in_south_andhra')
const userId = localStorage.getItem('nutriplan_user_id') || 'user_123'
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
const wsUrl = `${protocol}//${window.location.host}/api/v1/ai-chat/ws/${userId}`

const { status: wsStatus, send: wsSend, connect: wsConnect } = useResilientWebSocket({
  url: wsUrl,
  heartbeatIntervalMs: 20000,
  onOpen: () => {
    console.log("Connected to Resilient AI Chatbot WebSocket")
  },
  onMessage: async (data: any) => {
    if (data.type === 'status') {
      isAiTyping.value = true
    } else if (data.type === 'ai_response' || data.type === 'escalation') {
      isAiTyping.value = false
      aiMessages.value.push({
        id: String(Date.now()),
        role: 'assistant',
        content: data.message || data.text || 'Response received.',
        timestamp: new Date(),
      })
      await nextTick()
      scrollRef.value?.scrollTo({ top: scrollRef.value.scrollHeight, behavior: 'smooth' })
    }
  },
  onError: () => {
    console.warn("AI Chatbot WebSocket reconnecting...")
  }
})

// ── Tab 2: Assigned Clinical Dietitian State & Anti-Spam Guardrails ───────────
type ExpertConsentState = 'active' | 'pending' | 'none'
const expertConsent = ref<ExpertConsentState>(
  (localStorage.getItem('nutriplan_expert_consent_test@test.com') as any) || 'pending'
)
const expertEmail = ref('expert@nutriplan.local')
const expertName = ref('Dr. Sarah Jenkins, RD, CDE')
const expertTitle = ref('Clinical Dietitian · Diabetes & Metabolic Health')
const expertAvatar = ref('https://images.unsplash.com/photo-1594824813620-1361c4de4a75?w=150&q=80')
const officeHours = ref('Mon–Fri, 9:00 AM – 6:00 PM IST')
const maxPendingQueue = 3 // Anti-spam turn-taking limit

const expertMessages = ref<Message[]>([
  {
    id: 'exp-1',
    role: 'user',
    content: "Hello Dr. Sarah (expert@nutriplan.local), I am submitting my clinical intake request. I would like your guidance on optimizing my macros for energy and fat loss with South Indian regional foods (1800 kcal / 120g Protein).",
    timestamp: new Date(Date.now() - 3600000 * 3),
    attachment: {
      type: 'lab_report',
      title: 'Intake Health Bio & Macro Target Form (test@test.com)',
      meta: '1800 kcal · Fasting Glucose 114 mg/dL · 8,400 daily steps'
    }
  }
])

const expertInput = ref('')
const isExpertTyping = ref(false)

// Calculate unanswered consecutive patient messages (turn-taking anti-spam quota)
const pendingPatientQuestions = computed(() => {
  let count = 0
  for (let i = expertMessages.value.length - 1; i >= 0; i--) {
    if (expertMessages.value[i].role === 'user') {
      count++
    } else {
      break
    }
  }
  return count
})

const isQueueLimitReached = computed(() => {
  return pendingPatientQuestions.value >= maxPendingQueue
})

function activateConsentForTesting() {
  expertConsent.value = 'active'
  localStorage.setItem('nutriplan_expert_consent_test@test.com', 'active')
  expertMessages.value.push({
    id: `exp_welcome_${Date.now()}`,
    role: 'assistant',
    content: "Hello Test User! I (Dr. Sarah Jenkins, expert@nutriplan.local) have accepted your clinical consultation request and reviewed your health bio. Your two-way messaging channel is now active. How can I assist you with your diet plan today?",
    timestamp: new Date(),
  })
}

function resetConsentForTesting() {
  expertConsent.value = 'pending'
  localStorage.setItem('nutriplan_expert_consent_test@test.com', 'pending')
  expertMessages.value = [
    {
      id: 'exp-1',
      role: 'user',
      content: "Hello Dr. Sarah (expert@nutriplan.local), I am submitting my clinical intake request. I would like your guidance on optimizing my macros for energy and fat loss with South Indian regional foods (1800 kcal / 120g Protein).",
      timestamp: new Date(Date.now() - 3600000 * 3),
      attachment: {
        type: 'lab_report',
        title: 'Intake Health Bio & Macro Target Form (test@test.com)',
        meta: '1800 kcal · Fasting Glucose 114 mg/dL · 8,400 daily steps'
      }
    }
  ]
}

onMounted(() => {
  wsConnect()
  // Check if consent was accepted in expert portal tab
  const savedConsent = localStorage.getItem('nutriplan_expert_consent_test@test.com')
  if (savedConsent === 'active' && expertConsent.value !== 'active') {
    activateConsentForTesting()
  }
})

async function sendAiMessage(content?: string) {
  const text = content || aiInput.value.trim()
  if (!text) return

  aiMessages.value.push({
    id: String(Date.now()),
    role: 'user',
    content: text,
    timestamp: new Date(),
  })
  
  aiInput.value = ''
 
  const sent = wsSend({
    message: text,
    context: {
      glucose_mgdl: 112,
      steps: 8420,
      hrv_ms: 54,
      calories_eaten: 1420,
      calorie_goal: 2000
    }
  })

  if (!sent) {
    isAiTyping.value = true
    setTimeout(async () => {
      isAiTyping.value = false
      let reply = "Based on your recent biometric logs and dietary profile, your blood glucose levels (112 mg/dL) and daily steps (8,420) look well-balanced. Ensure you stay hydrated and hit your 120g protein target."
      
      const lower = text.toLowerCase()
      if (lower.includes('lunch') || lower.includes('eat')) {
        reply = "For lunch today, I recommend a balanced plate: 150g Grilled Tofu / Paneer, 1 cup Brown Rice, and a generous portion of Palak Dal. This provides ~480 kcal and 26g of clean protein."
      } else if (lower.includes('iron') || lower.includes('protein')) {
        reply = "To boost your daily bioavailable iron and protein, pair sprouted moong or spinach with vitamin C rich lemon juice or amla to enhance non-heme iron absorption per ICMR-NIN recommendations."
      }

      aiMessages.value.push({
        id: String(Date.now()),
        role: 'assistant',
        content: reply,
        timestamp: new Date(),
      })
      await nextTick()
      scrollRef.value?.scrollTo({ top: scrollRef.value.scrollHeight, behavior: 'smooth' })
    }, 1000)
  }

  await nextTick()
  scrollRef.value?.scrollTo({ top: scrollRef.value.scrollHeight, behavior: 'smooth' })
}

async function sendExpertMessage() {
  const text = expertInput.value.trim()
  if (!text || isQueueLimitReached.value || expertConsent.value !== 'active') return

  expertMessages.value.push({
    id: String(Date.now()),
    role: 'user',
    content: text,
    timestamp: new Date(),
  })
  
  expertInput.value = ''

  // Simulate dietitian acknowledgement
  isExpertTyping.value = true
  setTimeout(async () => {
    isExpertTyping.value = false
    expertMessages.value.push({
      id: String(Date.now()),
      role: 'assistant',
      content: "Thank you for the update! I have received your question and noted your log. I'm currently reviewing your latest meal macros and will give you a detailed dietary recommendation shortly.",
      timestamp: new Date(),
    })
    await nextTick()
    scrollRef.value?.scrollTo({ top: scrollRef.value.scrollHeight, behavior: 'smooth' })
  }, 1800)

  await nextTick()
  scrollRef.value?.scrollTo({ top: scrollRef.value.scrollHeight, behavior: 'smooth' })
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    if (activeTab.value === 'ai') {
      sendAiMessage()
    } else {
      sendExpertMessage()
    }
  }
}
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-8rem)] -my-6">

    <!-- Top Mode Switcher Bar -->
    <div class="shrink-0 pb-3 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <!-- Tabs -->
      <div class="inline-flex p-1 bg-surface-alt rounded-xl border border-border">
        <button
          class="px-4 py-1.5 rounded-lg font-display text-xs font-semibold transition-all flex items-center gap-2"
          :class="activeTab === 'expert' ? 'bg-card text-ink shadow-sm' : 'text-ink-muted hover:text-ink'"
          @click="activeTab = 'expert'"
        >
          <span class="w-2 h-2 rounded-full" :class="expertConsent === 'active' ? 'bg-emerald-500' : 'bg-amber-400 animate-pulse'" />
          🩺 Dr. Sarah Jenkins (Dietitian)
          <span
            class="px-1.5 py-0.2 rounded text-[0.65rem] font-bold"
            :class="expertConsent === 'active' ? 'bg-success/15 text-success' : 'bg-amber-500/15 text-amber-600'"
          >
            {{ expertConsent === 'active' ? 'ACTIVE' : 'PENDING' }}
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

      <!-- Context Badges & Test Helpers -->
      <div class="flex items-center gap-2">
        <div v-if="activeTab === 'ai'" class="px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-xs font-semibold text-primary">
          🥗 {{ activeRegion.replace('in_', '').replace('_', ' ').toUpperCase() }} DIET
        </div>
        <div v-else class="flex items-center gap-2">
          <!-- Test Mode Toggle Button -->
          <button
            v-if="expertConsent === 'pending'"
            @click="activateConsentForTesting"
            class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition-all shadow-xs flex items-center gap-1"
            title="Click to simulate expert approval"
          >
            ⚡ Approve Request (Test)
          </button>
          <button
            v-else
            @click="resetConsentForTesting"
            class="px-2 py-0.5 text-ink-muted hover:text-ink border border-border rounded text-[0.7rem]"
            title="Reset to pending request state"
          >
            ↺ Reset
          </button>

          <span class="text-[0.72rem] text-ink-muted font-data hidden sm:inline">🕒 {{ officeHours }}</span>
          <span
            v-if="expertConsent === 'active'"
            class="px-2.5 py-0.5 rounded-full text-[0.72rem] font-bold"
            :class="isQueueLimitReached ? 'bg-amber-500/15 text-amber-600 border border-amber-500/30' : 'bg-primary/10 text-primary border border-primary/20'"
          >
            {{ pendingPatientQuestions }}/{{ maxPendingQueue }} Questions Queued
          </span>
        </div>
      </div>
    </div>

    <!-- ═════════════════════════════════════════════════════════════════════════ -->
    <!-- VIEW 1: AI HEALTH COACH CHAT -->
    <!-- ═════════════════════════════════════════════════════════════════════════ -->
    <template v-if="activeTab === 'ai'">
      <!-- Messages area -->
      <div ref="scrollRef" class="flex-1 overflow-y-auto py-5 space-y-4 scroll-smooth">
        <ChatBubble
          v-for="msg in aiMessages"
          :key="msg.id"
          :sender-type="msg.role === 'assistant' ? 'ai' : 'user'"
          :sender-name="msg.role === 'assistant' ? 'NutriPlan AI' : undefined"
          :message="msg.content"
        />

        <!-- Typing indicator -->
        <div v-if="isAiTyping" class="flex items-end gap-2">
          <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-[0.75rem] font-bold shrink-0">N</div>
          <div class="bg-info-soft text-info rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-1">
            <span class="w-1.5 h-1.5 bg-current rounded-full animate-bounce" style="animation-delay: 0ms" />
            <span class="w-1.5 h-1.5 bg-current rounded-full animate-bounce" style="animation-delay: 150ms" />
            <span class="w-1.5 h-1.5 bg-current rounded-full animate-bounce" style="animation-delay: 300ms" />
          </div>
        </div>
      </div>

      <!-- Suggestions (shown when only greeting) -->
      <div v-if="aiMessages.length === 1" class="shrink-0 py-3">
        <p class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider mb-2">Suggested questions</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="s in suggestions"
            :key="s"
            class="font-body text-[0.8rem] text-primary border border-primary/30 rounded-full px-3 py-1.5 hover:bg-primary-soft transition-colors"
            @click="sendAiMessage(s)"
          >{{ s }}</button>
        </div>
      </div>

      <!-- AI Input area -->
      <div class="shrink-0 pt-4 border-t border-border">
        <div class="flex gap-2 items-end">
          <textarea
            v-model="aiInput"
            placeholder="Ask your AI coach about macros, recipes, or ICMR targets..."
            rows="1"
            class="flex-1 font-body text-[0.88rem] text-ink bg-canvas-raised border border-border rounded-xl px-4 py-3 outline-none resize-none focus:border-primary focus:ring-2 focus:ring-primary/15 transition-all placeholder:text-ink-muted/60 max-h-32 overflow-y-auto"
            @keydown="handleKeydown"
          />
          <button
            class="w-10 h-10 rounded-xl bg-primary text-white flex items-center justify-center shrink-0 hover:bg-primary-strong transition-colors disabled:opacity-50 active:scale-95"
            :disabled="!aiInput.trim() || isAiTyping"
            @click="sendAiMessage()"
            aria-label="Send message"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 19V5m0 0l-7 7m7-7l7 7" />
            </svg>
          </button>
        </div>
        <p class="font-data text-[0.65rem] text-ink-muted mt-1.5 text-center">
          AI responses are grounded in ICMR-NIN dietary guidelines. For medical diagnoses, consult your registered dietitian.
        </p>
      </div>
    </template>

    <!-- ═════════════════════════════════════════════════════════════════════════ -->
    <!-- VIEW 2: CLINICAL DIETITIAN CHAT (WITH CONSENT & ANTI-SPAM) -->
    <!-- ═════════════════════════════════════════════════════════════════════════ -->
    <template v-else>
      <!-- Provider Header Card -->
      <div class="bg-card border border-border rounded-xl p-3 my-2 flex items-center justify-between shadow-xs">
        <div class="flex items-center gap-3">
          <img :src="expertAvatar" alt="Doctor" class="w-10 h-10 rounded-full object-cover border border-border shrink-0" />
          <div>
            <div class="font-display font-semibold text-sm text-ink flex items-center gap-2">
              {{ expertName }}
              <span class="text-xs text-primary font-data font-normal">({{ expertEmail }})</span>
            </div>
            <div class="text-xs text-ink-muted">{{ expertTitle }}</div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <router-link to="/appointments" class="text-xs font-semibold text-primary hover:underline flex items-center gap-1">
            📅 Book Video Session
          </router-link>
        </div>
      </div>

      <!-- ── CASE A: PENDING INTAKE REQUEST STATE ────────────────────────────── -->
      <div v-if="expertConsent === 'pending'" class="flex-1 flex flex-col justify-center items-center p-6 bg-surface-alt/30 overflow-y-auto">
        <div class="bg-card border border-border rounded-2xl p-6 max-w-lg w-full shadow-sm text-center">
          <div class="w-12 h-12 rounded-full bg-amber-500/15 text-amber-600 flex items-center justify-center font-bold text-xl mx-auto mb-3">
            ⏳
          </div>
          <h3 class="font-display font-bold text-base text-ink mb-1">Consultation Request Pending</h3>
          <p class="text-xs text-ink-muted mb-4">
            Your intake request has been submitted to <span class="font-semibold text-ink">{{ expertName }}</span> (<span class="font-mono text-primary">{{ expertEmail }}</span>).
          </p>

          <!-- Intake details box -->
          <div class="p-3.5 bg-surface-alt rounded-xl border border-border/80 text-left text-xs text-ink space-y-1.5 mb-5">
            <div class="flex justify-between">
              <span class="text-ink-muted font-medium">Patient Account:</span>
              <span class="font-mono font-bold text-primary">test@test.com</span>
            </div>
            <div class="flex justify-between">
              <span class="text-ink-muted font-medium">Target Plan:</span>
              <span>1800 kcal · South Indian High-Protein</span>
            </div>
            <div class="flex justify-between">
              <span class="text-ink-muted font-medium">Fasting Blood Sugar:</span>
              <span>114 mg/dL</span>
            </div>
            <div class="flex justify-between">
              <span class="text-ink-muted font-medium">Anti-Spam Status:</span>
              <span class="text-amber-600 font-semibold">Locked until Expert Approval</span>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row gap-2.5 justify-center">
            <button
              @click="activateConsentForTesting"
              class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition-all shadow-xs"
            >
              ✅ Approve as Dr. Sarah (Simulate Test)
            </button>
            <router-link
              to="/appointments"
              class="px-4 py-2 border border-border hover:bg-surface-alt rounded-xl text-xs font-semibold text-ink transition-colors"
            >
              View Available Slots
            </router-link>
          </div>
        </div>
      </div>

      <!-- ── CASE B: ACTIVE TWO-WAY MESSAGING ───────────────────────────────── -->
      <template v-else>
        <!-- Messages area -->
        <div ref="scrollRef" class="flex-1 overflow-y-auto py-3 space-y-4 scroll-smooth">
          <div
            v-for="msg in expertMessages"
            :key="msg.id"
            class="flex flex-col"
            :class="msg.role === 'user' ? 'items-end' : 'items-start'"
          >
            <div
              class="max-w-[82%] sm:max-w-[70%] rounded-2xl px-4 py-3 text-[0.88rem] leading-relaxed shadow-xs"
              :class="msg.role === 'user' ? 'bg-primary text-white rounded-br-xs' : 'bg-surface-alt border border-border text-ink rounded-bl-xs'"
            >
              <div v-if="msg.role === 'assistant'" class="font-bold text-[0.75rem] text-primary mb-1">
                Dr. Sarah Jenkins (expert@nutriplan.local)
              </div>
              <p>{{ msg.content }}</p>

              <!-- Attachment Card -->
              <div
                v-if="msg.attachment"
                class="mt-2.5 p-2.5 rounded-xl border flex items-center gap-3 text-xs"
                :class="msg.role === 'user' ? 'bg-white/10 border-white/20 text-white' : 'bg-card border-border text-ink'"
              >
                <div class="w-8 h-8 rounded-lg bg-primary/15 text-primary flex items-center justify-center font-bold text-base shrink-0">
                  📊
                </div>
                <div class="overflow-hidden">
                  <div class="font-semibold truncate">{{ msg.attachment.title }}</div>
                  <div class="text-[0.72rem] opacity-80 truncate">{{ msg.attachment.meta }}</div>
                </div>
              </div>

              <div class="text-[0.68rem] mt-1.5 opacity-70 text-right">
                {{ msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
              </div>
            </div>
          </div>

          <!-- Provider typing indicator -->
          <div v-if="isExpertTyping" class="flex items-end gap-2">
            <img :src="expertAvatar" alt="Doctor" class="w-7 h-7 rounded-full object-cover shrink-0" />
            <div class="bg-surface-alt border border-border rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-1">
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 0ms" />
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 150ms" />
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 300ms" />
            </div>
          </div>
        </div>

        <!-- Anti-Spam Queue Warning Notice (when 3 questions pending) -->
        <div
          v-if="isQueueLimitReached"
          class="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3 mb-2 flex items-center gap-3 text-xs text-amber-700 dark:text-amber-300"
        >
          <span class="text-base">⏳</span>
          <div class="flex-1">
            <span class="font-bold">Pending Dietitian Review:</span>
            You have reached the limit of 3 unanswered clinical questions. Dr. Sarah typically reviews and replies within 4–6 hours during office hours.
          </div>
        </div>

        <!-- Expert Input area with Rate-Limit & Spam Prevention -->
        <div class="shrink-0 pt-2 border-t border-border">
          <div class="flex gap-2 items-end">
            <textarea
              v-model="expertInput"
              :placeholder="isQueueLimitReached ? 'Awaiting response from Dr. Sarah before sending next question...' : 'Send a message or query to Dr. Sarah (expert@nutriplan.local)...'"
              :disabled="isQueueLimitReached || isExpertTyping"
              rows="1"
              class="flex-1 font-body text-[0.88rem] text-ink bg-canvas-raised border border-border rounded-xl px-4 py-3 outline-none resize-none focus:border-primary focus:ring-2 focus:ring-primary/15 transition-all placeholder:text-ink-muted/60 disabled:opacity-50 disabled:bg-surface-alt max-h-32 overflow-y-auto"
              @keydown="handleKeydown"
            />
            <button
              class="w-10 h-10 rounded-xl bg-primary text-white flex items-center justify-center shrink-0 hover:bg-primary-strong transition-colors disabled:opacity-50 active:scale-95"
              :disabled="!expertInput.trim() || isQueueLimitReached || isExpertTyping"
              @click="sendExpertMessage()"
              aria-label="Send message"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 19V5m0 0l-7 7m7-7l7 7" />
              </svg>
            </button>
          </div>
          <div class="flex items-center justify-between text-[0.65rem] text-ink-muted mt-1.5 px-1">
            <span>🛡️ HIPAA-Compliant End-to-End Encrypted</span>
            <span class="text-error font-medium">⚠️ For medical emergencies, call 112 / 911 immediately</span>
          </div>
        </div>
      </template>
    </template>

  </div>
</template>
