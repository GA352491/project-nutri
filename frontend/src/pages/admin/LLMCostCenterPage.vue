<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '../../api'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'
import Modal from '../../components/ui/Modal.vue'

interface LLMModelOption {
  id: string
  name: string
  provider: string
  cost_per_1k_input_usd: number
  cost_per_1k_output_usd: number
  is_local: boolean
  context_window: number
  supports_vision: boolean
}

interface ServiceLLMConfig {
  service_key: string
  service_name: string
  description: string
  selected_model_id: string
  fallback_model_id: string
  temperature: number
  max_tokens: number
  user_rate_limit_per_hour: number
  monthly_budget_usd: number
  current_burn_usd: number
  total_tokens_consumed: number
  total_requests: number
}

interface UserBurnMetric {
  user_id: string
  user_email: string
  user_role: string
  plan: string
  requests_today: number
  rate_limit_hourly: number
  tokens_consumed: number
  total_cost_burned_usd: number
  last_active: string
  status: string
}

interface CostCenterOverview {
  total_burned_usd: number
  monthly_budget_total_usd: number
  local_inference_savings_usd: number
  total_tokens_processed: number
  cloud_vs_local_ratio: string
  services: ServiceLLMConfig[]
  available_models: LLMModelOption[]
  top_user_burners: UserBurnMetric[]
}

const overview = ref<CostCenterOverview | null>(null)
const isLoading = ref(false)
const isSaving = ref(false)
const showToast = ref(false)
const toastMsg = ref('')

const selectedService = ref<ServiceLLMConfig | null>(null)
const isEditModalOpen = ref(false)

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3500)
}

async function fetchCostCenter() {
  isLoading.value = true
  try {
    const res = await apiClient.get('/admin/cost-center')
    if (res.data) {
      overview.value = res.data
    }
  } catch (err) {
    console.warn('Failed to load cost center data:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchCostCenter()
})

function openConfigureModal(service: ServiceLLMConfig) {
  selectedService.value = JSON.parse(JSON.stringify(service))
  isEditModalOpen.value = true
}

async function saveServiceConfig() {
  if (!selectedService.value) return
  isSaving.value = true
  try {
    const s = selectedService.value
    const res = await apiClient.patch(`/admin/cost-center/service/${s.service_key}`, {
      selected_model_id: s.selected_model_id,
      fallback_model_id: s.fallback_model_id,
      temperature: s.temperature,
      max_tokens: s.max_tokens,
      user_rate_limit_per_hour: s.user_rate_limit_per_hour,
      monthly_budget_usd: s.monthly_budget_usd
    })
    
    // Update local list
    if (overview.value) {
      const idx = overview.value.services.findIndex(item => item.service_key === s.service_key)
      if (idx !== -1) {
        overview.value.services[idx] = res.data
      }
    }
    notify(`Updated LLM routing policy for "${s.service_name}"! 🚀`)
    isEditModalOpen.value = false
  } catch (err) {
    console.error('Failed to update LLM configuration:', err)
    notify('Failed to save LLM config. Check backend logs.')
  } finally {
    isSaving.value = false
  }
}

function getModelName(modelId: string): string {
  if (!overview.value) return modelId
  const found = overview.value.available_models.find(m => m.id === modelId)
  return found ? found.name : modelId
}

function isModelLocal(modelId: string): boolean {
  if (!overview.value) return false
  const found = overview.value.available_models.find(m => m.id === modelId)
  return found ? found.is_local : false
}
</script>

<template>
  <div class="space-y-8">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- Header Controls -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
      <div>
        <h2 class="font-display font-semibold text-[1.4rem] text-ink">LLM Dynamic Routing & Cost Center</h2>
        <p class="font-body text-[0.92rem] text-ink-muted">
          Dynamically route LLMs per microservice, enforce user rate limits, and track real-time token burn vs. local zero-cost inference.
        </p>
      </div>
      <Button variant="outline" size="sm" @click="fetchCostCenter">
        <svg class="w-3.5 h-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh Governance
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && !overview" class="p-8 text-center text-ink-muted font-body text-sm">
      Loading AI cost governance & model registry...
    </div>

    <template v-else-if="overview">

      <!-- Cost Center Strip -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <!-- Monthly Burn -->
        <div class="bg-primary/5 border border-primary/20 rounded-xl p-4">
          <div class="font-data text-[0.7rem] text-primary uppercase tracking-wider font-bold mb-1">Total Cloud Burn</div>
          <div class="font-display font-bold text-[1.8rem] text-primary">${{ overview.total_burned_usd.toFixed(2) }}</div>
          <div class="text-[11px] text-ink-muted mt-1">Budget: ${{ overview.monthly_budget_total_usd }} / mo</div>
        </div>

        <!-- Local Savings -->
        <div class="bg-success/5 border border-success/20 rounded-xl p-4">
          <div class="font-data text-[0.7rem] text-success uppercase tracking-wider font-bold mb-1">Local Ollama Savings</div>
          <div class="font-display font-bold text-[1.8rem] text-success">+${{ overview.local_inference_savings_usd.toFixed(2) }}</div>
          <div class="text-[11px] text-success/80 mt-1">Saved vs Cloud GPT-4o</div>
        </div>

        <!-- Total Tokens -->
        <div class="bg-canvas-raised border border-border rounded-xl p-4">
          <div class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider font-bold mb-1">Tokens Processed</div>
          <div class="font-display font-bold text-[1.8rem] text-ink">{{ overview.total_tokens_processed.toLocaleString() }}</div>
          <div class="text-[11px] text-ink-muted mt-1">Across 5 microservices</div>
        </div>

        <!-- Cloud vs Local Ratio -->
        <div class="bg-purple-500/5 border border-purple-500/20 rounded-xl p-4">
          <div class="font-data text-[0.7rem] text-purple-600 uppercase tracking-wider font-bold mb-1">Inference Engine</div>
          <div class="font-display font-bold text-[1.1rem] text-purple-700 mt-1 leading-tight">100% Local Ollama</div>
          <div class="text-[11px] text-purple-600/80 mt-1">Zero Cloud egress fee</div>
        </div>
      </div>

      <!-- Service LLM Router Grid -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="font-display font-semibold text-base text-ink">Microservice LLM Routing Matrix</h3>
          <span class="text-xs text-ink-muted">Configure active model, temperature & rate limits per service</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="service in overview.services" 
            :key="service.service_key"
            class="bg-canvas-raised border border-border rounded-xl p-5 shadow-sm space-y-4 flex flex-col justify-between hover:border-primary/40 transition-colors"
          >
            <div class="space-y-2">
              <div class="flex items-start justify-between gap-2">
                <h4 class="font-display font-semibold text-sm text-ink leading-tight">{{ service.service_name }}</h4>
                <span 
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase font-data"
                  :class="isModelLocal(service.selected_model_id) ? 'bg-emerald-100 text-emerald-800' : 'bg-sky-100 text-sky-800'"
                >
                  {{ isModelLocal(service.selected_model_id) ? 'Local 0$' : 'Cloud API' }}
                </span>
              </div>
              <p class="font-body text-[11px] text-ink-muted leading-relaxed line-clamp-2">
                {{ service.description }}
              </p>
            </div>

            <!-- Configuration Strip -->
            <div class="p-3 bg-canvas border border-border rounded-lg space-y-2 text-xs font-data">
              <div class="flex justify-between">
                <span class="text-ink-muted">Primary LLM:</span>
                <span class="font-bold text-ink font-mono text-[11px] text-right truncate max-w-[150px]">
                  {{ getModelName(service.selected_model_id) }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-muted">Fallback:</span>
                <span class="text-ink font-mono text-[11px] text-right truncate max-w-[150px]">
                  {{ getModelName(service.fallback_model_id) }}
                </span>
              </div>
              <div class="flex justify-between pt-1 border-t border-border/60">
                <span class="text-ink-muted">User Rate Limit:</span>
                <span class="font-bold text-primary">{{ service.user_rate_limit_per_hour }} req / hr</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-muted">Tokens Consumed:</span>
                <span class="text-ink font-mono">{{ service.total_tokens_consumed.toLocaleString() }}</span>
              </div>
            </div>

            <Button size="sm" variant="outline" class="w-full" @click="openConfigureModal(service)">
              Configure Dynamic LLM →
            </Button>
          </div>
        </div>
      </div>

      <!-- Top User Burners & Rate Limit Throttle Console -->
      <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-display font-semibold text-base text-ink">User AI Request Burn & Rate Limit Watch</h3>
            <p class="text-xs text-ink-muted">Inspect high-volume consumers, active throttling status, and token usage</p>
          </div>
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-primary/10 text-primary">
            Hourly Quota Enforced
          </span>
        </div>

        <div class="border border-border rounded-xl overflow-hidden bg-canvas">
          <div v-if="!overview.top_user_burners || overview.top_user_burners.length === 0" class="p-8 text-center text-ink-muted text-xs">
            No active user AI request telemetry recorded today.
          </div>
          <table v-else class="w-full text-left">
            <thead>
              <tr class="bg-canvas-raised border-b border-border text-[11px] font-semibold text-ink-muted uppercase">
                <th class="py-3 px-4">User</th>
                <th class="py-3 px-4">Plan</th>
                <th class="py-3 px-4">Requests Today</th>
                <th class="py-3 px-4">Hourly Limit</th>
                <th class="py-3 px-4">Tokens Burned</th>
                <th class="py-3 px-4">Est. Cost</th>
                <th class="py-3 px-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border text-xs">
              <tr v-for="user in overview.top_user_burners" :key="user.user_id" class="hover:bg-canvas-raised/50">
                <td class="py-3 px-4">
                  <div class="font-semibold text-ink">{{ user.user_email }}</div>
                  <span class="text-[10px] text-ink-muted uppercase font-data">{{ user.user_role }} · {{ user.last_active }}</span>
                </td>
                <td class="py-3 px-4 font-data font-semibold text-ink">{{ user.plan }}</td>
                <td class="py-3 px-4 font-mono font-bold text-ink">{{ user.requests_today }}</td>
                <td class="py-3 px-4 font-data text-ink-muted">{{ user.rate_limit_hourly }} / hr</td>
                <td class="py-3 px-4 font-mono text-ink">{{ user.tokens_consumed.toLocaleString() }}</td>
                <td class="py-3 px-4 font-mono text-emerald-600 font-bold">${{ user.total_cost_burned_usd.toFixed(2) }}</td>
                <td class="py-3 px-4 text-right">
                  <span 
                    class="px-2 py-0.5 rounded-full font-bold uppercase text-[10px] font-data inline-flex items-center gap-1"
                    :class="{
                      'bg-success-soft text-success': user.status === 'OK',
                      'bg-warning-soft text-warning': user.status === 'THROTTLED',
                      'bg-danger-soft text-danger': user.status === 'EXCEEDED',
                    }"
                  >
                    <span class="w-1.5 h-1.5 rounded-full" :class="user.status === 'OK' ? 'bg-success' : 'bg-warning animate-pulse'"></span>
                    {{ user.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </template>

    <!-- Configure Modal -->
    <Modal 
      v-model="isEditModalOpen" 
      :title="`Configure LLM: ${selectedService?.service_name}`" 
      size="md"
    >
      <form v-if="selectedService" @submit.prevent="saveServiceConfig" class="space-y-4">
        <!-- Selected Primary Model -->
        <div>
          <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Primary LLM Engine *</label>
          <select 
            v-model="selectedService.selected_model_id"
            class="w-full font-body text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
          >
            <option v-for="m in overview?.available_models" :key="m.id" :value="m.id">
              {{ m.name }} ({{ m.is_local ? 'Free Local' : `$${m.cost_per_1k_input_usd * 1000}/1M tokens` }})
            </option>
          </select>
        </div>

        <!-- Fallback Model -->
        <div>
          <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Fallback LLM (Failover) *</label>
          <select 
            v-model="selectedService.fallback_model_id"
            class="w-full font-body text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
          >
            <option v-for="m in overview?.available_models" :key="m.id" :value="m.id">
              {{ m.name }}
            </option>
          </select>
        </div>

        <!-- User Rate Limit & Temperature -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">User Limit (req/hr)</label>
            <input 
              v-model.number="selectedService.user_rate_limit_per_hour"
              type="number"
              min="1"
              max="500"
              required
              class="w-full font-body text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Temperature (0.0–1.0)</label>
            <input 
              v-model.number="selectedService.temperature"
              type="number"
              step="0.05"
              min="0"
              max="1"
              required
              class="w-full font-body text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
            />
          </div>
        </div>

        <!-- Max Tokens & Monthly Budget -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Max Output Tokens</label>
            <input 
              v-model.number="selectedService.max_tokens"
              type="number"
              step="128"
              min="256"
              max="8192"
              required
              class="w-full font-body text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block font-data text-xs uppercase tracking-wider text-ink-muted mb-1">Monthly Budget ($ USD)</label>
            <input 
              v-model.number="selectedService.monthly_budget_usd"
              type="number"
              step="10"
              min="10"
              max="2000"
              required
              class="w-full font-body text-xs bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
            />
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-3 border-t border-border">
          <Button variant="outline" size="sm" type="button" @click="isEditModalOpen = false">Cancel</Button>
          <Button variant="primary" size="sm" type="submit" :disabled="isSaving">
            {{ isSaving ? 'Saving...' : 'Save LLM Routing Policy' }}
          </Button>
        </div>
      </form>
    </Modal>

  </div>
</template>
