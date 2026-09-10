<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from '../../components/ui/Button.vue'
import VerificationBadge from '../../components/VerificationBadge.vue'
import apiClient from '../../api'

const route = useRoute()
const router = useRouter()

const token = ref((route.query.token as string) || '')
const email = ref((route.query.email as string) || '')
const password = ref('')
const confirmPassword = ref('')
const phone = ref('')
const bio = ref('')

const isClaiming = ref(false)
const errorMsg = ref('')
const isSuccess = ref(false)

onMounted(() => {
  if (!token.value) {
    errorMsg.value = 'Invalid or expired invitation link. Please request a new invitation from administrator.'
  }
})

async function handleClaim() {
  if (password.value.length < 6) {
    errorMsg.value = 'Password must be at least 6 characters long.'
    return
  }
  if (password.value !== confirmPassword.value) {
    errorMsg.value = 'Passwords do not match.'
    return
  }

  isClaiming.value = true
  errorMsg.value = ''
  try {
    const res = await apiClient.post('/marketplace/nutritionists/claim', {
      invite_token: token.value,
      password: password.value,
      phone: phone.value,
      bio: bio.value,
    })

    if (res.data?.status === 'success') {
      isSuccess.value = true
      const nutritionistId = res.data?.nutritionist_id || ''
      setTimeout(() => {
        // Redirect to the profile setup wizard with the nutritionist ID
        router.push({ path: '/expert/setup', query: { id: nutritionistId } })
      }, 1500)
    }
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to claim invitation. The link may have expired.'
  } finally {
    isClaiming.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-canvas flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md text-center">
      <div class="inline-flex items-center gap-2 mb-3">
        <span class="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center border border-primary/20">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
        </span>
        <span class="font-display font-bold text-2xl text-ink">NutriPlan Clinical</span>
      </div>
      <h2 class="font-display font-bold text-xl text-ink">Claim Your Clinical Practitioner Profile</h2>
      <p class="font-body text-xs text-ink-muted mt-1">
        You have been pre-verified and invited to the NutriPlan provider network.
      </p>
    </div>

    <div class="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-canvas-raised py-8 px-6 shadow-card border border-border sm:rounded-2xl sm:px-10">
        <!-- Success Screen -->
        <div v-if="isSuccess" class="text-center space-y-4 py-4">
          <div class="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-600 flex items-center justify-center mx-auto">
            <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <h3 class="font-display font-bold text-lg text-ink">Account Claimed Successfully</h3>
          <p class="font-body text-xs text-ink-muted">
            Taking you to complete your profile setup…
          </p>
        </div>

        <!-- Form -->
        <form v-else class="space-y-4" @submit.prevent="handleClaim">
          <div v-if="errorMsg" class="p-3 bg-red-500/10 border border-red-500/25 rounded-lg text-xs text-red-600 font-medium">
            {{ errorMsg }}
          </div>

          <!-- Verified Badge Banner -->
          <div class="p-3 bg-emerald-500/10 border border-emerald-500/25 rounded-xl flex items-center justify-between">
            <div>
              <div class="text-[0.72rem] font-bold text-emerald-900 uppercase tracking-wider font-data">Pre-Approved Status</div>
              <div class="text-xs text-emerald-800 font-medium">{{ email || 'Registered Practitioner' }}</div>
            </div>
            <VerificationBadge tier="ncahp_verified" status="verified" size="sm" />
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">Set Password *</label>
            <input
              v-model="password"
              type="password"
              required
              placeholder="Minimum 6 characters"
              class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">Confirm Password *</label>
            <input
              v-model="confirmPassword"
              type="password"
              required
              placeholder="Re-enter your password"
              class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">Phone Number</label>
            <input
              v-model="phone"
              type="tel"
              placeholder="+91-98765-43210"
              class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink uppercase tracking-wider mb-1">Public Bio (Optional)</label>
            <textarea
              v-model="bio"
              rows="3"
              placeholder="Brief summary of your clinical specialty and patient approach..."
              class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border text-ink focus:outline-none focus:border-primary"
            ></textarea>
          </div>

          <Button
            type="submit"
            variant="primary"
            class="w-full mt-2"
            :disabled="isClaiming || !token"
          >
            {{ isClaiming ? 'Activating Profile...' : 'Claim & Open Provider Portal →' }}
          </Button>
        </form>
      </div>
    </div>
  </div>
</template>
