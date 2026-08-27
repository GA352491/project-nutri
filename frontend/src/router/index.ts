import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
 // Public: Landing & Marketing
 { path: '/', component: () => import('../pages/landing/LandingPage.vue'), meta: { layout: 'landing', title: 'AI Nutrition Coach', public: true } },
 { path: '/privacy', component: () => import('../pages/legal/PrivacyPage.vue'), meta: { layout: 'landing', title: 'Privacy Policy', public: true } },
 { path: '/terms', component: () => import('../pages/legal/TermsPage.vue'), meta: { layout: 'landing', title: 'Terms of Service', public: true } },
 { path: '/cookies', component: () => import('../pages/legal/CookiesPage.vue'), meta: { layout: 'landing', title: 'Cookie Policy', public: true } },

 // Public: Auth
 { path: '/login', component: () => import('../pages/auth/LoginPage.vue'), meta: { layout: 'auth', title: 'Sign In', public: true } },
 { path: '/register', component: () => import('../pages/auth/RegisterPage.vue'), meta: { layout: 'auth', title: 'Create Account', public: true } },

 // Public: Onboarding (requires auth, not role)
 { path: '/onboarding', component: () => import('../pages/onboarding/StepDemographics.vue'), meta: { layout: 'onboarding', title: 'About You', step: 1, totalSteps: 5 } },
 { path: '/onboarding/diet', component: () => import('../pages/onboarding/StepDietAllergies.vue'), meta: { layout: 'onboarding', title: 'Diet & Allergies', step: 2, totalSteps: 5 } },
 { path: '/onboarding/cuisine', component: () => import('../pages/onboarding/StepCuisineBudget.vue'), meta: { layout: 'onboarding', title: 'Cuisine & Budget', step: 3, totalSteps: 5 } },
 { path: '/onboarding/pantry', component: () => import('../pages/onboarding/StepPantry.vue'), meta: { layout: 'onboarding', title: 'Your Pantry', step: 4, totalSteps: 5 } },
 { path: '/onboarding/subscription', component: () => import('../pages/onboarding/StepSubscription.vue'), meta: { layout: 'onboarding', title: 'Plan & Payment', step: 5, totalSteps: 5 } },

 // App: Patient (auth required)
 { path: '/dashboard', component: () => import('../pages/dashboard/TodayPage.vue'), meta: { layout: 'app', title: 'Today', requiresAuth: true } },
 { path: '/plan', component: () => import('../pages/plan/WeekViewPage.vue'), meta: { layout: 'app', title: 'Your Plan', requiresAuth: true } },
 { path: '/plan/:id', component: () => import('../pages/plan/MealDetailPage.vue'), meta: { layout: 'app', title: 'Meal Detail', requiresAuth: true } },
 { path: '/diary', component: () => import('../pages/diary/DailyDiaryPage.vue'), meta: { layout: 'app', title: 'Diary', requiresAuth: true } },
 { path: '/diary/trends', component: () => import('../pages/diary/TrendViewPage.vue'), meta: { layout: 'app', title: 'Trends', requiresAuth: true } },
 { path: '/grocery', component: () => import('../pages/grocery/GroceryListPage.vue'), meta: { layout: 'app', title: 'Grocery List', requiresAuth: true } },
 { path: '/chat', component: () => import('../pages/chat/ChatPage.vue'), meta: { layout: 'app', title: 'Chat', requiresAuth: true } },
 { path: '/wearables', component: () => import('../pages/wearables/WearablesPage.vue'), meta: { layout: 'app', title: 'Wearables', requiresAuth: true } },
 { path: '/appointments', component: () => import('../pages/appointments/BookingPage.vue'), meta: { layout: 'app', title: 'Book Appointment', requiresAuth: true } },
 { path: '/consultation/:id', component: () => import('../pages/appointments/VideoConsultationRoom.vue'), meta: { layout: 'app', title: 'Video Consultation', requiresAuth: true } },
 { path: '/notifications', component: () => import('../pages/notifications/NotificationsPage.vue'), meta: { layout: 'app', title: 'Notifications', requiresAuth: true } },
 { path: '/profile', component: () => import('../pages/profile/ProfilePage.vue'), meta: { layout: 'app', title: 'Profile & Settings', requiresAuth: true } },
 { path: '/settings', redirect: '/profile' },
 { path: '/subscribe', component: () => import('../pages/settings/PricingPage.vue'), meta: { layout: 'app', title: 'Plans & Pricing', requiresAuth: true } },
 { path: '/corporate', component: () => import('../pages/corporate/CorporateWellnessPage.vue'), meta: { layout: 'app', title: 'Corporate Wellness', requiresAuth: true } },
 { path: '/family', component: () => import('../pages/family/FamilyPlanPage.vue'), meta: { layout: 'app', title: 'Family Plan', requiresAuth: true } },
 { path: '/clinical', component: () => import('../pages/clinical/ClinicalProgramsPage.vue'), meta: { layout: 'app', title: 'Clinical Tracks', requiresAuth: true } },
 { path: '/checkout', component: () => import('../pages/settings/CheckoutPage.vue'), meta: { layout: 'app', title: 'Checkout', requiresAuth: true } },

 // Admin Portal (auth + role: admin)
 {
   path: '/admin',
   component: () => import('../pages/admin/AdminLayout.vue'),
   meta: { layout: 'app', title: 'Admin & Operations', requiresAuth: true, requiresRole: 'admin' },
   children: [
     { path: '', redirect: '/admin/overview' },
     { path: 'overview', component: () => import('../pages/admin/AdminDashboardPage.vue') },
     { path: 'recipes', component: () => import('../pages/admin/RecipesPage.vue') },
     { path: 'users', component: () => import('../pages/admin/UsersPage.vue') },
     { path: 'payments', component: () => import('../pages/admin/PaymentsPage.vue') },
     { path: 'nutritionists', component: () => import('../pages/admin/NutritionistsPage.vue') },
     { path: 'audit-logs', component: () => import('../pages/admin/AuditLogsPage.vue') },
     { path: 'llm-router', component: () => import('../pages/admin/LLMCostCenterPage.vue') },
     { path: 'feature-flags', component: () => import('../pages/admin/FeatureFlagsPage.vue') },
     { path: 'broadcasts', component: () => import('../pages/admin/BroadcastsPage.vue') },
     { path: 'devops', component: () => import('../pages/admin/DevOpsPipelinePage.vue') },
     { path: 'queue-monitor', component: () => import('../pages/admin/QueueMonitorPage.vue') },
     { path: 'mlops', component: () => import('../pages/admin/MLOpsPage.vue') },
     { path: 'analytics', component: () => import('../pages/admin/AnalyticsPage.vue') },
   ]
 },

 // Expert / Nutritionist Portal (auth + role: nutritionist)
 {
 path: '/expert',
 component: () => import('../pages/expert/ExpertLayout.vue'),
 meta: { layout: 'app', title: 'Provider Portal', requiresAuth: true, requiresRole: 'nutritionist' },
 children: [
 { path: '', redirect: '/expert/dashboard' },
 { path: 'dashboard', component: () => import('../pages/expert/ExpertDashboard.vue') },
 { path: 'patients', component: () => import('../pages/expert/MyPatients.vue') },
 { path: 'messages', component: () => import('../pages/expert/PatientChat.vue') },
 { path: 'settings', component: () => import('../pages/expert/ExpertSettings.vue') },
 ]
 },

 // Expert Onboarding — standalone (auth required, no role needed; nutritionists self-register)
 { path: '/expert/onboard', component: () => import('../pages/onboarding/ExpertOnboarding.vue'), meta: { layout: 'auth', title: 'Join as a Nutritionist', requiresAuth: true } },

 // Catch-all
 { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
 history: createWebHistory(),
 routes,
 scrollBehavior: () => ({ top: 0 })
})

// ── Global Navigation Guard ────────────────────────────────────────────────
router.beforeEach(async (to, _from) => {
  const auth = useAuthStore()

  // 1. Public route — ALWAYS allow without checking auth or calling protected APIs
  if (to.meta.public) {
    // If authenticated user visits login or register, redirect to appropriate home
    if (auth.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      if (auth.isAdmin) return '/admin'
      if (auth.isNutritionist) return '/expert/dashboard'
      return '/dashboard'
    }
    return true
  }

  // 2. Bootstrap auth state on first protected navigation (rehydrate token from localStorage)
  if (!auth.user && auth.token) {
    await auth.init()
  }

  // 3. Protected route — must be authenticated
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login'
  }

  // 4. Role-based guard
  if (to.meta.requiresRole) {
    const role = to.meta.requiresRole as string
    if (auth.user?.role !== role) {
      if (auth.isAdmin) return '/admin'
      if (auth.isNutritionist) return '/expert/dashboard'
      return '/dashboard'
    }
  }

  return true
})

// ── Set page title from route meta ────────────────────────────────────────
router.afterEach((to) => {
 document.title = `${to.meta.title as string || 'NutriPlan'} — NutriPlan`
})

export default router

