<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import apiClient from '../../api'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'

interface AuditLog {
  id: string
  timestamp: string
  actor_id: string
  actor_email: string
  actor_role: string
  action: string
  resource_type: string
  resource_id?: string
  status: string
  ip_address: string
  details?: string
}

const logs = ref<AuditLog[]>([])
const isLoading = ref(false)
const searchQuery = ref('')
const selectedAction = ref('all')
const selectedResource = ref('all')

const showToast = ref(false)
const toastMsg = ref('')

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3500)
}

// Pagination
const currentPage = ref(1)
const pageSize = 8

async function fetchAuditLogs() {
  isLoading.value = true
  try {
    const params: any = {}
    if (selectedAction.value !== 'all') params.action = selectedAction.value
    if (selectedResource.value !== 'all') params.resource_type = selectedResource.value
    const res = await apiClient.get('/admin/audit-logs', { params })
    if (res.data && Array.isArray(res.data)) {
      logs.value = res.data
    }
  } catch (err) {
    console.warn('Failed to load audit logs:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAuditLogs()
})

watch([selectedAction, selectedResource], () => {
  fetchAuditLogs()
  currentPage.value = 1
})

const filteredLogs = computed(() => {
  if (!searchQuery.value.trim()) return logs.value
  const q = searchQuery.value.toLowerCase()
  return logs.value.filter(l =>
    l.actor_email.toLowerCase().includes(q) ||
    l.action.toLowerCase().includes(q) ||
    l.resource_type.toLowerCase().includes(q) ||
    (l.details && l.details.toLowerCase().includes(q))
  )
})

watch(searchQuery, () => { currentPage.value = 1 })

const totalPages = computed(() => Math.max(1, Math.ceil(filteredLogs.value.length / pageSize)))
const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredLogs.value.slice(start, start + pageSize)
})

const rangeStart = computed(() => Math.min((currentPage.value - 1) * pageSize + 1, filteredLogs.value.length))
const rangeEnd = computed(() => Math.min(currentPage.value * pageSize, filteredLogs.value.length))

function exportCsv() {
  if (filteredLogs.value.length === 0) return
  const headers = ['Timestamp', 'Actor Email', 'Role', 'Action', 'Resource', 'Resource ID', 'Status', 'IP', 'Details']
  const rows = filteredLogs.value.map(l => [
    `"${l.timestamp}"`,
    `"${l.actor_email}"`,
    `"${l.actor_role}"`,
    `"${l.action}"`,
    `"${l.resource_type}"`,
    `"${l.resource_id || ''}"`,
    `"${l.status}"`,
    `"${l.ip_address}"`,
    `"${(l.details || '').replace(/"/g, '""')}"`
  ])
  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `nutriplan_audit_trail_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  notify('Audit log CSV exported successfully! 📄')
}
</script>

<template>
  <div class="space-y-6">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- Header Controls -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="font-display font-bold text-[1.7rem] text-ink">Audit Trail &amp; Compliance</h1>
        <p class="font-body text-[0.93rem] text-ink-muted mt-0.5">
          Immutable forensic log of all administrative actions, clinical record reads, and configuration changes.
        </p>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <Button variant="outline" size="sm" @click="fetchAuditLogs" :disabled="isLoading">
          Refresh
        </Button>
        <Button variant="primary" size="sm" @click="exportCsv">
          Export CSV
        </Button>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="flex flex-wrap items-center justify-between gap-4 bg-canvas-raised p-4 rounded-2xl border border-border shadow-xs">
      <div class="flex flex-wrap items-center gap-3 flex-1">
        <!-- Search Input -->
        <div class="relative min-w-[240px] flex-1 max-w-md">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by actor, action, or context..."
            class="w-full font-body text-[0.88rem] text-ink bg-canvas border border-border rounded-xl pl-9 pr-4 py-2 outline-none focus:border-primary"
          />
          <svg class="w-4 h-4 text-ink-muted absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <!-- Action Filter -->
        <select v-model="selectedAction" class="font-body text-[0.88rem] text-ink bg-canvas border border-border rounded-xl px-3 py-2 outline-none focus:border-primary">
          <option value="all">All Actions</option>
          <option value="READ">READ</option>
          <option value="WRITE">WRITE</option>
          <option value="DELETE">DELETE</option>
          <option value="EXPORT">EXPORT</option>
          <option value="VERIFY">VERIFY</option>
          <option value="BROADCAST">BROADCAST</option>
        </select>
        <!-- Resource Filter -->
        <select v-model="selectedResource" class="font-body text-[0.88rem] text-ink bg-canvas border border-border rounded-xl px-3 py-2 outline-none focus:border-primary">
          <option value="all">All Resources</option>
          <option value="USER">USER</option>
          <option value="NUTRITIONIST">NUTRITIONIST</option>
          <option value="MEAL_PLAN">MEAL_PLAN</option>
          <option value="FEATURE_FLAG">FEATURE_FLAG</option>
          <option value="NOTIFICATION">NOTIFICATION</option>
          <option value="SYSTEM">SYSTEM</option>
        </select>
      </div>
      <div class="font-data text-[0.8rem] text-ink-muted">
        <span class="font-semibold text-ink">{{ filteredLogs.length }}</span> records
      </div>
    </div>

    <!-- Audit Logs Table -->
    <div class="bg-canvas-raised border border-border rounded-2xl overflow-hidden shadow-xs">
      <div v-if="isLoading" class="p-8 space-y-3">
        <div v-for="i in 6" :key="i" class="h-10 bg-border/30 rounded-lg animate-pulse" />
      </div>
      <div v-else-if="filteredLogs.length === 0" class="p-12 text-center">
        <p class="font-display font-semibold text-[1rem] text-ink mb-1">No audit events match your filters</p>
        <p class="font-body text-[0.85rem] text-ink-muted">Try adjusting the search or action filter above.</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="sticky top-0 z-10">
            <tr class="bg-canvas border-b border-border">
              <th class="py-2.5 px-5 font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-semibold whitespace-nowrap">Timestamp</th>
              <th class="py-2.5 px-5 font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-semibold">Actor</th>
              <th class="py-2.5 px-5 font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-semibold">Action</th>
              <th class="py-2.5 px-5 font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-semibold">Resource</th>
              <th class="py-2.5 px-5 font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-semibold">Status</th>
              <th class="py-2.5 px-5 font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-semibold">Details</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-for="log in paginatedLogs" :key="log.id" class="hover:bg-canvas/40 transition-colors">
              <td class="py-3 px-5 font-mono text-[0.78rem] text-ink-muted whitespace-nowrap">{{ log.timestamp }}</td>
              <td class="py-3 px-5">
                <div class="font-semibold text-[0.86rem] text-ink">{{ log.actor_email }}</div>
                <span class="font-data text-[0.7rem] text-primary uppercase font-bold">{{ log.actor_role }}</span>
              </td>
              <td class="py-3 px-5">
                <span
                  class="px-2.5 py-0.5 rounded-md font-bold uppercase tracking-wider text-[0.7rem]"
                  :class="{
                    'bg-sky-100 text-sky-800': log.action === 'READ',
                    'bg-emerald-100 text-emerald-800': log.action === 'WRITE' || log.action === 'VERIFY',
                    'bg-rose-100 text-rose-800': log.action === 'DELETE',
                    'bg-purple-100 text-purple-800': log.action === 'EXPORT' || log.action === 'BROADCAST',
                  }"
                >
                  {{ log.action }}
                </span>
              </td>
              <td class="py-3 px-5">
                <span class="font-mono font-semibold text-[0.82rem] text-ink">{{ log.resource_type }}</span>
                <span v-if="log.resource_id" class="text-ink-muted text-[0.72rem] block font-mono">#{{ log.resource_id }}</span>
              </td>
              <td class="py-3 px-5">
                <span
                  class="font-data font-bold uppercase text-[0.7rem] px-2.5 py-0.5 rounded-full inline-flex items-center gap-1.5"
                  :class="log.status === 'SUCCESS' ? 'bg-success-soft text-success' : 'bg-danger-soft text-danger'"
                >
                  <span class="w-1.5 h-1.5 rounded-full" :class="log.status === 'SUCCESS' ? 'bg-success' : 'bg-danger'"></span>
                  {{ log.status }}
                </span>
              </td>
              <td class="py-3 px-5 font-body text-[0.82rem] text-ink-muted max-w-xs truncate">
                {{ log.details || '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <div v-if="!isLoading && filteredLogs.length > 0" class="px-5 py-4 bg-canvas border-t border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <p class="font-data text-[0.8rem] text-ink-muted">
          Showing <strong>{{ rangeStart }}–{{ rangeEnd }}</strong> of <strong>{{ filteredLogs.length }}</strong> audit records
        </p>
        <div class="flex items-center gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage <= 1"
            class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-border bg-canvas text-ink disabled:opacity-40 hover:bg-canvas-raised transition-colors"
          >
            ← Previous
          </button>
          <span class="font-data text-[0.8rem] text-ink-muted">Page <strong>{{ currentPage }}</strong> of <strong>{{ totalPages }}</strong></span>
          <button
            @click="currentPage++"
            :disabled="currentPage >= totalPages"
            class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-border bg-canvas text-ink disabled:opacity-40 hover:bg-canvas-raised transition-colors"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
