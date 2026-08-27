<script setup lang="ts">
import { ref, computed } from 'vue'
import Button from '../../components/ui/Button.vue'
import Modal from '../../components/ui/Modal.vue'
import Toast from '../../components/ui/Toast.vue'
import Icon from '../../components/ui/Icon.vue'

import { onMounted } from 'vue'
import apiClient from '../../api'

const showToast = ref(false)
const toastMsg = ref('')
const showReviewModal = ref(false)
const selectedExpert = ref<any>(null)
const filterStatus = ref<'all' | 'pending' | 'approved'>('all')
const isLoading = ref(false)

function notify(msg: string) {
 toastMsg.value = msg
 showToast.value = true
 setTimeout(() => { showToast.value = false }, 3500)
}

const experts = ref<any[]>([])

async function fetchNutritionists() {
 isLoading.value = true
 try {
 const res = await apiClient.get('/marketplace/nutritionists/search')
 if (res.data && Array.isArray(res.data) && res.data.length > 0) {
 experts.value = res.data.map((n: any) => ({
 id: n.id,
 name: n.name,
 spec: (n.specialties || []).join(', '),
 rate: n.hourly_rate_usd || 80,
 status: n.stripe_account_id ? 'Approved' : 'Pending Review',
 verifiedBadge: (n.rating || 5.0) >= 4.8,
 licenseNo: (n.certifications || [])[0] || 'IDA-REG-2026-VERIFIED',
 issuingBody: (n.certifications || [])[1] || 'Indian Dietetic Association (IDA)',
 experienceYears: 7,
 docs: [
 { name: `${n.name.replace(/[^a-zA-Z]/g, '_')}_Certification.pdf`, size: '2.1 MB', date: '12 Aug 2026' }
 ],
 connect: n.stripe_account_id ? 'Active' : 'Pending Onboarding',
 appliedDate: '12 Aug 2026'
 }))
 }
 } catch (err) {
 console.error('Failed to load experts from marketplace API:', err)
 } finally {
 isLoading.value = false
 }
}

onMounted(() => {
 fetchNutritionists()
})

const filteredExperts = computed(() => {
 if (filterStatus.value === 'pending') return experts.value.filter(e => e.status === 'Pending Review')
 if (filterStatus.value === 'approved') return experts.value.filter(e => e.status === 'Approved')
 return experts.value
})

const pendingCount = computed(() => experts.value.filter(e => e.status === 'Pending Review').length)

// Pagination
const currentPage = ref(1)
const pageSize = 8

const totalPages = computed(() => Math.max(1, Math.ceil(filteredExperts.value.length / pageSize)))
const paginatedExperts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredExperts.value.slice(start, start + pageSize)
})

const rangeStart = computed(() => Math.min((currentPage.value - 1) * pageSize + 1, filteredExperts.value.length))
const rangeEnd = computed(() => Math.min(currentPage.value * pageSize, filteredExperts.value.length))


function openReview(expert: any) {
 selectedExpert.value = expert
 showReviewModal.value = true
}

function approveExpert(expert: any) {
 expert.status = 'Approved'
 expert.verifiedBadge = true
 showReviewModal.value = false
 notify(`Approved credentials & granted Verified Badge to ${expert.name}! ✓`)
}

function revokeVerification(expert: any) {
 expert.status = 'Pending Review'
 expert.verifiedBadge = false
 showReviewModal.value = false
 notify(`Revoked verification for ${expert.name}. Status set to Pending Review.`)
}
</script>

<template>
 <div class="space-y-6">
 <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

 <!-- Credential Inspection & Verification Modal -->
 <Modal v-model="showReviewModal" :title="`Review Credentials: ${selectedExpert?.name}`" size="lg">
 <div v-if="selectedExpert" class="space-y-5">
 <!-- Summary Strip -->
 <div class="p-4 rounded-xl bg-canvas border border-border flex items-center justify-between">
 <div>
 <h3 class="font-display font-bold text-[1.1rem] text-ink">{{ selectedExpert.name }}</h3>
 <p class="font-body text-xs text-ink-muted">{{ selectedExpert.spec }} · {{ selectedExpert.experienceYears }} Years Experience</p>
 </div>
 <span
 class="px-3 py-1 rounded-full text-xs font-bold font-data"
 :class="selectedExpert.verifiedBadge ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning'"
 >
 {{ selectedExpert.verifiedBadge ? '✓ Verified Provider' : ' Pending Review' }}
 </span>
 </div>

 <!-- License Info -->
 <div class="grid grid-cols-2 gap-4">
 <div class="p-3 bg-canvas border border-border rounded-xl">
 <div class="font-data text-xs text-ink-muted uppercase">Medical / Dietetic License</div>
 <div class="font-display font-semibold text-sm text-ink mt-0.5">{{ selectedExpert.licenseNo }}</div>
 </div>
 <div class="p-3 bg-canvas border border-border rounded-xl">
 <div class="font-data text-xs text-ink-muted uppercase">Issuing Board / Body</div>
 <div class="font-display font-semibold text-sm text-ink mt-0.5">{{ selectedExpert.issuingBody }}</div>
 </div>
 </div>

 <!-- Uploaded Verification Documents -->
 <div>
 <h4 class="font-display font-semibold text-sm text-ink mb-2">Submitted Certificates & Diplomas (PDFs)</h4>
 <div class="divide-y divide-border border border-border rounded-xl overflow-hidden bg-canvas">
 <div v-for="doc in selectedExpert.docs" :key="doc.name" class="p-3.5 flex items-center justify-between">
 <div class="flex items-center gap-3">
 <Icon name="recipe" :size="18" class="text-primary" />
 <div>
 <div class="font-semibold text-xs text-ink">{{ doc.name }}</div>
 <div class="font-data text-[0.7rem] text-ink-muted">{{ doc.size }} · Uploaded {{ doc.date }}</div>
 </div>
 </div>
 <button class="text-primary text-xs font-semibold hover:underline" @click="notify(`Previewing ${doc.name} (Simulated PDF Viewer)...`)">
 Inspect Document ↗
 </button>
 </div>
 </div>
 </div>

 <div class="flex justify-end gap-3 pt-2">
 <Button variant="outline" @click="showReviewModal = false">Close</Button>
 <Button 
 v-if="selectedExpert.verifiedBadge" 
 variant="danger" 
 @click="revokeVerification(selectedExpert)"
 >
 Revoke Verification
 </Button>
 <Button 
 v-else 
 @click="approveExpert(selectedExpert)"
 >
 ✓ Verify Credentials & Approve Provider
 </Button>
 </div>
 </div>
 </Modal>

 <!-- Header -->
 <div class="flex flex-col sm:flex-row justify-between sm:items-end gap-4">
 <div>
 <h2 class="font-display font-semibold text-[1.4rem] text-ink">Experts Queue & Credential Verification</h2>
 <p class="font-body text-[0.95rem] text-ink-muted">Inspect submitted medical credentials, degrees, and approve verified provider badges.</p>
 </div>

 <div class="flex items-center gap-2">
 <button
 v-for="f in [
 { id: 'all', label: 'All Providers' },
 { id: 'pending', label: `Pending (${pendingCount})` },
 { id: 'approved', label: 'Verified' },
 ]"
 :key="f.id"
 class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer"
 :class="filterStatus === f.id ? 'bg-primary text-white' : 'bg-canvas-raised border border-border text-ink-muted hover:text-ink'"
 @click="filterStatus = f.id as any"
 >
 {{ f.label }}
 </button>
 </div>
 </div>

 <!-- Table -->
 <div class="bg-canvas-raised border border-border rounded-xl overflow-hidden shadow-sm">
 <table class="w-full text-left border-collapse">
 <thead>
 <tr class="bg-canvas border-b border-border">
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Doctor / Dietitian</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Specialty</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">License Registration</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Rate</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold">Status</th>
 <th class="py-3 px-4 font-data text-[0.75rem] text-ink-muted uppercase tracking-wider font-semibold text-right">Actions</th>
 </tr>
 </thead>
 <tbody class="divide-y divide-border">
 <tr v-for="expert in paginatedExperts" :key="expert.id" class="hover:bg-canvas/50 transition-colors">
 <td class="py-3.5 px-4 font-body text-[0.9rem] font-semibold text-ink">
 <div class="flex items-center gap-2.5">
 <div class="w-8 h-8 rounded-full bg-primary-soft text-primary font-bold text-xs flex items-center justify-center">
 {{ expert.name.split(' ').map((n: string)=>n[0]).join('') }}
 </div>
 <div>
 <div class="flex items-center gap-1.5">
 <span>{{ expert.name }}</span>
 <Icon v-if="expert.verifiedBadge" name="check" :size="14" class="text-success" />
 </div>
 <div class="text-[0.72rem] font-normal text-ink-muted">Applied on {{ expert.appliedDate }}</div>
 </div>
 </div>
 </td>
 <td class="py-3.5 px-4 font-body text-[0.88rem] text-ink-muted">{{ expert.spec }}</td>
 <td class="py-3.5 px-4 font-data text-[0.82rem] text-ink">{{ expert.licenseNo }}</td>
 <td class="py-3.5 px-4 font-data text-[0.85rem] text-ink">${{ expert.rate }}/hr</td>
 <td class="py-3.5 px-4">
 <span 
 class="font-data text-[0.75rem] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider inline-flex items-center gap-1"
 :class="expert.status === 'Approved' ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning'"
 >
 <span v-if="expert.status !== 'Approved'" class="w-1.5 h-1.5 rounded-full bg-warning animate-pulse"></span>
 {{ expert.status }}
 </span>
 </td>
 <td class="py-3.5 px-4 text-right">
 <Button size="sm" variant="outline" @click="openReview(expert)">
 Inspect Credentials →
 </Button>
 </td>
 </tr>
 </tbody>
 </table>
 </div>

 <!-- Pagination -->
 <div v-if="!isLoading && filteredExperts.length > pageSize" class="flex items-center justify-between mt-4">
   <p class="font-data text-[0.8rem] text-ink-muted">
     Showing {{ rangeStart }}–{{ rangeEnd }} of {{ filteredExperts.length }} providers
   </p>
   <div class="flex items-center gap-2">
     <button
       @click="currentPage--"
       :disabled="currentPage <= 1"
       class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-border bg-canvas text-ink disabled:opacity-40 hover:bg-canvas-raised transition-colors"
     >
       Previous
     </button>
     <span class="font-data text-[0.8rem] text-ink-muted">Page {{ currentPage }} of {{ totalPages }}</span>
     <button
       @click="currentPage++"
       :disabled="currentPage >= totalPages"
       class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-border bg-canvas text-ink disabled:opacity-40 hover:bg-canvas-raised transition-colors"
     >
       Next
     </button>
   </div>
 </div>

 </div>
</template>
