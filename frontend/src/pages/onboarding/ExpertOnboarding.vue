<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../../components/ui/Button.vue'
import VerificationBadge from '../../components/VerificationBadge.vue'
import { useVerificationStore } from '../../stores/verification'

const router = useRouter()
const store = useVerificationStore()

const step = ref<1 | 2 | 3>(1)
const isSubmitting = ref(false)
const submittedAppId = ref<string | null>(null)
const errorMsg = ref('')

const form = ref({
  name: '',
  email: '',
  phone: '',
  bio: '',
  hourlyRateUsd: 80,
  experienceYears: 1,
  specialties: [] as string[],
  ncahpRegNumber: '',
  idaMembershipNumber: '',
  degreeInstitution: '',
  degreeYear: '',
  degreeDigilockerRef: '',
  sampleCases: '',
  newSpecialty: '',
})

const SPECIALTY_OPTIONS = [
  'Diabetes', 'PCOS', 'Weight Loss', 'Keto', 'Sports Nutrition',
  'Gut Health', 'Thyroid', 'Metabolic Health', 'Vegetarian Nutrition',
  'Post-partum', 'Renal (CKD)', 'Hypertrophy', 'Fat Loss', 'Clinical Nutrition',
]

const isStep1Valid = computed(() =>
  form.value.name.trim().length > 2 &&
  form.value.email.trim().includes('@') &&
  form.value.bio.trim().length > 30 &&
  form.value.experienceYears >= 1
)

const isStep2Valid = computed(() =>
  form.value.degreeInstitution.trim().length > 3 &&
  form.value.degreeYear.length === 4
)

function toggleSpecialty(s: string) {
  const idx = form.value.specialties.indexOf(s)
  if (idx === -1) form.value.specialties.push(s)
  else form.value.specialties.splice(idx, 1)
}

function addCustomSpecialty() {
  const v = form.value.newSpecialty.trim()
  if (v && !form.value.specialties.includes(v)) form.value.specialties.push(v)
  form.value.newSpecialty = ''
}

async function submit() {
  if (!isStep1Valid.value || !isStep2Valid.value) return
  isSubmitting.value = true
  errorMsg.value = ''
  try {
    const result = await store.submitApplication({
      name: form.value.name,
      email: form.value.email,
      phone: form.value.phone,
      bio: form.value.bio,
      hourlyRateUsd: form.value.hourlyRateUsd,
      experienceYears: form.value.experienceYears,
      specialties: form.value.specialties,
      ncahpRegNumber: form.value.ncahpRegNumber || undefined,
      idaMembershipNumber: form.value.idaMembershipNumber || undefined,
      degreeInstitution: form.value.degreeInstitution,
      degreeYear: form.value.degreeYear,
      degreeDigilockerRef: form.value.degreeDigilockerRef || undefined,
      sampleCases: form.value.sampleCases || undefined,
    })
    if (result.success) {
      submittedAppId.value = result.id
      step.value = 3
    }
  } catch (e: any) {
    errorMsg.value = e.message ?? 'Submission failed. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}

// Timeline steps for status tracker
const timeline = [
  { id: 'submitted',  label: 'Application Submitted',     type: 'doc',    desc: 'Your credentials are in the queue.' },
  { id: 'registry',  label: 'Registry Check',             type: 'check',  desc: 'Ops checks NCAHP Central Register + IDA directory.' },
  { id: 'degree',    label: 'Degree Verification',        type: 'degree', desc: 'University confirms your qualification.' },
  { id: 'approved',  label: 'Badge Issued',               type: 'badge',  desc: 'Verified badge appears on your public profile.' },
]
</script>

<template>
  <div class="expert-onboard">

    <!-- Progress bar -->
    <div v-if="step < 3" class="progress-wrap">
      <div class="progress-steps">
        <div
          v-for="(label, i) in ['Your Profile', 'Credentials & Verification', 'Under Review']"
          :key="i"
          class="progress-step"
          :class="{ 'progress-step--done': step > i + 1, 'progress-step--active': step === i + 1 }"
        >
          <div class="ps-circle">{{ step > i + 1 ? '✓' : i + 1 }}</div>
          <span class="ps-label">{{ label }}</span>
        </div>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${((step - 1) / 2) * 100}%` }" />
      </div>
    </div>

    <!-- ── STEP 1: Profile ──────────────────────────────────────────────── -->
    <div v-if="step === 1" class="step-card">
      <div class="step-header">
        <div class="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0 border border-primary/20">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <div>
          <h2 class="step-title">Join as a Nutrition Expert</h2>
          <p class="step-sub">Build your profile. Credentials are verified in Step 2 — we follow NCAHP &amp; IDA standards.</p>
        </div>
      </div>

      <div class="form-grid">
        <div class="form-field">
          <label class="form-label">Full Name *</label>
          <input v-model="form.name" class="form-input" placeholder="Dr. Priya Sharma" />
        </div>
        <div class="form-field">
          <label class="form-label">Email Address *</label>
          <input v-model="form.email" type="email" class="form-input" placeholder="you@example.com" />
        </div>
        <div class="form-field">
          <label class="form-label">Phone (WhatsApp preferred)</label>
          <input v-model="form.phone" class="form-input" placeholder="+91-98765-43210" />
        </div>
        <div class="form-field">
          <label class="form-label">Years of Experience *</label>
          <input v-model.number="form.experienceYears" type="number" min="1" class="form-input" />
        </div>
        <div class="form-field form-field--full">
          <label class="form-label">Professional Bio * <span class="form-hint">(min 30 chars)</span></label>
          <textarea v-model="form.bio" class="form-textarea" rows="3" placeholder="Describe your clinical background, patient outcomes, and approach…" />
        </div>
        <div class="form-field">
          <label class="form-label">Consultation Rate (USD/hr)</label>
          <input v-model.number="form.hourlyRateUsd" type="number" min="20" class="form-input" />
          <span class="form-hint-block">≈ ₹{{ Math.round(form.hourlyRateUsd * 84) }}/hr · Platform takes 15–20% commission</span>
        </div>
      </div>

      <!-- Specialties -->
      <div class="form-section">
        <label class="form-label">Specializations</label>
        <div class="specialty-grid">
          <button
            v-for="s in SPECIALTY_OPTIONS"
            :key="s"
            class="spec-btn"
            :class="{ 'spec-btn--on': form.specialties.includes(s) }"
            type="button"
            @click="toggleSpecialty(s)"
          >{{ s }}</button>
        </div>
        <div class="custom-spec-row">
          <input v-model="form.newSpecialty" class="form-input" placeholder="Add custom specialization…" @keyup.enter="addCustomSpecialty" />
          <Button variant="outline" size="sm" @click="addCustomSpecialty">Add</Button>
        </div>
        <div v-if="form.specialties.length" class="selected-chips">
          <span v-for="s in form.specialties" :key="s" class="selected-chip">
            {{ s }}
            <button class="chip-remove" @click="toggleSpecialty(s)">×</button>
          </span>
        </div>
      </div>

      <div class="step-footer">
        <Button :disabled="!isStep1Valid" @click="step = 2">Continue to Credentials →</Button>
      </div>
    </div>

    <!-- ── STEP 2: Credentials ──────────────────────────────────────────── -->
    <div v-else-if="step === 2" class="step-card">
      <div class="step-header">
        <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center shrink-0 border border-emerald-500/20">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
        </div>
        <div>
          <h2 class="step-title">Credential Verification</h2>
          <p class="step-sub">We check NCAHP Central Register &amp; IDA directory. Provide as much as you have — more = faster Gold badge.</p>
        </div>
      </div>

      <!-- Badge tier explainer -->
      <div class="tier-explainer">
        <div class="tier-ex-title">Which badge will you receive?</div>
        <div class="tier-ex-cards">
          <div class="tier-ex-card">
            <VerificationBadge tier="ncahp_verified" status="verified" size="sm" />
            <p class="tier-ex-desc">Provide your NCAHP registration number → Gold badge (fastest trust signal)</p>
          </div>
          <div class="tier-ex-card">
            <VerificationBadge tier="ida_verified" status="verified" size="sm" />
            <p class="tier-ex-desc">IDA RD membership number → Silver badge</p>
          </div>
          <div class="tier-ex-card">
            <VerificationBadge tier="degree_verified" status="verified" size="sm" />
            <p class="tier-ex-desc">Degree-only (no registry number yet) → Bronze badge after university confirms</p>
          </div>
        </div>
      </div>

      <div class="form-grid">
        <!-- NCAHP -->
        <div class="form-field form-field--full">
          <label class="form-label">
            NCAHP Registration Number
            <a href="https://ncahp.abdm.gov.in" target="_blank" rel="noopener" class="form-ext-link">Check Register ↗</a>
          </label>
          <input v-model="form.ncahpRegNumber" class="form-input" placeholder="NCAHP-2024-XX-000000  (leave blank if not yet registered)" />
          <span class="form-hint-block">Under NCAHP Act 2021. Not registered yet? Leave blank — IDA or degree verification applies.</span>
        </div>

        <!-- IDA -->
        <div class="form-field form-field--full">
          <label class="form-label">IDA Membership Number (Registered Dietitian)</label>
          <input v-model="form.idaMembershipNumber" class="form-input" placeholder="IDA-YYYY-ST-NNNNN  (optional)" />
        </div>

        <!-- Degree -->
        <div class="form-field">
          <label class="form-label">Degree Institution *</label>
          <input v-model="form.degreeInstitution" class="form-input" placeholder="e.g. AIIMS Delhi, St. John's Bangalore" />
        </div>
        <div class="form-field">
          <label class="form-label">Year of Graduation *</label>
          <input v-model="form.degreeYear" class="form-input" placeholder="e.g. 2019" maxlength="4" />
        </div>
        <div class="form-field form-field--full">
          <label class="form-label">DigiLocker Reference (if degree is on DigiLocker)</label>
          <input v-model="form.degreeDigilockerRef" class="form-input" placeholder="DL-XXXXXXXX  (optional, speeds verification)" />
        </div>

        <!-- Sample cases -->
        <div class="form-field form-field--full">
          <label class="form-label">Sample Clinical Cases (optional but recommended)</label>
          <textarea v-model="form.sampleCases" class="form-textarea" rows="3" placeholder="Describe 1–2 anonymized patient outcomes that demonstrate your clinical impact…" />
        </div>
      </div>

      <!-- Doc upload notice -->
      <div class="doc-notice">
        <span class="w-6 h-6 rounded bg-primary/10 text-primary flex items-center justify-center shrink-0">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </span>
        <div>
          <div class="doc-notice-title">Document Upload</div>
          <div class="doc-notice-sub">After submitting, you'll receive an email with a secure link to upload your degree certificate, NCAHP/IDA registration certificate, and a masked government ID. All documents are reviewed by our ops team within 2–5 business days.</div>
        </div>
      </div>

      <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

      <div class="step-footer">
        <Button variant="outline" @click="step = 1">← Back</Button>
        <Button :disabled="!isStep2Valid || isSubmitting" @click="submit">
          {{ isSubmitting ? 'Submitting…' : 'Submit Application →' }}
        </Button>
      </div>
    </div>

    <!-- ── STEP 3: Submitted / Status Tracker ──────────────────────────── -->
    <div v-else-if="step === 3" class="step-card step-card--success">
      <div class="success-hero">
        <div class="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-600 flex items-center justify-center mx-auto mb-2">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <h2 class="step-title">Application Submitted</h2>
        <p class="step-sub">
          Thank you, <strong>{{ form.name }}</strong>. Our clinical verification team will review your credentials
          and issue your badge within 2–5 business days.
        </p>
        <VerificationBadge tier="pending" status="pending_review" size="lg" />
      </div>

      <!-- Timeline -->
      <div class="status-timeline">
        <div class="timeline-title">Your Verification Journey</div>
        <div class="timeline-steps">
          <div
            v-for="(ts, idx) in timeline"
            :key="ts.id"
            class="timeline-step"
            :class="{
              'timeline-step--done': idx === 0,
              'timeline-step--active': idx === 1,
            }"
          >
            <div class="ts-dot-wrap">
              <div class="ts-dot">
                <svg v-if="idx === 0" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                <span v-else class="text-[0.7rem] font-bold">{{ idx + 1 }}</span>
              </div>
              <div v-if="idx < timeline.length - 1" class="ts-connector" />
            </div>
            <div class="ts-body">
              <div class="ts-label">{{ ts.label }}</div>
              <div class="ts-desc">{{ ts.desc }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- What to expect -->
      <div class="expect-card">
        <div class="expect-title flex items-center gap-1.5">
          <svg class="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          What happens next?
        </div>
        <ul class="expect-list">
          <li>You'll receive an email with a <strong>secure document upload link</strong> within 30 minutes.</li>
          <li>Our ops team will cross-check your
            <strong>NCAHP registration</strong>{{ form.ncahpRegNumber ? ` (${form.ncahpRegNumber})` : '' }}
            {{ form.idaMembershipNumber ? ` and IDA membership (${form.idaMembershipNumber})` : '' }} against official directories.</li>
          <li>If we need clarification, you'll get an email with specific questions — no mystery requests.</li>
          <li>Once verified, your <strong>badge appears instantly</strong> on your public profile and in search results.</li>
        </ul>
      </div>

      <div class="step-footer step-footer--center">
        <Button variant="outline" @click="router.push('/expert/dashboard')">Go to Expert Dashboard</Button>
        <Button @click="router.push('/dashboard')">Back to App →</Button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.expert-onboard {
  max-width: 720px; margin: 0 auto;
  padding: 32px 20px;
  display: flex; flex-direction: column; gap: 24px;
}

/* Progress */
.progress-wrap { display: flex; flex-direction: column; gap: 12px; }
.progress-steps { display: flex; justify-content: space-between; }
.progress-step { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; }
.ps-circle {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700;
  background: var(--color-canvas-raised, #1e293b);
  border: 2px solid var(--color-border, rgba(255,255,255,0.1));
  color: var(--color-ink-muted, #94a3b8);
  transition: all 0.2s;
}
.progress-step--active .ps-circle { border-color: #4F46E5; background: rgba(99,102,241,0.2); color: #818CF8; }
.progress-step--done  .ps-circle { border-color: #10B981; background: rgba(16,185,129,0.2); color: #10B981; }
.ps-label { font-size: 0.72rem; color: var(--color-ink-muted, #94a3b8); text-align: center; }
.progress-step--active .ps-label { color: #818CF8; font-weight: 600; }
.progress-step--done  .ps-label  { color: #10B981; }

.progress-bar { height: 4px; background: var(--color-border, rgba(255,255,255,0.08)); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #4F46E5, #7C3AED); border-radius: 2px; transition: width 0.4s ease; }

/* Step card */
.step-card {
  background: var(--color-canvas-raised, #1e293b);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 20px; padding: 28px 28px 24px;
  display: flex; flex-direction: column; gap: 20px;
}
.step-card--success { border-color: rgba(16,185,129,0.3); background: rgba(16,185,129,0.04); }

.step-header { display: flex; gap: 16px; align-items: flex-start; }
.step-emoji { font-size: 40px; }
.step-title { font-size: 1.4rem; font-weight: 800; color: var(--color-ink, #f1f5f9); }
.step-sub { font-size: 0.875rem; color: var(--color-ink-muted, #94a3b8); margin-top: 4px; line-height: 1.5; }

/* Forms */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-field--full { grid-column: 1 / -1; }
.form-label { font-size: 0.78rem; font-weight: 600; color: var(--color-ink-muted, #94a3b8); display: flex; align-items: center; gap: 8px; }
.form-hint { font-weight: 400; font-size: 0.7rem; }
.form-ext-link { font-size: 0.7rem; color: #818CF8; text-decoration: none; }
.form-ext-link:hover { text-decoration: underline; }
.form-input {
  padding: 10px 14px; border-radius: 10px;
  background: var(--color-canvas, #0f172a);
  border: 1px solid var(--color-border, rgba(255,255,255,0.1));
  color: var(--color-ink, #f1f5f9); font-size: 0.9rem; outline: none; transition: border-color 0.15s;
}
.form-input:focus { border-color: rgba(99,102,241,0.6); }
.form-input::placeholder { color: rgba(148,163,184,0.5); }
.form-textarea { @extend .form-input; resize: vertical; }
.form-textarea {
  padding: 10px 14px; border-radius: 10px;
  background: var(--color-canvas, #0f172a);
  border: 1px solid var(--color-border, rgba(255,255,255,0.1));
  color: var(--color-ink, #f1f5f9); font-size: 0.9rem; outline: none; transition: border-color 0.15s; resize: vertical;
}
.form-textarea:focus { border-color: rgba(99,102,241,0.6); }
.form-hint-block { font-size: 0.68rem; color: rgba(148,163,184,0.6); }

.form-section { display: flex; flex-direction: column; gap: 10px; }

/* Specialties */
.specialty-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.spec-btn {
  padding: 5px 12px; border-radius: 8px; font-size: 0.78rem; font-weight: 500;
  cursor: pointer; border: 1px solid var(--color-border, rgba(255,255,255,0.1));
  background: var(--color-canvas, #0f172a); color: var(--color-ink-muted, #94a3b8);
  transition: all 0.15s;
}
.spec-btn:hover { border-color: rgba(99,102,241,0.4); color: #818CF8; }
.spec-btn--on { background: rgba(99,102,241,0.15); border-color: #4F46E5; color: #818CF8; font-weight: 700; }

.custom-spec-row { display: flex; gap: 8px; align-items: center; }
.selected-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.selected-chip {
  display: flex; align-items: center; gap: 4px;
  padding: 3px 10px 3px 10px; border-radius: 20px;
  background: rgba(99,102,241,0.15); color: #818CF8;
  font-size: 0.78rem; font-weight: 600; border: 1px solid rgba(99,102,241,0.3);
}
.chip-remove { background: none; border: none; color: #818CF8; cursor: pointer; font-size: 14px; padding: 0 0 0 2px; }

/* Tier explainer */
.tier-explainer {
  background: var(--color-canvas, #0f172a);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 14px; padding: 16px 18px;
}
.tier-ex-title { font-size: 0.78rem; font-weight: 700; color: var(--color-ink-muted, #94a3b8); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
.tier-ex-cards { display: flex; gap: 12px; flex-wrap: wrap; }
.tier-ex-card { display: flex; flex-direction: column; gap: 7px; flex: 1; min-width: 150px; }
.tier-ex-desc { font-size: 0.72rem; color: rgba(148,163,184,0.7); line-height: 1.4; }

/* Doc notice */
.doc-notice {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 14px 16px; border-radius: 12px;
  background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.2);
}
.doc-notice-icon { font-size: 20px; }
.doc-notice-title { font-size: 0.85rem; font-weight: 700; color: #FBBF24; }
.doc-notice-sub { font-size: 0.75rem; color: rgba(148,163,184,0.8); margin-top: 3px; line-height: 1.5; }

.error-msg { padding: 10px 14px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 10px; color: #F87171; font-size: 0.85rem; }

.step-footer { display: flex; gap: 12px; justify-content: flex-end; }
.step-footer--center { justify-content: center; }

/* Success step */
.success-hero { display: flex; flex-direction: column; align-items: center; gap: 10px; text-align: center; }
.success-icon { font-size: 52px; }

/* Timeline */
.status-timeline {
  background: var(--color-canvas, #0f172a);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 14px; padding: 18px 20px;
}
.timeline-title { font-size: 0.78rem; font-weight: 700; color: var(--color-ink-muted, #94a3b8); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px; }
.timeline-steps { display: flex; flex-direction: column; gap: 0; }
.timeline-step { display: flex; gap: 16px; }
.ts-dot-wrap { display: flex; flex-direction: column; align-items: center; gap: 0; }
.ts-dot {
  width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; z-index: 1;
  background: var(--color-canvas-raised, #1e293b);
  border: 2px solid var(--color-border, rgba(255,255,255,0.1));
  color: var(--color-ink-muted, #94a3b8);
}
.timeline-step--done  .ts-dot { background: rgba(16,185,129,0.2); border-color: #10B981; color: #10B981; }
.timeline-step--active .ts-dot { background: rgba(251,191,36,0.15); border-color: #FBBF24; color: #FBBF24; animation: badge-pulse 2s ease-in-out infinite; }
@keyframes badge-pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }

.ts-connector { flex: 1; width: 2px; background: var(--color-border, rgba(255,255,255,0.08)); margin: 4px 0; min-height: 24px; }

.ts-body { padding: 6px 0 18px; }
.ts-label { font-size: 0.9rem; font-weight: 700; color: var(--color-ink, #f1f5f9); }
.timeline-step--done  .ts-label { color: #10B981; }
.timeline-step--active .ts-label { color: #FBBF24; }
.ts-desc { font-size: 0.75rem; color: var(--color-ink-muted, #94a3b8); margin-top: 2px; line-height: 1.4; }

/* Expect card */
.expect-card {
  padding: 16px 18px; border-radius: 12px;
  background: rgba(99,102,241,0.06); border: 1px solid rgba(99,102,241,0.2);
}
.expect-title { font-size: 0.9rem; font-weight: 700; color: #818CF8; margin-bottom: 10px; }
.expect-list { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 7px; }
.expect-list li { font-size: 0.82rem; color: var(--color-ink-muted, #94a3b8); line-height: 1.5; }
.expect-list strong { color: var(--color-ink, #f1f5f9); }
</style>
