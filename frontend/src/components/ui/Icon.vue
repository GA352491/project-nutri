<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
 name: string
 size?: number | string
 class?: string
 color?: string
}>(), {
 size: 20,
 class: ''
})

const sizePx = computed(() => typeof props.size === 'number' ? `${props.size}px` : props.size)
</script>

<template>
 <svg
 :width="sizePx"
 :height="sizePx"
 viewBox="0 0 24 24"
 fill="none"
 stroke="currentColor"
 stroke-width="1.8"
 stroke-linecap="round"
 stroke-linejoin="round"
 :class="['shrink-0 inline-block', props.class]"
 >
 <!-- Navigation & Core -->
 <template v-if="name === 'today' || name === 'sun'">
 <circle cx="12" cy="12" r="4"/>
 <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
 </template>

 <template v-else-if="name === 'plan' || name === 'calendar'">
 <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
 <line x1="16" y1="2" x2="16" y2="6"/>
 <line x1="8" y1="2" x2="8" y2="6"/>
 <line x1="3" y1="10" x2="21" y2="10"/>
 <path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01M16 18h.01"/>
 </template>

 <template v-else-if="name === 'diary' || name === 'book'">
 <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
 <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
 <line x1="8" y1="6" x2="16" y2="6"/>
 <line x1="8" y1="10" x2="14" y2="10"/>
 </template>

 <template v-else-if="name === 'trends' || name === 'chart'">
 <line x1="18" y1="20" x2="18" y2="10"/>
 <line x1="12" y1="20" x2="12" y2="4"/>
 <line x1="6" y1="20" x2="6" y2="14"/>
 <line x1="2" y1="20" x2="22" y2="20"/>
 </template>

 <template v-else-if="name === 'grocery' || name === 'cart'">
 <circle cx="9" cy="21" r="1"/>
 <circle cx="20" cy="21" r="1"/>
 <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
 </template>

 <template v-else-if="name === 'wearable' || name === 'watch'">
 <rect x="7" y="5" width="10" height="14" rx="3" ry="3"/>
 <path d="M10 2h4M10 22h4"/>
 <circle cx="12" cy="12" r="2.5"/>
 </template>

 <template v-else-if="name === 'consultation' || name === 'doctor' || name === 'stethoscope'">
 <path d="M4.5 3v5a5.5 5.5 0 0 0 11 0V3"/>
 <path d="M2.5 3h4M13.5 3h4"/>
 <path d="M10 13.5V17a3 3 0 0 0 6 0v-2"/>
 <circle cx="16" cy="14" r="2"/>
 </template>

 <template v-else-if="name === 'chat' || name === 'message'">
 <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
 </template>

 <template v-else-if="name === 'pricing' || name === 'sparkles'">
 <path d="M12 3l1.912 5.885L20 10.8l-4.756 4.636 1.123 6.54L12 18.885 7.633 21.976l1.123-6.54L4 10.8l6.088-1.915L12 3z"/>
 </template>

 <template v-else-if="name === 'notification' || name === 'bell'">
 <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
 <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
 </template>

 <template v-else-if="name === 'logout' || name === 'exit'">
 <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
 <polyline points="16 17 21 12 16 7"/>
 <line x1="21" y1="12" x2="9" y2="12"/>
 </template>

 <template v-else-if="name === 'settings'">
 <circle cx="12" cy="12" r="3"/>
 <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
 </template>

 <template v-else-if="name === 'users' || name === 'patients'">
 <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
 <circle cx="9" cy="7" r="4"/>
 <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
 <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
 </template>

 <template v-else-if="name === 'recipe' || name === 'food'">
 <path d="M18 8h1a4 4 0 0 1 0 8h-1"/>
 <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/>
 <line x1="6" y1="1" x2="6" y2="4"/>
 <line x1="10" y1="1" x2="10" y2="4"/>
 <line x1="14" y1="1" x2="14" y2="4"/>
 </template>

 <template v-else-if="name === 'ai' || name === 'cpu'">
 <rect x="4" y="4" width="16" height="16" rx="2"/>
 <rect x="9" y="9" width="6" height="6"/>
 <line x1="9" y1="1" x2="9" y2="4"/>
 <line x1="15" y1="1" x2="15" y2="4"/>
 <line x1="9" y1="20" x2="9" y2="23"/>
 <line x1="15" y1="20" x2="15" y2="23"/>
 <line x1="20" y1="9" x2="23" y2="9"/>
 <line x1="20" y1="14" x2="23" y2="14"/>
 <line x1="1" y1="9" x2="4" y2="9"/>
 <line x1="1" y1="14" x2="4" y2="14"/>
 </template>

 <template v-else-if="name === 'bolt' || name === 'energy'">
 <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
 </template>

 <template v-else-if="name === 'heart'">
 <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
 </template>

 <template v-else-if="name === 'check'">
 <polyline points="20 6 9 17 4 12"/>
 </template>

 <template v-else-if="name === 'refresh' || name === 'sync'">
 <polyline points="23 4 23 10 17 10"/>
 <polyline points="1 20 1 14 7 14"/>
 <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
 </template>

 <template v-else-if="name === 'lock'">
 <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
 <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
 </template>

 <template v-else-if="name === 'user'">
 <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
 <circle cx="12" cy="7" r="4"/>
 </template>

 <template v-else-if="name === 'flame'">
 <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
 </template>

 <template v-else-if="name === 'moon'">
 <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
 </template>

 <template v-else-if="name === 'droplet'">
 <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
 </template>

 <template v-else-if="name === 'plus'">
 <line x1="12" y1="5" x2="12" y2="19"/>
 <line x1="5" y1="12" x2="19" y2="12"/>
 </template>

 <template v-else-if="name === 'trash'">
 <polyline points="3 6 5 6 21 6"/>
 <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
 </template>

 <template v-else-if="name === 'chevron-right'">
 <polyline points="9 18 15 12 9 6"/>
 </template>

 <template v-else-if="name === 'credit-card'">
 <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
 <line x1="1" y1="10" x2="23" y2="10"/>
 </template>

 <!-- Default fallback icon -->
 <template v-else>
 <circle cx="12" cy="12" r="10"/>
 <line x1="12" y1="8" x2="12" y2="12"/>
 <line x1="12" y1="16" x2="12.01" y2="16"/>
 </template>
 </svg>
</template>
