<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { loadStripe, type Stripe, type StripeElements, type StripePaymentElement } from '@stripe/stripe-js'
import Button from '../../components/ui/Button.vue'
import SlotPicker from '../../components/SlotPicker.vue'
import apiClient from '../../api'

// Stripe setup — using Stripe's public test key by default
const STRIPE_PUBLISHABLE_KEY = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'pk_test_TYooMQauvdEDq54NiTphI7jx'
let stripeInstance: Stripe | null = null
let elements: StripeElements | null = null
let paymentElement: StripePaymentElement | null = null

// UI state
const bookingResult = ref<any>(null)
const nutritionists = ref<any[]>([])
const isLoadingNutris = ref(true)
const selectedNutri = ref<any>(null)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const availableSlots = ref(['09:00 AM', '10:30 AM', '02:00 PM', '04:15 PM'])
const selectedSlot = ref('')

// Checkout state
const checkoutStep = ref<'select' | 'payment' | 'success'>('select')
const isLoadingPayment = ref(false)
const isConfirming = ref(false)
const clientSecret = ref('')
const errorMsg = ref('')
const paymentElementMounted = ref(false)

onMounted(async () => {
 try {
 const res = await apiClient.get('/marketplace/nutritionists/search')
 if (res.data && Array.isArray(res.data) && res.data.length > 0) {
 nutritionists.value = res.data.map((n: any) => ({
 id: n.id,
 name: n.name,
 spec: (n.specialties || []).join(', '),
 rating: n.rating || 4.9,
 avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(n.name)}&background=random`,
 rate: n.hourly_rate_usd || 50,
 stripeAccountId: n.stripe_account_id,
 available_slots: n.available_slots || ['10:00 AM', '02:00 PM', '05:00 PM'],
 }))
 } else {
 nutritionists.value = []
 }
 } catch (e) {
 console.error('Failed to load nutritionists from marketplace API:', e)
 nutritionists.value = []
 } finally {
 if (nutritionists.value.length > 0) {
 selectedNutri.value = nutritionists.value[0]
 availableSlots.value = selectedNutri.value.available_slots || ['10:00 AM', '02:00 PM']
 selectedSlot.value = availableSlots.value[0] || ''
 }
 isLoadingNutris.value = false
 }

 // Pre-load Stripe.js
 try {
 stripeInstance = await loadStripe(STRIPE_PUBLISHABLE_KEY)
 } catch {
 // Stripe fallback
 }
})

function handleSlotSelect(slot: string) {
 selectedSlot.value = slot
}

async function proceedToPayment() {
 if (!selectedSlot.value || !selectedNutri.value) return
 isLoadingPayment.value = true
 errorMsg.value = ''

 try {
 // Request PaymentIntent client_secret from backend
 const res = await apiClient.post('/payment/stripe/checkout/booking', {
 appointment_id: `appt_${Date.now()}`,
 amount_usd: selectedNutri.value.rate || 100.0,
 nutritionist_account_id: selectedNutri.value.stripeAccountId || 'acct_test_placeholder',
 metadata: {
 nutritionist_name: selectedNutri.value.name,
 date: selectedDate.value,
 slot: selectedSlot.value,
 }
 })
 clientSecret.value = res.data.client_secret
 checkoutStep.value = 'payment'

 // Mount Stripe Elements on next tick
 await mountStripeElements()
 } catch (err: any) {
 errorMsg.value = err?.response?.data?.detail || 'Could not initialize payment. Please try again.'
 } finally {
 isLoadingPayment.value = false
 }
}

async function mountStripeElements() {
 if (!stripeInstance || !clientSecret.value) return

 // Small delay to ensure the DOM node is rendered
 await new Promise(r => setTimeout(r, 100))

 const mountTarget = document.getElementById('stripe-payment-element')
 if (!mountTarget) return

 elements = stripeInstance.elements({
 clientSecret: clientSecret.value,
 appearance: {
 theme: 'flat',
 variables: {
 colorPrimary: '#4F8A5B',
 colorBackground: '#ffffff',
 colorText: '#1a2e24',
 colorDanger: '#e74c3c',
 fontFamily: 'Inter, system-ui, sans-serif',
 borderRadius: '10px',
 },
 },
 })

 paymentElement = elements.create('payment')
 paymentElement.mount('#stripe-payment-element')
 paymentElementMounted.value = true
}

async function confirmPayment() {
 if (!stripeInstance || !elements) return
 isConfirming.value = true
 errorMsg.value = ''

 const { error } = await stripeInstance.confirmPayment({
 elements,
 confirmParams: {
 return_url: `${window.location.origin}/appointments/book?success=1`,
 },
 redirect: 'if_required',
 })

 if (error) {
 errorMsg.value = error.message || 'Payment failed. Please try again.'
 isConfirming.value = false
 } else {
 // Payment confirmed — now trigger Temporal BookingWorkflow
 try {
 const bookRes = await apiClient.post('/appointments/book', {
 nutritionist_id: selectedNutri.value?.id,
 nutritionist_name: selectedNutri.value?.name,
 user_id: 'user_' + (Date.now() % 100000), // replaced by auth store user_id in production
 date: selectedDate.value,
 time: selectedSlot.value,
 amount_usd: selectedNutri.value?.rate || 100.0,
 })
 bookingResult.value = bookRes.data
 } catch (e) {
 // Booking workflow trigger is best-effort — payment already succeeded
 console.warn('[Booking] Temporal workflow trigger failed (non-critical):', e)
 }
 checkoutStep.value = 'success'
 isConfirming.value = false
 }
}

// Check for Stripe redirect success
onMounted(() => {
 const params = new URLSearchParams(window.location.search)
 if (params.get('success') === '1') {
 checkoutStep.value = 'success'
 }
})
</script>

<template>
 <div class="max-w-4xl mx-auto py-6">
 <div class="mb-8">
 <h1 class="font-display font-bold text-[1.8rem] text-ink">Book an Appointment</h1>
 <p class="font-body text-ink-muted text-[0.9rem] mt-0.5">Schedule a 1-on-1 video session with a certified nutritionist.</p>
 </div>

 <div v-if="errorMsg" class="bg-danger/10 text-danger text-sm p-3 rounded-lg mb-4 border border-danger/20">
 {{ errorMsg }}
 </div>

 <div v-if="isLoadingNutris" class="text-ink-muted font-body">Loading experts...</div>

 <!-- Step 1: Select Expert & Time -->
 <div v-else-if="checkoutStep === 'select'" class="grid md:grid-cols-2 gap-8">

 <!-- Select Nutritionist -->
 <div class="space-y-3">
 <h2 class="font-display font-semibold text-[1.1rem] text-ink flex items-center gap-2">
 <span class="w-6 h-6 rounded-full bg-primary text-white text-[0.72rem] font-bold flex items-center justify-center">1</span>
 Select Expert
 </h2>
 <div
 v-for="n in nutritionists"
 :key="n.id"
 class="flex items-center gap-4 p-4 border rounded-2xl cursor-pointer transition-all"
 :class="selectedNutri?.id === n.id ? 'border-primary bg-primary/5 ring-1 ring-primary shadow-md' : 'border-border bg-canvas-raised hover:border-primary/50 hover:shadow-card'"
 @click="selectedNutri = n; selectedSlot = ''"
 >
 <img :src="n.avatar" class="w-12 h-12 rounded-full object-cover border-2 border-border" />
 <div class="flex-1 min-w-0">
 <h3 class="font-display font-semibold text-ink text-[0.95rem]">{{ n.name }}</h3>
 <p class="font-body text-[0.78rem] text-ink-muted truncate">{{ n.spec }}</p>
 </div>
 <div class="flex flex-col items-end gap-1 font-data shrink-0">
 <div class="flex items-center gap-1 text-[0.82rem] font-bold text-warning">
 <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
 <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
 </svg>
 {{ n.rating }}
 </div>
 <span class="text-ink-muted text-[0.73rem]">${{ n.rate }}/hr</span>
 </div>
 </div>
 </div>

 <!-- Select Time & Confirm -->
 <div class="space-y-6" v-if="selectedNutri">
 <div>
 <h2 class="font-display font-semibold text-[1.1rem] text-ink mb-4 flex items-center gap-2">
 <span class="w-6 h-6 rounded-full bg-primary text-white text-[0.72rem] font-bold flex items-center justify-center">2</span>
 Select Time
 </h2>
 <input
 type="date"
 v-model="selectedDate"
 class="w-full font-body text-[0.95rem] text-ink bg-canvas border border-border rounded-xl px-4 py-2.5 outline-none focus:border-primary focus:ring-2 focus:ring-primary/15 mb-4"
 />
 <SlotPicker
 :slots="selectedNutri.available_slots || availableSlots"
 :selected="selectedSlot"
 @select="handleSlotSelect"
 />
 </div>

 <!-- Booking Summary -->
 <div class="bg-canvas-raised border border-border p-5 rounded-2xl shadow-card">
 <h3 class="font-data text-[0.72rem] uppercase tracking-wider text-ink-muted mb-4 font-semibold">Booking Summary</h3>
 <div class="space-y-2.5 mb-5">
 <div class="flex justify-between items-center">
 <span class="font-body text-[0.9rem] text-ink-muted">Expert</span>
 <span class="font-body text-[0.9rem] font-semibold text-ink">{{ selectedNutri.name }}</span>
 </div>
 <div class="flex justify-between items-center">
 <span class="font-body text-[0.9rem] text-ink-muted">Date & Time</span>
 <span class="font-body text-[0.9rem] font-semibold text-ink">
 {{ selectedDate }} {{ selectedSlot ? `at ${selectedSlot}` : '—' }}
 </span>
 </div>
 <div class="flex justify-between items-center border-t border-border pt-3 mt-1">
 <span class="font-body text-[0.92rem] font-bold text-ink">Total</span>
 <span class="font-data font-bold text-[1.1rem] text-primary">${{ selectedNutri.rate }}</span>
 </div>
 </div>
 <Button
 class="w-full"
 variant="primary"
 :disabled="!selectedSlot || isLoadingPayment"
 @click="proceedToPayment"
 >
 <span v-if="isLoadingPayment">Preparing checkout...</span>
 <span v-else>Proceed to Payment →</span>
 </Button>
 </div>
 </div>
 </div>

 <!-- Step 2: Stripe Payment Element -->
 <div v-else-if="checkoutStep === 'payment'" class="grid md:grid-cols-5 gap-8">

 <!-- Order Summary (sidebar) -->
 <div class="md:col-span-2 space-y-4">
 <h2 class="font-display font-semibold text-[1.2rem] text-ink">Order Summary</h2>
 <div class="bg-canvas-raised border border-border rounded-xl p-5 shadow-sm space-y-3">
 <div class="flex items-center gap-3">
 <img :src="selectedNutri?.avatar" class="w-10 h-10 rounded-full border border-border" />
 <div>
 <p class="font-display font-semibold text-ink text-[0.95rem]">{{ selectedNutri?.name }}</p>
 <p class="font-body text-[0.78rem] text-ink-muted">{{ selectedNutri?.spec }}</p>
 </div>
 </div>
 <div class="border-t border-border pt-3 space-y-1">
 <div class="flex justify-between font-body text-[0.88rem] text-ink-muted">
 <span>Session (1 hr)</span>
 <span>${{ selectedNutri?.rate }}</span>
 </div>
 <div class="flex justify-between font-body text-[0.88rem] text-ink-muted">
 <span>Date</span>
 <span>{{ selectedDate }}</span>
 </div>
 <div class="flex justify-between font-body text-[0.88rem] text-ink-muted">
 <span>Time</span>
 <span>{{ selectedSlot }}</span>
 </div>
 </div>
 <div class="border-t border-border pt-3 flex justify-between">
 <span class="font-body font-semibold text-ink">Total</span>
 <span class="font-data font-bold text-[1.1rem] text-primary">${{ selectedNutri?.rate }}</span>
 </div>
 </div>

 <!-- Secure payment badge -->
 <div class="flex items-center gap-2 text-ink-muted">
 <svg class="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
 <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
 </svg>
 <span class="font-body text-[0.78rem]">Secured by Stripe · SSL encrypted</span>
 </div>

 <button
 class="font-body text-[0.82rem] text-ink-muted underline hover:text-ink"
 @click="checkoutStep = 'select'"
 >
 ← Change selection
 </button>
 </div>

 <!-- Stripe Elements -->
 <div class="md:col-span-3">
 <h2 class="font-display font-semibold text-[1.2rem] text-ink mb-4">Payment Details</h2>
 <div class="bg-canvas-raised border border-border rounded-xl p-6 shadow-sm">
 <!-- Stripe mounts here -->
 <div id="stripe-payment-element" class="mb-6 min-h-[200px]">
 <div v-if="!paymentElementMounted" class="flex items-center gap-3 text-ink-muted font-body text-sm py-8 justify-center">
 <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
 <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
 <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
 </svg>
 Loading secure payment form...
 </div>
 </div>

 <div v-if="errorMsg" class="bg-danger/10 text-danger text-sm p-3 rounded-lg mb-4 border border-danger/20">
 {{ errorMsg }}
 </div>

 <Button
 class="w-full"
 variant="primary"
 :disabled="!paymentElementMounted || isConfirming"
 @click="confirmPayment"
 >
 <span v-if="isConfirming">Processing payment...</span>
 <span v-else>Pay ${{ selectedNutri?.rate }}</span>
 </Button>

 <p class="font-body text-center text-[0.75rem] text-ink-muted mt-3">
 Use test card <code class="font-mono bg-canvas px-1 rounded">4242 4242 4242 4242</code> with any future expiry.
 </p>
 </div>
 </div>
 </div>

 <!-- Step 3: Success -->
 <div v-else-if="checkoutStep === 'success'" class="text-center py-16 bg-canvas-raised border border-border rounded-2xl">
 <div class="w-16 h-16 bg-success/20 text-success rounded-full flex items-center justify-center mx-auto mb-4">
 <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
 <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
 </svg>
 </div>
 <h2 class="font-display font-semibold text-[1.8rem] text-ink mb-2">Booking Confirmed!</h2>
 <p class="font-body text-ink-muted text-[1rem] max-w-sm mx-auto mb-6">
 You are scheduled with {{ selectedNutri?.name }} on {{ selectedDate }} at {{ selectedSlot }}.
 </p>
 <div class="flex items-center justify-center gap-3">
 <router-link
 :to="bookingResult?.appointment_id ? `/consultation/${bookingResult.appointment_id}?provider=${encodeURIComponent(selectedNutri?.name || 'Dr. Nutritionist')}` : `/consultation/apt_${Date.now()}?provider=${encodeURIComponent(selectedNutri?.name || 'Dr. Nutritionist')}`"
 class="px-5 py-2.5 bg-primary text-white hover:bg-primary-strong rounded-xl text-sm font-semibold shadow-md transition-all flex items-center gap-2"
 >
 <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
 <path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
 </svg>
 Launch Video Consultation
 </router-link>
 <Button variant="outline" @click="$router.push('/dashboard')">Back to Dashboard</Button>
 </div>
 </div>

 </div>
</template>
