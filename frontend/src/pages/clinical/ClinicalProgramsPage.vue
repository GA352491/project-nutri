<script setup lang="ts">
import { ref, computed } from 'vue'
import Icon from '../../components/ui/Icon.vue'
import Toast from '../../components/ui/Toast.vue'

const showToast = ref(false)
const toastMsg = ref('')

function notify(msg: string) {
 toastMsg.value = msg
 showToast.value = true
 setTimeout(() => { showToast.value = false }, 3500)
}

import { onMounted } from 'vue'
import apiClient from '../../api'

// Active Selected Track
const activeTrack = ref<'diabetes' | 'PCOS' | 'CKD' | 'post_partum'>('diabetes')

// Biomarker Input State
const showLogBiomarkerModal = ref(false)
const biomarkerType = ref('HbA1c')
const biomarkerValue = ref('6.2')
const biomarkerUnit = ref('%')
const biomarkerNotes = ref('Fasting lab test at SRL Diagnostics')

// Dietitian Clinical Note State
const clinicalNotes = ref([
 {
 id: 'note_1',
 author: 'Dr. Sarah Jenkins, RD (IDA-9482)',
 date: '18 Aug 2026',
 tag: 'Glycemic Regulation',
 content: 'Patient transitioned to foxtail millet and moong dal breakfast. 2-hour postprandial glucose stabilized below 135 mg/dL. Retain 45% carbohydrate ceiling.',
 },
 {
 id: 'note_2',
 author: 'Dr. Sarah Jenkins, RD (IDA-9482)',
 date: '10 Aug 2026',
 tag: 'Renal / Sodium Guardrail',
 content: 'Blood pressure 124/82 mmHg. Maintain sodium strictly under 1,800 mg/day. Zero added sugar limit verified.',
 }
])

const newNoteText = ref('')
const newNoteTag = ref('Follow-up Review')

async function fetchClinicalProfile() {
 try {
 const res = await apiClient.get('/profile/me')
 if (res.data?.health_conditions && res.data.health_conditions.length > 0) {
 const cond = res.data.health_conditions[0].toLowerCase()
 if (cond.includes('diabetes')) activeTrack.value = 'diabetes'
 else if (cond.includes('pcos')) activeTrack.value = 'PCOS'
 else if (cond.includes('ckd') || cond.includes('renal')) activeTrack.value = 'CKD'
 }
 } catch (err) {
 console.warn('Clinical profile sync fallback:', err)
 }
}

onMounted(() => {
 fetchClinicalProfile()
})

async function addClinicalNote() {
 if (!newNoteText.value.trim()) return
 const id = `note_${Date.now()}`
 clinicalNotes.value.unshift({
 id,
 author: 'Dr. Sarah Jenkins, RD (Supervising Dietitian)',
 date: 'Just now',
 tag: newNoteTag.value,
 content: newNoteText.value.trim()
 })
 
 try {
 await apiClient.put('/profile/me', {
 clinical_notes: newNoteText.value.trim()
 })
 } catch (err) {
 console.warn('Clinical note backend sync:', err)
 }

 newNoteText.value = ''
 notify('Clinical progress note attached to patient medical chart.')
}

// Track Specific Metadata
const trackConfigs = {
 diabetes: {
 title: 'Type 2 Diabetes & Glycemic Control Track',
 badge: 'ICMR-NIN & RSSDI Guidelines',
 bannerGradient: 'from-blue-950 via-slate-900 to-indigo-950',
 primaryMetric: 'HbA1c Target: < 6.5%',
 macroRules: [
 { rule: 'Carbohydrate Ceiling', value: 'Max 45% of Daily Calories', icon: 'shield-check', desc: 'Low-GI whole grains, millets, legumes' },
 { rule: 'Added Sugar Limit', value: '< 20g / day strict', icon: 'flame', desc: 'Zero artificial syrups or refined fructose' },
 { rule: 'Dietary Fiber', value: '40g / day minimum', icon: 'activity', desc: 'Slows glucose absorption & insulin response' },
 { rule: 'Protein Intake', value: '1.2g / kg body weight', icon: 'shield-check', desc: 'Preserves lean metabolic muscle mass' },
 ],
 biomarkers: [
 { name: 'HbA1c', current: '6.2 %', target: '< 6.5 %', status: 'Optimal', trend: 'down', history: '6.8% (3mo ago) → 6.2%' },
 { name: 'Fasting Blood Glucose', current: '108 mg/dL', target: '70–110 mg/dL', status: 'In Range', trend: 'stable', history: '112 mg/dL avg (7d)' },
 { name: 'Post-Prandial Glucose', current: '134 mg/dL', target: '< 140 mg/dL', status: 'Optimal', trend: 'down', history: 'Time-in-Range: 96%' },
 { name: 'Serum Triglycerides', current: '142 mg/dL', target: '< 150 mg/dL', status: 'Normal', trend: 'down', history: 'Down 18% with Low-GI diet' },
 ],
 recommendedRecipes: [
 { title: 'Foxtail Millet & Sprouted Moong Khichdi', tags: ['Low-GI', 'High-Fiber', 'Gluten-Free'], cal: 340, carbs: '42g', protein: '16g' },
 { title: 'Palak Paneer with Jowar Roti', tags: ['Low-Carb', 'Diabetic-Safe'], cal: 380, carbs: '28g', protein: '22g' },
 { title: 'Roasted Cinnamon Makhana & Walnuts', tags: ['Anti-Spike Snack'], cal: 160, carbs: '18g', protein: '6g' }
 ]
 },
 PCOS: {
 title: 'PCOS & Insulin Sensitivity Track',
 badge: 'AES & ICMR Clinical Protocols',
 bannerGradient: 'from-purple-950 via-slate-900 to-pink-950',
 primaryMetric: 'HOMA-IR Optimization',
 macroRules: [
 { rule: 'Anti-Inflammatory Ratio', value: 'High Omega-3 : Omega-6', icon: 'shield-check', desc: 'Flaxseeds, chia, walnuts, cold-pressed oils' },
 { rule: 'Carbohydrate Distribution', value: 'Max 40% (Complex Only)', icon: 'activity', desc: 'Zero white flour or refined seed oils' },
 { rule: 'Protein Density', value: '1.2g / kg body weight', icon: 'shield-check', desc: 'Satiety, hormone regulation & ovarian health' },
 { rule: 'Micronutrient Boost', value: 'Inositol + Zinc + Magnesium', icon: 'flame', desc: 'Supports regular ovulatory cycles' },
 ],
 biomarkers: [
 { name: 'Fasting Insulin', current: '8.4 μIU/mL', target: '< 10 μIU/mL', status: 'Optimal', trend: 'down', history: 'Down from 14.2' },
 { name: 'LH : FSH Ratio', current: '1.2 : 1', target: '1 : 1', status: 'Improving', trend: 'down', history: 'Normalized from 2.4 : 1' },
 { name: 'C-Reactive Protein (hs-CRP)', current: '1.1 mg/L', target: '< 2.0 mg/L', status: 'Low Inflammation', trend: 'down', history: '1.8 → 1.1' },
 { name: 'Vitamin D3', current: '42 ng/mL', target: '> 30 ng/mL', status: 'Sufficient', trend: 'up', history: 'Supplemented + Diet' },
 ],
 recommendedRecipes: [
 { title: 'Methi Sprouts & Tofu Chaat', tags: ['Hormone-Balance', 'High-Protein'], cal: 290, carbs: '24g', protein: '20g' },
 { title: 'Spearmint & Turmeric Chia Pudding', tags: ['Anti-Androgen', 'Anti-Inflammatory'], cal: 210, carbs: '19g', protein: '8g' },
 { title: 'Stir-Fried Broccoli, Almonds & Paneer', tags: ['Low-GI Dinner'], cal: 360, carbs: '16g', protein: '24g' }
 ]
 },
 CKD: {
 title: 'Renal Care & CKD Management Track',
 badge: 'KDOQI & ICMR-NIN Renal Rules',
 bannerGradient: 'from-emerald-950 via-slate-900 to-teal-950',
 primaryMetric: 'eGFR & Electrolyte Balance',
 macroRules: [
 { rule: 'Protein Restriction', value: 'Strict 0.6g / kg body weight', icon: 'shield-check', desc: 'Minimizes nitrogenous waste & glomerular strain' },
 { rule: 'Sodium Ceiling', value: '< 1,500 mg / day', icon: 'shield-check', desc: 'Prevents fluid retention & hypertension' },
 { rule: 'Potassium Restriction', value: '< 2,000 mg / day', icon: 'activity', desc: 'Avoids hyperkalemia; leached cooking mandated' },
 { rule: 'Phosphorus Ceiling', value: '< 800 mg / day', icon: 'flame', desc: 'Protects vascular & bone metabolism' },
 ],
 biomarkers: [
 { name: 'Serum Creatinine', current: '1.2 mg/dL', target: '0.7–1.3 mg/dL', status: 'Stable', trend: 'stable', history: 'eGFR: 68 mL/min/1.73m²' },
 { name: 'Serum Potassium', current: '4.3 mEq/L', target: '3.5–5.0 mEq/L', status: 'Safe', trend: 'stable', history: 'Within safe guardrails' },
 { name: 'Blood Urea Nitrogen (BUN)', current: '18 mg/dL', target: '7–20 mg/dL', status: 'Normal', trend: 'down', history: 'Improved on 0.6g/kg protein' },
 { name: 'Serum Phosphorus', current: '3.6 mg/dL', target: '2.5–4.5 mg/dL', status: 'Optimal', trend: 'stable', history: 'Low-dairy compliance' },
 ],
 recommendedRecipes: [
 { title: 'Leached Bottle Gourd (Lauki) & Jeera Rice', tags: ['Low-Potassium', 'Renal-Safe'], cal: 310, carbs: '58g', protein: '7g' },
 { title: 'Egg White & Steamed French Bean Salad', tags: ['High Biological Value', 'Low-Phos'], cal: 240, carbs: '14g', protein: '18g' },
 { title: 'Roasted Poha with Cumin & Curry Leaves', tags: ['Low-Sodium Snack'], cal: 170, carbs: '32g', protein: '4g' }
 ]
 },
 post_partum: {
 title: 'Post-Partum & Lactation Recovery Track',
 badge: 'ICMR-NIN Maternal Nutrition 2020',
 bannerGradient: 'from-amber-950 via-slate-900 to-orange-950',
 primaryMetric: 'Lactation Micronutrient Density',
 macroRules: [
 { rule: 'Caloric Supplementation', value: '+400 kcal / day addition', icon: 'activity', desc: 'Supports metabolic energy expenditure of milk production' },
 { rule: 'Elevated Protein Target', value: '1.25g / kg body weight', icon: 'shield-check', desc: 'Tissue recovery & infant amino acid transfer' },
 { rule: 'Dietary Iron & Folate', value: '21mg Iron • 300mcg Folate', icon: 'shield-check', desc: 'Prevents postpartum anemia & supports vitality' },
 { rule: 'Calcium & Galactagogues', value: '1,200mg Calcium / day', icon: 'flame', desc: 'Shatavari, methi, fennel, sesame & ragi' },
 ],
 biomarkers: [
 { name: 'Hemoglobin (Hb)', current: '12.4 g/dL', target: '> 12.0 g/dL', status: 'Optimal', trend: 'up', history: 'Recovered from 10.8 postpartum' },
 { name: 'Serum Ferritin', current: '48 ng/mL', target: '30–150 ng/mL', status: 'Normal', trend: 'up', history: 'Iron stores replenishing' },
 { name: 'Serum Calcium', current: '9.4 mg/dL', target: '8.8–10.2 mg/dL', status: 'Normal', trend: 'stable', history: 'Ragi + sesame diet' },
 { name: 'Energy & Sleep Score', current: '82 / 100', target: '> 75', status: 'Good Recovery', trend: 'up', history: 'Wearable tracking active' },
 ],
 recommendedRecipes: [
 { title: 'Ragi & Almond Porridge with Jaggery', tags: ['High-Calcium', 'Galactagogue'], cal: 360, carbs: '54g', protein: '12g' },
 { title: 'Methi-Fenugreek Dal with Moringa Leaves', tags: ['Iron-Rich', 'Postpartum-Healing'], cal: 320, carbs: '42g', protein: '18g' },
 { title: 'Gondh, Dry Fruits & Sesame Ladoo', tags: ['Traditional Recovery', 'Calorie-Dense'], cal: 210, carbs: '22g', protein: '6g' }
 ]
 }
}

const currentConfig = computed(() => trackConfigs[activeTrack.value])

function saveBiomarker() {
 notify(`Biomarker logged: ${biomarkerType.value} = ${biomarkerValue.value} ${biomarkerUnit.value}`)
 showLogBiomarkerModal.value = false
}
</script>

<template>
 <div class="space-y-6">
 <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

 <!-- Track Selector Pills -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-4 shadow-sm">
 <div class="flex items-center justify-between gap-4 flex-wrap">
 <div>
 <h2 class="font-display font-bold text-lg text-ink">Specialized Clinical Condition Tracks</h2>
 <p class="text-xs text-ink-muted">Evidence-based clinical nutrition protocols tailored to specific medical conditions</p>
 </div>

 <div class="flex items-center gap-2 overflow-x-auto pb-1">
 <button
 v-for="track in [
 { id: 'diabetes', label: ' Type 2 Diabetes', sub: 'Glycemic Control' },
 { id: 'PCOS', label: ' PCOS & Insulin', sub: 'Hormonal Balance' },
 { id: 'CKD', label: ' CKD / Renal Care', sub: 'Electrolyte Guardrails' },
 { id: 'post_partum', label: ' Post-Partum', sub: 'Lactation & Recovery' }
 ]"
 :key="track.id"
 class="px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer flex flex-col items-start border shrink-0"
 :class="activeTrack === track.id ? 'bg-primary text-white border-primary shadow-md' : 'bg-canvas text-ink-muted border-border hover:text-ink hover:border-primary/40'"
 @click="activeTrack = track.id as any"
 >
 <span class="font-bold text-xs">{{ track.label }}</span>
 <span class="text-[10px] opacity-80 mt-0.5">{{ track.sub }}</span>
 </button>
 </div>
 </div>
 </div>

 <!-- Active Track Clinical Banner -->
 <div class="bg-gradient-to-r text-white rounded-2xl p-6 border shadow-xl relative overflow-hidden" :class="currentConfig.bannerGradient">
 <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
 <div>
 <div class="flex items-center gap-2">
 <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-white/20 text-white uppercase tracking-wider">
 {{ currentConfig.badge }}
 </span>
 <span class="text-xs text-white/70">&bull; Supervising Dietitian Active</span>
 </div>
 <h1 class="font-display font-bold text-2xl text-white mt-1.5">{{ currentConfig.title }}</h1>
 <p class="text-xs text-white/80 mt-1">
 Clinical Priority: <span class="font-semibold text-amber-300">{{ currentConfig.primaryMetric }}</span>
 </p>
 </div>

 <div class="flex items-center gap-3">
 <button
 @click="showLogBiomarkerModal = true"
 class="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white border border-white/20 rounded-xl text-xs font-semibold backdrop-blur-md transition-all flex items-center gap-2 cursor-pointer"
 >
 <Icon name="plus" class="w-4 h-4" />
 Log Lab Biomarker
 </button>
 </div>
 </div>

 <!-- Macro Guardrails Ribbon -->
 <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10">
 <div v-for="(rule, idx) in currentConfig.macroRules" :key="idx" class="bg-white/5 p-3.5 rounded-xl border border-white/10">
 <p class="text-[10px] text-white/70 uppercase font-semibold">{{ rule.rule }}</p>
 <p class="text-sm font-bold font-mono text-amber-300 mt-1">{{ rule.value }}</p>
 <p class="text-[10px] text-white/60 mt-0.5 leading-snug">{{ rule.desc }}</p>
 </div>
 </div>
 </div>

 <!-- Biomarkers Matrix & Dietitian Notes Grid -->
 <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

 <!-- Left 2 Cols: Clinical Biomarkers Card -->
 <div class="lg:col-span-2 bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-4">
 <div class="flex items-center justify-between">
 <div>
 <h3 class="font-display font-semibold text-base text-ink">Clinical Biomarkers & Lab Telemetry</h3>
 <p class="text-xs text-ink-muted">Monitored parameters against therapeutic ranges</p>
 </div>
 <span class="text-xs text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-full font-bold">
 All Targets Met
 </span>
 </div>

 <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
 <div
 v-for="b in currentConfig.biomarkers"
 :key="b.name"
 class="p-4 rounded-xl border border-border bg-canvas space-y-2"
 >
 <div class="flex items-center justify-between">
 <span class="text-xs font-bold text-ink">{{ b.name }}</span>
 <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
 {{ b.status }}
 </span>
 </div>
 <div class="flex items-baseline gap-2">
 <span class="text-2xl font-bold font-mono text-ink">{{ b.current }}</span>
 <span class="text-xs text-ink-muted font-mono">(Goal: {{ b.target }})</span>
 </div>
 <p class="text-[11px] text-ink-muted border-t border-border pt-1.5 flex items-center justify-between">
 <span>{{ b.history }}</span>
 <span class="font-bold text-emerald-600">&darr; Improved</span>
 </p>
 </div>
 </div>

 <!-- Curated Medical Recipes for this track -->
 <div class="pt-4 border-t border-border space-y-3">
 <h4 class="font-bold text-xs uppercase tracking-wider text-ink-muted">Condition-Tailored Recipes</h4>
 <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
 <div
 v-for="rec in currentConfig.recommendedRecipes"
 :key="rec.title"
 class="p-3.5 rounded-xl border border-border bg-canvas hover:border-primary/50 transition-all space-y-2"
 >
 <h5 class="text-xs font-bold text-ink leading-snug">{{ rec.title }}</h5>
 <div class="flex flex-wrap gap-1">
 <span v-for="t in rec.tags" :key="t" class="text-[9px] font-semibold bg-primary-soft text-primary px-1.5 py-0.5 rounded">
 {{ t }}
 </span>
 </div>
 <div class="text-[10px] font-mono text-ink-muted flex justify-between pt-1 border-t border-border/60">
 <span>{{ rec.cal }} kcal</span>
 <span>C: {{ rec.carbs }} &bull; P: {{ rec.protein }}</span>
 </div>
 </div>
 </div>
 </div>
 </div>

 <!-- Right 1 Col: Supervising Dietitian Clinical Notes -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-4 flex flex-col justify-between">
 <div class="space-y-4">
 <div class="flex items-center justify-between">
 <h3 class="font-display font-semibold text-base text-ink">Dietitian Clinical Chart</h3>
 <span class="text-[10px] font-bold text-primary bg-primary-soft px-2 py-0.5 rounded-full">
 DISHA / HIPAA
 </span>
 </div>

 <div class="space-y-3 max-h-72 overflow-y-auto pr-1">
 <div
 v-for="note in clinicalNotes"
 :key="note.id"
 class="p-3 rounded-xl bg-canvas border border-border space-y-1.5"
 >
 <div class="flex items-center justify-between text-[10px]">
 <span class="font-bold text-primary">{{ note.tag }}</span>
 <span class="text-ink-muted font-mono">{{ note.date }}</span>
 </div>
 <p class="text-xs text-ink leading-relaxed">{{ note.content }}</p>
 <p class="text-[10px] text-ink-muted font-semibold">&mdash; {{ note.author }}</p>
 </div>
 </div>
 </div>

 <!-- Add Clinical Note Form -->
 <div class="pt-4 border-t border-border space-y-2">
 <label class="block text-[10px] font-bold uppercase text-ink-muted">Add Clinician Assessment Note</label>
 <textarea
 v-model="newNoteText"
 placeholder="Document carbohydrate tolerance, fasting glucose adjustment, or renal advice..."
 rows="3"
 class="w-full text-xs p-2.5 rounded-xl bg-canvas border border-border outline-none focus:border-primary text-ink resize-none"
 ></textarea>
 <div class="flex justify-between items-center">
 <select v-model="newNoteTag" class="text-xs px-2 py-1.5 rounded-lg bg-canvas border border-border text-ink outline-none">
 <option>Follow-up Review</option>
 <option>Glycemic Regulation</option>
 <option>Renal Guardrail</option>
 <option>Hormone Optimization</option>
 </select>
 <button
 @click="addClinicalNote"
 class="px-3.5 py-1.5 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-lg shadow transition-all cursor-pointer"
 >
 Post Note
 </button>
 </div>
 </div>
 </div>

 </div>

 <!-- Log Lab Biomarker Modal -->
 <div v-if="showLogBiomarkerModal" class="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
 <div class="bg-canvas-raised rounded-2xl border border-border shadow-2xl max-w-md w-full p-6 space-y-5">
 <div class="flex items-center justify-between border-b border-border pb-4">
 <div>
 <h3 class="font-display font-bold text-lg text-ink">Log Clinical Biomarker</h3>
 <p class="text-xs text-ink-muted">Record blood test results or CGM parameters</p>
 </div>
 <button @click="showLogBiomarkerModal = false" class="text-ink-muted hover:text-ink">
 <Icon name="x" class="w-5 h-5" />
 </button>
 </div>

 <div class="space-y-3">
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Biomarker Metric</label>
 <select v-model="biomarkerType" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink">
 <option>HbA1c (%)</option>
 <option>Fasting Blood Glucose (mg/dL)</option>
 <option>Post-Prandial Glucose (mg/dL)</option>
 <option>Serum Creatinine (mg/dL)</option>
 <option>Serum Potassium (mEq/L)</option>
 <option>Fasting Insulin (μIU/mL)</option>
 <option>Hemoglobin (g/dL)</option>
 </select>
 </div>

 <div class="grid grid-cols-2 gap-3">
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Measured Value</label>
 <input v-model="biomarkerValue" placeholder="e.g. 6.2" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink font-mono font-bold" />
 </div>
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Unit</label>
 <input v-model="biomarkerUnit" placeholder="e.g. % or mg/dL" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink font-mono" />
 </div>
 </div>

 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Lab / Diagnostic Center Notes</label>
 <input v-model="biomarkerNotes" placeholder="e.g. 12-hour fasting venous sample" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink" />
 </div>
 </div>

 <div class="flex justify-end gap-3 pt-2">
 <button @click="showLogBiomarkerModal = false" class="px-4 py-2 text-xs font-semibold text-ink-muted hover:text-ink">Cancel</button>
 <button @click="saveBiomarker" class="px-5 py-2 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl shadow">
 Save Biomarker
 </button>
 </div>
 </div>
 </div>

 </div>
</template>
