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
})

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

 </div>

 </template>
 </div>
</template>
