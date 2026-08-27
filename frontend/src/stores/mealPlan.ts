import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api'

export interface PlanMeal {
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

export interface DayPlan {
  day: string
  themeTitle?: string
  themeDesc?: string
  meals: PlanMeal[]
  micros?: {
    calcium_mg: number
    iron_mg: number
    fiber_g: number
  }
}

export const useMealPlanStore = defineStore('mealPlan', () => {
  const activeDay = ref<'Mon' | 'Tue' | 'Wed' | 'Thu' | 'Fri' | 'Sat' | 'Sun'>('Mon')
  const selectedRegion = ref<string>(localStorage.getItem('nutriplan_regional_pref') || 'palate_tour')
  const isPalateTourActive = ref<boolean>(true)
  const weekTourData = ref<Record<string, any>>({})
  const weekPlanCache = ref<Record<string, PlanMeal[]>>({})
  const activeTheme = ref({ title: 'Andhra & Telangana Heritage', desc: 'High-protein lentils & sun-dried spices' })
  const planMicros = ref({ calcium_mg: 778, iron_mg: 19, fiber_g: 46 })
  const isLoading = ref<boolean>(false)
  const lastFetched = ref<number | null>(null)

  const activeDayMeals = computed(() => {
    return weekPlanCache.value[activeDay.value] || []
  })

  const activeDayTotals = computed(() => {
    return activeDayMeals.value.reduce(
      (acc, m) => ({
        calories: acc.calories + (m.calories || 0),
        protein: acc.protein + (m.protein || 0),
        carbs: acc.carbs + (m.carbs || 0),
        fat: acc.fat + (m.fat || 0),
      }),
      { calories: 0, protein: 0, carbs: 0, fat: 0 }
    )
  })

  async function fetchWeeklyPlan(forceRefresh = false) {
    if (!forceRefresh && lastFetched.value && Date.now() - lastFetched.value < 60000 && Object.keys(weekTourData.value).length > 0) {
      return
    }

    isLoading.value = true
    try {
      const res = await apiClient.get('/plan/palate-tour')
      if (res.data?.success && res.data.schedule) {
        weekTourData.value = res.data.schedule
        const daysMap: Record<string, string> = {
          monday: 'Mon', tuesday: 'Tue', wednesday: 'Wed', thursday: 'Thu',
          friday: 'Fri', saturday: 'Sat', sunday: 'Sun'
        }

        const newCache: Record<string, PlanMeal[]> = {}
        for (const [dayKey, dayData] of Object.entries(res.data.schedule) as [string, any][]) {
          const shortDay = daysMap[dayKey.toLowerCase()] || dayKey
          if (dayData?.meals) {
            newCache[shortDay] = dayData.meals.map((m: any, idx: number) => ({
              id: m.id || `${shortDay}-${idx}-${m.type || 'meal'}`,
              type: m.type ? m.type.charAt(0).toUpperCase() + m.type.slice(1) : 'Meal',
              title: m.title || m.name || 'Nutritious Meal',
              cuisine: m.cuisine || m.region_label || 'Indian Balanced',
              region_id: m.region_id,
              description: m.description || '',
              image: m.image_url || m.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80',
              calories: m.calories || 0,
              protein: m.protein || m.protein_g || 0,
              carbs: m.carbs || m.carbs_g || 0,
              fat: m.fat || m.fat_g || 0,
              fiber: m.fiber_g || 10,
              calcium_mg: m.calcium_mg || 150,
              iron_mg: m.iron_mg || 4,
              isLogged: false
            }))
          }
        }
        weekPlanCache.value = newCache
        lastFetched.value = Date.now()
      }
    } catch (err) {
      console.warn('Palate tour fetch fallback:', err)
    } finally {
      isLoading.value = false
    }
  }

  function setActiveDay(day: 'Mon' | 'Tue' | 'Wed' | 'Thu' | 'Fri' | 'Sat' | 'Sun') {
    activeDay.value = day
  }

  function setRegion(regionId: string) {
    selectedRegion.value = regionId
    localStorage.setItem('nutriplan_regional_pref', regionId)
  }

  function markMealLogged(mealId: string, isLogged = true, diaryEntryId?: string) {
    for (const day of Object.keys(weekPlanCache.value)) {
      const meal = weekPlanCache.value[day].find(m => m.id === mealId)
      if (meal) {
        meal.isLogged = isLogged
        meal.diaryEntryId = diaryEntryId
        break
      }
    }
  }

  function swapMeal(day: string, mealType: string, newMeal: PlanMeal) {
    if (weekPlanCache.value[day]) {
      const idx = weekPlanCache.value[day].findIndex(m => m.type.toLowerCase() === mealType.toLowerCase())
      if (idx !== -1) {
        weekPlanCache.value[day][idx] = { ...newMeal }
      }
    }
  }

  return {
    activeDay,
    selectedRegion,
    isPalateTourActive,
    weekTourData,
    weekPlanCache,
    activeTheme,
    planMicros,
    isLoading,
    activeDayMeals,
    activeDayTotals,
    fetchWeeklyPlan,
    setActiveDay,
    setRegion,
    markMealLogged,
    swapMeal,
  }
})
