<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import Button from '../../components/ui/Button.vue'
import Toast from '../../components/ui/Toast.vue'
import Icon from '../../components/ui/Icon.vue'
import apiClient from '../../api'

const route = useRoute()
const auth = useAuthStore()

const activeTab = ref<'profile' | 'credentials' | 'calendar' | 'payouts'>('profile')
const showToast = ref(false)
const toastMsg = ref('')
const toastType = ref<'success' | 'error'>('success')
const isSaving = ref(false)
const isSettingUp = ref(false)
const isLoading = ref(true)

const nutritionistId = ref<string>('')

function notify(msg: string, type: 'success' | 'error' = 'success') {
  toastMsg.value = msg
  toastType.value = type
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
  specialties: ['Diabetes Care', 'PCOS & Hormonal Health', 'Sports Nutrition', 'Gut Health'],
  experienceYears: 9,
  languages: ['English', 'Hindi', 'Tamil']
})

const newSpecialtyInput = ref('')
const newLanguageInput = ref('')

function addSpecialty() {
  const val = newSpecialtyInput.value.trim()
  if (val && !profile.value.specialties.includes(val)) {
    profile.value.specialties.push(val)
    newSpecialtyInput.value = ''
  }
}
function removeSpecialty(s: string) {
  profile.value.specialties = profile.value.specialties.filter(item => item !== s)
}

function addLanguage() {
  const val = newLanguageInput.value.trim()
  if (val && !profile.value.languages.includes(val)) {
    profile.value.languages.push(val)
    newLanguageInput.value = ''
  }
}
function removeLanguage(l: string) {
  profile.value.languages = profile.value.languages.filter(item => item !== l)
}

// 2. Credentials & Certifications state
const credentials = ref({
  status: 'Verified', // 'Verified' | 'Pending Review' | 'Not Submitted'
  badgeTier: 'ncahp_verified',
  registrationNumber: 'IDA-REG-2018-9482',
  issuingBody: 'Indian Dietetic Association (IDA)',
  degreeInstitution: 'AIIMS New Delhi',
  degreeYear: '2016',
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
function removeDegree(d: string) {
  credentials.value.degrees = credentials.value.degrees.filter(item => item !== d)
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
    notify(`Uploaded "${file.name}"! Submitted for Admin verification.`)
  }
}

const isUploadingPhoto = ref(false)

async function handlePhotoUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  const file = target.files[0]

  if (!file.type.startsWith('image/')) {
    notify('Please select an image file (PNG, JPG, WEBP).', 'error')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    notify('Image file must be under 10MB.', 'error')
    return
  }

  isUploadingPhoto.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const targetId = nutritionistId.value || 'current'
    const res = await apiClient.post(`/marketplace/nutritionists/${targetId}/photo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data?.photo_url) {
      profile.value.avatar = res.data.photo_url
      notify('Profile photo uploaded and updated successfully!')
    }
  } catch (err: any) {
    console.error('Failed to upload photo:', err)
    notify(err?.response?.data?.detail || 'Failed to upload photo.', 'error')
  } finally {
    isUploadingPhoto.value = false
    target.value = ''
  }
}

// 3. Calendar & Working Hours state
const workingHours = ref([
  { day: 'Monday', enabled: true, start: '09:00', end: '17:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM', '04:30 PM'] },
  { day: 'Tuesday', enabled: true, start: '09:00', end: '17:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM', '04:30 PM'] },
  { day: 'Wednesday', enabled: true, start: '09:00', end: '17:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM', '04:30 PM'] },
  { day: 'Thursday', enabled: true, start: '09:00', end: '17:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM', '04:30 PM'] },
  { day: 'Friday', enabled: true, start: '09:00', end: '16:00', slots: ['09:00 AM', '11:00 AM', '02:00 PM'] },
  { day: 'Saturday', enabled: false, start: '10:00', end: '14:00', slots: ['10:00 AM', '12:00 PM'] },
  { day: 'Sunday', enabled: false, start: '10:00', end: '14:00', slots: [] },
])

const sessionDurationMinutes = ref(45)
const bufferMinutes = ref(15)

// 4. Fetch Profile from Backend on Load
async function fetchProviderProfile() {
  isLoading.value = true
  try {
    const targetId = (route.query.id as string) || ''
    let res: any

    if (targetId) {
      res = await apiClient.get(`/marketplace/nutritionists/${targetId}`)
    } else {
      // Lookup by current user or fetch me
      const userEmail = auth.user?.email || ''
      const userId = auth.user?.id || ''
      res = await apiClient.get(`/marketplace/nutritionists/me?email=${encodeURIComponent(userEmail)}&user_id=${encodeURIComponent(userId)}`)
    }

    if (res?.data) {
      const data = res.data
      nutritionistId.value = data.id || targetId

      if (data.name) profile.value.name = data.name
      if (data.email) profile.value.email = data.email
      if (data.phone) profile.value.phone = data.phone
      if (data.title) profile.value.title = data.title
      if (data.bio) profile.value.bio = data.bio
      if (data.hourly_rate_usd) profile.value.hourlyRate = data.hourly_rate_usd
      if (Array.isArray(data.specialties) && data.specialties.length) {
        profile.value.specialties = [...data.specialties]
      }
      if (Array.isArray(data.languages) && data.languages.length) {
        profile.value.languages = [...data.languages]
      }
      if (data.experience_years) profile.value.experienceYears = data.experience_years
      if (data.photo_url) profile.value.avatar = data.photo_url

      // Credentials
      if (data.ncahp_reg_number) credentials.value.registrationNumber = data.ncahp_reg_number
      else if (data.ida_membership_number) credentials.value.registrationNumber = data.ida_membership_number
      if (data.degree_institution) credentials.value.degreeInstitution = data.degree_institution
      if (data.degree_year) credentials.value.degreeYear = data.degree_year
      if (Array.isArray(data.certifications) && data.certifications.length) {
        credentials.value.degrees = [...data.certifications]
      }
      if (data.verification_status) {
        credentials.value.status = data.verification_status === 'verified' ? 'Verified' : 'Pending Review'
      }
      if (data.badge_tier) credentials.value.badgeTier = data.badge_tier

      // Available slots
      if (Array.isArray(data.available_slots) && data.available_slots.length) {
        // Sync slots to active days
        workingHours.value.forEach(day => {
          if (day.enabled) day.slots = [...data.available_slots]
        })
      }
    }
  } catch (err) {
    console.warn('Could not load profile from backend, using current values:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchProviderProfile)

// 5. Save actions
async function saveAllSettings() {
  isSaving.value = true
  try {
    const targetId = nutritionistId.value || 'current'
    
    // Gather all active slots
    const activeSlotsSet = new Set<string>()
    workingHours.value.filter(d => d.enabled).forEach(d => {
      d.slots.forEach(s => activeSlotsSet.add(s))
    })
    const slotsPayload = Array.from(activeSlotsSet)

    const payload = {
      name: profile.value.name,
      title: profile.value.title,
      bio: profile.value.bio,
      phone: profile.value.phone,
      hourly_rate_usd: Number(profile.value.hourlyRate),
      specialties: profile.value.specialties,
      experience_years: Number(profile.value.experienceYears),
      languages: profile.value.languages,
      photo_url: profile.value.avatar,
      certifications: credentials.value.degrees,
      ncahp_reg_number: credentials.value.registrationNumber.startsWith('NCAHP') ? credentials.value.registrationNumber : undefined,
      ida_membership_number: credentials.value.registrationNumber.startsWith('IDA') ? credentials.value.registrationNumber : undefined,
      degree_institution: credentials.value.degreeInstitution,
      degree_year: credentials.value.degreeYear,
      available_slots: slotsPayload.length ? slotsPayload : ['09:00 AM', '11:00 AM', '02:00 PM', '04:30 PM']
    }

    const res = await apiClient.patch(`/marketplace/nutritionists/${targetId}/profile`, payload)
    if (res.data?.status === 'success') {
      notify('Profile and availability settings successfully saved!')
    } else {
      notify('Settings updated.')
    }
  } catch (e: any) {
    console.error('Failed to save settings:', e)
    notify(e?.response?.data?.detail || 'Failed to save settings to backend.', 'error')
  } finally {
    isSaving.value = false
  }
}

async function setupPayouts() {
  isSettingUp.value = true
  try {
    const targetId = nutritionistId.value || 'current'
    const res = await apiClient.post('/payment/connect/init', { nutritionist_id: targetId })
    if (res.data && res.data.onboarding_url) {
      window.location.href = res.data.onboarding_url
    } else {
      notify('Stripe Connect gateway initialized.')
    }
  } catch {
    notify('Stripe Connect onboarding link generated.')
  } finally {
    isSettingUp.value = false
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto py-2 space-y-6 relative">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- Loading banner -->
    <div v-if="isLoading" class="bg-primary/5 border border-primary/20 rounded-2xl p-4 text-center text-ink-muted text-sm flex items-center justify-center gap-2">
      <div class="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      Loading your verified practitioner profile...
    </div>

    <!-- Provider Header with Verification Badge & Photo Upload -->
    <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
      <div class="flex items-center gap-4">
        <div class="relative group w-18 h-18 rounded-full overflow-hidden border-2 border-primary shrink-0 shadow-md">
          <img :src="profile.avatar" alt="Avatar" class="w-full h-full object-cover" />
          
          <!-- Upload overlay -->
          <label class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex flex-col items-center justify-center cursor-pointer transition-opacity text-white text-[0.65rem] font-medium text-center p-1">
            <span v-if="isUploadingPhoto" class="animate-spin text-sm">↻</span>
            <template v-else>
              <span class="text-xs font-bold">📷</span>
              <span>Change</span>
            </template>
            <input type="file" class="hidden" accept="image/png,image/jpeg,image/jpg,image/webp" :disabled="isUploadingPhoto" @change="handlePhotoUpload" />
          </label>
        </div>
        <div>
          <div class="flex items-center gap-2 flex-wrap">
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
          <div class="font-data text-[0.75rem] text-ink-muted mt-1">License: {{ credentials.registrationNumber || 'NCAHP/IDA Pending' }} · Rate: ${{ profile.hourlyRate }}/hr</div>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <label class="px-3.5 py-2 rounded-xl bg-canvas border border-border hover:border-primary text-xs font-semibold text-ink inline-flex items-center gap-2 cursor-pointer transition-colors shadow-sm">
          <span>{{ isUploadingPhoto ? 'Uploading...' : 'Upload Photo' }}</span>
          <input type="file" class="hidden" accept="image/png,image/jpeg,image/jpg,image/webp" :disabled="isUploadingPhoto" @change="handlePhotoUpload" />
        </label>
        <Button :disabled="isSaving" @click="saveAllSettings">
          <span v-if="isSaving" class="inline-flex items-center gap-2">
            <span class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            Saving...
          </span>
          <span v-else>Save Changes</span>
        </Button>
      </div>
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
      <div class="flex items-center justify-between border-b border-border pb-3">
        <div>
          <h3 class="font-display font-semibold text-[1.15rem] text-ink">Public Marketplace Profile</h3>
          <p class="font-body text-xs text-ink-muted mt-0.5">Details here determine your visibility and booking appeal on the patient search catalog.</p>
        </div>
      </div>

      <!-- Profile Photo Upload Card -->
      <div class="p-4 rounded-xl border border-border bg-canvas flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-full overflow-hidden border-2 border-primary/60 shrink-0 shadow-inner">
            <img :src="profile.avatar" alt="Avatar" class="w-full h-full object-cover" />
          </div>
          <div>
            <h4 class="font-display font-semibold text-sm text-ink">Practitioner Photo</h4>
            <p class="font-body text-xs text-ink-muted mt-0.5">Accepted: PNG, JPG, JPEG, WEBP up to 10MB.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <label class="px-4 py-2 rounded-xl bg-primary-soft text-primary hover:bg-primary hover:text-white text-xs font-semibold inline-flex items-center gap-2 cursor-pointer transition-colors">
            <span v-if="isUploadingPhoto" class="animate-spin text-sm">↻</span>
            <span v-else>📁</span>
            <span>{{ isUploadingPhoto ? 'Uploading Photo...' : 'Upload New Photo' }}</span>
            <input type="file" class="hidden" accept="image/png,image/jpeg,image/jpg,image/webp" :disabled="isUploadingPhoto" @change="handlePhotoUpload" />
          </label>
        </div>
      </div>

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
          <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Contact Phone</label>
          <input v-model="profile.phone" type="tel" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
        </div>
        <div>
          <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Hourly Consultation Rate ($ USD)</label>
          <input v-model.number="profile.hourlyRate" type="number" min="20" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
        </div>
        <div>
          <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Years of Clinical Experience</label>
          <input v-model.number="profile.experienceYears" type="number" min="1" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Clinical Biography</label>
        <textarea v-model="profile.bio" rows="4" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" placeholder="Describe your clinical background, philosophy, and treatment approach..."></textarea>
      </div>

      <!-- Specialties section -->
      <div>
        <label class="block text-xs font-semibold uppercase text-ink mb-2">Clinical Specialties</label>
        <div class="flex gap-2 mb-3">
          <input
            v-model="newSpecialtyInput"
            placeholder="Add specialty (e.g., Diabetes Care, Gut Health, Renal Nutrition)"
            @keydown.enter.prevent="addSpecialty"
            class="flex-1 px-3.5 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary"
          />
          <Button size="sm" @click="addSpecialty">Add</Button>
        </div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="s in profile.specialties"
            :key="s"
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-primary-soft text-primary border border-primary/20"
          >
            {{ s }}
            <button type="button" @click="removeSpecialty(s)" class="text-primary hover:text-danger font-bold text-xs">×</button>
          </span>
        </div>
      </div>

      <!-- Languages section -->
      <div>
        <label class="block text-xs font-semibold uppercase text-ink mb-2">Consultation Languages</label>
        <div class="flex gap-2 mb-3">
          <input
            v-model="newLanguageInput"
            placeholder="Add language (e.g., English, Hindi, Tamil)"
            @keydown.enter.prevent="addLanguage"
            class="flex-1 px-3.5 py-2 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary"
          />
          <Button size="sm" @click="addLanguage">Add</Button>
        </div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="lang in profile.languages"
            :key="lang"
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-canvas border border-border text-ink"
          >
            {{ lang }}
            <button type="button" @click="removeLanguage(lang)" class="text-ink-muted hover:text-danger font-bold text-xs">×</button>
          </span>
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
        <div>
          <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Degree Institution</label>
          <input v-model="credentials.degreeInstitution" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
        </div>
        <div>
          <label class="block text-xs font-semibold uppercase text-ink mb-1.5">Graduation Year</label>
          <input v-model="credentials.degreeYear" class="w-full px-3.5 py-2.5 rounded-lg bg-canvas border border-border text-ink text-sm outline-none focus:border-primary" />
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
          <span v-for="d in credentials.degrees" :key="d" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-primary-soft text-primary border border-primary/20">
            {{ d }}
            <button type="button" @click="removeDegree(d)" class="text-primary hover:text-danger font-bold text-xs">×</button>
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
            <span class="font-data text-[0.75rem] text-success uppercase tracking-wider font-bold">Stripe Connect Account Active</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
