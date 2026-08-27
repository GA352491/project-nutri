<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../../components/ui/Button.vue'
import GroceryListItem from '../../components/GroceryListItem.vue' // Re-using as a checkbox list
import apiClient from '../../api'

const router = useRouter()
const isLoading = ref(false)
const diet = ref('Omnivore')
const selectedCondition = ref('none')
const allergyList = [
 'Dairy / Lactose',
 'Gluten',
 'Peanuts',
 'Tree Nuts',
 'Soy',
 'Eggs',
 'Shellfish'
]
const selectedAllergies = ref<string[]>([])

function toggleAllergy(item: string, checked: boolean) {
 if (checked) {
 selectedAllergies.value.push(item)
 } else {
 selectedAllergies.value = selectedAllergies.value.filter(a => a !== item)
 }
}

async function nextStep() {
 isLoading.value = true
 try {
 await apiClient.put('/profile/me', {
 dietary_preference: diet.value,
 allergies: selectedAllergies.value,
 ...(selectedCondition.value !== 'none' ? { primary_goal: selectedCondition.value } : {})
 })
 } catch (err) {
 console.warn('Diet preferences save warning:', err)
 } finally {
 isLoading.value = false
 router.push('/onboarding/cuisine')
 }
}
function backStep() {
 router.push('/onboarding')
}
</script>

<template>
 <div class="animate-[step-slide-in_260ms_var(--ease-out)_both]">
 <h2 class="font-display font-semibold text-[1.4rem] text-ink mb-2">Diet & Allergies</h2>
 <p class="text-ink-muted text-[0.88rem] mb-6">We'll filter out recipes and ingredients that don't match your profile.</p>

 <div class="mb-8">
 <label class="font-body text-[0.82rem] font-semibold text-ink mb-2 block">Dietary Preference</label>
 <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
 <div 
 v-for="type in ['Omnivore', 'Vegetarian', 'Vegan', 'Pescatarian', 'Keto', 'Paleo']" 
 :key="type"
 class="font-body text-[0.85rem] border border-border rounded-md py-2 px-3 text-center cursor-pointer transition-colors"
 :class="diet === type ? 'bg-primary text-white border-primary' : 'bg-canvas-raised hover:border-primary/50 text-ink'"
 @click="diet = type"
 >
 {{ type }}
 </div>
 </div>
 </div>

 <div class="mb-8">
 <label class="font-body text-[0.82rem] font-semibold text-ink mb-1 block">Clinical Condition Track (Optional)</label>
 <p class="text-ink-muted text-xs mb-2.5">Applies medical-grade macro caps and ICMR-NIN/USDA micronutrient targets.</p>
 <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
 <div
 v-for="cond in [
 { id: 'none', label: 'None (Healthy Adult)', icon: 'shield-check', desc: 'Standard balanced nutrition targets' },
 { id: 'diabetes', label: 'Type 2 Diabetes / Pre-DM', icon: 'activity', desc: 'Low-GI, carb capped at 45%, sugar <20g' },
 { id: 'PCOS', label: 'PCOS / Insulin Resistance', icon: 'flame', desc: 'Anti-inflammatory, protein 1.2g/kg' },
 { id: 'CKD', label: 'CKD / Renal Diet', icon: 'shield-check', desc: 'Protein 0.6g/kg, sodium <1500mg, low K/P' },
 { id: 'post_partum', label: 'Post-Partum / Lactating', icon: 'users', desc: '+400 kcal, high iron (21mg), folate & B12' }
 ]"
 :key="cond.id"
 class="p-3 border rounded-xl cursor-pointer transition-all flex items-start gap-2.5"
 :class="selectedCondition === cond.id ? 'bg-primary-soft/40 border-primary text-ink shadow-sm' : 'bg-canvas-raised border-border text-ink hover:border-primary/50'"
 @click="selectedCondition = cond.id"
 >
 <div class="w-7 h-7 rounded-lg bg-primary/10 text-primary flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
 {{ cond.id === 'diabetes' ? '' : cond.id === 'PCOS' ? '' : cond.id === 'CKD' ? '' : cond.id === 'post_partum' ? '' : '' }}
 </div>
 <div class="min-w-0">
 <p class="text-xs font-bold leading-tight">{{ cond.label }}</p>
 <p class="text-[11px] text-ink-muted mt-0.5 leading-snug">{{ cond.desc }}</p>
 </div>
 </div>
 </div>
 </div>

 <div class="mb-8">
 <label class="font-body text-[0.82rem] font-semibold text-ink mb-2 block">Allergies & Intolerances</label>
 <div class="bg-canvas-raised border border-border rounded-md px-4 py-2">
 <GroceryListItem 
 v-for="allergy in allergyList" 
 :key="allergy" 
 :name="allergy" 
 :initial-checked="selectedAllergies.includes(allergy)"
 @update:checked="(checked) => toggleAllergy(allergy, checked)"
 class="last:border-b-0"
 />
 </div>
 </div>

 <div class="flex justify-between mt-8">
 <Button variant="ghost" @click="backStep">Back</Button>
 <Button @click="nextStep" :loading="isLoading">Next: Cuisine & Budget</Button>
 </div>
 </div>
</template>
