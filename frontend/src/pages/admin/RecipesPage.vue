<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import apiClient from '../../api'
import Button from '../../components/ui/Button.vue'
import Modal from '../../components/ui/Modal.vue'

interface RecipeItem {
 id: string
 title: string
 cuisine: string
 prep_time_minutes: number
 cook_time_minutes: number
 description?: string
 image_url?: string
 total_macros?: {
 calories_kcal: number
 protein_g: number
 fat_g: number
 carbs_g: number
 fiber_g?: number
 }
 tags: string[]
 instructions?: string[]
}

const recipes = ref<RecipeItem[]>([])
const isLoading = ref(false)
const searchQuery = ref('')
const selectedCuisine = ref('all')

// Modal state
const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref<string | null>(null)
const isSaving = ref(false)

// Form fields
const form = ref({
 title: '',
 description: '',
 cuisine: 'Indian',
 prep_time_minutes: 15,
 cook_time_minutes: 20,
 image_url: '',
 calories_kcal: 350,
 protein_g: 15,
 fat_g: 10,
 carbs_g: 45,
 tagsInput: 'vegetarian, high-protein',
 instructions: ['Prepare ingredients', 'Cook on medium heat', 'Serve warm']
})

const cuisines = ['Indian', 'Mediterranean', 'Mexican', 'Asian', 'Continental', 'Italian', 'Other']

async function fetchRecipes() {
 isLoading.value = true
 try {
 const res = await apiClient.get('/recipes/')
 recipes.value = res.data
 } catch (err) {
 console.error('Failed to fetch recipes', err)
 // Fallback demo data if backend is empty/offline
 if (recipes.value.length === 0) {
 recipes.value = [
 {
 id: 'demo_1',
 title: 'Moong Dal Chilla',
 cuisine: 'Indian',
 prep_time_minutes: 10,
 cook_time_minutes: 15,
 total_macros: { calories_kcal: 320, protein_g: 14, fat_g: 8, carbs_g: 45 },
 tags: ['vegetarian', 'high-protein', 'breakfast']
 },
 {
 id: 'demo_2',
 title: 'Palak Paneer with Brown Rice',
 cuisine: 'Indian',
 prep_time_minutes: 20,
 cook_time_minutes: 25,
 total_macros: { calories_kcal: 450, protein_g: 20, fat_g: 18, carbs_g: 48 },
 tags: ['vegetarian', 'keto-friendly', 'dinner']
 },
 {
 id: 'demo_3',
 title: 'Mediterranean Chickpea Bowl',
 cuisine: 'Mediterranean',
 prep_time_minutes: 15,
 cook_time_minutes: 0,
 total_macros: { calories_kcal: 390, protein_g: 16, fat_g: 12, carbs_g: 52 },
 tags: ['vegan', 'quick', 'lunch']
 }
 ]
 }
 } finally {
 isLoading.value = false
 }
}

onMounted(() => {
 fetchRecipes()
})

const filteredRecipes = computed(() => {
 return recipes.value.filter(r => {
 const matchesSearch = r.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
 r.tags.some(t => t.toLowerCase().includes(searchQuery.value.toLowerCase()))
 const matchesCuisine = selectedCuisine.value === 'all' || r.cuisine.toLowerCase() === selectedCuisine.value.toLowerCase()
 return matchesSearch && matchesCuisine
 })
})

// Pagination
const currentPage = ref(1)
const pageSize = 8

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRecipes.value.length / pageSize)))
const paginatedRecipes = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredRecipes.value.slice(start, start + pageSize)
})

const rangeStart = computed(() => Math.min((currentPage.value - 1) * pageSize + 1, filteredRecipes.value.length))
const rangeEnd = computed(() => Math.min(currentPage.value * pageSize, filteredRecipes.value.length))


function openCreateModal() {
 isEditing.value = false
 editingId.value = null
 form.value = {
 title: '',
 description: '',
 cuisine: 'Indian',
 prep_time_minutes: 15,
 cook_time_minutes: 20,
 image_url: '',
 calories_kcal: 350,
 protein_g: 15,
 fat_g: 10,
 carbs_g: 45,
 tagsInput: 'vegetarian, healthy',
 instructions: ['Step 1: Prep the ingredients', 'Step 2: Cook and serve']
 }
 isModalOpen.value = true
}

async function openEditModal(recipe: RecipeItem) {
 isEditing.value = true
 editingId.value = recipe.id
 
 // Try fetching detailed recipe
 try {
 const res = await apiClient.get(`/recipes/${recipe.id}`)
 const full = res.data
 form.value = {
 title: full.title,
 description: full.description || '',
 cuisine: full.cuisine || 'Indian',
 prep_time_minutes: full.prep_time_minutes || 15,
 cook_time_minutes: full.cook_time_minutes || 15,
 image_url: full.image_url || '',
 calories_kcal: full.total_macros?.calories_kcal || 300,
 protein_g: full.total_macros?.protein_g || 15,
 fat_g: full.total_macros?.fat_g || 10,
 carbs_g: full.total_macros?.carbs_g || 40,
 tagsInput: (full.tags || []).join(', '),
 instructions: full.instructions && full.instructions.length ? [...full.instructions] : ['Serve fresh']
 }
 } catch (err) {
 // Fallback to table item data
 form.value = {
 title: recipe.title,
 description: recipe.description || '',
 cuisine: recipe.cuisine,
 prep_time_minutes: recipe.prep_time_minutes,
 cook_time_minutes: recipe.cook_time_minutes,
 image_url: recipe.image_url || '',
 calories_kcal: recipe.total_macros?.calories_kcal || 300,
 protein_g: recipe.total_macros?.protein_g || 15,
 fat_g: recipe.total_macros?.fat_g || 10,
 carbs_g: recipe.total_macros?.carbs_g || 40,
 tagsInput: recipe.tags.join(', '),
 instructions: recipe.instructions || ['Cook and serve']
 }
 }
 
 isModalOpen.value = true
}

function addInstructionStep() {
 form.value.instructions.push(`Step ${form.value.instructions.length + 1}`)
}

function removeInstructionStep(idx: number) {
 if (form.value.instructions.length > 1) {
 form.value.instructions.splice(idx, 1)
 }
}

async function saveRecipe() {
 if (!form.value.title.trim()) return
 
 isSaving.value = true
 const tags = form.value.tagsInput
 .split(',')
 .map(t => t.trim())
 .filter(t => t.length > 0)

 const payload = {
 title: form.value.title,
 description: form.value.description,
 cuisine: form.value.cuisine,
 prep_time_minutes: Number(form.value.prep_time_minutes),
 cook_time_minutes: Number(form.value.cook_time_minutes),
 image_url: form.value.image_url || undefined,
 instructions: form.value.instructions.filter(s => s.trim().length > 0),
 tags,
 total_macros: {
 calories_kcal: Number(form.value.calories_kcal),
 protein_g: Number(form.value.protein_g),
 fat_g: Number(form.value.fat_g),
 carbs_g: Number(form.value.carbs_g),
 fiber_g: 0
 }
 }

 try {
 if (isEditing.value && editingId.value) {
 await apiClient.put(`/recipes/${editingId.value}`, payload)
 } else {
 await apiClient.post('/recipes/', payload)
 }
 isModalOpen.value = false
 await fetchRecipes()
 } catch (err) {
 console.error('Failed to save recipe', err)
 // Update local state anyway for instant UI preview
 if (isEditing.value && editingId.value) {
 const idx = recipes.value.findIndex(r => r.id === editingId.value)
 if (idx !== -1) {
 recipes.value[idx] = {
 ...recipes.value[idx],
 ...payload,
 id: editingId.value
 }
 }
 } else {
 recipes.value.unshift({
 id: `rec_${Date.now()}`,
 ...payload
 })
 }
 isModalOpen.value = false
 } finally {
 isSaving.value = false
 }
}

async function deleteRecipe(id: string) {
 if (!confirm('Are you sure you want to delete this recipe?')) return
 try {
 await apiClient.delete(`/recipes/${id}`)
 recipes.value = recipes.value.filter(r => r.id !== id)
 } catch (err) {
 console.error('Failed to delete recipe', err)
 recipes.value = recipes.value.filter(r => r.id !== id)
 }
}
</script>

<template>
 <div class="space-y-6">
 <!-- Header Controls -->
 <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
 <div>
 <h2 class="font-display font-semibold text-[1.4rem] text-ink">Recipe Database Management</h2>
 <p class="font-body text-[0.92rem] text-ink-muted">Create, edit, and organize verified clinical & curated recipes.</p>
 </div>
 <Button variant="primary" size="md" @click="openCreateModal">
 <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
 <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
 </svg>
 Add Recipe
 </Button>
 </div>

 <!-- Filters Bar -->
 <div class="flex flex-wrap items-center justify-between gap-4 bg-canvas-raised p-4 rounded-xl border border-border">
 <div class="flex flex-wrap items-center gap-3 flex-1">
 <!-- Search Input -->
 <div class="relative min-w-[240px] flex-1 max-w-md">
 <input 
 v-model="searchQuery"
 type="text" 
 placeholder="Search by title or tag (e.g. keto, chilla)..." 
 class="w-full font-body text-[0.88rem] text-ink bg-canvas border border-border rounded-lg pl-9 pr-4 py-2 outline-none focus:border-primary focus:ring-1 focus:ring-primary"
 />
 <svg class="w-4 h-4 text-ink-muted absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
 <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
 </svg>
 </div>

 <!-- Cuisine Filter -->
 <select 
 v-model="selectedCuisine"
 class="font-body text-[0.88rem] text-ink bg-canvas border border-border rounded-lg px-3 py-2 outline-none focus:border-primary"
 >
 <option value="all">All Cuisines</option>
 <option v-for="c in cuisines" :key="c" :value="c">{{ c }}</option>
 </select>
 </div>

 <div class="font-data text-[0.8rem] text-ink-muted">
 Total: <span class="font-semibold text-ink">{{ filteredRecipes.length }}</span> recipes
 </div>
 </div>

 <!-- Recipe Table -->
 <div class="bg-canvas-raised border border-border rounded-xl overflow-hidden shadow-sm">
 <div class="overflow-x-auto">
 <table class="w-full text-left border-collapse">
 <thead>
 <tr class="bg-canvas border-b border-border">
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Recipe</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Cuisine</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Time</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Macros (per serving)</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Tags</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold text-right">Actions</th>
 </tr>
 </thead>
 <tbody class="divide-y divide-border">
 <tr v-if="filteredRecipes.length === 0">
 <td colspan="6" class="py-12 text-center text-ink-muted font-body text-[0.9rem]">
 No recipes found matching your filters.
 </td>
 </tr>
 <tr 
 v-for="recipe in paginatedRecipes" 
 :key="recipe.id"
 class="hover:bg-canvas/40 transition-colors group"
 >
 <!-- Title & Image -->
 <td class="py-3.5 px-4">
 <div class="flex items-center gap-3">
 <div class="w-10 h-10 rounded-lg bg-primary-soft/40 border border-border flex items-center justify-center overflow-hidden shrink-0">
 <img 
 v-if="recipe.image_url" 
 :src="recipe.image_url" 
 :alt="recipe.title"
 class="w-full h-full object-cover"
 />
 <svg v-else class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
   <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
 </svg>
 </div>
 <div>
 <div class="font-body text-[0.92rem] font-semibold text-ink">{{ recipe.title }}</div>
 <div class="font-data text-[0.75rem] text-ink-muted">ID: {{ recipe.id.slice(0, 8) }}</div>
 </div>
 </div>
 </td>

 <!-- Cuisine -->
 <td class="py-3.5 px-4 font-body text-[0.88rem] text-ink">
 <span class="px-2.5 py-0.5 rounded-full bg-secondary-soft text-ink font-medium text-[0.78rem]">
 {{ recipe.cuisine }}
 </span>
 </td>

 <!-- Time -->
 <td class="py-3.5 px-4 font-data text-[0.82rem] text-ink-muted tabular-nums">
 {{ recipe.prep_time_minutes + recipe.cook_time_minutes }}m total
 <span class="block text-[0.7rem] text-ink-muted/70">Prep: {{ recipe.prep_time_minutes }}m · Cook: {{ recipe.cook_time_minutes }}m</span>
 </td>

 <!-- Macros -->
 <td class="py-3.5 px-4">
 <div v-if="recipe.total_macros" class="font-data text-[0.8rem] space-y-0.5">
 <div class="font-semibold text-ink">{{ recipe.total_macros.calories_kcal }} kcal</div>
 <div class="text-[0.72rem] text-ink-muted flex gap-2">
 <span class="text-info">P: {{ recipe.total_macros.protein_g }}g</span>
 <span class="text-warning">F: {{ recipe.total_macros.fat_g }}g</span>
 <span class="text-danger">C: {{ recipe.total_macros.carbs_g }}g</span>
 </div>
 </div>
 <span v-else class="text-ink-muted font-data text-[0.75rem]">—</span>
 </td>

 <!-- Tags -->
 <td class="py-3.5 px-4">
 <div class="flex flex-wrap gap-1 max-w-xs">
 <span 
 v-for="tag in recipe.tags.slice(0, 3)" 
 :key="tag"
 class="font-data text-[0.68rem] px-2 py-0.5 rounded-md bg-canvas border border-border text-ink-muted"
 >
 {{ tag }}
 </span>
 <span v-if="recipe.tags.length > 3" class="text-[0.68rem] text-ink-muted font-data">
 +{{ recipe.tags.length - 3 }}
 </span>
 </div>
 </td>

 <!-- Actions -->
 <td class="py-3.5 px-4 text-right whitespace-nowrap">
 <button 
 class="font-body text-[0.82rem] text-primary hover:underline font-semibold mr-3 cursor-pointer"
 @click="openEditModal(recipe)"
 >
 Edit
 </button>
 <button 
 class="font-body text-[0.82rem] text-danger hover:underline font-semibold cursor-pointer"
 @click="deleteRecipe(recipe.id)"
 >
 Delete
 </button>
 </td>
 </tr>
 </tbody>
 </table>
 </div>
 </div>

 <!-- Pagination -->
 <div v-if="!isLoading && filteredRecipes.length > pageSize" class="flex items-center justify-between mt-4">
   <p class="font-data text-[0.8rem] text-ink-muted">
     Showing {{ rangeStart }}–{{ rangeEnd }} of {{ filteredRecipes.length }} recipes
   </p>
   <div class="flex items-center gap-2">
     <button
       @click="currentPage--"
       :disabled="currentPage <= 1"
       class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-border bg-canvas text-ink disabled:opacity-40 hover:bg-canvas-raised transition-colors"
     >
       Previous
     </button>
     <span class="font-data text-[0.8rem] text-ink-muted">Page {{ currentPage }} of {{ totalPages }}</span>
     <button
       @click="currentPage++"
       :disabled="currentPage >= totalPages"
       class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-border bg-canvas text-ink disabled:opacity-40 hover:bg-canvas-raised transition-colors"
     >
       Next
     </button>
   </div>
 </div>

 <!-- Create / Edit Recipe Modal -->
 <Modal 
 v-model="isModalOpen" 
 :title="isEditing ? 'Edit Recipe' : 'Add New Recipe'"
 size="lg"
 >
 <form @submit.prevent="saveRecipe" class="space-y-4 max-h-[70vh] overflow-y-auto px-1">
 <!-- Title & Cuisine -->
 <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
 <div class="sm:col-span-2">
 <label class="block font-data text-[0.78rem] text-ink-muted uppercase tracking-wider mb-1">Recipe Title *</label>
 <input 
 v-model="form.title" 
 required
 placeholder="e.g. Masala Oats with Chia" 
 class="w-full font-body text-[0.9rem] bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
 />
 </div>
 <div>
 <label class="block font-data text-[0.78rem] text-ink-muted uppercase tracking-wider mb-1">Cuisine</label>
 <select 
 v-model="form.cuisine" 
 class="w-full font-body text-[0.9rem] bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
 >
 <option v-for="c in cuisines" :key="c" :value="c">{{ c }}</option>
 </select>
 </div>
 </div>

 <!-- Description -->
 <div>
 <label class="block font-data text-[0.78rem] text-ink-muted uppercase tracking-wider mb-1">Description</label>
 <textarea 
 v-model="form.description" 
 rows="2"
 placeholder="Nutrient-dense breakfast rich in soluble fiber..." 
 class="w-full font-body text-[0.88rem] bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
 ></textarea>
 </div>

 <!-- Times & Image URL -->
 <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
 <div>
 <label class="block font-data text-[0.78rem] text-ink-muted uppercase tracking-wider mb-1">Prep Time (min)</label>
 <input 
 v-model.number="form.prep_time_minutes" 
 type="number"
 min="0"
 class="w-full font-body text-[0.9rem] bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
 />
 </div>
 <div>
 <label class="block font-data text-[0.78rem] text-ink-muted uppercase tracking-wider mb-1">Cook Time (min)</label>
 <input 
 v-model.number="form.cook_time_minutes" 
 type="number"
 min="0"
 class="w-full font-body text-[0.9rem] bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
 />
 </div>
 <div>
 <label class="block font-data text-[0.78rem] text-ink-muted uppercase tracking-wider mb-1">Image URL</label>
 <input 
 v-model="form.image_url" 
 placeholder="https://..." 
 class="w-full font-body text-[0.9rem] bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
 />
 </div>
 </div>

 <!-- Target Macros -->
 <div class="p-3.5 bg-canvas rounded-xl border border-border space-y-2">
 <div class="font-data text-[0.75rem] font-semibold text-ink uppercase tracking-wider">Macros per Serving</div>
 <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
 <div>
 <label class="block font-data text-[0.7rem] text-ink-muted">Calories (kcal)</label>
 <input v-model.number="form.calories_kcal" type="number" class="w-full text-[0.85rem] font-data bg-canvas-raised border border-border rounded p-1.5" />
 </div>
 <div>
 <label class="block font-data text-[0.7rem] text-info">Protein (g)</label>
 <input v-model.number="form.protein_g" type="number" class="w-full text-[0.85rem] font-data bg-canvas-raised border border-border rounded p-1.5" />
 </div>
 <div>
 <label class="block font-data text-[0.7rem] text-warning">Fat (g)</label>
 <input v-model.number="form.fat_g" type="number" class="w-full text-[0.85rem] font-data bg-canvas-raised border border-border rounded p-1.5" />
 </div>
 <div>
 <label class="block font-data text-[0.7rem] text-danger">Carbs (g)</label>
 <input v-model.number="form.carbs_g" type="number" class="w-full text-[0.85rem] font-data bg-canvas-raised border border-border rounded p-1.5" />
 </div>
 </div>
 </div>

 <!-- Tags -->
 <div>
 <label class="block font-data text-[0.78rem] text-ink-muted uppercase tracking-wider mb-1">Tags (comma separated)</label>
 <input 
 v-model="form.tagsInput" 
 placeholder="vegetarian, high-protein, quick, breakfast" 
 class="w-full font-body text-[0.9rem] bg-canvas border border-border rounded-lg px-3 py-2 text-ink outline-none focus:border-primary"
 />
 </div>

 <!-- Instructions Steps -->
 <div>
 <div class="flex items-center justify-between mb-2">
 <label class="font-data text-[0.78rem] text-ink-muted uppercase tracking-wider">Instructions Steps</label>
 <button 
 type="button" 
 class="text-[0.78rem] font-semibold text-primary hover:underline cursor-pointer"
 @click="addInstructionStep"
 >
 + Add Step
 </button>
 </div>
 <div class="space-y-2">
 <div 
 v-for="(_step, idx) in form.instructions" 
 :key="idx"
 class="flex items-center gap-2"
 >
 <span class="font-data text-[0.75rem] text-ink-muted w-6 text-right">{{ idx + 1 }}.</span>
 <input 
 v-model="form.instructions[idx]"
 class="flex-1 font-body text-[0.85rem] bg-canvas border border-border rounded-lg px-3 py-1.5 text-ink outline-none focus:border-primary"
 placeholder="Describe preparation step..."
 />
 <button 
 type="button"
 class="text-ink-muted hover:text-danger p-1 text-base leading-none cursor-pointer"
 @click="removeInstructionStep(idx)"
 >
 ×
 </button>
 </div>
 </div>
 </div>
 </form>

 <template #footer>
 <div class="flex justify-end gap-3">
 <Button variant="ghost" @click="isModalOpen = false">Cancel</Button>
 <Button variant="primary" :loading="isSaving" @click="saveRecipe">
 {{ isEditing ? 'Save Changes' : 'Create Recipe' }}
 </Button>
 </div>
 </template>
 </Modal>
 </div>
</template>
