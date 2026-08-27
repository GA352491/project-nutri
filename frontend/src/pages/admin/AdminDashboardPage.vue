<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import apiClient from '../../api'
import Icon from '../../components/ui/Icon.vue'

const stats = ref({
  total_users: 0,
  active_subscriptions: 0,
  recipes_curated: 0,
  daily_active_users: 0
})

const system_health = ref<any[]>([])
const isLoading = ref(true)

async function fetchAdminStats() {
  isLoading.value = true
  try {
    const res = await apiClient.get('/admin/dashboard')
    if (res.data) {
      if (res.data.stats) stats.value = res.data.stats
      if (res.data.system_health) system_health.value = res.data.system_health
    }
  } catch (err) {
    console.warn('Failed to load admin dashboard stats from backend API:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => { fetchAdminStats() })

const healthyCount = computed(() => system_health.value.filter(s => s.status === 'healthy').length)
const unhealthyCount = computed(() => system_health.value.length - healthyCount.value)

const kpiCards = computed(() => [
  {
    label: 'Total Users',
    value: stats.value.total_users.toLocaleString(),
    sub: 'Registered accounts',
    icon: 'users',
    accent: 'primary',
    bg: 'bg-primary-soft',
    color: 'text-primary'
  },
  {
    label: 'Active Subscriptions',
    value: stats.value.active_subscriptions.toLocaleString(),
    sub: 'Paying customers',
    icon: 'pricing',
    accent: 'emerald',
    bg: 'bg-emerald-50',
    color: 'text-emerald-700'
  },
  {
    label: 'Recipes Curated',
    value: stats.value.recipes_curated.toLocaleString(),
    sub: 'In content library',
    icon: 'recipe',
    accent: 'amber',
    bg: 'bg-amber-50',
    color: 'text-amber-700'
  },
  {
    label: 'Daily Active Users',
    value: stats.value.daily_active_users.toLocaleString(),
    sub: 'Last 24 hours',
    icon: 'activity',
    accent: 'purple',
    bg: 'bg-purple-50',
    color: 'text-purple-700'
  }
])
</script>

<template>
  <div class="space-y-8">

    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="font-display font-bold text-[1.7rem] text-ink">Platform Overview</h1>
        <p class="font-body text-ink-muted text-[0.93rem] mt-0.5">
          Real-time health of all NutriPlan services and key platform metrics.
        </p>
      </div>
      <button
        @click="fetchAdminStats"
        class="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-border bg-canvas text-[0.85rem] font-semibold text-ink hover:bg-canvas-raised transition-colors"
        :disabled="isLoading"
      >
        <Icon name="activity" :size="14" :class="isLoading ? 'animate-spin' : ''" />
        {{ isLoading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <!-- KPI Metric Cards -->
    <div class="grid grid-cols-2 xl:grid-cols-4 gap-5">
      <div
        v-for="card in kpiCards"
        :key="card.label"
        class="bg-canvas-raised border border-border rounded-2xl p-5 shadow-xs flex flex-col gap-3"
      >
        <div class="flex items-start justify-between">
          <div class="text-[0.78rem] font-data font-semibold text-ink-muted uppercase tracking-wider leading-none">
            {{ card.label }}
          </div>
          <div class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0" :class="card.bg">
            <Icon :name="card.icon" :size="17" :class="card.color" />
          </div>
        </div>
        <div class="font-display font-bold text-[2rem] text-ink leading-none tabular-nums">
          <span v-if="isLoading" class="inline-block w-16 h-7 bg-border/60 rounded animate-pulse" />
          <span v-else>{{ card.value }}</span>
        </div>
        <div class="font-body text-[0.78rem] text-ink-muted">{{ card.sub }}</div>
      </div>
    </div>

    <!-- System Health + Quick Links Row -->
    <div class="grid xl:grid-cols-3 gap-6">

      <!-- System Health Table — takes 2/3 width -->
      <div class="xl:col-span-2 bg-canvas-raised border border-border rounded-2xl overflow-hidden shadow-xs">
        <div class="px-6 py-4 border-b border-border flex items-center justify-between">
          <div>
            <h2 class="font-display font-semibold text-[1.1rem] text-ink">Service Health</h2>
            <p class="font-body text-[0.78rem] text-ink-muted mt-0.5">All microservice status and response latency</p>
          </div>
          <div class="flex items-center gap-3">
            <span v-if="!isLoading" class="inline-flex items-center gap-1.5 text-[0.75rem] font-semibold text-success">
              <span class="w-2 h-2 rounded-full bg-success"></span>
              {{ healthyCount }} healthy
            </span>
            <span v-if="unhealthyCount > 0" class="inline-flex items-center gap-1.5 text-[0.75rem] font-semibold text-danger">
              <span class="w-2 h-2 rounded-full bg-danger"></span>
              {{ unhealthyCount }} degraded
            </span>
          </div>
        </div>

        <!-- Loading skeleton -->
        <div v-if="isLoading" class="p-6 space-y-3">
          <div v-for="i in 6" :key="i" class="h-10 bg-border/30 rounded-lg animate-pulse" />
        </div>

        <!-- Empty state -->
        <div v-else-if="system_health.length === 0" class="p-10 text-center">
          <Icon name="activity" :size="28" class="mx-auto mb-3 text-ink-muted/40" />
          <p class="font-body text-[0.9rem] text-ink-muted">No services reporting. Check backend connectivity.</p>
        </div>

        <table v-else class="w-full text-left">
          <thead>
            <tr class="bg-canvas/60 border-b border-border">
              <th class="py-2.5 px-5 font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-semibold">Service</th>
              <th class="py-2.5 px-5 font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-semibold">Status</th>
              <th class="py-2.5 px-5 font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-semibold text-right">Latency</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr
              v-for="service in system_health"
              :key="service.service_name"
              class="hover:bg-canvas/40 transition-colors"
            >
              <td class="py-3 px-5 font-body text-[0.875rem] font-medium text-ink">
                {{ service.service_name }}
              </td>
              <td class="py-3 px-5">
                <span
                  class="inline-flex items-center gap-1.5 text-[0.78rem] font-semibold capitalize px-2.5 py-0.5 rounded-full border"
                  :class="service.status === 'healthy'
                    ? 'bg-success-soft text-success border-success/30'
                    : 'bg-danger-soft text-danger border-danger/30'"
                >
                  <span class="w-1.5 h-1.5 rounded-full" :class="service.status === 'healthy' ? 'bg-success' : 'bg-danger'"></span>
                  {{ service.status }}
                </span>
              </td>
              <td class="py-3 px-5 text-right font-data text-[0.82rem] tabular-nums">
                <span :class="service.latency_ms > 100 ? 'text-amber-600 font-bold' : service.latency_ms > 200 ? 'text-danger font-bold' : 'text-ink-muted'">
                  {{ service.latency_ms }} ms
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Quick Actions Panel -->
      <div class="space-y-4">
        <div class="bg-canvas-raised border border-border rounded-2xl p-5 shadow-xs">
          <h2 class="font-display font-semibold text-[1rem] text-ink mb-4">Quick Actions</h2>
          <div class="space-y-2">
            <a href="/admin/users" class="flex items-center gap-3 p-3 rounded-xl bg-canvas hover:bg-primary-soft/30 hover:text-primary transition-colors group">
              <div class="w-8 h-8 rounded-lg bg-primary-soft text-primary flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                <Icon name="users" :size="15" />
              </div>
              <div>
                <div class="font-semibold text-[0.85rem]">Manage Users</div>
                <div class="text-[0.72rem] text-ink-muted">View, search, and manage all accounts</div>
              </div>
            </a>
            <a href="/admin/payments" class="flex items-center gap-3 p-3 rounded-xl bg-canvas hover:bg-primary-soft/30 hover:text-primary transition-colors group">
              <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                <Icon name="pricing" :size="15" />
              </div>
              <div>
                <div class="font-semibold text-[0.85rem]">Payments & Subs</div>
                <div class="text-[0.72rem] text-ink-muted">Subscription ledger and MRR metrics</div>
              </div>
            </a>
            <a href="/admin/audit-logs" class="flex items-center gap-3 p-3 rounded-xl bg-canvas hover:bg-primary-soft/30 hover:text-primary transition-colors group">
              <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                <Icon name="lock" :size="15" />
              </div>
              <div>
                <div class="font-semibold text-[0.85rem]">Audit Trail</div>
                <div class="text-[0.72rem] text-ink-muted">View all admin action logs</div>
              </div>
            </a>
            <a href="/admin/feature-flags" class="flex items-center gap-3 p-3 rounded-xl bg-canvas hover:bg-primary-soft/30 hover:text-primary transition-colors group">
              <div class="w-8 h-8 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                <Icon name="settings" :size="15" />
              </div>
              <div>
                <div class="font-semibold text-[0.85rem]">Feature Flags</div>
                <div class="text-[0.72rem] text-ink-muted">Remote config and canary rollouts</div>
              </div>
            </a>
            <a href="/admin/llm-router" class="flex items-center gap-3 p-3 rounded-xl bg-canvas hover:bg-primary-soft/30 hover:text-primary transition-colors group">
              <div class="w-8 h-8 rounded-lg bg-sky-50 text-sky-700 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                <Icon name="ai" :size="15" />
              </div>
              <div>
                <div class="font-semibold text-[0.85rem]">LLM Router</div>
                <div class="text-[0.72rem] text-ink-muted">Model routing and cost budgets</div>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
