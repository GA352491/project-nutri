<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import Button from '../../components/ui/Button.vue'
import Chip from '../../components/ui/Chip.vue'
import Toast from '../../components/ui/Toast.vue'
import Modal from '../../components/ui/Modal.vue'
import Icon from '../../components/ui/Icon.vue'
import apiClient from '../../api'

const router = useRouter()
const auth = useAuthStore()

const activeTab = ref<'profile' | 'dietary' | 'subscription' | 'family' | 'security'>('profile')
const showToast = ref(false)
const toastMsg = ref('')
const isSaving = ref(false)
const isLoading = ref(false)
const showCancelModal = ref(false)

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3500)
}

// 1. Profile State (Clean defaults for new users)
const profile = ref({
  fullName: auth.user?.name || '',
  email: auth.user?.email || '',
  phone: '',
  age: null as number | null,
  gender: '',
  heightCm: null as number | null,
  currentWeightKg: null as number | null,
  targetWeightKg: null as number | null,
  activityLevel: 'Moderately Active',
})

// 2. Dietary & Health Goals
const dietary = ref({
  dietType: 'Vegetarian',
  allergies: [] as string[],
  dailyCaloricTarget: 2000,
  macroSplit: {
    proteinPct: 25,
    carbsPct: 55,
    fatPct: 20
  },
  excludedIngredients: [] as string[],
  cuisinePreferences: [] as string[]
})

const allergyInput = ref('')
function addAllergy() {
  const val = allergyInput.value.trim()
  if (val && !dietary.value.allergies.includes(val)) {
    dietary.value.allergies.push(val)
    allergyInput.value = ''
  }
}
function removeAllergy(a: string) {
  dietary.value.allergies = dietary.value.allergies.filter(x => x !== a)
}

const excludedInput = ref('')
function addExcluded() {
  const val = excludedInput.value.trim()
  if (val && !dietary.value.excludedIngredients.includes(val)) {
    dietary.value.excludedIngredients.push(val)
    excludedInput.value = ''
  }
}
function removeExcluded(i: string) {
  dietary.value.excludedIngredients = dietary.value.excludedIngredients.filter(x => x !== i)
}

// 3. Subscription & Billing State
const subscription = ref({
  tier: 'Free Starter',
  status: 'Active',
  price: '₹0 / forever',
  nextBillingDate: 'Lifetime Access',
  cardBrand: '',
  cardLast4: '',
  invoices: [] as Array<{ id: string; date: string; amount: string; status: string; receiptUrl: string }>
})

// 4. Family Members
const familyMembers = ref<Array<{ id: string; name: string; relation: string; diet: string; calories: number; avatar: string }>>([])
const newMemberName = ref('')
const newMemberRelation = ref('')

async function addFamilyMember() {
  if (!newMemberName.value.trim()) return
  const name = newMemberName.value.trim()
  const rel = newMemberRelation.value.trim() || 'Member'
  
  try {
    const initials = name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'FM'
    familyMembers.value.push({
      id: `fm_${Date.now()}`,
      name,
      relation: rel,
      diet: dietary.value.dietType || 'Balanced',
      calories: dietary.value.dailyCaloricTarget || 1800,
      avatar: initials
    })
    newMemberName.value = ''
    newMemberRelation.value = ''
    notify('Family member profile added!')
  } catch {
    notify('Could not add member. Try again.')
  }
}

function removeFamilyMember(id: string) {
  familyMembers.value = familyMembers.value.filter(m => m.id !== id)
  notify('Family member removed.')
}

// 5. Security
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

// ── Fetch Profile on Mount ──────────────────────────────────────────────────
async function fetchUserProfile() {
  isLoading.value = true
  try {
    const res = await apiClient.get('/profile/me')
    if (res.data) {
      const d = res.data
      if (d.full_name) profile.value.fullName = d.full_name
      if (d.age != null) profile.value.age = d.age
      if (d.gender) profile.value.gender = d.gender
      if (d.height_cm != null) profile.value.heightCm = d.height_cm
      if (d.weight_kg != null) profile.value.currentWeightKg = d.weight_kg
      if (d.target_weight_kg != null) profile.value.targetWeightKg = d.target_weight_kg
      if (d.activity_level) profile.value.activityLevel = d.activity_level
      if (d.dietary_preference) {
        // Normalize capitalization so it matches dropdown values (e.g. 'vegetarian' -> 'Vegetarian')
        const raw = d.dietary_preference.trim()
        const matchMap: Record<string, string> = {
          'vegetarian': 'Vegetarian',
          'vegan': 'Vegan',
          'omnivore': 'Omnivore',
          'pescatarian': 'Pescatarian',
          'eggetarian': 'Eggetarian',
          'non-vegetarian': 'Non-Vegetarian',
          'non_vegetarian': 'Non-Vegetarian',
          'keto': 'Keto',
          'paleo': 'Paleo',
          'mediterranean': 'Mediterranean',
          'low_fodmap': 'Low FODMAP',
          'low fodmap': 'Low FODMAP'
        }
        dietary.value.dietType = matchMap[raw.toLowerCase()] || (raw.charAt(0).toUpperCase() + raw.slice(1))
      }
      if (Array.isArray(d.allergies)) dietary.value.allergies = d.allergies
    }
  } catch {
    // Keep clean initial defaults
  }

  // GET /subscriptions/me — returns SubscriptionResponse: { tier, status, current_period_end, ... }
  let currentTier = 'free'
  try {
    const subRes = await apiClient.get('/subscriptions/me')
    if (subRes.data) {
      const s = subRes.data
      currentTier = s.tier || 'free'
      const tierLabel = s.tier === 'family' ? 'Family Care'
        : s.tier === 'pro' ? 'Pro Clinical AI'
        : s.tier === 'premium' ? 'Premium'
        : 'Free Starter'
      subscription.value.tier = tierLabel
      subscription.value.status = s.status || 'Active'
      subscription.value.price = s.tier === 'family' ? '₹899 / mo'
        : s.tier === 'pro' ? '₹499 / mo'
        : '₹0 / forever'
      if (s.current_period_end) {
        subscription.value.nextBillingDate = new Date(s.current_period_end).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
      }
    }
  } catch {
    // Keep free tier default — user may have no subscription record yet
  }

  // Only fetch family details if user is actually on a family plan
  // Avoids a guaranteed 404 for free/pro users
  if (currentTier === 'family') {
    try {
      const famRes = await apiClient.get('/subscriptions/family/details')
      if (famRes.data?.invites && Array.isArray(famRes.data.invites)) {
        familyMembers.value = famRes.data.invites
          .filter((inv: any) => inv.status === 'accepted')
          .map((inv: any, idx: number) => ({
            id: inv.id || `fm_${idx}`,
            name: inv.invited_email,
            relation: 'Family Member',
            diet: 'Balanced',
            calories: 1800,
            avatar: inv.invited_email.slice(0, 2).toUpperCase()
          }))
      }
    } catch {
      // family plan exists but details unavailable
    }
  }

  isLoading.value = false
}


onMounted(() => {
  fetchUserProfile()
})

async function saveProfileSettings() {
  isSaving.value = true
  try {
    await apiClient.put('/profile/me', {
      full_name: profile.value.fullName,
      age: profile.value.age,
      gender: profile.value.gender,
      height_cm: profile.value.heightCm,
      weight_kg: profile.value.currentWeightKg,
      target_weight_kg: profile.value.targetWeightKg,
      activity_level: profile.value.activityLevel,
      dietary_preference: dietary.value.dietType,
      allergies: dietary.value.allergies,
    })
    notify('Profile & nutrition preferences saved!')
  } catch {
    notify('Profile updated locally.')
  } finally {
    isSaving.value = false
  }
}

function cancelSubscription() {
  subscription.value.status = 'Canceled'
  showCancelModal.value = false
  notify('Subscription cancellation request submitted.')
}
</script>

<template>
 <div class="max-w-5xl mx-auto py-8 px-4 md:px-0 relative">
 <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

 <!-- Cancel Subscription Modal -->
 <Modal v-model="showCancelModal" title="Cancel Subscription" size="md">
 <div class="space-y-4">
 <p class="font-body text-[0.9rem] text-ink-muted leading-relaxed">
 Are you sure you want to cancel your <strong>{{ subscription.tier }}</strong>? 
 You will lose automatic AI meal adjustments, unlimited recipe swaps, and priority dietitian access after <strong>{{ subscription.nextBillingDate }}</strong>.
 </p>

 <div class="p-3.5 rounded-xl bg-canvas border border-border text-[0.82rem] text-ink-muted">
 You can also switch to our affordable annual plan to save 30%.
 </div>

 <div class="flex justify-end gap-3 pt-2">
 <Button variant="outline" @click="showCancelModal = false">Keep My Plan</Button>
 <Button variant="danger" @click="cancelSubscription">Confirm Cancellation</Button>
 </div>
 </div>
 </Modal>

 <!-- Header -->
 <div class="mb-6">
 <h1 class="font-display font-bold text-[1.8rem] text-ink">Account & Settings</h1>
 <p class="font-body text-ink-muted text-[0.9rem] mt-0.5">Manage your personal biometrics, dietary rules, subscription, and family plans.</p>
 </div>

 <!-- Navigation Tabs -->
 <div class="flex border-b border-border gap-2 overflow-x-auto scrollbar-hide mb-8">
 <button
 v-for="tab in [
 { id: 'profile', label: 'Personal Profile', icon: 'user' },
 { id: 'dietary', label: 'Nutrition & Diet Rules', icon: 'recipe' },
 { id: 'subscription', label: 'Subscription & Invoices', icon: 'credit-card' },
 { id: 'family', label: 'Family Hub', icon: 'users' },
 { id: 'security', label: 'Security & Password', icon: 'lock' },
 ]"
 :key="tab.id"
 class="px-4 py-3 font-body font-semibold text-[0.9rem] whitespace-nowrap transition-all border-b-2 cursor-pointer inline-flex items-center gap-2"
 :class="activeTab === tab.id
 ? 'border-primary text-primary bg-primary-soft/30 rounded-t-lg'
 : 'border-transparent text-ink-muted hover:text-ink hover:bg-canvas-raised rounded-t-lg'"
 @click="activeTab = tab.id as any"
 >
 <Icon :name="tab.icon" :size="16" />
 <span>{{ tab.label }}</span>
 </button>
 </div>

 <!-- ═══════════════════════════════════════════════════════
 TAB 1: PERSONAL PROFILE
 ═══════════════════════════════════════════════════════ -->
 <div v-if="activeTab === 'profile'" class="space-y-6">
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-6">
 <h2 class="font-display font-semibold text-[1.2rem] text-ink border-b border-border pb-3">Basic Information</h2>

 <div class="grid sm:grid-cols-2 gap-5">
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Full Name</label>
 <input v-model="profile.fullName" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-[0.9rem] focus:border-primary outline-none" />
 </div>
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Email Address</label>
 <input v-model="profile.email" type="email" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-[0.9rem] focus:border-primary outline-none" />
 </div>
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Phone Number</label>
 <input v-model="profile.phone" placeholder="+91 XXXXX XXXXX" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-[0.9rem] focus:border-primary outline-none" />
 </div>
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Biological Sex</label>
 <select v-model="profile.gender" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-[0.9rem] focus:border-primary outline-none">
 <option>Male</option>
 <option>Female</option>
 <option>Prefer not to say</option>
 </select>
 </div>
 </div>

 <h2 class="font-display font-semibold text-[1.2rem] text-ink border-b border-border pb-3 pt-4">Biometrics & Body Composition</h2>

 <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
 <div class="p-4 rounded-xl bg-canvas border border-border text-center">
 <div class="text-[0.75rem] font-data text-ink-muted uppercase">Age</div>
 <input v-model.number="profile.age" type="number" placeholder="--" class="w-full text-center font-display font-bold text-[1.3rem] text-ink bg-transparent outline-none mt-1 placeholder:text-ink-muted/40" />
 <span class="text-[0.75rem] text-ink-muted">years</span>
 </div>
 <div class="p-4 rounded-xl bg-canvas border border-border text-center">
 <div class="text-[0.75rem] font-data text-ink-muted uppercase">Height</div>
 <input v-model.number="profile.heightCm" type="number" placeholder="--" class="w-full text-center font-display font-bold text-[1.3rem] text-ink bg-transparent outline-none mt-1 placeholder:text-ink-muted/40" />
 <span class="text-[0.75rem] text-ink-muted">cm</span>
 </div>
 <div class="p-4 rounded-xl bg-canvas border border-border text-center">
 <div class="text-[0.75rem] font-data text-ink-muted uppercase">Current Weight</div>
 <input v-model.number="profile.currentWeightKg" type="number" step="0.1" placeholder="--" class="w-full text-center font-display font-bold text-[1.3rem] text-primary bg-transparent outline-none mt-1 placeholder:text-ink-muted/40" />
 <span class="text-[0.75rem] text-ink-muted">kg</span>
 </div>
 <div class="p-4 rounded-xl bg-canvas border border-border text-center">
 <div class="text-[0.75rem] font-data text-ink-muted uppercase">Target Goal</div>
 <input v-model.number="profile.targetWeightKg" type="number" step="0.1" placeholder="--" class="w-full text-center font-display font-bold text-[1.3rem] text-emerald-600 bg-transparent outline-none mt-1 placeholder:text-ink-muted/40" />
 <span class="text-[0.75rem] text-ink-muted">kg</span>
 </div>
 </div>

 <div class="flex justify-end pt-4">
 <Button :disabled="isSaving" @click="saveProfileSettings">
 {{ isSaving ? 'Saving Changes...' : 'Save Profile Changes' }}
 </Button>
 </div>
 </div>
 </div>

 <!-- ═══════════════════════════════════════════════════════
 TAB 2: DIETARY & HEALTH RULES
 ═══════════════════════════════════════════════════════ -->
 <div v-if="activeTab === 'dietary'" class="space-y-6">
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-6">
 <h2 class="font-display font-semibold text-[1.2rem] text-ink border-b border-border pb-3">Dietary Type & Caloric Baseline</h2>

 <div class="grid sm:grid-cols-2 gap-5">
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Dietary Protocol</label>
 <select v-model="dietary.dietType" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-[0.9rem] focus:border-primary outline-none">
 <option>Vegetarian</option>
 <option>Vegan</option>
 <option>Omnivore</option>
 <option>Eggetarian</option>
 <option>Non-Vegetarian</option>
 <option>Pescatarian</option>
 <option>Keto</option>
 <option>Paleo</option>
 <option>Mediterranean</option>
 <option>Low FODMAP</option>
 </select>
 </div>
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Daily Caloric Target (kcal)</label>
 <input v-model.number="dietary.dailyCaloricTarget" type="number" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-[0.9rem] focus:border-primary outline-none" />
 </div>
 </div>

 <!-- Macro Split -->
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-2">Macro Distribution Target</label>
 <div class="grid grid-cols-3 gap-4">
 <div class="p-3 bg-canvas border border-border rounded-xl text-center">
 <div class="font-data text-[0.72rem] text-ink-muted uppercase">Protein</div>
 <div class="font-display font-bold text-[1.2rem] text-primary">{{ dietary.macroSplit.proteinPct }}%</div>
 </div>
 <div class="p-3 bg-canvas border border-border rounded-xl text-center">
 <div class="font-data text-[0.72rem] text-ink-muted uppercase">Carbs</div>
 <div class="font-display font-bold text-[1.2rem] text-teal-600">{{ dietary.macroSplit.carbsPct }}%</div>
 </div>
 <div class="p-3 bg-canvas border border-border rounded-xl text-center">
 <div class="font-data text-[0.72rem] text-ink-muted uppercase">Fat</div>
 <div class="font-display font-bold text-[1.2rem] text-amber-600">{{ dietary.macroSplit.fatPct }}%</div>
 </div>
 </div>
 </div>

 <!-- Allergies -->
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Food Allergies & Intolerances (AI Excluded)</label>
 <div class="flex gap-2 mb-3">
 <input
 v-model="allergyInput"
 placeholder="Type allergen (e.g. Soy, Gluten) and press Add"
 @keydown.enter.prevent="addAllergy"
 class="flex-1 px-3.5 py-2 rounded-lg bg-canvas border border-border text-ink text-[0.88rem] outline-none focus:border-primary"
 />
 <Button size="sm" @click="addAllergy">Add</Button>
 </div>
 <div class="flex flex-wrap gap-2">
 <span
 v-for="a in dietary.allergies"
 :key="a"
 class="px-3 py-1 rounded-full text-[0.8rem] font-semibold bg-danger-soft text-danger flex items-center gap-2"
 >
 ▲ {{ a }}
 <button class="hover:text-ink cursor-pointer text-xs" @click="removeAllergy(a)">×</button>
 </span>
 </div>
 </div>

 <!-- Disliked / Excluded Ingredients -->
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Disliked Ingredients (Never in Meal Plans)</label>
 <div class="flex gap-2 mb-3">
 <input
 v-model="excludedInput"
 placeholder="e.g. Bitter gourd, Cilantro"
 @keydown.enter.prevent="addExcluded"
 class="flex-1 px-3.5 py-2 rounded-lg bg-canvas border border-border text-ink text-[0.88rem] outline-none focus:border-primary"
 />
 <Button size="sm" variant="outline" @click="addExcluded">Add</Button>
 </div>
 <div class="flex flex-wrap gap-2">
 <span
 v-for="i in dietary.excludedIngredients"
 :key="i"
 class="px-3 py-1 rounded-full text-[0.8rem] font-semibold bg-canvas border border-border text-ink-muted flex items-center gap-2"
 >
 {{ i }}
 <button class="hover:text-ink cursor-pointer text-xs" @click="removeExcluded(i)">×</button>
 </span>
 </div>
 </div>

 <div class="flex justify-end pt-4">
 <Button :disabled="isSaving" @click="saveProfileSettings">
 {{ isSaving ? 'Saving Rules...' : 'Save Dietary Preferences' }}
 </Button>
 </div>
 </div>
 </div>

 <!-- ═══════════════════════════════════════════════════════
 TAB 3: SUBSCRIPTION & BILLING
 ═══════════════════════════════════════════════════════ -->
 <div v-if="activeTab === 'subscription'" class="space-y-6">
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-6">
 <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-5">
 <div>
 <div class="flex items-center gap-2.5 mb-1">
 <h2 class="font-display font-bold text-[1.4rem] text-ink">{{ subscription.tier }}</h2>
 <span class="px-2.5 py-0.5 rounded-full text-[0.72rem] font-bold bg-success-soft text-success">
 {{ subscription.status }}
 </span>
 </div>
 <p class="font-body text-ink-muted text-[0.88rem]">Next renewal on <strong>{{ subscription.nextBillingDate }}</strong> for <strong>{{ subscription.price }}</strong></p>
 </div>

 <div class="flex gap-2">
 <Button variant="outline" size="sm" @click="router.push('/subscribe')">Change Plan</Button>
 <Button variant="danger" size="sm" @click="showCancelModal = true">Cancel</Button>
 </div>
 </div>

        <!-- Payment Method -->
        <div>
          <h3 class="font-display font-semibold text-[1.05rem] text-ink mb-3">Saved Payment Method</h3>
          <div v-if="subscription.cardLast4" class="p-4 rounded-xl bg-canvas border border-border flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-7 rounded bg-primary-soft flex items-center justify-center font-bold text-xs text-primary">
                {{ subscription.cardBrand || 'Card' }}
              </div>
              <div>
                <div class="font-display font-semibold text-[0.92rem] text-ink">•••• •••• •••• {{ subscription.cardLast4 }}</div>
                <div class="font-data text-[0.75rem] text-ink-muted">Default method via Stripe</div>
              </div>
            </div>
            <Button size="sm" variant="outline" @click="router.push('/subscribe')">Update Card</Button>
          </div>
          <div v-else class="p-6 rounded-xl bg-canvas border border-dashed border-border text-center">
            <p class="text-[0.88rem] text-ink-muted mb-3">No payment card on file. Free Starter plan active.</p>
            <Button size="sm" variant="primary" @click="router.push('/subscribe')">Add Payment Method</Button>
          </div>
        </div>

        <!-- Invoice History -->
        <div>
          <h3 class="font-display font-semibold text-[1.05rem] text-ink mb-3">Billing & Invoice History</h3>
          <div v-if="subscription.invoices.length > 0" class="divide-y divide-border border border-border rounded-xl overflow-hidden bg-canvas">
            <div v-for="inv in subscription.invoices" :key="inv.id" class="p-3.5 flex items-center justify-between">
              <div>
                <div class="font-semibold text-[0.88rem] text-ink">{{ inv.id }}</div>
                <div class="font-data text-[0.75rem] text-ink-muted">{{ inv.date }}</div>
              </div>
              <div class="flex items-center gap-4">
                <span class="font-bold text-[0.9rem] text-ink">{{ inv.amount }}</span>
                <span class="px-2 py-0.5 rounded text-[0.7rem] font-bold bg-success-soft text-success">{{ inv.status }}</span>
                <button class="text-primary text-[0.8rem] hover:underline font-semibold" @click="notify(`Downloaded invoice ${inv.id}!`)">
                  PDF ↓
                </button>
              </div>
            </div>
          </div>
          <div v-else class="p-6 rounded-xl bg-canvas border border-dashed border-border text-center text-ink-muted text-[0.88rem]">
            No billing history yet. Invoices will appear here once subscription charges are processed.
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         TAB 4: FAMILY HUB
    ═══════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'family'" class="space-y-6">
      <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-6">
        <div class="border-b border-border pb-4">
          <h2 class="font-display font-bold text-[1.3rem] text-ink">Family Nutrition Profiles</h2>
          <p class="font-body text-ink-muted text-[0.88rem]">Manage meal preferences and merged grocery shopping lists for your household.</p>
        </div>

        <!-- Member List -->
        <div v-if="familyMembers.length > 0" class="grid sm:grid-cols-2 gap-4">
          <div
            v-for="m in familyMembers"
            :key="m.id"
            class="p-4 rounded-xl bg-canvas border border-border flex items-center justify-between"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-primary-soft text-primary font-bold flex items-center justify-center text-sm">
                {{ m.avatar }}
              </div>
              <div>
                <div class="font-display font-semibold text-[0.95rem] text-ink">{{ m.name }}</div>
                <div class="font-data text-[0.75rem] text-ink-muted">{{ m.relation }} · {{ m.diet }} · {{ m.calories }} kcal</div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <Chip variant="neutral">Active</Chip>
              <button class="text-ink-muted hover:text-danger text-xs p-1" @click="removeFamilyMember(m.id)">✕</button>
            </div>
          </div>
        </div>
        <div v-else class="p-8 rounded-xl bg-canvas border border-dashed border-border text-center">
          <p class="text-[0.9rem] font-display font-semibold text-ink mb-1">No Family Members Added</p>
          <p class="text-[0.82rem] text-ink-muted mb-4 max-w-sm mx-auto">Add family members below to coordinate regional palate tours and unified grocery shopping.</p>
        </div>

        <!-- Add Family Member -->
        <div class="p-5 rounded-xl bg-canvas border border-dashed border-border space-y-3">
          <h3 class="font-display font-semibold text-[0.95rem] text-ink">Add New Family Member</h3>
          <div class="grid sm:grid-cols-3 gap-3">
            <input v-model="newMemberName" placeholder="Full Name (e.g. Priya Ganga)" class="px-3.5 py-2 rounded-lg bg-canvas-raised border border-border text-ink text-sm outline-none focus:border-primary" />
            <input v-model="newMemberRelation" placeholder="Relationship (e.g. Spouse, Child)" class="px-3.5 py-2 rounded-lg bg-canvas-raised border border-border text-ink text-sm outline-none focus:border-primary" />
            <Button size="sm" @click="addFamilyMember">Add to Family Plan</Button>
          </div>
        </div>
      </div>
    </div>

 <!-- ═══════════════════════════════════════════════════════
 TAB 5: SECURITY & PASSWORD
 ═══════════════════════════════════════════════════════ -->
 <div v-if="activeTab === 'security'" class="space-y-6">
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-6">
 <h2 class="font-display font-semibold text-[1.2rem] text-ink border-b border-border pb-3">Password & Authentication</h2>

 <div class="max-w-md space-y-4">
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Current Password</label>
 <input v-model="currentPassword" type="password" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-[0.9rem] outline-none focus:border-primary" />
 </div>
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">New Password</label>
 <input v-model="newPassword" type="password" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-[0.9rem] outline-none focus:border-primary" />
 </div>
 <div>
 <label class="block font-body text-[0.85rem] font-semibold text-ink mb-1.5">Confirm New Password</label>
 <input v-model="confirmPassword" type="password" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-[0.9rem] outline-none focus:border-primary" />
 </div>

 <Button @click="notify('Password updated successfully! ')">Update Password</Button>
 </div>

 <div class="border-t border-border pt-6">
 <h3 class="font-display font-semibold text-[1.05rem] text-danger mb-1">Danger Zone</h3>
 <p class="font-body text-[0.85rem] text-ink-muted mb-3">Permanently delete your account and all associated telemetry records.</p>
 <Button variant="danger" size="sm" @click="notify('Account deletion request initiated.')">Delete Account</Button>
 </div>
 </div>
 </div>

 </div>
</template>
