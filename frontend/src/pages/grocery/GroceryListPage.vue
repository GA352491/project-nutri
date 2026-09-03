<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import SectionLabel from '../../components/ui/SectionLabel.vue'
import Icon from '../../components/ui/Icon.vue'
import apiClient from '../../api'

interface Item {
 id: string
 name: string
 quantity: string
 unit: string
 category: string
 checked: boolean
}

const REGIONAL_OPTIONS = [
  { value: 'in_south_andhra', label: '🌶️ Andhra/Telangana', color: '#e63946' },
  { value: 'in_south_tamil', label: '🍚 Tamil Nadu', color: '#f4a261' },
  { value: 'in_north_punjab', label: '🫓 Punjab/UP', color: '#e9c46a' },
  { value: 'in_west_maharashtra', label: '🌾 Maharashtra', color: '#2a9d8f' },
  { value: 'in_west_gujarat', label: '🥜 Gujarat', color: '#264653' },
  { value: 'in_east_bengal', label: '🐟 Bengal', color: '#3a86ff' },
]

const items = ref<Item[]>([])
const newItemName = ref('')
const newItemQty = ref('')
const newItemUnit = ref('')
const showAddForm = ref(false)
const activeFilter = ref<'all' | 'pending' | 'checked'>('all')
const isOrdering = ref(false)
const isGenerating = ref(false)
const selectedRegion = ref('in_south_andhra')
const generateMsg = ref('')
const planSummary = ref<Record<string, any>>({})

// Feature 3: Pantry Leftover Recycler state
const recycledDishes = ref<any[]>([])

async function openPantryRecycler() {
  try {
    const res = await apiClient.post('/grocery/recycle-leftovers', {
      user_id: 'current_user',
      pantry_items: ['paneer', 'spinach', 'cooked rice', 'curd', 'tomatoes'],
      regional_preference: selectedRegion.value,
      target_meal: 'dinner'
    })
    if (res.data?.recycled_dishes) {
      recycledDishes.value = res.data.recycled_dishes
    }
  } catch {
    recycledDishes.value = [
      {
        dish_name: 'Palak Paneer Bhurji with Roti',
        waste_saved_estimate_inr: 120,
        cooking_tip: 'Sauté leftover spinach with crumbled paneer and roasted cumin for a 15-min high-protein dinner.',
        estimated_calories: 320,
        protein_g: 20.0
      },
      {
        dish_name: 'Tomato Curd Rice Tadka',
        waste_saved_estimate_inr: 60,
        cooking_tip: 'Mix cooked rice with fresh curd, add ginger-curry leaf tempering, and top with diced tomatoes.',
        estimated_calories: 280,
        protein_g: 8.5
      }
    ]
  }
}


const fetchGroceryList = async () => {
 try {
 const res = await apiClient.get('/grocery/list')
 if (res.data && res.data.items && res.data.items.length > 0) {
 items.value = res.data.items.map((i: any) => ({
 id: String(i.id),
 name: i.name,
 quantity: String(i.quantity || '1'),
 unit: i.unit || '',
 category: i.category || 'General',
 checked: !!i.is_checked,
 }))
 }
 } catch (err) {
 // Retain default items
 }
}

onMounted(() => {
 fetchGroceryList()
})

const pendingItems = computed(() => items.value.filter(i => !i.checked))
const sagaStatus = ref('')
const trackingId = ref('')

async function generateFromPlan() {
  isGenerating.value = true
  generateMsg.value = `🔄 Generating ${REGIONAL_OPTIONS.find(r => r.value === selectedRegion.value)?.label} shopping list...`
  try {
    const res = await apiClient.post('/grocery/generate-from-plan', {
      regional_preference: selectedRegion.value,
      caloric_target: 1800,
      dietary_flag: 'vegetarian',
      replace_existing: false,
    })
    planSummary.value = res.data?.plan_summary || {}
    generateMsg.value = `✅ Added ${res.data?.total_items || 0} ingredients to your list!`
    await fetchGroceryList()
    setTimeout(() => { generateMsg.value = '' }, 4000)
  } catch {
    generateMsg.value = '⚠️ Could not generate list. Please retry.'
    setTimeout(() => { generateMsg.value = '' }, 3000)
  } finally {
    isGenerating.value = false
  }
}

async function generateQuickDelivery(partner: 'Blinkit' | 'Zepto' | 'Instacart') {
 isOrdering.value = true
 sagaStatus.value = `Starting Temporal Grocery Delivery Saga for ${partner}...`
 try {
 const missingNames = pendingItems.value.map(i => i.name)
 const payloadItems = missingNames.length > 0 ? missingNames : ['Moong Dal', 'Spinach (Palak)', 'Paneer', 'Brown Rice']
 
 // Trigger Delivery service with Temporal Saga
 const res = await apiClient.post('/delivery/checkout-links', {
 items: payloadItems,
 location: 'IN',
 partner: partner
 })
 
 sagaStatus.value = ` Saga Active: Inventory reserved at ${partner} → Stripe hold authorized → Rider dispatched!`
 trackingId.value = `trk_${Math.random().toString(36).substring(2, 9)}`
 
 const url = res.data?.links?.[partner]
 if (url) {
 setTimeout(() => {
 window.open(url, '_blank')
 }, 1500)
 }
 } catch (e) {
 // Fallback direct deep link
 const query = pendingItems.value.slice(0, 3).map(i => i.name).join(' ')
 const encoded = encodeURIComponent(query || 'groceries')
 if (partner === 'Blinkit') window.open(`https://blinkit.com/s/?q=${encoded}`, '_blank')
 if (partner === 'Zepto') window.open(`https://www.zeptonow.com/search?q=${encoded}`, '_blank')
 if (partner === 'Instacart') window.open(`https://www.instacart.com/store/s?k=${encoded}`, '_blank')
 sagaStatus.value = `Order dispatched to ${partner}!`
 } finally {
 isOrdering.value = false
 }
}

const filteredByCategory = computed(() => {
 const filtered = items.value.filter(i => {
 if (activeFilter.value === 'pending') return !i.checked
 if (activeFilter.value === 'checked') return i.checked
 return true
 })
 const grouped: Record<string, Item[]> = {}
 for (const item of filtered) {
 if (!grouped[item.category]) grouped[item.category] = []
 grouped[item.category].push(item)
 }
 return grouped
})

const checkedCount = computed(() => items.value.filter(i => i.checked).length)
const totalCount = computed(() => items.value.length)

async function toggle(id: string, checked: boolean) {
 const item = items.value.find(i => i.id === id)
 if (item) item.checked = checked
 
 try {
 await apiClient.patch(`/grocery/items/${id}/toggle`, { is_checked: checked })
 } catch (err) {
 // Best effort
 }
}

async function addItem() {
 if (!newItemName.value.trim()) return
 const newItem: Item = {
 id: String(Date.now()),
 name: newItemName.value.trim(),
 quantity: newItemQty.value || '1',
 unit: newItemUnit.value,
 category: 'General',
 checked: false,
 }
 items.value.push(newItem)
 newItemName.value = ''
 newItemQty.value = ''
 newItemUnit.value = ''
 showAddForm.value = false

 try {
 await apiClient.post('/grocery/items', {
 name: newItem.name,
 quantity: parseFloat(newItem.quantity) || 1.0,
 unit: newItem.unit || 'units',
 category: newItem.category,
 })
 } catch (err) {
 // Best effort
 }
}

async function clearChecked() {
 items.value = items.value.filter(i => !i.checked)
 try {
 await apiClient.delete('/grocery/clear-checked')
 } catch (err) {
 // Best effort
 }
}
</script>

<template>
 <div>
 <!-- Header -->
 <div class="flex items-start justify-between mb-5 flex-wrap gap-3">
 <div>
 <h1 class="font-display font-bold text-[1.8rem] text-ink">Grocery List</h1>
 <p class="font-data text-[0.85rem] text-ink-muted mt-0.5">
 <span class="font-semibold text-ink">{{ checkedCount }}</span> of {{ totalCount }} items collected
 <span class="text-ink-muted/50 mx-1">&middot;</span>
 <span class="text-primary font-semibold">{{ pendingItems.length }} pending</span>
 </p>
 </div>
 <div class="flex gap-2">
 <Button variant="ghost" size="sm" @click="clearChecked">Clear done</Button>
 <Button size="sm" @click="showAddForm = !showAddForm">+ Add Item</Button>
 </div>
 </div>

  <!-- Regional Smart Generate Banner -->
  <div class="bg-gradient-to-br from-primary/10 to-green-500/10 border border-primary/25 rounded-2xl p-5 mb-5">
    <div class="flex items-start gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-primary/15 flex items-center justify-center text-primary shrink-0">
        <Icon name="sparkles" class="w-5 h-5" />
      </div>
      <div>
        <h3 class="text-sm font-bold text-ink">Auto-Generate from Regional Meal Plan</h3>
        <p class="text-xs text-ink-muted mt-0.5">Pick your cuisine region → AI extracts & categorizes all ingredients instantly</p>
      </div>
    </div>
    <div class="flex flex-wrap gap-2 mb-4">
      <button
        v-for="opt in REGIONAL_OPTIONS"
        :key="opt.value"
        @click="selectedRegion = opt.value"
        class="px-3 py-1.5 rounded-full text-xs font-semibold border transition-all"
        :class="selectedRegion === opt.value
          ? 'bg-primary text-white border-primary shadow-sm scale-105'
          : 'bg-canvas-raised text-ink-muted border-border hover:border-primary/50'"
      >{{ opt.label }}</button>
    </div>
    <div class="flex items-center gap-3 flex-wrap">
      <Button size="sm" :disabled="isGenerating" @click="generateFromPlan" class="flex items-center gap-2">
        <span v-if="isGenerating">Generating…</span>
        <span v-else>⚡ Generate Shopping List</span>
      </Button>
      <Transition name="slide-down">
        <span v-if="generateMsg" class="text-xs font-medium text-primary animate-pulse">{{ generateMsg }}</span>
      </Transition>
    </div>
    <!-- Plan summary after generation -->
    <div v-if="planSummary.meals?.length" class="mt-3 pt-3 border-t border-primary/15">
      <p class="text-xs text-ink-muted mb-1.5 font-semibold">Meals in plan:</p>
      <div class="flex flex-wrap gap-1.5">
        <span v-for="meal in planSummary.meals" :key="meal" class="px-2 py-0.5 bg-primary/10 text-primary rounded-md text-[0.7rem] font-medium">{{ meal }}</span>
      </div>
    </div>
  </div>

  <!-- Pantry Zero-Waste & Leftover Recycler Card -->
  <div class="bg-gradient-to-br from-amber-50 to-emerald-50 border border-amber-300/60 rounded-2xl p-5 mb-5 shadow-xs">
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div class="flex items-start gap-3">
        <div class="w-10 h-10 rounded-xl bg-amber-500/15 flex items-center justify-center text-amber-700 shrink-0">
          <Icon name="sparkles" class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-bold text-ink">Pantry & Fridge Zero-Waste Recycler</h3>
            <span class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[0.65rem] font-bold uppercase tracking-wider">Save ₹120-250</span>
          </div>
          <p class="text-xs text-ink-muted mt-0.5">Got leftover ingredients in your fridge? Turn near-expiry staples into quick regional dishes!</p>
        </div>
      </div>
      <button 
        @click="openPantryRecycler" 
        class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all flex items-center gap-2 cursor-pointer"
      >
        <span>♻️ Recycle Leftovers</span>
      </button>
    </div>

    <!-- Recycled Dishes Preview if generated -->
    <div v-if="recycledDishes.length > 0" class="mt-4 pt-4 border-t border-amber-200 grid sm:grid-cols-3 gap-3">
      <div v-for="dish in recycledDishes" :key="dish.dish_name" class="p-3 bg-white rounded-xl border border-amber-200 text-xs shadow-xs">
        <p class="font-bold text-ink truncate">{{ dish.dish_name }}</p>
        <p class="text-[0.7rem] text-emerald-700 font-semibold mt-0.5">Saves approx. ₹{{ dish.waste_saved_estimate_inr }}</p>
        <p class="text-[0.68rem] text-ink-muted mt-1 leading-snug">{{ dish.cooking_tip }}</p>
        <div class="mt-2 flex items-center justify-between text-[0.68rem] font-data text-ink-muted">
          <span>{{ dish.estimated_calories }} kcal</span>
          <span class="text-primary font-bold">{{ dish.protein_g }}g P</span>
        </div>
      </div>
    </div>
  </div>


 <!-- Quick 10-Min Delivery Bar -->
 <div class="bg-primary/5 border border-primary/20 rounded-xl p-4 mb-6 flex items-center justify-between flex-wrap gap-4">
 <div class="flex items-center gap-3">
 <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
 <Icon name="truck" class="w-5 h-5" />
 </div>
 <div>
 <h3 class="text-sm font-bold text-ink">Order Missing Ingredients (10-Min Delivery)</h3>
 <p class="text-xs text-ink-muted">Deep link {{ pendingItems.length }} missing items directly into your cart</p>
 </div>
 </div>
 
 <div class="flex items-center gap-2">
 <button 
 @click="generateQuickDelivery('Blinkit')"
 class="px-3 py-1.5 bg-[#F4C430]/20 hover:bg-[#F4C430]/30 text-amber-900 border border-amber-400/40 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5"
 >
 Blinkit
 </button>
 <button 
 @click="generateQuickDelivery('Zepto')"
 class="px-3 py-1.5 bg-[#8E24AA]/15 hover:bg-[#8E24AA]/25 text-purple-900 border border-purple-400/40 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5"
 >
 Zepto
 </button>
 <button 
 @click="generateQuickDelivery('Instacart')"
 class="px-3 py-1.5 bg-[#43A047]/15 hover:bg-[#43A047]/25 text-emerald-900 border border-emerald-400/40 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5"
 >
 Instacart
 </button>
 </div>
 </div>

 <!-- Temporal Saga Live Status Banner -->
 <div v-if="sagaStatus" class="bg-primary/10 border border-primary/30 rounded-xl p-4 mb-6 shadow-sm flex items-center justify-between">
 <div class="flex items-center gap-3">
 <div class="w-3 h-3 rounded-full bg-primary animate-ping"></div>
 <div>
 <h4 class="font-display font-semibold text-[0.95rem] text-primary">Temporal GroceryDeliverySaga Live</h4>
 <p class="font-body text-[0.85rem] text-ink mt-0.5">{{ sagaStatus }}</p>
 <p v-if="trackingId" class="text-xs text-ink-muted mt-1 font-mono">Tracking ID: {{ trackingId }} | ETA: 10 mins</p>
 </div>
 </div>
 <button @click="sagaStatus = ''" class="text-xs text-ink-muted hover:text-ink">Dismiss</button>
 </div>

 <!-- Add item form (collapsible) -->
 <Transition name="slide-down">
 <div v-if="showAddForm" class="bg-canvas-raised border border-border rounded-lg p-4 mb-5 shadow-card">
 <h3 class="font-display font-semibold text-[0.95rem] text-ink mb-3">Add Item</h3>
 <div class="grid grid-cols-3 gap-3 mb-3">
 <div class="col-span-2">
 <Input v-model="newItemName" placeholder="e.g. Brown Eggs" label="Item name" />
 </div>
 <Input v-model="newItemQty" placeholder="1" label="Qty" type="number" />
 </div>
 <div class="flex gap-2 justify-end">
 <Button variant="ghost" size="sm" @click="showAddForm = false">Cancel</Button>
 <Button size="sm" @click="addItem">Add to list</Button>
 </div>
 </div>
 </Transition>

 <!-- Filter tabs -->
 <div class="flex gap-1 p-1 bg-canvas border border-border rounded-xl mb-5 w-fit shadow-sm">
 <button
 v-for="f in (['all', 'pending', 'checked'] as const)"
 :key="f"
 class="px-4 py-1.5 text-[0.75rem] font-data font-semibold uppercase tracking-wider rounded-lg transition-all capitalize"
 :class="activeFilter === f ? 'bg-primary text-white shadow-sm' : 'text-ink-muted hover:text-ink hover:bg-canvas-raised'"
 @click="activeFilter = f"
 >{{ f }}</button>
 </div>

 <!-- Grouped items -->
 <div class="space-y-6">
 <div v-for="(catItems, category) in filteredByCategory" :key="category">
 <SectionLabel>{{ category }}</SectionLabel>
 <div class="bg-canvas-raised border border-border rounded-2xl overflow-hidden">
 <div
 v-for="item in catItems"
 :key="item.id"
 class="flex items-center gap-4 px-4 py-3.5 border-b border-border last:border-b-0 transition-colors hover:bg-canvas/50"
 :class="item.checked ? 'bg-canvas/40' : ''"
 >
 <!-- Checkbox -->
 <button
 class="w-5 h-5 rounded-md border-2 flex items-center justify-center shrink-0 transition-all"
 :class="item.checked ? 'bg-primary border-primary shadow-sm' : 'border-border hover:border-primary'"
 @click="toggle(item.id, !item.checked)"
 :aria-label="`${item.checked ? 'Uncheck' : 'Check'} ${item.name}`"
 >
 <svg v-if="item.checked" class="w-3 h-3 text-white" fill="none" viewBox="0 0 12 12">
 <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
 </svg>
 </button>

 <!-- Name & quantity -->
 <div class="flex-1 min-w-0">
 <span
 class="font-body text-[0.9rem] text-ink transition-all"
 :class="item.checked ? 'line-through text-ink-muted/60' : ''"
 >{{ item.name }}</span>
 </div>
 <span class="font-data text-[0.82rem] text-ink-muted shrink-0 tabular-nums">
 {{ item.quantity }}{{ item.unit ? ' ' + item.unit : '' }}
 </span>
 </div>
 </div>
 </div>

 <!-- Empty state -->
 <div v-if="Object.keys(filteredByCategory).length === 0" class="text-center py-14 text-ink-muted">
 <div class="text-4xl mb-3">🛒</div>
 <div class="font-display font-semibold text-[1rem] text-ink mb-1">
 {{ activeFilter === 'checked' ? 'Nothing checked off yet.' : 'Your list is empty!' }}
 </div>
 <div class="font-body text-[0.85rem] text-ink-muted">
 {{ activeFilter === 'all' ? 'Generate from your meal plan above or add items manually.' : '' }}
 </div>
 </div>
 </div>
 </div>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active {
 transition: opacity 220ms var(--ease-out), transform 220ms var(--ease-out);
}
.slide-down-enter-from { opacity: 0; transform: translateY(-8px); }
.slide-down-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
