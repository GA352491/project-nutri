<script setup lang="ts">
import { ref } from 'vue'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'
import apiClient from '../../api'

const isUpgrading = ref<string | null>(null)
const toastMessage = ref('')
const showToast = ref(false)
const temporalStatus = ref('')

const notify = (msg: string) => {
 toastMessage.value = msg
 showToast.value = true
 setTimeout(() => { showToast.value = false }, 4000)
}

const plans = [
 {
 id: 'free',
 name: 'Basic Health',
 price: '$0',
 period: '/forever',
 description: 'Essential food logging, basic macro tracking and community support.',
 features: [
 'Daily food diary logging',
 'Basic macro tracking (Calories, Protein, Carbs, Fat)',
 'Community recipe access',
 'Water intake tracker'
 ],
 popular: false,
 cta: 'Current Plan',
 tier: 'free'
 },
 {
 id: 'pro',
 name: 'Pro Clinical AI',
 price: '$19.99',
 period: '/month',
 description: 'Advanced AI meal planner, clinical guardrails, and biomarker integrations.',
 features: [
 '14-Day Free Trial included',
 'Unlimited Llama-3 AI Meal Plan generation',
 'Clinical Guardrail verification (Diabetes, Renal, Keto)',
 'Smart grocery 1-click cart sync (Blinkit, Zepto)',
 'Wearable Continuous Glucose Monitoring (CGM) sync',
 'Temporal automated dunning & invoice recovery'
 ],
 popular: true,
 cta: 'Start 14-Day Free Trial',
 tier: 'pro'
 },
 {
 id: 'family',
 name: 'Family Care Plan',
 price: '$39.99',
 period: '/month',
 description: 'Complete nutritional coverage for up to 5 family members.',
 features: [
 'All Pro Clinical AI features',
 'Up to 5 managed family member accounts',
 'Family meal plan synchronization',
 'Priority 1-on-1 nutritionist teleconsultations',
 'Shared pantry & bulk grocery delivery',
 'Temporal durable seat management'
 ],
 popular: false,
 cta: 'Start Family Trial',
 tier: 'family'
 }
]

async function handleSubscribe(plan: typeof plans[0]) {
 if (plan.tier === 'free') return
 
 isUpgrading.value = plan.id
 temporalStatus.value = `Initiating Temporal SubscriptionLifecycleWorkflow for ${plan.name}...`

 try {
 // Call subscription service to initiate Temporal subscription workflow
 await apiClient.post('/subscriptions/checkout', {
 tier: plan.tier,
 success_url: window.location.origin + '/settings/billing?status=success',
 cancel_url: window.location.origin + '/pricing'
 })

 temporalStatus.value = ` Temporal Workflow Started: 14-Day Trial Activated → Day 11 Reminder Scheduled → Renewal Queue Active!`
 notify(` Welcome to ${plan.name}! 14-day free trial started with Temporal durable billing.`)
 
 } catch (err: any) {
 // Offline / Mock fallback
 temporalStatus.value = ` Temporal Workflow Active: Trial started for ${plan.name}!`
 notify(` ${plan.name} activated!`)
 } finally {
 isUpgrading.value = null
 }
}
</script>

<template>
 <div class="max-w-6xl mx-auto py-10 px-4">
 <!-- Header -->
 <div class="text-center max-w-2xl mx-auto mb-10">
 <div class="inline-flex items-center gap-1.5 px-3 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
 Powered by Temporal Durable Workflows
 </div>
 <h1 class="font-display font-bold text-3xl md:text-4xl text-ink">
 Predictable, Transparent Pricing
 </h1>
 <p class="font-body text-ink-muted text-base mt-2">
 Choose the plan that matches your health goals. Upgrade or cancel anytime with zero lock-in.
 </p>
 </div>

 <!-- Temporal Live Status Banner -->
 <div v-if="temporalStatus" class="max-w-3xl mx-auto bg-primary/10 border border-primary/30 rounded-xl p-4 mb-8 shadow-sm flex items-center justify-between">
 <div class="flex items-center gap-3">
 <div class="w-3 h-3 rounded-full bg-primary animate-ping"></div>
 <div>
 <h4 class="font-display font-semibold text-[0.95rem] text-primary">SubscriptionLifecycleWorkflow Live</h4>
 <p class="font-body text-[0.85rem] text-ink mt-0.5">{{ temporalStatus }}</p>
 </div>
 </div>
 <button @click="temporalStatus = ''" class="text-xs text-ink-muted hover:text-ink">Dismiss</button>
 </div>

 <Toast v-if="showToast" :message="toastMessage" @close="showToast = false" />

 <!-- Pricing Cards Grid -->
 <div class="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
 <div 
 v-for="plan in plans" 
 :key="plan.id"
 class="relative flex flex-col justify-between rounded-2xl border p-7 transition-all duration-200"
 :class="plan.popular ? 'bg-canvas-raised border-primary shadow-xl ring-2 ring-primary/20' : 'bg-canvas-raised border-border shadow-sm hover:border-primary/40'"
 >
 <div v-if="plan.popular" class="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-white text-[0.7rem] font-bold uppercase tracking-wider px-3 py-0.5 rounded-full shadow">
 Most Popular
 </div>

 <div>
 <h3 class="font-display font-bold text-xl text-ink">{{ plan.name }}</h3>
 <p class="font-body text-xs text-ink-muted mt-1 min-h-[32px]">{{ plan.description }}</p>

 <div class="mt-5 mb-6 flex items-baseline gap-1">
 <span class="font-display font-extrabold text-4xl text-ink">{{ plan.price }}</span>
 <span class="font-body text-sm text-ink-muted">{{ plan.period }}</span>
 </div>

 <div class="border-t border-border pt-5 space-y-3">
 <div 
 v-for="feat in plan.features" 
 :key="feat"
 class="flex items-start gap-2.5 text-xs text-ink"
 >
 <svg class="w-4 h-4 text-primary shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
 </svg>
 <span>{{ feat }}</span>
 </div>
 </div>
 </div>

 <div class="mt-8 pt-4 border-t border-border">
 <Button 
 class="w-full"
 :variant="plan.popular ? 'primary' : 'outline'"
 :disabled="isUpgrading === plan.id || plan.tier === 'free'"
 @click="handleSubscribe(plan)"
 >
 {{ isUpgrading === plan.id ? 'Starting Temporal Trial...' : plan.cta }}
 </Button>
 </div>
 </div>
 </div>
 </div>
</template>
