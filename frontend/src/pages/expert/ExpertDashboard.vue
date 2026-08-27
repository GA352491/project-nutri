<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '../../api'

const router = useRouter()

const appointments = ref<any[]>([
  { id: 'apt_101', patient: 'Rohan Sharma', time: '10:00 AM', duration: '30m', status: 'Upcoming', type: 'Clinical Consultation', video_room_url: '/consultation/apt_101' },
  { id: 'apt_102', patient: 'Priya Patel', time: '11:30 AM', duration: '45m', status: 'Upcoming', type: 'PCOS Diet Follow-up', video_room_url: '/consultation/apt_102' },
  { id: 'apt_103', patient: 'Amit Kumar', time: '02:00 PM', duration: '30m', status: 'Upcoming', type: 'Sports Nutrition', video_room_url: '/consultation/apt_103' },
])

const stats = ref({
 total_patients: 45,
 monthly_earnings: 3240.00,
 rating: 4.9,
 pending_payouts: 480.00
})

const isLoading = ref(false)

async function fetchExpertDashboard() {
 isLoading.value = true
 try {
 const res = await apiClient.get('/marketplace/nutritionists/search')
 if (res.data && Array.isArray(res.data) && res.data.length > 0) {
 const first = res.data[0]
 stats.value.rating = first.rating || 4.9
 stats.value.total_patients = (first.review_count || 38) + 7
 stats.value.monthly_earnings = Math.round((first.hourly_rate_usd || 100) * 32)
 stats.value.pending_payouts = Math.round((first.hourly_rate_usd || 100) * 4)
 }
 } catch (err) {
 console.warn('Expert dashboard stats sync fallback:', err)
 }

 try {
    const apptRes = await apiClient.get('/appointments?nutritionist_id=nut_201')
    if (apptRes.data && Array.isArray(apptRes.data) && apptRes.data.length > 0) {
      appointments.value = apptRes.data.map((a: any) => ({
        id: a.id || a.appointment_id,
        patient: a.patient || a.user_id || 'Client',
        time: a.time || '10:00 AM',
        duration: a.duration || '30m',
        status: a.status || 'Upcoming',
        type: a.type || 'Nutrition Consultation',
        video_room_url: a.video_room_url || `/consultation/${a.id || a.appointment_id}`,
      }))
    }
  } catch (err) {
    console.warn('Live appointments fallback:', err)
  } finally {
 isLoading.value = false
 }
}

function handleJoinVideo(apt: any) {
  router.push(apt.video_room_url || `/consultation/${apt.id}`)
}

function handleViewProfile(_apt: any) {
  router.push('/expert/patients')
}

onMounted(() => {
 fetchExpertDashboard()
})
</script>

<template>
 <div class="space-y-8">
 
 <!-- Stats Grid -->
 <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
 <div class="bg-canvas-raised border border-border rounded-xl p-5 shadow-sm">
 <div class="font-data text-[0.75rem] text-ink-muted uppercase tracking-wider mb-2">Total Patients</div>
 <div class="font-display font-bold text-[2rem] text-ink tabular-nums">{{ stats.total_patients }}</div>
 </div>
 <div class="bg-canvas-raised border border-border rounded-xl p-5 shadow-sm">
 <div class="font-data text-[0.75rem] text-ink-muted uppercase tracking-wider mb-2">This Month</div>
 <div class="font-display font-bold text-[2rem] text-success tabular-nums">${{ stats.monthly_earnings.toLocaleString() }}</div>
 </div>
 <div class="bg-canvas-raised border border-border rounded-xl p-5 shadow-sm">
 <div class="font-data text-[0.75rem] text-ink-muted uppercase tracking-wider mb-2">Pending Payouts</div>
 <div class="font-display font-bold text-[2rem] text-ink tabular-nums">${{ stats.pending_payouts.toLocaleString() }}</div>
 </div>
 <div class="bg-canvas-raised border border-border rounded-xl p-5 shadow-sm">
 <div class="font-data text-[0.75rem] text-ink-muted uppercase tracking-wider mb-2">Average Rating</div>
 <div class="font-display font-bold text-[2rem] text-warning flex items-center gap-2">
 {{ stats.rating }}
 <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
 <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
 </svg>
 </div>
 </div>
 </div>

 <!-- Today's Schedule -->
 <div>
 <h2 class="font-display font-semibold text-[1.4rem] text-ink mb-4">Today's Schedule</h2>
 
 <div v-if="appointments.length === 0" class="text-center py-10 bg-canvas-raised border border-border rounded-xl text-ink-muted font-body">
 No appointments scheduled for today.
 </div>
 
 <div v-else class="space-y-4">
 <div 
 v-for="apt in appointments" 
 :key="apt.id"
 class="flex items-center justify-between p-5 bg-canvas-raised border border-border rounded-xl shadow-sm hover:border-primary/50 transition-colors"
 >
 <div class="flex items-center gap-5">
 <div class="text-center w-20">
 <div class="font-display font-bold text-[1.1rem] text-ink">{{ apt.time }}</div>
 <div class="font-data text-[0.75rem] text-ink-muted">{{ apt.duration }}</div>
 </div>
 <div class="w-px h-10 bg-border"></div>
 <div>
 <h3 class="font-display font-semibold text-[1.1rem] text-ink">{{ apt.patient }}</h3>
 <p class="font-body text-[0.9rem] text-ink-muted">{{ apt.type }}</p>
 </div>
 </div>
 
 <div class="flex items-center gap-3">
 <button
            @click="handleJoinVideo(apt)"
            class="px-4 py-2 bg-primary/10 text-primary font-body text-[0.9rem] font-medium rounded-lg hover:bg-primary/20 transition-colors cursor-pointer"
          >
            Join Video
          </button>
          <button
            @click="handleViewProfile(apt)"
            class="px-4 py-2 border border-border text-ink font-body text-[0.9rem] font-medium rounded-lg hover:bg-canvas transition-colors cursor-pointer"
          >
            View Profile
          </button>
 </div>
 </div>
 </div>
 </div>

 </div>
</template>
