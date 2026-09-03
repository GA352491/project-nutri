<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Bar as BarChart } from 'vue-chartjs'
import {
 Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend
} from 'chart.js'
import apiClient from '../../api'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const isLoading = ref(true)
const costs = ref({
 stripe_fees: 0.0,
 jitsi_infra: 0.0,
 ollama_compute: 0.0,
 redis_broker: 0.0,
 temporal_server: 0.0
})

const revenue = ref({
 subscriptions: 0.0,
 marketplace_commissions: 0.0,
})

const kpis = ref({
  total_users: 0,
  total_recipes: 0,
  avg_platform_latency_ms: 0.0,
})

interface ServiceLatency {
  service: string
  status: string
  latency_ms: number
  p95_ms: number
  grade: string
  sla_target_ms: number
}

const serviceLatencies = ref<ServiceLatency[]>([])

async function fetchAnalytics() {
  isLoading.value = true
  try {
    const res = await apiClient.get('/admin/analytics')
    if (res.data?.revenue) {
      revenue.value.subscriptions = res.data.revenue.subscriptions_usd || 0
      revenue.value.marketplace_commissions = res.data.revenue.marketplace_commissions_usd || 0
    }
    if (res.data?.costs) {
      costs.value.stripe_fees = res.data.costs.stripe_fees_usd || 0
      costs.value.jitsi_infra = res.data.costs.jitsi_infra_usd || 0
      costs.value.ollama_compute = res.data.costs.ollama_compute_usd || 0
      costs.value.redis_broker = res.data.costs.redis_broker_usd || 0
      costs.value.temporal_server = res.data.costs.temporal_server_usd || 0
    }
    if (res.data?.kpis) {
      kpis.value.total_users = res.data.kpis.total_users || 0
      kpis.value.total_recipes = res.data.kpis.total_recipes || 0
      kpis.value.avg_platform_latency_ms = res.data.kpis.avg_platform_latency_ms || 0.0
    }
    if (res.data?.latencies) {
      serviceLatencies.value = res.data.latencies
    }
  } catch (err) {
    console.warn('Analytics API unavailable:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchAnalytics)

const totalRevenue = computed(() => revenue.value.subscriptions + revenue.value.marketplace_commissions)
const totalCosts = computed(() => costs.value.stripe_fees + costs.value.jitsi_infra)
const netProfit = computed(() => totalRevenue.value - totalCosts.value)

const chartData = computed(() => ({
 labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun (Live)'],
 datasets: [
  {
   label: 'Revenue (USD)',
   backgroundColor: '#10b981',
   data: [0, 0, 0, 0, 0, totalRevenue.value],
   borderRadius: 4
  },
  {
   label: 'Costs (USD)',
   backgroundColor: '#ef4444',
   data: [0, 0, 0, 0, 0, totalCosts.value],
   borderRadius: 4
  }
 ]
}))

const chartOptions = {
 responsive: true,
 maintainAspectRatio: false,
 plugins: { legend: { position: 'top' as const } },
 scales: {
  x: { grid: { display: false } },
  y: { grid: { color: 'rgba(0,0,0,0.05)' } }
 }
}
</script>

<template>
 <div class="space-y-8">

 <!-- Loading state -->
 <div v-if="isLoading" class="p-8 text-center text-ink-muted font-body text-sm">
  Loading analytics from live services...
 </div>

 <template v-else>

 <!-- KPI row from real data -->
 <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
  <div class="bg-primary/5 border border-primary/20 rounded-xl p-4">
  <div class="font-data text-[0.7rem] text-primary uppercase tracking-wider font-bold mb-1">Total Revenue</div>
  <div class="font-display font-bold text-[1.8rem] text-primary">${{ totalRevenue.toFixed(2) }}</div>
  </div>
  <div class="bg-danger/5 border border-danger/20 rounded-xl p-4">
  <div class="font-data text-[0.7rem] text-danger uppercase tracking-wider font-bold mb-1">Total Costs</div>
  <div class="font-display font-bold text-[1.8rem] text-danger">${{ totalCosts.toFixed(2) }}</div>
  </div>
  <div class="bg-success/5 border border-success/20 rounded-xl p-4">
  <div class="font-data text-[0.7rem] text-success uppercase tracking-wider font-bold mb-1">Total Users</div>
  <div class="font-display font-bold text-[1.8rem] text-success">{{ kpis.total_users }}</div>
  </div>
  <div class="bg-canvas-raised border border-border rounded-xl p-4">
  <div class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-bold mb-1">Recipes Curated</div>
  <div class="font-display font-bold text-[1.8rem] text-ink">{{ kpis.total_recipes }}</div>
  </div>
 </div>

 <!-- Profit Margin -->
 <div class="bg-primary/5 border border-primary/20 rounded-2xl p-6 text-center">
  <div class="font-data text-[0.8rem] text-primary uppercase tracking-wider font-bold mb-1">Net Profit (All-Time)</div>
  <div class="font-display font-bold text-[2.5rem]" :class="netProfit >= 0 ? 'text-primary' : 'text-danger'">
  {{ netProfit >= 0 ? '+' : '' }}${{ netProfit.toFixed(2) }}
  </div>
  <p v-if="totalRevenue === 0" class="font-body text-[0.9rem] text-primary/70 mt-2">
  No transactions yet — revenue will appear here once subscriptions or marketplace bookings are made.
  </p>
  <p v-else class="font-body text-[0.9rem] text-primary/70 mt-2 max-w-lg mx-auto">
  Running AI and Event Brokers locally (Ollama, Temporal, FastStream) saves on cloud compute costs.
  </p>
 </div>

 <!-- Chart -->
 <div class="bg-canvas-raised border border-border p-6 rounded-2xl shadow-card">
  <h2 class="font-display font-semibold text-[1.2rem] text-ink mb-4">Revenue vs Costs (Live Data)</h2>
  <div class="h-64">
  <BarChart :data="chartData" :options="chartOptions" />
  </div>
 </div>

 <!-- Cost Burn & Revenue -->
 <div class="grid md:grid-cols-2 gap-6">
 
 <!-- Revenue -->
 <div class="bg-canvas-raised border border-border p-6 rounded-2xl shadow-card">
  <h2 class="font-display font-semibold text-[1.2rem] text-ink mb-6">Revenue Breakdown</h2>
  <div class="space-y-4">
  <div class="flex justify-between items-center pb-4 border-b border-border">
  <span class="font-body text-[0.95rem] text-ink">Premium Subscriptions</span>
  <span class="font-data font-semibold text-[1.1rem] text-success">${{ revenue.subscriptions.toFixed(2) }}</span>
  </div>
  <div class="flex justify-between items-center pb-4 border-b border-border">
  <div>
  <span class="font-body text-[0.95rem] text-ink block">Marketplace Commissions</span>
  <span class="font-data text-[0.75rem] text-ink-muted">20% cut from appointments</span>
  </div>
  <span class="font-data font-semibold text-[1.1rem] text-success">${{ revenue.marketplace_commissions.toFixed(2) }}</span>
  </div>
  </div>
 </div>

 <!-- Cost Burn -->
 <div class="bg-canvas-raised border border-border p-6 rounded-2xl shadow-card">
  <h2 class="font-display font-semibold text-[1.2rem] text-ink mb-6">Cost Breakdown</h2>
  <div class="space-y-4">
  <div class="flex justify-between items-center pb-4 border-b border-border">
  <span class="font-body text-[0.95rem] text-ink">Stripe Fees (2.9% + 30¢)</span>
  <span class="font-data font-semibold text-[1.1rem] text-danger">-${{ costs.stripe_fees.toFixed(2) }}</span>
  </div>
  <div class="flex justify-between items-center pb-4 border-b border-border">
  <span class="font-body text-[0.95rem] text-ink">Jitsi Video Infra</span>
  <span class="font-data font-semibold text-[1.1rem]" :class="costs.jitsi_infra > 0 ? 'text-danger' : 'text-ink-muted'">
   {{ costs.jitsi_infra > 0 ? '-$' + costs.jitsi_infra.toFixed(2) : '$0.00 (Self-hosted)' }}
  </span>
  </div>
  <div class="flex justify-between items-center pb-4 border-b border-border">
  <span class="font-body text-[0.95rem] text-ink">LLM Compute (Ollama Local)</span>
  <span class="font-data font-semibold text-[1.1rem] text-ink-muted">$0.00 (Local)</span>
  </div>
  <div class="flex justify-between items-center pb-4 border-b border-border">
  <span class="font-body text-[0.95rem] text-ink">Redis Broker</span>
  <span class="font-data font-semibold text-[1.1rem] text-ink-muted">$0.00 (Local)</span>
  </div>
  <div class="flex justify-between items-center">
  <span class="font-body text-[0.95rem] text-ink">Temporal Server</span>
  <span class="font-data font-semibold text-[1.1rem] text-ink-muted">$0.00 (Local)</span>
  </div>
  </div>
 </div>

  <!-- Live Latency & API Performance Card -->
  <div class="bg-canvas-raised border border-border p-6 rounded-2xl shadow-card space-y-4">
   <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-4">
    <div>
     <h2 class="font-display font-semibold text-[1.2rem] text-ink">Live API Latency & Performance Leaderboard</h2>
     <p class="font-body text-xs text-ink-muted mt-0.5">Real-time response times (RTT), P95 estimates, and SLA health grades across all 21 microservices</p>
    </div>
    <div class="flex items-center gap-2 font-data text-xs">
     <span class="px-2.5 py-1 rounded-full bg-primary/10 text-primary font-bold">
      Avg Platform Latency: {{ kpis.avg_platform_latency_ms }} ms
     </span>
     <button @click="fetchAnalytics" class="px-3 py-1 bg-canvas border border-border hover:border-primary text-ink rounded-lg font-semibold transition-colors cursor-pointer">
      Refresh Latency
     </button>
    </div>
   </div>

   <div class="overflow-x-auto">
    <table class="w-full text-left text-xs">
     <thead>
      <tr class="bg-canvas/80 border-b border-border text-ink-muted uppercase font-data text-[0.68rem] tracking-wider">
       <th class="py-2.5 px-4 font-semibold">Rank & Service</th>
       <th class="py-2.5 px-3 font-semibold">Status</th>
       <th class="py-2.5 px-3 font-semibold text-right">Live Latency</th>
       <th class="py-2.5 px-3 font-semibold text-right">P95 (Est.)</th>
       <th class="py-2.5 px-3 font-semibold text-right">SLA Target</th>
       <th class="py-2.5 px-4 font-semibold text-center">SLA Grade</th>
      </tr>
     </thead>
     <tbody class="divide-y divide-border font-body">
      <tr v-for="(lat, idx) in serviceLatencies" :key="lat.service" class="hover:bg-canvas/50 transition-colors">
       <td class="py-3 px-4 font-semibold text-ink flex items-center gap-2">
        <span class="w-5 h-5 rounded-full bg-canvas border border-border flex items-center justify-center font-data text-[0.65rem] text-ink-muted">{{ idx + 1 }}</span>
        <span>{{ lat.service }}</span>
       </td>
       <td class="py-3 px-3">
        <span 
         class="px-2 py-0.5 rounded-full text-[0.68rem] font-bold capitalize border inline-flex items-center gap-1"
         :class="lat.status === 'healthy' ? 'bg-success-soft text-success border-success/30' : 'bg-danger-soft text-danger border-danger/30'"
        >
         <span class="w-1.5 h-1.5 rounded-full" :class="lat.status === 'healthy' ? 'bg-success' : 'bg-danger'"></span>
         {{ lat.status }}
        </span>
       </td>
       <td class="py-3 px-3 text-right font-data tabular-nums font-semibold" :class="lat.latency_ms < 20 ? 'text-emerald-600' : lat.latency_ms < 100 ? 'text-primary' : lat.latency_ms < 300 ? 'text-amber-600' : 'text-danger'">
        {{ lat.latency_ms }} ms
       </td>
       <td class="py-3 px-3 text-right font-data tabular-nums text-ink-muted">
        {{ lat.p95_ms }} ms
       </td>
       <td class="py-3 px-3 text-right font-data tabular-nums text-ink-muted">
        &lt; {{ lat.sla_target_ms }} ms
       </td>
       <td class="py-3 px-4 text-center">
        <span 
         class="px-2 py-0.5 rounded text-[0.7rem] font-bold font-data"
         :class="{
          'bg-emerald-500/15 text-emerald-700': lat.grade === 'A+' || lat.grade === 'A',
          'bg-primary/15 text-primary': lat.grade === 'B',
          'bg-amber-500/15 text-amber-700': lat.grade === 'C',
          'bg-danger/15 text-danger': lat.grade === 'D'
         }"
        >
         Grade {{ lat.grade }}
        </span>
       </td>
      </tr>
     </tbody>
    </table>
   </div>
  </div>

  </div>

  </template>
 </div>
</template>
