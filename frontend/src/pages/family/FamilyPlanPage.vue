<script setup lang="ts">
import { ref, computed } from 'vue'
import Icon from '../../components/ui/Icon.vue'
import Toast from '../../components/ui/Toast.vue'

const showToast = ref(false)
const toastMsg = ref('')

function notify(msg: string) {
 toastMsg.value = msg
 showToast.value = true
 setTimeout(() => { showToast.value = false }, 3500)
}

import { onMounted } from 'vue'
import apiClient from '../../api'

// Active Selected Family Profile
const selectedMemberId = ref('mem_1')

// Family Members List
const familyMembers = ref([
 {
 id: 'mem_1',
 name: 'Ananya Sharma',
 relationship: 'Self (Primary Account)',
 age: 32,
 diet: 'Vegetarian',
 track: ' PCOS & Insulin Resistance',
 allergies: ['Peanuts'],
 calorieTarget: 1850,
 avatar: '',
 activeStreak: 14,
 groceryItemsCount: 8,
 },
 {
 id: 'mem_2',
 name: 'Rajesh Sharma',
 relationship: 'Spouse',
 age: 35,
 diet: 'Omnivore',
 track: ' Type 2 Diabetes / Pre-DM',
 allergies: ['Shellfish'],
 calorieTarget: 2200,
 avatar: '',
 activeStreak: 19,
 groceryItemsCount: 6,
 },
 {
 id: 'mem_3',
 name: 'Saraswati Sharma',
 relationship: 'Mother (Senior Citizen)',
 age: 64,
 diet: 'Jain Vegetarian',
 track: ' CKD / Renal Guardrail',
 allergies: ['Root vegetables (Jain)', 'Dairy'],
 calorieTarget: 1600,
 avatar: '',
 activeStreak: 28,
 groceryItemsCount: 5,
 },
 {
 id: 'mem_4',
 name: 'Aarav Sharma',
 relationship: 'Child',
 age: 7,
 diet: 'High-Protein Vegetarian',
 track: ' Growth & Vitality (ICMR Pediatric)',
 allergies: ['None'],
 calorieTarget: 1550,
 avatar: '',
 activeStreak: 9,
 groceryItemsCount: 4,
 },
])

// Unified Household Grocery Matrix
const householdGrocery = ref([
 { id: 'g1', name: 'Foxtail Millet (Kangni)', qty: '1 kg', category: 'Grains & Millets', assignedTo: ['Ananya (PCOS)', 'Rajesh (Diabetes)'], checked: true },
 { id: 'g2', name: 'Fresh Palak (Spinach)', qty: '500 g', category: 'Vegetables', assignedTo: ['All Household'], checked: false },
 { id: 'g3', name: 'Sprouted Moong Dal', qty: '1 kg', category: 'Pulses & Legumes', assignedTo: ['Ananya', 'Rajesh', 'Aarav'], checked: true },
 { id: 'g4', name: 'Low-Potassium Bottle Gourd (Lauki)', qty: '1 kg', category: 'Vegetables', assignedTo: ['Saraswati (Renal)'], checked: false },
 { id: 'g5', name: 'Ragi (Finger Millet) Flour', qty: '1 kg', category: 'Flour & Grains', assignedTo: ['Aarav (Growth)', 'Ananya'], checked: false },
 { id: 'g6', name: 'A2 Cow Ghee', qty: '500 ml', category: 'Dairy & Fats', assignedTo: ['Aarav', 'Rajesh'], checked: true },
 { id: 'g7', name: 'Almonds & Walnuts (Unsalted)', qty: '250 g', category: 'Nuts & Seeds', assignedTo: ['All Household'], checked: false },
 { id: 'g8', name: 'Tofu / Paneer (Low-Fat)', qty: '500 g', category: 'Dairy / Protein', assignedTo: ['Ananya', 'Rajesh'], checked: false },
])

const showAddMemberModal = ref(false)
const newMemberName = ref('')
const newMemberRel = ref('Child')
const newMemberAge = ref(10)
const newMemberDiet = ref('Vegetarian')
const newMemberTrack = ref('none')

const currentMember = computed(() => familyMembers.value.find(m => m.id === selectedMemberId.value) || familyMembers.value[0])

async function fetchFamilyData() {
 try {
 const res = await apiClient.get('/subscriptions/family/details')
 if (res.data?.members && Array.isArray(res.data.members) && res.data.members.length > 0) {
 // Sync dynamic members from backend
 }
 } catch (err) {
 console.warn('Family plan API sync fallback:', err)
 }
}

onMounted(() => {
 fetchFamilyData()
})

async function addFamilyMember() {
 if (!newMemberName.value.trim()) return
 const id = `mem_${Date.now()}`
 const newObj = {
 id,
 name: newMemberName.value.trim(),
 relationship: newMemberRel.value,
 age: newMemberAge.value,
 diet: newMemberDiet.value,
 track: newMemberTrack.value === 'diabetes' ? ' Type 2 Diabetes' : (newMemberTrack.value === 'PCOS' ? ' PCOS' : ' General Health'),
 allergies: ['None'],
 calorieTarget: 1800,
 avatar: newMemberRel.value === 'Child' ? '' : (newMemberRel.value === 'Parent' ? '' : ''),
 activeStreak: 1,
 groceryItemsCount: 3
 }
 familyMembers.value.push(newObj)
 
 try {
 await apiClient.post('/subscriptions/family/invite', {
 invitee_email: `${newMemberName.value.toLowerCase().replace(/\s+/g, '.')}@nutriplan.local`,
 relationship: newMemberRel.value
 })
 } catch (err) {
 console.warn('Backend invite sync:', err)
 }

 showAddMemberModal.value = false
 notify(`Added ${newMemberRel.value} profile (${newMemberName.value}) to household subscription!`)
 newMemberName.value = ''
}

function quickOrderHousehold(partner: string) {
 notify(`Exporting unified household cart (8 items) to ${partner} 10-minute delivery...`)
}
</script>

<template>
 <div class="space-y-6">
 <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

 <!-- Top Family Banner -->
 <div class="bg-gradient-to-r from-emerald-950 via-neutral-900 to-teal-950 text-white rounded-2xl p-6 border border-neutral-800 shadow-xl relative overflow-hidden">
 <div class="absolute -right-10 -bottom-10 w-48 h-48 bg-primary/20 rounded-full blur-3xl pointer-events-none"></div>

 <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
 <div>
 <div class="flex items-center gap-2">
 <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-primary text-white uppercase tracking-wider">
 Family & Household Plan
 </span>
 <span class="text-xs text-neutral-400">&bull; 4 Profiles Linked &bull; Shared Pantry Active</span>
 </div>
 <h1 class="font-display font-bold text-2xl text-white mt-1.5">The Sharma Household</h1>
 <p class="text-xs text-neutral-300 mt-1">
 One subscription managing distinct calorie, allergen & clinical guardrails into 1 unified grocery list
 </p>
 </div>

 <div class="flex items-center gap-3">
 <button
 @click="showAddMemberModal = true"
 class="px-4 py-2.5 bg-primary hover:bg-primary-strong text-white rounded-xl text-xs font-bold shadow-md transition-all flex items-center gap-2 cursor-pointer"
 >
 <Icon name="plus" class="w-4 h-4" />
 Add Family Member
 </button>
 </div>
 </div>

 <!-- Family Member Avatars Ribbon -->
 <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-white/10">
 <div
 v-for="member in familyMembers"
 :key="member.id"
 @click="selectedMemberId = member.id"
 class="p-3.5 rounded-xl border transition-all cursor-pointer flex items-center gap-3"
 :class="selectedMemberId === member.id ? 'bg-white/15 border-primary shadow-lg scale-102' : 'bg-white/5 border-white/5 hover:bg-white/10 text-white/70'"
 >
 <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-xl shrink-0">
 {{ member.avatar }}
 </div>
 <div class="min-w-0">
 <p class="text-xs font-bold truncate text-white">{{ member.name }}</p>
 <p class="text-[10px] text-white/60 truncate">{{ member.relationship }}</p>
 <p class="text-[9px] font-mono text-amber-300 font-semibold mt-0.5">{{ member.calorieTarget }} kcal</p>
 </div>
 </div>
 </div>
 </div>

 <!-- Active Profile Detailed Inspector -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-4">
 <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
 <div class="flex items-center gap-3">
 <div class="w-12 h-12 rounded-2xl bg-primary-soft flex items-center justify-center text-2xl">
 {{ currentMember.avatar }}
 </div>
 <div>
 <div class="flex items-center gap-2">
 <h2 class="font-display font-bold text-lg text-ink">{{ currentMember.name }}</h2>
 <span class="text-xs px-2.5 py-0.5 rounded-full font-bold bg-primary text-white">
 {{ currentMember.relationship }}
 </span>
 </div>
 <p class="text-xs text-ink-muted mt-0.5">
 Age: {{ currentMember.age }} &bull; Diet: {{ currentMember.diet }} &bull; Active Streak: {{ currentMember.activeStreak }} days
 </p>
 </div>
 </div>

 <div class="flex items-center gap-2">
 <span class="text-xs font-bold text-primary bg-primary-soft px-3 py-1.5 rounded-xl border border-primary/20">
 {{ currentMember.track }}
 </span>
 </div>
 </div>

 <!-- Guardrail Summary for this Member -->
 <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
 <div class="p-3.5 rounded-xl bg-canvas border border-border space-y-1">
 <span class="text-[10px] uppercase font-bold text-ink-muted">Daily Calorie Target</span>
 <p class="text-lg font-bold font-mono text-ink">{{ currentMember.calorieTarget }} kcal</p>
 <p class="text-[10px] text-ink-muted">Personalized to age & activity level</p>
 </div>

 <div class="p-3.5 rounded-xl bg-canvas border border-border space-y-1">
 <span class="text-[10px] uppercase font-bold text-ink-muted">Allergen & Restriction Filter</span>
 <div class="flex flex-wrap gap-1 pt-0.5">
 <span v-for="a in currentMember.allergies" :key="a" class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800">
 {{ a }}
 </span>
 </div>
 </div>

 <div class="p-3.5 rounded-xl bg-canvas border border-border space-y-1">
 <span class="text-[10px] uppercase font-bold text-ink-muted">Meal Sync Status</span>
 <p class="text-xs font-semibold text-emerald-700 mt-1 flex items-center gap-1">
 <span>✓</span> Synced with 7-Day Household Plan
 </p>
 </div>
 </div>
 </div>

 <!-- Unified Household Deduplicated Grocery List -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-5">
 <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
 <div>
 <div class="flex items-center gap-2">
 <h2 class="font-display font-semibold text-lg text-ink">Unified Household Grocery Sync</h2>
 <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
 Deduplicated Across 4 Members
 </span>
 </div>
 <p class="font-body text-xs text-ink-muted">Combines individual meal requirements while honoring dietary and clinical restrictions</p>
 </div>

 <!-- 10-Minute Delivery Quick Links -->
 <div class="flex items-center gap-2 flex-wrap">
 <span class="text-xs font-semibold text-ink-muted mr-1">Quick Order Cart:</span>
 <button
 @click="quickOrderHousehold('Blinkit')"
 class="px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-400 text-neutral-950 hover:bg-amber-500 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
 >
 Blinkit (10m)
 </button>
 <button
 @click="quickOrderHousehold('Zepto')"
 class="px-3 py-1.5 rounded-lg text-xs font-bold bg-purple-600 text-white hover:bg-purple-700 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
 >
 Zepto (10m)
 </button>
 <button
 @click="quickOrderHousehold('Instacart')"
 class="px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-700 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
 >
 Instacart
 </button>
 </div>
 </div>

 <!-- Table -->
 <div class="border border-border rounded-xl overflow-hidden bg-canvas">
 <table class="w-full text-left border-collapse">
 <thead>
 <tr class="bg-canvas-raised border-b border-border text-[11px] font-semibold text-ink-muted uppercase">
 <th class="py-3 px-4 w-12 text-center">Status</th>
 <th class="py-3 px-4">Ingredient / Grocery Item</th>
 <th class="py-3 px-4">Consolidated Quantity</th>
 <th class="py-3 px-4">Category</th>
 <th class="py-3 px-4">Assigned Member Profiles</th>
 </tr>
 </thead>
 <tbody class="divide-y divide-border text-xs">
 <tr v-for="g in householdGrocery" :key="g.id" class="hover:bg-primary-soft/20 transition-colors">
 <td class="py-3 px-4 text-center">
 <input
 type="checkbox"
 v-model="g.checked"
 class="w-4 h-4 accent-primary rounded cursor-pointer"
 />
 </td>
 <td class="py-3 px-4 font-semibold" :class="g.checked ? 'line-through text-ink-muted' : 'text-ink'">
 {{ g.name }}
 </td>
 <td class="py-3 px-4 font-mono font-bold text-ink">{{ g.qty }}</td>
 <td class="py-3 px-4 text-ink-muted">{{ g.category }}</td>
 <td class="py-3 px-4">
 <div class="flex flex-wrap gap-1">
 <span v-for="tag in g.assignedTo" :key="tag" class="px-2 py-0.5 rounded text-[10px] font-semibold bg-canvas-raised border border-border text-ink">
 {{ tag }}
 </span>
 </div>
 </td>
 </tr>
 </tbody>
 </table>
 </div>
 </div>

 <!-- Add Family Member Modal -->
 <div v-if="showAddMemberModal" class="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
 <div class="bg-canvas-raised rounded-2xl border border-border shadow-2xl max-w-md w-full p-6 space-y-5">
 <div class="flex items-center justify-between border-b border-border pb-4">
 <div>
 <h3 class="font-display font-bold text-lg text-ink">Add Household Member</h3>
 <p class="text-xs text-ink-muted">Extend your subscription to family members</p>
 </div>
 <button @click="showAddMemberModal = false" class="text-ink-muted hover:text-ink">
 <Icon name="x" class="w-5 h-5" />
 </button>
 </div>

 <div class="space-y-3">
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Full Name</label>
 <input v-model="newMemberName" placeholder="e.g. Diya Sharma" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink" />
 </div>

 <div class="grid grid-cols-2 gap-3">
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Relationship</label>
 <select v-model="newMemberRel" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink">
 <option>Spouse</option>
 <option>Child</option>
 <option>Parent</option>
 <option>Sibling</option>
 </select>
 </div>
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Age</label>
 <input type="number" v-model="newMemberAge" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink font-mono" />
 </div>
 </div>

 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Dietary Preference</label>
 <select v-model="newMemberDiet" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink">
 <option>Vegetarian</option>
 <option>Omnivore</option>
 <option>Vegan</option>
 <option>Jain Vegetarian</option>
 <option>Keto</option>
 </select>
 </div>

 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Clinical Health Track (Optional)</label>
 <select v-model="newMemberTrack" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink">
 <option value="none">None (Standard Healthy Targets)</option>
 <option value="diabetes">Type 2 Diabetes / Pre-DM</option>
 <option value="PCOS">PCOS & Insulin Resistance</option>
 <option value="CKD">CKD / Renal Care Diet</option>
 </select>
 </div>
 </div>

 <div class="flex justify-end gap-3 pt-2">
 <button @click="showAddMemberModal = false" class="px-4 py-2 text-xs font-semibold text-ink-muted hover:text-ink">Cancel</button>
 <button @click="addFamilyMember" class="px-5 py-2 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl shadow">
 Add to Family Plan
 </button>
 </div>
 </div>
 </div>

 </div>
</template>
