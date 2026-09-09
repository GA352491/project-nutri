<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import Input from '../../components/ui/Input.vue'
import Button from '../../components/ui/Button.vue'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('admin@nutriplan.local')
const password = ref('Admin@123')
const isLoading = ref(false)
const error = ref('')

async function handleLogin() {
 error.value = ''
 isLoading.value = true
 
 try {
 const success = await authStore.login(email.value, password.value)
 if (success) {
 if (authStore.isAdmin) {
 router.push('/admin/overview')
 } else if (authStore.isNutritionist) {
 router.push('/expert/dashboard')
 } else {
 router.push('/dashboard')
 }
 } else {
 error.value = authStore.error || 'Invalid email or password'
 }
 } catch (e: any) {
 error.value = e.message || 'Login failed'
 } finally {
 isLoading.value = false
 }
}

function setCredentials(e: string, p: string) {
 email.value = e
 password.value = p
}
</script>

<template>
 <div>
 <h1 class="font-display font-semibold text-[1.4rem] text-ink mb-1">Welcome back</h1>
 <p class="text-ink-muted text-[0.88rem] mb-6">Log in to your NutriPlan account to continue.</p>

 <div v-if="error" class="bg-danger-soft text-danger px-3 py-2 rounded-md text-[0.8rem] mb-4">
 {{ error }}
 </div>

 <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
 <Input
 v-model="email"
 label="Email"
 type="email"
 placeholder="you@example.com"
 required
 />
 
 <div>
 <Input
 v-model="password"
 label="Password"
 type="password"
 placeholder="••••••••"
 required
 />
 <div class="flex justify-end mt-1">
 <a href="#" class="text-primary text-[0.76rem] font-medium hover:underline">Forgot password?</a>
 </div>
 </div>

 <Button type="submit" class="w-full mt-2" :loading="isLoading">
 Sign in
 </Button>
 </form>

 <!-- Quick test credential presets -->
 <div class="mt-6 border-t border-border pt-4">
 <p class="font-data text-[0.72rem] uppercase tracking-wider text-ink-muted mb-2 font-semibold">Quick Role Switcher (Local Testing)</p>
 <div class="flex flex-wrap gap-2">
 <button
 type="button"
 @click="setCredentials('admin@nutriplan.local', 'Admin@123')"
 class="px-2.5 py-1 text-xs rounded-lg border border-primary/40 bg-primary/10 text-primary font-medium hover:bg-primary/20 transition"
 >
 Admin
 </button>
 <button
 type="button"
 @click="setCredentials('expert@nutriplan.local', 'Expert@123')"
 class="px-2.5 py-1 text-xs rounded-lg border border-warning/40 bg-warning/10 text-warning font-medium hover:bg-warning/20 transition"
 >
 ‍️ Expert / Nutritionist
 </button>
 <button
 type="button"
 @click="setCredentials('patient@nutriplan.local', 'Patient@123')"
 class="px-2.5 py-1 text-xs rounded-lg border border-border bg-canvas-raised text-ink-muted font-medium hover:border-primary/50 transition"
 >
 Patient
 </button>
 </div>
 </div>
 </div>
</template>
