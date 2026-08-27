<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import NotificationCenter from '../components/NotificationCenter.vue'
import Icon from '../components/ui/Icon.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function handleLogout() {
 auth.logout()
 router.push('/login')
}

interface NavGroup {
  groupTitle?: string
  items: { label: string; icon: string; to: string }[]
}

const patientNavGroups: NavGroup[] = [
  {
    groupTitle: 'Daily Nutrition',
    items: [
      { label: 'Today', icon: 'today', to: '/dashboard' },
      { label: 'Meal Plan', icon: 'plan', to: '/plan' },
      { label: 'Food Diary', icon: 'diary', to: '/diary' },
      { label: 'Grocery List', icon: 'grocery', to: '/grocery' },
    ]
  },
  {
    groupTitle: 'Health & Care',
    items: [
      { label: 'Wearables & CGM', icon: 'wearable', to: '/wearables' },
      { label: 'Consultations', icon: 'consultation', to: '/appointments' },
      { label: 'Clinical Tracks', icon: 'shield-check', to: '/clinical' },
      { label: 'AI Health Chat', icon: 'chat', to: '/chat' },
    ]
  },
  {
    groupTitle: 'Plans & Team',
    items: [
      { label: 'Family Plan', icon: 'users', to: '/family' },
      { label: 'Corporate B2B', icon: 'users', to: '/corporate' },
      { label: 'Pricing & Plans', icon: 'pricing', to: '/subscribe' },
    ]
  }
]

const expertNavGroups: NavGroup[] = [
  {
    groupTitle: 'Clinical Workspace',
    items: [
      { label: 'Overview', icon: 'trends', to: '/expert/dashboard' },
      { label: 'My Patients', icon: 'users', to: '/expert/patients' },
      { label: 'Patient Chat', icon: 'chat', to: '/expert/messages' },
      { label: 'Settings & Payouts', icon: 'settings', to: '/expert/settings' },
    ]
  }
]

const adminNavGroups: NavGroup[] = [
  {
    groupTitle: 'Platform & Users',
    items: [
      { label: 'Overview', icon: 'trends', to: '/admin/overview' },
      { label: 'User Directory', icon: 'users', to: '/admin/users' },
      { label: 'Payments & Subs', icon: 'pricing', to: '/admin/payments' },
      { label: 'Nutritionists Queue', icon: 'consultation', to: '/admin/nutritionists' },
      { label: 'Recipes CMS', icon: 'recipe', to: '/admin/recipes' },
    ]
  },
  {
    groupTitle: 'AI & Governance',
    items: [
      { label: 'LLM Router & Costs', icon: 'ai', to: '/admin/llm-router' },
      { label: 'MLOps & Safety', icon: 'shield-check', to: '/admin/mlops' },
      { label: 'Audit Trail', icon: 'lock', to: '/admin/audit-logs' },
      { label: 'Feature Flags', icon: 'settings', to: '/admin/feature-flags' },
    ]
  },
  {
    groupTitle: 'Infrastructure',
    items: [
      { label: 'Global Broadcasts', icon: 'notification', to: '/admin/broadcasts' },
      { label: 'CI/CD Pipelines', icon: 'play', to: '/admin/devops' },
      { label: 'Queue & Cache', icon: 'activity', to: '/admin/queue-monitor' },
      { label: 'Revenue & Costs', icon: 'trends', to: '/admin/analytics' },
    ]
  }
]

const currentNavGroups = computed(() => {
  if (route.path.startsWith('/admin') || auth.isAdmin) {
    return adminNavGroups
  }
  if (route.path.startsWith('/expert') || auth.isNutritionist) {
    return expertNavGroups
  }
  return patientNavGroups
})

const flatNavItems = computed(() => {
  return currentNavGroups.value.flatMap(g => g.items)
})

const portalTitle = computed(() => {
 if (route.path.startsWith('/admin')) return 'Admin Portal'
 if (route.path.startsWith('/expert')) return 'Provider Hub'
 return 'NutriPlan'
})

const sidebarCollapsed = ref(false)

function isActive(to: string) {
 if (to === '/diary' && route.path === '/diary/trends') return false
 return route.path.startsWith(to)
}
</script>

<template>
 <div class="min-h-screen bg-canvas flex font-body text-ink">
 
 <!-- Sidebar -->
 <aside
 class="hidden md:flex flex-col shrink-0 bg-canvas-raised border-r border-border transition-all duration-[260ms] ease-[var(--ease-standard)]"
 :class="sidebarCollapsed ? 'w-[64px]' : 'w-[248px]'"
 >
 <!-- Brand -->
 <div class="flex items-center gap-3 px-4 py-5 border-b border-border">
 <div class="w-8 h-8 rounded-md bg-primary flex items-center justify-center text-white font-display font-bold text-[0.9rem] shrink-0">N</div>
 <div v-if="!sidebarCollapsed" class="min-w-0">
 <div class="font-display font-bold text-[0.95rem] text-ink leading-none">{{ portalTitle }}</div>
 <div class="text-[0.65rem] font-data text-ink-muted mt-1 uppercase tracking-wider">
 {{ route.path.startsWith('/admin') ? 'Admin Operations' : route.path.startsWith('/expert') ? 'Dietitian Portal' : 'Patient View' }}
 </div>
 </div>
 </div>

    <!-- Nav -->
    <nav class="flex-1 py-3 px-2 space-y-4 overflow-y-auto" aria-label="Main navigation">
      <div v-for="(group, gIdx) in currentNavGroups" :key="gIdx" class="space-y-1">
        <div 
          v-if="group.groupTitle && !sidebarCollapsed" 
          class="px-3 pt-2 pb-1 text-[0.65rem] font-data font-bold uppercase tracking-wider text-ink-muted/80"
        >
          {{ group.groupTitle }}
        </div>
        <RouterLink
          v-for="item in group.items"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-[7.5px] rounded-lg text-[0.84rem] font-medium transition-colors duration-[150ms] min-h-[36px]"
          :class="[
            isActive(item.to)
              ? 'bg-primary-soft text-primary font-semibold shadow-xs'
              : 'text-ink-muted hover:text-ink hover:bg-canvas'
          ]"
          :aria-current="isActive(item.to) ? 'page' : undefined"
        >
          <Icon :name="item.icon" :size="16" class="shrink-0" />
          <span v-if="!sidebarCollapsed" class="truncate">{{ item.label }}</span>
        </RouterLink>
      </div>
    </nav>

 <!-- Profile + collapse -->
 <div class="border-t border-border p-3 flex items-center gap-2">
 <RouterLink to="/profile" class="flex items-center gap-2.5 min-w-0 flex-1 hover:opacity-80 transition-opacity no-underline text-ink">
 <div class="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-ink font-semibold text-[0.8rem] shrink-0">
 <Icon name="user" :size="15" />
 </div>
 <div v-if="!sidebarCollapsed" class="flex-1 min-w-0">
 <div class="text-[0.82rem] font-semibold truncate">{{ auth.user?.name || 'Profile' }}</div>
 <div class="text-[0.72rem] text-ink-muted truncate">Settings & Plan</div>
 </div>
 </RouterLink>
 <button
 v-if="!sidebarCollapsed"
 class="w-7 h-7 flex items-center justify-center text-ink-muted hover:text-danger hover:bg-danger-soft rounded transition-colors cursor-pointer"
 title="Sign out"
 @click="handleLogout"
 >
 <Icon name="logout" :size="16" />
 </button>
 <button
 class="w-7 h-7 flex items-center justify-center text-ink-muted hover:text-ink transition-colors cursor-pointer"
 :aria-label="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
 @click="sidebarCollapsed = !sidebarCollapsed"
 >
 {{ sidebarCollapsed ? '›' : '‹' }}
 </button>
 </div>
 </aside>

 <!-- Main content -->
 <div class="flex-1 flex flex-col min-w-0">
 <!-- Top header (mobile + breadcrumb) -->
 <header class="sticky top-0 z-10 bg-canvas-raised/90 backdrop-blur border-b border-border px-4 md:px-6 py-3 flex items-center gap-3">
 <!-- Mobile brand -->
 <div class="md:hidden flex items-center gap-2 mr-auto">
 <div class="w-7 h-7 rounded-md bg-primary flex items-center justify-center text-white font-display font-bold text-[0.8rem]">N</div>
 <span class="font-display font-semibold text-[0.95rem]">NutriPlan</span>
 </div>
 <div class="hidden md:block flex-1">
 <slot name="header-title">
 <h1 class="font-display font-semibold text-[1.1rem] text-ink m-0">
 {{ route.meta.title || 'Today' }}
 </h1>
 </slot>
 </div>
 <div class="flex items-center gap-3">
 <NotificationCenter />
 <button
 class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-semibold text-ink-muted hover:text-danger hover:border-danger/30 hover:bg-danger-soft transition-colors cursor-pointer"
 @click="handleLogout"
 title="Sign out of NutriPlan"
 >
 <Icon name="logout" :size="14" />
 <span>Sign out</span>
 </button>
 <slot name="header-actions" />
 </div>
 </header>

  <!-- Page content -->
  <main
    class="flex-1 py-6 w-full"
    :class="route.path.startsWith('/admin') || route.path.startsWith('/expert')
      ? 'px-4 md:px-8 max-w-[1440px] mx-auto'
      : 'px-4 md:px-6 max-w-[1140px] mx-auto'"
  >
    <slot />
  </main>
 </div>

 <!-- Mobile bottom nav -->
 <nav class="md:hidden fixed bottom-0 inset-x-0 bg-canvas-raised border-t border-border flex justify-around py-2 z-20 overflow-x-auto scrollbar-hide" aria-label="Bottom navigation">
 <RouterLink
 v-for="item in flatNavItems.slice(0, 5)"
 :key="item.to"
 :to="item.to"
 class="flex flex-col items-center gap-0.5 px-3 py-1 min-w-[44px] min-h-[44px] justify-center transition-colors"
 :class="[
 isActive(item.to)
 ? 'text-primary'
 : 'text-ink-muted'
 ]"
 :aria-current="isActive(item.to) ? 'page' : undefined"
 >
 <Icon :name="item.icon" :size="18" />
 <span class="text-[0.6rem] font-data font-semibold uppercase tracking-wider">{{ item.label }}</span>
 </RouterLink>
 </nav>
 </div>
</template>
