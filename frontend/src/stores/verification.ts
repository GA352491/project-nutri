import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api'

// ── Types ──────────────────────────────────────────────────────────────────

export type VerificationStatus =
  | 'verified'
  | 'pending_review'
  | 'needs_info'
  | 'rejected'
  | 'unverified'

export type BadgeTier =
  | 'ncahp_verified'
  | 'ida_verified'
  | 'degree_verified'
  | 'pending'
  | 'none'

export interface AuditLogEntry {
  id: string
  timestamp: string
  action: string
  performedBy: string
  note?: string
}

export interface NutritionistApplication {
  id: string
  name: string
  email: string
  phone?: string
  ncahpRegNumber?: string
  idaMembershipNumber?: string
  degreeInstitution: string
  degreeYear: string
  degreeDigilockerRef?: string
  specialties: string[]
  bio: string
  experienceYears: number
  hourlyRateUsd: number
  docs: Array<{ name: string; size: string; uploadedAt: string; type: 'degree' | 'registration' | 'id' | 'other' }>
  sampleCases?: string
  status: VerificationStatus
  badgeTier: BadgeTier
  appliedAt: string
  lastUpdatedAt: string
  auditLog: AuditLogEntry[]
  opsNotes?: string
  ncahpLookupStatus?: 'found' | 'not_found' | 'pending_manual' | null
  idaLookupStatus?: 'found' | 'not_found' | 'pending_manual' | null
}

const SEED_APPLICATIONS: NutritionistApplication[] = [
  {
    id: 'nut-001',
    name: 'Dr. Priya Sharma',
    email: 'priya.sharma@example.com',
    phone: '+91-98765-43210',
    ncahpRegNumber: 'NCAHP-2024-DL-004821',
    idaMembershipNumber: 'IDA-2019-MH-7823',
    degreeInstitution: 'Institute of Home Economics, Delhi University',
    degreeYear: '2017',
    degreeDigilockerRef: 'DL-ABC123XYZ',
    specialties: ['Diabetes', 'PCOS', 'Metabolic Health'],
    bio: 'Clinical dietitian with 7 years in endocrinology and metabolic disorders. Worked at AIIMS Delhi before private practice.',
    experienceYears: 7,
    hourlyRateUsd: 90,
    docs: [
      { name: 'Priya_Sharma_BSc_Nutrition.pdf', size: '2.1 MB', uploadedAt: '2026-08-12T09:30:00Z', type: 'degree' },
      { name: 'NCAHP_Registration_Certificate.pdf', size: '1.4 MB', uploadedAt: '2026-08-12T09:31:00Z', type: 'registration' },
      { name: 'IDA_Membership_Card_2026.pdf', size: '0.8 MB', uploadedAt: '2026-08-12T09:32:00Z', type: 'registration' },
      { name: 'Aadhaar_Masked.pdf', size: '0.5 MB', uploadedAt: '2026-08-12T09:33:00Z', type: 'id' },
    ],
    sampleCases: 'Patient A: 45F, HbA1c 8.2%, reduced to 6.8% in 16 weeks via low-GI intervention.',
    status: 'verified',
    badgeTier: 'ncahp_verified',
    appliedAt: '2026-08-12T09:00:00Z',
    lastUpdatedAt: '2026-08-20T14:00:00Z',
    ncahpLookupStatus: 'found',
    idaLookupStatus: 'found',
    opsNotes: 'NCAHP register confirms active status. IDA membership current until Dec 2026. Degree verified via DigiLocker.',
    auditLog: [
      { id: 'a1', timestamp: '2026-08-12T09:00:00Z', action: 'Application submitted', performedBy: 'priya.sharma@example.com' },
      { id: 'a2', timestamp: '2026-08-14T11:00:00Z', action: 'NCAHP register lookup — Found', performedBy: 'ops@nutriplan.in', note: 'NCAHP-2024-DL-004821 active in Central Register' },
      { id: 'a3', timestamp: '2026-08-14T11:30:00Z', action: 'IDA membership confirmed', performedBy: 'ops@nutriplan.in' },
      { id: 'a4', timestamp: '2026-08-20T14:00:00Z', action: 'Status → Verified · Badge: NCAHP Verified (Gold)', performedBy: 'ops@nutriplan.in' },
    ],
  },
  {
    id: 'nut-002',
    name: 'Meera Iyer',
    email: 'meera.iyer@gmail.com',
    phone: '+91-99887-76655',
    idaMembershipNumber: 'IDA-2021-KA-3341',
    degreeInstitution: "St. John's Medical College, Bangalore",
    degreeYear: '2019',
    specialties: ['Weight Loss', 'Sports Nutrition', 'Gut Health'],
    bio: 'Registered Dietitian specializing in sports nutrition and metabolic health.',
    experienceYears: 5,
    hourlyRateUsd: 70,
    docs: [
      { name: 'Meera_Iyer_MSc_Dietetics.pdf', size: '3.2 MB', uploadedAt: '2026-08-28T10:00:00Z', type: 'degree' },
      { name: 'IDA_RD_Certificate_2021.pdf', size: '1.1 MB', uploadedAt: '2026-08-28T10:01:00Z', type: 'registration' },
    ],
    status: 'pending_review',
    badgeTier: 'pending',
    appliedAt: '2026-08-28T10:00:00Z',
    lastUpdatedAt: '2026-08-29T09:00:00Z',
    ncahpLookupStatus: 'pending_manual',
    idaLookupStatus: 'found',
    opsNotes: 'IDA confirmed. NCAHP not provided. Manual degree verification with St. Johns pending.',
    auditLog: [
      { id: 'b1', timestamp: '2026-08-28T10:00:00Z', action: 'Application submitted', performedBy: 'meera.iyer@gmail.com' },
      { id: 'b2', timestamp: '2026-08-29T09:00:00Z', action: 'IDA membership confirmed', performedBy: 'ops@nutriplan.in' },
      { id: 'b3', timestamp: '2026-08-29T09:10:00Z', action: 'NCAHP lookup — No reg number. Manual verification initiated.', performedBy: 'ops@nutriplan.in' },
    ],
  },
  {
    id: 'nut-003',
    name: 'Rajan Pillai',
    email: 'rajan.pillai@example.in',
    phone: '+91-97654-32109',
    degreeInstitution: 'Madras University (SNDT affiliated)',
    degreeYear: '2022',
    specialties: ['Thyroid', 'Post-partum', 'Vegetarian Nutrition'],
    bio: 'Nutritionist running a WhatsApp-based practice with 80+ clients.',
    experienceYears: 3,
    hourlyRateUsd: 50,
    docs: [
      { name: 'Rajan_Pillai_BSc_Food_Science.pdf', size: '4.5 MB', uploadedAt: '2026-09-01T14:00:00Z', type: 'degree' },
      { name: 'Passport_Copy.pdf', size: '0.6 MB', uploadedAt: '2026-09-01T14:01:00Z', type: 'id' },
    ],
    status: 'needs_info',
    badgeTier: 'pending',
    appliedAt: '2026-09-01T14:00:00Z',
    lastUpdatedAt: '2026-09-03T10:00:00Z',
    ncahpLookupStatus: null,
    idaLookupStatus: null,
    opsNotes: 'Degree doc is blurry. Requested reupload. No NCAHP/IDA registration provided.',
    auditLog: [
      { id: 'c1', timestamp: '2026-09-01T14:00:00Z', action: 'Application submitted', performedBy: 'rajan.pillai@example.in' },
      { id: 'c2', timestamp: '2026-09-03T10:00:00Z', action: 'Status → Needs Info — Degree doc blurry', performedBy: 'ops@nutriplan.in', note: 'Email sent requesting clear scan' },
    ],
  },
  {
    id: 'nut-004',
    name: 'Anjali Gupta',
    email: 'anjali.g@nutrition.co',
    ncahpRegNumber: 'NCAHP-2025-UP-009134',
    degreeInstitution: 'BHU — Banaras Hindu University',
    degreeYear: '2020',
    specialties: ['Renal (CKD)', 'Diabetes', 'Clinical Nutrition'],
    bio: 'Hospital-trained clinical dietitian. 6 years at SGPGI Lucknow.',
    experienceYears: 6,
    hourlyRateUsd: 85,
    docs: [
      { name: 'Anjali_Gupta_MSc_Clinical_Nutrition.pdf', size: '2.8 MB', uploadedAt: '2026-09-06T11:00:00Z', type: 'degree' },
      { name: 'NCAHP_Certificate_2025.pdf', size: '1.2 MB', uploadedAt: '2026-09-06T11:01:00Z', type: 'registration' },
      { name: 'SGPGI_Experience_Letter.pdf', size: '0.9 MB', uploadedAt: '2026-09-06T11:02:00Z', type: 'other' },
    ],
    status: 'pending_review',
    badgeTier: 'pending',
    appliedAt: '2026-09-06T11:00:00Z',
    lastUpdatedAt: '2026-09-06T11:00:00Z',
    ncahpLookupStatus: 'pending_manual',
    idaLookupStatus: null,
    opsNotes: '',
    auditLog: [
      { id: 'd1', timestamp: '2026-09-06T11:00:00Z', action: 'Application submitted', performedBy: 'anjali.g@nutrition.co' },
    ],
  },
]

export const useVerificationStore = defineStore('verification', () => {
  const applications = ref<NutritionistApplication[]>([...SEED_APPLICATIONS])
  const isLoading = ref(false)

  const pendingCount = computed(() => applications.value.filter(a => a.status === 'pending_review').length)
  const needsInfoCount = computed(() => applications.value.filter(a => a.status === 'needs_info').length)
  const verifiedCount = computed(() => applications.value.filter(a => a.status === 'verified').length)
  const totalCount = computed(() => applications.value.length)

  function getById(id: string) {
    return applications.value.find(a => a.id === id) ?? null
  }

  function approveApplication(id: string, tier: BadgeTier, opsNote: string, performedBy = 'ops@nutriplan.in') {
    const app = getById(id)
    if (!app) return
    app.status = 'verified'
    app.badgeTier = tier
    app.opsNotes = opsNote
    app.lastUpdatedAt = new Date().toISOString()
    app.auditLog.push({
      id: `audit-${Date.now()}`,
      timestamp: new Date().toISOString(),
      action: `Status → Verified · Badge: ${tierLabel(tier)}`,
      performedBy,
      note: opsNote || undefined,
    })
  }

  function requestMoreInfo(id: string, note: string, performedBy = 'ops@nutriplan.in') {
    const app = getById(id)
    if (!app) return
    app.status = 'needs_info'
    app.badgeTier = 'pending'
    app.opsNotes = note
    app.lastUpdatedAt = new Date().toISOString()
    app.auditLog.push({ id: `audit-${Date.now()}`, timestamp: new Date().toISOString(), action: 'Status → Needs Info', performedBy, note })
  }

  function rejectApplication(id: string, reason: string, performedBy = 'ops@nutriplan.in') {
    const app = getById(id)
    if (!app) return
    app.status = 'rejected'
    app.badgeTier = 'none'
    app.opsNotes = reason
    app.lastUpdatedAt = new Date().toISOString()
    app.auditLog.push({ id: `audit-${Date.now()}`, timestamp: new Date().toISOString(), action: 'Status → Rejected', performedBy, note: reason })
  }

  function revokeVerification(id: string, reason: string, performedBy = 'ops@nutriplan.in') {
    const app = getById(id)
    if (!app) return
    app.status = 'pending_review'
    app.badgeTier = 'pending'
    app.opsNotes = reason
    app.lastUpdatedAt = new Date().toISOString()
    app.auditLog.push({ id: `audit-${Date.now()}`, timestamp: new Date().toISOString(), action: 'Verification Revoked → Pending Review', performedBy, note: reason })
  }

  function setNcahpLookup(id: string, result: 'found' | 'not_found', performedBy = 'ops@nutriplan.in') {
    const app = getById(id)
    if (!app) return
    app.ncahpLookupStatus = result
    app.lastUpdatedAt = new Date().toISOString()
    app.auditLog.push({ id: `audit-${Date.now()}`, timestamp: new Date().toISOString(), action: `NCAHP Lookup — ${result === 'found' ? '✓ Found' : '✗ Not Found'}`, performedBy })
  }

  function setIdaLookup(id: string, result: 'found' | 'not_found', performedBy = 'ops@nutriplan.in') {
    const app = getById(id)
    if (!app) return
    app.idaLookupStatus = result
    app.lastUpdatedAt = new Date().toISOString()
    app.auditLog.push({ id: `audit-${Date.now()}`, timestamp: new Date().toISOString(), action: `IDA Lookup — ${result === 'found' ? '✓ Found' : '✗ Not Listed'}`, performedBy })
  }

  async function submitApplication(form: any) {
    isLoading.value = true
    try {
      try { await apiClient.post('/marketplace/nutritionists/apply', form) } catch {}
      const newApp: NutritionistApplication = {
        id: `nut-${Date.now()}`,
        ...form,
        docs: [],
        status: 'pending_review',
        badgeTier: 'pending',
        appliedAt: new Date().toISOString(),
        lastUpdatedAt: new Date().toISOString(),
        ncahpLookupStatus: form.ncahpRegNumber ? 'pending_manual' : null,
        idaLookupStatus: form.idaMembershipNumber ? 'pending_manual' : null,
        opsNotes: '',
        auditLog: [{ id: `audit-${Date.now()}`, timestamp: new Date().toISOString(), action: 'Application submitted', performedBy: form.email }],
      }
      applications.value.unshift(newApp)
      return { success: true, id: newApp.id }
    } finally {
      isLoading.value = false
    }
  }

  return {
    applications, isLoading,
    pendingCount, needsInfoCount, verifiedCount, totalCount,
    getById, approveApplication, requestMoreInfo, rejectApplication,
    revokeVerification, setNcahpLookup, setIdaLookup, submitApplication,
  }
})

export function tierLabel(tier: BadgeTier): string {
  const map: Record<BadgeTier, string> = {
    ncahp_verified: 'NCAHP Verified (Gold)', ida_verified: 'IDA Registered Dietitian (Silver)',
    degree_verified: 'Degree Verified (Bronze)', pending: 'Pending Verification', none: 'Unverified',
  }
  return map[tier]
}

export function statusLabel(status: VerificationStatus): string {
  const map: Record<VerificationStatus, string> = {
    verified: 'Verified', pending_review: 'Pending Review', needs_info: 'Needs More Info',
    rejected: 'Rejected', unverified: 'Not Applied',
  }
  return map[status]
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
