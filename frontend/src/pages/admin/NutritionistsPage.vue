<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Button from '../../components/ui/Button.vue'
import Modal from '../../components/ui/Modal.vue'
import Toast from '../../components/ui/Toast.vue'
import VerificationBadge from '../../components/VerificationBadge.vue'
import {
  useVerificationStore,
  type NutritionistApplication,
  type BadgeTier,
  tierLabel,
  statusLabel,
  formatDate,
} from '../../stores/verification'

const store = useVerificationStore()

// ── UI state ──────────────────────────────────────────────────────────────
const showToast = ref(false)
const toastMsg = ref('')
const showReviewModal = ref(false)
const showActionModal = ref<'approve' | 'needs_info' | 'reject' | 'revoke' | null>(null)
const selected = ref<NutritionistApplication | null>(null)
const filterStatus = ref<'all' | 'pending_review' | 'verified' | 'needs_info' | 'rejected'>('all')
const searchQ = ref('')
const currentPage = ref(1)
const pageSize = 6

// action modal form
const actionTier = ref<BadgeTier>('ncahp_verified')
const actionNote = ref('')

// ── Invite Clinician State ──────────────────────────────────────────────────
const showInviteModal = ref(false)
const isInviting = ref(false)
const inviteForm = ref({
  name: '',
  email: '',
  ncahp_reg_number: '',
  ida_membership_number: '',
  assigned_tier: 'ncahp_verified' as BadgeTier,
  specialtiesText: 'Diabetes Management, Metabolic Health, PCOS',
  hourly_rate_usd: 90,
})

async function submitInvite() {
  if (!inviteForm.value.name.trim() || !inviteForm.value.email.includes('@')) {
    notify('Please enter a valid practitioner name and email.')
    return
  }
  isInviting.value = true
  try {
    const specialties = inviteForm.value.specialtiesText.split(',').map(s => s.trim()).filter(Boolean)
    await store.inviteClinician({
      name: inviteForm.value.name.trim(),
      email: inviteForm.value.email.trim(),
      ncahp_reg_number: inviteForm.value.ncahp_reg_number.trim() || undefined,
      ida_membership_number: inviteForm.value.ida_membership_number.trim() || undefined,
      assigned_tier: inviteForm.value.assigned_tier,
      specialties,
      hourly_rate_usd: inviteForm.value.hourly_rate_usd,
    })
    showInviteModal.value = false
    notify(`Invitation dispatched to ${inviteForm.value.email}! Activation token generated.`)
    inviteForm.value = {
      name: '',
      email: '',
      ncahp_reg_number: '',
      ida_membership_number: '',
      assigned_tier: 'ncahp_verified',
      specialtiesText: 'Diabetes Management, Metabolic Health, PCOS',
      hourly_rate_usd: 90,
    }
  } catch (err: any) {
    notify(`Failed to send invite: ${err.message || 'Error'}`)
  } finally {
    isInviting.value = false
  }
}

function notify(msg: string) {
  toastMsg.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 4000)
}

// ── Filtering & pagination ─────────────────────────────────────────────────
const filtered = computed(() => {
  let list = store.applications
  if (filterStatus.value !== 'all') list = list.filter(a => a.status === filterStatus.value)
  if (searchQ.value.trim()) {
    const q = searchQ.value.toLowerCase()
    list = list.filter(a =>
      a.name.toLowerCase().includes(q) ||
      a.email.toLowerCase().includes(q) ||
      (a.ncahpRegNumber ?? '').toLowerCase().includes(q) ||
      (a.idaMembershipNumber ?? '').toLowerCase().includes(q) ||
      a.specialties.some(s => s.toLowerCase().includes(q))
    )
  }
  return list
})

watch([searchQ, filterStatus], () => {
  currentPage.value = 1
})

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))

const paginated = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

const rangeStart = computed(() => filtered.value.length === 0 ? 0 : (currentPage.value - 1) * pageSize + 1)
const rangeEnd = computed(() => Math.min(currentPage.value * pageSize, filtered.value.length))

// ── Actions ────────────────────────────────────────────────────────────────
function openReview(app: NutritionistApplication) {
  selected.value = app
  showReviewModal.value = true
}

function openActionModal(type: 'approve' | 'needs_info' | 'reject' | 'revoke') {
  actionNote.value = selected.value?.opsNotes ?? ''
  if (type === 'approve') {
    if (selected.value?.ncahpLookupStatus === 'found') actionTier.value = 'ncahp_verified'
    else if (selected.value?.idaLookupStatus === 'found') actionTier.value = 'ida_verified'
    else actionTier.value = 'degree_verified'
  }
  showActionModal.value = type
}

function confirmAction() {
  if (!selected.value) return
  const id = selected.value.id
  const note = actionNote.value

  switch (showActionModal.value) {
    case 'approve':
      store.approveApplication(id, actionTier.value, note)
      notify(`${selected.value.name} approved. ${tierLabel(actionTier.value)} badge issued.`)
      break
    case 'needs_info':
      store.requestMoreInfo(id, note)
      notify(`Requested more information from ${selected.value.name}.`)
      break
    case 'reject':
      store.rejectApplication(id, note)
      notify(`Application rejected. ${selected.value.name} notified.`)
      break
    case 'revoke':
      store.revokeVerification(id, note)
      notify(`Verification revoked for ${selected.value.name}.`)
      break
  }

  showActionModal.value = null
  showReviewModal.value = false
  selected.value = null
}

function runNcahpLookup(app: NutritionistApplication) {
  if (!app.ncahpRegNumber) return
  notify(`Checking NCAHP Central Register for ${app.ncahpRegNumber}...`)
  setTimeout(() => {
    store.setNcahpLookup(app.id, 'found')
    notify(`NCAHP lookup complete: ${app.ncahpRegNumber} is active in the Central Register.`)
  }, 1500)
}

function runIdaLookup(app: NutritionistApplication) {
  if (!app.idaMembershipNumber) return
  notify(`Checking IDA Directory for ${app.idaMembershipNumber}...`)
  setTimeout(() => {
    store.setIdaLookup(app.id, 'found')
    notify(`IDA lookup complete: ${app.idaMembershipNumber} is a confirmed RD member.`)
  }, 1500)
}

// ── Helpers ────────────────────────────────────────────────────────────────
const statusStyle: Record<string, { bg: string; text: string; dot: string; border: string }> = {
  verified:       { bg: 'rgba(16,185,129,0.12)', text: '#059669', dot: '#10B981', border: 'rgba(16,185,129,0.25)' },
  pending_review: { bg: 'rgba(245,158,11,0.12)', text: '#D97706', dot: '#F59E0B', border: 'rgba(245,158,11,0.25)' },
  needs_info:     { bg: 'rgba(234,88,12,0.12)',  text: '#EA580C', dot: '#F97316', border: 'rgba(234,88,12,0.25)' },
  rejected:       { bg: 'rgba(239,68,68,0.12)',  text: '#DC2626', dot: '#EF4444', border: 'rgba(239,68,68,0.25)' },
  unverified:     { bg: 'rgba(100,116,139,0.1)', text: '#64748B', dot: '#94A3B8', border: 'rgba(100,116,139,0.2)' },
}

function initials(name: string) {
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
}

const actionModalConfig = computed(() => {
  const map = {
    approve:    { title: 'Approve & Issue Verification Badge', cta: 'Approve & Issue Badge', variant: 'primary' as const },
    needs_info: { title: 'Request Additional Information',     cta: 'Send Info Request',     variant: 'outline' as const },
    reject:     { title: 'Reject Application',                 cta: 'Reject Application',    variant: 'danger' as const },
    revoke:     { title: 'Revoke Verification',                cta: 'Revoke Verification',   variant: 'danger' as const },
  }
  return showActionModal.value ? map[showActionModal.value] : null
})

const tierOptions: Array<{ value: BadgeTier; label: string; tierBadge: string; desc: string }> = [
  { value: 'ncahp_verified',  label: 'Gold — NCAHP Verified',             tierBadge: 'NCAHP Gold',   desc: 'NCAHP Central Register confirmed active registration under NCAHP Act 2021' },
  { value: 'ida_verified',    label: 'Silver — IDA Registered Dietitian', tierBadge: 'IDA Silver',   desc: 'IDA directory confirms active Registered Dietitian (RD) credential' },
  { value: 'degree_verified', label: 'Bronze — Degree Verified',          tierBadge: 'Degree Bronze', desc: 'University graduate degree confirmed via DigiLocker or registrar' },
]
</script>

<template>
  <div class="space-y-6">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- ── Header ──────────────────────────────────────────────────────────── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-display font-bold text-[1.8rem] text-ink">Nutritionist Verification</h1>
          <span class="px-2.5 py-0.5 rounded-full text-[0.7rem] font-bold bg-primary/10 text-primary border border-primary/20">
            NCAHP / IDA Registry Ops
          </span>
        </div>
        <p class="font-body text-[0.88rem] text-ink-muted mt-0.5">
          Review practitioner credentials, execute official registry lookups, and issue trust badges.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <Button variant="outline" size="sm" @click="notify('Refreshed verification data.')">
          <svg class="w-3.5 h-3.5 mr-1.5 inline" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
          Refresh
        </Button>
        <Button variant="primary" size="sm" @click="showInviteModal = true">
          <svg class="w-3.5 h-3.5 mr-1.5 inline" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Invite Clinician
        </Button>
      </div>
    </div>

    <!-- ── Metric Cards ────────────────────────────────────────────────────── -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="p-4 rounded-xl border border-border bg-canvas-raised shadow-xs">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-ink-muted uppercase font-data">Total Applicants</span>
          <span class="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-600 flex items-center justify-center">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </span>
        </div>
        <div class="mt-3 font-display font-bold text-2xl text-ink">{{ store.totalCount }}</div>
      </div>

      <div class="p-4 rounded-xl border border-amber-500/30 bg-amber-500/5 shadow-xs relative">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-amber-800 uppercase font-data">Pending Review</span>
          <span class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-700 flex items-center justify-center">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </span>
        </div>
        <div class="mt-3 font-display font-bold text-2xl text-amber-900 flex items-center gap-2">
          {{ store.pendingCount }}
          <span v-if="store.pendingCount > 0" class="inline-flex items-center px-1.5 py-0.5 rounded text-[0.65rem] font-bold bg-amber-500/20 text-amber-800">
            Action Req.
          </span>
        </div>
      </div>

      <div class="p-4 rounded-xl border border-orange-500/30 bg-orange-500/5 shadow-xs">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-orange-800 uppercase font-data">Needs More Info</span>
          <span class="w-8 h-8 rounded-lg bg-orange-500/20 text-orange-700 flex items-center justify-center">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          </span>
        </div>
        <div class="mt-3 font-display font-bold text-2xl text-orange-900">{{ store.needsInfoCount }}</div>
      </div>

      <div class="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5 shadow-xs">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-emerald-800 uppercase font-data">Verified Providers</span>
          <span class="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-700 flex items-center justify-center">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
          </span>
        </div>
        <div class="mt-3 font-display font-bold text-2xl text-emerald-900">{{ store.verifiedCount }}</div>
      </div>
    </div>

    <!-- ── Filter & Search Toolbar ────────────────────────────────────────── -->
    <div class="flex flex-col md:flex-row justify-between items-stretch md:items-center gap-3 bg-canvas-raised p-3 rounded-xl border border-border">
      <!-- Search Input -->
      <div class="relative flex-1 max-w-md">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-ink-muted">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </div>
        <input
          v-model="searchQ"
          type="text"
          placeholder="Search by name, email, reg number, or specialty..."
          class="w-full pl-9 pr-4 py-2 text-xs font-body rounded-lg bg-canvas border border-border text-ink placeholder-ink-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition"
        />
      </div>

      <!-- Filter Tabs -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
        <button
          v-for="f in [
            { id: 'all',            label: 'All' },
            { id: 'pending_review', label: `Pending (${store.pendingCount})` },
            { id: 'needs_info',     label: `Needs Info (${store.needsInfoCount})` },
            { id: 'verified',       label: `Verified (${store.verifiedCount})` },
            { id: 'rejected',       label: 'Rejected' },
          ]"
          :key="f.id"
          @click="filterStatus = f.id as any"
          class="px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition cursor-pointer"
          :class="filterStatus === f.id ? 'bg-primary text-white shadow-xs' : 'bg-canvas text-ink-muted hover:text-ink border border-border'"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <!-- ── Applications Table ────────────────────────────────────────────── -->
    <div class="bg-canvas-raised border border-border rounded-xl overflow-hidden shadow-xs">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-canvas border-b border-border text-[0.72rem] font-data text-ink-muted uppercase tracking-wider">
              <th class="py-3 px-4 font-semibold">Nutritionist</th>
              <th class="py-3 px-3 font-semibold">Specialties</th>
              <th class="py-3 px-4 font-semibold">Registry Status</th>
              <th class="py-3 px-3 font-semibold">Badge Tier</th>
              <th class="py-3 px-3 font-semibold">Status</th>
              <th class="py-3 px-3 font-semibold">Applied</th>
              <th class="py-3 px-4 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border font-body text-xs">
            <tr v-for="app in paginated" :key="app.id" class="hover:bg-canvas/50 transition-colors">
              <!-- Name & Email -->
              <td class="py-3.5 px-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-primary/15 text-primary font-bold flex items-center justify-center text-[0.72rem] shrink-0 border border-primary/25">
                    {{ initials(app.name) }}
                  </div>
                  <div>
                    <div class="font-semibold text-ink text-[0.85rem]">{{ app.name }}</div>
                    <div class="text-[0.72rem] text-ink-muted">{{ app.email }}</div>
                  </div>
                </div>
              </td>

              <!-- Specialties -->
              <td class="py-3.5 px-3">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="s in app.specialties.slice(0, 2)"
                    :key="s"
                    class="px-2 py-0.5 rounded text-[0.68rem] font-medium bg-primary/10 text-primary border border-primary/20"
                  >
                    {{ s }}
                  </span>
                  <span
                    v-if="app.specialties.length > 2"
                    class="px-1.5 py-0.5 rounded text-[0.68rem] bg-canvas text-ink-muted border border-border"
                  >
                    +{{ app.specialties.length - 2 }}
                  </span>
                </div>
              </td>

              <!-- Registry Checks -->
              <td class="py-3.5 px-4">
                <div v-if="app.ncahpRegNumber" class="flex items-center gap-1.5 font-data text-[0.72rem]">
                  <span class="w-2 h-2 rounded-full" :class="app.ncahpLookupStatus === 'found' ? 'bg-emerald-500' : 'bg-amber-500'"></span>
                  <span class="font-bold text-ink-muted">NCAHP:</span>
                  <span class="font-mono text-ink">{{ app.ncahpRegNumber }}</span>
                </div>
                <div v-if="app.idaMembershipNumber" class="flex items-center gap-1.5 font-data text-[0.72rem] mt-0.5">
                  <span class="w-2 h-2 rounded-full" :class="app.idaLookupStatus === 'found' ? 'bg-emerald-500' : 'bg-amber-500'"></span>
                  <span class="font-bold text-ink-muted">IDA:</span>
                  <span class="font-mono text-ink">{{ app.idaMembershipNumber }}</span>
                </div>
                <div v-if="!app.ncahpRegNumber && !app.idaMembershipNumber" class="text-ink-muted text-[0.72rem] italic">
                  Degree verification only
                </div>
              </td>

              <!-- Badge Tier -->
              <td class="py-3.5 px-3">
                <VerificationBadge :tier="app.badgeTier" :status="app.status" size="sm" :show-label="false" />
                <span class="block text-[0.68rem] text-ink-muted mt-1 font-data">{{ tierLabel(app.badgeTier) }}</span>
              </td>

              <!-- Status -->
              <td class="py-3.5 px-3">
                <span
                  class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.7rem] font-bold border"
                  :style="{
                    background: statusStyle[app.status].bg,
                    color: statusStyle[app.status].text,
                    borderColor: statusStyle[app.status].border,
                  }"
                >
                  <span
                    class="w-1.5 h-1.5 rounded-full"
                    :class="{ 'animate-ping': app.status === 'pending_review' }"
                    :style="{ background: statusStyle[app.status].dot }"
                  />
                  {{ statusLabel(app.status) }}
                </span>
              </td>

              <!-- Applied Date -->
              <td class="py-3.5 px-3 text-ink-muted font-data text-[0.72rem] whitespace-nowrap">
                {{ formatDate(app.appliedAt) }}
              </td>

              <!-- Actions -->
              <td class="py-3.5 px-4 text-right">
                <Button size="sm" variant="outline" @click="openReview(app)">
                  Audit Details
                  <svg class="w-3 h-3 ml-1 inline" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
                </Button>
              </td>
            </tr>

            <!-- Empty State -->
            <tr v-if="paginated.length === 0">
              <td colspan="7" class="py-12 text-center text-ink-muted">
                <div class="w-12 h-12 rounded-full bg-border/40 text-ink-muted flex items-center justify-center mx-auto mb-2">
                  <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                </div>
                <div class="font-display font-semibold text-sm text-ink">No applicants found</div>
                <div class="text-xs text-ink-muted mt-0.5">Try adjusting your search terms or filter selection.</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ── Pagination Bar ────────────────────────────────────────────────── -->
      <div v-if="filtered.length > 0" class="px-4 py-3 bg-canvas border-t border-border flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="font-data text-xs text-ink-muted">
          Showing <strong>{{ rangeStart }}–{{ rangeEnd }}</strong> of <strong>{{ filtered.length }}</strong> applicants
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage <= 1"
            class="px-3 py-1 text-xs font-semibold rounded-lg border border-border bg-canvas-raised text-ink disabled:opacity-40 hover:bg-canvas transition cursor-pointer flex items-center gap-1"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            Previous
          </button>
          <span class="font-data text-xs text-ink-muted px-2">
            Page <strong>{{ currentPage }}</strong> of <strong>{{ totalPages }}</strong>
          </span>
          <button
            @click="currentPage++"
            :disabled="currentPage >= totalPages"
            class="px-3 py-1 text-xs font-semibold rounded-lg border border-border bg-canvas-raised text-ink disabled:opacity-40 hover:bg-canvas transition cursor-pointer flex items-center gap-1"
          >
            Next
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- ── Credential Review Modal ───────────────────────────────────────── -->
    <Modal v-model="showReviewModal" :title="`Credential Audit: ${selected?.name}`" size="lg">
      <div v-if="selected" class="space-y-5 max-h-[75vh] overflow-y-auto pr-1">

        <!-- Top Profile Strip -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-xl bg-canvas border border-border">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-primary/20 text-primary font-bold flex items-center justify-center text-sm border border-primary/30 shrink-0">
              {{ initials(selected.name) }}
            </div>
            <div>
              <div class="font-display font-bold text-ink text-base">{{ selected.name }}</div>
              <div class="font-body text-xs text-ink-muted">{{ selected.email }} &bull; {{ selected.phone || 'No phone provided' }}</div>
              <div class="font-data text-[0.72rem] text-ink-muted mt-0.5">
                {{ selected.experienceYears }} Years Experience &bull; Hourly Rate: ${{ selected.hourlyRateUsd }}/hr
              </div>
            </div>
          </div>
          <VerificationBadge :tier="selected.badgeTier" :status="selected.status" size="md" />
        </div>

        <!-- Registry Verification Cards -->
        <div>
          <h4 class="font-display font-semibold text-xs text-ink uppercase tracking-wider mb-2">Council Registry Check</h4>
          <div class="grid sm:grid-cols-2 gap-3">
            <!-- NCAHP Central Register -->
            <div class="p-3.5 rounded-xl bg-canvas border border-border flex flex-col justify-between gap-3">
              <div>
                <div class="flex items-center justify-between">
                  <div class="font-semibold text-xs text-ink flex items-center gap-1.5">
                    <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                    NCAHP Central Register
                  </div>
                  <span class="text-[0.7rem] font-bold" :class="selected.ncahpLookupStatus === 'found' ? 'text-emerald-600' : 'text-amber-600'">
                    {{ selected.ncahpLookupStatus === 'found' ? 'Verified Active' : selected.ncahpRegNumber ? 'Pending Check' : 'Not Provided' }}
                  </span>
                </div>
                <p class="text-[0.7rem] text-ink-muted mt-1">ncahp.abdm.gov.in &bull; Allied Healthcare Council</p>
                <div class="mt-2 font-mono text-xs p-2 rounded bg-canvas-raised border border-border text-ink">
                  {{ selected.ncahpRegNumber || 'No registration number submitted' }}
                </div>
              </div>
              <div class="pt-1">
                <button
                  v-if="selected.ncahpRegNumber && selected.ncahpLookupStatus !== 'found'"
                  @click="runNcahpLookup(selected)"
                  class="px-2.5 py-1 text-xs font-semibold rounded bg-primary/10 text-primary border border-primary/25 hover:bg-primary/20 transition cursor-pointer"
                >
                  Execute Live Lookup
                </button>
                <a
                  v-else-if="selected.ncahpRegNumber"
                  href="https://ncahp.abdm.gov.in"
                  target="_blank"
                  rel="noopener"
                  class="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1"
                >
                  Open Central Register
                  <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                </a>
              </div>
            </div>

            <!-- IDA Directory -->
            <div class="p-3.5 rounded-xl bg-canvas border border-border flex flex-col justify-between gap-3">
              <div>
                <div class="flex items-center justify-between">
                  <div class="font-semibold text-xs text-ink flex items-center gap-1.5">
                    <svg class="w-4 h-4 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    Indian Dietetic Association
                  </div>
                  <span class="text-[0.7rem] font-bold" :class="selected.idaLookupStatus === 'found' ? 'text-emerald-600' : 'text-amber-600'">
                    {{ selected.idaLookupStatus === 'found' ? 'Confirmed RD' : selected.idaMembershipNumber ? 'Pending Check' : 'Not Provided' }}
                  </span>
                </div>
                <p class="text-[0.7rem] text-ink-muted mt-1">Registered Dietitian (RD) Member Directory</p>
                <div class="mt-2 font-mono text-xs p-2 rounded bg-canvas-raised border border-border text-ink">
                  {{ selected.idaMembershipNumber || 'No IDA number submitted' }}
                </div>
              </div>
              <div class="pt-1">
                <button
                  v-if="selected.idaMembershipNumber && selected.idaLookupStatus !== 'found'"
                  @click="runIdaLookup(selected)"
                  class="px-2.5 py-1 text-xs font-semibold rounded bg-primary/10 text-primary border border-primary/25 hover:bg-primary/20 transition cursor-pointer"
                >
                  Execute Live Lookup
                </button>
                <span v-else-if="selected.idaLookupStatus === 'found'" class="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                  <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                  Directory Match Confirmed
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Degree & Education -->
        <div>
          <h4 class="font-display font-semibold text-xs text-ink uppercase tracking-wider mb-2">Degree Qualification</h4>
          <div class="p-3.5 rounded-xl bg-canvas border border-border flex items-center gap-3">
            <span class="w-9 h-9 rounded-lg bg-amber-500/15 text-amber-700 flex items-center justify-center shrink-0">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
            </span>
            <div class="flex-1">
              <div class="font-semibold text-xs text-ink">{{ selected.degreeInstitution }}</div>
              <div class="text-[0.72rem] text-ink-muted mt-0.5">
                Year of Graduation: {{ selected.degreeYear }}
                <span v-if="selected.degreeDigilockerRef" class="text-blue-600 font-mono ml-2">
                  DigiLocker Ref: {{ selected.degreeDigilockerRef }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Submitted Documents -->
        <div>
          <h4 class="font-display font-semibold text-xs text-ink uppercase tracking-wider mb-2">
            Uploaded Verification Evidence ({{ selected.docs.length }})
          </h4>
          <div class="divide-y divide-border border border-border rounded-xl bg-canvas overflow-hidden">
            <div
              v-for="doc in selected.docs"
              :key="doc.name"
              class="flex items-center justify-between p-3 hover:bg-canvas-raised transition"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <span class="w-7 h-7 rounded bg-primary/10 text-primary flex items-center justify-center shrink-0">
                  <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                </span>
                <div class="min-w-0">
                  <div class="font-semibold text-xs text-ink truncate">{{ doc.name }}</div>
                  <div class="text-[0.7rem] text-ink-muted">{{ doc.size }} &bull; {{ formatDate(doc.uploadedAt) }}</div>
                </div>
              </div>
              <button
                @click="notify(`Document preview opened: ${doc.name}`)"
                class="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 cursor-pointer"
              >
                Inspect
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Audit Log -->
        <div>
          <h4 class="font-display font-semibold text-xs text-ink uppercase tracking-wider mb-2">Audit History</h4>
          <div class="space-y-2 p-3 rounded-xl bg-canvas border border-border text-xs">
            <div v-for="entry in [...selected.auditLog].reverse()" :key="entry.id" class="flex items-start gap-2 border-b border-border/50 pb-2 last:border-b-0 last:pb-0">
              <span class="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0"></span>
              <div class="flex-1">
                <div class="font-semibold text-ink">{{ entry.action }}</div>
                <div class="text-[0.7rem] text-ink-muted">{{ formatDate(entry.timestamp) }} &bull; {{ entry.performedBy }}</div>
                <div v-if="entry.note" class="text-[0.72rem] text-ink-muted italic mt-0.5">"{{ entry.note }}"</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Footer -->
        <div class="flex flex-wrap items-center justify-end gap-2 pt-3 border-t border-border">
          <Button variant="outline" size="sm" @click="showReviewModal = false">Close</Button>
          <template v-if="selected.status !== 'verified'">
            <Button variant="outline" size="sm" @click="openActionModal('needs_info')">Request Information</Button>
            <Button variant="danger" size="sm" @click="openActionModal('reject')">Reject Application</Button>
            <Button variant="primary" size="sm" @click="openActionModal('approve')">Approve & Issue Badge</Button>
          </template>
          <template v-else>
            <Button variant="danger" size="sm" @click="openActionModal('revoke')">Revoke Verification</Button>
          </template>
        </div>

      </div>
    </Modal>

    <!-- ── Action Confirm Modal ──────────────────────────────────────────── -->
    <Modal
      v-if="showActionModal"
      :model-value="!!showActionModal"
      :title="actionModalConfig?.title ?? ''"
      @update:model-value="showActionModal = null"
    >
      <div class="space-y-4">
        <!-- Tier Selection (Approve only) -->
        <div v-if="showActionModal === 'approve'" class="space-y-2">
          <label class="block text-xs font-semibold text-ink uppercase tracking-wider">Select Badge Tier</label>
          <div class="space-y-2">
            <div
              v-for="opt in tierOptions"
              :key="opt.value"
              @click="actionTier = opt.value"
              class="p-3 rounded-xl border cursor-pointer transition"
              :class="actionTier === opt.value ? 'bg-primary/10 border-primary ring-1 ring-primary' : 'bg-canvas border-border hover:border-primary/40'"
            >
              <div class="flex items-center justify-between">
                <span class="font-semibold text-xs text-ink">{{ opt.label }}</span>
                <span class="text-[0.7rem] px-2 py-0.5 rounded font-bold" :class="actionTier === opt.value ? 'bg-primary text-white' : 'bg-canvas-raised text-ink-muted'">
                  {{ opt.tierBadge }}
                </span>
              </div>
              <p class="text-[0.72rem] text-ink-muted mt-1">{{ opt.desc }}</p>
            </div>
          </div>
        </div>

        <!-- Note Input -->
        <div class="space-y-1.5">
          <label class="block text-xs font-semibold text-ink uppercase tracking-wider">
            {{ showActionModal === 'approve' ? 'Internal Ops Note (Optional)' : 'Auditable Reason / Note *' }}
          </label>
          <textarea
            v-model="actionNote"
            rows="3"
            class="w-full p-2.5 rounded-lg bg-canvas border border-border text-xs text-ink focus:outline-none focus:border-primary transition"
            placeholder="Add context for patient and compliance audit log..."
          ></textarea>
        </div>

        <!-- Modal Footer -->
        <div class="flex justify-end gap-2 pt-2 border-t border-border">
          <Button variant="outline" size="sm" @click="showActionModal = null">Cancel</Button>
          <Button :variant="actionModalConfig?.variant ?? 'primary'" size="sm" @click="confirmAction">
            {{ actionModalConfig?.cta }}
          </Button>
        </div>
      </div>
    </Modal>

    <!-- ── Invite Clinician Modal ────────────────────────────────────────── -->
    <Modal
      v-model="showInviteModal"
      title="Invite Clinician & Pre-Verify"
      size="md"
    >
      <div class="space-y-4">
        <p class="text-xs text-ink-muted">
          Generate a pre-verified practitioner account. The clinician will receive an email containing a secure 1-time magic link to claim their profile and set a password.
        </p>

        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">Clinician Full Name *</label>
            <input
              v-model="inviteForm.name"
              type="text"
              placeholder="e.g. Dr. Kavita Nair, RD"
              class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">Email Address *</label>
            <input
              v-model="inviteForm.email"
              type="email"
              placeholder="kavita.nair@hospital.org"
              class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">NCAHP Reg No.</label>
              <input
                v-model="inviteForm.ncahp_reg_number"
                type="text"
                placeholder="NCAHP/RD/2024/..."
                class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">IDA Member No.</label>
              <input
                v-model="inviteForm.ida_membership_number"
                type="text"
                placeholder="IDA-REG-..."
                class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary font-mono"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">Pre-Assigned Badge Tier</label>
            <select
              v-model="inviteForm.assigned_tier"
              class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary"
            >
              <option value="ncahp_verified">Gold — NCAHP Central Register Verified</option>
              <option value="ida_verified">Silver — IDA Registered Dietitian</option>
              <option value="degree_verified">Bronze — University Degree Verified</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">Specialties (comma-separated)</label>
            <input
              v-model="inviteForm.specialtiesText"
              type="text"
              class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">Consultation Hourly Rate ($ USD)</label>
            <input
              v-model.number="inviteForm.hourly_rate_usd"
              type="number"
              min="30"
              class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t border-border">
          <Button variant="outline" size="sm" @click="showInviteModal = false">Cancel</Button>
          <Button variant="primary" size="sm" :disabled="isInviting" @click="submitInvite">
            {{ isInviting ? 'Dispatching...' : 'Dispatch Email Invitation' }}
          </Button>
        </div>
      </div>
    </Modal>
  </div>
</template>
