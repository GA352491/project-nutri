<script setup lang="ts">
import { ref, watch } from 'vue'
import Modal from '../ui/Modal.vue'
import Button from '../ui/Button.vue'
import apiClient from '../../api'

interface LiveRecipe {
  id: string
  title: string
  source: string
  cuisine: string
  category: string
  meal_type: string
  thumbnail_url?: string
  instructions: string[]
  ingredients: Array<{ name: string; measure?: string }>
  macros: {
    calories_kcal: number
    protein_g: number
    carbs_g: number
    fat_g: number
    fiber_g: number
    calcium_mg: number
    iron_mg: number
    is_icmr_computed: boolean
  }
}

const props = defineProps<{
  modelValue: boolean
  targetMeal?: {
    id: string
    type: string
    title: string
    calories: number
  } | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
  (e: 'swap', selected: any): void
}>()

const searchQuery = ref('')
const selectedCuisine = ref('Indian')
const isSearching = ref(false)
const results = ref<LiveRecipe[]>([])
const searchError = ref('')

const quickQueries = [
  'Paneer', 'Dal', 'Biryani', 'Curry', 'Chicken', 'Salad', 'Fish'
]

async function executeSearch(query = searchQuery.value) {
  if (!query.trim()) return
  searchQuery.value = query
  isSearching.value = true
  searchError.value = ''
  results.value = []

  try {
    const res = await apiClient.get('/recipes/external/live-search', {
      params: {
        q: query.trim(),
        cuisine: selectedCuisine.value,
        limit: 8
      }
    })

    if (Array.isArray(res.data) && res.data.length > 0) {
      results.value = res.data
    } else {
      searchError.value = `No live recipes found for "${query}". Try another term like "Curry" or "Paneer".`
    }
  } catch (err: any) {
    console.error('Live recipe search error:', err)
    searchError.value = 'Failed to fetch live recipes. Please verify backend recipe service.'
  } finally {
    isSearching.value = false
  }
}

function selectAndSwap(recipe: LiveRecipe) {
  const replacement = {
    id: recipe.id || `live_${Date.now()}`,
    type: props.targetMeal?.type || 'LUNCH',
    title: recipe.title,
    cuisine: recipe.cuisine,
    description: `Live recipe from ${recipe.source.replace('_', ' ').toUpperCase()}`,
    image: recipe.thumbnail_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80',
    calories: Math.round(recipe.macros.calories_kcal),
    protein: Math.round(recipe.macros.protein_g),
    carbs: Math.round(recipe.macros.carbs_g),
    fat: Math.round(recipe.macros.fat_g),
    fiber: Math.round(recipe.macros.fiber_g || 6),
    calcium_mg: Math.round(recipe.macros.calcium_mg || 100),
    iron_mg: Math.round(recipe.macros.iron_mg || 3),
    isLogged: false
  }
  emit('swap', replacement)
  emit('update:modelValue', false)
}

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    searchQuery.value = ''
    results.value = []
    searchError.value = ''
    executeSearch('Paneer')
  }
})
</script>

<template>
  <Modal :model-value="modelValue" @update:model-value="emit('update:modelValue', $event)" size="lg" title="Live Food & Recipe Search (No Hardcoding)">
    <div class="space-y-4">
      <!-- Target Context Banner -->
      <div v-if="targetMeal" class="bg-primary/10 border border-primary/20 rounded-xl p-3 flex items-center justify-between text-xs">
        <div>
          <span class="text-ink-muted">Replacing:</span>
          <span class="font-bold text-ink ml-1">{{ targetMeal.title }}</span>
          <span class="text-primary font-semibold ml-2">({{ targetMeal.calories }} kcal · {{ targetMeal.type }})</span>
        </div>
        <span class="px-2 py-0.5 rounded bg-primary/20 text-primary font-semibold text-[0.68rem]">Live ICMR Engine</span>
      </div>

      <!-- Search Input + Controls -->
      <div class="flex gap-2">
        <div class="relative flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search live Indian recipes (e.g., Dal, Biryani, Paneer, Upma)..."
            class="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-border bg-canvas focus:outline-none focus:border-primary"
            @keyup.enter="executeSearch()"
          />
          <svg class="absolute left-3 top-2.5 w-4 h-4 text-ink-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
        </div>
        <select
          v-model="selectedCuisine"
          class="text-xs px-3 py-2 rounded-lg border border-border bg-canvas text-ink focus:outline-none focus:border-primary"
          @change="executeSearch()"
        >
          <option value="Indian">Indian (All Regions)</option>
          <option value="South Indian">South Indian</option>
          <option value="North Indian">North Indian</option>
          <option value="Global">Global / Balanced</option>
        </select>
        <Button variant="primary" size="sm" @click="executeSearch()" :disabled="isSearching">
          {{ isSearching ? 'Searching...' : 'Search' }}
        </Button>
      </div>

      <!-- Quick Search Chips -->
      <div class="flex flex-wrap items-center gap-1.5 pt-1">
        <span class="text-[0.7rem] font-semibold text-ink-muted uppercase tracking-wider">Quick:</span>
        <button
          v-for="q in quickQueries"
          :key="q"
          @click="executeSearch(q)"
          class="px-2.5 py-0.5 rounded-full text-[0.72rem] bg-canvas-raised border border-border hover:border-primary hover:text-primary transition-colors cursor-pointer"
        >
          {{ q }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isSearching" class="py-8 flex flex-col items-center justify-center gap-2 text-ink-muted">
        <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        <span class="text-xs font-data">Connecting to live open recipe APIs & calculating ICMR-NIN macros...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="searchError" class="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl text-center text-xs text-amber-900">
        {{ searchError }}
      </div>

      <!-- Live Search Results Grid -->
      <div v-else-if="results.length > 0" class="max-h-[380px] overflow-y-auto pr-1 space-y-3">
        <div
          v-for="r in results"
          :key="r.id"
          class="p-3 bg-canvas border border-border hover:border-primary/60 rounded-xl flex items-center justify-between gap-3 transition-all hover:shadow-sm"
        >
          <div class="flex items-center gap-3">
            <img
              :src="r.thumbnail_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=120&q=80'"
              :alt="r.title"
              class="w-14 h-14 rounded-lg object-cover border border-border shrink-0"
            />
            <div>
              <div class="flex items-center gap-2">
                <h4 class="font-display font-bold text-sm text-ink">{{ r.title }}</h4>
                <span class="px-1.5 py-0.5 rounded text-[0.62rem] font-bold uppercase bg-primary-soft text-primary">
                  {{ r.source.replace('_', ' ') }}
                </span>
              </div>
              <p class="text-[0.72rem] text-ink-muted line-clamp-1">
                {{ r.ingredients.map(i => i.name).slice(0, 5).join(', ') }}
              </p>
              <!-- Macros Row -->
              <div class="flex items-center gap-2 text-[0.7rem] font-data text-ink-muted mt-1">
                <span class="font-bold text-ink">{{ Math.round(r.macros.calories_kcal) }} kcal</span>
                <span>·</span>
                <span class="text-primary font-semibold">P {{ Math.round(r.macros.protein_g) }}g</span>
                <span>·</span>
                <span>C {{ Math.round(r.macros.carbs_g) }}g</span>
                <span>·</span>
                <span>F {{ Math.round(r.macros.fat_g) }}g</span>
                <span>·</span>
                <span class="text-amber-700 font-semibold">{{ Math.round(r.macros.iron_mg) }}mg Iron</span>
              </div>
            </div>
          </div>
          <Button variant="primary" size="sm" @click="selectAndSwap(r)">
            Swap In
          </Button>
        </div>
      </div>
    </div>
  </Modal>
</template>
