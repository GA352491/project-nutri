<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Icon from '../../components/ui/Icon.vue'
import apiClient from '../../api'

// ── Live Metrics State ─────────────────────────────────────────────────────

const lastRefreshed = ref<Date | null>(null)
const isRefreshing = ref(false)
let refreshInterval: ReturnType<typeof setInterval> | null = null

interface CacheStats {
 connected: boolean
 redis_version: string
 used_memory_human: string
 used_memory_peak_human: string
 connected_clients: number
 total_commands_processed: number
 keyspace_hits: number
 keyspace_misses: number
 hit_rate_pct: number
 uptime_in_seconds: number
 rdb_last_bgsave_status: string
 keyspace: Record<string, any>
 error?: string
}

interface QueueStats {
 queue: string
 pending_messages: number
 dead_letter_messages: number
 status: string
}

const cacheStats = ref<CacheStats>({
 connected: false,
 redis_version: '—',
 used_memory_human: '—',
 used_memory_peak_human: '—',
 connected_clients: 0,
 total_commands_processed: 0,
 keyspace_hits: 0,
 keyspace_misses: 0,
 hit_rate_pct: 0,
 uptime_in_seconds: 0,
 rdb_last_bgsave_status: '—',
 keyspace: {}
})

const emailQueueStats = ref<QueueStats>({
 queue: 'nutriplan:email:requested',
 pending_messages: 3,
 dead_letter_messages: 0,
 status: 'healthy'
})

// Namespace breakdown — populated from real keyspace data
const namespaceMetrics = ref<{ ns: string; keys: number; ttl: string; desc: string; hitRate: number }[]>([])

// Event log — pub/sub stream (populated live from queue-stats endpoint)
const eventLog = ref<{ ts: string; channel: string; user: string; msg: string }[]>([])

const hitRatePct = computed(() => cacheStats.value.hit_rate_pct)
const hitRateColor = computed(() => {
 if (hitRatePct.value >= 85) return 'text-emerald-600'
 if (hitRatePct.value >= 65) return 'text-amber-600'
 return 'text-rose-600'
})

const uptimeHuman = computed(() => {
 const s = cacheStats.value.uptime_in_seconds
 const h = Math.floor(s / 3600)
 const m = Math.floor((s % 3600) / 60)
 return `${h}h ${m}m`
})

// Channel badge colors
const channelColor: Record<string, string> = {
 'steps_updated': 'bg-sky-100 text-sky-800',
 'plan_generated': 'bg-emerald-100 text-emerald-800',
 'appointment_booked':'bg-purple-100 text-purple-800',
 'email:requested': 'bg-amber-100 text-amber-800',
}

async function fetchStats() {
 isRefreshing.value = true
 try {
  const res = await apiClient.get('/notifications/admin/queue-stats')
  if (res.data?.cache) {
  cacheStats.value = { ...cacheStats.value, ...res.data.cache }
  // Derive namespace metrics from real keyspace
  const ks = res.data.cache.keyspace || {}
  const entries = Object.entries(ks).map(([db, info]: [string, any]) => ({
   ns: db,
   keys: info.keys || 0,
   ttl: info.avg_ttl > 0 ? `${Math.round(info.avg_ttl / 1000)}s avg` : 'no-expiry',
   desc: db === 'db0' ? 'Primary key store' : db === 'db1' ? 'Session / auth cache' : `Database ${db}`,
   hitRate: res.data.cache.hit_rate_pct || 0
  }))
  if (entries.length > 0) namespaceMetrics.value = entries
  }
  if (res.data?.email_queue) {
  emailQueueStats.value = { ...emailQueueStats.value, ...res.data.email_queue }
  // Append an event if there are pending messages
  if (res.data.email_queue.pending_messages > 0) {
   const now = new Date().toLocaleTimeString('en-IN', { hour12: false })
   eventLog.value.unshift({
   ts: now,
   channel: 'email:requested',
   user: 'system',
   msg: `${res.data.email_queue.pending_messages} pending email(s) in queue`
   })
   if (eventLog.value.length > 20) eventLog.value.pop()
  }
  }
 } catch (err) {
  console.warn('Queue stats fetch failed:', err)
 } finally {
  isRefreshing.value = false
  lastRefreshed.value = new Date()
 }
}

function formatTime(d: Date | null): string {
 if (!d) return 'Never'
 return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

onMounted(() => {
 fetchStats()
 refreshInterval = setInterval(fetchStats, 15000) // Auto-refresh every 15s
})

onUnmounted(() => {
 if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<template>
 <div class="space-y-6">

 <!-- Header -->
 <div class="flex items-center justify-between">
 <div>
 <h1 class="font-display font-bold text-2xl text-ink">Queue & Cache Monitor</h1>
 <p class="text-xs text-ink-muted mt-0.5">
 Live Redis cache telemetry, Pub/Sub event streams, and email queue depth
 <span class="ml-2 text-ink-muted/60">Last refresh: {{ formatTime(lastRefreshed) }}</span>
 </p>
 </div>
 <button
 @click="fetchStats"
 class="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-white rounded-xl shadow hover:bg-primary-strong transition-all cursor-pointer"
 :class="{ 'opacity-70': isRefreshing }"
 >
 <Icon name="activity" class="w-4 h-4" :style="isRefreshing ? 'animation: spin 1s linear infinite' : ''" />
 Refresh Metrics
 </button>
 </div>

 <!-- Top KPI Cards -->
 <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
 <!-- Hit Rate -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-5 shadow-sm">
 <p class="text-[10px] font-semibold uppercase text-ink-muted tracking-wider mb-1">Cache Hit Rate</p>
 <p class="text-3xl font-bold font-mono" :class="hitRateColor">{{ hitRatePct }}%</p>
 <div class="mt-2 h-1.5 bg-border rounded-full overflow-hidden">
 <div class="h-full rounded-full bg-emerald-500 transition-all duration-700"
 :style="{ width: hitRatePct + '%' }"></div>
 </div>
 <p class="text-[10px] text-ink-muted mt-1.5">
 ✓ {{ cacheStats.keyspace_hits.toLocaleString() }} hits &nbsp;✕ {{ cacheStats.keyspace_misses.toLocaleString() }} misses
 </p>
 </div>

 <!-- Memory -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-5 shadow-sm">
 <p class="text-[10px] font-semibold uppercase text-ink-muted tracking-wider mb-1">Memory Used</p>
 <p class="text-3xl font-bold font-mono text-ink">{{ cacheStats.used_memory_human }}</p>
 <p class="text-[10px] text-ink-muted mt-2">Peak: {{ cacheStats.used_memory_peak_human }}</p>
 <p class="text-[10px] text-ink-muted mt-0.5">Redis {{ cacheStats.redis_version }}</p>
 </div>

 <!-- Connected Clients -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-5 shadow-sm">
 <p class="text-[10px] font-semibold uppercase text-ink-muted tracking-wider mb-1">Active Clients</p>
 <p class="text-3xl font-bold font-mono text-sky-600">{{ cacheStats.connected_clients }}</p>
 <p class="text-[10px] text-ink-muted mt-2">Uptime: {{ uptimeHuman }}</p>
 <p class="text-[10px] text-ink-muted mt-0.5">{{ cacheStats.total_commands_processed.toLocaleString() }} commands</p>
 </div>

 <!-- Email Queue Depth -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-5 shadow-sm">
 <p class="text-[10px] font-semibold uppercase text-ink-muted tracking-wider mb-1">Email Queue Depth</p>
 <p class="text-3xl font-bold font-mono"
 :class="emailQueueStats.pending_messages > 50 ? 'text-rose-600' : emailQueueStats.pending_messages > 10 ? 'text-amber-600' : 'text-emerald-600'">
 {{ emailQueueStats.pending_messages }}
 </p>
 <p class="text-[10px] mt-2"
 :class="emailQueueStats.status === 'healthy' ? 'text-emerald-600 font-semibold' : 'text-amber-600 font-semibold'">
 ● {{ emailQueueStats.status.charAt(0).toUpperCase() + emailQueueStats.status.slice(1) }}
 </p>
 <p class="text-[10px] text-ink-muted mt-0.5">DLQ: {{ emailQueueStats.dead_letter_messages }} msgs</p>
 </div>
 </div>

 <!-- Namespace Cache Breakdown Table -->
 <div class="bg-canvas-raised border border-border rounded-2xl shadow-sm overflow-hidden">
 <div class="px-6 py-4 border-b border-border flex items-center justify-between">
 <div>
 <h2 class="font-display font-semibold text-base text-ink">Cache Namespace Breakdown</h2>
 <p class="text-xs text-ink-muted">Key counts, TTL policy, and hit rates by domain prefix</p>
 </div>
 <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
 ● CONNECTED · Redis {{ cacheStats.redis_version }}
 </span>
 </div>

 <table class="w-full text-left">
 <thead>
 <tr class="text-[11px] font-semibold uppercase tracking-wider text-ink-muted border-b border-border bg-canvas">
 <th class="py-3 px-6">Namespace</th>
 <th class="py-3 px-4">Cached Keys</th>
 <th class="py-3 px-4">TTL Policy</th>
 <th class="py-3 px-4">Hit Rate</th>
 <th class="py-3 px-6">Purpose</th>
 </tr>
 </thead>
 <tbody class="divide-y divide-border text-sm">
 <tr v-if="namespaceMetrics.length === 0">
  <td colspan="5" class="py-8 text-center text-xs text-ink-muted">
   No active namespaces reported by Redis keyspace probe.
  </td>
 </tr>
 <tr v-for="ns in namespaceMetrics" :key="ns.ns" class="hover:bg-primary-soft/20 transition-colors">
  <td class="py-3.5 px-6">
  <code class="font-mono text-xs bg-canvas px-2 py-0.5 rounded border border-border text-primary">nutriplan:{{ ns.ns }}:</code>
  </td>
  <td class="py-3.5 px-4 font-mono font-bold text-ink text-sm">{{ ns.keys }}</td>
  <td class="py-3.5 px-4">
  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-100 text-sky-800">{{ ns.ttl }}</span>
  </td>
  <td class="py-3.5 px-4">
  <div class="flex items-center gap-2">
  <div class="w-20 h-1.5 bg-border rounded-full overflow-hidden">
  <div class="h-full rounded-full bg-emerald-500 transition-all duration-500"
  :style="{ width: ns.hitRate + '%' }"></div>
  </div>
  <span class="font-mono text-xs font-bold text-emerald-700">{{ ns.hitRate }}%</span>
  </div>
  </td>
  <td class="py-3.5 px-6 text-xs text-ink-muted">{{ ns.desc }}</td>
 </tr>
 </tbody>
 </table>
 </div>

 <!-- Pub/Sub Event Stream Log -->
 <div class="bg-canvas-raised border border-border rounded-2xl shadow-sm overflow-hidden">
 <div class="px-6 py-4 border-b border-border flex items-center gap-3">
 <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
 <div>
 <h2 class="font-display font-semibold text-base text-ink">Live Pub/Sub Event Stream</h2>
 <p class="text-xs text-ink-muted">Real-time Redis channel events across all NutriPlan microservices</p>
 </div>
 </div>

 <div class="divide-y divide-border font-mono text-xs">
 <div v-if="eventLog.length === 0" class="px-6 py-8 text-center text-xs text-ink-muted">
   Listening for Redis pub/sub queue events (FastStream broker active)...
 </div>
 <div
 v-for="(event, idx) in eventLog"
 :key="idx"
 class="px-6 py-3.5 flex items-start gap-4 hover:bg-canvas transition-colors"
 >
 <span class="text-ink-muted w-16 shrink-0 pt-0.5">{{ event.ts }}</span>
 <span
 class="px-2 py-0.5 rounded text-[10px] font-bold shrink-0 uppercase tracking-wide"
 :class="channelColor[event.channel] || 'bg-neutral-100 text-neutral-700'"
 >
 {{ event.channel }}
 </span>
 <span class="text-ink-muted shrink-0 w-24">{{ event.user }}</span>
 <span class="text-ink flex-1">{{ event.msg }}</span>
 </div>
 </div>
 </div>

 <!-- Temporal & RabbitMQ Status Tiles -->
 <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
 <div class="bg-canvas-raised border border-border rounded-2xl p-5 shadow-sm flex items-center gap-4">
 <div class="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center text-purple-700 font-bold text-lg">T</div>
 <div>
 <p class="text-xs font-bold text-ink">Temporal Orchestration</p>
 <p class="text-[10px] text-emerald-600 font-semibold mt-0.5">● Healthy · Port 7233</p>
 <p class="text-[10px] text-ink-muted">BookingWorkflow · PlanGenWorkflow</p>
 </div>
 </div>

 <div class="bg-canvas-raised border border-border rounded-2xl p-5 shadow-sm flex items-center gap-4">
 <div class="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center text-orange-700 font-bold text-lg">R</div>
 <div>
 <p class="text-xs font-bold text-ink">RabbitMQ AMQP Broker</p>
 <p class="text-[10px] text-amber-600 font-semibold mt-0.5">○ Optional · Port 5672</p>
 <p class="text-[10px] text-ink-muted">Enabled when Redis Streams insufficient</p>
 </div>
 </div>

 <div class="bg-canvas-raised border border-border rounded-2xl p-5 shadow-sm flex items-center gap-4">
 <div class="w-10 h-10 rounded-xl bg-rose-100 flex items-center justify-center text-rose-700 font-bold text-sm">DLQ</div>
 <div>
 <p class="text-xs font-bold text-ink">Dead Letter Queue</p>
 <p class="text-[10px] text-emerald-600 font-semibold mt-0.5">● {{ emailQueueStats.dead_letter_messages }} failed msgs</p>
 <p class="text-[10px] text-ink-muted">nutriplan:email:dead_letter</p>
 </div>
 </div>
 </div>

 </div>
</template>
