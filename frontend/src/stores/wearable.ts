import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../api'

export interface WearableReading {
  timestamp: string
  heart_rate?: number
  steps?: number
  calories_burned?: number
  active_calories?: number
  basal_calories?: number
  sleep_hours?: number
  hrv_ms?: number
  blood_oxygen?: number
  strain?: number
  recovery_score?: number
  device: string
}

export interface WearableSummary {
  today_steps: number
  today_calories: number
  avg_heart_rate: number
  sleep_last_night: number
  blood_oxygen: number
  hrv_ms: number
  strain?: number
  recovery_score?: number
  connected_device: string | null
  last_sync: string | null
  readings_7d: WearableReading[]
  total_calories_burned?: number
  tdee_adjustment_kcal?: number
  adaptive_message?: string
  has_data?: boolean
}

export interface CGMLiveTelemetry {
  user_id: string
  sensor_model: string
  current_glucose_mg_dl: number
  trend_arrow: string
  time_in_range_pct: number
  average_glucose_mg_dl: number
  estimated_hba1c: number
  readings_24h: Array<{
    timestamp: string
    time_label: string
    glucose_mg_dl: number
    in_range: boolean
  }>
  active_alert?: {
    severity: string
    message: string
  } | null
  glycemic_variability_cv_pct: number
}

export const useWearableStore = defineStore('wearable', () => {
  const summary = ref<WearableSummary | null>(null)
  const cgmTelemetry = ref<CGMLiveTelemetry | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchSummary(userId: string) {
    isLoading.value = true
    error.value = null
    try {
      const res = await apiClient.get(`/wearable/summary/${userId}`)
      summary.value = res.data
    } catch (err: any) {
      error.value = err?.message || 'Failed to load wearable metrics'
      console.warn('Wearable backend service unavailable:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchLiveCgm(userId: string, scenario: 'fiber_first' | 'carbs_first' | 'fasting' = 'fiber_first') {
    try {
      const res = await apiClient.get(`/wearable/cgm/live-stream/${userId}?scenario=${scenario}`)
      cgmTelemetry.value = res.data
      return res.data
    } catch (err) {
      console.warn('CGM Live stream unavailable:', err)
      return null
    }
  }

  async function ingestReading(reading: Omit<WearableReading, 'timestamp'>) {
    try {
      await apiClient.post('/wearable/ingest', {
        ...reading,
        timestamp: new Date().toISOString()
      })
    } catch (err) {
      console.error('Failed to ingest wearable reading:', err)
    }
  }

  async function triggerOAuth(provider: string, userId: string) {
    try {
      const res = await apiClient.get(`/wearable/oauth/${provider}/authorize?user_id=${userId}`)
      return res.data
    } catch (err) {
      console.error(`Failed to authorize ${provider}:`, err)
      return null
    }
  }

  return { 
    summary, 
    cgmTelemetry, 
    isLoading, 
    error, 
    fetchSummary, 
    fetchLiveCgm, 
    ingestReading, 
    triggerOAuth 
  }
})
