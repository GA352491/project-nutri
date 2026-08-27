<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Input from '../../components/ui/Input.vue'
import Button from '../../components/ui/Button.vue'
import apiClient from '../../api'

const router = useRouter()
const isLoading = ref(false)
const age = ref('')
const gender = ref('')
const height = ref('')
const weight = ref('')
const activity = ref('')

async function nextStep() {
  isLoading.value = true
  try {
    await apiClient.put('/profile/me', {
      ...(age.value ? { age: parseInt(age.value) } : {}),
      ...(gender.value ? { gender: gender.value } : {}),
      ...(height.value ? { height_cm: parseFloat(height.value) } : {}),
      ...(weight.value ? { weight_kg: parseFloat(weight.value) } : {}),
      ...(activity.value ? { activity_level: activity.value } : {}),
    })
  } catch (err) {
    console.warn('Biometrics save warning:', err)
  } finally {
    isLoading.value = false
    router.push('/onboarding/diet')
  }
}
</script>

<template>
 <div class="animate-[step-slide-in_260ms_var(--ease-out)_both]">
 <h2 class="font-display font-semibold text-[1.4rem] text-ink mb-2">Let's get to know you</h2>
 <p class="text-ink-muted text-[0.88rem] mb-6">These details help us calculate your baseline metabolic rate.</p>

 <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
 <Input v-model="age" label="Age" type="number" placeholder="Years" />
 <div class="flex flex-col gap-1">
 <label class="font-body text-[0.82rem] font-semibold text-ink">Gender</label>
 <select v-model="gender" class="font-body text-[0.88rem] text-ink bg-canvas-raised border border-border rounded-md px-3 py-[10px] w-full outline-none focus:border-primary focus:ring-2 focus:ring-primary/15">
 <option value="" disabled>Select</option>
 <option value="male">Male</option>
 <option value="female">Female</option>
 <option value="other">Other</option>
 </select>
 </div>
 </div>

 <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
 <Input v-model="height" label="Height (cm)" type="number" placeholder="175" />
 <Input v-model="weight" label="Weight (kg)" type="number" placeholder="70" />
 </div>

 <div class="mb-8">
 <label class="font-body text-[0.82rem] font-semibold text-ink mb-2 block">Base Activity Level</label>
 <div class="space-y-2">
 <label v-for="level in ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active']" :key="level" class="flex items-center gap-3 p-3 border border-border rounded-md cursor-pointer hover:bg-primary-soft/50 transition-colors" :class="{'border-primary bg-primary-soft/50': activity === level}">
 <input type="radio" :value="level" v-model="activity" class="accent-primary" />
 <span class="font-body text-[0.88rem]">{{ level }}</span>
 </label>
 </div>
 </div>

 <div class="flex justify-end">
 <Button @click="nextStep" :loading="isLoading">Next: Diet & Allergies</Button>
 </div>
 </div>
</template>
