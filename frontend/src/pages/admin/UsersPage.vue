<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import apiClient from '../../api'

const users = ref<any[]>([])
const isLoading = ref(false)
const searchQuery = ref('')

// Pagination
const currentPage = ref(1)
const pageSize = 10

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

onMounted(() => {
  fetchUsers()
})

const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) return users.value
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u =>
    u.name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q) || u.role?.toLowerCase().includes(q)
  )
})

// Reset to page 1 when search changes
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
              <th class="py-3 px-5 font-semibold">Email</th>
              <th class="py-3 px-5 font-semibold">Plan</th>
              <th class="py-3 px-5 font-semibold">Status</th>
              <th class="py-3 px-5 font-semibold text-right">Joined</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border font-body text-[0.86rem]">
            <tr v-for="user in paginatedUsers" :key="user.id" class="hover:bg-canvas/40 transition-colors">
              <td class="py-3.5 px-5 font-medium text-ink">
                <div class="font-semibold">{{ user.name }}</div>
                <span class="text-[0.7rem] font-bold text-primary uppercase font-data">{{ user.role }}</span>
              </td>
              <td class="py-3.5 px-5 text-ink-muted">{{ user.email }}</td>
              <td class="py-3.5 px-5">
                <span 
                  class="font-data text-[0.72rem] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider border"
                  :class="user.plan === 'Premium' || user.plan === 'pro' || user.plan === 'family' ? 'bg-primary-soft text-primary border-primary/20' : 'bg-canvas text-ink-muted border-border'"
                >
                  {{ user.plan || 'Free' }}
                </span>
              </td>
              <td class="py-3.5 px-5">
                <div class="flex items-center gap-1.5">
                  <div class="w-2 h-2 rounded-full" :class="user.status === 'Active' ? 'bg-success' : 'bg-danger'"></div>
                  <span class="font-data text-[0.78rem]" :class="user.status === 'Active' ? 'text-success' : 'text-danger'">{{ user.status }}</span>
                </div>
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

