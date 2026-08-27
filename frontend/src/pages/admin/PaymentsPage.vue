<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import apiClient from '../../api'
import Icon from '../../components/ui/Icon.vue'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'

interface SubscriptionRecord {
  id: string
  user_id: string
  user_email?: string
  user_name?: string
  tier: string
  status: string
  provider: string
  provider_subscription_id?: string
  amount_inr: number
  current_period_start: string
  current_period_end: string
  cancel_at_period_end: boolean
  family_plan_id?: string
}

const subscriptions = ref<SubscriptionRecord[]>([])
const isLoading = ref(false)
const totalRecords = ref(0)
const totalPages = ref(1)
const mrrInr = ref(0)
const activePaidCount = ref(0)
const familyPlansCount = ref(0)

// Filters & Pagination State
const currentPage = ref(1)
const pageSize = ref(10)
const selectedTier = ref('all')
const selectedStatus = ref('all')
const searchQuery = ref('')
const searchDebounce = ref<any>(null)

// User map cache for resolving User IDs to Names/Emails
const userMap = ref<Record<string, { name: string; email: string }>>({})

const showToast = ref(false)
const toastMsg = ref('')

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 2500)
}

function copyToClipboard(text: string, label: string) {
  navigator.clipboard.writeText(text)
  notify(`Copied ${label} to clipboard!`)
}

async function fetchUsersCache() {
  try {
    const res = await apiClient.get('/auth/users')
    if (res.data && Array.isArray(res.data)) {
      const map: Record<string, { name: string; email: string }> = {}
      res.data.forEach((u: any) => {
        if (u.id) {
          map[u.id] = { name: u.name || 'User', email: u.email || '' }
        }
      })
      userMap.value = map
    }
  } catch {
    // Graceful fallback
  }
}

async function fetchSubscriptions() {
  isLoading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (selectedTier.value !== 'all') params.tier = selectedTier.value
    if (selectedStatus.value !== 'all') params.status = selectedStatus.value
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()

    const res = await apiClient.get('/subscriptions/admin/all', { params })
    if (res.data) {
      subscriptions.value = res.data.items || []
      totalRecords.value = res.data.total || 0
      totalPages.value = res.data.total_pages || 1
      mrrInr.value = res.data.mrr_inr || 0
      activePaidCount.value = res.data.active_paid_count || 0
      familyPlansCount.value = res.data.family_plans_count || 0
    }
  } catch (err) {
    console.error('Failed to load subscriptions:', err)
    notify('Failed to load payment records.')
  } finally {
    isLoading.value = false
  }
}

function onSearchInput() {
  clearTimeout(searchDebounce.value)
  searchDebounce.value = setTimeout(() => {
    currentPage.value = 1
    fetchSubscriptions()
  }, 300)
}

watch([selectedTier, selectedStatus, pageSize], () => {
  currentPage.value = 1
  fetchSubscriptions()
})

watch(currentPage, () => {
  fetchSubscriptions()
})

onMounted(async () => {
  await fetchUsersCache()
  await fetchSubscriptions()
})

function formatPrice(amount: number) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount)
}

function formatDate(dateStr: string) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

function getTierBadgeClass(tier: string) {
  switch (tier.toLowerCase()) {
    case 'family':
      return 'bg-purple-100 text-purple-800 border-purple-200'
    case 'pro':
    case 'premium':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200'
    default:
      return 'bg-canvas text-ink-muted border-border'
  }
}

function getStatusBadgeClass(status: string) {
  switch (status.toLowerCase()) {
    case 'active':
      return 'bg-success-soft text-success border-success/30'
    case 'trialing':
      return 'bg-amber-100 text-amber-800 border-amber-300'
    case 'past_due':
      return 'bg-danger-soft text-danger border-danger/30'
    case 'canceled':
    case 'cancelled':
      return 'bg-canvas text-ink-muted border-border'
    default:
      return 'bg-canvas text-ink-muted border-border'
  }
}

const rangeStart = computed(() => {
  if (totalRecords.value === 0) return 0
  return (currentPage.value - 1) * pageSize.value + 1
})

const rangeEnd = computed(() => {
  return Math.min(currentPage.value * pageSize.value, totalRecords.value)
})
</script>

<template>
  <div class="space-y-6">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display font-bold text-[1.6rem] text-ink">Payments & Subscriptions</h1>
        <p class="font-body text-ink-muted text-[0.92rem]">
          Live telemetry of user plans, subscription IDs, billing periods, and recurring MRR.
        </p>
      </div>
      <div class="flex items-center gap-3">
        <Button variant="outline" size="sm" @click="fetchSubscriptions" :disabled="isLoading">
          <Icon name="activity" :size="14" class="mr-1.5" />
          {{ isLoading ? 'Refreshing...' : 'Refresh Records' }}
        </Button>
      </div>
    </div>

    <!-- Metric KPI Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="p-5 rounded-2xl bg-canvas-raised border border-border shadow-xs">
        <div class="flex items-center justify-between text-ink-muted mb-2">
          <span class="font-body text-[0.82rem] font-semibold uppercase tracking-wider">Total Subscriptions</span>
          <div class="w-8 h-8 rounded-lg bg-primary-soft text-primary flex items-center justify-center">
            <Icon name="users" :size="16" />
          </div>
        </div>
        <div class="font-display font-bold text-[1.8rem] text-ink">{{ totalRecords }}</div>
        <div class="font-data text-[0.75rem] text-ink-muted mt-1">Platform Accounts Tracked</div>
      </div>

      <div class="p-5 rounded-2xl bg-canvas-raised border border-border shadow-xs">
        <div class="flex items-center justify-between text-ink-muted mb-2">
          <span class="font-body text-[0.82rem] font-semibold uppercase tracking-wider">Active Paid Users</span>
          <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
            <Icon name="shield-check" :size="16" />
          </div>
        </div>
        <div class="font-display font-bold text-[1.8rem] text-emerald-700">{{ activePaidCount }}</div>
        <div class="font-data text-[0.75rem] text-ink-muted mt-1">Pro & Family Tier Active</div>
      </div>

      <div class="p-5 rounded-2xl bg-canvas-raised border border-border shadow-xs">
        <div class="flex items-center justify-between text-ink-muted mb-2">
          <span class="font-body text-[0.82rem] font-semibold uppercase tracking-wider">Estimated MRR</span>
          <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center">
            <Icon name="trends" :size="16" />
          </div>
        </div>
        <div class="font-display font-bold text-[1.8rem] text-ink">{{ formatPrice(mrrInr) }}</div>
        <div class="font-data text-[0.75rem] text-ink-muted mt-1">Monthly Recurring Run-rate</div>
      </div>

      <div class="p-5 rounded-2xl bg-canvas-raised border border-border shadow-xs">
        <div class="flex items-center justify-between text-ink-muted mb-2">
          <span class="font-body text-[0.82rem] font-semibold uppercase tracking-wider">Family Plans</span>
          <div class="w-8 h-8 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center">
            <Icon name="users" :size="16" />
          </div>
        </div>
        <div class="font-display font-bold text-[1.8rem] text-purple-700">{{ familyPlansCount }}</div>
        <div class="font-data text-[0.75rem] text-ink-muted mt-1">Multi-seat Umbrella Hubs</div>
      </div>
    </div>

    <!-- Filters and Search Toolbar -->
    <div class="bg-canvas-raised border border-border rounded-2xl p-4 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex-1 flex flex-col sm:flex-row items-center gap-3">
        <!-- Search Input -->
        <div class="relative w-full sm:w-80">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search Sub ID, User ID, or Provider ID..."
            @input="onSearchInput"
            class="w-full pl-9 pr-4 py-2 text-[0.86rem] bg-canvas border border-border rounded-xl text-ink placeholder:text-ink-muted/50 outline-none focus:border-primary"
          />
          <svg class="w-4 h-4 text-ink-muted absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <!-- Tier Filter -->
        <div class="flex items-center gap-2 w-full sm:w-auto">
          <span class="text-xs font-semibold text-ink-muted uppercase">Tier:</span>
          <select
            v-model="selectedTier"
            class="px-3 py-2 text-[0.85rem] bg-canvas border border-border rounded-xl text-ink outline-none focus:border-primary"
          >
            <option value="all">All Tiers</option>
            <option value="free">Free Starter</option>
            <option value="pro">Pro Clinical AI</option>
            <option value="premium">Premium</option>
            <option value="family">Family Care</option>
          </select>
        </div>

        <!-- Status Filter -->
        <div class="flex items-center gap-2 w-full sm:w-auto">
          <span class="text-xs font-semibold text-ink-muted uppercase">Status:</span>
          <select
            v-model="selectedStatus"
            class="px-3 py-2 text-[0.85rem] bg-canvas border border-border rounded-xl text-ink outline-none focus:border-primary"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="trialing">Trialing</option>
            <option value="past_due">Past Due</option>
            <option value="canceled">Canceled</option>
          </select>
        </div>
      </div>

      <!-- Page Size Selector -->
      <div class="flex items-center gap-2 self-end sm:self-auto">
        <span class="text-xs font-semibold text-ink-muted uppercase">Rows:</span>
        <select
          v-model.number="pageSize"
          class="px-2.5 py-1.5 text-[0.82rem] bg-canvas border border-border rounded-lg text-ink outline-none focus:border-primary"
        >
          <option :value="10">10</option>
          <option :value="25">25</option>
          <option :value="50">50</option>
        </select>
      </div>
    </div>

    <!-- Payments & Subscriptions Table -->
    <div class="bg-canvas-raised border border-border rounded-2xl overflow-hidden shadow-xs">
      <div v-if="isLoading" class="p-12 text-center text-ink-muted">
        <div class="animate-spin inline-block w-6 h-6 border-2 border-primary border-t-transparent rounded-full mb-3"></div>
        <p class="font-body text-[0.9rem]">Fetching subscription & payment ledger...</p>
      </div>

      <div v-else-if="subscriptions.length === 0" class="p-12 text-center text-ink-muted">
        <Icon name="credit-card" :size="32" class="mx-auto mb-3 opacity-40" />
        <p class="font-display font-semibold text-[1.1rem] text-ink mb-1">No Subscription Records Found</p>
        <p class="font-body text-[0.85rem] text-ink-muted">Try adjusting your search keywords or tier filters.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-canvas border-b border-border text-[0.72rem] font-data text-ink-muted uppercase tracking-wider">
              <th class="py-3 px-4">Subscription & User ID</th>
              <th class="py-3 px-4">User / Account</th>
              <th class="py-3 px-4">Plan & Amount</th>
              <th class="py-3 px-4">Provider / Reference</th>
              <th class="py-3 px-4">Status</th>
              <th class="py-3 px-4">Billing Period</th>
              <th class="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border font-body text-[0.86rem]">
            <tr
              v-for="sub in subscriptions"
              :key="sub.id"
              class="hover:bg-canvas/50 transition-colors"
            >
              <!-- Subscription ID & User ID -->
              <td class="py-3.5 px-4 font-data">
                <div class="flex items-center gap-1.5">
                  <span class="font-mono text-ink text-[0.82rem] font-semibold">{{ sub.id.slice(0, 8) }}...</span>
                  <button
                    @click="copyToClipboard(sub.id, 'Subscription ID')"
                    title="Copy full Subscription UUID"
                    class="text-ink-muted hover:text-primary transition-colors cursor-pointer text-xs"
                  >
                    📋
                  </button>
                </div>
                <div class="flex items-center gap-1 text-[0.72rem] text-ink-muted mt-0.5">
                  <span>User:</span>
                  <span class="font-mono">{{ sub.user_id.slice(0, 8) }}...</span>
                  <button
                    @click="copyToClipboard(sub.user_id, 'User UUID')"
                    title="Copy User UUID"
                    class="text-ink-muted hover:text-primary transition-colors cursor-pointer text-[10px]"
                  >
                    📋
                  </button>
                </div>
              </td>

              <!-- User / Account -->
              <td class="py-3.5 px-4">
                <div class="font-semibold text-ink">
                  {{ userMap[sub.user_id]?.name || 'Platform Member' }}
                </div>
                <div class="text-[0.76rem] text-ink-muted">
                  {{ userMap[sub.user_id]?.email || (sub.user_id === '00000000-0000-0000-0000-000000000000' ? 'System Demo' : 'Synced via Auth') }}
                </div>
              </td>

              <!-- Plan & Amount -->
              <td class="py-3.5 px-4">
                <div class="flex items-center gap-2">
                  <span
                    class="px-2.5 py-0.5 rounded-full text-[0.72rem] font-bold border uppercase tracking-wider"
                    :class="getTierBadgeClass(sub.tier)"
                  >
                    {{ sub.tier }}
                  </span>
                </div>
                <div class="font-data font-bold text-[0.82rem] text-ink mt-1">
                  {{ formatPrice(sub.amount_inr) }} / mo
                </div>
              </td>

              <!-- Provider / Provider Subscription ID -->
              <td class="py-3.5 px-4 font-data">
                <div class="flex items-center gap-1.5">
                  <span class="px-2 py-0.5 rounded text-[0.7rem] font-semibold bg-canvas border border-border uppercase">
                    {{ sub.provider }}
                  </span>
                </div>
                <div class="text-[0.74rem] text-ink-muted font-mono mt-1 flex items-center gap-1">
                  <span>{{ sub.provider_subscription_id || 'sub_mock_sys' }}</span>
                  <button
                    v-if="sub.provider_subscription_id"
                    @click="copyToClipboard(sub.provider_subscription_id, 'Provider Sub ID')"
                    title="Copy Provider Reference"
                    class="text-ink-muted hover:text-primary text-[10px]"
                  >
                    📋
                  </button>
                </div>
              </td>

              <!-- Status -->
              <td class="py-3.5 px-4">
                <span
                  class="px-2.5 py-0.5 rounded-full text-[0.74rem] font-bold border uppercase tracking-wider"
                  :class="getStatusBadgeClass(sub.status)"
                >
                  {{ sub.status }}
                </span>
                <div v-if="sub.cancel_at_period_end" class="text-[0.68rem] text-danger font-semibold mt-1">
                  Cancels at period end
                </div>
              </td>

              <!-- Billing Period -->
              <td class="py-3.5 px-4 font-data text-[0.78rem]">
                <div class="text-ink">
                  {{ formatDate(sub.current_period_start) }}
                </div>
                <div class="text-ink-muted text-[0.72rem]">
                  to {{ formatDate(sub.current_period_end) }}
                </div>
              </td>

              <!-- Actions -->
              <td class="py-3.5 px-4 text-right">
                <Button
                  size="sm"
                  variant="outline"
                  @click="copyToClipboard(JSON.stringify(sub, null, 2), 'JSON Telemetry')"
                  title="Copy full JSON record"
                >
                  JSON
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <div class="p-4 bg-canvas border-t border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="font-data text-[0.8rem] text-ink-muted">
          Showing <strong>{{ rangeStart }}–{{ rangeEnd }}</strong> of <strong>{{ totalRecords }}</strong> records
        </div>

        <div class="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            :disabled="currentPage <= 1 || isLoading"
            @click="currentPage--"
          >
            ← Previous
          </Button>
          <span class="font-data text-[0.82rem] text-ink-muted px-2">
            Page <strong>{{ currentPage }}</strong> of <strong>{{ totalPages }}</strong>
          </span>
          <Button
            size="sm"
            variant="outline"
            :disabled="currentPage >= totalPages || isLoading"
            @click="currentPage++"
          >
            Next →
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
