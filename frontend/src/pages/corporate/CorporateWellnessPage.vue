<script setup lang="ts">
import { ref, computed } from 'vue'
import Icon from '../../components/ui/Icon.vue'
import Toast from '../../components/ui/Toast.vue'

const showToast = ref(false)
const toastMsg = ref('')

function notify(msg: string) {
 toastMsg.value = msg
 showToast.value = true
 setTimeout(() => { showToast.value = false }, 3500)
}

// Corporate Account State
const corporateAccount = ref({
 companyName: 'Acme Technologies Pvt Ltd',
 planTier: 'Enterprise Health Elite',
 totalSeatsPurchased: 250,
 activeSeatsUsed: 194,
 contractRenewal: '15 March 2027',
 accountManager: 'Priya Narayanan (NutriPlan Corporate)',
 avgCompanyAdherence: 88.4,
 cgmCoverageEnabled: true,
})

const showInviteModal = ref(false)
const showBulkSeatsModal = ref(false)

// Invite single / CSV state
const inviteEmail = ref('')
const inviteDepartment = ref('Engineering')
const inviteName = ref('')

// Bulk Seats Calculator state
const additionalSeats = ref(50)
const pricePerSeatAnnual = 1800 // INR per seat / year

const employees = ref([
 { id: 'emp_1', name: 'Rohan Sharma', email: 'rohan.s@acme.corp', department: 'Engineering', status: 'Active', loggedThisWeek: '18 / 21 meals', streak: 14, lastActive: 'Today' },
 { id: 'emp_2', name: 'Meera Deshmukh', email: 'meera.d@acme.corp', department: 'Product', status: 'Active', loggedThisWeek: '20 / 21 meals', streak: 21, lastActive: 'Today' },
 { id: 'emp_3', name: 'Aditya Varma', email: 'aditya.v@acme.corp', department: 'Sales', status: 'Active', loggedThisWeek: '14 / 21 meals', streak: 8, lastActive: 'Yesterday' },
 { id: 'emp_4', name: 'Siddharth Rao', email: 'sid.r@acme.corp', department: 'Human Resources', status: 'Active', loggedThisWeek: '16 / 21 meals', streak: 11, lastActive: 'Today' },
 { id: 'emp_5', name: 'Kavita Menon', email: 'kavita.m@acme.corp', department: 'Marketing', status: 'Pending Invite', loggedThisWeek: '—', streak: 0, lastActive: 'Invited 2d ago' },
 { id: 'emp_6', name: 'Arjun Nambiar', email: 'arjun.n@acme.corp', department: 'Engineering', status: 'Active', loggedThisWeek: '19 / 21 meals', streak: 19, lastActive: 'Today' },
])

const filterDept = ref('All')
const filteredEmployees = computed(() => {
 if (filterDept.value === 'All') return employees.value
 return employees.value.filter(e => e.department === filterDept.value)
})

function sendEmployeeInvite() {
 if (!inviteEmail.value) return
 employees.value.push({
 id: `emp_${Date.now()}`,
 name: inviteName.value || inviteEmail.value.split('@')[0],
 email: inviteEmail.value,
 department: inviteDepartment.value,
 status: 'Pending Invite',
 loggedThisWeek: '0 / 21 meals',
 streak: 0,
 lastActive: 'Just now',
 })
 corporateAccount.value.activeSeatsUsed++
 showInviteModal.value = false
 inviteEmail.value = ''
 inviteName.value = ''
 notify('Employee wellness onboarding invitation dispatched successfully!')
}

function handleCsvUpload(e: Event) {
 const target = e.target as HTMLInputElement
 if (target.files && target.files.length > 0) {
 notify(`Parsed ${target.files[0].name}: 24 employee seats allocated and invitation emails queued!`)
 corporateAccount.value.activeSeatsUsed = Math.min(
 corporateAccount.value.totalSeatsPurchased,
 corporateAccount.value.activeSeatsUsed + 24
 )
 }
}

function purchaseAdditionalSeats() {
 corporateAccount.value.totalSeatsPurchased += additionalSeats.value
 showBulkSeatsModal.value = false
 notify(`Successfully added ${additionalSeats.value} corporate seats to contract! Invoice generated.`)
}
</script>

<template>
 <div class="space-y-6">
 <Toast v-if="showToast" :message="toastMsg" @close="showToast = false" />

 <!-- Top Corporate Welcome & Cohort Summary -->
 <div class="bg-gradient-to-r from-neutral-900 via-neutral-800 to-neutral-900 text-white rounded-2xl p-6 border border-neutral-800 shadow-xl relative overflow-hidden">
 <div class="absolute -right-10 -bottom-10 w-48 h-48 bg-primary/20 rounded-full blur-3xl pointer-events-none"></div>

 <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
 <div>
 <div class="flex items-center gap-2">
 <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-primary text-white uppercase tracking-wider">
 B2B Corporate Wellness
 </span>
 <span class="text-xs text-neutral-400">&bull; Account ID: CORP-ACME-2026</span>
 </div>
 <h1 class="font-display font-bold text-2xl text-white mt-1.5">{{ corporateAccount.companyName }}</h1>
 <p class="text-xs text-neutral-300 mt-1">
 Program: <span class="font-semibold text-emerald-400">{{ corporateAccount.planTier }}</span> &bull; Contract Renewal: {{ corporateAccount.contractRenewal }}
 </p>
 </div>

 <div class="flex items-center gap-3">
 <button
 @click="showBulkSeatsModal = true"
 class="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white border border-white/20 rounded-xl text-xs font-semibold backdrop-blur-md transition-all flex items-center gap-2 cursor-pointer"
 >
 <Icon name="plus" class="w-4 h-4" />
 Add Seats
 </button>
 <button
 @click="showInviteModal = true"
 class="px-4 py-2.5 bg-primary hover:bg-primary-strong text-white rounded-xl text-xs font-bold shadow-md transition-all flex items-center gap-2 cursor-pointer"
 >
 <Icon name="users" class="w-4 h-4" />
 Invite Employees
 </button>
 </div>
 </div>

 <!-- Quick Metrics Ribbon -->
 <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10">
 <div class="bg-white/5 p-3.5 rounded-xl border border-white/5">
 <p class="text-[10px] text-neutral-400 uppercase font-semibold">Seat Utilization</p>
 <div class="flex items-baseline gap-2 mt-1">
 <span class="text-xl font-bold font-mono text-white">{{ corporateAccount.activeSeatsUsed }}</span>
 <span class="text-xs text-neutral-400 font-mono">/ {{ corporateAccount.totalSeatsPurchased }}</span>
 </div>
 <div class="w-full bg-white/10 h-1.5 rounded-full mt-2 overflow-hidden">
 <div 
 class="bg-emerald-400 h-full rounded-full transition-all duration-500" 
 :style="{ width: `${(corporateAccount.activeSeatsUsed / corporateAccount.totalSeatsPurchased) * 100}%` }"
 ></div>
 </div>
 </div>

 <div class="bg-white/5 p-3.5 rounded-xl border border-white/5">
 <p class="text-[10px] text-neutral-400 uppercase font-semibold">Cohort Adherence</p>
 <p class="text-xl font-bold font-mono text-emerald-400 mt-1">{{ corporateAccount.avgCompanyAdherence }}%</p>
 <p class="text-[10px] text-neutral-400 mt-0.5">&uarr; 6.2% vs last month</p>
 </div>

 <div class="bg-white/5 p-3.5 rounded-xl border border-white/5">
 <p class="text-[10px] text-neutral-400 uppercase font-semibold">Dietitian Consults</p>
 <p class="text-xl font-bold font-mono text-sky-400 mt-1">142 Sessions</p>
 <p class="text-[10px] text-neutral-400 mt-0.5">Completed across team</p>
 </div>

 <div class="bg-white/5 p-3.5 rounded-xl border border-white/5">
 <p class="text-[10px] text-neutral-400 uppercase font-semibold">CGM Metabolic Shield</p>
 <p class="text-xl font-bold font-mono text-amber-300 mt-1">Active</p>
 <p class="text-[10px] text-neutral-400 mt-0.5">Continuous glucose pilot</p>
 </div>
 </div>
 </div>

 <!-- Employee Roster & Department Filters -->
 <div class="bg-canvas-raised border border-border rounded-2xl p-6 shadow-sm space-y-5">
 <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
 <div>
 <h2 class="font-display font-semibold text-lg text-ink">Employee Wellness Roster</h2>
 <p class="font-body text-xs text-ink-muted">Manage seat allocations, track team streaks, and export cohort adherence</p>
 </div>

 <!-- Department Tabs -->
 <div class="flex items-center gap-2 overflow-x-auto pb-1">
 <button
 v-for="dept in ['All', 'Engineering', 'Product', 'Sales', 'Marketing', 'Human Resources']"
 :key="dept"
 class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer shrink-0"
 :class="filterDept === dept ? 'bg-primary text-white' : 'bg-canvas border border-border text-ink-muted hover:text-ink'"
 @click="filterDept = dept"
 >
 {{ dept }}
 </button>
 </div>
 </div>

 <!-- Table -->
 <div class="border border-border rounded-xl overflow-hidden bg-canvas">
 <table class="w-full text-left border-collapse">
 <thead>
 <tr class="bg-canvas-raised border-b border-border text-[11px] font-semibold text-ink-muted uppercase tracking-wider">
 <th class="py-3 px-4">Employee</th>
 <th class="py-3 px-4">Department</th>
 <th class="py-3 px-4">Status</th>
 <th class="py-3 px-4">Weekly Adherence</th>
 <th class="py-3 px-4">Streak</th>
 <th class="py-3 px-4 text-right">Actions</th>
 </tr>
 </thead>
 <tbody class="divide-y divide-border text-sm">
 <tr v-for="emp in filteredEmployees" :key="emp.id" class="hover:bg-primary-soft/20 transition-colors">
 <td class="py-3.5 px-4">
 <div class="font-semibold text-ink text-xs">{{ emp.name }}</div>
 <div class="text-[11px] text-ink-muted font-mono">{{ emp.email }}</div>
 </td>
 <td class="py-3.5 px-4 text-xs text-ink-muted">{{ emp.department }}</td>
 <td class="py-3.5 px-4">
 <span
 class="px-2.5 py-0.5 rounded-full text-[10px] font-bold inline-flex items-center gap-1"
 :class="emp.status === 'Active' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
 >
 <span class="w-1.5 h-1.5 rounded-full" :class="emp.status === 'Active' ? 'bg-emerald-600' : 'bg-amber-600'"></span>
 {{ emp.status }}
 </span>
 </td>
 <td class="py-3.5 px-4 font-mono text-xs text-ink">{{ emp.loggedThisWeek }}</td>
 <td class="py-3.5 px-4">
 <span v-if="emp.streak > 0" class="font-bold font-mono text-xs text-amber-600 flex items-center gap-1">
 {{ emp.streak }}d
 </span>
 <span v-else class="text-xs text-ink-muted">—</span>
 </td>
 <td class="py-3.5 px-4 text-right">
 <button
 @click="notify(`Sent weekly wellness cheer to ${emp.name}!`)"
 class="text-primary hover:underline text-xs font-semibold"
 >
 Cheer &bull; Re-engage
 </button>
 </td>
 </tr>
 </tbody>
 </table>
 </div>
 </div>

 <!-- Bulk Seat Purchase Modal -->
 <div v-if="showBulkSeatsModal" class="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
 <div class="bg-canvas-raised rounded-2xl border border-border shadow-2xl max-w-md w-full p-6 space-y-5">
 <div class="flex items-center justify-between border-b border-border pb-4">
 <div>
 <h3 class="font-display font-bold text-lg text-ink">Add Corporate Wellness Seats</h3>
 <p class="text-xs text-ink-muted">Expand seat allocation for new departments or cohorts</p>
 </div>
 <button @click="showBulkSeatsModal = false" class="text-ink-muted hover:text-ink">
 <Icon name="x" class="w-5 h-5" />
 </button>
 </div>

 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-2">Number of Additional Seats</label>
 <div class="flex items-center gap-3">
 <input
 type="range"
 min="10"
 max="500"
 step="10"
 v-model.number="additionalSeats"
 class="w-full accent-primary"
 />
 <span class="font-mono font-bold text-base text-ink w-16 text-right">{{ additionalSeats }} seats</span>
 </div>
 </div>

 <div class="bg-canvas p-4 rounded-xl border border-border space-y-2 text-xs">
 <div class="flex justify-between text-ink-muted">
 <span>Price Per Seat (Annual)</span>
 <span class="font-mono text-ink">₹{{ pricePerSeatAnnual.toLocaleString() }}/yr</span>
 </div>
 <div class="flex justify-between font-bold text-sm text-ink border-t border-border pt-2">
 <span>Total Contract Addition</span>
 <span class="text-primary font-mono">₹{{ (additionalSeats * pricePerSeatAnnual).toLocaleString() }}</span>
 </div>
 </div>

 <div class="flex justify-end gap-3 pt-2">
 <button @click="showBulkSeatsModal = false" class="px-4 py-2 text-xs font-semibold text-ink-muted hover:text-ink">Cancel</button>
 <button @click="purchaseAdditionalSeats" class="px-5 py-2 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl shadow">
 Confirm & Issue Invoice
 </button>
 </div>
 </div>
 </div>

 <!-- Invite Employees Modal -->
 <div v-if="showInviteModal" class="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
 <div class="bg-canvas-raised rounded-2xl border border-border shadow-2xl max-w-md w-full p-6 space-y-5">
 <div class="flex items-center justify-between border-b border-border pb-4">
 <div>
 <h3 class="font-display font-bold text-lg text-ink">Invite Employee to Program</h3>
 <p class="text-xs text-ink-muted">Send automated onboarding link via work email</p>
 </div>
 <button @click="showInviteModal = false" class="text-ink-muted hover:text-ink">
 <Icon name="x" class="w-5 h-5" />
 </button>
 </div>

 <div class="space-y-3">
 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Full Name</label>
 <input v-model="inviteName" placeholder="e.g. Priya Sundaram" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink" />
 </div>

 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Work Email</label>
 <input v-model="inviteEmail" placeholder="priya@acme.corp" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink" />
 </div>

 <div>
 <label class="block text-xs font-semibold uppercase text-ink mb-1">Department</label>
 <select v-model="inviteDepartment" class="w-full px-3 py-2 text-xs rounded-lg bg-canvas border border-border outline-none focus:border-primary text-ink">
 <option>Engineering</option>
 <option>Product</option>
 <option>Sales</option>
 <option>Marketing</option>
 <option>Human Resources</option>
 </select>
 </div>

 <!-- CSV Bulk Option -->
 <div class="pt-2">
 <label class="block text-xs font-semibold uppercase text-ink-muted mb-1.5">Or Upload Team CSV</label>
 <label class="border-2 border-dashed border-border hover:border-primary/50 bg-canvas rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer">
 <Icon name="file-text" class="w-5 h-5 text-primary mb-1" />
 <span class="text-xs font-medium text-ink">Click to upload .csv roster</span>
 <input type="file" accept=".csv" class="hidden" @change="handleCsvUpload" />
 </label>
 </div>
 </div>

 <div class="flex justify-end gap-3 pt-2">
 <button @click="showInviteModal = false" class="px-4 py-2 text-xs font-semibold text-ink-muted hover:text-ink">Cancel</button>
 <button @click="sendEmployeeInvite" class="px-5 py-2 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl shadow">
 Send Invitation
 </button>
 </div>
 </div>
 </div>

 </div>
</template>
