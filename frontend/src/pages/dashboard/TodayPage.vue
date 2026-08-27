<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import MealCard from '../../components/MealCard.vue'
import ActivityBanner from '../../components/ActivityBanner.vue'
import StreakBanner from '../../components/dashboard/StreakBanner.vue'
import Button from '../../components/ui/Button.vue'
import Chip from '../../components/ui/Chip.vue'
import SectionLabel from '../../components/ui/SectionLabel.vue'
import Icon from '../../components/ui/Icon.vue'
import { useRouter } from 'vue-router'

import apiClient from '../../api'

const router = useRouter()

const showActivity = ref(true)
const userName = ref('')

const today = new Date().toLocaleDateString('en-IN', {
 weekday: 'long', day: 'numeric', month: 'long'
})

const greeting = computed(() => {
 const h = new Date().getHours()
 if (h < 12) return 'Good morning'
 if (h < 17) return 'Good afternoon'
 return 'Good evening'
})

const targets = ref({ calories: 2000, protein: 120, fat: 65, carbs: 250 })
const eaten = ref({ calories: 0, protein: 0, fat: 0, carbs: 0 })
const todayEntries = ref<any[]>([])
const remaining = computed(() => ({
 calories: Math.max(0, targets.value.calories - eaten.value.calories),
 protein: Math.max(0, targets.value.protein - eaten.value.protein),
 fat: Math.max(0, targets.value.fat - eaten.value.fat),
 carbs: Math.max(0, targets.value.carbs - eaten.value.carbs),
}))

interface DashboardMeal {
 title: string
 image: string
 calories: number
 protein: number
 carbs: number
 fat: number
 logged: boolean
 diaryEntryId?: string
}

const upcomingMeals = ref<DashboardMeal[]>([])

async function fetchTodayData() {
 const todayStr = new Date().toISOString().split('T')[0]
 try {
 // 1. Fetch user profile (name + dietary target)
 const profRes = await apiClient.get('/profile/me')
 if (profRes.data?.daily_caloric_target) {
 targets.value.calories = profRes.data.daily_caloric_target
 }
 if (profRes.data?.full_name) {
 userName.value = profRes.data.full_name.split(' ')[0]
 }
 } catch (e) {
 // Keep standard targets
 }

 try {
 // 2. Fetch today's actual food diary sum + entries
 const diaryRes = await apiClient.get(`/diary/day/${todayStr}`)
 if (diaryRes.data) {
 eaten.value.calories = diaryRes.data.total_calories || 0
 eaten.value.protein = diaryRes.data.total_protein_g || 0
 eaten.value.fat = diaryRes.data.total_fat_g || 0
 eaten.value.carbs = diaryRes.data.total_carbs_g || 0
 // Store entries for display
 if (diaryRes.data.entries && Array.isArray(diaryRes.data.entries)) {
 todayEntries.value = diaryRes.data.entries.slice(0, 6)
 }
 }
 } catch (e) {
 console.warn('Today diary fetch fallback:', e)
 }

 try {
 // 3. Fetch meal plan recommendations from plan service
 const planRes = await apiClient.post('/plan/generate', {
 user_id: 'user_123',
 preferences: ['vegetarian'],
 dietary_restrictions: [],
 caloric_target: targets.value.calories,
 macro_split: { protein_pct: 0.25, carb_pct: 0.5, fat_pct: 0.25 },
 use_ai: false
 })
 if (planRes.data?.plan?.meals && Array.isArray(planRes.data.plan.meals)) {
 upcomingMeals.value = planRes.data.plan.meals.slice(0, 3).map((m: any) => ({
 title: m.name || m.title,
 image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80',
 calories: m.calories || 400,
 protein: m.protein_g || m.protein || 20,
 carbs: m.carbs_g || m.carbs || 45,
 fat: m.fat_g || m.fat || 12,
 logged: false
 }))
 } else {
 throw new Error('No meals returned')
 }
 } catch (e) {
 // Fallback default meals
 upcomingMeals.value = [
 {
 title: 'Quinoa & Paneer Salad',
 image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80',
 calories: 450, protein: 22, carbs: 38, fat: 18, logged: false
 },
 {
 title: 'Roasted Makhana & Walnuts',
 image: 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80',
 calories: 120, protein: 3, carbs: 22, fat: 2, logged: false
 },
 ]
 }
}

onMounted(() => {
 fetchTodayData()
})

async function logMeal(meal: DashboardMeal) {
 meal.logged = true
 eaten.value.calories += meal.calories
 eaten.value.protein += meal.protein
 eaten.value.carbs += meal.carbs
 eaten.value.fat += meal.fat

 try {
 const todayStr = new Date().toISOString().split('T')[0]
 const res = await apiClient.post('/diary/entries', {
 log_date: todayStr,
 meal_type: 'lunch',
 food_name: meal.title,
 quantity_g: 200,
 calories: meal.calories,
 protein_g: meal.protein,
 fat_g: meal.fat,
 carbs_g: meal.carbs,
 source: 'today_dashboard'
 })
 if (res.data && res.data.id) {
 meal.diaryEntryId = res.data.id
 }
 } catch (err) {
 // Best effort
 }
}

async function unlogMeal(meal: DashboardMeal) {
 meal.logged = false
 eaten.value.calories = Math.max(0, eaten.value.calories - meal.calories)
 eaten.value.protein = Math.max(0, eaten.value.protein - meal.protein)
 eaten.value.carbs = Math.max(0, eaten.value.carbs - meal.carbs)
 eaten.value.fat = Math.max(0, eaten.value.fat - meal.fat)

 try {
 if (meal.diaryEntryId) {
 await apiClient.delete(`/diary/entries/${meal.diaryEntryId}`)
 }
 } catch (err) {
 // Best effort
 }
}
</script>

<template>
 <div class="space-y-6">

 <!-- Gamification Streak & Badges Widget -->
 <StreakBanner />

 <!-- Activity Banner (wearable nudge) -->
 <ActivityBanner
 v-if="showActivity"
 title="Wearable Activity Synced"
 description="Your Fitbit sync shows 3,200 steps today. Log a 20-min walk to earn 120 kcal."
 @dismiss="showActivity = false"
 />

 <!-- Greeting & Date -->
 <div class="flex items-center justify-between">
 <div>
 <p class="font-data text-[0.75rem] text-ink-muted uppercase tracking-[0.1em]">{{ today }}</p>
 <h1 class="font-display font-bold text-[1.8rem] text-ink mt-0.5">
 {{ greeting }}<span v-if="userName">, {{ userName }}</span> 👋
 </h1>
 </div>
 <Button variant="outline" size="sm" @click="router.push('/diary')">
 + Log Food
 </Button>
 </div>

 <!-- Macro Dashboard Card -->
 <div class="bg-canvas-raised border border-border rounded-xl p-5 shadow-card">
 <div class="flex items-center justify-between mb-5">
 <div>
 <div class="font-data text-[0.72rem] text-ink-muted uppercase tracking-wider mb-1">Calories Remaining</div>
 <div class="font-display font-bold text-[2.4rem] text-ink tabular-nums leading-none">
 {{ remaining.calories.toLocaleString() }}
 </div>
 </div>
 <!-- Pie-style SVG calorie ring -->
 <svg width="72" height="72" class="-rotate-90">
 <circle cx="36" cy="36" r="30" fill="none" stroke="var(--color-border)" stroke-width="7" />
 <circle
 cx="36" cy="36" r="30" fill="none"
 stroke="var(--color-primary)" stroke-width="7" stroke-linecap="round"
 :stroke-dasharray="`${(eaten.calories / targets.calories) * 188.5} 188.5`"
 class="transition-all duration-700 ease-out"
 />
 </svg>
 </div>

 <!-- Macro rows -->
 <div class="grid grid-cols-3 gap-4 pt-4 border-t border-border">
 <div v-for="(m, idx) in [
 { label: 'Protein', eaten: eaten.protein, remaining: remaining.protein, unit: 'g', color: 'bg-info' },
 { label: 'Carbs', eaten: eaten.carbs, remaining: remaining.carbs, unit: 'g', color: 'bg-danger' },
 { label: 'Fat', eaten: eaten.fat, remaining: remaining.fat, unit: 'g', color: 'bg-warning' },
 ]" :key="idx" class="flex flex-col gap-1">
 <div class="flex justify-between items-baseline">
 <span class="font-data text-[0.7rem] text-ink-muted uppercase tracking-wide">{{ m.label }}</span>
 <span class="font-data text-[0.8rem] font-semibold text-ink tabular-nums">{{ m.remaining }}g</span>
 </div>
 <div class="h-1.5 bg-border rounded-full overflow-hidden">
 <div
 class="h-full rounded-full transition-all duration-500"
 :class="m.color"
 :style="{ width: `${Math.min(100, (m.eaten / (m.eaten + m.remaining)) * 100)}%` }"
 />
 </div>
 <div class="font-data text-[0.68rem] text-ink-muted">{{ m.eaten }}g eaten</div>
 </div>
 </div>
 </div>

 <!-- Today's Logged Meals -->
 <div>
 <SectionLabel>Logged Today</SectionLabel>
 <div class="bg-canvas-raised border border-border rounded-xl overflow-hidden mb-2">
 <!-- Live diary entries -->
 <div
 v-if="todayEntries.length > 0"
 class="divide-y divide-border"
 >
 <div
 v-for="(entry, i) in todayEntries"
 :key="i"
 class="flex items-center justify-between px-4 py-3"
 >
 <span class="font-body text-[0.88rem] text-ink">{{ entry.food_name }}</span>
 <div class="flex items-center gap-3">
 <Chip variant="neutral" class="capitalize">{{ entry.meal_type }}</Chip>
 <span class="font-data text-[0.82rem] font-semibold text-ink-muted tabular-nums">{{ Math.round(entry.calories) }} kcal</span>
 </div>
 </div>
 </div>
 <!-- Empty state -->
 <div v-else class="py-8 text-center text-ink-muted">
 <div class="text-2xl mb-2">🍽️</div>
 <p class="font-body text-[0.85rem]">Nothing logged yet today.</p>
 <p class="font-data text-[0.75rem] text-ink-muted/70 mt-0.5">Start by logging your breakfast!</p>
 </div>
 </div>
 <button class="text-primary text-[0.82rem] font-semibold hover:underline" @click="router.push('/diary')">
 View full diary →
 </button>
 </div>

 <!-- Upcoming Meals -->
 <div>
 <SectionLabel>Coming Up</SectionLabel>
 <div class="space-y-3">
 <MealCard
 v-for="(meal, i) in upcomingMeals"
 :key="i"
 :title="meal.title"
 :macros="`${meal.calories} kcal · P ${meal.protein}g · C ${meal.carbs}g · F ${meal.fat}g`"
 :is-logged="meal.logged"
 @log="logMeal(meal)"
 @unlog="unlogMeal(meal)"
 >
 <template #thumbnail>
 <img :src="meal.image" :alt="meal.title" class="w-full h-full object-cover" />
 </template>
 </MealCard>
 </div>
 </div>

  <!-- Quick Nav Cards -->
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
    <button
      class="bg-canvas-raised border border-border rounded-2xl p-4 text-left hover:border-primary/50 hover:shadow-card transition-all flex flex-col gap-3 group cursor-pointer"
      @click="router.push('/plan')"
    >
      <div class="w-10 h-10 rounded-xl bg-primary-soft text-primary flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
        <Icon name="plan" :size="18" />
      </div>
      <div>
        <div class="font-display font-semibold text-[0.88rem] text-ink group-hover:text-primary transition-colors leading-snug">Weekly Plan</div>
        <div class="font-body text-[0.72rem] text-ink-muted mt-0.5">7-day regional meals</div>
      </div>
    </button>
    <button
      class="bg-canvas-raised border border-border rounded-2xl p-4 text-left hover:border-emerald-500/50 hover:shadow-card transition-all flex flex-col gap-3 group cursor-pointer"
      @click="router.push('/grocery')"
    >
      <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
        <Icon name="grocery" :size="18" />
      </div>
      <div>
        <div class="font-display font-semibold text-[0.88rem] text-ink group-hover:text-emerald-700 transition-colors leading-snug">Grocery List</div>
        <div class="font-body text-[0.72rem] text-ink-muted mt-0.5">1-click delivery</div>
      </div>
    </button>
    <button
      class="bg-canvas-raised border border-border rounded-2xl p-4 text-left hover:border-amber-500/50 hover:shadow-card transition-all flex flex-col gap-3 group cursor-pointer"
      @click="router.push('/diary')"
    >
      <div class="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
        <Icon name="diary" :size="18" />
      </div>
      <div>
        <div class="font-display font-semibold text-[0.88rem] text-ink group-hover:text-amber-700 transition-colors leading-snug">Food Diary</div>
        <div class="font-body text-[0.72rem] text-ink-muted mt-0.5">Log today's meals</div>
      </div>
    </button>
    <button
      class="bg-canvas-raised border border-border rounded-2xl p-4 text-left hover:border-violet-500/50 hover:shadow-card transition-all flex flex-col gap-3 group cursor-pointer"
      @click="router.push('/booking')"
    >
      <div class="w-10 h-10 rounded-xl bg-violet-500/10 text-violet-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
        <Icon name="consultation" :size="18" />
      </div>
      <div>
        <div class="font-display font-semibold text-[0.88rem] text-ink group-hover:text-violet-700 transition-colors leading-snug">Book Expert</div>
        <div class="font-body text-[0.72rem] text-ink-muted mt-0.5">Consult a nutritionist</div>
      </div>
    </button>
  </div>

 </div>
</template>
