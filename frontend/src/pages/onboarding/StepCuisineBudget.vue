<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'

const router = useRouter()
const budget = ref('₹3000')

interface RegionalOption {
  id: string
  name: string
  zone: string
  desc: string
  staples: string
}

const regions: RegionalOption[] = [
  {
    id: 'in_south_andhra',
    name: 'South Indian (Andhra / Telangana)',
    zone: 'South',
    desc: 'High-protein pesarattu, ragi mudda, pappu & gunpowder spices',
    staples: 'Ragi, Sona Masoori, Green Gram, Sesame Oil'
  },
  {
    id: 'in_south_tamilnadu',
    name: 'South Indian (Tamil Nadu / Kerala)',
    zone: 'South',
    desc: 'Millet adai, moringa sambhar, sundal & coconut cold-press',
    staples: 'Millets, Chana, Toor Dal, Coconut Oil'
  },
  {
    id: 'in_north_punjab',
    name: 'North Indian (Punjab / UP / Delhi)',
    zone: 'North',
    desc: 'Low-oil paneer bhurji, Jammu rajma, missi roti & saag',
    staples: 'Whole Wheat, Rajma, Artisanal Paneer, Desi Ghee'
  },
  {
    id: 'in_west_maharashtra',
    name: 'West Indian (Maharashtra / Gujarat)',
    zone: 'West',
    desc: 'Sprouted matki usal, jowar bhakri, methi thepla & sattu',
    staples: 'Jowar, Sprouted Moth, Besan, Groundnut Oil'
  },
  {
    id: 'in_east_bengal',
    name: 'East Indian (Bengal / Odisha)',
    zone: 'East',
    desc: 'Light macher jhol (carp), chholar dal, kalo jeere & unpolished rice',
    staples: 'Gobindobhog Rice, Rohu Fish, Mustard Oil'
  },
  {
    id: 'global',
    name: 'Global / Mediterranean Balanced',
    zone: 'Global',
    desc: 'Whole grain sourdough, Greek salads, grilled chicken & olive oil',
    staples: 'Oats, Quinoa, Extra Virgin Olive Oil'
  },
]

import apiClient from '../../api'

const isLoading = ref(false)
const selectedRegion = ref('in_south_andhra')
const cookingOil = ref('cold_pressed')

function selectRegion(id: string) {
  selectedRegion.value = id
  localStorage.setItem('nutriplan_regional_pref', id)
}

async function nextStep() {
  isLoading.value = true
  localStorage.setItem('nutriplan_regional_pref', selectedRegion.value)
  localStorage.setItem('nutriplan_cooking_oil', cookingOil.value)
  try {
    await apiClient.put('/profile/me', {
      regional_preference: selectedRegion.value,
      home_cooking_oil: cookingOil.value
    })
  } catch (err) {
    console.warn('Regional preferences save warning:', err)
  } finally {
    isLoading.value = false
    router.push('/onboarding/pantry')
  }
}

function backStep() {
  router.push('/onboarding/diet')
}
</script>

<template>
  <div class="animate-[step-slide-in_260ms_var(--ease-out)_both]">
    <h2 class="font-display font-semibold text-[1.4rem] text-ink mb-2">Regional Cuisine & Food Heritage</h2>
    <p class="text-ink-muted text-[0.88rem] mb-6">
      NutriPlan grounds your meal plans in authentic regional culinary traditions and ICMR-NIN nutritional tables.
    </p>

    <!-- Regional Food Culture Selector -->
    <div class="mb-8">
      <label class="font-body text-[0.85rem] font-semibold text-ink mb-3 block">
        Select Your Primary Regional Food Style:
      </label>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div
          v-for="r in regions"
          :key="r.id"
          class="p-4 rounded-xl border cursor-pointer transition-all flex flex-col justify-between"
          :class="selectedRegion === r.id ? 'bg-primary-soft/60 border-primary shadow-sm' : 'bg-canvas-raised border-border hover:border-primary/40'"
          @click="selectRegion(r.id)"
        >
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <h3 class="font-display font-bold text-[0.95rem] text-ink">{{ r.name }}</h3>
              <span class="px-2 py-0.5 rounded text-[0.68rem] font-bold uppercase bg-canvas border border-border text-ink-muted">
                {{ r.zone }}
              </span>
            </div>
            <p class="font-body text-[0.8rem] text-ink-muted mb-2 leading-relaxed">{{ r.desc }}</p>
          </div>
          <div class="text-[0.72rem] font-data text-primary font-medium pt-2 border-t border-border/50">
            🌾 {{ r.staples }}
          </div>
        </div>
      </div>
    </div>

    <!-- Home Cooking Oil Baseline -->
    <div class="mb-8">
      <label class="font-body text-[0.85rem] font-semibold text-ink mb-1.5 block">
        Primary Home Cooking Oil (for exact macro calibration):
      </label>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div
          v-for="oil in [
            { id: 'cold_pressed', name: 'Cold-Pressed Groundnut/Sesame' },
            { id: 'mustard_oil', name: 'Raw Mustard Oil' },
            { id: 'desi_ghee', name: 'Pure Desi A2 Ghee' },
            { id: 'olive_oil', name: 'Extra Virgin Olive Oil' },
          ]"
          :key="oil.id"
          class="p-2.5 rounded-lg border text-center text-[0.8rem] font-medium cursor-pointer transition-colors"
          :class="cookingOil === oil.id ? 'bg-primary text-white border-primary' : 'bg-canvas-raised border-border text-ink hover:border-primary/40'"
          @click="cookingOil = oil.id"
        >
          {{ oil.name }}
        </div>
      </div>
    </div>

    <div class="mb-8">
      <Input v-model="budget" label="Weekly Grocery Budget (Optional)" type="text" placeholder="e.g. ₹3000 or $50" />
    </div>

    <div class="flex justify-between mt-8">
      <Button variant="ghost" @click="backStep">Back</Button>
      <Button @click="nextStep" :loading="isLoading">Next: Pantry & Spices</Button>
    </div>
  </div>
</template>
