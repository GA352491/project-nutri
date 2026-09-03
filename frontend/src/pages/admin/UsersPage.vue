<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import apiClient from '../../api'

const users = ref<any[]>([])
const isLoading = ref(false)
const searchQuery = ref('')

// Per-user AI plan overrides: userId -> true/false
const userAiOverrides = ref<Record<string, boolean>>({})
const togglingUserId = ref<string | null>(null)
const triggeringUserId = ref<string | null>(null)
const toastMsg = ref('')
const showToast = ref(false)

// Global flag status
const globalAiPlanEnabled = ref(true)
const isLoadingGlobalStatus = ref(false)

// Pagination
const currentPage = ref(1)
const pageSize = 10

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3500)
}

async function fetchUsers() {
  isLoading.value = true
  try {
    const res = await apiClient.get('/auth/users')
    if (res.data && Array.isArray(res.data)) {
      users.value = res.data
    }
  } catch (err) {
    console.warn('Failed to load users from auth API:', err)
  } finally {
    isLoading.value = false
  }
}

async function fetchGlobalAiStatus() {
  isLoadingGlobalStatus.value = true
  try {
    const res = await apiClient.get('/admin/ai-plan/status')
    globalAiPlanEnabled.value = res.data?.global_enabled ?? true
  } catch {
    // default to true if admin service unavailable
  } finally {
    isLoadingGlobalStatus.value = false
  }
}

async function toggleGlobalAiPlan() {
  const newState = !globalAiPlanEnabled.value
  try {
    await apiClient.patch('/admin/feature-flags/ff_ai_auto_plan_on_register', { enabled: newState })
    globalAiPlanEnabled.value = newState
    notify(`Global AI Auto-Plan is now ${newState ? 'ENABLED' : 'DISABLED'} for all new registrations.`)
  } catch {
    notify('Failed to update global AI plan setting.')
  }
}

async function toggleUserAiPlan(user: any) {
  togglingUserId.value = user.id
  const current = userAiOverrides.value[user.id] ?? globalAiPlanEnabled.value
  const newState = !current
  try {
    await apiClient.patch(`/admin/users/${user.id}/ai-plan-override`, { enabled: newState })
    userAiOverrides.value[user.id] = newState
    notify(`AI Auto-Plan override for ${user.name}: ${newState ? 'ENABLED' : 'DISABLED'}`)
  } catch {
    notify(`Failed to update AI plan override for ${user.name}`)
  } finally {
    togglingUserId.value = null
  }
}

async function generatePlanForUser(user: any) {
  triggeringUserId.value = user.id
  try {
    const res = await apiClient.post(`/admin/users/${user.id}/generate-plan`, {
      caloric_target: 1800,
      region: 'in_south_andhra',
      dietary_flag: user.dietary_flag || 'vegetarian'
    })
    if (res.data?.status === 'success') {
      notify(`✅ AI Meal Plan generated & assigned to ${user.name}!`)
    } else {
      notify(`⏳ Meal plan generation queued for ${user.name} — will appear in their dashboard shortly.`)
    }
  } catch {
    notify(`Failed to generate plan for ${user.name}`)
  } finally {
    triggeringUserId.value = null
  }
}

function getUserAiState(user: any): boolean {
  if (user.id in userAiOverrides.value) return userAiOverrides.value[user.id]
  return globalAiPlanEnabled.value
}

onMounted(() => {
  fetchUsers()
  fetchGlobalAiStatus()
})

const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) return users.value
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u =>
    u.name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q) || u.role?.toLowerCase().includes(q)
  )
})

watch(searchQuery, () => { currentPage.value = 1 })

const totalPages = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize)))
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})

const rangeStart = computed(() => Math.min((currentPage.value - 1) * pageSize + 1, filteredUsers.value.length))
const rangeEnd = computed(() => Math.min(currentPage.value * pageSize, filteredUsers.value.length))
</script>

<template>
  <div class="space-y-6">

    <!-- Toast Notification -->
    <transition name="fade">
      <div v-if="showToast" class="fixed top-5 right-5 z-50 bg-ink text-canvas px-4 py-3 rounded-xl shadow-xl text-sm font-semibold animate-bounce-in">
        {{ toastMsg }}
      </div>
    </transition>

    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display font-bold text-[1.7rem] text-ink">User Management</h1>
        <p class="font-body text-[0.93rem] text-ink-muted mt-0.5">Directory of all registered patient, clinician, and administrator accounts.</p>
      </div>
      <div class="relative w-full sm:w-80">
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Search users by name, email, or role..." 
          class="font-body text-[0.88rem] text-ink bg-canvas-raised border border-border rounded-xl pl-9 pr-4 py-2 outline-none focus:border-primary w-full shadow-xs"
        />
        <svg class="w-4 h-4 text-ink-muted absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>

    <!-- Global AI Plan Toggle Banner -->
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border-2 transition-colors"
      :class="globalAiPlanEnabled ? 'bg-emerald-50 border-emerald-200' : 'bg-amber-50 border-amber-200'"
    >
      <div>
        <div class="flex items-center gap-2.5">
          <span
            class="w-3 h-3 rounded-full shadow"
            :class="globalAiPlanEnabled ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'"
          ></span>
          <h2 class="font-display font-bold text-[1.05rem]" :class="globalAiPlanEnabled ? 'text-emerald-800' : 'text-amber-800'">
            Global AI Meal Plan Auto-Assign
          </h2>
          <span
            class="text-[0.7rem] font-bold px-2.5 py-0.5 rounded-full font-data uppercase tracking-wider border"
            :class="globalAiPlanEnabled ? 'bg-emerald-100 text-emerald-700 border-emerald-300' : 'bg-amber-100 text-amber-700 border-amber-300'"
          >
            {{ globalAiPlanEnabled ? 'ON — Auto-assigning to new users' : 'OFF — Manual assignment only' }}
          </span>
        </div>
        <p class="font-body text-[0.83rem] mt-1.5" :class="globalAiPlanEnabled ? 'text-emerald-700' : 'text-amber-700'">
          <span v-if="globalAiPlanEnabled">After every new user completes onboarding, AI automatically generates and assigns a personalized 7-day meal plan.</span>
          <span v-else">New users complete onboarding but receive no plan — nutritionist assigns manually or user requests one explicitly.</span>
        </p>
      </div>
      <button
        @click="toggleGlobalAiPlan"
        :disabled="isLoadingGlobalStatus"
        class="shrink-0 px-5 py-2.5 rounded-xl font-semibold font-body text-sm border-2 transition-all cursor-pointer"
        :class="globalAiPlanEnabled
          ? 'bg-emerald-600 hover:bg-emerald-700 text-white border-emerald-600'
          : 'bg-amber-500 hover:bg-amber-600 text-white border-amber-500'"
      >
        {{ globalAiPlanEnabled ? 'Disable Global Auto-Assign' : 'Enable Global Auto-Assign' }}
      </button>
    </div>

    <!-- Users Table -->
    <div class="bg-canvas-raised border border-border rounded-2xl overflow-hidden shadow-xs">
      <div v-if="isLoading" class="p-8 space-y-3">
        <div v-for="i in 6" :key="i" class="h-10 bg-border/30 rounded-lg animate-pulse" />
      </div>
      <div v-else-if="filteredUsers.length === 0" class="p-12 text-center text-ink-muted">
        <p class="font-display font-semibold text-[1.1rem] text-ink mb-1">No Users Found</p>
        <p class="font-body text-[0.85rem] text-ink-muted">No registered users match your search query.</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-canvas border-b border-border text-[0.72rem] font-data text-ink-muted uppercase tracking-wider">
              <th class="py-3 px-5 font-semibold">Name & Role</th>
              <th class="py-3 px-4 font-semibold">Email</th>
              <th class="py-3 px-4 font-semibold">Plan</th>
              <th class="py-3 px-4 font-semibold">Status</th>
              <th class="py-3 px-4 font-semibold text-center">AI Auto-Plan</th>
              <th class="py-3 px-4 font-semibold text-center">Actions</th>
              <th class="py-3 px-5 font-semibold text-right">Joined</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border font-body text-[0.86rem]">
            <tr v-for="user in paginatedUsers" :key="user.id" class="hover:bg-canvas/40 transition-colors">
              <td class="py-3.5 px-5 font-medium text-ink">
                <div class="font-semibold">{{ user.name }}</div>
                <span class="text-[0.7rem] font-bold text-primary uppercase font-data">{{ user.role }}</span>
              </td>
              <td class="py-3.5 px-4 text-ink-muted text-[0.82rem]">{{ user.email }}</td>
              <td class="py-3.5 px-4">
                <span 
                  class="font-data text-[0.72rem] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider border"
                  :class="user.plan === 'Premium' || user.plan === 'pro' || user.plan === 'family' ? 'bg-primary-soft text-primary border-primary/20' : 'bg-canvas text-ink-muted border-border'"
                >
                  {{ user.plan || 'Free' }}
                </span>
              </td>
              <td class="py-3.5 px-4">
                <div class="flex items-center gap-1.5">
                  <div class="w-2 h-2 rounded-full" :class="user.status === 'Active' ? 'bg-success' : 'bg-danger'"></div>
                  <span class="font-data text-[0.78rem]" :class="user.status === 'Active' ? 'text-success' : 'text-danger'">{{ user.status }}</span>
                </div>
              </td>

              <!-- AI Auto-Plan Per-User Toggle -->
              <td class="py-3.5 px-4 text-center">
                <div class="flex flex-col items-center gap-1">
                  <button
                    @click="toggleUserAiPlan(user)"
                    :disabled="togglingUserId === user.id"
                    class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors cursor-pointer focus:outline-none disabled:opacity-50"
                    :class="getUserAiState(user) ? 'bg-emerald-500' : 'bg-border'"
                  >
                    <span
                      class="inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform"
                      :class="getUserAiState(user) ? 'translate-x-4' : 'translate-x-1'"
                    ></span>
                  </button>
                  <span class="text-[0.6rem] font-data font-bold uppercase"
                    :class="getUserAiState(user) ? 'text-emerald-600' : 'text-ink-muted'"
                  >
                    {{ user.id in userAiOverrides ? (getUserAiState(user) ? 'Override ON' : 'Override OFF') : (getUserAiState(user) ? 'Global ON' : 'Global OFF') }}
                  </span>
                </div>
              </td>

              <!-- Generate Plan Action -->
              <td class="py-3.5 px-4 text-center">
                <button
                  @click="generatePlanForUser(user)"
                  :disabled="triggeringUserId === user.id"
                  class="px-3 py-1.5 rounded-lg text-[0.72rem] font-bold font-data uppercase tracking-wide border transition-all cursor-pointer disabled:opacity-50"
                  :class="triggeringUserId === user.id
                    ? 'bg-canvas text-ink-muted border-border'
                    : 'bg-primary/10 text-primary border-primary/30 hover:bg-primary hover:text-white'"
                >
                  {{ triggeringUserId === user.id ? '⏳ Generating...' : '⚡ Assign AI Plan' }}
                </button>
              </td>

              <td class="py-3.5 px-5 text-right font-data text-[0.8rem] text-ink-muted">
                {{ user.joined || 'Recent' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <div v-if="!isLoading && filteredUsers.length > 0" class="p-4 bg-canvas border-t border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="font-data text-[0.8rem] text-ink-muted">
          Showing <strong>{{ rangeStart }}–{{ rangeEnd }}</strong> of <strong>{{ filteredUsers.length }}</strong> users
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage <= 1"
            class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-border bg-canvas text-ink disabled:opacity-40 hover:bg-canvas-raised transition-colors cursor-pointer"
          >
            ← Previous
          </button>
          <span class="font-data text-[0.82rem] text-ink-muted px-2">Page <strong>{{ currentPage }}</strong> of <strong>{{ totalPages }}</strong></span>
          <button
            @click="currentPage++"
            :disabled="currentPage >= totalPages"
            class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-border bg-canvas text-ink disabled:opacity-40 hover:bg-canvas-raised transition-colors cursor-pointer"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
