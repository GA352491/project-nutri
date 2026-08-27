import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api'

export interface User {
 id: string
 email: string
 name: string
 role: 'patient' | 'nutritionist' | 'admin'
 avatar?: string
 subscription?: 'free' | 'premium'
 onboarding_complete?: boolean
}

export const useAuthStore = defineStore('auth', () => {
 // ── State ──────────────────────────────────────────────
 const token = ref<string | null>(localStorage.getItem('auth_token'))
 const user = ref<User | null>(null)
 const isLoading = ref(false)
 const error = ref<string | null>(null)

 // ── Getters ────────────────────────────────────────────
 const isAuthenticated = computed(() => !!token.value)
 const isAdmin = computed(() => user.value?.role === 'admin')
 const isNutritionist = computed(() => user.value?.role === 'nutritionist')
 const isPatient = computed(() => user.value?.role === 'patient')

 // ── Actions ────────────────────────────────────────────
 async function login(email: string, password: string) {
 isLoading.value = true
 error.value = null
 try {
 const res = await apiClient.post('/auth/login', { email, password })
 token.value = res.data.access_token
 localStorage.setItem('auth_token', res.data.access_token)
 if (res.data.user) {
 user.value = {
 id: String(res.data.user.id),
 email: res.data.user.email,
 name: res.data.user.full_name || res.data.user.name || 'User',
 role: res.data.user.role,
 }
 } else {
 await fetchMe()
 }
 return true
 } catch (err: any) {
 error.value = err.response?.data?.detail || 'Login failed'
 return false
 } finally {
 isLoading.value = false
 }
 }

 async function register(email: string, password: string, name: string) {
 isLoading.value = true
 error.value = null
 try {
 const res = await apiClient.post('/auth/register', { 
 email, 
 password, 
 name,
 full_name: name 
 })
 token.value = res.data.access_token
 localStorage.setItem('auth_token', res.data.access_token)
 await fetchMe()
 return true
 } catch (err: any) {
 error.value = err.response?.data?.detail || 'Registration failed'
 return false
 } finally {
 isLoading.value = false
 }
 }

 async function fetchMe() {
 if (!token.value) return
 try {
 const res = await apiClient.get('/auth/me')
 user.value = res.data
 } catch {
 // Token is invalid — clear everything
 logout()
 }
 }

 function logout() {
 token.value = null
 user.value = null
 localStorage.removeItem('auth_token')
 }

 // Bootstrap: try to rehydrate user from saved token on app start
 async function init() {
 if (token.value && !user.value) {
 await fetchMe()
 }
 }

 return {
 token, user, isLoading, error,
 isAuthenticated, isAdmin, isNutritionist, isPatient,
 login, register, logout, fetchMe, init,
 }
})
