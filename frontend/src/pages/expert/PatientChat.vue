<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'
import apiClient from '../../api'

interface PatientContact {
  id: string
  name: string
  avatar: string
  condition: string
  unreadCount: number
  lastMessage: string
  lastTime: string
  online: boolean
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
    online: true
  },
  {
    id: 'usr_2',
    name: 'Priya Patel',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&q=80',
    condition: 'PCOS & Insulin Resistance',
    unreadCount: 0,
    lastMessage: 'Got the new cooked veggie plan. Feeling much less bloated!',
    lastTime: 'Yesterday',
    online: false
  },
  {
    id: 'usr_3',
    name: 'Amit Kumar',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&q=80',
    condition: 'Sports Hypertrophy',
    unreadCount: 0,
    lastMessage: 'Hit 140g protein yesterday with the paneer + sattu shake.',
    lastTime: '2 days ago',
    online: true
  },
  {
    id: 'usr_4',
    name: 'Sneha Desai',
    avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&q=80',
    condition: 'Cardiovascular / DASH Diet',
    unreadCount: 0,
    lastMessage: 'Uploaded my 7-day sodium diary report for review.',
    lastTime: '3 days ago',
    online: false
  }
])

const activePatientId = ref('usr_1')
const activePatient = computed(() => patients.value.find(p => p.id === activePatientId.value) || patients.value[0])

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
        title: 'Continuous Glucose Monitor 24h Trend',
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
  ]
})

const currentMessages = computed(() => conversations.value[activePatientId.value] || [])

function selectPatient(patient: PatientContact) {
  activePatientId.value = patient.id
  patient.unreadCount = 0
  scrollToBottom()
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text) return

  const newMsg: Message = {
    id: `msg_${Date.now()}`,
    sender: 'expert',
    text: text,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    status: 'sent'
  }

  if (!conversations.value[activePatientId.value]) {
    conversations.value[activePatientId.value] = []
  }
  conversations.value[activePatientId.value].push(newMsg)
  inputMessage.value = ''
  scrollToBottom()

  // Send to backend chat API
  try {
    isSending.value = true
    await apiClient.post('/chat/send', {
      content: `[Expert Note to ${activePatient.value.name}]: ${text}`,
      user_id: activePatientId.value
    })
  } catch (e) {
    // Local state already updated
  } finally {
    isSending.value = false
  }
}

function sendQuickPrescription() {
  const prescriptionMsg: Message = {
    id: `msg_${Date.now()}`,
    sender: 'expert',
    text: 'I have reviewed your logs and assigned a revised clinical meal plan directly to your app schedule.',
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    attachment: {
      type: 'plan',
      title: 'Clinical High-Protein Diabetic Protocol (1,750 kcal)',
      meta: 'Prescribed by Dr. Sarah Jenkins · P: 130g | C: 150g | F: 55g'
    }
  }
  conversations.value[activePatientId.value].push(prescriptionMsg)
  scrollToBottom()
  notify(`Sent clinical prescription card to ${activePatient.value.name}!`)
}

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="h-[750px] bg-canvas-raised border border-border rounded-2xl shadow-card overflow-hidden grid grid-cols-1 md:grid-cols-12">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- ── LEFT SIDEBAR: PATIENT ROSTER (4 cols) ─────────────────────── -->
    <div class="md:col-span-4 border-r border-border flex flex-col h-full bg-canvas/40">
      <!-- Search & Filter Header -->
      <div class="p-4 border-b border-border bg-canvas-raised">
        <div class="flex items-center justify-between mb-3">
          <h2 class="font-display font-bold text-[1.1rem] text-ink">Patient Conversations</h2>
          <span class="px-2 py-0.5 rounded-full text-[0.72rem] font-bold bg-primary-soft text-primary">
            {{ patients.length }} Active
          </span>
        </div>
        <div class="relative">
          <input
            type="text"
            placeholder="Search patient or condition..."
            class="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-canvas border border-border text-ink placeholder:text-ink-muted outline-none focus:border-primary transition-colors"
          />
          <span class="absolute left-3 top-2.5 text-ink-muted">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </span>
        </div>
      </div>

      <!-- Patient Cards List -->
      <div class="flex-1 overflow-y-auto divide-y divide-border/60">
        <div
          v-for="p in patients"
          :key="p.id"
          @click="selectPatient(p)"
          class="p-3.5 flex items-start gap-3 cursor-pointer transition-all hover:bg-canvas-raised"
          :class="activePatientId === p.id ? 'bg-primary-soft/30 border-l-4 border-primary' : ''"
        >
          <div class="relative shrink-0">
            <img :src="p.avatar" :alt="p.name" class="w-11 h-11 rounded-full object-cover border border-border" />
            <span
              v-if="p.online"
              class="absolute bottom-0 right-0 w-3 h-3 bg-success rounded-full border-2 border-canvas"
            ></span>
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <h3 class="font-display font-semibold text-sm text-ink truncate">{{ p.name }}</h3>
              <span class="font-data text-[0.7rem] text-ink-muted shrink-0">{{ p.lastTime }}</span>
            </div>
            <div class="text-[0.72rem] font-medium text-primary mb-1">{{ p.condition }}</div>
            <p class="font-body text-xs text-ink-muted truncate">{{ p.lastMessage }}</p>
          </div>

          <span
            v-if="p.unreadCount > 0"
            class="w-5 h-5 rounded-full bg-primary text-white text-[0.68rem] font-bold flex items-center justify-center shrink-0"
          >
            {{ p.unreadCount }}
          </span>
        </div>
      </div>
    </div>

    <!-- ── RIGHT MAIN: CHAT ACTIVE CONVERSATION (8 cols) ─────────────── -->
    <div class="md:col-span-8 flex flex-col h-full bg-canvas-raised">
      <!-- Conversation Header -->
      <div class="p-4 border-b border-border flex items-center justify-between bg-canvas/30">
        <div class="flex items-center gap-3">
          <div class="relative">
            <img :src="activePatient.avatar" :alt="activePatient.name" class="w-10 h-10 rounded-full object-cover" />
            <span
              v-if="activePatient.online"
              class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-success rounded-full border-2 border-canvas"
            ></span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="font-display font-bold text-base text-ink">{{ activePatient.name }}</h3>
              <span class="px-2 py-0.5 text-[0.68rem] font-semibold rounded-full bg-success-soft text-success">
                {{ activePatient.online ? 'Online' : 'Offline' }}
              </span>
            </div>
            <p class="font-body text-xs text-ink-muted">Clinical Track: {{ activePatient.condition }}</p>
          </div>
        </div>

        <!-- Action Quick Tools -->
        <div class="flex items-center gap-2">
          <button
            @click="sendQuickPrescription"
            class="px-3 py-1.5 rounded-lg border border-primary/40 bg-primary-soft text-primary font-body text-xs font-semibold hover:bg-primary/20 transition-colors flex items-center gap-1.5"
            title="Push assigned meal protocol directly to patient chat"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            <span>Attach Plan</span>
          </button>
          <router-link
            to="/expert/patients"
            class="px-3 py-1.5 rounded-lg border border-border text-ink font-body text-xs font-semibold hover:bg-canvas transition-colors"
          >
            Patient Chart
          </router-link>
        </div>
      </div>

      <!-- Messages Stream -->
      <div ref="chatContainer" class="flex-1 p-5 overflow-y-auto space-y-4 bg-canvas/20">
        <div
          v-for="msg in currentMessages"
          :key="msg.id"
          class="flex flex-col"
          :class="msg.sender === 'expert' ? 'items-end' : 'items-start'"
        >
          <!-- Sender Label & Timestamp -->
          <div class="flex items-center gap-2 mb-1 px-1">
            <span class="text-[0.7rem] font-semibold text-ink-muted">
              {{ msg.sender === 'expert' ? 'You (Clinician)' : activePatient.name }}
            </span>
            <span class="text-[0.68rem] text-ink-muted font-data">{{ msg.time }}</span>
          </div>

          <!-- Message Bubble -->
          <div
            class="max-w-[78%] rounded-2xl px-4 py-2.5 text-sm font-body shadow-xs"
            :class="msg.sender === 'expert'
              ? 'bg-primary text-white rounded-tr-xs'
              : 'bg-canvas-raised border border-border text-ink rounded-tl-xs'"
          >
            <p class="leading-relaxed whitespace-pre-wrap">{{ msg.text }}</p>

            <!-- Attachment Card (Lab Report or Meal Plan) -->
            <div
              v-if="msg.attachment"
              class="mt-2.5 p-3 rounded-xl border text-xs"
              :class="msg.sender === 'expert'
                ? 'bg-white/10 border-white/20 text-white'
                : 'bg-canvas border-border text-ink'"
            >
              <div class="font-display font-bold text-[0.82rem] flex items-center gap-1.5 mb-0.5">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <span>{{ msg.attachment.title }}</span>
              </div>
              <div class="opacity-80 font-data text-[0.72rem]">{{ msg.attachment.meta }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Message Input Footer -->
      <div class="p-3.5 border-t border-border bg-canvas-raised">
        <form @submit.prevent="sendMessage" class="flex items-center gap-2">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Type clinical advice, dietary feedback, or follow-up note..."
            class="flex-1 px-4 py-2.5 rounded-xl bg-canvas border border-border text-ink text-sm outline-none focus:border-primary transition-colors placeholder:text-ink-muted"
          />
          <Button type="submit" :disabled="!inputMessage.trim() || isSending" size="md">
            {{ isSending ? 'Sending...' : 'Send' }}
          </Button>
        </form>
      </div>
    </div>
  </div>
</template>
