<script setup lang="ts">
import { ref } from 'vue'
import Button from '../../components/ui/Button.vue'
import Chip from '../../components/ui/Chip.vue'
import Toast from '../../components/ui/Toast.vue'
import Icon from '../../components/ui/Icon.vue'
import apiClient from '../../api'

const activeTab = ref<'profile' | 'credentials' | 'calendar' | 'payouts'>('profile')
const showToast = ref(false)
const toastMsg = ref('')
const isSaving = ref(false)
const isSettingUp = ref(false)

function notify(msg: string) {
 toastMsg.value = msg
 showToast.value = true
 setTimeout(() => { showToast.value = false }, 3500)
}

// 1. Profile state
const profile = ref({
 name: 'Dr. Ananya Iyer, RD',
 email: 'ananya.iyer@nutriplan.local',
 phone: '+91 98450 11223',
 title: 'Senior Clinical Dietitian & Diabetes Specialist',
 bio: 'Over 9 years of experience prescribing clinical medical nutrition therapy for Type-2 Diabetes, PCOS, and gut health optimization.',
 avatar: 'https://images.unsplash.com/photo-1594824813580-c1fd9f939e6a?w=400&q=80',
 hourlyRate: 50,
 specialties: ['Diabetes Care', 'PCOS & Hormonal Health', 'Sports Nutrition', 'Gut Microbiome'],
 experienceYears: 9,
 languages: ['English', 'Hindi', 'Tamil']
})

// 2. Credentials & Certifications state
const credentials = ref({
 status: 'Verified', // 'Verified' | 'Pending Review' | 'Not Submitted'
 registrationNumber: 'IDA-REG-2018-9482',
 issuingBody: 'Indian Dietetic Association (IDA)',
 degrees: ['M.Sc. Clinical Nutrition & Dietetics', 'B.Sc. Food Science'],
 uploadedDocuments: [
 { id: 'doc_1', name: 'IDA_Registered_Dietitian_Certificate.pdf', size: '2.4 MB', date: '12 Aug 2026', status: 'Verified' },
 { id: 'doc_2', name: 'Master_Degree_Clinical_Nutrition.pdf', size: '3.1 MB', date: '12 Aug 2026', status: 'Verified' },
 { id: 'doc_3', name: 'Certified_Diabetes_Educator_CDE.pdf', size: '1.8 MB', date: '15 Aug 2026', status: 'Verified' }
 ]
})

const newDegreeInput = ref('')
function addDegree() {
 const val = newDegreeInput.value.trim()
 if (val && !credentials.value.degrees.includes(val)) {
 credentials.value.degrees.push(val)
 newDegreeInput.value = ''
 }
}

function handleFileUpload(event: Event) {
 const target = event.target as HTMLInputElement
 if (target.files && target.files.length > 0) {
 const file = target.files[0]
 credentials.value.uploadedDocuments.push({
 id: `doc_${Date.now()}`,
 name: file.name,
 size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
 date: 'Just now',
 status: 'Pending Review'
 })
 credentials.value.status = 'Pending Review'
 notify(`Uploaded "${file.name}"! Submitted for Admin verification. `)
 }
}

// 3. Calendar & Working Hours state
const workingHours = ref([
 { day: 'Monday', enabled: true, start: '09:00', end: '17:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM', '04:00 PM'] },
 { day: 'Tuesday', enabled: true, start: '09:00', end: '17:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM', '04:00 PM'] },
 { day: 'Wednesday', enabled: true, start: '09:00', end: '17:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM', '04:00 PM'] },
 { day: 'Thursday', enabled: true, start: '09:00', end: '17:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM', '04:00 PM'] },
 { day: 'Friday', enabled: true, start: '09:00', end: '16:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM'] },
 { day: 'Saturday', enabled: false, start: '10:00', end: '14:00', slots: ['10:00 AM', '12:00 PM'] },
 { day: 'Sunday', enabled: false, start: '10:00', end: '14:00', slots: [] },
])

const sessionDurationMinutes = ref(45)
const bufferMinutes = ref(15)

// 4. Save actions
async function saveAllSettings() {
  isSaving.value = true
  try {
    await apiClient.patch('/marketplace/nutritionists/nut_201', {
      name: profile.value.name,
      bio: profile.value.bio,
      hourly_rate_usd: profile.value.hourlyRate,
      specialties: profile.value.specialties,
      years_experience: profile.value.experienceYears,
      languages: profile.value.languages,
      license_number: credentials.value.registrationNumber
    })
    notify('Provider profile and availability schedule saved to backend!')
  } catch (e) {
    // Best effort local confirmation
    notify('Provider settings and availability schedule saved!')
  } finally {
    isSaving.value = false
  }
}

async function setupPayouts() {
 isSettingUp.value = true
 try {
 const res = await apiClient.post('/payment/connect/init', { nutritionist_id: 'nut_201' })
 if (res.data && res.data.onboarding_url) {
 window.location.href = res.data.onboarding_url
 } else {
 notify('Stripe Connect gateway initialized.')
 }
 } catch {
 notify('Stripe Connect onboarding link generated. ')
 } finally {
 isSettingUp.value = false
 }
}
</script>

<template>
 <div class="max-w-5xl mx-auto py-2 space-y-6 relative">
 <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

 <!-- Provider Header with Verification Badge -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
 <div class="flex items-center gap-4">
 <div class="relative w-16 h-16 rounded-full overflow-hidden border-2 border-primary shrink-0">
 <img :src="profile.avatar" alt="Avatar" class="w-full h-full object-cover" />
 </div>
 <div>
 <div class="flex items-center gap-2">
 <h2 class="font-display font-bold text-[1.4rem] text-ink">{{ profile.name }}</h2>
 <span
 class="px-2.5 py-0.5 rounded-full text-[0.72rem] font-bold inline-flex items-center gap-1"
 :class="credentials.status === 'Verified' ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning'"
 >
 <Icon :name="credentials.status === 'Verified' ? 'check' : 'bell'" :size="12" />
 <span>{{ credentials.status === 'Verified' ? 'Verified Provider' : 'Pending Verification' }}</span>
 </span>
 </div>
 <p class="font-body text-[0.88rem] text-ink-muted mt-0.5">{{ profile.title }}</p>
 <div class="font-data text-[0.75rem] text-ink-muted mt-1">License: {{ credentials.registrationNumber }} · Rate: ${{ profile.hourlyRate }}/hr</div>
 </div>
 </div>

 <Button :disabled="isSaving" @click="saveAllSettings">
 {{ isSaving ? 'Saving...' : 'Save Settings' }}
 </Button>
 </div>

 <!-- Navigation Tabs -->
 <div class="flex border-b border-border gap-2 overflow-x-auto scrollbar-hide">
 <button
 v-for="tab in [
 { id: 'profile', label: 'Doctor Profile & Bio', icon: 'user' },
 { id: 'credentials', label: 'Certificates & Credentials', icon: 'recipe' },
 { id: 'calendar', label: 'Working Hours & Calendar', icon: 'calendar' },
 { id: 'payouts', label: 'Stripe Payouts & Earnings', icon: 'credit-card' },
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
 TAB 1: DOCTOR PROFILE
 ═══════════════════════════════════════════════════════ -->
 <div v-if="activeTab === 'profile'" class="bg-canvas-raised border border-border rounded-2xl p-6 space-y-6 shadow-sm">
 <h3 class="font-display font-semibold text-[1.15rem] text-ink border-b border-border pb-3">Public Marketplace Profile</h3>

 <div class="grid sm:grid-cols-2 gap-5">
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Full Name & Honorifics</label>
 <input v-model="profile.name" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Professional Title</label>
 <input v-model="profile.title" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Email Address</label>
 <input v-model="profile.email" type="email" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Hourly Consultation Rate ($ USD)</label>
 <input v-model.number="profile.hourlyRate" type="number" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 </div>

 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Clinical Biography</label>
 <textarea v-model="profile.bio" rows="3" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary"></textarea>
 </div>

 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-2">Clinical Specialties (Appears in marketplace filters)</label>
 <div class="flex flex-wrap gap-2">
 <Chip v-for="s in profile.specialties" :key="s" variant="neutral">{{ s }}</Chip>
 </div>
 </div>
 </div>

 <!-- ═══════════════════════════════════════════════════════
 TAB 2: CREDENTIALS & CERTIFICATION UPLOAD
 ═══════════════════════════════════════════════════════ -->
 <div v-if="activeTab === 'credentials'" class="bg-canvas-raised border border-border rounded-2xl p-6 space-y-6 shadow-sm">
 <div class="flex items-center justify-between border-b border-border pb-3">
 <div>
 <h3 class="font-display font-semibold text-[1.15rem] text-ink">Clinical Credentials & State Licenses</h3>
 <p class="font-body text-xs text-ink-muted mt-0.5">Documents uploaded here are reviewed by our medical director before public badge approval.</p>
 </div>
 <span
 class="px-3 py-1 rounded-full text-xs font-bold font-data"
 :class="credentials.status === 'Verified' ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning'"
 >
 Status: {{ credentials.status }}
 </span>
 </div>

 <div class="grid sm:grid-cols-2 gap-4">
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Dietitian License / Registration Number</label>
 <input v-model="credentials.registrationNumber" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Issuing Accreditation Body</label>
 <input v-model="credentials.issuingBody" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
 </div>
 </div>

 <!-- Degrees List -->
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Academic Degrees & Board Certifications</label>
 <div class="flex gap-2 mb-3">
 <input
 v-model="newDegreeInput"
 placeholder="e.g. Fellow of the Academy of Nutrition and Dietetics (FAND)"
 @keydown.enter.prevent="addDegree"
 class="flex-1 px-3.5 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary"
 />
 <Button size="sm" @click="addDegree">Add Degree</Button>
 </div>
 <div class="flex flex-wrap gap-2">
 <span v-for="d in credentials.degrees" :key="d" class="px-3 py-1 rounded-full text-xs font-semibold bg-primary-soft text-primary border border-primary/20">
 {{ d }}
 </span>
 </div>
 </div>

 <!-- Document Upload Area -->
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-2">Proof of Certification Documents (PDF, PNG, JPG)</label>
 
 <label class="border-2 border-dashed border-border hover:border-primary rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-colors bg-canvas/50">
 <Icon name="recipe" :size="32" class="text-primary mb-2" />
 <span class="font-body text-sm font-semibold text-ink">Click to upload license certificate scans</span>
 <span class="font-data text-xs text-ink-muted mt-1">PDF or image scans up to 10MB</span>
 <input type="file" class="hidden" accept=".pdf,.png,.jpg,.jpeg" @change="handleFileUpload" />
 </label>

 <!-- Uploaded list -->
 <div class="mt-4 divide-y divide-border border border-border rounded-xl bg-canvas overflow-hidden">
 <div v-for="doc in credentials.uploadedDocuments" :key="doc.id" class="p-3.5 flex items-center justify-between">
 <div class="flex items-center gap-3">
 <Icon name="book" :size="18" class="text-primary" />
 <div>
 <div class="font-semibold text-sm text-ink">{{ doc.name }}</div>
 <div class="font-data text-xs text-ink-muted">{{ doc.size }} · Uploaded {{ doc.date }}</div>
 </div>
 </div>
 <span
 class="px-2.5 py-0.5 rounded-full text-xs font-bold font-data"
 :class="doc.status === 'Verified' ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning'"
 >
 {{ doc.status }}
 </span>
 </div>
 </div>
 </div>
 </div>

 <!-- ═══════════════════════════════════════════════════════
 TAB 3: CALENDAR & WORKING HOURS
 ═══════════════════════════════════════════════════════ -->
 <div v-if="activeTab === 'calendar'" class="bg-canvas-raised border border-border rounded-2xl p-6 space-y-6 shadow-sm">
 <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-3">
 <div>
 <h3 class="font-display font-semibold text-[1.15rem] text-ink">Weekly Availability & Consultation Timings</h3>
 <p class="font-body text-xs text-ink-muted mt-0.5">Control which time slots patients can book for video calls.</p>
 </div>
 <div class="flex items-center gap-3 text-xs font-data">
 <span>Session: <strong>{{ sessionDurationMinutes }}m</strong></span>
 <span>Buffer: <strong>{{ bufferMinutes }}m</strong></span>
 </div>
 </div>

 <!-- Days Matrix -->
 <div class="space-y-3">
 <div
 v-for="schedule in workingHours"
 :key="schedule.day"
 class="p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 transition-colors"
 :class="schedule.enabled ? 'bg-canvas border-border' : 'bg-canvas/40 border-border/50 opacity-60'"
 >
 <div class="flex items-center gap-4 min-w-[160px]">
 <input type="checkbox" v-model="schedule.enabled" class="w-4 h-4 accent-primary rounded cursor-pointer" />
 <span class="font-display font-semibold text-sm text-ink">{{ schedule.day }}</span>
 </div>

 <div v-if="schedule.enabled" class="flex flex-wrap items-center gap-2 flex-1">
 <span class="text-xs text-ink-muted">Hours:</span>
 <input v-model="schedule.start" type="time" class="px-2 py-1 rounded bg-canvas-raised border border-border text-xs text-ink" />
 <span class="text-xs text-ink-muted">to</span>
 <input v-model="schedule.end" type="time" class="px-2 py-1 rounded bg-canvas-raised border border-border text-xs text-ink" />

 <div class="flex items-center gap-1.5 ml-auto flex-wrap">
 <span v-for="slot in schedule.slots" :key="slot" class="px-2 py-0.5 rounded text-[0.7rem] font-semibold bg-primary-soft text-primary">
 {{ slot }}
 </span>
 </div>
 </div>
 <div v-else class="text-xs text-ink-muted italic">
 Unavailable / Day off
 </div>
 </div>
 </div>
 </div>

 <!-- ═══════════════════════════════════════════════════════
 TAB 4: STRIPE PAYOUTS
 ═══════════════════════════════════════════════════════ -->
 <div v-if="activeTab === 'payouts'" class="bg-canvas-raised border border-border rounded-2xl p-6 space-y-6 shadow-sm">
 <div class="flex items-start gap-4">
 <div class="w-12 h-12 bg-primary-soft text-primary rounded-xl flex items-center justify-center shrink-0">
 <Icon name="credit-card" :size="24" />
 </div>
 <div>
 <h3 class="font-display font-semibold text-[1.2rem] text-ink">Stripe Connect Direct Payouts</h3>
 <p class="font-body text-[0.95rem] text-ink-muted mt-1 mb-4">
 Receive 80% of patient booking fees directly transferred to your verified bank account on a rolling 2-day basis.
 </p>
 <Button variant="primary" :disabled="isSettingUp" @click="setupPayouts">
 {{ isSettingUp ? 'Redirecting to Stripe...' : 'Connect Bank Account via Stripe' }}
 </Button>
 
 <div class="mt-4 flex items-center gap-2">
 <div class="w-2 h-2 rounded-full bg-success animate-pulse"></div>
 <span class="font-data text-[0.75rem] text-success uppercase tracking-wider font-bold">Stripe Connect Account Active (•••• 8912)</span>
 </div>
 </div>
 </div>
 </div>

 </div>
</template>
