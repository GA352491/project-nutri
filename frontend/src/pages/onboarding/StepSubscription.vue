<script setup lang="ts">
import { ref, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { loadStripe, type Stripe, type StripeElements, type StripePaymentElement } from '@stripe/stripe-js'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'
import apiClient from '../../api'

// ── Stripe Publishable Key ────────────────────────────────────────────────────
// Set VITE_STRIPE_PUBLISHABLE_KEY in your .env file with your real test key from
// https://dashboard.stripe.com/test/apikeys
const STRIPE_PUBLISHABLE_KEY = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY as string

const router = useRouter()
const selectedTier = ref<'pro' | 'family' | 'free'>('pro')
const showPaymentModal = ref(false)
const toastMessage = ref('')
const showToast = ref(false)
const temporalMessage = ref('')

// Stripe state
const isLoadingStripe = ref(false)
const isProcessing = ref(false)
const stripeError = ref('')
const stripeInstance = ref<Stripe | null>(null)
const stripeElements = ref<StripeElements | null>(null)
const paymentElement = ref<StripePaymentElement | null>(null)
const stripeReady = ref(false)
const setupIntentClientSecret = ref('')

const plans = [
  {
    tier: 'free',
    name: 'Basic Starter',
    price: '₹0',
    period: '/forever',
    description: 'Basic food logging and community recipe catalog.',
    features: ['Manual food diary logging', 'Basic daily macro calculation', 'Community recipes'],
    cta: 'Continue with Basic'
  },
  {
    tier: 'pro',
    name: 'Pro Clinical AI',
    price: '₹499',
    period: '/mo',
    trial: '',
    popular: true,
    description: '7-Day Regional Palate Tours, clinical guardrails & grocery sync.',
    features: [
      'Instant Active Subscription',
      'Unlimited 7-Day Regional Palate Tours',
      'Clinical Guardrails (Diabetes, Keto, Renal)',
      '1-Click Grocery Cart Sync (Zepto, Blinkit)',
      'Wearable & CGM Continuous Telemetry'
    ],
    cta: 'Subscribe to Pro (₹499/mo)'
  },
  {
    tier: 'family',
    name: 'Family Care',
    price: '₹899',
    period: '/mo',
    trial: '',
    popular: false,
    description: 'Full nutrition coverage for up to 5 family members.',
    features: [
      'All Pro Clinical features included',
      'Up to 5 managed family profiles',
      'Shared pantry sync & bulk ordering',
      '1-on-1 nutritionist telehealth consults'
    ],
    cta: 'Subscribe to Family (₹899/mo)'
  }
]

const notify = (msg: string) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3500)
}

// ── Open the payment modal and initialise Stripe Elements ────────────────────
async function handleSelectPlan(tier: 'pro' | 'family' | 'free') {
  selectedTier.value = tier
  if (tier === 'free') {
    completeOnboarding()
    return
  }

  showPaymentModal.value = true
  stripeError.value = ''
  stripeReady.value = false
  isLoadingStripe.value = true

  try {
    // 1. Load Stripe.js
    if (!stripeInstance.value) {
      if (!STRIPE_PUBLISHABLE_KEY) {
        stripeError.value = 'Stripe publishable key is not configured. Set VITE_STRIPE_PUBLISHABLE_KEY in your .env file.'
        return
      }
      stripeInstance.value = await loadStripe(STRIPE_PUBLISHABLE_KEY)
    }

    // 2. Request a real SetupIntent from the backend
    const res = await apiClient.post('/payment/stripe/checkout/setup-intent', {
      tier: selectedTier.value
    })
    setupIntentClientSecret.value = res.data.client_secret

    // 3. Mount Stripe Elements PaymentElement
    await nextTick()
    await mountStripeElements()
  } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.message || 'Could not initialize Stripe payment.'
    stripeError.value = msg
  } finally {
    isLoadingStripe.value = false
  }
}

async function mountStripeElements() {
  if (!stripeInstance.value || !setupIntentClientSecret.value) return

  // Wait a tick so #stripe-subscription-element is in the DOM
  await new Promise(r => setTimeout(r, 100))

  const mountTarget = document.getElementById('stripe-subscription-element')
  if (!mountTarget) return

  stripeElements.value = stripeInstance.value.elements({
    clientSecret: setupIntentClientSecret.value,
    appearance: {
      theme: 'flat',
      variables: {
        colorPrimary: '#2F5233',
        colorBackground: '#FFFFFF',
        colorText: '#1C2620',
        colorDanger: '#DC2626',
        colorTextPlaceholder: '#5B6B5E',
        fontFamily: 'IBM Plex Sans, system-ui, sans-serif',
        borderRadius: '8px',
        spacingUnit: '4px',
      },
      rules: {
        '.Input': {
          border: '1px solid #D9DED3',
          backgroundColor: '#FFFFFF',
        },
        '.Input:focus': {
          border: '1px solid #2F5233',
          boxShadow: '0 0 0 3px rgba(47,82,51,0.15)',
        },
        '.Label': {
          color: '#5B6B5E',
          fontWeight: '600',
          fontSize: '11px',
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
        },
      }
    }
  })

  paymentElement.value = stripeElements.value.create('payment')
  paymentElement.value.mount('#stripe-subscription-element')
  paymentElement.value.on('ready', () => { stripeReady.value = true })
  paymentElement.value.on('change', (e) => {
    if (e.complete) stripeError.value = ''
  })
}

// ── Confirm the SetupIntent and activate the subscription ────────────────────
async function confirmAndActivate() {
  if (!stripeInstance.value || !stripeElements.value) return
  isProcessing.value = true
  stripeError.value = ''
  temporalMessage.value = ` Securing card with Stripe SetupIntent...`

  const { error, setupIntent } = await stripeInstance.value.confirmSetup({
    elements: stripeElements.value,
    confirmParams: {
      return_url: `${window.location.origin}/dashboard?onboarding=done`,
    },
    redirect: 'if_required',
  })

  if (error) {
    stripeError.value = error.message || 'Payment authorization failed. Please try again.'
    temporalMessage.value = ''
    isProcessing.value = false
    return
  }

  // Card secured — now activate the subscription workflow via backend
  try {
    temporalMessage.value = ` Activating Temporal SubscriptionLifecycleWorkflow (${selectedTier.value.toUpperCase()})...`
    await apiClient.post('/subscriptions/checkout', {
      tier: selectedTier.value,
      payment_method_id: setupIntent?.payment_method as string ?? '',
      success_url: `${window.location.origin}/dashboard`,
      cancel_url: `${window.location.origin}/onboarding/subscription`
    })
    temporalMessage.value = '✅ Subscription activated! Redirecting to your dashboard...'
    notify(' Subscription Activated!')
    setTimeout(() => completeOnboarding(), 1200)
  } catch {
    // If subscription backend call fails, still redirect — payment method was saved
    temporalMessage.value = '✅ Card saved! Setting up your plan...'
    setTimeout(() => completeOnboarding(), 1200)
  } finally {
    isProcessing.value = false
  }
}

function closeModal() {
  showPaymentModal.value = false
  stripeError.value = ''
  temporalMessage.value = ''
  // Unmount Stripe element to avoid memory leaks
  paymentElement.value?.destroy()
  paymentElement.value = null
  stripeElements.value = null
  stripeReady.value = false
}

function completeOnboarding() {
  router.push('/dashboard')
}

function backStep() {
  router.push('/onboarding/pantry')
}

onBeforeUnmount(() => {
  paymentElement.value?.destroy()
})
</script>

<template>
  <div class="animate-[step-slide-in_260ms_var(--ease-out)_both] pb-6">
    <div class="text-center max-w-lg mx-auto mb-6">
      <div class="inline-flex items-center gap-1.5 px-3 py-0.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-xs font-semibold uppercase tracking-wider mb-2">
        Step 5 of 5 • Final Step
      </div>
      <h2 class="font-display font-bold text-2xl md:text-3xl text-ink">Choose Your Plan</h2>
      <p class="text-ink-muted text-sm mt-1">
        Select a membership to unlock AI meal rotation, 1-click cart sync, and expert consultations.
      </p>
    </div>

 <!-- Temporal Status Notification -->
 <div v-if="temporalMessage" class="bg-primary/10 border border-primary/30 rounded-xl p-3.5 mb-6 text-sm text-primary flex items-center gap-3 animate-pulse">
 <div class="w-2.5 h-2.5 rounded-full bg-primary animate-ping shrink-0"></div>
 <span class="font-medium">{{ temporalMessage }}</span>
 </div>

 <Toast v-if="showToast" :message="toastMessage" @close="showToast = false" />

 <!-- Plans Selection Grid -->
 <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
 <div
 v-for="plan in plans"
 :key="plan.tier"
 class="relative flex flex-col justify-between rounded-xl border p-5 transition-all cursor-pointer"
 :class="[
 selectedTier === plan.tier
 ? 'bg-canvas-raised border-primary shadow-lg ring-2 ring-primary/20'
 : 'bg-canvas-raised border-border hover:border-primary/40',
 plan.popular ? 'border-primary/80' : ''
 ]"
 @click="selectedTier = plan.tier as any"
 >
 <div v-if="plan.popular" class="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-primary text-white text-[0.65rem] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full shadow">
 Recommended
 </div>

 <div>
 <div class="flex justify-between items-start mb-1">
 <h3 class="font-display font-bold text-base text-ink">{{ plan.name }}</h3>
 <span v-if="plan.trial" class="text-[0.68rem] bg-emerald-500/10 text-emerald-600 font-semibold px-2 py-0.5 rounded-full border border-emerald-500/20">
 {{ plan.trial }}
 </span>
 </div>
 <p class="text-xs text-ink-muted mb-3 min-h-[30px]">{{ plan.description }}</p>

 <div class="flex items-baseline gap-1 mb-4">
 <span class="font-display font-extrabold text-2xl text-ink">{{ plan.price }}</span>
 <span class="text-xs text-ink-muted">{{ plan.period }}</span>
 </div>

 <div class="space-y-2 border-t border-border pt-3">
 <div
 v-for="feat in plan.features"
 :key="feat"
 class="flex items-start gap-2 text-xs text-ink"
 >
 <svg class="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
 </svg>
 <span>{{ feat }}</span>
 </div>
 </div>
 </div>

 <div class="mt-5 pt-3 border-t border-border">
 <Button
 class="w-full"
 size="sm"
 :variant="selectedTier === plan.tier ? 'primary' : 'outline'"
 @click.stop="handleSelectPlan(plan.tier as any)"
 >
 {{ plan.cta }}
 </Button>
 </div>
 </div>
 </div>

 <!-- Navigation Footer -->
 <div class="flex justify-between items-center border-t border-border pt-4">
 <Button variant="ghost" @click="backStep">Back</Button>
 <Button variant="outline" @click="completeOnboarding">Skip to Dashboard</Button>
 </div>

 <!-- Real Stripe Elements Payment Modal -->
 <div v-if="showPaymentModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
 <div class="bg-canvas-raised border border-border rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">

      <!-- Header -->
      <div class="flex justify-between items-center pb-3 border-b border-border">
        <div>
          <h3 class="font-display font-bold text-lg text-ink">Payment Subscription</h3>
          <p class="text-xs text-ink-muted">Secure monthly subscription • Cancel anytime</p>
        </div>
        <button @click="closeModal" class="text-ink-muted hover:text-ink text-sm font-bold leading-none px-1" aria-label="Close">✕</button>
      </div>

      <!-- Stripe Error Banner -->
      <div v-if="stripeError" class="bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2.5 text-xs text-red-400 flex items-start gap-2">
        <span class="shrink-0 mt-0.5">▲</span>
        <span>{{ stripeError }}</span>
      </div>

      <!-- Stripe Loading State -->
      <div v-if="isLoadingStripe" class="flex flex-col items-center py-8 gap-3">
        <svg class="w-8 h-8 text-primary animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <p class="text-xs text-ink-muted">Connecting to Stripe...</p>
      </div>

      <!-- Official Stripe PaymentElement iframe -->
      <div v-show="!isLoadingStripe && !stripeError" class="space-y-3">
        <!-- Stripe PaymentElement mounts here — this is the official PCI-safe Stripe iframe -->
        <div id="stripe-subscription-element" class="min-h-[200px]"></div>

        <!-- Pricing summary -->
        <div class="bg-primary/5 border border-primary/15 rounded-lg p-3 text-xs text-ink-muted flex items-center justify-between">
          <span>Plan: <strong class="text-ink font-semibold">{{ selectedTier === 'family' ? 'Family Care' : 'Pro Clinical AI' }}</strong></span>
          <span>Subscription: <strong class="text-ink font-semibold">{{ selectedTier === 'family' ? '₹899' : '₹499' }}/mo</strong></span>
        </div>
      </div>

      <!-- Confirm Button -->
      <Button
        v-if="!isLoadingStripe && !stripeError"
        class="w-full"
        variant="primary"
        :loading="isProcessing"
        :disabled="!stripeReady || isProcessing"
        @click="confirmAndActivate"
        id="stripe-confirm-btn"
      >
        {{ isProcessing ? 'Processing subscription...' : `Pay & Subscribe (${selectedTier === 'family' ? '₹899' : '₹499'}/mo)` }}
      </Button>

      <!-- Stripe branding + security note -->
      <div class="flex items-center justify-center gap-2 text-[0.65rem] text-ink-muted">
        <svg viewBox="0 0 60 25" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-4 opacity-60">
          <path d="M59.64 14.28c0 3.37-1.77 5.3-4.87 5.3-2.77 0-4.43-1.46-4.43-3.97 0-2.67 1.85-4.04 5.04-4.04.44 0 .84.04 1.2.1V10.9c0-1.12-.53-1.7-1.74-1.7-1.15 0-2.09.3-2.97.78l-.53-1.7a9.4 9.4 0 014.02-.87c2.88 0 4.28 1.44 4.28 4.12v2.75zM57.02 13.4c-.3-.06-.66-.1-1.04-.1-1.56 0-2.36.62-2.36 1.84 0 1.06.6 1.66 1.64 1.66 1.14 0 1.76-.72 1.76-2.02v-1.38zm-8.64 5.94h-2.2v-5.5c0-1.34-.5-2.04-1.65-2.04-1.08 0-1.8.72-1.8 2.04v5.5H40.5V6.86h2.23v5.04c.6-.8 1.47-1.24 2.6-1.24 2.04 0 3.05 1.25 3.05 3.53v5.15zM37.2 9.78h-1.94v5.12c0 1.04.4 1.52 1.24 1.52.22 0 .46-.04.7-.1l.04 1.84a6.01 6.01 0 01-1.3.12c-2.06 0-2.9-.9-2.9-3.02V9.78h-1.3V8h1.3V5.86l2.22-.68V8h1.94v1.78zm-7.94 9.56h-2.22V11c0-.84-.03-1.66-.08-2.46l2-.12.12 1.54c.54-1.1 1.47-1.7 2.74-1.7.3 0 .58.03.84.1l-.1 2.1a3.1 3.1 0 00-.8-.1c-1.36 0-2.2.9-2.2 2.58l-.3 6.4zM23.2 9.78h-1.94V14.9c0 1.04.4 1.52 1.24 1.52.22 0 .46-.04.7-.1l.04 1.84a6.01 6.01 0 01-1.3.12c-2.06 0-2.9-.9-2.9-3.02V9.78h-1.3V8h1.3V5.86l2.22-.68V8h1.94v1.78zm-8.3 9.56h-2.2V11c0-.84-.04-1.66-.1-2.46l2-.12.12 1.54c.54-1.1 1.48-1.7 2.74-1.7.3 0 .58.03.84.1l-.1 2.1a3.1 3.1 0 00-.8-.1c-1.36 0-2.2.9-2.2 2.58l-.3 6.4z" fill="currentColor"/>
          <path d="M7.8 4.8C4.06 4.8 1.5 7.04 1.5 10.44c0 3.46 2.3 5.34 6.18 5.34 1.74 0 3.24-.36 4.52-1.08l-.56-1.8a8.24 8.24 0 01-3.6.82c-2.16 0-3.42-.96-3.56-2.9h8.26c.04-.3.07-.64.07-1.04C12.81 6.88 11.02 4.8 7.8 4.8zm-3.28 4.42c.2-1.72 1.2-2.74 2.94-2.74 1.6 0 2.5 1 2.5 2.74H4.52z" fill="currentColor"/>
        </svg>
        <span>Secured by Stripe — 256-bit TLS encryption. Cancel anytime.</span>
      </div>
 </div>
 </div>
 </div>
</template>
