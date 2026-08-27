<script setup lang="ts">
import { ref } from 'vue'
import NutritionFactsBlock from '../../components/NutritionFactsBlock.vue'
import Button from '../../components/ui/Button.vue'
import Chip from '../../components/ui/Chip.vue'
import Toast from '../../components/ui/Toast.vue'
import Modal from '../../components/ui/Modal.vue'
import Icon from '../../components/ui/Icon.vue'
import apiClient from '../../api'

const isLogged = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const diaryEntryId = ref<string | null>(null)
const showSwapModal = ref(false)

const mealAlternatives = [
 {
 id: 'alt_1',
 title: 'Grilled Tofu Buddha Bowl',
 image: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&q=80&w=800',
 prepTime: '20 min',
 calories: 420,
 protein: 24,
 carbs: 42,
 fat: 16,
 fiber: 9,
 tags: ['High Protein', 'Vegan', 'Superfood'],
 ingredients: [
 { name: 'Firm Tofu (pressed & cubed)', amount: '150g', isPantry: false },
 { name: 'Edamame', amount: '1/2 cup', isPantry: true },
 { name: 'Brown Rice', amount: '1/2 cup', isPantry: true },
 { name: 'Avocado', amount: '1/2 sliced', isPantry: false },
 { name: 'Sesame dressing', amount: '1 tbsp', isPantry: true }
 ],
 instructions: [
 'Pan-sear the seasoned tofu cubes until crisp on all sides.',
 'Assemble brown rice, edamame, avocado, and tofu in a wide bowl.',
 'Drizzle with sesame dressing and serve warm.'
 ]
 },
 {
 id: 'alt_2',
 title: 'Mediterranean Chickpea & Spinach Bowl',
 image: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&q=80&w=800',
 prepTime: '15 min',
 calories: 460,
 protein: 20,
 carbs: 48,
 fat: 17,
 fiber: 10,
 tags: ['High Fiber', 'Vegetarian', 'Mediterranean'],
 ingredients: [
 { name: 'Boiled Chickpeas', amount: '1.5 cups', isPantry: true },
 { name: 'Baby Spinach', amount: '2 cups', isPantry: false },
 { name: 'Feta Cheese (crumbled)', amount: '30g', isPantry: false },
 { name: 'Kalamata Olives', amount: '6 pcs', isPantry: true },
 { name: 'Extra Virgin Olive Oil', amount: '1 tbsp', isPantry: true }
 ],
 instructions: [
 'Lightly sauté the spinach in olive oil until just wilted.',
 'Toss warm chickpeas with fresh herbs, garlic, and sea salt.',
 'Combine in a bowl and top with crumbled feta and olives.'
 ]
 },
 {
 id: 'alt_3',
 title: 'Moong Sprouts & Roasted Paneer Chaat',
 image: 'https://images.unsplash.com/photo-1543339308-43e59d6b73a6?auto=format&fit=crop&q=80&w=800',
 prepTime: '10 min',
 calories: 390,
 protein: 23,
 carbs: 35,
 fat: 14,
 fiber: 8,
 tags: ['Quick Prep', 'Low GI', 'Indian Healthy'],
 ingredients: [
 { name: 'Sprouted Moong Beans', amount: '1 cup', isPantry: true },
 { name: 'Paneer (pan-roasted)', amount: '80g', isPantry: false },
 { name: 'Pomegranate Seeds', amount: '1/4 cup', isPantry: false },
 { name: 'Chaat Masala & Lemon', amount: '1 tsp', isPantry: true }
 ],
 instructions: [
 'Steam sprouted moong for 3 minutes until slightly tender.',
 'Toss with roasted paneer cubes, chopped tomatoes, and cilantro.',
 'Season with chaat masala and fresh lemon juice.'
 ]
 }
]

const meal = ref({
 id: '123',
 title: 'Quinoa & Paneer Salad',
 image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&q=80&w=800',
 prepTime: '15 min',
 calories: 450,
 protein: 22,
 carbs: 45,
 fat: 18,
 fiber: 8,
 tags: ['High Protein', 'Vegetarian', 'Quick'],
 ingredients: [
 { name: 'Quinoa (cooked)', amount: '1 cup', isPantry: true },
 { name: 'Paneer (cubed)', amount: '100g', isPantry: false },
 { name: 'Cherry tomatoes', amount: '1/2 cup', isPantry: false },
 { name: 'Cucumber (diced)', amount: '1/2 cup', isPantry: true },
 { name: 'Olive oil', amount: '1 tbsp', isPantry: true },
 { name: 'Lemon juice', amount: '1 tbsp', isPantry: true },
 ],
 instructions: [
 'Rinse and cook the quinoa according to package instructions if not already prepared.',
 'Lightly pan-fry the paneer cubes in half of the olive oil until golden brown.',
 'In a large bowl, combine the cooked quinoa, tomatoes, cucumber, and paneer.',
 'Whisk together the remaining olive oil, lemon juice, salt, and pepper. Pour over the salad and toss well.',
 ]
})

function notify(msg: string) {
 toastMessage.value = msg
 showToast.value = true
 setTimeout(() => {
 showToast.value = false
 }, 3000)
}

function selectAlternative(alt: typeof mealAlternatives[0]) {
 meal.value = {
 id: alt.id,
 title: alt.title,
 image: alt.image,
 prepTime: alt.prepTime,
 calories: alt.calories,
 protein: alt.protein,
 carbs: alt.carbs,
 fat: alt.fat,
 fiber: alt.fiber,
 tags: alt.tags,
 ingredients: alt.ingredients,
 instructions: alt.instructions
 }
 isLogged.value = false
 showSwapModal.value = false
 notify(`Swapped meal to "${alt.title}"! `)
}

async function toggleLogMeal() {
 if (!isLogged.value) {
 isLogged.value = true
 try {
 const todayStr = new Date().toISOString().split('T')[0]
 const res = await apiClient.post('/diary/entries', {
 log_date: todayStr,
 meal_type: 'lunch',
 food_name: meal.value.title,
 quantity_g: 250,
 calories: meal.value.calories,
 protein_g: meal.value.protein,
 fat_g: meal.value.fat,
 carbs_g: meal.value.carbs,
 fiber_g: meal.value.fiber,
 source: 'meal_detail'
 })
 if (res.data && res.data.id) {
 diaryEntryId.value = res.data.id
 }
 notify(`Logged "${meal.value.title}" to your Food Diary! `)
 } catch (err) {
 notify(`Logged "${meal.value.title}"!`)
 }
 } else {
 isLogged.value = false
 try {
 if (diaryEntryId.value) {
 await apiClient.delete(`/diary/entries/${diaryEntryId.value}`)
 }
 notify(`Removed "${meal.value.title}" from your Food Diary.`)
 } catch (err) {
 notify(`Removed "${meal.value.title}".`)
 }
 }
}
</script>

<template>
 <div class="max-w-5xl mx-auto pb-12 relative">
 <Toast v-if="showToast" :message="toastMessage" @close="showToast = false" />

 <!-- Swap Meal Modal -->
 <Modal v-model="showSwapModal" title="Swap Meal with Equal Macros" size="lg">
 <div class="space-y-4">
 <p class="font-body text-[0.88rem] text-ink-muted">
 Choose an alternative meal recipe matching your daily caloric target (~{{ meal.calories }} kcal):
 </p>

 <div class="space-y-3">
 <div
 v-for="alt in mealAlternatives"
 :key="alt.id"
 class="flex items-center gap-4 p-3 bg-canvas border border-border rounded-xl hover:border-primary cursor-pointer transition-all hover:shadow-card group"
 @click="selectAlternative(alt)"
 >
 <div class="w-16 h-16 rounded-lg overflow-hidden bg-primary-soft shrink-0">
 <img :src="alt.image" :alt="alt.title" class="w-full h-full object-cover group-hover:scale-105 transition-transform" />
 </div>

 <div class="flex-1 min-w-0">
 <div class="flex items-center gap-2 mb-1">
 <h4 class="font-display font-semibold text-[0.95rem] text-ink truncate">{{ alt.title }}</h4>
 <Chip variant="neutral" class="text-[0.65rem]">{{ alt.prepTime }}</Chip>
 </div>
 <div class="font-data text-[0.75rem] text-ink-muted">
 {{ alt.calories }} kcal · P {{ alt.protein }}g · C {{ alt.carbs }}g · F {{ alt.fat }}g
 </div>
 </div>

 <Button size="sm" variant="outline" class="shrink-0 group-hover:bg-primary group-hover:text-white group-hover:border-primary transition-colors">
 Select
 </Button>
 </div>
 </div>
 </div>
 </Modal>

 <!-- Hero Image -->
 <div class="h-64 md:h-96 w-full rounded-2xl overflow-hidden mb-8 relative">
 <img :src="meal.image" alt="Meal Image" class="w-full h-full object-cover" />
 <div class="absolute inset-0 bg-gradient-to-t from-ink/60 to-transparent"></div>
 <div class="absolute bottom-0 left-0 p-6 md:p-8 w-full">
 <div class="flex gap-2 mb-3">
 <Chip v-for="t in meal.tags" :key="t" variant="neutral">{{ t }}</Chip>
 </div>
 <h1 class="font-display font-bold text-white text-[2rem] md:text-[3rem] leading-tight">{{ meal.title }}</h1>
 <div class="text-white/80 font-data text-[0.85rem] mt-2 flex items-center gap-4">
 <span class="flex items-center gap-1.5">
 <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
 <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
 </svg>
 {{ meal.prepTime }}
 </span>
 <span>•</span>
 <span class="tabular-nums font-bold">{{ meal.calories }} kcal</span>
 </div>
 </div>
 </div>

 <div class="grid md:grid-cols-3 gap-8 px-4 md:px-0">
 
 <!-- Main Content (Ingredients & Instructions) -->
 <div class="md:col-span-2 space-y-10">
 <!-- Actions -->
 <div class="flex gap-3">
 <Button 
 :variant="isLogged ? 'outline' : 'primary'" 
 class="flex-1 text-[0.9rem] flex items-center justify-center gap-2"
 @click="toggleLogMeal"
 >
 <span v-if="isLogged" class="inline-flex items-center gap-1.5">
 <Icon name="check" :size="15" />
 <span>Logged (Click to Unlog)</span>
 </span>
 <span v-else class="inline-flex items-center gap-1.5">
 <Icon name="plus" :size="15" />
 <span>Log this meal</span>
 </span>
 </Button>
 <Button 
 variant="outline" 
 class="flex-1 text-[0.9rem] flex items-center justify-center gap-1.5"
 @click="showSwapModal = true"
 >
 <Icon name="refresh" :size="15" />
 <span>Swap meal</span>
 </Button>
 </div>

 <section>
 <h2 class="font-display font-semibold text-[1.5rem] text-ink mb-4 border-b border-border pb-2">Ingredients</h2>
 <ul class="divide-y divide-border/50">
 <li v-for="ing in meal.ingredients" :key="ing.name" class="py-3 flex items-center justify-between">
 <span class="font-body text-[1rem] text-ink">{{ ing.name }}</span>
 <div class="flex items-center gap-3">
 <span class="font-data text-[0.9rem] text-ink-muted tabular-nums">{{ ing.amount }}</span>
 <span 
 v-if="ing.isPantry" 
 class="text-[0.6rem] uppercase tracking-wider font-data bg-primary-soft text-primary px-1.5 py-0.5 rounded border border-primary/20"
 title="You have this in your pantry!"
 >
 In Pantry
 </span>
 </div>
 </li>
 </ul>
 </section>

 <section>
 <h2 class="font-display font-semibold text-[1.5rem] text-ink mb-4 border-b border-border pb-2">Instructions</h2>
 <ol class="space-y-4">
 <li v-for="(step, idx) in meal.instructions" :key="idx" class="flex gap-4">
 <div class="shrink-0 w-7 h-7 rounded-full bg-canvas-raised border border-border flex items-center justify-center font-display font-bold text-ink text-[0.9rem]">
 {{ idx + 1 }}
 </div>
 <p class="font-body text-[1rem] text-ink pt-0.5 leading-relaxed">{{ step }}</p>
 </li>
 </ol>
 </section>
 </div>

 <!-- Sidebar (Nutrition Facts) -->
 <div>
 <NutritionFactsBlock 
 title="Nutrition Facts"
 :rows="[
 { label: 'Calories', value: `${meal.calories} kcal`, thick: true },
 { label: 'Protein', value: `${meal.protein}g`, dv: '44% DV' },
 { label: 'Carbohydrates', value: `${meal.carbs}g`, dv: '15% DV' },
 { label: 'Dietary Fiber', value: `${meal.fiber}g`, indent: true, dv: '32% DV' },
 { label: 'Total Fat', value: `${meal.fat}g`, dv: '23% DV' },
 ]"
 class="sticky top-6"
 />
 </div>

 </div>
 </div>
</template>
