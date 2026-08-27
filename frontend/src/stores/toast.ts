import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ToastItem {
 id: string
 message: string
 title?: string
 variant?: 'success' | 'warning' | 'danger' | 'info'
 duration?: number
}

export const useToastStore = defineStore('toast', () => {
 const toasts = ref<ToastItem[]>([])

 function show(toast: Omit<ToastItem, 'id'>) {
 const id = `toast_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`
 const newToast: ToastItem = {
 id,
 duration: 4000,
 variant: 'info',
 ...toast,
 }
 toasts.value.push(newToast)

 if (newToast.duration && newToast.duration > 0) {
 setTimeout(() => {
 remove(id)
 }, newToast.duration)
 }
 return id
 }

 function success(message: string, title?: string) {
 return show({ message, title, variant: 'success' })
 }

 function error(message: string, title?: string) {
 return show({ message, title: title || 'Error', variant: 'danger', duration: 5000 })
 }

 function warning(message: string, title?: string) {
 return show({ message, title, variant: 'warning' })
 }

 function info(message: string, title?: string) {
 return show({ message, title, variant: 'info' })
 }

 function remove(id: string) {
 toasts.value = toasts.value.filter((t) => t.id !== id)
 }

 return {
 toasts,
 show,
 success,
 error,
 warning,
 info,
 remove,
 }
})
