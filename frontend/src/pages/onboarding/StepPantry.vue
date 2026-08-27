<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../../components/ui/Button.vue'
import GroceryListItem from '../../components/GroceryListItem.vue'

const router = useRouter()

const pantryStaples = [
 'Rice',
 'Atta (Whole Wheat Flour)',
 'Olive Oil',
 'Onions',
 'Tomatoes',
 'Garlic',
 'Ginger'
]
const checkedStaples = ref<string[]>([...pantryStaples]) // Assume they have everything by default

function toggleStaple(item: string, checked: boolean) {
 if (checked) {
 checkedStaples.value.push(item)
 } else {
 checkedStaples.value = checkedStaples.value.filter(s => s !== item)
 }
}

async function finishOnboarding() {
  router.push('/onboarding/subscription')
}

function backStep() {
  router.push('/onboarding/cuisine')
}
</script>

<template>
  <div class="animate-[step-slide-in_260ms_var(--ease-out)_both]">
    <h2 class="font-display font-semibold text-[1.4rem] text-ink mb-2">Your Pantry</h2>
    <p class="text-ink-muted text-[0.88rem] mb-6">Uncheck anything you don't currently have. This helps us plan meals with what you already own.</p>

    <div class="mb-8 bg-canvas-raised border border-border rounded-md px-4 py-2">
      <GroceryListItem 
        v-for="staple in pantryStaples" 
        :key="staple" 
        :name="staple" 
        :initial-checked="checkedStaples.includes(staple)"
        @update:checked="(checked) => toggleStaple(staple, checked)"
        class="last:border-b-0"
      />
    </div>

    <div class="flex justify-between mt-8">
      <Button variant="ghost" @click="backStep">Back</Button>
      <Button @click="finishOnboarding">Next: Choose Plan & Payment</Button>
    </div>
  </div>
</template>
