<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apiClient from '../../api'

const router = useRouter()
const route = useRoute()

const nutritionistId = ref((route.query.id as string) || '')

// ── Step management ────────────────────────────────────────────────────────
const currentStep = ref(1)
const TOTAL_STEPS = 4
const isSubmitting = ref(false)
const errorMsg = ref('')
const showSuccess = ref(false)

const stepProgress = computed(() => ((currentStep.value - 1) / TOTAL_STEPS) * 100)

function nextStep() {
  if (!validateCurrentStep()) return
  if (currentStep.value < TOTAL_STEPS) currentStep.value++
}
function prevStep() {
  if (currentStep.value > 1) currentStep.value--
}

// ── Step 1: Personal Info ──────────────────────────────────────────────────
const personal = ref({ name: '', title: '', phone: '', languages: [] as string[] })
const langInput = ref('')
const langOptions = ['English', 'Hindi', 'Tamil', 'Telugu', 'Kannada', 'Malayalam', 'Bengali', 'Marathi', 'Gujarati']

function addLanguage(lang: string) {
  if (lang && !personal.value.languages.includes(lang)) personal.value.languages.push(lang)
  langInput.value = ''
}
function removeLanguage(lang: string) {
  personal.value.languages = personal.value.languages.filter(l => l !== lang)
}

// ── Step 2: Professional Profile ──────────────────────────────────────────
const professional = ref({
  bio: '', photo_url: '', experience_years: '',
  specialties: [] as string[], consultation_modes: [] as string[],
})
const specialtyInput = ref('')
const specialtyOptions = [
  'Clinical Nutrition', 'Diabetes Care', 'PCOS & Hormonal Health', 'Sports Nutrition',
  'Gut Health', 'Weight Management', 'Paediatric Nutrition', 'Oncology Nutrition',
  'Renal Diet', 'Cardiovascular Health', 'Eating Disorders', 'Prenatal Nutrition',
]

function addSpecialty(s: string) {
  if (s && !professional.value.specialties.includes(s)) professional.value.specialties.push(s)
  specialtyInput.value = ''
}
function removeSpecialty(s: string) {
  professional.value.specialties = professional.value.specialties.filter(x => x !== s)
}
function toggleMode(mode: string) {
  const arr = professional.value.consultation_modes
  const idx = arr.indexOf(mode)
  if (idx > -1) arr.splice(idx, 1); else arr.push(mode)
}

const isUploadingPhoto = ref(false)

async function handlePhotoUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  const file = target.files[0]

  if (!file.type.startsWith('image/')) {
    errorMsg.value = 'Please select an image file (PNG, JPG, WEBP).'
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    errorMsg.value = 'Image file must be under 10MB.'
    return
  }

  isUploadingPhoto.value = true
  errorMsg.value = ''
  const formData = new FormData()
  formData.append('file', file)

  try {
    const targetId = nutritionistId.value || 'current'
    const res = await apiClient.post(`/marketplace/nutritionists/${targetId}/photo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data?.photo_url) {
      professional.value.photo_url = res.data.photo_url
    }
  } catch (err: any) {
    console.error('Failed to upload photo:', err)
    errorMsg.value = err?.response?.data?.detail || 'Failed to upload photo.'
  } finally {
    isUploadingPhoto.value = false
    target.value = ''
  }
}

// ── Step 3: Credentials ───────────────────────────────────────────────────
const credentials = ref({
  ncahp_reg_number: '', ida_membership_number: '',
  degree_institution: '', degree_year: '', certifications: [] as string[],
})
const certInput = ref('')

function addCertification() {
  const val = certInput.value.trim()
  if (val && !credentials.value.certifications.includes(val)) {
    credentials.value.certifications.push(val); certInput.value = ''
  }
}
function removeCert(c: string) {
  credentials.value.certifications = credentials.value.certifications.filter(x => x !== c)
}

// ── Step 4: Availability & Rate ───────────────────────────────────────────
const availability = ref({ hourly_rate_usd: '', available_slots: [] as string[] })
const ALL_SLOTS = [
  '07:00 AM', '08:00 AM', '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
  '01:00 PM', '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM', '06:00 PM', '07:00 PM', '08:00 PM',
]
function toggleSlot(slot: string) {
  const arr = availability.value.available_slots
  const idx = arr.indexOf(slot)
  if (idx > -1) arr.splice(idx, 1); else arr.push(slot)
}

// ── Validation ─────────────────────────────────────────────────────────────
function validateCurrentStep(): boolean {
  errorMsg.value = ''
  if (currentStep.value === 1) {
    if (!personal.value.name.trim()) { errorMsg.value = 'Full name is required.'; return false }
    if (!personal.value.title.trim()) { errorMsg.value = 'Professional title is required.'; return false }
  }
  if (currentStep.value === 2) {
    if (professional.value.bio.trim().length < 40) { errorMsg.value = 'Bio must be at least 40 characters.'; return false }
    if (!professional.value.specialties.length) { errorMsg.value = 'Add at least one specialty.'; return false }
    if (!professional.value.consultation_modes.length) { errorMsg.value = 'Select at least one consultation mode.'; return false }
  }
  if (currentStep.value === 4) {
    const rate = parseFloat(availability.value.hourly_rate_usd)
    if (!rate || rate < 5) { errorMsg.value = 'Enter a valid hourly rate (minimum ₹5).'; return false }
    if (!availability.value.available_slots.length) { errorMsg.value = 'Select at least one time slot.'; return false }
  }
  return true
}

// ── Submit ─────────────────────────────────────────────────────────────────
async function handleSubmit() {
  if (!validateCurrentStep()) return
  isSubmitting.value = true
  errorMsg.value = ''
  const payload = {
    ...personal.value,
    ...professional.value,
    experience_years: professional.value.experience_years ? parseInt(professional.value.experience_years) : undefined,
    ...credentials.value,
    hourly_rate_usd: parseFloat(availability.value.hourly_rate_usd),
    available_slots: availability.value.available_slots,
  }
  try {
    const targetId = nutritionistId.value || 'placeholder'
    await apiClient.patch(`/marketplace/nutritionists/${targetId}/profile`, payload)
    showSuccess.value = true
    setTimeout(() => router.push('/expert/dashboard'), 2500)
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to save profile. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}

const steps = [
  { num: 1, label: 'Personal Info' },
  { num: 2, label: 'Professional' },
  { num: 3, label: 'Credentials' },
  { num: 4, label: 'Availability' },
]
</script>

<template>
  <div class="min-h-screen bg-[#0a0c10] flex flex-col items-center justify-start py-10 px-4">

    <!-- Success -->
    <div v-if="showSuccess" class="flex flex-col items-center justify-center min-h-screen gap-6 text-center">
      <div class="w-20 h-20 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
        <svg class="w-10 h-10 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </div>
      <h2 class="text-2xl font-bold text-white">Profile Complete!</h2>
      <p class="text-sm text-white/50 max-w-xs">Your clinical profile is live. Taking you to your Provider Portal…</p>
    </div>

    <template v-else>
      <!-- Logo -->
      <div class="flex items-center gap-2 mb-8">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center shadow-lg shadow-teal-500/30">
          <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <polyline points="9 12 11 14 15 10"/>
          </svg>
        </div>
        <span class="font-bold text-lg text-white tracking-tight">NutriPlan Clinical</span>
      </div>

      <div class="w-full max-w-2xl">
        <div class="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl overflow-hidden">

          <!-- Progress Bar -->
          <div class="h-1 bg-white/5">
            <div class="h-1 bg-gradient-to-r from-teal-400 to-emerald-400 transition-all duration-500" :style="{ width: stepProgress + '%' }" />
          </div>

          <!-- Step Tabs -->
          <div class="flex border-b border-white/10">
            <button
              v-for="s in steps" :key="s.num"
              class="flex-1 flex flex-col items-center gap-1 py-4 px-2 text-xs font-medium transition-colors"
              :class="currentStep === s.num ? 'text-teal-400' : currentStep > s.num ? 'text-emerald-500' : 'text-white/30'"
              @click="currentStep > s.num && (currentStep = s.num)"
            >
              <div class="w-7 h-7 rounded-full flex items-center justify-center transition-all"
                :class="currentStep === s.num ? 'bg-teal-500/20 border border-teal-400/60' : currentStep > s.num ? 'bg-emerald-500/20 border border-emerald-400/60' : 'bg-white/5 border border-white/10'">
                <svg v-if="currentStep > s.num" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                <span v-else class="text-[0.65rem] font-bold">{{ s.num }}</span>
              </div>
              <span class="hidden sm:block">{{ s.label }}</span>
            </button>
          </div>

          <!-- Content -->
          <div class="p-8">
            <div v-if="errorMsg" class="mb-5 p-3 bg-red-500/10 border border-red-500/25 rounded-xl text-xs text-red-400 font-medium">
              {{ errorMsg }}
            </div>

            <!-- STEP 1 -->
            <div v-if="currentStep === 1" class="space-y-5">
              <div>
                <h2 class="text-xl font-bold text-white">Welcome to the Provider Network</h2>
                <p class="text-sm text-white/40 mt-1">Let's start with your name and how patients will identify you.</p>
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">Full Name *</label>
                <input v-model="personal.name" type="text" placeholder="Dr. Ananya Iyer"
                  class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">Professional Title *</label>
                <input v-model="personal.title" type="text" placeholder="Senior Clinical Dietitian & Diabetes Specialist"
                  class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">Phone Number</label>
                <input v-model="personal.phone" type="tel" placeholder="+91 98765 43210"
                  class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">Languages Spoken</label>
                <div class="flex flex-wrap gap-2 mb-3">
                  <span v-for="lang in personal.languages" :key="lang"
                    class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-teal-500/15 border border-teal-500/30 text-teal-300 text-xs font-medium">
                    {{ lang }}
                    <button @click="removeLanguage(lang)" class="hover:text-red-400 transition">
                      <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                  </span>
                </div>
                <select v-model="langInput" class="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:border-teal-400/60 transition"
                  @change="addLanguage(langInput)">
                  <option value="" class="bg-[#1a1d24]">Select a language…</option>
                  <option v-for="l in langOptions" :key="l" :value="l" class="bg-[#1a1d24]">{{ l }}</option>
                </select>
              </div>
            </div>

            <!-- STEP 2 -->
            <div v-else-if="currentStep === 2" class="space-y-5">
              <div>
                <h2 class="text-xl font-bold text-white">Professional Profile</h2>
                <p class="text-sm text-white/40 mt-1">This is what patients see when they discover your profile in the marketplace.</p>
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">Profile Photo</label>
                
                <div class="flex flex-col sm:flex-row items-center gap-4 p-4 rounded-2xl bg-white/5 border border-white/10">
                  <div class="w-16 h-16 rounded-2xl overflow-hidden bg-white/10 border border-white/20 shrink-0 flex items-center justify-center">
                    <img v-if="professional.photo_url" :src="professional.photo_url" class="w-full h-full object-cover" alt="Avatar" />
                    <span v-else class="text-2xl">👤</span>
                  </div>
                  <div class="flex-1 space-y-2 w-full">
                    <div class="flex items-center gap-2">
                      <label class="px-4 py-2 rounded-xl bg-teal-500/20 border border-teal-400/40 text-teal-300 hover:bg-teal-500/30 text-xs font-semibold inline-flex items-center gap-2 cursor-pointer transition">
                        <span v-if="isUploadingPhoto" class="animate-spin text-sm">↻</span>
                        <span v-else>📷</span>
                        <span>{{ isUploadingPhoto ? 'Uploading...' : 'Upload Image File' }}</span>
                        <input type="file" class="hidden" accept="image/png,image/jpeg,image/jpg,image/webp" :disabled="isUploadingPhoto" @change="handlePhotoUpload" />
                      </label>
                      <span class="text-xs text-white/30">or enter image URL below</span>
                    </div>
                    <input v-model="professional.photo_url" type="url" placeholder="https://…/your-photo.jpg"
                      class="w-full px-3 py-2 rounded-xl bg-black/20 border border-white/10 text-white text-xs placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
                  </div>
                </div>
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">Professional Bio * <span class="text-white/20 font-normal">(min 40 chars)</span></label>
                <textarea v-model="professional.bio" rows="4" placeholder="Describe your clinical approach, areas of expertise, and what patients can expect…"
                  class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition resize-none" />
                <div class="text-right text-xs mt-1" :class="professional.bio.length >= 40 ? 'text-emerald-400' : 'text-white/30'">{{ professional.bio.length }} / 40+</div>
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">Years of Experience</label>
                <input v-model="professional.experience_years" type="number" min="0" max="50" placeholder="e.g. 9"
                  class="w-40 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">Specialties * <span class="text-white/20 font-normal">(at least one)</span></label>
                <div class="flex flex-wrap gap-2 mb-3">
                  <button v-for="s in specialtyOptions" :key="s" type="button"
                    class="px-3 py-1.5 rounded-full text-xs font-medium border transition"
                    :class="professional.specialties.includes(s) ? 'bg-teal-500/20 border-teal-400/60 text-teal-300' : 'bg-white/5 border-white/10 text-white/50 hover:border-white/25'"
                    @click="professional.specialties.includes(s) ? removeSpecialty(s) : addSpecialty(s)">{{ s }}</button>
                </div>
                <input v-model="specialtyInput" type="text" placeholder="Add custom specialty…"
                  class="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition"
                  @keydown.enter.prevent="addSpecialty(specialtyInput)" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">Consultation Modes *</label>
                <div class="flex gap-3">
                  <button v-for="mode in ['video', 'in_person', 'chat']" :key="mode" type="button"
                    class="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl border text-xs font-medium transition"
                    :class="professional.consultation_modes.includes(mode) ? 'bg-teal-500/15 border-teal-400/60 text-teal-300' : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'"
                    @click="toggleMode(mode)">
                    <svg v-if="mode === 'video'" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
                    <svg v-else-if="mode === 'in_person'" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
                    <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                    {{ mode === 'in_person' ? 'In-Person' : mode === 'video' ? 'Video Call' : 'Text Chat' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- STEP 3 -->
            <div v-else-if="currentStep === 3" class="space-y-5">
              <div>
                <h2 class="text-xl font-bold text-white">Credentials & Certifications</h2>
                <p class="text-sm text-white/40 mt-1">Displayed as trust signals. Skip any that don't apply.</p>
              </div>
              <div class="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 text-xs text-emerald-300/80 leading-relaxed">
                <strong class="block text-emerald-400 mb-1">Pre-Verified by NutriPlan Ops</strong>
                Your NCAHP/IDA credentials have been pre-checked. Providing registration numbers ensures accurate badge display.
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">NCAHP Reg. Number</label>
                  <input v-model="credentials.ncahp_reg_number" type="text" placeholder="NCAHP-2023-XXXXX"
                    class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
                </div>
                <div>
                  <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">IDA Membership No.</label>
                  <input v-model="credentials.ida_membership_number" type="text" placeholder="IDA-REG-XXXX-XXXX"
                    class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
                </div>
                <div>
                  <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">Degree Institution</label>
                  <input v-model="credentials.degree_institution" type="text" placeholder="AIIMS New Delhi"
                    class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
                </div>
                <div>
                  <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">Graduation Year</label>
                  <input v-model="credentials.degree_year" type="text" placeholder="2017"
                    class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
                </div>
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">Additional Certifications</label>
                <div class="flex flex-wrap gap-2 mb-3">
                  <span v-for="c in credentials.certifications" :key="c"
                    class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-teal-500/15 border border-teal-500/30 text-teal-300 text-xs font-medium">
                    {{ c }}
                    <button @click="removeCert(c)" class="hover:text-red-400 transition">
                      <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                  </span>
                </div>
                <div class="flex gap-2">
                  <input v-model="certInput" type="text" placeholder="e.g. Certified Diabetes Educator (CDE)"
                    class="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition"
                    @keydown.enter.prevent="addCertification" />
                  <button type="button" class="px-4 py-2.5 rounded-xl bg-teal-500/15 border border-teal-500/30 text-teal-300 text-xs font-semibold hover:bg-teal-500/25 transition" @click="addCertification">Add</button>
                </div>
              </div>
            </div>

            <!-- STEP 4 -->
            <div v-else-if="currentStep === 4" class="space-y-5">
              <div>
                <h2 class="text-xl font-bold text-white">Availability & Rate</h2>
                <p class="text-sm text-white/40 mt-1">Set your consultation rate and available time slots.</p>
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1.5">Hourly Rate (₹) *</label>
                <div class="relative w-52">
                  <span class="absolute left-4 top-1/2 -translate-y-1/2 text-white/30 text-sm font-semibold">₹</span>
                  <input v-model="availability.hourly_rate_usd" type="number" min="5" placeholder="1500"
                    class="w-full pl-8 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/20 focus:outline-none focus:border-teal-400/60 transition" />
                </div>
              </div>
              <div>
                <label class="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">Available Time Slots * <span class="text-white/20 font-normal">({{ availability.available_slots.length }} selected)</span></label>
                <div class="grid grid-cols-4 sm:grid-cols-5 gap-2">
                  <button v-for="slot in ALL_SLOTS" :key="slot" type="button"
                    class="py-2.5 px-1 rounded-xl border text-xs font-medium transition text-center"
                    :class="availability.available_slots.includes(slot) ? 'bg-teal-500/20 border-teal-400/60 text-teal-300' : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'"
                    @click="toggleSlot(slot)">{{ slot }}</button>
                </div>
              </div>
              <!-- Profile Preview -->
              <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
                <div class="text-xs font-semibold text-white/30 uppercase tracking-wider mb-3">Profile Preview</div>
                <div class="flex items-start gap-4">
                  <img v-if="professional.photo_url" :src="professional.photo_url"
                    class="w-14 h-14 rounded-2xl object-cover border border-white/10 flex-shrink-0" alt="" />
                  <div v-else class="w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-500/30 to-emerald-500/30 border border-teal-500/20 flex items-center justify-center flex-shrink-0">
                    <svg class="w-6 h-6 text-teal-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="font-bold text-white text-sm">{{ personal.name || 'Your Name' }}</div>
                    <div class="text-xs text-white/40 mt-0.5">{{ personal.title || 'Your Title' }}</div>
                    <div class="flex flex-wrap gap-1.5 mt-2">
                      <span v-for="s in professional.specialties.slice(0,3)" :key="s"
                        class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-300 text-[0.65rem] font-medium">{{ s }}</span>
                      <span v-if="professional.specialties.length > 3" class="text-xs text-white/25">+{{ professional.specialties.length - 3 }} more</span>
                    </div>
                    <div class="mt-2 flex items-center gap-3 text-xs text-white/40">
                      <span v-if="availability.hourly_rate_usd">₹{{ availability.hourly_rate_usd }}/hr</span>
                      <span>{{ availability.available_slots.length }} slots</span>
                      <span v-if="professional.experience_years">{{ professional.experience_years }} yrs exp</span>
                    </div>
                  </div>
                </div>
                <p v-if="professional.bio" class="text-xs text-white/40 mt-3 line-clamp-2 leading-relaxed">{{ professional.bio }}</p>
              </div>
            </div>

            <!-- Navigation -->
            <div class="flex items-center justify-between mt-8 pt-6 border-t border-white/10">
              <button v-if="currentStep > 1" type="button"
                class="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-white/10 bg-white/5 text-white/60 text-sm font-medium hover:bg-white/10 hover:text-white transition"
                @click="prevStep">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
                Back
              </button>
              <div v-else />

              <button v-if="currentStep < TOTAL_STEPS" type="button"
                class="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 text-white text-sm font-semibold shadow-lg shadow-teal-500/30 hover:opacity-90 transition"
                @click="nextStep">
                Continue
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
              </button>
              <button v-else type="button" :disabled="isSubmitting"
                class="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 text-white text-sm font-semibold shadow-lg shadow-teal-500/30 hover:opacity-90 transition disabled:opacity-50"
                @click="handleSubmit">
                <svg v-if="isSubmitting" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
                {{ isSubmitting ? 'Saving Profile…' : 'Launch My Profile →' }}
              </button>
            </div>
          </div>
        </div>
        <p class="text-center text-xs text-white/20 mt-4">Step {{ currentStep }} of {{ TOTAL_STEPS }}</p>
      </div>
    </template>
  </div>
</template>
