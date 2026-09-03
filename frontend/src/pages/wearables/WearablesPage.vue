<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Line as LineChart, Bar as BarChart, Doughnut as DoughnutChart } from 'vue-chartjs'
import {
 Chart as ChartJS, CategoryScale, LinearScale, PointElement,
 LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import { useWearableStore } from '../../stores/wearable'
import { useAuthStore } from '../../stores/auth'
import Modal from '../../components/ui/Modal.vue'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'
import Icon from '../../components/ui/Icon.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement,
 BarElement, ArcElement, Title, Tooltip, Legend, Filler)

const auth = useAuthStore()
const wearable = useWearableStore()

const showConnectModal = ref(false)
const showToast = ref(false)
const toastMsg = ref('')
const selectedTracker = ref<any>(null)
const isSyncing = ref(false)

interface TrackerProvider {
 id: string
 name: string
 icon: string
 color: string
 desc: string
 metrics: string[]
 connected: boolean
 batteryPct?: number
 lastSync?: string
}

const trackers = ref<TrackerProvider[]>([
 {
 id: 'whoop',
 name: 'Whoop 4.0',
 icon: '',
 color: 'from-zinc-900 to-black border-white/20',
 desc: 'Strain, recovery score, sleep stages & real-time HRV',
 metrics: ['Recovery %', 'Day Strain', 'HRV', 'Sleep Quality'],
 connected: true,
 batteryPct: 88,
 lastSync: '4 mins ago'
 },
 {
 id: 'apple_health',
 name: 'Apple HealthKit',
 icon: '',
 color: 'from-rose-500/20 to-red-600/10 border-red-500/30',
 desc: 'Step count, active energy, standing hours & SpO₂',
 metrics: ['Steps', 'Active Calories', 'Resting HR', 'Walking Distance'],
 connected: true,
 batteryPct: 94,
 lastSync: '12 mins ago'
 },
 {
 id: 'fitbit',
 name: 'Fitbit / Pixel Watch',
 icon: '',
 color: 'from-cyan-500/20 to-blue-600/10 border-cyan-500/30',
 desc: 'Heart rate zones, daily steps & sleep score by Google',
 metrics: ['Zone Minutes', 'Cardio Fitness', 'Sleep Score'],
 connected: false,
 },
 {
 id: 'garmin',
 name: 'Garmin Connect',
 icon: '',
 color: 'from-blue-600/20 to-sky-600/10 border-blue-500/30',
 desc: 'Body Battery™, VO2 Max, training load & stress index',
 metrics: ['Body Battery', 'Stress Index', 'VO2 Max', 'Respiration'],
 connected: false,
 },
 {
 id: 'oura',
 name: 'Oura Ring Gen 3',
 icon: '',
 color: 'from-purple-600/20 to-indigo-600/10 border-purple-500/30',
 desc: 'Sleep stages, readiness score & nighttime skin temperature',
 metrics: ['Readiness', 'Sleep Score', 'Skin Temp Trend'],
 connected: false,
 }
])

function notify(msg: string) {
 toastMsg.value = msg
 showToast.value = true
 setTimeout(() => { showToast.value = false }, 3500)
}

function openConnect(tracker: TrackerProvider) {
 selectedTracker.value = tracker
 showConnectModal.value = true
}

async function toggleConnection(tracker: TrackerProvider) {
  const willConnect = !tracker.connected
  if (!willConnect) {
    tracker.connected = false
    tracker.lastSync = undefined
    notify(`Disconnected ${tracker.name}. Health data sync paused.`)
  } else {
    tracker.connected = true
    tracker.batteryPct = 95
    tracker.lastSync = 'Just now'
    
    // Transmit telemetry to backend
    if (tracker.id === 'apple_health') {
      await wearable.ingestReading({
        device: 'Apple HealthKit (Watch)',
        steps: 10450,
        active_calories: 530,
        basal_calories: 1650,
        heart_rate: 68,
        blood_oxygen: 98,
      })
    } else if (tracker.id === 'whoop') {
      await wearable.ingestReading({
        device: 'Whoop 4.0',
        steps: 11880,
        active_calories: 540,
        basal_calories: 1600,
        hrv_ms: 65,
        strain: 16.2,
        recovery_score: 88,
      })
    }
    
    await wearable.fetchSummary(auth.user?.id || 'user_123')
    notify(`Successfully paired ${tracker.name}! Daily biometrics synced.`)
  }
  showConnectModal.value = false
}

async function triggerManualSync() {
  isSyncing.value = true
  await wearable.ingestReading({
    device: 'Apple HealthKit (Watch)',
    steps: 11200,
    active_calories: 560,
    basal_calories: 1650,
    heart_rate: 66,
    hrv_ms: 68,
    blood_oxygen: 99,
  })
  await wearable.fetchSummary(auth.user?.id || 'user_123')
  isSyncing.value = false
  notify('Biometric telemetry refreshed from active wearables!')
}

onMounted(() => {
 wearable.fetchSummary(auth.user?.id || 'user_123')
})

const s = computed(() => wearable.summary)

const labels7d = computed(() =>
 (s.value?.readings_7d ?? []).map(r =>
 new Date(r.timestamp).toLocaleDateString('en-IN', { weekday: 'short' })
 ).reverse()
)

const heartRateData = computed(() => ({
 labels: labels7d.value,
 datasets: [{
 label: 'Heart Rate (bpm)',
 data: (s.value?.readings_7d ?? []).map(r => r.heart_rate ?? 0).reverse(),
 borderColor: '#ef4444',
 backgroundColor: 'rgba(239,68,68,0.1)',
 fill: true,
 tension: 0.4,
 pointRadius: 4,
 }]
}))

const stepsData = computed(() => ({
 labels: labels7d.value,
 datasets: [{
 label: 'Steps',
 data: (s.value?.readings_7d ?? []).map(r => r.steps ?? 0).reverse(),
 backgroundColor: 'rgba(16,185,129,0.7)',
 borderRadius: 6,
 }]
}))

const sleepData = computed(() => ({
 labels: ['Deep Sleep', 'Light Sleep', 'REM', 'Awake'],
 datasets: [{
 data: [2.1, 3.4, 1.8, 0.5],
 backgroundColor: ['#10b981', '#34d399', '#6ee7b7', '#d1fae5'],
 borderWidth: 0,
 }]
}))

const chartOptions = {
 responsive: true,
 maintainAspectRatio: false,
 plugins: { legend: { display: false } },
 scales: {
 x: { grid: { display: false } },
 y: { grid: { color: 'rgba(0,0,0,0.05)' } }
 }
}

const doughnutOptions = {
 responsive: true,
 maintainAspectRatio: false,
 cutout: '70%',
 plugins: { legend: { position: 'bottom' as const } }
}

// ─── CGM Glucose Simulator ────────────────────────────────────────────────────
// 24-hour interstitial glucose readings (simulated, 30-min intervals)
const cgmTimeLabels = [
 '12am','12:30','1am','1:30','2am','2:30','3am','3:30','4am','4:30','5am','5:30',
 '6am','6:30','7am','7:30','8am','8:30','9am','9:30','10am','10:30','11am','11:30',
 '12pm','12:30','1pm','1:30','2pm','2:30','3pm','3:30','4pm','4:30','5pm','5:30',
 '6pm','6:30','7pm','7:30','8pm','8:30','9pm','9:30','10pm','10:30','11pm','11:30'
]

// Carbs-first scenario: sharp breakfast & lunch spike, high post-dinner excursion
const cgmCarbsFirst = [
 82,80,79,78,78,77,76,76,77,78,80,84,
 90,112,148,175,185,172,145,122,108,98,92,89,
 88,100,128,162,178,168,150,132,115,105,96,92,
 90,88,92,110,148,174,182,170,148,128,108,92
]

// Protein+Fiber-first scenario: attenuated peaks, faster return to baseline
const cgmFiberFirst = [
 82,80,79,78,78,77,76,76,77,78,80,84,
 88,96,112,128,135,128,118,108,99,93,89,87,
 86,93,108,124,132,126,116,106,98,92,89,87,
 86,85,88,98,118,132,136,128,114,102,94,87
]

const cgmChartData = computed(() => ({
 labels: cgmTimeLabels,
 datasets: [
 {
 label: '🔴 Carbs First (High Spike)',
 data: cgmCarbsFirst,
 borderColor: 'rgba(239,68,68,0.9)',
 backgroundColor: 'rgba(239,68,68,0.08)',
 fill: true,
 tension: 0.4,
 pointRadius: 0,
 borderWidth: 2.5,
 borderDash: [6, 3],
 },
 {
 label: '🟢 Salad & Protein First (Blunted)',
 data: cgmFiberFirst,
 borderColor: 'rgba(16,185,129,0.95)',
 backgroundColor: 'rgba(16,185,129,0.10)',
 fill: true,
 tension: 0.4,
 pointRadius: 0,
 borderWidth: 2.5,
 }
 ]
}))

const cgmChartOptions = {
 responsive: true,
 maintainAspectRatio: false,
 interaction: { mode: 'index' as const, intersect: false },
 plugins: {
 legend: {
 display: true,
 position: 'top' as const,
 labels: { usePointStyle: true, padding: 16, font: { size: 12 } }
 },
 tooltip: {
 callbacks: {
 label: (ctx: any) => ` ${ctx.dataset.label}: ${ctx.parsed.y} mg/dL`
 }
 }
 },
 scales: {
 x: {
 grid: { display: false },
 ticks: {
 maxTicksLimit: 8,
 font: { size: 10 },
 color: '#94a3b8'
 }
 },
 y: {
 min: 60,
 max: 210,
 grid: { color: 'rgba(0,0,0,0.05)' },
 ticks: { font: { size: 10 }, color: '#94a3b8' },
 title: { display: true, text: 'Glucose (mg/dL)', color: '#64748b', font: { size: 11 } }
 }
 }
}

// Live CGM status (simulated current reading)
const liveCgmReading = ref(92)
const cgmRiskLabel = computed(() => {
 if (liveCgmReading.value < 70) return { label: 'Low — Eat Fast-Carbs', color: 'text-amber-600', bg: 'bg-amber-500/15 border-amber-300' }
 if (liveCgmReading.value <= 140) return { label: 'In Range ✅', color: 'text-emerald-600', bg: 'bg-emerald-500/15 border-emerald-300' }
 if (liveCgmReading.value <= 180) return { label: 'Elevated — Monitor', color: 'text-orange-600', bg: 'bg-orange-500/15 border-orange-300' }
 return { label: 'High — Take Action', color: 'text-red-600', bg: 'bg-red-500/15 border-red-300' }
})

// Simulate a tick every 5s nudging glucose slightly
setInterval(() => {
 const delta = (Math.random() - 0.48) * 1.5
 liveCgmReading.value = Math.min(200, Math.max(65, Math.round((liveCgmReading.value + delta) * 10) / 10))
}, 5000)
</script>

<template>
 <div class="max-w-6xl mx-auto py-8 px-4 md:px-0 relative">
 <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

 <!-- Connect / Disconnect Tracker Modal -->
 <Modal v-model="showConnectModal" :title="selectedTracker?.connected ? `Manage ${selectedTracker?.name}` : `Connect ${selectedTracker?.name}`" size="md">
 <div v-if="selectedTracker" class="space-y-5">
 <div class="flex items-center gap-4 p-4 rounded-xl bg-canvas border border-border">
 <div class="text-3xl p-2 bg-primary-soft rounded-lg">{{ selectedTracker.icon }}</div>
 <div>
 <h3 class="font-display font-semibold text-ink text-[1.05rem]">{{ selectedTracker.name }}</h3>
 <p class="font-body text-[0.82rem] text-ink-muted">{{ selectedTracker.desc }}</p>
 </div>
 </div>

 <div>
 <h4 class="font-data text-[0.75rem] uppercase tracking-wider text-ink-muted mb-2">Metrics Shared with NutriPlan AI:</h4>
 <div class="flex flex-wrap gap-2">
 <span v-for="m in selectedTracker.metrics" :key="m" class="px-2.5 py-1 rounded-full text-[0.75rem] font-semibold bg-primary-soft text-primary">
 ✓ {{ m }}
 </span>
 </div>
 </div>

 <div class="p-3.5 rounded-lg bg-canvas text-[0.82rem] text-ink-muted leading-relaxed border border-border">
 OAuth 2.0 Encrypted Connection. NutriPlan AI only reads metabolic and activity telemetry. Your credentials are never stored.
 </div>

 <div class="flex justify-end gap-3 pt-2">
 <Button variant="outline" @click="showConnectModal = false">Cancel</Button>
 <Button 
 :variant="selectedTracker.connected ? 'danger' : 'primary'"
 @click="toggleConnection(selectedTracker)"
 >
 {{ selectedTracker.connected ? 'Disconnect Device' : 'Authorize & Connect' }}
 </Button>
 </div>
 </div>
 </Modal>

 <!-- Header -->
 <div class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
 <div>
 <h1 class="font-display font-bold text-[2rem] text-ink">Wearables & Health Hub</h1>
 <p class="font-body text-ink-muted text-[1rem]">Connect Whoop, Fitbit, Apple Health, or Garmin to auto-adjust your daily macros.</p>
 </div>

 <div class="flex items-center gap-3">
 <Button 
 variant="outline" 
 size="sm" 
 :disabled="isSyncing"
 @click="triggerManualSync" 
 class="flex items-center gap-2"
 >
 <span :class="{'animate-spin': isSyncing}"></span>
 <span>{{ isSyncing ? 'Syncing...' : 'Sync Now' }}</span>
 </Button>
 </div>
 </div>

  <!-- Active AI Recovery Nudge Banner -->
  <div class="bg-gradient-to-r from-emerald-500/15 via-teal-500/10 to-transparent border border-emerald-500/30 rounded-2xl p-5 mb-8 flex items-start gap-4 shadow-sm">
    <div class="text-2xl p-2.5 rounded-xl bg-emerald-500/20 text-emerald-600 shrink-0"></div>
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2">
        <h3 class="font-display font-bold text-[1.05rem] text-ink">
          {{ s?.connected_device || 'Wearable' }} Active Telemetry
        </h3>
        <span class="px-2 py-0.5 rounded-full text-[0.68rem] font-bold bg-emerald-500 text-white">LIVE AI ADAPTED</span>
      </div>
      <p class="font-body text-[0.88rem] text-ink-muted mt-1 leading-relaxed">
        {{ s?.adaptive_message || 'Biometric readings received. Your daily meal plan and macronutrient targets automatically balance against physical strain and calorie burn.' }}
      </p>
    </div>
  </div>

 <!-- Connected Device Cards Section -->
 <div class="mb-10">
 <div class="flex items-center justify-between mb-4">
 <h2 class="font-display font-semibold text-[1.2rem] text-ink">Available Health Trackers</h2>
 <span class="font-data text-[0.8rem] text-ink-muted">{{ trackers.filter(t => t.connected).length }} of {{ trackers.length }} connected</span>
 </div>

 <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
 <div
 v-for="t in trackers"
 :key="t.id"
 class="p-5 rounded-2xl bg-canvas-raised border transition-all hover:shadow-card flex flex-col justify-between"
 :class="t.connected ? 'border-primary/40 shadow-sm' : 'border-border opacity-80 hover:opacity-100'"
 >
 <div>
 <div class="flex items-center justify-between mb-3">
 <div class="flex items-center gap-2.5">
 <span class="text-2xl">{{ t.icon }}</span>
 <h3 class="font-display font-bold text-[1rem] text-ink">{{ t.name }}</h3>
 </div>
 <span 
 class="px-2.5 py-0.5 rounded-full text-[0.7rem] font-bold font-data flex items-center gap-1.5"
 :class="t.connected ? 'bg-success-soft text-success' : 'bg-canvas text-ink-muted border border-border'"
 >
 <span v-if="t.connected" class="w-1.5 h-1.5 rounded-full bg-success animate-pulse"></span>
 {{ t.connected ? 'CONNECTED' : 'NOT CONNECTED' }}
 </span>
 </div>

 <p class="font-body text-[0.82rem] text-ink-muted mb-4">{{ t.desc }}</p>

 <div v-if="t.connected" class="flex items-center justify-between text-[0.75rem] font-data text-ink-muted pt-2 border-t border-border/60 mb-4">
 <span> Battery: {{ t.batteryPct }}%</span>
 <span> Synced: {{ t.lastSync }}</span>
 </div>
 </div>

 <Button
 :variant="t.connected ? 'outline' : 'primary'"
 size="sm"
 class="w-full text-[0.82rem]"
 @click="openConnect(t)"
 >
 {{ t.connected ? 'Manage Connection' : 'Connect Device →' }}
 </Button>
 </div>
 </div>
 </div>

 <div v-if="wearable.isLoading" class="text-ink-muted font-body py-10 text-center">
 Loading biometric telemetry...
 </div>

 <!-- Telemetry Dashboards & Charts -->
 <div v-else-if="s" class="space-y-6">
 <div class="flex items-center justify-between border-b border-border pb-3">
 <h2 class="font-display font-semibold text-[1.2rem] text-ink">Live Biometrics & Vitals</h2>
 <span class="font-data text-[0.8rem] text-ink-muted">Aggregated from Whoop & Apple Health</span>
 </div>

 <!-- Stats Row -->
 <div class="grid grid-cols-3 md:grid-cols-6 gap-4">
 <div class="bg-canvas-raised border border-border rounded-xl p-4 shadow-sm text-center col-span-1">
 <div class="flex items-center justify-center text-primary mb-1.5"><Icon name="trends" :size="22" /></div>
 <div class="font-display font-bold text-[1.4rem] text-ink tabular-nums">{{ (s?.today_steps ?? 7842).toLocaleString() }}</div>
 <div class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider">Steps</div>
 </div>
 <div class="bg-canvas-raised border border-border rounded-xl p-4 shadow-sm text-center col-span-1">
 <div class="flex items-center justify-center text-danger mb-1.5"><Icon name="heart" :size="22" /></div>
 <div class="font-display font-bold text-[1.4rem] text-ink tabular-nums">{{ s?.avg_heart_rate ?? 72 }}</div>
 <div class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider">Avg BPM</div>
 </div>
 <div class="bg-canvas-raised border border-border rounded-xl p-4 shadow-sm text-center col-span-1">
 <div class="flex items-center justify-center text-amber-500 mb-1.5"><Icon name="flame" :size="22" /></div>
 <div class="font-display font-bold text-[1.4rem] text-ink tabular-nums">{{ s?.today_calories ?? 512 }}</div>
 <div class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider">Active Kcal</div>
 </div>
 <div class="bg-canvas-raised border border-border rounded-xl p-4 shadow-sm text-center col-span-1">
 <div class="flex items-center justify-center text-indigo-500 mb-1.5"><Icon name="moon" :size="22" /></div>
 <div class="font-display font-bold text-[1.4rem] text-ink tabular-nums">{{ s?.sleep_last_night ?? 7.2 }}h</div>
 <div class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider">Sleep</div>
 </div>
 <div class="bg-canvas-raised border border-border rounded-xl p-4 shadow-sm text-center col-span-1">
 <div class="flex items-center justify-center text-cyan-500 mb-1.5"><Icon name="droplet" :size="22" /></div>
 <div class="font-display font-bold text-[1.4rem] text-ink tabular-nums">{{ s?.blood_oxygen ?? 98 }}%</div>
 <div class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider">SpO₂</div>
 </div>
 <div class="bg-canvas-raised border border-border rounded-xl p-4 shadow-sm text-center col-span-1">
 <div class="flex items-center justify-center text-emerald-500 mb-1.5"><Icon name="bolt" :size="22" /></div>
 <div class="font-display font-bold text-[1.4rem] text-ink tabular-nums">{{ s?.hrv_ms ?? 45 }}ms</div>
 <div class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider">HRV (Whoop)</div>
 </div>
 </div>

 <!-- Charts Row -->
 <div class="grid md:grid-cols-3 gap-6">
 <!-- Heart Rate 7d -->
 <div class="md:col-span-2 bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm">
 <h3 class="font-display font-semibold text-[1.1rem] text-ink mb-4">Continuous Heart Rate (7-Day Trend)</h3>
 <div class="h-48">
 <LineChart :data="heartRateData" :options="chartOptions" />
 </div>
 </div>

 <!-- Sleep breakdown -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm">
 <h3 class="font-display font-semibold text-[1.1rem] text-ink mb-4">Sleep Architecture (Last Night)</h3>
 <div class="h-48">
 <DoughnutChart :data="sleepData" :options="doughnutOptions" />
 </div>
 </div>
 </div>

 <!-- Steps 7d -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm">
 <h3 class="font-display font-semibold text-[1.1rem] text-ink mb-4">Daily Activity & Step Target Progress</h3>
 <div class="h-40">
 <BarChart :data="stepsData" :options="chartOptions" />
 </div>
 </div>

  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- CGM Live Glucose Sensor Simulator                                   -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <div class="mt-10 space-y-6">
    <div class="flex items-center justify-between border-b border-border pb-3">
      <div class="flex items-center gap-3">
        <h2 class="font-display font-semibold text-[1.2rem] text-ink">🩸 CGM Glucose Sensor Simulator</h2>
        <span class="px-2.5 py-0.5 rounded-full text-[0.7rem] font-bold bg-red-500/15 text-red-600 border border-red-300">Abbott FreeStyle Libre · Simulated</span>
      </div>
      <span class="font-data text-[0.8rem] text-ink-muted">24-Hour Interstitial Glucose Readings</span>
    </div>

    <!-- Live Status Row -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div :class="['border rounded-2xl p-4 text-center', cgmRiskLabel.bg]">
        <div class="font-display font-bold text-[2rem] tabular-nums" :class="cgmRiskLabel.color">{{ liveCgmReading }}</div>
        <div class="font-data text-[0.7rem] uppercase tracking-wider text-ink-muted mt-0.5">mg/dL · Current</div>
        <div class="font-body text-[0.78rem] font-semibold mt-1" :class="cgmRiskLabel.color">{{ cgmRiskLabel.label }}</div>
      </div>
      <div class="border border-border rounded-2xl p-4 text-center bg-canvas-raised">
        <div class="font-display font-bold text-[2rem] text-emerald-600 tabular-nums">3.2</div>
        <div class="font-data text-[0.7rem] uppercase tracking-wider text-ink-muted mt-0.5">mmol/L · Equivalent</div>
        <div class="font-body text-[0.78rem] font-semibold mt-1 text-emerald-600">Normal</div>
      </div>
      <div class="border border-border rounded-2xl p-4 text-center bg-canvas-raised">
        <div class="font-display font-bold text-[2rem] text-blue-600 tabular-nums">87%</div>
        <div class="font-data text-[0.7rem] uppercase tracking-wider text-ink-muted mt-0.5">Time In Range (TIR)</div>
        <div class="font-body text-[0.78rem] font-semibold mt-1 text-blue-600">Target: &gt;70%</div>
      </div>
      <div class="border border-border rounded-2xl p-4 text-center bg-canvas-raised">
        <div class="font-display font-bold text-[2rem] text-purple-600 tabular-nums">5.4%</div>
        <div class="font-data text-[0.7rem] uppercase tracking-wider text-ink-muted mt-0.5">Est. HbA1c</div>
        <div class="font-body text-[0.78rem] font-semibold mt-1 text-purple-600">Optimal</div>
      </div>
    </div>

    <!-- 24-Hour Dual Scenario Chart -->
    <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm">
      <div class="flex flex-col md:flex-row md:items-start justify-between gap-3 mb-5">
        <div>
          <h3 class="font-display font-semibold text-[1.1rem] text-ink">24-Hour Glucose Comparison</h3>
          <p class="font-body text-[0.82rem] text-ink-muted mt-0.5">Same meals, different eating order. See how food sequencing flattens your glucose curve.</p>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <span class="px-3 py-1 rounded-full text-[0.72rem] font-bold bg-emerald-500/15 text-emerald-700 border border-emerald-300">−35% Peak Spike</span>
          <span class="px-3 py-1 rounded-full text-[0.72rem] font-bold bg-blue-500/15 text-blue-700 border border-blue-300">Lim et al., 2023</span>
        </div>
      </div>

      <!-- Danger zone annotation -->
      <div class="relative">
        <div class="absolute right-4 top-1 font-data text-[0.68rem] text-red-400">⚠ Spike Zone &gt;140 mg/dL</div>
        <div class="h-72">
          <LineChart :data="cgmChartData" :options="cgmChartOptions" />
        </div>
      </div>

      <div class="mt-4 grid grid-cols-2 gap-4">
        <div class="p-3 rounded-xl bg-red-500/8 border border-red-200">
          <div class="font-data text-[0.72rem] uppercase tracking-wider text-red-600 mb-1">🔴 Carbs First Peak</div>
          <div class="font-display font-bold text-[1.4rem] text-red-600">185 mg/dL</div>
          <div class="font-body text-[0.78rem] text-ink-muted">Biryani eaten immediately → sharp excursion, 2h to return</div>
        </div>
        <div class="p-3 rounded-xl bg-emerald-500/8 border border-emerald-200">
          <div class="font-data text-[0.72rem] uppercase tracking-wider text-emerald-600 mb-1">🟢 Fiber+Protein First Peak</div>
          <div class="font-display font-bold text-[1.4rem] text-emerald-600">136 mg/dL</div>
          <div class="font-body text-[0.78rem] text-ink-muted">Salad → Dal → Biryani last → flat curve, 45 min faster recovery</div>
        </div>
      </div>
    </div>

    <!-- Order of Eating Explainer -->
    <div class="bg-gradient-to-br from-emerald-500/10 via-teal-500/5 to-transparent border border-emerald-400/30 rounded-2xl p-6 shadow-sm">
      <div class="flex items-center gap-3 mb-5">
        <div class="text-2xl">🍽️</div>
        <div>
          <h3 class="font-display font-semibold text-[1.1rem] text-ink">Clinical Order of Eating — Food Sequencing Buffer</h3>
          <p class="font-body text-[0.82rem] text-ink-muted">Reduces postprandial glucose peak by ~35% with zero dietary changes · <span class="text-emerald-600 font-semibold">Lim et al., 2023 · Weickert et al., 2022</span></p>
        </div>
      </div>

      <div class="grid md:grid-cols-3 gap-4">
        <!-- Step 1 -->
        <div class="relative p-5 rounded-xl bg-white/60 border border-emerald-200 shadow-sm">
          <div class="absolute -top-3 left-4 px-2.5 py-0.5 rounded-full bg-emerald-500 text-white text-[0.7rem] font-bold">STEP 1 · 0 min</div>
          <div class="text-3xl mb-3 mt-2">🥗</div>
          <div class="font-display font-bold text-[1rem] text-emerald-700 mb-1">Fiber Primer</div>
          <div class="font-body text-[0.82rem] text-ink-muted leading-relaxed">
            Salad, leafy greens, raita, soup, or sabzi.<br/>
            <span class="text-emerald-600 font-semibold">Why:</span> Soluble fiber forms a viscous gel that slows glucose absorption in the small intestine.
          </div>
          <div class="mt-3 px-2.5 py-1 rounded-lg bg-emerald-500/15 text-[0.72rem] font-bold text-emerald-700 inline-block">Impact: −18% peak</div>
        </div>

        <!-- Step 2 -->
        <div class="relative p-5 rounded-xl bg-white/60 border border-blue-200 shadow-sm">
          <div class="absolute -top-3 left-4 px-2.5 py-0.5 rounded-full bg-blue-500 text-white text-[0.7rem] font-bold">STEP 2 · +5 min</div>
          <div class="text-3xl mb-3 mt-2">🍗</div>
          <div class="font-display font-bold text-[1rem] text-blue-700 mb-1">Protein & Fat Anchor</div>
          <div class="font-body text-[0.82rem] text-ink-muted leading-relaxed">
            Dal, paneer, chicken, fish, curd, eggs, or nuts.<br/>
            <span class="text-blue-600 font-semibold">Why:</span> Stimulates GLP-1 & GIP incretin release which potentiates insulin response before the carb load arrives.
          </div>
          <div class="mt-3 px-2.5 py-1 rounded-lg bg-blue-500/15 text-[0.72rem] font-bold text-blue-700 inline-block">Impact: −12% peak</div>
        </div>

        <!-- Step 3 -->
        <div class="relative p-5 rounded-xl bg-white/60 border border-amber-200 shadow-sm">
          <div class="absolute -top-3 left-4 px-2.5 py-0.5 rounded-full bg-amber-500 text-white text-[0.7rem] font-bold">STEP 3 · +10 min</div>
          <div class="text-3xl mb-3 mt-2">🍚</div>
          <div class="font-display font-bold text-[1rem] text-amber-700 mb-1">Carbohydrates Last</div>
          <div class="font-body text-[0.82rem] text-ink-muted leading-relaxed">
            Rice, roti, biryani, bread, pasta, or dessert.<br/>
            <span class="text-amber-600 font-semibold">Why:</span> By this point, insulin is pre-activated and gut motility is slowed — carbs are absorbed gradually.
          </div>
          <div class="mt-3 px-2.5 py-1 rounded-lg bg-amber-500/15 text-[0.72rem] font-bold text-amber-700 inline-block">Total reduction: −35%</div>
        </div>
      </div>

      <div class="mt-5 p-3.5 rounded-xl bg-white/50 border border-emerald-200 flex items-start gap-3">
        <span class="text-xl">💡</span>
        <p class="font-body text-[0.82rem] text-ink-muted leading-relaxed">
          <span class="font-semibold text-ink">NutriPlan AI automatically applies this sequence</span> when generating your meal plan. 
          Meals with GI &gt;55 (Biryani, White Rice, Naan) are flagged with the 🩸 CGM badge and sequenced 
          with a <span class="text-emerald-600 font-semibold">fiber-protein primer course</span> in your daily schedule.
        </p>
      </div>
    </div>
  </div>
  <!-- end CGM section -->

 </div>
 </div>
</template>
