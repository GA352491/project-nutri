<script setup lang="ts">
import { ref, computed } from 'vue'
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
const pageSize = 8

// action modal form
const actionTier = ref<BadgeTier>('ncahp_verified')
const actionNote = ref('')

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

const paginated = computed(() => {
  currentPage.value = 1
  return filtered.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize)
})

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
      notify(`✓ ${selected.value.name} approved — ${tierLabel(actionTier.value)} badge issued.`)
      break
    case 'needs_info':
      store.requestMoreInfo(id, note)
      notify(`📬 Requested more information from ${selected.value.name}.`)
      break
    case 'reject':
      store.rejectApplication(id, note)
      notify(`✗ Application rejected — ${selected.value.name} notified.`)
      break
    case 'revoke':
      store.revokeVerification(id, note)
      notify(`⚠️ Verification revoked for ${selected.value.name}.`)
      break
  }

  showActionModal.value = null
  showReviewModal.value = false
  selected.value = null
}

function runNcahpLookup(app: NutritionistApplication) {
  if (!app.ncahpRegNumber) return
  notify(`🔍 Checking NCAHP Central Register for ${app.ncahpRegNumber}…`)
  setTimeout(() => {
    store.setNcahpLookup(app.id, 'found')
    notify(`✓ NCAHP lookup complete: ${app.ncahpRegNumber} is active in the Central Register.`)
  }, 2000)
}

function runIdaLookup(app: NutritionistApplication) {
  if (!app.idaMembershipNumber) return
  notify(`🔍 Checking IDA Directory for ${app.idaMembershipNumber}…`)
  setTimeout(() => {
    store.setIdaLookup(app.id, 'found')
    notify(`✓ IDA lookup complete: ${app.idaMembershipNumber} is a confirmed RD member.`)
  }, 2000)
}

// ── Helpers ────────────────────────────────────────────────────────────────
const statusStyle: Record<string, { bg: string; text: string; dot: string }> = {
  verified:       { bg: 'rgba(16,185,129,0.15)', text: '#10B981', dot: '#10B981' },
  pending_review: { bg: 'rgba(251,191,36,0.15)', text: '#FBBF24', dot: '#FBBF24' },
  needs_info:     { bg: 'rgba(249,115,22,0.15)', text: '#FB923C', dot: '#FB923C' },
  rejected:       { bg: 'rgba(239,68,68,0.15)',  text: '#F87171', dot: '#F87171' },
  unverified:     { bg: 'rgba(100,116,139,0.1)', text: '#94A3B8', dot: '#94A3B8' },
}

function initials(name: string) {
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
}

const lookupStyle = (s?: string | null) =>
  s === 'found'        ? { text: '#10B981', icon: '✓' } :
  s === 'not_found'    ? { text: '#F87171', icon: '✗' } :
  s === 'pending_manual' ? { text: '#FBBF24', icon: '⏳' } :
                           { text: '#64748B', icon: '—' }

const actionModalConfig = computed(() => {
  const map = {
    approve:    { title: 'Approve & Issue Verification Badge', cta: '✓ Approve & Issue Badge', variant: 'primary' as const },
    needs_info: { title: 'Request Additional Information',     cta: '📬 Send Info Request',     variant: 'outline' as const },
    reject:     { title: 'Reject Application',                 cta: '✗ Reject Application',     variant: 'danger' as const },
    revoke:     { title: 'Revoke Verification',                cta: '⚠️ Revoke',                variant: 'danger' as const },
  }
  return showActionModal.value ? map[showActionModal.value] : null
})

const tierOptions: Array<{ value: BadgeTier; label: string; desc: string }> = [
  { value: 'ncahp_verified',  label: '🛡️ Gold — NCAHP Verified',                desc: 'NCAHP Central Register confirmed active registration' },
  { value: 'ida_verified',    label: '✅ Silver — IDA Registered Dietitian',    desc: 'IDA directory confirms active RD membership' },
  { value: 'degree_verified', label: '🎓 Bronze — Degree Verified',             desc: 'University degree confirmed (DigiLocker or direct)' },
]
</script>

<template>
  <div class="ops-page">
    <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

    <!-- ── Stats bar ─────────────────────────────────────────────────────── -->
    <div class="stats-bar">
      <div class="stat-card stat-card--total">
        <div class="stat-num">{{ store.totalCount }}</div>
        <div class="stat-label">Total Applicants</div>
      </div>
      <div class="stat-card stat-card--pending">
        <div class="stat-num">{{ store.pendingCount }}</div>
        <div class="stat-label">Pending Review</div>
        <span v-if="store.pendingCount > 0" class="stat-ping" />
      </div>
      <div class="stat-card stat-card--info">
        <div class="stat-num">{{ store.needsInfoCount }}</div>
        <div class="stat-label">Needs More Info</div>
      </div>
      <div class="stat-card stat-card--verified">
        <div class="stat-num">{{ store.verifiedCount }}</div>
        <div class="stat-label">Verified Providers</div>
      </div>
    </div>

    <!-- ── Header & filters ──────────────────────────────────────────────── -->
    <div class="page-header">
      <div>
        <h2 class="page-title">Nutritionist Verification Dashboard</h2>
        <p class="page-sub">Credential Ops · NCAHP / IDA registry checks · Badge issuance</p>
      </div>
      <div class="header-actions">
        <!-- Search -->
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input v-model="searchQ" class="search-input" placeholder="Search by name, email, reg no…" />
        </div>
        <!-- Status filter -->
        <div class="filter-tabs">
          <button
            v-for="f in [
              { id: 'all',          label: 'All' },
              { id: 'pending_review', label: `Pending (${store.pendingCount})` },
              { id: 'needs_info',   label: `Needs Info (${store.needsInfoCount})` },
              { id: 'verified',     label: `Verified (${store.verifiedCount})` },
              { id: 'rejected',     label: 'Rejected' },
            ]"
            :key="f.id"
            class="filter-tab"
            :class="{ 'filter-tab--active': filterStatus === f.id }"
            @click="filterStatus = f.id as any"
          >{{ f.label }}</button>
        </div>
      </div>
    </div>

    <!-- ── Applications table ────────────────────────────────────────────── -->
    <div class="table-wrap">
      <table class="ops-table">
        <thead>
          <tr>
            <th>Nutritionist</th>
            <th>Specialties</th>
            <th>NCAHP / IDA Registry</th>
            <th>Badge</th>
            <th>Status</th>
            <th>Applied</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in paginated" :key="app.id" class="table-row">
            <!-- Name -->
            <td class="td-name">
              <div class="avatar">{{ initials(app.name) }}</div>
              <div>
                <div class="name-text">{{ app.name }}</div>
                <div class="email-text">{{ app.email }}</div>
              </div>
            </td>
            <!-- Specialties -->
            <td class="td-spec">
              <div class="spec-chips">
                <span v-for="s in app.specialties.slice(0, 2)" :key="s" class="spec-chip">{{ s }}</span>
                <span v-if="app.specialties.length > 2" class="spec-chip spec-chip--more">+{{ app.specialties.length - 2 }}</span>
              </div>
            </td>
            <!-- Registry lookup -->
            <td class="td-registry">
              <div v-if="app.ncahpRegNumber" class="registry-row">
                <span :style="{ color: lookupStyle(app.ncahpLookupStatus).text, fontWeight: 700 }">
                  {{ lookupStyle(app.ncahpLookupStatus).icon }}
                </span>
                <span class="registry-label">NCAHP</span>
                <code class="registry-code">{{ app.ncahpRegNumber }}</code>
              </div>
              <div v-if="app.idaMembershipNumber" class="registry-row">
                <span :style="{ color: lookupStyle(app.idaLookupStatus).text, fontWeight: 700 }">
                  {{ lookupStyle(app.idaLookupStatus).icon }}
                </span>
                <span class="registry-label">IDA</span>
                <code class="registry-code">{{ app.idaMembershipNumber }}</code>
              </div>
              <div v-if="!app.ncahpRegNumber && !app.idaMembershipNumber" class="registry-none">
                No reg. number provided
              </div>
            </td>
            <!-- Badge -->
            <td class="td-badge">
              <VerificationBadge :tier="app.badgeTier" :status="app.status" size="sm" :show-label="false" />
              <span class="badge-tier-label">{{ tierLabel(app.badgeTier) }}</span>
            </td>
            <!-- Status pill -->
            <td class="td-status">
              <span
                class="status-pill"
                :style="{ background: statusStyle[app.status].bg, color: statusStyle[app.status].text }"
              >
                <span
                  class="status-dot"
                  :class="{ 'status-dot--pulse': app.status === 'pending_review' }"
                  :style="{ background: statusStyle[app.status].dot }"
                />
                {{ statusLabel(app.status) }}
              </span>
            </td>
            <!-- Date -->
            <td class="td-date">{{ formatDate(app.appliedAt) }}</td>
            <!-- Actions -->
            <td class="td-actions">
              <Button size="sm" variant="outline" @click="openReview(app)">
                Review →
              </Button>
            </td>
          </tr>

          <tr v-if="paginated.length === 0">
            <td colspan="7" class="empty-row">No applications match the current filter.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ── Credential Review Modal ───────────────────────────────────────── -->
    <Modal v-model="showReviewModal" :title="`Credential Review: ${selected?.name}`" size="lg">
      <div v-if="selected" class="review-modal">

        <!-- Top strip: badge + status -->
        <div class="review-strip">
          <div>
            <div class="review-name">{{ selected.name }}</div>
            <div class="review-sub">{{ selected.specialties.join(' · ') }} · {{ selected.experienceYears }}yr exp · ₹{{ Math.round(selected.hourlyRateUsd * 84) }}/hr</div>
          </div>
          <VerificationBadge :tier="selected.badgeTier" :status="selected.status" size="md" />
        </div>

        <!-- Registry checks -->
        <div class="section-title">Registry Verification</div>
        <div class="registry-checks">
          <div class="registry-check-card">
            <div class="rcc-header">
              <span class="rcc-icon">🏛️</span>
              <div>
                <div class="rcc-title">NCAHP Central Register</div>
                <div class="rcc-sub">ncahp.abdm.gov.in · National Commission for Allied &amp; Healthcare Professions</div>
              </div>
              <span
                class="rcc-status"
                :style="{ color: lookupStyle(selected.ncahpLookupStatus).text }"
              >
                {{ selected.ncahpLookupStatus === 'found' ? '✓ Found'
                   : selected.ncahpLookupStatus === 'not_found' ? '✗ Not Found'
                   : selected.ncahpLookupStatus === 'pending_manual' ? '⏳ Manual Check Pending'
                   : '— Not Checked' }}
              </span>
            </div>
            <div class="rcc-reg">
              {{ selected.ncahpRegNumber || 'No NCAHP registration number provided' }}
            </div>
            <button
              v-if="selected.ncahpRegNumber && selected.ncahpLookupStatus !== 'found'"
              class="lookup-btn"
              @click="runNcahpLookup(selected)"
            >
              Run Lookup ↗
            </button>
            <a
              v-else-if="selected.ncahpRegNumber"
              href="https://ncahp.abdm.gov.in"
              target="_blank"
              rel="noopener"
              class="lookup-btn lookup-btn--link"
            >
              Open Register ↗
            </a>
          </div>

          <div class="registry-check-card">
            <div class="rcc-header">
              <span class="rcc-icon">📋</span>
              <div>
                <div class="rcc-title">IDA — Indian Dietetic Association</div>
                <div class="rcc-sub">Registered Dietitian (RD) membership directory</div>
              </div>
              <span
                class="rcc-status"
                :style="{ color: lookupStyle(selected.idaLookupStatus).text }"
              >
                {{ selected.idaLookupStatus === 'found' ? '✓ Confirmed RD'
                   : selected.idaLookupStatus === 'not_found' ? '✗ Not Listed'
                   : selected.idaLookupStatus === 'pending_manual' ? '⏳ Manual Check Pending'
                   : '— Not Checked' }}
              </span>
            </div>
            <div class="rcc-reg">
              {{ selected.idaMembershipNumber || 'No IDA membership number provided' }}
            </div>
            <button
              v-if="selected.idaMembershipNumber && selected.idaLookupStatus !== 'found'"
              class="lookup-btn"
              @click="runIdaLookup(selected)"
            >
              Run Lookup ↗
            </button>
          </div>
        </div>

        <!-- Credentials & degree -->
        <div class="section-title">Degree &amp; Education</div>
        <div class="degree-card">
          <span class="degree-icon">🎓</span>
          <div>
            <div class="degree-inst">{{ selected.degreeInstitution }}</div>
            <div class="degree-sub">Graduated {{ selected.degreeYear }}
              <span v-if="selected.degreeDigilockerRef" class="digilocker-ref">· DigiLocker: {{ selected.degreeDigilockerRef }}</span>
            </div>
          </div>
        </div>

        <!-- Documents -->
        <div class="section-title">Submitted Documents ({{ selected.docs.length }})</div>
        <div class="docs-list">
          <div v-for="doc in selected.docs" :key="doc.name" class="doc-row">
            <div class="doc-icon-wrap">
              <span class="doc-icon">
                {{ doc.type === 'degree' ? '📄' : doc.type === 'registration' ? '🏅' : doc.type === 'id' ? '🪪' : '📎' }}
              </span>
            </div>
            <div class="doc-info">
              <div class="doc-name">{{ doc.name }}</div>
              <div class="doc-meta">{{ doc.size }} · Uploaded {{ formatDate(doc.uploadedAt) }}</div>
            </div>
            <button class="doc-view-btn" @click="notify(`Simulated preview: ${doc.name}`)">
              Inspect ↗
            </button>
          </div>
        </div>

        <!-- Sample cases -->
        <div v-if="selected.sampleCases" class="section-title">Sample Clinical Cases</div>
        <div v-if="selected.sampleCases" class="sample-cases">{{ selected.sampleCases }}</div>

        <!-- Ops notes -->
        <div class="section-title">Internal Ops Notes</div>
        <div class="ops-notes">{{ selected.opsNotes || 'No notes yet.' }}</div>

        <!-- Audit log -->
        <div class="section-title">Audit Log</div>
        <div class="audit-log">
          <div v-for="entry in [...selected.auditLog].reverse()" :key="entry.id" class="audit-entry">
            <div class="audit-dot" />
            <div class="audit-body">
              <div class="audit-action">{{ entry.action }}</div>
              <div class="audit-meta">{{ formatDate(entry.timestamp) }} · {{ entry.performedBy }}</div>
              <div v-if="entry.note" class="audit-note">{{ entry.note }}</div>
            </div>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="review-actions">
          <Button variant="outline" @click="showReviewModal = false">Close</Button>

          <template v-if="selected.status !== 'verified'">
            <Button variant="outline" @click="openActionModal('needs_info')">📬 Request Info</Button>
            <Button variant="danger" @click="openActionModal('reject')">✗ Reject</Button>
            <Button @click="openActionModal('approve')">✓ Approve &amp; Issue Badge</Button>
          </template>
          <template v-else>
            <Button variant="danger" @click="openActionModal('revoke')">⚠️ Revoke Verification</Button>
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
      <div class="action-modal">
        <!-- Badge tier picker (approve only) -->
        <div v-if="showActionModal === 'approve'" class="tier-picker">
          <div class="section-title" style="margin-bottom: 10px">Select Verification Badge Tier</div>
          <div
            v-for="opt in tierOptions"
            :key="opt.value"
            class="tier-option"
            :class="{ 'tier-option--selected': actionTier === opt.value }"
            @click="actionTier = opt.value"
          >
            <div class="tier-option-top">
              <span class="tier-label">{{ opt.label }}</span>
              <span v-if="actionTier === opt.value" class="tier-check">✓</span>
            </div>
            <div class="tier-desc">{{ opt.desc }}</div>
          </div>
        </div>

        <!-- Note -->
        <label class="form-label">
          {{ showActionModal === 'approve' ? 'Internal note (optional)' :
             showActionModal === 'needs_info' ? 'Specify what information is needed *' :
             'Reason *' }}
        </label>
        <textarea v-model="actionNote" class="action-textarea" rows="3" placeholder="Add context for audit log…" />

        <div class="action-footer">
          <Button variant="outline" @click="showActionModal = null">Cancel</Button>
          <Button :variant="actionModalConfig?.variant ?? 'primary'" @click="confirmAction">
            {{ actionModalConfig?.cta }}
          </Button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped>
/* ── Page layout ─────────────────────────────────────────────────────────── */
.ops-page { display: flex; flex-direction: column; gap: 24px; }

/* ── Stats bar ───────────────────────────────────────────────────────────── */
.stats-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  position: relative;
  padding: 16px 20px;
  border-radius: 14px;
  border: 1px solid;
  overflow: hidden;
}

.stat-card--total   { background: rgba(99,102,241,0.1);  border-color: rgba(99,102,241,0.3); }
.stat-card--pending { background: rgba(251,191,36,0.1);  border-color: rgba(251,191,36,0.35); }
.stat-card--info    { background: rgba(249,115,22,0.1);  border-color: rgba(249,115,22,0.3); }
.stat-card--verified{ background: rgba(16,185,129,0.1);  border-color: rgba(16,185,129,0.3); }

.stat-num {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-ink, #f1f5f9);
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-ink-muted, #94a3b8);
  margin-top: 4px;
  font-weight: 500;
}

.stat-ping {
  position: absolute;
  top: 14px;
  right: 16px;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #FBBF24;
  animation: ping 1.5s ease-in-out infinite;
}
@keyframes ping { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.5)} }

/* ── Header ─────────────────────────────────────────────────────────────── */
.page-header { display: flex; flex-wrap: wrap; gap: 16px; justify-content: space-between; align-items: flex-start; }
.page-title { font-size: 1.4rem; font-weight: 700; color: var(--color-ink, #f1f5f9); }
.page-sub { font-size: 0.875rem; color: var(--color-ink-muted, #94a3b8); margin-top: 2px; }

.header-actions { display: flex; flex-direction: column; gap: 10px; align-items: flex-end; }

.search-box {
  display: flex; align-items: center; gap: 8px;
  background: var(--color-canvas-raised, #1e293b);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 10px;
  padding: 8px 12px;
  width: 280px;
}
.search-icon { font-size: 13px; }
.search-input {
  background: none; border: none; outline: none;
  color: var(--color-ink, #f1f5f9); font-size: 0.875rem; width: 100%;
}
.search-input::placeholder { color: var(--color-ink-muted, #94a3b8); }

.filter-tabs { display: flex; gap: 6px; flex-wrap: wrap; }
.filter-tab {
  padding: 6px 14px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; cursor: pointer;
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  background: var(--color-canvas-raised, #1e293b);
  color: var(--color-ink-muted, #94a3b8);
  transition: all 0.15s;
}
.filter-tab:hover { color: var(--color-ink, #f1f5f9); }
.filter-tab--active { background: var(--color-primary, #4F46E5); border-color: var(--color-primary, #4F46E5); color: #fff; }

/* ── Table ───────────────────────────────────────────────────────────────── */
.table-wrap {
  background: var(--color-canvas-raised, #1e293b);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 16px; overflow: hidden;
}

.ops-table { width: 100%; border-collapse: collapse; }

.ops-table thead tr {
  background: var(--color-canvas, #0f172a);
  border-bottom: 1px solid var(--color-border, rgba(255,255,255,0.08));
}

.ops-table th {
  padding: 12px 16px;
  font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--color-ink-muted, #94a3b8); font-weight: 600; text-align: left;
}
.text-right { text-align: right !important; }

.table-row { border-bottom: 1px solid var(--color-border, rgba(255,255,255,0.06)); transition: background 0.1s; }
.table-row:hover { background: rgba(255,255,255,0.02); }
.table-row:last-child { border-bottom: none; }

.ops-table td { padding: 14px 16px; vertical-align: middle; }

/* cells */
.td-name { display: flex; align-items: center; gap: 12px; min-width: 180px; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
  background: rgba(99,102,241,0.2); color: #818CF8;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.name-text { font-size: 0.9rem; font-weight: 600; color: var(--color-ink, #f1f5f9); }
.email-text { font-size: 0.72rem; color: var(--color-ink-muted, #94a3b8); margin-top: 2px; }

.td-spec { min-width: 160px; }
.spec-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.spec-chip {
  font-size: 0.7rem; padding: 2px 8px; border-radius: 6px;
  background: rgba(99,102,241,0.15); color: #818CF8; font-weight: 500;
}
.spec-chip--more { background: rgba(100,116,139,0.15); color: #94A3B8; }

.td-registry { min-width: 210px; }
.registry-row { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.registry-label { font-size: 0.7rem; font-weight: 700; color: var(--color-ink-muted, #94a3b8); width: 30px; }
.registry-code { font-size: 0.7rem; font-family: monospace; color: var(--color-ink, #f1f5f9); background: rgba(255,255,255,0.05); padding: 1px 5px; border-radius: 4px; }
.registry-none { font-size: 0.72rem; color: rgba(100,116,139,0.7); font-style: italic; }

.td-badge { min-width: 140px; }
.badge-tier-label { display: block; font-size: 0.68rem; color: var(--color-ink-muted, #94a3b8); margin-top: 4px; }

.status-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 20px;
  font-size: 0.72rem; font-weight: 700; white-space: nowrap;
}
.status-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.status-dot--pulse { animation: ping 1.5s ease-in-out infinite; }

.td-date { font-size: 0.75rem; color: var(--color-ink-muted, #94a3b8); white-space: nowrap; }
.td-actions { text-align: right; }

.empty-row { text-align: center; padding: 40px; color: var(--color-ink-muted, #94a3b8); font-size: 0.875rem; }

/* ── Review Modal ────────────────────────────────────────────────────────── */
.review-modal { display: flex; flex-direction: column; gap: 16px; max-height: 70vh; overflow-y: auto; padding-right: 4px; }

.review-strip {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 16px; border-radius: 12px;
  background: var(--color-canvas, #0f172a);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
}
.review-name { font-size: 1.1rem; font-weight: 700; color: var(--color-ink, #f1f5f9); }
.review-sub  { font-size: 0.78rem; color: var(--color-ink-muted, #94a3b8); margin-top: 3px; }

.section-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-ink-muted, #94a3b8); font-weight: 700; }

.registry-checks { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.registry-check-card {
  padding: 14px; border-radius: 12px;
  background: var(--color-canvas, #0f172a);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
}
.rcc-header { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px; }
.rcc-icon { font-size: 20px; }
.rcc-title { font-size: 0.85rem; font-weight: 700; color: var(--color-ink, #f1f5f9); }
.rcc-sub { font-size: 0.68rem; color: var(--color-ink-muted, #94a3b8); margin-top: 1px; }
.rcc-status { font-size: 0.75rem; font-weight: 700; margin-left: auto; white-space: nowrap; }
.rcc-reg { font-size: 0.78rem; font-family: monospace; color: var(--color-ink, #f1f5f9); padding: 6px 8px; background: rgba(255,255,255,0.04); border-radius: 6px; margin-bottom: 8px; }
.lookup-btn {
  font-size: 0.75rem; font-weight: 700; color: #818CF8; cursor: pointer;
  background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3);
  padding: 4px 10px; border-radius: 6px; transition: background 0.15s;
}
.lookup-btn:hover { background: rgba(99,102,241,0.2); }
.lookup-btn--link { text-decoration: none; display: inline-block; }

.degree-card {
  display: flex; align-items: center; gap: 12px; padding: 12px 14px;
  border-radius: 10px; background: var(--color-canvas, #0f172a);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
}
.degree-icon { font-size: 24px; }
.degree-inst { font-size: 0.9rem; font-weight: 600; color: var(--color-ink, #f1f5f9); }
.degree-sub { font-size: 0.75rem; color: var(--color-ink-muted, #94a3b8); margin-top: 2px; }
.digilocker-ref { color: #60A5FA; font-family: monospace; font-size: 0.7rem; }

.docs-list { display: flex; flex-direction: column; gap: 0; border: 1px solid var(--color-border, rgba(255,255,255,0.08)); border-radius: 10px; overflow: hidden; }
.doc-row {
  display: flex; align-items: center; gap: 12px; padding: 10px 14px;
  border-bottom: 1px solid var(--color-border, rgba(255,255,255,0.06));
}
.doc-row:last-child { border-bottom: none; }
.doc-icon-wrap { width: 32px; height: 32px; border-radius: 8px; background: rgba(99,102,241,0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.doc-icon { font-size: 16px; }
.doc-info { flex: 1; }
.doc-name { font-size: 0.82rem; font-weight: 600; color: var(--color-ink, #f1f5f9); }
.doc-meta { font-size: 0.7rem; color: var(--color-ink-muted, #94a3b8); margin-top: 2px; }
.doc-view-btn { font-size: 0.72rem; font-weight: 700; color: #818CF8; cursor: pointer; background: none; border: none; }
.doc-view-btn:hover { text-decoration: underline; }

.sample-cases {
  font-size: 0.82rem; color: var(--color-ink-muted, #94a3b8);
  background: var(--color-canvas, #0f172a); border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 8px; padding: 10px 14px; line-height: 1.5;
}

.ops-notes {
  font-size: 0.82rem; color: var(--color-ink-muted, #94a3b8);
  font-style: italic; padding: 8px 12px;
  background: rgba(255,255,255,0.02); border-radius: 8px;
  border: 1px dashed var(--color-border, rgba(255,255,255,0.08));
}

.audit-log { display: flex; flex-direction: column; gap: 0; position: relative; padding-left: 20px; }
.audit-log::before {
  content: '';
  position: absolute; left: 7px; top: 8px; bottom: 8px;
  width: 2px; background: rgba(255,255,255,0.08); border-radius: 2px;
}
.audit-entry { display: flex; gap: 12px; padding: 8px 0; position: relative; }
.audit-dot {
  position: absolute; left: -17px; top: 13px;
  width: 8px; height: 8px; border-radius: 50%;
  background: rgba(99,102,241,0.7); border: 2px solid var(--color-canvas, #0f172a);
}
.audit-body { flex: 1; }
.audit-action { font-size: 0.82rem; font-weight: 600; color: var(--color-ink, #f1f5f9); }
.audit-meta { font-size: 0.68rem; color: var(--color-ink-muted, #94a3b8); margin-top: 2px; }
.audit-note { font-size: 0.72rem; color: rgba(148,163,184,0.7); margin-top: 3px; font-style: italic; }

.review-actions { display: flex; gap: 10px; justify-content: flex-end; flex-wrap: wrap; padding-top: 4px; border-top: 1px solid var(--color-border, rgba(255,255,255,0.08)); }

/* ── Action Modal ────────────────────────────────────────────────────────── */
.action-modal { display: flex; flex-direction: column; gap: 16px; }

.tier-picker { display: flex; flex-direction: column; gap: 8px; }
.tier-option {
  padding: 12px 14px; border-radius: 10px; cursor: pointer;
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  background: var(--color-canvas, #0f172a);
  transition: all 0.15s;
}
.tier-option:hover { border-color: rgba(99,102,241,0.4); }
.tier-option--selected { border-color: #4F46E5; background: rgba(99,102,241,0.1); }
.tier-option-top { display: flex; justify-content: space-between; align-items: center; }
.tier-label { font-size: 0.85rem; font-weight: 600; color: var(--color-ink, #f1f5f9); }
.tier-check { color: #4F46E5; font-weight: 800; }
.tier-desc { font-size: 0.72rem; color: var(--color-ink-muted, #94a3b8); margin-top: 4px; }

.form-label { font-size: 0.78rem; font-weight: 600; color: var(--color-ink-muted, #94a3b8); }
.action-textarea {
  width: 100%; padding: 10px 12px; border-radius: 10px;
  background: var(--color-canvas, #0f172a);
  border: 1px solid var(--color-border, rgba(255,255,255,0.1));
  color: var(--color-ink, #f1f5f9); font-size: 0.875rem;
  resize: vertical; outline: none; transition: border-color 0.15s;
}
.action-textarea:focus { border-color: rgba(99,102,241,0.6); }

.action-footer { display: flex; gap: 10px; justify-content: flex-end; padding-top: 4px; }
</style>
