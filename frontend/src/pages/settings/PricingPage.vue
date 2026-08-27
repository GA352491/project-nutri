<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Button from '../../components/ui/Button.vue'
import apiClient from '../../api'

const currentPlan = ref('free')
const isProcessing = ref(false)
const showSuccessMock = ref(false)
const successMessage = ref('')

// Referral state
const referralData = ref({
 referral_code: '',
 share_url: '',
 reward_days: 30,
 total_referrals: 0,
 successful_referrals: 0
})
const referralInput = ref('')
const isRedeeming = ref(false)
const referralMessage = ref('')
const referralError = ref('')
const copied = ref(false)

// Family Plan state
const familyPlan = ref<any>(null)
const inviteEmail = ref('')
const isInviting = ref(false)
const familyError = ref('')
const familySuccess = ref('')

const tiers = [
 {
 id: 'free',
 name: 'Basic',
 price: '₹0',
 interval: 'forever',
 description: 'Perfect for getting started with mindful eating.',
 features: [
 'Basic macro tracking',
 'IFCT ingredient database',
 'Standard meal plans',
 'Community support'
 ]
 },
 {
 id: 'premium',
 name: 'Premium',
 price: '₹249',
 interval: '/month',
 description: 'Advanced tracking and personalized insights.',
 popular: true,
 features: [
 'Everything in Basic',
 'Curated recipe generation',
 'AI Nutritionist Chat',
 'Grocery list sync',
 'Micro-nutrient tracking'
 ]
 },
 {
 id: 'family',
 name: 'Family Plan',
 price: '₹499',
 interval: '/month',
 description: 'One billing umbrella for up to 5 family members.',
 features: [
 'Everything in Premium for 5 users',
 'Shared grocery lists',
 'Family dietary profiles & preferences',
 'Child & spouse profile management',
 'Priority family support'
 ]
 },
 {
 id: 'pro',
 name: 'Pro',
 price: '₹999',
 interval: '/year',
 description: 'The ultimate tool for fitness enthusiasts.',
 features: [
 'Everything in Premium',
 'Wearable device sync (Fitbit/Apple)',
 '1-on-1 human nutritionist review',
 'Export detailed reports for doctors',
 'Priority support'
 ]
 }
]

onMounted(async () => {
 try {
 const subRes = await apiClient.get('/subscriptions/me')
 if (subRes.data) {
 currentPlan.value = subRes.data.tier || 'free'
 }
 } catch (e) {
 console.warn('Could not fetch subscription, running in sandbox mode')
 }

 try {
 const refRes = await apiClient.get('/subscriptions/referrals/my-code')
 if (refRes.data) {
 referralData.value = refRes.data
 }
 } catch (e) {
 referralData.value = {
 referral_code: 'NUTRI-GIFT30',
 share_url: `${window.location.origin}/register?ref=NUTRI-GIFT30`,
 reward_days: 30,
 total_referrals: 2,
 successful_referrals: 1
 }
 }

 if (currentPlan.value === 'family') {
 loadFamilyPlan()
 }
})

async function loadFamilyPlan() {
 try {
 const famRes = await apiClient.get('/subscriptions/family/details')
 if (famRes.data) {
 familyPlan.value = famRes.data
 }
 } catch (e) {
 familyPlan.value = {
 plan_name: 'Family Nutrition Plan',
 max_members: 5,
 current_member_count: 1,
 invites: []
 }
 }
}

async function checkout(tierId: string) {
 isProcessing.value = true
 try {
 await apiClient.post(`/subscriptions/mock-webhook?tier=${tierId}`)
 currentPlan.value = tierId
 successMessage.value = `Account successfully upgraded to ${tierId.toUpperCase()}!`
 showSuccessMock.value = true
 if (tierId === 'family') {
 loadFamilyPlan()
 }
 } catch (e) {
 currentPlan.value = tierId
 successMessage.value = `Sandbox: Account simulated as ${tierId.toUpperCase()}!`
 showSuccessMock.value = true
 } finally {
 isProcessing.value = false
 }
}

function copyReferralLink() {
 navigator.clipboard.writeText(referralData.value.share_url)
 copied.value = true
 setTimeout(() => (copied.value = false), 2000)
}

async function redeemCode() {
 if (!referralInput.value) return
 isRedeeming.value = true
 referralError.value = ''
 referralMessage.value = ''
 
 try {
 const res = await apiClient.post('/subscriptions/referrals/redeem', {
 referral_code: referralInput.value
 })
 referralMessage.value = res.data.message || ' 30 days added to your plan!'
 currentPlan.value = 'premium'
 } catch (err: any) {
 referralError.value = err.response?.data?.detail || 'Invalid or expired referral code.'
 } finally {
 isRedeeming.value = false
 }
}

async function sendFamilyInvite() {
 if (!inviteEmail.value) return
 isInviting.value = true
 familyError.value = ''
 familySuccess.value = ''
 
 try {
 await apiClient.post('/subscriptions/family/invite', {
 email: inviteEmail.value
 })
 familySuccess.value = `Invitation sent to ${inviteEmail.value}`
 inviteEmail.value = ''
 loadFamilyPlan()
 } catch (err: any) {
 familyError.value = err.response?.data?.detail || 'Failed to send invite.'
 } finally {
 isInviting.value = false
 }
}
</script>

<template>
 <div class="max-w-6xl mx-auto py-8 px-4">
 
 <div class="text-center mb-12">
 <h1 class="font-display font-semibold text-[2rem] text-ink mb-3">Upgrade your journey</h1>
 <p class="font-body text-ink-muted text-[1.05rem] max-w-lg mx-auto">
 Unlock AI-powered recipes, smart grocery lists, family plans, and personalized nutritionist guidance.
 </p>
 </div>

 <!-- Pricing Cards -->
 <div class="grid md:grid-cols-4 gap-6 items-start mb-16">
 <div 
 v-for="tier in tiers" 
 :key="tier.id"
 class="bg-canvas-raised rounded-2xl p-6 border relative transition-all"
 :class="tier.popular ? 'border-primary shadow-card shadow-primary/10 -mt-2' : 'border-border shadow-sm'"
 >
 <div v-if="tier.popular" class="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-primary text-white text-[0.7rem] font-data uppercase tracking-wider font-bold py-1 px-3 rounded-full">
 Most Popular
 </div>
 
 <h3 class="font-display font-semibold text-[1.2rem] text-ink mb-2">{{ tier.name }}</h3>
 <p class="font-body text-[0.85rem] text-ink-muted min-h-[40px]">{{ tier.description }}</p>
 
 <div class="my-6">
 <span class="font-display font-bold text-[2rem] text-ink tabular-nums">{{ tier.price }}</span>
 <span class="font-data text-[0.8rem] text-ink-muted">{{ tier.interval }}</span>
 </div>

 <Button 
 class="w-full mb-6" 
 :variant="tier.popular ? 'primary' : 'outline'"
 :disabled="currentPlan === tier.id || isProcessing"
 @click="checkout(tier.id)"
 >
 <span v-if="isProcessing && tier.popular">Processing...</span>
 <span v-else-if="currentPlan === tier.id">Current Plan</span>
 <span v-else>Choose {{ tier.name }}</span>
 </Button>

 <ul class="space-y-3">
 <li v-for="(feature, idx) in tier.features" :key="idx" class="flex items-start gap-2">
 <svg class="w-4 h-4 text-primary shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
 <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
 </svg>
 <span class="font-body text-[0.85rem] text-ink">{{ feature }}</span>
 </li>
 </ul>
 </div>
 </div>

 <!-- Growth Feature 1: Referral Program ("Give a month, get a month") -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-8 mb-12 shadow-sm grid md:grid-cols-2 gap-8 items-center">
 <div>
 <div class="inline-flex items-center gap-2 px-3 py-1 bg-accent-coral/10 text-accent-coral text-xs font-semibold rounded-full mb-3">
 Referral Rewards
 </div>
 <h2 class="font-display font-semibold text-2xl text-ink mb-2">Give a Month, Get a Month</h2>
 <p class="font-body text-ink-muted text-sm leading-relaxed mb-4">
 Invite friends to NutriPlan. When they sign up using your link, both of you get <strong class="text-ink">30 days of Premium for free</strong>!
 </p>

 <!-- Referral Link Share Box -->
 <div class="flex items-center gap-2 bg-canvas border border-border p-2 rounded-xl mb-4">
 <input 
 type="text" 
 readonly 
 :value="referralData.share_url" 
 class="bg-transparent font-data text-xs text-ink flex-1 outline-none px-2 select-all"
 />
 <button 
 @click="copyReferralLink" 
 class="px-3 py-1.5 bg-primary text-white font-body text-xs font-semibold rounded-lg hover:bg-primary-dark transition"
 >
 {{ copied ? 'Copied! ' : 'Copy Link' }}
 </button>
 </div>

 <div class="flex gap-6 font-data text-xs text-ink-muted">
 <div><strong class="text-ink font-bold">{{ referralData.total_referrals }}</strong> Friends Invited</div>
 <div><strong class="text-success font-bold">{{ referralData.successful_referrals }}</strong> Rewards Earned</div>
 </div>
 </div>

 <!-- Redeem Code Section -->
 <div class="bg-canvas border border-border p-6 rounded-xl">
 <h3 class="font-display font-semibold text-lg text-ink mb-2">Have a Referral Code?</h3>
 <p class="font-body text-xs text-ink-muted mb-4">Enter a friend's invite code below to unlock your free 30-day Premium membership.</p>
 
 <div class="flex gap-2 mb-3">
 <input 
 v-model="referralInput"
 type="text" 
 placeholder="e.g. NUTRI-ABC1234"
 class="bg-canvas-raised font-mono text-xs uppercase text-ink border border-border rounded-lg px-3 py-2 flex-1 outline-none focus:border-primary"
 />
 <Button variant="primary" :disabled="!referralInput || isRedeeming" @click="redeemCode">
 {{ isRedeeming ? 'Redeeming...' : 'Apply' }}
 </Button>
 </div>

 <p v-if="referralMessage" class="text-success text-xs font-medium">{{ referralMessage }}</p>
 <p v-if="referralError" class="text-danger text-xs font-medium">{{ referralError }}</p>
 </div>
 </div>

 <!-- Growth Feature 2: Family Plan Management (If on family plan or preview) -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-8 shadow-sm">
 <div class="flex justify-between items-center mb-6">
 <div>
 <div class="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 text-primary text-xs font-semibold rounded-full mb-2">
 ‍‍‍ Family Sharing
 </div>
 <h2 class="font-display font-semibold text-2xl text-ink">Manage Family Plan</h2>
 <p class="font-body text-ink-muted text-sm">
 Share premium features with spouse or children under a single unified billing umbrella (up to 5 members).
 </p>
 </div>
 <div v-if="currentPlan !== 'family'">
 <Button variant="outline" @click="checkout('family')">Upgrade to Family Plan (₹499/mo)</Button>
 </div>
 </div>

 <div v-if="currentPlan === 'family'" class="space-y-6">
 <!-- Invite input -->
 <div class="flex gap-3 max-w-md">
 <input 
 v-model="inviteEmail"
 type="email" 
 placeholder="family.member@example.com"
 class="bg-canvas font-body text-sm text-ink border border-border rounded-xl px-4 py-2 flex-1 outline-none focus:border-primary"
 />
 <Button variant="primary" :disabled="!inviteEmail || isInviting" @click="sendFamilyInvite">
 {{ isInviting ? 'Inviting...' : 'Send Invite' }}
 </Button>
 </div>
 <p v-if="familySuccess" class="text-success text-xs">{{ familySuccess }}</p>
 <p v-if="familyError" class="text-danger text-xs">{{ familyError }}</p>

 <!-- Member list preview -->
 <div class="border-t border-border pt-4">
 <h4 class="font-body text-xs font-semibold text-ink-muted uppercase tracking-wider mb-3">Plan Members ({{ familyPlan?.current_member_count || 1 }}/5)</h4>
 <div class="flex items-center gap-3 py-2 text-sm text-ink">
 <div class="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-xs">YOU</div>
 <div>
 <p class="font-semibold">Primary Subscriber</p>
 <p class="text-xs text-ink-muted">Organizer & Billing Admin</p>
 </div>
 </div>
 <div v-for="inv in familyPlan?.invites || []" :key="inv.id" class="flex items-center justify-between py-2 text-sm border-t border-border/50">
 <span class="text-ink">{{ inv.invited_email }}</span>
 <span class="text-xs px-2 py-0.5 rounded bg-warning/10 text-warning font-medium uppercase">{{ inv.status }}</span>
 </div>
 </div>
 </div>

 <div v-else class="bg-canvas border border-border p-4 rounded-xl text-center">
 <p class="text-sm text-ink-muted mb-2">You are currently on the <strong class="text-ink uppercase">{{ currentPlan }}</strong> plan.</p>
 <p class="text-xs text-ink-muted">Upgrade to the Family Plan to unlock member invitations and shared pantry management.</p>
 </div>
 </div>

 <!-- Mock Success Toast (Sandbox only) -->
 <Transition name="fade">
 <div v-if="showSuccessMock" class="fixed bottom-6 left-1/2 -translate-x-1/2 bg-success text-white px-6 py-3 rounded-lg shadow-lg font-body text-[0.9rem] flex items-center gap-3">
 <span> {{ successMessage }}</span>
 <button class="opacity-80 hover:opacity-100" @click="showSuccessMock = false">×</button>
 </div>
 </Transition>

 </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
 transition: opacity 300ms ease, transform 300ms ease;
}
.fade-enter-from, .fade-leave-to {
 opacity: 0;
 transform: translate(-50%, 10px);
}
</style>
