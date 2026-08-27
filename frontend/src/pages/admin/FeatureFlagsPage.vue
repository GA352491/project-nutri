<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '../../api'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'

interface FeatureFlag {
  key: string
  name: string
  description: string
  enabled: boolean
  category: 'ai' | 'checkout' | 'regional' | 'media'
  rollout_pct: number
  updated_at: string
}

const flags = ref<FeatureFlag[]>([])
const isLoading = ref(false)
const updatingKey = ref<string | null>(null)

const showToast = ref(false)
const toastMsg = ref('')

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3500)
}

async function fetchFlags() {
  isLoading.value = true
  try {
    const res = await apiClient.get('/admin/feature-flags')
    if (res.data && Array.isArray(res.data)) {
      flags.value = res.data
    }
  } catch (err) {
    console.warn('Failed to load feature flags:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchFlags()
})

async function toggleFlag(flag: FeatureFlag) {
  updatingKey.value = flag.key
  const newStatus = !flag.enabled
  try {
    const res = await apiClient.patch(`/admin/feature-flags/${flag.key}`, {
      enabled: newStatus
    })
    flag.enabled = res.data.enabled
    flag.updated_at = res.data.updated_at
    notify(`Flag "${flag.name}" is now ${newStatus ? 'ENABLED' : 'DISABLED'}`)
  } catch (err) {
    console.error('Failed to toggle flag:', err)
    notify(`Failed to update feature flag: ${flag.name}`)
  } finally {
    updatingKey.value = null
  }
}

async function updateRollout(flag: FeatureFlag, pct: number) {
  updatingKey.value = flag.key
  try {
    const res = await apiClient.patch(`/admin/feature-flags/${flag.key}`, {
      rollout_pct: pct
    })
    flag.rollout_pct = res.data.rollout_pct
    flag.updated_at = res.data.updated_at
    notify(`Updated "${flag.name}" rollout to ${pct}%`)
  } catch (err) {
    console.error('Failed to update rollout percentage:', err)
  } finally {
    updatingKey.value = null
  }
}
</script>

<template>
  <div class="space-y-6">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- Header Controls -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="font-display font-bold text-[1.7rem] text-ink">Feature Flags &amp; Remote Config</h1>
        <p class="font-body text-[0.93rem] text-ink-muted mt-0.5">
          Dynamically enable, disable, and canary-rollout microservice capabilities with sub-second propagation.
        </p>
      </div>
      <Button variant="outline" size="sm" @click="fetchFlags" :disabled="isLoading" class="shrink-0">
        Refresh Flags
      </Button>
    </div>

    <!-- Active Flags Grid -->
    <!-- Loading Skeleton -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="i in 4" :key="i" class="h-44 bg-border/30 rounded-2xl animate-pulse" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div 
        v-for="flag in flags" 
        :key="flag.key"
        class="bg-canvas-raised border border-border rounded-xl p-5 shadow-sm space-y-4 hover:border-primary/40 transition-colors"
      >
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="flex items-center gap-2">
              <h3 class="font-display font-semibold text-base text-ink">{{ flag.name }}</h3>
              <span 
                class="px-2 py-0.5 rounded text-[10px] font-bold uppercase font-data"
                :class="{
                  'bg-purple-100 text-purple-800': flag.category === 'ai',
                  'bg-emerald-100 text-emerald-800': flag.category === 'checkout',
                  'bg-amber-100 text-amber-800': flag.category === 'regional',
                  'bg-sky-100 text-sky-800': flag.category === 'media',
                }"
              >
                {{ flag.category }}
              </span>
            </div>
            <code class="text-[11px] text-ink-muted font-mono mt-0.5 block">{{ flag.key }}</code>
          </div>

          <!-- Toggle Switch -->
          <button 
            type="button" 
            role="switch" 
            :aria-checked="flag.enabled"
            :disabled="updatingKey === flag.key"
            @click="toggleFlag(flag)"
            class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none disabled:opacity-50"
            :class="flag.enabled ? 'bg-primary' : 'bg-neutral-300'"
          >
            <span 
              class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
              :class="flag.enabled ? 'translate-x-5' : 'translate-x-0'"
            />
          </button>
        </div>

        <p class="font-body text-xs text-ink-muted leading-relaxed">
          {{ flag.description }}
        </p>

        <!-- Rollout Slider Strip -->
        <div class="pt-3 border-t border-border flex items-center justify-between gap-4">
          <div class="flex-1 space-y-1">
            <div class="flex justify-between text-[11px] font-data text-ink-muted">
              <span>Traffic Rollout:</span>
              <span class="font-bold text-ink">{{ flag.rollout_pct }}%</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="100" 
              step="5"
              :value="flag.rollout_pct"
              :disabled="!flag.enabled || updatingKey === flag.key"
              @change="(e: any) => updateRollout(flag, parseInt(e.target.value))"
              class="w-full h-1.5 bg-canvas rounded-lg appearance-none cursor-pointer accent-primary disabled:opacity-40"
            />
          </div>
          <div class="text-[10px] text-ink-muted font-mono whitespace-nowrap self-end">
            {{ flag.updated_at.slice(11, 16) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
