<script setup lang="ts">
// Centered single-column layout for Login / Register pages
</script>

<template>
 <div class="min-h-screen bg-canvas flex flex-col items-center justify-center px-4 py-12">
 <!-- Brand mark -->
 <div class="mb-8 flex flex-col items-center gap-3">
 <div class="w-12 h-12 rounded-xl bg-primary flex items-center justify-center text-white font-display font-bold text-[1.4rem] shadow-card">
 N
 </div>
 <span class="font-display font-semibold text-[1.4rem] text-ink">NutriPlan</span>
 </div>

 <!-- Card panel -->
 <div class="w-full max-w-md bg-canvas-raised rounded-lg shadow-card p-8 border border-border">
 <slot />
 </div>

 <!-- Footer text -->
 <p class="mt-6 text-[0.8rem] text-ink-muted text-center">
 <span v-if="$route.path === '/login'">
 Don't have an account? 
 <RouterLink to="/register" class="text-primary font-semibold hover:underline">Sign up</RouterLink>
 </span>
 <span v-else-if="$route.path === '/register'">
 Already have an account? 
 <RouterLink to="/login" class="text-primary font-semibold hover:underline">Sign in</RouterLink>
 </span>
 </p>
 </div>
</template>
