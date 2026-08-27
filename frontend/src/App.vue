<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from './layouts/AppLayout.vue'
import AuthLayout from './layouts/AuthLayout.vue'
import OnboardingLayout from './layouts/OnboardingLayout.vue'
import LandingLayout from './layouts/LandingLayout.vue'
import ToastContainer from './components/ui/ToastContainer.vue'

const route = useRoute()
const layout = computed(() => route.meta.layout ?? 'app')
</script>

<template>
 <LandingLayout v-if="layout === 'landing'">
 <RouterView />
 </LandingLayout>

 <AppLayout v-else-if="layout === 'app'">
 <RouterView />
 </AppLayout>

 <AuthLayout v-else-if="layout === 'auth'">
 <RouterView />
 </AuthLayout>

 <OnboardingLayout
 v-else-if="layout === 'onboarding'"
 :current-step="(route.meta.step as number) ?? 1"
 :total-steps="(route.meta.totalSteps as number) ?? 4"
 :step-label="route.meta.title as string"
 >
 <RouterView />
 <template #nav-back>
 <slot name="nav-back" />
 </template>
 <template #nav-next>
 <slot name="nav-next" />
 </template>
 </OnboardingLayout>

 <!-- Fallback -->
 <RouterView v-else />

 <!-- Global Toast & Alert Notification Container -->
 <ToastContainer />
</template>
