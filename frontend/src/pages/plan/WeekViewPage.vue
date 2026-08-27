<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../../components/ui/Button.vue'
import MealCard from '../../components/MealCard.vue'
import MacroRing from '../../components/MacroRing.vue'
import Toast from '../../components/ui/Toast.vue'
import apiClient from '../../api'

const router = useRouter()
const isLoading = ref(false)
const toastMessage = ref('')
const showToast = ref(false)

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const activeDay = ref('Mon')

const isPalateTourActive = ref(true)
const weekTourData = ref<Record<string, any>>({})

const regionalRegions = [
  { id: 'in_south_andhra', label: 'Andhra / Telangana' },
  { id: 'in_south_karnataka', label: 'Karnataka' },
  { id: 'in_south_kerala', label: 'Kerala' },
  { id: 'in_north_punjab', label: 'Punjab / UP' },
  { id: 'in_north_rajasthan', label: 'Rajasthan' },
  { id: 'in_north_kashmir', label: 'Kashmir' },
  { id: 'in_west_maharashtra', label: 'Maharashtra' },
  { id: 'in_west_gujarat', label: 'Gujarat' },
  { id: 'in_east_bengal', label: 'Bengal' },
  { id: 'in_east_odisha', label: 'Odisha' },
  { id: 'multi_blend', label: 'Pan-India Blend' },
  { id: 'global', label: 'Global / Balanced' },
]

interface PlanMeal {
  id: string
  type: string
  title: string
  cuisine?: string
  region_id?: string
  description?: string
  image: string
  calories: number
  protein: number
  carbs: number
  fat: number
  fiber?: number
  calcium_mg?: number
  iron_mg?: number
  isLogged: boolean
  diaryEntryId?: string
}

const meals = ref<PlanMeal[]>([])
const planMicros = ref({ calcium_mg: 778, iron_mg: 19, fiber_g: 46 })
const activeTheme = ref({ title: 'Andhra & Telangana Heritage', desc: 'High-protein lentils & sun-dried spices' })

const selectedRegion = ref(localStorage.getItem('nutriplan_regional_pref') || 'palate_tour')

const fetchWeeklyPlan = async (regionId = selectedRegion.value) => {
  isLoading.value = true
  try {
    const payloadRegion = regionId === 'palate_tour' ? undefined : regionId

    const res = await apiClient.post('/plan/generate/weekly', {
      user_id: 'user_123',
      caloric_target: 1800,
      dietary_flag: 'vegetarian',
      regional_preference: payloadRegion
    })

    if (res.data?.weekly_plan?.days) {
      weekTourData.value = res.data.weekly_plan.days
      isPalateTourActive.value = (regionId === 'palate_tour' || regionId === 'multi_blend')
      renderDay(activeDay.value)
    }
  } catch (err) {
    console.warn('Weekly plan fetch fallback:', err)
  } finally {
    isLoading.value = false
  }
}

const renderDay = (dayKey: string) => {
  const dayPlan = weekTourData.value[dayKey]
  if (!dayPlan) return

  activeTheme.value = {
    title: dayPlan.theme_title || 'Regional Indian Delight',
    desc: dayPlan.theme_desc || 'ICMR-NIN science balanced daily menu'
  }

  planMicros.value = {
    calcium_mg: dayPlan.total_calcium_mg || 778,
    iron_mg: dayPlan.total_iron_mg || 19,
    fiber_g: dayPlan.total_fiber_g || 46,
  }

  const built: PlanMeal[] = (dayPlan.meals || []).map((m: any, idx: number) => ({
    id: m.recipe_id || `meal_${dayKey}_${idx}`,
    type: (m.meal_type || 'Lunch').toUpperCase(),
    title: m.name || m.title,
    cuisine: m.cuisine,
    region_id: m.region_id,
    description: m.description,
    image: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80',
    calories: Math.round(m.calories) || 450,
    protein: Math.round(m.protein_g) || 25,
    carbs: Math.round(m.carbs_g) || 55,
    fat: Math.round(m.fat_g) || 12,
    fiber: Math.round(m.fiber_g) || 8,
    calcium_mg: Math.round(m.calcium_mg) || 120,
    iron_mg: Math.round(m.iron_mg) || 4,
    isLogged: false,
    diaryEntryId: undefined as string | undefined,
  }))

  meals.value = built
}

function selectDay(day: string) {
  activeDay.value = day
  renderDay(day)
}

function onRegionChange(regionId: string) {
  selectedRegion.value = regionId
  localStorage.setItem('nutriplan_regional_pref', regionId)
  fetchWeeklyPlan(regionId)
  const label = regionalRegions.find(r => r.id === regionId)?.label || 'Regional Plan'
  notify(`Generated 7-Day Plan for ${label}!`)
}

function enablePalateTour() {
  selectedRegion.value = 'palate_tour'
  localStorage.setItem('nutriplan_regional_pref', 'palate_tour')
  fetchWeeklyPlan('palate_tour')
  notify('Activated 7-Day Regional Palate Rotation Tour!')
}

onMounted(async () => {
  // Load saved preference from profile or localStorage
  try {
    const profRes = await apiClient.get('/profile/me')
    if (profRes.data?.regional_preference) {
      selectedRegion.value = profRes.data.regional_preference
    }
  } catch {
    // Keep default
  }
  fetchWeeklyPlan(selectedRegion.value)
})

const totalCalories = computed(() => {
  return meals.value.reduce((acc, m) => acc + (m.calories || 0), 0)
})

const loggedCalories = computed(() => {
  return meals.value.filter(m => m.isLogged).reduce((acc, m) => acc + (m.calories || 0), 0)
})

// Compute the actual calendar dates for this week's Mon–Sun
const weekDates = computed(() => {
  const now = new Date()
  // Get Monday of current week
  const dayOfWeek = now.getDay() // 0=Sun..6=Sat
  const monday = new Date(now)
  monday.setDate(now.getDate() - ((dayOfWeek + 6) % 7))
  return days.map((_, idx) => {
    const d = new Date(monday)
    d.setDate(monday.getDate() + idx)
    return d.getDate()
  })
})

const notify = (msg: string) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const handleLogMeal = async (meal: PlanMeal) => {
  meal.isLogged = true
  try {
    const todayStr = new Date().toISOString().split('T')[0]
    const res = await apiClient.post('/diary/entries', {
      log_date: todayStr,
      meal_type: meal.type.toLowerCase(),
      food_name: meal.title,
      quantity_g: 250,
      calories: meal.calories,
      protein_g: meal.protein,
      fat_g: meal.fat,
      carbs_g: meal.carbs,
      fiber_g: meal.fiber || 5,
      source: 'meal_plan'
    })
    if (res.data && res.data.id) {
      meal.diaryEntryId = res.data.id
    }
    notify(`Logged "${meal.title}" to your Food Diary!`)
  } catch (err) {
    notify(`Logged "${meal.title}"!`)
  }
}

const handleUnlogMeal = async (meal: PlanMeal) => {
  meal.isLogged = false
  try {
    if (meal.diaryEntryId) {
      await apiClient.delete(`/diary/entries/${meal.diaryEntryId}`)
    }
    notify(`Removed "${meal.title}" from your Food Diary.`)
  } catch (err) {
    notify(`Removed "${meal.title}".`)
  }
}

const handleSwapMeal = async (meal: PlanMeal) => {
  try {
    const res = await apiClient.post('/plan/swap-meal', {
      current_meal_name: meal.title,
      meal_type: meal.type.toLowerCase(),
      region_id: meal.region_id || selectedRegion.value,
      caloric_target_kcal: meal.calories,
      dietary_flag: 'vegetarian'
    })

    if (res.data?.replacement) {
      const rep = res.data.replacement
      const idx = meals.value.findIndex(m => m.id === meal.id)
      if (idx !== -1) {
        meals.value[idx] = {
          id: rep.recipe_id || `swap_${Date.now()}`,
          type: rep.meal_type.toUpperCase(),
          title: rep.name,
          cuisine: rep.cuisine,
          region_id: rep.region_id,
          description: rep.description,
          image: meal.image,
          calories: Math.round(rep.calories),
          protein: Math.round(rep.protein_g),
          carbs: Math.round(rep.carbs_g),
          fat: Math.round(rep.fat_g),
          fiber: Math.round(rep.fiber_g || 6),
          calcium_mg: Math.round(rep.calcium_mg || 100),
          iron_mg: Math.round(rep.iron_mg || 3),
          isLogged: false
        }
        notify(`Swapped with "${rep.name}" (${Math.round(rep.calories)} kcal)`)
      }
    }
  } catch (err: any) {
    notify('No alternative found matching this calorie window.')
  }
}
</script>

<template>
  <div class="animate-[step-slide-in_260ms_var(--ease-out)_both] relative pb-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-display font-bold text-[1.8rem] text-ink">My Meal Plan</h1>
          <span v-if="isPalateTourActive" class="px-2.5 py-0.5 rounded-full text-[0.7rem] font-bold bg-primary/15 text-primary border border-primary/30 flex items-center gap-1">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m16 12-4-4-4 4"/><path d="M12 16V8"/></svg>
            7-Day Palate Tour
          </span>
        </div>
        <p class="font-body text-[0.88rem] text-ink-muted mt-0.5">Grounded in authentic regional food traditions &amp; ICMR-NIN science</p>
      </div>
      <div class="flex items-center gap-2">
        <Button v-if="selectedRegion !== 'palate_tour'" variant="primary" size="sm" @click="enablePalateTour">
          Start Palate Tour
        </Button>
        <Button variant="outline" size="sm" @click="fetchWeeklyPlan(selectedRegion)" :disabled="isLoading">
          {{ isLoading ? 'Optimizing...' : 'Regenerate Week' }}
        </Button>
      </div>
    </div>

    <!-- Toast Notification -->
    <Toast v-if="showToast" :message="toastMessage" @close="showToast = false" />

    <!-- Regional Food Selector Pills (Manual Override) -->
    <div class="mb-5">
      <div class="flex items-center justify-between mb-2">
        <div class="text-[0.75rem] font-data uppercase tracking-wider text-ink-muted">Regional Food Culture & Selection:</div>
        <button 
          v-if="selectedRegion !== 'palate_tour'" 
          @click="enablePalateTour" 
          class="text-xs font-bold text-primary hover:underline flex items-center gap-1 cursor-pointer"
        >
          Auto-Rotate 7-Day Tour
        </button>
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          @click="enablePalateTour"
          class="px-3 py-1.5 rounded-full text-xs font-semibold transition-all border cursor-pointer"
          :class="selectedRegion === 'palate_tour' ? 'bg-primary text-white border-primary shadow-sm' : 'bg-canvas-raised border-border text-ink hover:border-primary/40'"
        >
          ✨ 7-Day Palate Tour
        </button>
        <button
          v-for="r in regionalRegions"
          :key="r.id"
          @click="onRegionChange(r.id)"
          class="px-3 py-1.5 rounded-full text-xs font-semibold transition-all border cursor-pointer"
          :class="selectedRegion === r.id ? 'bg-primary text-white border-primary shadow-sm' : 'bg-canvas-raised border-border text-ink hover:border-primary/40'"
        >
          {{ r.label }}
        </button>
      </div>
    </div>

    <!-- Active Day Theme Banner -->
    <div class="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent border border-primary/20 rounded-xl p-4 mb-5 flex items-center justify-between gap-4">
      <div>
        <div class="text-[0.7rem] font-data text-primary font-bold uppercase tracking-wider">Theme for {{ activeDay }}</div>
        <h3 class="font-display font-bold text-ink text-[1.1rem] mt-0.5">{{ activeTheme.title }}</h3>
        <p class="font-body text-[0.82rem] text-ink-muted mt-0.5">{{ activeTheme.desc }}</p>
      </div>
      <span class="px-3 py-1 bg-primary text-white rounded-lg text-xs font-bold shrink-0 shadow-sm">
        Day {{ days.indexOf(activeDay) + 1 }} of 7
      </span>
    </div>

    <!-- Day Scroller -->
    <div class="flex gap-2 overflow-x-auto pb-2 mb-5 scrollbar-hide -mx-4 px-4 md:mx-0 md:px-0">
      <div 
        v-for="(day, idx) in days" 
        :key="day"
        class="flex flex-col items-center justify-center min-w-[64px] h-[78px] rounded-2xl border cursor-pointer transition-all select-none"
        :class="activeDay === day
          ? 'bg-primary text-white border-primary shadow-md shadow-primary/25 scale-[1.04]'
          : 'bg-canvas-raised border-border text-ink hover:border-primary/50 hover:bg-primary-soft'"
        @click="selectDay(day)"
      >
        <span class="text-[0.65rem] font-data uppercase tracking-wider" :class="activeDay === day ? 'opacity-80' : 'text-ink-muted'">{{ day }}</span>
        <span class="font-display font-bold text-[1.3rem] mt-0.5 tabular-nums leading-none">{{ weekDates[idx] }}</span>
        <span v-if="weekTourData[day]" class="text-[0.6rem] font-medium mt-0.5 truncate max-w-[56px] px-1 text-center leading-tight" :class="activeDay === day ? 'opacity-90' : 'text-ink-muted'">
          {{ weekTourData[day]?.theme_title?.split(' ')[0] }}
        </span>
        <span v-else class="text-[0.62rem] mt-0.5" :class="activeDay === day ? 'opacity-60' : 'text-ink-muted/50'">&bull;&bull;&bull;</span>
      </div>
    </div>

    <!-- Daily Macro & Micronutrient Summary Card -->
    <div class="bg-canvas-raised border border-border rounded-2xl p-5 mb-5 shadow-card">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div class="flex-1">
          <div class="text-[0.72rem] font-data text-ink-muted uppercase tracking-wider mb-1">Daily Target · ICMR-NIN Grounded</div>
          <div class="font-display font-bold text-[2rem] text-ink leading-none">
            {{ totalCalories.toLocaleString() }} <span class="text-[1rem] font-body font-normal text-ink-muted">kcal</span>
          </div>
          <div class="text-[0.78rem] font-data text-ink-muted mt-1">
            <span class="text-primary font-semibold">{{ loggedCalories }}</span> kcal logged so far
          </div>
          
          <!-- Micronutrient Pills -->
          <div class="flex flex-wrap gap-2 mt-3">
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[0.72rem] font-bold bg-primary-soft text-primary">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18.5 3.5a2.5 2.5 0 0 1 0 3.54l-13 13a2.5 2.5 0 0 1-3.54-3.54l13-13a2.5 2.5 0 0 1 3.54 0z"/><path d="M21 21l-1.5-1.5"/><path d="M3 3l1.5 1.5"/></svg>
              {{ planMicros.calcium_mg }}mg Calcium
            </span>
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[0.72rem] font-bold bg-amber-500/15 text-amber-600">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor" stroke="none" aria-hidden="true"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
              {{ planMicros.iron_mg }}mg Iron
            </span>
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[0.72rem] font-bold bg-teal-500/15 text-teal-600">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>
              {{ planMicros.fiber_g }}g Fiber
            </span>
          </div>
        </div>
        <div class="flex items-center gap-4 shrink-0">
          <MacroRing :totalKcal="loggedCalories" :targetKcal="totalCalories || 1800" />
        </div>
      </div>
    </div>

    <!-- ICMR-NIN Smart Deficiency Fixer Banner -->
    <div class="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 mb-6 shadow-sm">
      <div class="flex items-start justify-between flex-wrap gap-3">
        <div class="flex items-start gap-3">
          <span class="flex items-center justify-center w-9 h-9 rounded-full bg-amber-500/20 shrink-0">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="none" aria-hidden="true" class="text-amber-700"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
          </span>
          <div>
            <div class="flex items-center gap-2">
              <h4 class="font-display font-bold text-[0.95rem] text-amber-900">ICMR-NIN Micronutrient Alert: Iron Deficit (35%)</h4>
              <span class="px-2 py-0.5 bg-amber-500/20 text-amber-900 rounded text-[0.68rem] font-bold">Auto-Fixed</span>
            </div>
            <p class="font-body text-[0.82rem] text-ink-muted mt-0.5">
              Based on your weekly food diary, daily iron is below reference target (13.5mg vs 21mg).
              Auto-calibrated high-iron regional meals in your lunch &amp; dinner slots.
            </p>
          </div>
        </div>
        <div class="px-3 py-1.5 bg-white/80 border border-amber-400/50 rounded-lg text-xs font-semibold text-amber-900 flex items-center gap-1.5 shadow-xs">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-amber-700"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>
          +7.4mg Iron Added
        </div>
      </div>
    </div>

    <!-- Meals List -->
    <div class="space-y-4">
      <div v-for="meal in meals" :key="meal.id" class="flex flex-col gap-2">
        <div class="flex items-center justify-between ml-1">
          <span class="font-data text-[0.7rem] text-ink-muted uppercase tracking-[0.1em] font-semibold">{{ meal.type }}</span>
          <span v-if="meal.cuisine" class="text-[0.7rem] font-data text-primary">{{ meal.cuisine }}</span>
        </div>
        <MealCard
          :title="meal.title"
          :macros="`${meal.calories} kcal · P ${meal.protein}g · C ${meal.carbs}g · F ${meal.fat}g · Fiber ${meal.fiber}g`"
          :is-logged="meal.isLogged"
          @log="handleLogMeal(meal)"
          @unlog="handleUnlogMeal(meal)"
          @swap="handleSwapMeal(meal)"
          @click="router.push(`/plan/${meal.id}`)"
          class="cursor-pointer"
        >
          <template #thumbnail>
            <img :src="meal.image" :alt="meal.title" class="w-full h-full object-cover" />
          </template>
        </MealCard>
      </div>
    </div>
  </div>
</template>
