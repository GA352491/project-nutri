<script setup lang="ts">
import { ref } from 'vue'
import Icon from '../ui/Icon.vue'

const props = defineProps<{
 isOpen: boolean
}>()

const emit = defineEmits<{
 (e: 'close'): void
}>()

const isGenerating = ref(false)
const downloadSuccess = ref(false)

const reportMeta = ref({
 patientName: 'Ananya Sharma',
 patientId: 'NP-9842-PT',
 period: 'Last 7 Days (13 Aug - 19 Aug 2026)',
 nutritionist: 'Dr. Ananya Iyer, RD (IDA-REG-2018-9482)',
 complianceScore: 94,
 avgCalories: 1971,
 avgProtein: 109,
 avgCarbs: 211,
 avgFat: 67,
 avgSteps: 8420,
 cgmAvgGlucose: '112 mg/dL',
 glucoseInRange: '96%'
})

function generateAndPrintPDF() {
 isGenerating.value = true
 setTimeout(() => {
 isGenerating.value = false
 window.print()
 downloadSuccess.value = true
 }, 1000)
}
</script>

<template>
 <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
 <div class="bg-canvas-raised rounded-2xl border border-border shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col max-h-[90vh]">
 
 <!-- Modal Header (hidden during print) -->
 <div class="p-5 border-b border-border flex items-center justify-between bg-canvas print:hidden">
 <div class="flex items-center gap-3">
 <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
 <Icon name="file-text" class="w-5 h-5" />
 </div>
 <div>
 <h2 class="text-base font-bold text-ink font-serif">Clinical Nutrition & Health Report Export</h2>
 <p class="text-xs text-ink-muted">Standardized ICMR-NIN & DISHA clinical progress summary</p>
 </div>
 </div>
 <button @click="emit('close')" class="text-ink-muted hover:text-ink p-1.5 rounded-lg hover:bg-canvas transition-colors">
 <Icon name="x" class="w-5 h-5" />
 </button>
 </div>

 <!-- Printable Report Document Body -->
 <div id="printable-health-report" class="p-8 overflow-y-auto space-y-6 flex-1 bg-white text-ink font-sans">
 
 <!-- Clinical Header -->
 <div class="flex justify-between items-start border-b-2 border-primary pb-4">
 <div>
 <div class="flex items-center gap-2">
 <span class="w-7 h-7 rounded-lg bg-primary text-white flex items-center justify-center font-serif font-bold text-sm">N</span>
 <span class="font-serif font-bold text-xl text-primary tracking-tight">NutriPlan Clinical</span>
 </div>
 <p class="text-[11px] text-ink-muted mt-1">Certified Telehealth Nutrition & Biometric Intelligence</p>
 </div>
 <div class="text-right">
 <span class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
 OFFICIAL CLINICAL SUMMARY
 </span>
 <p class="text-xs text-ink-muted mt-1 font-mono">Date: {{ new Date().toLocaleDateString('en-IN') }}</p>
 </div>
 </div>

 <!-- Patient & Doctor Metadata Grid -->
 <div class="grid grid-cols-2 gap-4 bg-neutral-50 p-4 rounded-xl border border-neutral-200 text-xs">
 <div>
 <p class="text-[10px] text-ink-muted uppercase font-semibold">Patient Information</p>
 <p class="font-bold text-sm text-ink mt-0.5">{{ reportMeta.patientName }}</p>
 <p class="text-ink-muted font-mono text-[11px]">ID: {{ reportMeta.patientId }}</p>
 <p class="text-ink-muted">Evaluation Period: {{ reportMeta.period }}</p>
 </div>
 <div>
 <p class="text-[10px] text-ink-muted uppercase font-semibold">Supervising Provider</p>
 <p class="font-bold text-sm text-ink mt-0.5">{{ reportMeta.nutritionist }}</p>
 <p class="text-ink-muted">Clinical Nutrition & Diabetes Care</p>
 <p class="text-emerald-700 font-semibold mt-0.5">✓ Verified Dietitian License</p>
 </div>
 </div>

 <!-- Macro Adherence & Caloric Summary -->
 <div>
 <h3 class="text-xs font-bold uppercase tracking-wider text-ink-muted mb-3 flex items-center gap-1.5">
 <span>1. Macronutrient Adherence & Energy Intake</span>
 </h3>
 <div class="grid grid-cols-4 gap-3 text-center">
 <div class="p-3 bg-neutral-50 border border-neutral-200 rounded-xl">
 <p class="text-[10px] text-ink-muted font-semibold uppercase">Daily Calories</p>
 <p class="text-lg font-bold text-ink font-mono">{{ reportMeta.avgCalories }}</p>
 <p class="text-[10px] text-emerald-600 font-medium">98.5% Adherence</p>
 </div>
 <div class="p-3 bg-neutral-50 border border-neutral-200 rounded-xl">
 <p class="text-[10px] text-ink-muted font-semibold uppercase">Protein</p>
 <p class="text-lg font-bold text-blue-700 font-mono">{{ reportMeta.avgProtein }}g</p>
 <p class="text-[10px] text-ink-muted">Target: 120g/day</p>
 </div>
 <div class="p-3 bg-neutral-50 border border-neutral-200 rounded-xl">
 <p class="text-[10px] text-ink-muted font-semibold uppercase">Carbohydrates</p>
 <p class="text-lg font-bold text-amber-700 font-mono">{{ reportMeta.avgCarbs }}g</p>
 <p class="text-[10px] text-ink-muted">Target: 250g/day</p>
 </div>
 <div class="p-3 bg-neutral-50 border border-neutral-200 rounded-xl">
 <p class="text-[10px] text-ink-muted font-semibold uppercase">Healthy Fats</p>
 <p class="text-lg font-bold text-red-700 font-mono">{{ reportMeta.avgFat }}g</p>
 <p class="text-[10px] text-ink-muted">Target: 65g/day</p>
 </div>
 </div>
 </div>

 <!-- Continuous Glucose (CGM) & Wearable Biomarkers -->
 <div>
 <h3 class="text-xs font-bold uppercase tracking-wider text-ink-muted mb-3">
 2. Wearable Biomarkers & Metabolic Telemetry
 </h3>
 <div class="grid grid-cols-3 gap-3">
 <div class="p-3.5 bg-neutral-50 border border-neutral-200 rounded-xl">
 <p class="text-[10px] text-ink-muted font-semibold uppercase">Mean Blood Glucose</p>
 <p class="text-base font-bold text-ink font-mono mt-0.5">{{ reportMeta.cgmAvgGlucose }}</p>
 <p class="text-[11px] text-emerald-600 font-medium">Optimal Glycemic Control</p>
 </div>
 <div class="p-3.5 bg-neutral-50 border border-neutral-200 rounded-xl">
 <p class="text-[10px] text-ink-muted font-semibold uppercase">Time in Range (TIR)</p>
 <p class="text-base font-bold text-emerald-700 font-mono mt-0.5">{{ reportMeta.glucoseInRange }}</p>
 <p class="text-[11px] text-ink-muted">Target &gt; 90% in 70-140 mg/dL</p>
 </div>
 <div class="p-3.5 bg-neutral-50 border border-neutral-200 rounded-xl">
 <p class="text-[10px] text-ink-muted font-semibold uppercase">Average Daily Steps</p>
 <p class="text-base font-bold text-ink font-mono mt-0.5">{{ reportMeta.avgSteps.toLocaleString() }}</p>
 <p class="text-[11px] text-emerald-600 font-medium">Active Lifestyle Tier</p>
 </div>
 </div>
 </div>

 <!-- Clinical Assessment & Action Items -->
 <div class="p-4 bg-neutral-50 border border-neutral-200 rounded-xl text-xs space-y-2">
 <p class="text-[10px] text-ink-muted uppercase font-semibold">Doctor Clinical Assessment & Guidance</p>
 <p class="text-ink leading-relaxed">
 Patient demonstrates outstanding dietary compliance (94% score) with stable glycemic response following low-GI grain adjustments. Recommended to maintain hydration (&gt;2.5L/day) and increase post-workout plant protein (sprouted legumes, tofu) by ~10g to reach full 120g target.
 </p>
 </div>

 <!-- Footer Sign-off -->
 <div class="pt-4 border-t border-neutral-200 flex justify-between items-end text-[10px] text-neutral-500">
 <div>
 <p>Generated by NutriPlan Clinical Engine &bull; Complies with DISHA & ICMR-NIN 2024</p>
 <p>Digital Signature: SHA256-NP7721-AUTH-VERIFIED</p>
 </div>
 <div class="text-right">
 <p class="font-bold text-neutral-800">Dr. Ananya Iyer, RD</p>
 <p>Clinical Dietetic Practitioner</p>
 </div>
 </div>

 </div>

 <!-- Action Footer (hidden during print) -->
 <div class="p-4 border-t border-border bg-canvas flex items-center justify-between print:hidden">
 <span v-if="downloadSuccess" class="text-xs text-emerald-600 font-medium flex items-center gap-1">
 <Icon name="check" class="w-4 h-4" /> Ready for printing / PDF save!
 </span>
 <span v-else class="text-xs text-ink-muted">
 Click below to export or save as PDF via system dialog
 </span>

 <div class="flex items-center gap-3">
 <button 
 @click="emit('close')"
 class="px-4 py-2 text-sm font-medium text-ink-muted hover:text-ink rounded-xl transition-colors"
 >
 Cancel
 </button>
 <button 
 @click="generateAndPrintPDF"
 :disabled="isGenerating"
 class="px-5 py-2 text-sm font-semibold text-white bg-primary hover:bg-primary-strong rounded-xl shadow transition-all flex items-center gap-2"
 >
 <Icon name="download" class="w-4 h-4" />
 {{ isGenerating ? 'Generating PDF...' : 'Print / Export PDF Report' }}
 </button>
 </div>
 </div>

 </div>
 </div>
</template>

<style scoped>
@media print {
 body * {
 visibility: hidden;
 }
 #printable-health-report, #printable-health-report * {
 visibility: visible;
 }
 #printable-health-report {
 position: absolute;
 left: 0;
 top: 0;
 width: 100%;
 margin: 0;
 padding: 20px;
 background: white !important;
 }
}
</style>
