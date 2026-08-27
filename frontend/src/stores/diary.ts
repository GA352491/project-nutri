import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api'

export interface DiaryEntry {
  id: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack' | string
  food_name: string
  calories: number
  protein_g: number
  fat_g: number
  carbs_g: number
  quantity_g: number
  logged_at?: string
  photo_url?: string
}

export interface MacroTargets {
  calories: number
  protein: number
  fat: number
  carbs: number
  water_ml?: number
}

export const useDiaryStore = defineStore('diary', () => {
  const currentDate = ref<string>(new Date().toISOString().split('T')[0])
  const entries = ref<DiaryEntry[]>([])
  const targets = ref<MacroTargets>({
    calories: 2000,
    protein: 120,
    fat: 65,
    carbs: 250,
    water_ml: 3000
  })
  const waterConsumedMl = ref<number>(1750)
  const isLoading = ref<boolean>(false)

  const totals = computed(() => {
    return entries.value.reduce(
      (acc, e) => ({
        calories: acc.calories + (Number(e.calories) || 0),
        protein: acc.protein + (Number(e.protein_g) || 0),
        fat: acc.fat + (Number(e.fat_g) || 0),
        carbs: acc.carbs + (Number(e.carbs_g) || 0),
      }),
      { calories: 0, protein: 0, fat: 0, carbs: 0 }
    )
  })

  const remaining = computed(() => ({
    calories: Math.max(0, targets.value.calories - totals.value.calories),
    protein: Math.max(0, targets.value.protein - totals.value.protein),
    fat: Math.max(0, targets.value.fat - totals.value.fat),
    carbs: Math.max(0, targets.value.carbs - totals.value.carbs),
  }))

  const percentCalories = computed(() => {
    return targets.value.calories > 0
      ? Math.min(100, Math.round((totals.value.calories / targets.value.calories) * 100))
      : 0
  })

  async function fetchDiary(dateStr?: string) {
    const targetDate = dateStr || currentDate.value
    currentDate.value = targetDate
    isLoading.value = true

    try {
      const res = await apiClient.get(`/diary/day/${targetDate}`)
      if (res.data?.entries && Array.isArray(res.data.entries)) {
        entries.value = res.data.entries.map((e: any) => ({
          id: String(e.id || Date.now()),
          meal_type: e.meal_type || 'lunch',
          food_name: e.food_name || 'Food Item',
          calories: Number(e.calories) || 0,
          protein_g: Number(e.protein_g) || 0,
          fat_g: Number(e.fat_g) || 0,
          carbs_g: Number(e.carbs_g) || 0,
          quantity_g: Number(e.quantity_g) || 100,
          logged_at: e.logged_at,
          photo_url: e.photo_url
        }))
      }
      if (res.data?.targets) {
        targets.value = { ...targets.value, ...res.data.targets }
      }
    } catch (err) {
      console.warn('Diary fetch fallback to local store state:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function addEntry(entry: Omit<DiaryEntry, 'id'>) {
    const tempId = `temp-${Date.now()}`
    const newEntry: DiaryEntry = { ...entry, id: tempId }
    entries.value.push(newEntry)

    try {
      const res = await apiClient.post('/diary/entry', {
        date: currentDate.value,
        meal_type: entry.meal_type,
        food_name: entry.food_name,
        calories: entry.calories,
        protein_g: entry.protein_g,
        fat_g: entry.fat_g,
        carbs_g: entry.carbs_g,
        quantity_g: entry.quantity_g
      })
      if (res.data?.id) {
        const found = entries.value.find(e => e.id === tempId)
        if (found) found.id = String(res.data.id)
      }
    } catch (err) {
      console.warn('Diary server sync notice, entry kept in reactive state:', err)
    }
    return newEntry
  }

  async function removeEntry(id: string) {
    const idx = entries.value.findIndex(e => e.id === id)
    if (idx !== -1) {
      entries.value.splice(idx, 1)
      try {
        await apiClient.delete(`/diary/entry/${id}`)
      } catch (err) {
        console.warn('Delete server sync error:', err)
      }
    }
  }

  function addWater(amountMl: number) {
    waterConsumedMl.value = Math.max(0, waterConsumedMl.value + amountMl)
  }

  return {
    currentDate,
    entries,
    targets,
    waterConsumedMl,
    isLoading,
    totals,
    remaining,
    percentCalories,
    fetchDiary,
    addEntry,
    removeEntry,
    addWater,
  }
})
