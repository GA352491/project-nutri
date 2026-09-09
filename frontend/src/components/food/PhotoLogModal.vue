<script setup lang="ts">
import { ref, computed } from 'vue'
import apiClient from '../../api'

const emit = defineEmits<{
  close: []
  logged: [entry: { food_name: string; calories: number; protein_g: number; fat_g: number; carbs_g: number }]
}>()

// ── State ────────────────────────────────────────────────────────────────────
const phase = ref<'idle' | 'preview' | 'analyzing' | 'results' | 'logging' | 'done'>('idle')
const error = ref('')
const previewUrl = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)

interface FoodItem {
  name: string
  confidence: number
  portion_g: number
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g: number
  region: string
}

interface RecognitionResult {
  image_id: string
  items: FoodItem[]
  total_calories: number
  total_protein_g: number
  total_carbs_g: number
  total_fat_g: number
  meal_type_guess: string
  compliance_warnings: string[]
}

const result = ref<RecognitionResult | null>(null)
const selectedItems = ref<Set<number>>(new Set())
const mealType = ref('lunch')
const mealTypes = ['breakfast', 'lunch', 'snack', 'dinner']

const selectedTotal = computed(() => {
  if (!result.value) return { calories: 0, protein: 0, carbs: 0, fat: 0 }
  const items = result.value.items.filter((_, i) => selectedItems.value.has(i))
  return {
    calories: Math.round(items.reduce((s, i) => s + i.calories, 0)),
    protein: Math.round(items.reduce((s, i) => s + i.protein_g, 0)),
    carbs: Math.round(items.reduce((s, i) => s + i.carbs_g, 0)),
    fat: Math.round(items.reduce((s, i) => s + i.fat_g, 0)),
  }
})

function triggerFilePicker() { fileInput.value?.click() }

function triggerCamera() {
  if (fileInput.value) {
    fileInput.value.capture = 'environment'
    fileInput.value.click()
  }
}

function onFileSelected(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  selectedFile.value = f
  previewUrl.value = URL.createObjectURL(f)
  phase.value = 'preview'
  error.value = ''
}

async function analyzePhoto() {
  if (!selectedFile.value) return
  phase.value = 'analyzing'
  error.value = ''
  try {
    const form = new FormData()
    form.append('file', selectedFile.value)
    form.append('user_region', 'india')
    form.append('auto_log', 'false')
    const res = await apiClient.post('/food-recognition/analyze', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    result.value = res.data
    selectedItems.value = new Set(result.value!.items.map((_, i) => i))
    if (result.value?.meal_type_guess) mealType.value = result.value.meal_type_guess
    phase.value = 'results'
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Could not analyze photo. Try a clearer image.'
    phase.value = 'preview'
  }
}

function retake() {
  phase.value = 'idle'
  previewUrl.value = ''
  selectedFile.value = null
  result.value = null
  error.value = ''
  selectedItems.value = new Set()
}

function toggleItem(idx: number) {
  const s = new Set(selectedItems.value)
  if (s.has(idx)) { s.delete(idx) } else { s.add(idx) }
  selectedItems.value = s
}

async function logToDiary() {
  if (!result.value || selectedItems.value.size === 0) return
  phase.value = 'logging'
  const todayStr = new Date().toISOString().split('T')[0]
  const items = result.value.items.filter((_, i) => selectedItems.value.has(i))
  try {
    for (const item of items) {
      await apiClient.post('/diary/entries', {
        log_date: todayStr,
        meal_type: mealType.value,
        food_name: item.name,
        quantity_g: Math.round(item.portion_g),
        calories: item.calories,
        protein_g: item.protein_g,
        fat_g: item.fat_g,
        carbs_g: item.carbs_g,
        source: 'photo_log',
      })
    }
    phase.value = 'done'
    emit('logged', {
      food_name: items.map(i => i.name).join(', '),
      calories: selectedTotal.value.calories,
      protein_g: selectedTotal.value.protein,
      fat_g: selectedTotal.value.fat,
      carbs_g: selectedTotal.value.carbs,
    })
    setTimeout(() => emit('close'), 1800)
  } catch (err: any) {
    error.value = 'Failed to log entries. Please try again.'
    phase.value = 'results'
  }
}

function confidencePct(c: number) { return Math.round(c * 100) }
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')" />
    <div class="relative z-10 w-full sm:max-w-lg mx-auto bg-canvas border border-border rounded-t-3xl sm:rounded-3xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">

      <!-- Header -->
      <div class="flex items-center justify-between px-5 pt-5 pb-3 border-b border-border shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-xl bg-primary-soft text-primary flex items-center justify-center text-lg">📷</div>
          <div>
            <h2 class="font-display font-bold text-[1rem] text-ink leading-tight">Snap &amp; Log</h2>
            <p class="font-body text-[0.7rem] text-ink-muted">AI Food Recognition</p>
          </div>
        </div>
        <button
          class="w-8 h-8 rounded-full bg-canvas-raised border border-border flex items-center justify-center text-ink-muted hover:text-ink transition-colors"
          @click="$emit('close')"
        >✕</button>
      </div>

      <div class="flex-1 overflow-y-auto">

        <!-- IDLE -->
        <div v-if="phase === 'idle'" class="p-5 flex flex-col gap-4">
          <div
            class="border-2 border-dashed border-border rounded-2xl p-10 flex flex-col items-center gap-3 hover:border-primary/50 hover:bg-primary-soft/20 transition-all cursor-pointer group"
            @click="triggerFilePicker"
          >
            <div class="w-16 h-16 rounded-2xl bg-primary-soft flex items-center justify-center text-3xl group-hover:scale-110 transition-transform">🍱</div>
            <p class="font-display font-semibold text-ink text-[0.95rem]">Upload a Food Photo</p>
            <p class="font-body text-[0.78rem] text-ink-muted text-center">JPEG · PNG · WebP · Max 10MB</p>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex-1 h-px bg-border" />
            <span class="font-body text-[0.72rem] text-ink-muted">or</span>
            <div class="flex-1 h-px bg-border" />
          </div>
          <button
            class="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-primary text-white font-semibold text-[0.9rem] hover:opacity-90 active:scale-95 transition-all shadow-lg shadow-primary/30"
            @click="triggerCamera"
          >
            <span class="text-lg">📸</span> Take a Photo
          </button>
          <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileSelected" />
        </div>

        <!-- PREVIEW -->
        <div v-else-if="phase === 'preview'" class="p-5 flex flex-col gap-4">
          <div class="relative rounded-2xl overflow-hidden bg-canvas-raised border border-border" style="aspect-ratio:4/3;">
            <img :src="previewUrl" alt="Food preview" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
          </div>
          <div v-if="error" class="px-4 py-3 rounded-xl bg-danger/10 border border-danger/30 text-danger text-[0.82rem] font-body">
            ⚠️ {{ error }}
          </div>
          <div class="flex gap-3">
            <button class="flex-1 py-3 rounded-xl border border-border text-ink font-semibold text-[0.9rem] hover:bg-canvas-raised transition-colors" @click="retake">Retake</button>
            <button class="flex-1 py-3 rounded-xl bg-primary text-white font-semibold text-[0.9rem] hover:opacity-90 transition-opacity shadow-lg shadow-primary/30" @click="analyzePhoto">🤖 Analyse</button>
          </div>
        </div>

        <!-- ANALYZING -->
        <div v-else-if="phase === 'analyzing'" class="p-8 flex flex-col items-center gap-5">
          <div class="relative w-20 h-20">
            <div class="absolute inset-0 rounded-full border-4 border-primary/20" />
            <div class="absolute inset-0 rounded-full border-4 border-t-primary animate-spin" />
            <div class="absolute inset-0 flex items-center justify-center text-3xl">🔬</div>
          </div>
          <div class="text-center">
            <p class="font-display font-bold text-ink text-[1rem]">Identifying Food Items…</p>
            <p class="font-body text-ink-muted text-[0.78rem] mt-1">Running LLaVA vision model + IFCT nutrition lookup</p>
          </div>
        </div>

        <!-- RESULTS -->
        <div v-else-if="phase === 'results' && result" class="p-5 flex flex-col gap-4">
          <div class="rounded-xl overflow-hidden border border-border" style="height:140px;">
            <img :src="previewUrl" alt="Analysed photo" class="w-full h-full object-cover" />
          </div>

          <div v-if="result.compliance_warnings.length > 0" class="flex flex-col gap-1.5">
            <div v-for="(w, i) in result.compliance_warnings" :key="i" class="px-3 py-2 rounded-lg bg-warning/10 border border-warning/20 text-ink text-[0.78rem] font-body">{{ w }}</div>
          </div>

          <div>
            <p class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider mb-2">Select items to log:</p>
            <div class="flex flex-col gap-2">
              <button
                v-for="(item, idx) in result.items"
                :key="idx"
                class="flex items-center gap-3 px-4 py-3 rounded-xl border transition-all text-left"
                :class="selectedItems.has(idx) ? 'border-primary bg-primary-soft' : 'border-border bg-canvas-raised hover:border-primary/30'"
                @click="toggleItem(idx)"
              >
                <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors" :class="selectedItems.has(idx) ? 'border-primary bg-primary text-white' : 'border-border'">
                  <span v-if="selectedItems.has(idx)" class="text-[0.6rem] font-bold">✓</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="font-display font-semibold text-[0.88rem] text-ink truncate">{{ item.name }}</div>
                  <div class="font-data text-[0.7rem] text-ink-muted">{{ Math.round(item.portion_g) }}g · {{ Math.round(item.calories) }} kcal · P {{ Math.round(item.protein_g) }}g</div>
                </div>
                <div class="text-[0.68rem] font-data text-ink-muted">{{ confidencePct(item.confidence) }}%</div>
              </button>
            </div>
          </div>

          <!-- Selected totals -->
          <div class="grid grid-cols-4 gap-2 px-4 py-3 rounded-xl bg-canvas-raised border border-border">
            <div class="text-center" v-for="[label, val] in [['kcal', selectedTotal.calories], ['Prot', selectedTotal.protein], ['Carbs', selectedTotal.carbs], ['Fat', selectedTotal.fat]]" :key="String(label)">
              <div class="font-data font-bold text-[1rem] text-ink tabular-nums">{{ val }}</div>
              <div class="font-data text-[0.66rem] text-ink-muted uppercase tracking-wide">{{ label }}</div>
            </div>
          </div>

          <!-- Meal type -->
          <div>
            <p class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wider mb-2">Meal type:</p>
            <div class="flex gap-2 flex-wrap">
              <button
                v-for="mt in mealTypes"
                :key="mt"
                class="px-4 py-1.5 rounded-full border text-[0.8rem] font-semibold capitalize transition-all"
                :class="mealType === mt ? 'bg-primary text-white border-primary' : 'bg-canvas-raised border-border text-ink hover:border-primary/50'"
                @click="mealType = mt"
              >{{ mt }}</button>
            </div>
          </div>

          <div v-if="error" class="px-3 py-2 rounded-lg bg-danger/10 border border-danger/20 text-danger text-[0.8rem]">⚠️ {{ error }}</div>

          <div class="flex gap-3">
            <button class="flex-1 py-3 rounded-xl border border-border text-ink font-semibold text-[0.88rem] hover:bg-canvas-raised transition-colors" @click="retake">Retake</button>
            <button
              class="flex-1 py-3 rounded-xl font-semibold text-[0.88rem] transition-all shadow-lg shadow-primary/30"
              :class="selectedItems.size > 0 ? 'bg-primary text-white hover:opacity-90' : 'bg-border text-ink-muted cursor-not-allowed'"
              :disabled="selectedItems.size === 0"
              @click="logToDiary"
            >Log {{ selectedItems.size }} Item{{ selectedItems.size !== 1 ? 's' : '' }} →</button>
          </div>
        </div>

        <!-- LOGGING -->
        <div v-else-if="phase === 'logging'" class="p-8 flex flex-col items-center gap-4">
          <div class="relative w-16 h-16">
            <div class="absolute inset-0 rounded-full border-4 border-t-primary animate-spin" />
            <div class="absolute inset-0 flex items-center justify-center text-2xl">📓</div>
          </div>
          <p class="font-display font-semibold text-ink">Saving to Diary…</p>
        </div>

        <!-- DONE -->
        <div v-else-if="phase === 'done'" class="p-8 flex flex-col items-center gap-4">
          <div class="w-16 h-16 rounded-full bg-success/10 border-2 border-success flex items-center justify-center text-3xl animate-bounce">✅</div>
          <div class="text-center">
            <p class="font-display font-bold text-ink text-[1.05rem]">Logged!</p>
            <p class="font-body text-ink-muted text-[0.82rem] mt-1">{{ selectedTotal.calories }} kcal added to your diary</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
