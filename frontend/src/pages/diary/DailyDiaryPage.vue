<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Button from '../../components/ui/Button.vue'
import SectionLabel from '../../components/ui/SectionLabel.vue'
import Icon from '../../components/ui/Icon.vue'
import FoodPhotoModal from '../../components/food/FoodPhotoModal.vue'
import apiClient from '../../api'

const showLogModal = ref(false)
const showPhotoModal = ref(false)
const selectedMeal = ref('breakfast')

const targets = { calories: 2000, protein: 120, fat: 65, carbs: 250 }

const entries = ref<any[]>([])

const fetchDiaryForToday = async () => {
 try {
 const todayStr = new Date().toISOString().split('T')[0]
 const res = await apiClient.get(`/diary/day/${todayStr}`)
 if (res.data && res.data.entries && res.data.entries.length > 0) {
 entries.value = res.data.entries.map((e: any) => ({
 id: e.id,
 meal_type: e.meal_type,
 food_name: e.food_name,
 calories: e.calories,
 protein_g: e.protein_g,
 fat_g: e.fat_g,
 carbs_g: e.carbs_g,
 quantity_g: e.quantity_g
 }))
 }
 } catch (err) {
 // Keep local default state
 }
}

onMounted(() => {
 fetchDiaryForToday()
})

function handlePhotoMealLogged(meal: any) {
 const newEntry = {
 id: String(Date.now()),
 meal_type: meal.meal_type || selectedMeal.value,
 food_name: meal.name,
 calories: meal.calories,
 protein_g: meal.protein_g,
 fat_g: meal.fat_g,
 carbs_g: meal.carbs_g,
 quantity_g: 300,
 }
 entries.value.push(newEntry)
}

const totals = computed(() => entries.value.reduce(
 (acc, e) => ({
 calories: acc.calories + e.calories,
 protein_g: acc.protein_g + e.protein_g,
 fat_g: acc.fat_g + e.fat_g,
 carbs_g: acc.carbs_g + e.carbs_g,
 }),
 { calories: 0, protein_g: 0, fat_g: 0, carbs_g: 0 }
))

const mealGroups = computed(() => {
 const groups: Record<string, typeof entries.value> = {
 breakfast: [], lunch: [], snack: [], dinner: []
 }
 for (const e of entries.value) {
 groups[e.meal_type]?.push(e)
 }
 return groups
})

async function removeEntry(id: string) {
 entries.value = entries.value.filter(e => e.id !== id)
 try {
 await apiClient.delete(`/diary/entries/${id}`)
 } catch (err) {
 // Ignore error in local dev
 }
}

const searchQuery = ref('')
const searchResults = ref<any[]>([
 { food_name: 'Roti (Whole Wheat)', calories: 100, protein_g: 3.0, fat_g: 2.5, carbs_g: 18.0 },
 { food_name: 'Paneer (100g)', calories: 265, protein_g: 18.3, fat_g: 20.8, carbs_g: 1.2 },
 { food_name: 'Dal (Lentil Curry)', calories: 130, protein_g: 9.0, fat_g: 0.5, carbs_g: 22.0 },
 { food_name: 'Cooked Rice (150g)', calories: 195, protein_g: 4.0, fat_g: 0.4, carbs_g: 43.0 },
])

async function handleFoodSearch(query: string) {
 searchQuery.value = query
 if (!query.trim()) return
 try {
 const res = await apiClient.get(`/food-recognition/foods/search?q=${encodeURIComponent(query.trim())}`)
 if (res.data?.results && Array.isArray(res.data.results) && res.data.results.length > 0) {
 searchResults.value = res.data.results.map((i: any) => ({
 food_name: i.name,
 calories: i.calories,
 protein_g: i.protein_g,
 fat_g: i.fat_g,
 carbs_g: i.carbs_g,
 }))
 }
 } catch (err) {
 console.warn('Food search API query fallback:', err)
 }
}

async function logItem(item: any) {
 const newEntry = {
 id: String(Date.now()),
 meal_type: selectedMeal.value,
 food_name: item.food_name,
 calories: item.calories,
 protein_g: item.protein_g,
 fat_g: item.fat_g,
 carbs_g: item.carbs_g,
 quantity_g: 100,
 }
 entries.value.push(newEntry)
 showLogModal.value = false
 searchQuery.value = ''

 try {
 const todayStr = new Date().toISOString().split('T')[0]
 await apiClient.post('/diary/entries', {
 log_date: todayStr,
 meal_type: newEntry.meal_type,
 food_name: newEntry.food_name,
 quantity_g: newEntry.quantity_g,
 calories: newEntry.calories,
 protein_g: newEntry.protein_g,
 fat_g: newEntry.fat_g,
 carbs_g: newEntry.carbs_g,
 source: 'search'
 })
 } catch (err) {
 // Best-effort in dev
 }
}
</script>

<template>
 <div>
 <!-- Header Date Row -->
 <div class="flex items-center justify-between mb-6 flex-wrap gap-3">
 <div>
 <h1 class="font-display font-bold text-[1.8rem] text-ink">Food Diary</h1>
 <p class="text-ink-muted text-[0.88rem] mt-0.5">
 {{ new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' }) }}
 </p>
 </div>
 <div class="flex items-center gap-2">
 <button 
 @click="showPhotoModal = true"
 class="flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary hover:bg-primary/20 rounded-xl text-sm font-semibold border border-primary/20 transition-all"
 >
 <Icon name="camera" class="w-4 h-4" />
 AI Photo Scan
 </button>
 <Button @click="showLogModal = true">+ Manual Log</Button>
 </div>
 </div>

 <!-- Macro Summary Ring -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-5 mb-6 shadow-card">
 <div class="flex items-center justify-between mb-4">
 <div class="flex flex-col gap-1">
 <div class="font-data text-[0.72rem] text-ink-muted uppercase tracking-wider">Calories Remaining</div>
 <div class="font-display font-bold text-[2.4rem] text-ink tabular-nums leading-none">
 {{ Math.max(0, targets.calories - totals.calories).toLocaleString() }}
 </div>
 <div class="flex items-center gap-2 text-[0.78rem] text-ink-muted font-data mt-0.5">
 <span>{{ targets.calories }} goal</span>
 <span class="text-ink-muted/40">–</span>
 <span class="text-ink font-semibold">{{ Math.round(totals.calories) }} eaten</span>
 </div>
 </div>

 <!-- Macro progress mini bars -->
 <div class="flex gap-4">
 <div class="flex flex-col items-center gap-1.5 min-w-[52px]">
 <div class="font-data font-bold text-[1.05rem] text-info tabular-nums">{{ Math.round(totals.protein_g) }}g</div>
 <div class="w-full h-2 bg-border rounded-full overflow-hidden">
 <div class="h-full rounded-full bg-info transition-all" :style="{ width: `${Math.min(100,(totals.protein_g/targets.protein)*100)}%` }" />
 </div>
 <span class="text-[0.65rem] font-data text-ink-muted uppercase tracking-wide">Protein</span>
 </div>
 <div class="flex flex-col items-center gap-1.5 min-w-[52px]">
 <div class="font-data font-bold text-[1.05rem] text-warning tabular-nums">{{ Math.round(totals.fat_g) }}g</div>
 <div class="w-full h-2 bg-border rounded-full overflow-hidden">
 <div class="h-full rounded-full bg-warning transition-all" :style="{ width: `${Math.min(100,(totals.fat_g/targets.fat)*100)}%` }" />
 </div>
 <span class="text-[0.65rem] font-data text-ink-muted uppercase tracking-wide">Fat</span>
 </div>
 <div class="flex flex-col items-center gap-1.5 min-w-[52px]">
 <div class="font-data font-bold text-[1.05rem] text-danger tabular-nums">{{ Math.round(totals.carbs_g) }}g</div>
 <div class="w-full h-2 bg-border rounded-full overflow-hidden">
 <div class="h-full rounded-full bg-danger transition-all" :style="{ width: `${Math.min(100,(totals.carbs_g/targets.carbs)*100)}%` }" />
 </div>
 <span class="text-[0.65rem] font-data text-ink-muted uppercase tracking-wide">Carbs</span>
 </div>
 </div>
 </div>

 <!-- Calorie progress bar -->
 <div class="mt-4 h-2.5 bg-border rounded-full overflow-hidden">
 <div
 class="h-full rounded-full transition-all duration-500"
 :class="totals.calories >= targets.calories ? 'bg-danger' : 'bg-primary'"
 :style="{ width: `${Math.min(100, (totals.calories / targets.calories) * 100)}%` }"
 />
 </div>
 </div>

 <!-- Meals Grouped -->
 <div class="space-y-6">
 <div v-for="(mealEntries, mealType) in mealGroups" :key="mealType">
 <div class="flex items-center justify-between mb-3">
 <SectionLabel>{{ String(mealType) }}</SectionLabel>
 <button
 class="text-[0.8rem] font-semibold text-primary hover:text-primary/80 flex items-center gap-1 transition-colors"
 @click="selectedMeal = String(mealType); showLogModal = true"
 >+ Add</button>
 </div>

 <div v-if="mealEntries.length === 0" class="bg-canvas-raised border border-dashed border-border rounded-xl py-5 px-4 text-ink-muted text-[0.85rem] text-center">
 Nothing logged yet
 </div>

 <div v-else class="bg-canvas-raised border border-border rounded-xl overflow-hidden divide-y divide-border">
 <div
 v-for="entry in mealEntries"
 :key="entry.id"
 class="flex items-center justify-between px-4 py-3.5 group hover:bg-canvas/50 transition-colors"
 >
 <div class="flex-1 min-w-0">
 <div class="font-body text-[0.9rem] font-medium text-ink truncate">{{ entry.food_name }}</div>
 <div class="font-data text-[0.73rem] text-ink-muted mt-0.5">
 {{ entry.quantity_g }}g &middot; {{ Math.round(entry.calories) }} kcal
 </div>
 </div>
 <div class="flex items-center gap-3 ml-3">
 <div class="hidden sm:flex gap-3 font-data text-[0.75rem]">
 <span class="text-info font-semibold">P {{ entry.protein_g }}g</span>
 <span class="text-warning font-semibold">F {{ entry.fat_g }}g</span>
 <span class="text-danger font-semibold">C {{ entry.carbs_g }}g</span>
 </div>
 <button
 class="opacity-0 group-hover:opacity-100 transition-opacity text-ink-muted hover:text-danger w-6 h-6 flex items-center justify-center rounded-md hover:bg-danger/10"
 @click="removeEntry(entry.id)"
 aria-label="Remove entry"
 >&times;</button>
 </div>
 </div>
 </div>

 <!-- Meal subtotal -->
 <div v-if="mealEntries.length > 0" class="flex justify-end mt-1.5 font-data text-[0.75rem] text-ink-muted">
 <span class="font-semibold text-ink">{{ Math.round(mealEntries.reduce((s, e) => s + e.calories, 0)) }}</span>&nbsp;kcal
 </div>
 </div>
 </div>

 <!-- Log Food Modal -->
 <Teleport to="body">
 <Transition name="modal-overlay">
 <div v-if="showLogModal" class="fixed inset-0 z-50 flex items-end md:items-center justify-center p-0 md:p-4">
 <div class="absolute inset-0 bg-ink/40 backdrop-blur-sm" @click="showLogModal = false" />

 <div class="relative z-10 w-full md:max-w-md bg-canvas-raised rounded-t-2xl md:rounded-xl shadow-[0_-8px_40px_rgba(28,38,32,.2)] md:shadow-[0_20px_60px_rgba(28,38,32,.2)]">
 <!-- Handle -->
 <div class="flex justify-center pt-3 mb-1 md:hidden">
 <div class="w-10 h-1 bg-border rounded-full" />
 </div>

 <div class="p-5">
 <div class="flex items-center justify-between mb-4">
 <h2 class="font-display font-semibold text-[1.1rem] text-ink">Log Food</h2>
 <button class="text-ink-muted hover:text-ink text-xl" @click="showLogModal = false">×</button>
 </div>

 <!-- Meal type selector -->
 <div class="flex gap-1 p-1 bg-canvas rounded-lg mb-4">
 <button
 v-for="m in ['breakfast', 'lunch', 'snack', 'dinner']"
 :key="m"
 class="flex-1 py-1.5 text-[0.72rem] font-data font-semibold uppercase tracking-wide rounded-md transition-colors capitalize"
 :class="selectedMeal === m ? 'bg-primary text-white shadow-sm' : 'text-ink-muted hover:text-ink'"
 @click="selectedMeal = m"
 >{{ m }}</button>
 </div>

 <!-- Search input -->
 <div class="relative mb-4">
 <input
 v-model="searchQuery"
 @input="handleFoodSearch(($event.target as HTMLInputElement).value)"
 placeholder="Search food (e.g. Roti, Dal, Paneer, Rice)"
 class="w-full font-body text-[0.88rem] bg-canvas border border-border rounded-lg px-4 py-2.5 outline-none focus:border-primary focus:ring-2 focus:ring-primary/15 text-ink placeholder:text-ink-muted/60"
 />
 </div>

 <!-- Quick add results -->
 <div class="space-y-2 max-h-64 overflow-y-auto">
 <button
 v-for="item in searchResults"
 :key="item.food_name"
 class="w-full text-left flex items-center justify-between px-3 py-2.5 rounded-md bg-canvas hover:bg-primary-soft/50 transition-colors"
 @click="logItem(item)"
 >
 <div>
 <div class="font-body text-[0.88rem] font-medium text-ink">{{ item.food_name }}</div>
 <div class="font-data text-[0.72rem] text-ink-muted mt-0.5">{{ item.calories }} kcal / 100g</div>
 </div>
 <div class="flex gap-2 font-data text-[0.72rem]">
 <span class="text-info">P {{ item.protein_g }}g</span>
 <span class="text-warning">F {{ item.fat_g }}g</span>
 <span class="text-danger">C {{ item.carbs_g }}g</span>
 </div>
 </button>
 </div>
 </div>
 </div>
 </div>
 </Transition>
 </Teleport>

 <!-- AI Food Photo Modal -->
 <FoodPhotoModal 
 :is-open="showPhotoModal" 
 @close="showPhotoModal = false"
 @meal-logged="handlePhotoMealLogged"
 />
 </div>
</template>

<style scoped>
.modal-overlay-enter-active,
.modal-overlay-leave-active {
 transition: opacity 260ms var(--ease-out);
}
.modal-overlay-enter-from,
.modal-overlay-leave-to { opacity: 0; }
</style>
