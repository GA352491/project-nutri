<script setup lang="ts">
import { ref } from 'vue'
import apiClient from '../../api'
import Icon from '../../components/ui/Icon.vue'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'

const showToast = ref(false)
const toastMsg = ref('')
const isSending = ref(false)

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3500)
}

const form = ref({
  title: '',
  message: '',
  audience: 'all', // all, patients, nutritionists, premium
  channel: 'all', // in_app, email, all
  severity: 'info', // info, warning, success, urgent
  action_url: '/notifications'
})

const recentBroadcasts = ref([
  {
    id: 'bc_init_01',
    title: 'Monsoon Immunity & Dietary Guide Available',
    audience: 'all',
    channel: 'in_app',
    severity: 'info',
    timestamp: 'Aug 26, 2026 18:30',
    delivered: 14,
    status: 'COMPLETED'
  },
  {
    id: 'bc_init_02',
    title: 'Updated IDA Telemedicine Prescribing Protocol',
    audience: 'nutritionists',
    channel: 'all',
    severity: 'urgent',
    timestamp: 'Aug 25, 2026 11:15',
    delivered: 3,
    status: 'COMPLETED'
  }
])

async function sendBroadcast() {
  if (!form.value.title.trim() || !form.value.message.trim()) {
    notify('Please provide both title and message for the announcement.')
    return
  }

  isSending.value = true
  try {
    const res = await apiClient.post('/admin/broadcast', form.value)
    if (res.data) {
      recentBroadcasts.value.unshift({
        id: res.data.broadcast_id,
        title: form.value.title,
        audience: form.value.audience,
        channel: form.value.channel,
        severity: form.value.severity,
        timestamp: res.data.timestamp,
        delivered: res.data.target_count,
        status: res.data.status
      })
      notify(res.data.summary || 'Broadcast dispatched successfully! 🚀')
      // Reset form
      form.value.title = ''
      form.value.message = ''
    }
  } catch (err) {
    console.error('Failed to dispatch broadcast:', err)
    notify('Failed to dispatch broadcast. Check backend logs.')
  } finally {
    isSending.value = false
  }
}
</script>

<template>
  <div class="space-y-8">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- Header Controls -->
    <div>
      <h2 class="font-display font-semibold text-[1.4rem] text-ink">Global Notification Broadcast Manager</h2>
      <p class="font-body text-[0.92rem] text-ink-muted">
        Compose high-priority announcements, emergency maintenance alerts, and seasonal dietary campaigns across In-App & Email channels.
      </p>
    </div>

    <!-- Main Grid: Composer & History -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- Composer Form (7 cols) -->
      <div class="lg:col-span-7 bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-5">
        <h3 class="font-display font-semibold text-base text-ink flex items-center gap-2">
          <Icon name="chat" :size="18" class="text-primary" />
          Compose Global Broadcast
        </h3>

        <form @submit.prevent="sendBroadcast" class="space-y-4">
          <!-- Title -->
          <div>
            <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Broadcast Title *</label>
            <input 
              v-model="form.title"
              type="text"
              required
              placeholder="e.g. Scheduled Maintenance: Aug 28 at 02:00 IST"
              class="w-full font-body text-[0.9rem] bg-canvas border border-border rounded-lg px-3.5 py-2.5 text-ink outline-none focus:border-primary"
            />
          </div>

          <!-- Message Body -->
          <div>
            <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Message Content (Markdown supported) *</label>
            <textarea 
              v-model="form.message"
              required
              rows="4"
              placeholder="Provide clear details, actionable advice, or direct links for users..."
              class="w-full font-body text-[0.9rem] bg-canvas border border-border rounded-lg px-3.5 py-2.5 text-ink outline-none focus:border-primary"
            ></textarea>
          </div>

          <!-- Audience & Channel Pickers -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Target Audience</label>
              <select 
                v-model="form.audience"
                class="w-full font-body text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
              >
                <option value="all">All Users (14)</option>
                <option value="patients">Patients Only (11)</option>
                <option value="nutritionists">Verified Nutritionists (3)</option>
                <option value="premium">Premium Subscribers (5)</option>
              </select>
            </div>

            <div>
              <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Delivery Channel</label>
              <select 
                v-model="form.channel"
                class="w-full font-body text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
              >
                <option value="all">In-App + Email Queue</option>
                <option value="in_app">In-App Banner Only</option>
                <option value="email">Email Broadcast Only</option>
              </select>
            </div>

            <div>
              <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Alert Severity</label>
              <select 
                v-model="form.severity"
                class="w-full font-body text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
              >
                <option value="info">Info (Standard)</option>
                <option value="success">Success (Product Launch)</option>
                <option value="warning">Warning (Maintenance)</option>
                <option value="urgent">Urgent / Emergency</option>
              </select>
            </div>
          </div>

          <!-- Action URL -->
          <div>
            <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Optional Action URL (Deep Link)</label>
            <input 
              v-model="form.action_url"
              type="text"
              placeholder="/notifications, /clinical, or /subscribe"
              class="w-full font-mono text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
            />
          </div>

          <div class="flex justify-end pt-2">
            <Button 
              type="submit" 
              variant="primary" 
              size="md" 
              :disabled="isSending"
            >
              {{ isSending ? 'Queuing Broadcast...' : '🚀 Dispatch Broadcast' }}
            </Button>
          </div>
        </form>
      </div>

      <!-- Recent Broadcasts Feed (5 cols) -->
      <div class="lg:col-span-5 bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-4">
        <h3 class="font-display font-semibold text-base text-ink">Broadcast History</h3>
        
        <div class="divide-y divide-border space-y-3">
          <div 
            v-for="bc in recentBroadcasts" 
            :key="bc.id"
            class="pt-3 first:pt-0 space-y-1.5"
          >
            <div class="flex items-start justify-between gap-2">
              <span class="font-semibold text-xs text-ink line-clamp-1">{{ bc.title }}</span>
              <span 
                class="px-2 py-0.5 rounded text-[9px] font-bold uppercase font-data whitespace-nowrap"
                :class="{
                  'bg-sky-100 text-sky-800': bc.severity === 'info',
                  'bg-amber-100 text-amber-800': bc.severity === 'warning',
                  'bg-rose-100 text-rose-800': bc.severity === 'urgent',
                  'bg-emerald-100 text-emerald-800': bc.severity === 'success',
                }"
              >
                {{ bc.severity }}
              </span>
            </div>

            <div class="flex items-center justify-between text-[11px] font-data text-ink-muted">
              <span>Audience: <strong class="text-ink">{{ bc.audience }}</strong></span>
              <span>Delivered: <strong class="text-emerald-600">{{ bc.delivered }}</strong></span>
            </div>

            <div class="text-[10px] text-ink-muted font-mono">
              {{ bc.timestamp }} · Channel: {{ bc.channel }}
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>
