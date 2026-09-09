<script setup lang="ts">
import type { BadgeTier, VerificationStatus } from '../stores/verification'

interface Props {
  tier: BadgeTier
  status: VerificationStatus
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showLabel: true,
})

const config = {
  ncahp_verified: {
    icon: '🛡️',
    label: 'NCAHP Verified',
    sublabel: 'Central Register · Gold',
    bg: 'rgba(16, 185, 129, 0.15)',
    border: 'rgba(16, 185, 129, 0.5)',
    text: '#10B981',
    dot: '#10B981',
    pulse: false,
  },
  ida_verified: {
    icon: '✅',
    label: 'IDA Registered Dietitian',
    sublabel: 'Indian Dietetic Association · Silver',
    bg: 'rgba(59, 130, 246, 0.15)',
    border: 'rgba(59, 130, 246, 0.5)',
    text: '#60A5FA',
    dot: '#60A5FA',
    pulse: false,
  },
  degree_verified: {
    icon: '🎓',
    label: 'Degree Verified',
    sublabel: 'University Confirmed · Bronze',
    bg: 'rgba(245, 158, 11, 0.12)',
    border: 'rgba(245, 158, 11, 0.4)',
    text: '#F59E0B',
    dot: '#F59E0B',
    pulse: false,
  },
  pending: {
    icon: '⏳',
    label: 'Verification Pending',
    sublabel: 'Credentials under review',
    bg: 'rgba(251, 191, 36, 0.1)',
    border: 'rgba(251, 191, 36, 0.35)',
    text: '#FBBF24',
    dot: '#FBBF24',
    pulse: true,
  },
  none: {
    icon: '○',
    label: 'Unverified',
    sublabel: 'No application on file',
    bg: 'rgba(100, 116, 139, 0.1)',
    border: 'rgba(100, 116, 139, 0.3)',
    text: '#94A3B8',
    dot: '#94A3B8',
    pulse: false,
  },
}

const c = config[props.tier]

const sizeClass = {
  sm: { badge: 'badge-sm', icon: '11px', iconPx: 12, label: '10px', sub: '9px', gap: '4px' },
  md: { badge: 'badge-md', icon: '13px', iconPx: 14, label: '12px', sub: '10px', gap: '6px' },
  lg: { badge: 'badge-lg', icon: '15px', iconPx: 16, label: '14px', sub: '11px', gap: '8px' },
}[props.size]
</script>

<template>
  <div
    class="vbadge"
    :class="sizeClass.badge"
    :style="{
      background: c.bg,
      border: `1px solid ${c.border}`,
      gap: sizeClass.gap,
    }"
  >
    <!-- Status dot -->
    <span
      class="vbadge-dot"
      :class="{ 'vbadge-dot--pulse': c.pulse }"
      :style="{ background: c.dot }"
    />

    <!-- Icon (Clean SVG) -->
    <span class="vbadge-icon" :style="{ color: c.text }">
      <!-- NCAHP Shield -->
      <svg v-if="props.tier === 'ncahp_verified'" :width="sizeClass.iconPx" :height="sizeClass.iconPx" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        <polyline points="9 12 11 14 15 10"/>
      </svg>
      <!-- IDA Check Badge -->
      <svg v-else-if="props.tier === 'ida_verified'" :width="sizeClass.iconPx" :height="sizeClass.iconPx" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
      </svg>
      <!-- Degree Verified -->
      <svg v-else-if="props.tier === 'degree_verified'" :width="sizeClass.iconPx" :height="sizeClass.iconPx" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
        <path d="M6 12v5c3 3 9 3 12 0v-5"/>
      </svg>
      <!-- Pending Review -->
      <svg v-else-if="props.tier === 'pending'" :width="sizeClass.iconPx" :height="sizeClass.iconPx" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <polyline points="12 6 12 12 16 14"/>
      </svg>
      <!-- Unverified -->
      <svg v-else :width="sizeClass.iconPx" :height="sizeClass.iconPx" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="9"/>
      </svg>
    </span>

    <!-- Label -->
    <div v-if="showLabel" class="vbadge-text">
      <span class="vbadge-label" :style="{ color: c.text, fontSize: sizeClass.label }">{{ c.label }}</span>
      <span v-if="size !== 'sm'" class="vbadge-sub" :style="{ fontSize: sizeClass.sub }">{{ c.sublabel }}</span>
    </div>
  </div>
</template>

<style scoped>
.vbadge {
  display: inline-flex;
  align-items: center;
  border-radius: 8px;
  padding: 4px 10px 4px 7px;
  transition: box-shadow 0.2s ease;
  cursor: default;
  user-select: none;
  max-width: 100%;
}

.vbadge:hover {
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.08);
}

.vbadge-sm { padding: 3px 7px 3px 5px; border-radius: 6px; }
.vbadge-lg { padding: 6px 14px 6px 10px; border-radius: 10px; }

.vbadge-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.vbadge-dot--pulse {
  animation: badge-pulse 2s ease-in-out infinite;
}

@keyframes badge-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.vbadge-icon {
  flex-shrink: 0;
  line-height: 1;
}

.vbadge-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  min-width: 0;
}

.vbadge-label {
  font-weight: 700;
  letter-spacing: 0.01em;
  white-space: nowrap;
}

.vbadge-sub {
  color: rgba(148, 163, 184, 0.8);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
