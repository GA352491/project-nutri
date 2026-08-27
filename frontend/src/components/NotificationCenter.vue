<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '../api'

const router = useRouter()
const showDropdown = ref(false)
const isLoading = ref(false)

interface AppNotification {
 id: string
 title: string
 body: string
 type: string
 is_read: boolean
 created_at: string
 action_url?: string
}

const notifications = ref<AppNotification[]>([])
const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

async function fetchNotifications() {
 isLoading.value = true
 try {
 const res = await apiClient.get('/notifications/')
 if (Array.isArray(res.data)) {
 notifications.value = res.data
 } else if (res.data && Array.isArray(res.data.items)) {
 notifications.value = res.data.items
 }
 } catch (err) {
 // Graceful fallback for local dev
 if (notifications.value.length === 0) {
 notifications.value = [
 {
 id: 'notif_1',
 title: 'Welcome to NutriPlan!',
 body: 'Your personalized ICMR-NIN nutrition plan is ready for review.',
 type: 'system',
 is_read: false,
 created_at: new Date().toISOString(),
 action_url: '/plan'
 },
 {
 id: 'notif_2',
 title: 'Wearable Synced',
 body: '8,420 steps recorded today. Great job hitting your active goal!',
 type: 'wearable',
 is_read: false,
 created_at: new Date().toISOString(),
 action_url: '/wearables'
 }
 ]
 }
 } finally {
 isLoading.value = false
 }
}

onMounted(() => {
 fetchNotifications()
 // Optional: Poll every 30s
 setInterval(fetchNotifications, 30000)
})

function toggleDropdown() {
 showDropdown.value = !showDropdown.value
}

async function markAllAsRead() {
 try {
 await apiClient.post('/notifications/read-all')
 notifications.value.forEach(n => n.is_read = true)
 } catch (err) {
 console.error('Failed to mark all as read', err)
 }
}

async function handleNotifClick(notif: AppNotification) {
 if (!notif.is_read) {
 try {
 await apiClient.patch(`/notifications/${notif.id}/read`)
 notif.is_read = true
 } catch (err) {
 console.error('Failed to mark notification as read', err)
 }
 }
 showDropdown.value = false
 if (notif.action_url) {
 router.push(notif.action_url)
 }
}
</script>

<template>
 <div class="relative">
 <button 
 class="relative p-2 rounded-full hover:bg-canvas-raised transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20"
 @click="toggleDropdown"
 aria-label="Notifications"
 >
 <svg class="w-6 h-6 text-ink" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
 <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
 </svg>
 <span 
 v-if="unreadCount > 0" 
 class="absolute top-1.5 right-1.5 w-2 h-2 bg-danger rounded-full border border-canvas"
 />
 </button>

 <!-- Dropdown -->
 <Transition name="fade-scale">
 <div 
 v-if="showDropdown" 
 class="absolute right-0 mt-2 w-80 bg-canvas-raised border border-border rounded-xl shadow-[0_8px_30px_rgba(28,38,32,0.12)] z-50 overflow-hidden origin-top-right"
 >
 <div class="flex items-center justify-between p-4 border-b border-border bg-canvas">
 <h3 class="font-display font-semibold text-[1rem] text-ink">Notifications</h3>
 <button 
 v-if="unreadCount > 0"
 class="text-[0.75rem] font-semibold text-primary hover:underline"
 @click="markAllAsRead"
 >
 Mark all read
 </button>
 </div>
 
 <div class="max-h-96 overflow-y-auto">
 <div v-if="notifications.length === 0" class="p-6 text-center text-ink-muted text-[0.85rem]">
 No notifications right now.
 </div>
 
 <div 
 v-for="notif in notifications" 
 :key="notif.id"
 class="flex items-start gap-3 p-4 border-b border-border/50 hover:bg-canvas transition-colors cursor-pointer"
 :class="!notif.is_read ? 'bg-primary-soft/10' : ''"
 @click="handleNotifClick(notif)"
 >
 <div 
 class="w-2 h-2 mt-1.5 rounded-full shrink-0" 
 :class="!notif.is_read ? 'bg-primary' : 'bg-transparent'" 
 />
 <div class="flex-1 min-w-0">
 <h4 class="font-body font-semibold text-[0.85rem] text-ink truncate">{{ notif.title }}</h4>
 <p class="font-body text-[0.8rem] text-ink-muted mt-0.5 line-clamp-2">{{ notif.body }}</p>
 <span class="font-data text-[0.65rem] text-ink-muted uppercase tracking-wider block mt-2">
 {{ new Date(notif.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}
 </span>
 </div>
 </div>
 </div>
 </div>
 </Transition>
 </div>
</template>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
 transition: opacity 150ms ease, transform 150ms ease;
}
.fade-scale-enter-from,
.fade-scale-leave-to {
 opacity: 0;
 transform: scale(0.95);
}
</style>
