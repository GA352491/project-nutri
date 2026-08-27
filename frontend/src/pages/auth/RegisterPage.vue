<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Input from '../../components/ui/Input.vue'
import Button from '../../components/ui/Button.vue'

import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const fullName = ref('')
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

async function handleRegister() {
 error.value = ''
 isLoading.value = true
 
 try {
 if (!fullName.value || !email.value || !password.value) {
 throw new Error('Please fill out all fields.')
 }
 const success = await authStore.register(email.value, password.value, fullName.value)
 if (success) {
 router.push('/onboarding')
 } else {
 error.value = authStore.error || 'Registration failed'
 }
 } catch (e: any) {
 error.value = e.message || 'Registration failed'
 } finally {
 isLoading.value = false
 }
}
</script>

<template>
 <div>
 <h1 class="font-display font-semibold text-[1.4rem] text-ink mb-1">Create an account</h1>
 <p class="text-ink-muted text-[0.88rem] mb-6">Join NutriPlan and start your personalized journey.</p>

 <div v-if="error" class="bg-danger-soft text-danger px-3 py-2 rounded-md text-[0.8rem] mb-4">
 {{ error }}
 </div>

 <form @submit.prevent="handleRegister" class="flex flex-col gap-4">
 <Input
 v-model="fullName"
 label="Full Name"
 type="text"
 placeholder="Jane Doe"
 required
 />

 <Input
 v-model="email"
 label="Email"
 type="email"
 placeholder="you@example.com"
 required
 />
 
 <Input
 v-model="password"
 label="Password"
 type="password"
 placeholder="••••••••"
 hint="Must be at least 8 characters."
 required
 />

 <Button type="submit" class="w-full mt-4" :loading="isLoading">
 Create account
 </Button>
 </form>
 </div>

</template>
