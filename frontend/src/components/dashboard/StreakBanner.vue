<script setup lang="ts">
import { ref } from 'vue'
import Icon from '../ui/Icon.vue'

const streakCount = ref(14)
const showBadgesModal = ref(false)

const weeklyDays = ref([
 { day: 'M', logged: true, current: false },
 { day: 'T', logged: true, current: false },
 { day: 'W', logged: true, current: false },
 { day: 'T', logged: true, current: false },
 { day: 'F', logged: true, current: false },
 { day: 'S', logged: true, current: false },
 { day: 'S', logged: true, current: true },
])

const badges = ref([
 {
 id: 'b1',
 name: '14-Day Consistency Titan',
 category: 'Streak',
 icon: 'flame',
 color: 'from-amber-500 to-orange-500',
 desc: 'Logged all 4 meals consistently for 14 straight days.',
 unlocked: true,
 unlockedAt: 'Today',
 },
 {
 id: 'b2',
 name: 'Protein Champion',
 category: 'Nutrition Target',
 icon: 'shield-check',
 color: 'from-blue-500 to-indigo-600',
 desc: 'Hit exact 120g protein target for 7 consecutive days.',
 unlocked: true,
 unlockedAt: 'Yesterday',
 },
 {
 id: 'b3',
 name: 'Metabolic Master',
 category: 'Biomarkers',
 icon: 'activity',
 color: 'from-emerald-500 to-teal-600',
 desc: 'Maintained 95%+ Continuous Glucose Time-in-Range (TIR).',
 unlocked: true,
 unlockedAt: '16 Aug 2026',
 },
 {
 id: 'b4',
 name: 'AI Vision Pioneer',
 category: 'Photo Logging',
 icon: 'camera',
 color: 'from-purple-500 to-pink-600',
 desc: 'Scanned and logged 20 meals using AI Food Camera.',
 unlocked: true,
 unlockedAt: '14 Aug 2026',
 },
 {
 id: 'b5',
 name: '30-Day Master Nutritionist',
 category: 'Milestone',
 icon: 'check',
 color: 'from-amber-400 to-yellow-600',
 desc: 'Reach a full 30-day logging streak with active dietitian review.',
 unlocked: false,
 progress: '14 / 30 Days',
 },
])
</script>

<template>
 <div>
 <!-- Streak Banner Widget -->
 <div class="bg-gradient-to-r from-[#2F5233] via-[#234226] to-[#1C331F] rounded-2xl p-5 text-white shadow-lg border border-primary/30 mb-6 flex flex-col md:flex-row items-center justify-between gap-5 relative overflow-hidden">
 
 <!-- Background Ambient Glow -->
 <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

 <!-- Left: Streak Counter & Fire -->
 <div class="flex items-center gap-4">
 <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center text-white shadow-md shadow-orange-950/40 text-2xl font-bold animate-pulse">
 
 </div>
 <div>
 <div class="flex items-center gap-2">
 <span class="text-2xl font-extrabold font-mono tracking-tight text-white">{{ streakCount }} Day Streak!</span>
 <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-400/20 text-amber-300 border border-amber-400/30">
 Top 5% Adherence
 </span>
 </div>
 <p class="text-xs text-white/70 mt-0.5">Keep logging your meals today to maintain your consistency multiplier.</p>
 </div>
 </div>

 <!-- Middle: Weekly Circle Checkers -->
 <div class="flex items-center gap-2 bg-black/20 px-3.5 py-2 rounded-xl border border-white/10">
 <div 
 v-for="(item, idx) in weeklyDays" 
 :key="idx"
 class="flex flex-col items-center gap-1"
 >
 <div 
 class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-all"
 :class="item.logged ? 'bg-amber-400 text-ink shadow-sm shadow-amber-400/50 scale-105' : 'bg-white/10 text-white/50'"
 >
 {{ item.logged ? '✓' : '' }}
 </div>
 <span class="text-[9px] font-bold font-mono" :class="item.current ? 'text-amber-300' : 'text-white/40'">{{ item.day }}</span>
 </div>
 </div>

 <!-- Right: View Rewards Button -->
 <button 
 @click="showBadgesModal = true"
 class="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white border border-white/20 rounded-xl text-xs font-semibold backdrop-blur-md transition-all flex items-center gap-2 shrink-0 cursor-pointer"
 >
 <span> Badges & Rewards (4)</span>
 <Icon name="chevron-right" class="w-3.5 h-3.5 text-white/70" />
 </button>

 </div>

 <!-- Badges & Achievements Modal -->
 <div v-if="showBadgesModal" class="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
 <div class="bg-canvas-raised rounded-2xl border border-border shadow-2xl max-w-xl w-full overflow-hidden flex flex-col max-h-[90vh]">
 
 <!-- Header -->
 <div class="p-6 border-b border-border flex items-center justify-between bg-canvas">
 <div class="flex items-center gap-3">
 <div class="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-600 text-lg">
 
 </div>
 <div>
 <h2 class="text-lg font-bold text-ink font-serif">Nutrition Mastery Badges</h2>
 <p class="text-xs text-ink-muted">Earn reward badges by maintaining clinical diet compliance</p>
 </div>
 </div>
 <button @click="showBadgesModal = false" class="text-ink-muted hover:text-ink p-1.5 rounded-lg hover:bg-canvas transition-colors">
 <Icon name="x" class="w-5 h-5" />
 </button>
 </div>

 <!-- Badges Grid -->
 <div class="p-6 overflow-y-auto space-y-4 flex-1">
 <div 
 v-for="badge in badges" 
 :key="badge.id"
 class="p-4 rounded-xl border transition-all flex items-start gap-4"
 :class="badge.unlocked ? 'bg-canvas-raised border-border shadow-sm' : 'bg-canvas/50 border-dashed border-border opacity-70'"
 >
 <!-- Badge Icon Bubble -->
 <div 
 class="w-12 h-12 rounded-2xl flex items-center justify-center text-white text-lg font-bold shrink-0 shadow-md"
 :class="badge.unlocked ? `bg-gradient-to-tr ${badge.color}` : 'bg-neutral-300 text-neutral-500'"
 >
 {{ badge.unlocked ? '★' : '' }}
 </div>

 <!-- Details -->
 <div class="flex-1 min-w-0">
 <div class="flex items-center justify-between gap-2">
 <h4 class="text-sm font-bold text-ink">{{ badge.name }}</h4>
 <span 
 v-if="badge.unlocked" 
 class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800"
 >
 Unlocked {{ badge.unlockedAt }}
 </span>
 <span 
 v-else 
 class="text-[10px] font-bold text-ink-muted bg-canvas px-2 py-0.5 rounded-full border border-border"
 >
 {{ badge.progress }}
 </span>
 </div>
 <p class="text-xs text-ink-muted mt-1 leading-relaxed">{{ badge.desc }}</p>
 <span class="inline-block text-[10px] uppercase font-mono tracking-wider font-semibold text-primary mt-2">
 Category: {{ badge.category }}
 </span>
 </div>
 </div>
 </div>

 <!-- Footer -->
 <div class="p-4 border-t border-border bg-canvas flex justify-end">
 <button 
 @click="showBadgesModal = false"
 class="px-5 py-2 text-sm font-semibold text-white bg-primary hover:bg-primary-strong rounded-xl shadow transition-all"
 >
 Close
 </button>
 </div>

 </div>
 </div>
 </div>
</template>
