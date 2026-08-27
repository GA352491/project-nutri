import axios from 'axios'
import { useToastStore } from './stores/toast'

// Create a centralized Axios instance
// Using Vite proxies, so base URL is just /api/v1
const apiClient = axios.create({
 baseURL: '/api/v1',
 headers: {
 'Content-Type': 'application/json',
 },
})

// Request interceptor for attaching auth tokens (JWT)
apiClient.interceptors.request.use(
 (config) => {
 const token = localStorage.getItem('auth_token')
 if (token) {
 config.headers.Authorization = `Bearer ${token}`
 }
 config.headers['X-Correlation-ID'] = crypto.randomUUID()
 return config
 },
 (error) => Promise.reject(error)
)

// Response interceptor for handling errors & session expiration
apiClient.interceptors.response.use(
 (response) => response,
 (error) => {
 const status = error.response?.status
 const errorDetail = error.response?.data?.message || error.response?.data?.detail || error.message || 'Request failed'
 const isPublicPage = ['/', '/login', '/register', '/terms', '/privacy', '/cookies'].includes(window.location.pathname)

 if (status === 401) {
 localStorage.removeItem('auth_token')
 if (!isPublicPage) {
 window.location.href = '/login'
 }
 } else if (status >= 500) {
 try {
 const toast = useToastStore()
 toast.error(errorDetail, 'Server Error')
 } catch {
 // Safe fallback
 }
 }
 return Promise.reject(error)
 }
)

export default apiClient
