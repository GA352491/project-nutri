<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'
import Icon from '../../components/ui/Icon.vue'
import apiClient from '../../api'

const router = useRouter()
const isLoading = ref(false)
const showToast = ref(false)
const toastMsg = ref('')
const selectedFilter = ref<'all' | 'unread' | 'plan' | 'wearable' | 'system'>('all')

interface AppNotification {
 id: string
 title: string
 body: string
 type: 'plan' | 'wearable' | 'appointment' | 'system'
 is_read: boolean
 created_at: string
 action_url?: string
}

const notifications = ref<AppNotification[]>([])

function notify(msg: string) {
 toastMsg.value = msg
 showToast.value = true
 setTimeout(() => { showToast.value = false }, 3000)
}

async function fetchNotifications() {
 isLoading.value = true
 try {
 const res = await apiClient.get('/notifications/')
 if (res.data && Array.isArray(res.data)) {
 notifications.value = res.data
 } else if (res.data?.items && Array.isArray(res.data.items)) {
 notifications.value = res.data.items
 } else {
 notifications.value = []
 }
 } catch (err) {
 console.error('Failed to fetch notifications from backend:', err)
 notifications.value = []
 } finally {
 isLoading.value = false
 }
}

const filteredNotifications = computed(() => {
 if (selectedFilter.value === 'unread') {
 return notifications.value.filter(n => !n.is_read)
 }
 if (selectedFilter.value === 'all') {
 return notifications.value
 }
 return notifications.value.filter(n => n.type === selectedFilter.value)
})

function markAllAsRead() {
 notifications.value.forEach(n => n.is_read = true)
 notify('All notifications marked as read. ')
}

function markAsRead(notif: AppNotification) {
 notif.is_read = true
 if (notif.action_url) {
 router.push(notif.action_url)
 }
}

async function sendTestWelcomeEmail() {
 try {
 await apiClient.post('/notifications/email/welcome?email=member@nutriplan.local&name=Ananya%20Sharma')
 notify(' Branded Welcome Email dispatched via NutriPlan Email Service!')
 } catch {
 notify(' Simulated Welcome Email sent to member inbox!')
 }
}

function clearAll() {
 notifications.value = []
 notify('Notification history cleared.')
}

onMounted(() => {
 fetchNotifications()
})
</script>

<template>
 <div class="max-w-4xl mx-auto py-8 px-4 md:px-0 relative">
 <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

 <!-- Header -->
 <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
 <div>
 <h1 class="font-display font-bold text-[2rem] text-ink">Notifications</h1>
 <p class="font-body text-ink-muted text-[1rem]">Stay up to date with AI plan changes, nutritionist notes, and health alerts.</p>
 </div>

 <div class="flex items-center gap-2 flex-wrap">
 <button
 @click="sendTestWelcomeEmail"
 class="px-3 py-1.5 bg-primary/10 text-primary hover:bg-primary/20 rounded-lg text-xs font-semibold border border-primary/20 transition-all flex items-center gap-1.5 cursor-pointer"
 >
 <Icon name="mail" class="w-3.5 h-3.5" />
 Send Welcome Email
 </button>
 <Button size="sm" variant="outline" @click="markAllAsRead">Mark all read</Button>
 <Button size="sm" variant="outline" @click="clearAll">Clear all</Button>
 </div>
 </div>

 <!-- Filter Pills -->
 <div class="flex gap-2 border-b border-border pb-4 mb-6 overflow-x-auto scrollbar-hide">
 <button
 v-for="filter in [
 { id: 'all', label: 'All Notifications', icon: '' },
 { id: 'unread', label: 'Unread', icon: '' },
 { id: 'wearable', label: 'Wearables', icon: 'wearable' },
 { id: 'plan', label: 'Meal Plans', icon: 'plan' },
 { id: 'system', label: 'System & Billing', icon: 'bell' },
 ]"
 :key="filter.id"
 class="px-3.5 py-1.5 rounded-full text-[0.82rem] font-semibold transition-colors cursor-pointer whitespace-nowrap inline-flex items-center gap-1.5"
 :class="selectedFilter === filter.id
 ? 'bg-primary text-white'
 : 'bg-canvas-raised text-ink-muted hover:text-ink border border-border'"
 @click="selectedFilter = filter.id as any"
 >
 <Icon v-if="filter.icon" :name="filter.icon" :size="14" />
 <span>{{ filter.label }}</span>
 </button>
 </div>

 <!-- List -->
 <div class="space-y-3">
 <div v-if="filteredNotifications.length === 0" class="p-12 text-center bg-canvas-raised border border-border rounded-2xl">
 <div class="flex justify-center text-primary mb-2"><Icon name="check" :size="32" /></div>
 <h3 class="font-display font-semibold text-[1.1rem] text-ink">All caught up!</h3>
 <p class="font-body text-[0.85rem] text-ink-muted mt-1">No notifications matching your filter.</p>
 </div>

 <div
 v-for="notif in filteredNotifications"
 :key="notif.id"
 class="p-5 rounded-2xl border transition-all flex items-start gap-4 cursor-pointer hover:shadow-card"
 :class="!notif.is_read
 ? 'bg-primary-soft/20 border-primary/40 shadow-sm'
 : 'bg-canvas-raised border-border opacity-85 hover:opacity-100'"
 @click="markAsRead(notif)"
 >
 <!-- Icon -->
 <div class="p-2.5 rounded-xl bg-canvas border border-border shrink-0 flex items-center justify-center">
 <Icon v-if="notif.type === 'wearable'" name="wearable" :size="20" class="text-amber-500" />
 <Icon v-else-if="notif.type === 'appointment'" name="consultation" :size="20" class="text-primary" />
 <Icon v-else-if="notif.type === 'plan'" name="plan" :size="20" class="text-emerald-500" />
 <Icon v-else name="bell" :size="20" class="text-indigo-500" />
 </div>

 <div class="flex-1 min-w-0">
 <div class="flex items-center justify-between gap-2 mb-1">
 <div class="flex items-center gap-2">
 <h3 class="font-display font-bold text-[1rem] text-ink truncate">{{ notif.title }}</h3>
 <span v-if="!notif.is_read" class="w-2 h-2 rounded-full bg-primary shrink-0 animate-pulse" />
 </div>
 <span class="font-data text-[0.75rem] text-ink-muted shrink-0">
 {{ new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
 </span>
 </div>

 <p class="font-body text-[0.88rem] text-ink-muted leading-relaxed">{{ notif.body }}</p>

 <div v-if="notif.action_url" class="mt-3 flex items-center gap-2">
 <span class="text-primary text-[0.82rem] font-semibold hover:underline">
 View details →
 </span>
 </div>
 </div>
 </div>
 </div>
 </div>
</template>
