<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../../components/ui/Button.vue'
import apiClient from '../../api'

const router = useRouter()

// Form state
const step = ref<1 | 2>(1)
const isSubmitting = ref(false)
const errorMsg = ref('')

const form = ref({
 name: '',
 email: '',
 bio: '',
 hourly_rate_usd: 80,
 specialties: [] as string[],
 certifications: [] as string[],
 newSpecialty: '',
 newCertification: '',
})

const SPECIALTY_OPTIONS = [
 'Diabetes', 'PCOS', 'Weight Loss', 'Keto', 'Sports Nutrition',
 'Gut Health', 'Thyroid', 'Metabolic Health', 'Vegetarian Nutrition',
 'Post-partum', 'Renal (CKD)', 'Hypertrophy', 'Fat Loss',
]

const isStep1Valid = computed(() =>
 form.value.name.trim().length > 2 &&
 form.value.bio.trim().length > 20 &&
 form.value.hourly_rate_usd >= 20
)

function toggleSpecialty(s: string) {
 const idx = form.value.specialties.indexOf(s)
 if (idx === -1) form.value.specialties.push(s)
 else form.value.specialties.splice(idx, 1)
}

function addCustomSpecialty() {
 const v = form.value.newSpecialty.trim()
 if (v && !form.value.specialties.includes(v)) {
 form.value.specialties.push(v)
 }
 form.value.newSpecialty = ''
}

function addCertification() {
 const v = form.value.newCertification.trim()
 if (v && !form.value.certifications.includes(v)) {
 form.value.certifications.push(v)
 }
 form.value.newCertification = ''
}

function removeCertification(c: string) {
 form.value.certifications = form.value.certifications.filter(x => x !== c)
}

async function submitOnboarding() {
 if (!isStep1Valid.value) return
 isSubmitting.value = true
 errorMsg.value = ''

 try {
 const payload = {
 name: form.value.name.trim(),
 email: form.value.email.trim(),
 bio: form.value.bio.trim(),
 hourly_rate_usd: form.value.hourly_rate_usd,
 specialties: form.value.specialties,
 certifications: form.value.certifications,
 }
 const res = await apiClient.post('/marketplace/nutritionists/onboard', payload)
 const data = res.data
 if (data.onboarding_url && data.onboarding_url.startsWith('http')) {
 // Redirect to Stripe Connect hosted onboarding
 window.location.href = data.onboarding_url
 } else {
 // Stripe unavailable locally — show success anyway
 step.value = 2
 }
 } catch (err: any) {
 errorMsg.value = err?.response?.data?.detail || 'Onboarding failed. Please try again.'
 } finally {
 isSubmitting.value = false
 }
}
</script>

<template>
 <div class="min-h-screen bg-canvas flex items-center justify-center py-10 px-4">
 <div class="w-full max-w-xl">

 <!-- Header -->
 <div class="text-center mb-10">
 <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-primary to-primary-dark mb-4 shadow-lg">
 <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
 <path stroke-linecap="round" stroke-linejoin="round"
 d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806
 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438
 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806
 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138
 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946
 3.42 3.42 0 013.138-3.138z" />
 </svg>
 </div>
 <h1 class="font-display font-bold text-[2rem] text-ink">Join as a Nutritionist</h1>
 <p class="font-body text-ink-muted text-[1rem] mt-2 max-w-md mx-auto">
 Build your client base on NutriPlan. Set your own rates and receive 80% of every booking.
 </p>
 </div>

 <!-- Step 1: Profile Form -->
 <div v-if="step === 1" class="bg-canvas-raised border border-border rounded-2xl p-8 shadow-sm space-y-6">

 <!-- Progress -->
 <div class="flex gap-2 mb-2">
 <div class="h-1 flex-1 rounded-full bg-primary"></div>
 <div class="h-1 flex-1 rounded-full bg-border"></div>
 </div>
 <p class="font-data text-[0.72rem] uppercase tracking-widest text-ink-muted">Step 1 of 2 — Your Profile</p>

 <div v-if="errorMsg" class="bg-danger/10 text-danger text-sm p-3 rounded-lg border border-danger/20">
 {{ errorMsg }}
 </div>

 <!-- Name -->
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1">Full Name & Credentials</label>
 <input
 v-model="form.name"
 placeholder="e.g. Dr. Sarah Jenkins, RD"
 class="w-full font-body text-[0.95rem] text-ink bg-canvas border border-border rounded-xl px-4 py-2.5 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition"
 />
 </div>

 <!-- Email -->
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1">Email Address</label>
 <input
 v-model="form.email"
 type="email"
 placeholder="you@example.com"
 class="w-full font-body text-[0.95rem] text-ink bg-canvas border border-border rounded-xl px-4 py-2.5 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition"
 />
 <p class="font-body text-[0.75rem] text-ink-muted mt-1">Used for Stripe payouts. Not shown publicly.</p>
 </div>

 <!-- Bio -->
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1">Professional Bio</label>
 <textarea
 v-model="form.bio"
 rows="3"
 placeholder="Describe your expertise, approach, and who you work best with..."
 class="w-full font-body text-[0.95rem] text-ink bg-canvas border border-border rounded-xl px-4 py-2.5 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition resize-none"
 />
 </div>

 <!-- Hourly Rate -->
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1">
 Hourly Rate
 <span class="ml-2 font-data font-bold text-primary text-[1rem]">${{ form.hourly_rate_usd }}/hr</span>
 </label>
 <input
 v-model.number="form.hourly_rate_usd"
 type="range"
 min="20" max="300" step="5"
 class="w-full accent-primary"
 />
 <div class="flex justify-between font-data text-[0.72rem] text-ink-muted mt-1">
 <span>$20/hr (min)</span>
 <span class="text-ink-muted">You earn 80% = ${{ Math.round(form.hourly_rate_usd * 0.8) }}/hr</span>
 <span>$300/hr</span>
 </div>
 </div>

 <!-- Specialties -->
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-2">Specialties</label>
 <div class="flex flex-wrap gap-2">
 <button
 v-for="s in SPECIALTY_OPTIONS"
 :key="s"
 type="button"
 class="px-3 py-1 rounded-full font-body text-[0.8rem] border transition"
 :class="form.specialties.includes(s)
 ? 'bg-primary text-white border-primary'
 : 'bg-canvas border-border text-ink-muted hover:border-primary/60'"
 @click="toggleSpecialty(s)"
 >
 {{ s }}
 </button>
 </div>
 <div class="flex gap-2 mt-3">
 <input
 v-model="form.newSpecialty"
 placeholder="Add custom specialty..."
 class="flex-1 font-body text-[0.88rem] text-ink bg-canvas border border-border rounded-lg px-3 py-1.5 outline-none focus:border-primary text-sm"
 @keyup.enter="addCustomSpecialty"
 />
 <button type="button" class="px-3 py-1.5 bg-primary text-white rounded-lg text-sm font-body hover:bg-primary-dark transition" @click="addCustomSpecialty">Add</button>
 </div>
 </div>

 <!-- Certifications -->
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-2">Certifications</label>
 <div class="flex flex-wrap gap-2 mb-2">
 <span
 v-for="c in form.certifications"
 :key="c"
 class="flex items-center gap-1 px-3 py-1 rounded-full bg-success/10 text-success border border-success/20 text-[0.8rem] font-body"
 >
 {{ c }}
 <button type="button" class="text-success/60 hover:text-danger ml-1" @click="removeCertification(c)">×</button>
 </span>
 </div>
 <div class="flex gap-2">
 <input
 v-model="form.newCertification"
 placeholder="e.g. Registered Dietitian (RD)"
 class="flex-1 font-body text-[0.88rem] text-ink bg-canvas border border-border rounded-lg px-3 py-1.5 outline-none focus:border-primary text-sm"
 @keyup.enter="addCertification"
 />
 <button type="button" class="px-3 py-1.5 bg-canvas-raised border border-border text-ink-muted rounded-lg text-sm font-body hover:border-primary transition" @click="addCertification">Add</button>
 </div>
 </div>

 <Button
 class="w-full"
 variant="primary"
 :disabled="!isStep1Valid || isSubmitting"
 @click="submitOnboarding"
 >
 <span v-if="isSubmitting">Creating your profile...</span>
 <span v-else>Continue to Payout Setup →</span>
 </Button>

 <!-- Earnings info -->
 <div class="flex items-start gap-3 bg-primary/5 border border-primary/15 rounded-xl p-4">
 <svg class="w-5 h-5 text-primary mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
 <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
 </svg>
 <p class="font-body text-[0.82rem] text-ink-muted">
 NutriPlan takes a <strong class="text-ink">20% platform fee</strong> per booking. Payouts are processed via
 <strong class="text-ink">Stripe Connect</strong> and typically arrive in your bank within 2 business days.
 </p>
 </div>
 </div>

 <!-- Step 2: Success (fallback when Stripe not available locally) -->
 <div v-else class="text-center py-16 bg-canvas-raised border border-border rounded-2xl shadow-sm px-8">
 <div class="w-16 h-16 bg-success/20 text-success rounded-full flex items-center justify-center mx-auto mb-5">
 <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
 <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
 </svg>
 </div>
 <h2 class="font-display font-bold text-[1.8rem] text-ink mb-2">Profile Created!</h2>
 <p class="font-body text-ink-muted text-[1rem] max-w-sm mx-auto mb-6">
 Your marketplace profile is live. Complete your Stripe payout setup to start receiving payments.
 </p>
 <div class="flex flex-col gap-3 items-center">
 <Button variant="primary" @click="router.push('/expert/dashboard')">Go to Expert Dashboard</Button>
 <Button variant="outline" @click="router.push('/appointments/book')">Browse Marketplace</Button>
 </div>
 </div>

 </div>
 </div>
</template>
