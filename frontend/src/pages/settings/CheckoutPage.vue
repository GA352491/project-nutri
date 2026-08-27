<script setup lang="ts">
import { ref } from 'vue'
import Button from '../../components/ui/Button.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// In a real app, tier would come from query param or route state
const tier = ref('premium')
const tierPrices: Record<string, { name: string; price: string; period: string; features: string[] }> = {
 premium: {
 name: 'Premium',
 price: '₹249',
 period: 'per month',
 features: ['Curated recipe generation', 'AI Nutritionist Chat', 'Grocery list sync', 'Micro-nutrient tracking']
 },
 pro: {
 name: 'Pro',
 price: '₹999',
 period: 'per year',
 features: ['Everything in Premium', 'Wearable device sync', '1-on-1 human nutritionist review', 'Priority support']
 }
}

const selectedTier = ref(tierPrices[tier.value])

const form = ref({
 name: '',
 email: '',
 cardNumber: '',
 expiry: '',
 cvv: ''
})

const isProcessing = ref(false)
const isSuccess = ref(false)
const errors = ref<Record<string, string>>({})

function formatCard(e: Event) {
 const input = e.target as HTMLInputElement
 let val = input.value.replace(/\D/g, '').slice(0, 16)
 form.value.cardNumber = val.replace(/(.{4})/g, '$1 ').trim()
}

function formatExpiry(e: Event) {
 const input = e.target as HTMLInputElement
 let val = input.value.replace(/\D/g, '').slice(0, 4)
 if (val.length > 2) val = val.slice(0, 2) + '/' + val.slice(2)
 form.value.expiry = val
}

function validate() {
 errors.value = {}
 if (!form.value.name.trim()) errors.value.name = 'Name is required'
 if (!form.value.email.trim()) errors.value.email = 'Email is required'
 if (form.value.cardNumber.replace(/\s/g, '').length < 16) errors.value.cardNumber = 'Enter a valid card number'
 if (form.value.expiry.length < 5) errors.value.expiry = 'Enter a valid expiry'
 if (form.value.cvv.length < 3) errors.value.cvv = 'Invalid CVV'
 return Object.keys(errors.value).length === 0
}

function submitPayment() {
 if (!validate()) return
 isProcessing.value = true
 // Sandbox — simulate success after 1.5s
 setTimeout(() => {
 isProcessing.value = false
 isSuccess.value = true
 }, 1500)
}
</script>

<template>
 <div class="max-w-4xl mx-auto py-8 px-4">

 <!-- Success State -->
 <div v-if="isSuccess" class="text-center py-20 bg-canvas-raised border border-border rounded-2xl">
 <div class="w-16 h-16 bg-success/20 text-success rounded-full flex items-center justify-center mx-auto mb-6">
 <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
 <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
 </svg>
 </div>
 <h2 class="font-display font-semibold text-[2rem] text-ink mb-2">Payment Successful!</h2>
 <p class="font-body text-ink-muted text-[1.05rem] max-w-sm mx-auto mb-8">
 Welcome to NutriPlan {{ selectedTier.name }}. Your account has been upgraded. 
 </p>
 <Button variant="primary" @click="router.push('/dashboard')">Go to Dashboard</Button>
 </div>

 <!-- Checkout Form -->
 <div v-else class="grid md:grid-cols-2 gap-10 items-start">

 <!-- Left: Order Summary -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm">
 <h2 class="font-display font-semibold text-[1.3rem] text-ink mb-4">Order Summary</h2>
 <div class="border-b border-border pb-4 mb-4">
 <div class="flex justify-between mb-1">
 <span class="font-body text-ink">NutriPlan {{ selectedTier.name }}</span>
 <span class="font-display font-bold text-ink tabular-nums">{{ selectedTier.price }}</span>
 </div>
 <span class="font-data text-[0.75rem] text-ink-muted">Billed {{ selectedTier.period }}</span>
 </div>
 <ul class="space-y-2 mb-6">
 <li v-for="f in selectedTier.features" :key="f" class="flex items-start gap-2">
 <svg class="w-4 h-4 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
 <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
 </svg>
 <span class="font-body text-[0.85rem] text-ink">{{ f }}</span>
 </li>
 </ul>
 <div class="flex justify-between items-center pt-4 border-t border-border">
 <span class="font-data font-bold uppercase tracking-wider text-[0.75rem] text-ink-muted">Total Today</span>
 <span class="font-display font-bold text-[1.5rem] text-ink tabular-nums">{{ selectedTier.price }}</span>
 </div>
 <p class="font-data text-[0.7rem] text-ink-muted/70 mt-4">
 Sandbox mode: No actual charge will be made. Use any 16-digit card number.
 </p>
 </div>

 <!-- Right: Payment Form -->
 <div>
 <h2 class="font-display font-semibold text-[1.3rem] text-ink mb-6">Payment Details</h2>
 <form class="space-y-4" @submit.prevent="submitPayment">

 <div>
 <label class="block font-data text-[0.75rem] text-ink-muted uppercase tracking-wider mb-1.5">Full Name</label>
 <input 
 v-model="form.name"
 type="text" 
 placeholder="Anish Ganga"
 class="w-full font-body text-[0.95rem] text-ink bg-canvas border rounded-lg px-4 py-2.5 outline-none transition-all"
 :class="errors.name ? 'border-danger focus:ring-danger/20' : 'border-border focus:border-primary focus:ring-1 focus:ring-primary'"
 />
 <p v-if="errors.name" class="text-[0.75rem] text-danger mt-1">{{ errors.name }}</p>
 </div>

 <div>
 <label class="block font-data text-[0.75rem] text-ink-muted uppercase tracking-wider mb-1.5">Email Address</label>
 <input 
 v-model="form.email"
 type="email" 
 placeholder="you@example.com"
 class="w-full font-body text-[0.95rem] text-ink bg-canvas border rounded-lg px-4 py-2.5 outline-none transition-all"
 :class="errors.email ? 'border-danger focus:ring-danger/20' : 'border-border focus:border-primary focus:ring-1 focus:ring-primary'"
 />
 <p v-if="errors.email" class="text-[0.75rem] text-danger mt-1">{{ errors.email }}</p>
 </div>

 <div>
 <label class="block font-data text-[0.75rem] text-ink-muted uppercase tracking-wider mb-1.5">Card Number</label>
 <input 
 :value="form.cardNumber"
 type="text" 
 placeholder="1234 5678 9012 3456"
 maxlength="19"
 class="w-full font-data text-[0.95rem] text-ink bg-canvas border rounded-lg px-4 py-2.5 outline-none tracking-widest transition-all"
 :class="errors.cardNumber ? 'border-danger focus:ring-danger/20' : 'border-border focus:border-primary focus:ring-1 focus:ring-primary'"
 @input="formatCard"
 />
 <p v-if="errors.cardNumber" class="text-[0.75rem] text-danger mt-1">{{ errors.cardNumber }}</p>
 </div>

 <div class="grid grid-cols-2 gap-4">
 <div>
 <label class="block font-data text-[0.75rem] text-ink-muted uppercase tracking-wider mb-1.5">Expiry</label>
 <input 
 :value="form.expiry"
 type="text" 
 placeholder="MM/YY"
 maxlength="5"
 class="w-full font-data text-[0.95rem] text-ink bg-canvas border rounded-lg px-4 py-2.5 outline-none tracking-widest transition-all"
 :class="errors.expiry ? 'border-danger' : 'border-border focus:border-primary focus:ring-1 focus:ring-primary'"
 @input="formatExpiry"
 />
 <p v-if="errors.expiry" class="text-[0.75rem] text-danger mt-1">{{ errors.expiry }}</p>
 </div>
 <div>
 <label class="block font-data text-[0.75rem] text-ink-muted uppercase tracking-wider mb-1.5">CVV</label>
 <input 
 v-model="form.cvv"
 type="password" 
 placeholder="•••"
 maxlength="4"
 class="w-full font-data text-[0.95rem] text-ink bg-canvas border rounded-lg px-4 py-2.5 outline-none tracking-widest transition-all"
 :class="errors.cvv ? 'border-danger' : 'border-border focus:border-primary focus:ring-1 focus:ring-primary'"
 />
 <p v-if="errors.cvv" class="text-[0.75rem] text-danger mt-1">{{ errors.cvv }}</p>
 </div>
 </div>

 <Button type="submit" variant="primary" class="w-full mt-2 py-3" :disabled="isProcessing">
 <span v-if="isProcessing">Processing payment...</span>
 <span v-else>Pay {{ selectedTier.price }} &rarr;</span>
 </Button>

 <div class="flex items-center justify-center gap-2 text-ink-muted mt-3">
 <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
 <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
 </svg>
 <span class="font-data text-[0.75rem]">256-bit SSL secured · Sandbox environment</span>
 </div>

 </form>
 </div>
 </div>

 </div>
</template>
