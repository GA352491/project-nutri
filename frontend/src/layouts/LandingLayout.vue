<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Button from '../components/ui/Button.vue'
import Icon from '../components/ui/Icon.vue'

const router = useRouter()
const route = useRoute()

const scrolled = ref(false)
const mobileOpen = ref(false)

function onScroll() { scrolled.value = window.scrollY > 30 }
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'Palate Tour', href: '#palate-tour' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
]

function scrollTo(href: string) {
  mobileOpen.value = false
  if (href.startsWith('#')) {
    document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' })
  } else {
    router.push(href)
  }
}

function isLegalPage() {
  return ['/privacy', '/terms', '/cookies'].includes(route.path)
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-canvas font-body text-ink">

    <!-- ── Nav Header ─────────────────────────────────────────────────────── -->
    <header
      class="fixed inset-x-0 top-0 z-50 transition-all duration-300"
      :class="scrolled || mobileOpen || isLegalPage()
        ? 'bg-canvas-raised/90 backdrop-blur-md border-b border-border shadow-xs'
        : 'bg-transparent'"
    >
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

        <!-- Logo / Brand Mark matching AppLayout -->
        <a href="/" class="flex items-center gap-2.5 group no-underline">
          <div class="w-8 h-8 rounded-md bg-primary flex items-center justify-center text-white font-display font-bold text-[0.95rem] shadow-xs group-hover:bg-primary-strong transition-colors">
            N
          </div>
          <div class="flex items-baseline gap-1">
            <span class="font-display font-bold text-[1.2rem] text-ink tracking-tight">
              Nutri<span class="text-primary">Plan</span>
            </span>
            <span class="text-[0.65rem] font-data uppercase tracking-wider px-1.5 py-0.5 rounded bg-primary-soft text-primary font-bold">
              AI
            </span>
          </div>
        </a>

        <!-- Desktop Navigation Links -->
        <nav v-if="!isLegalPage()" class="hidden md:flex items-center gap-8">
          <button
            v-for="link in navLinks"
            :key="link.label"
            class="text-[0.88rem] font-medium text-ink-muted hover:text-primary transition-colors cursor-pointer"
            @click="scrollTo(link.href)"
          >{{ link.label }}</button>
        </nav>

        <!-- Desktop CTAs -->
        <div class="hidden md:flex items-center gap-3">
          <a href="/login" class="text-[0.88rem] font-semibold text-ink-muted hover:text-ink transition-colors px-3 py-1.5 no-underline">
            Sign in
          </a>
          <Button variant="primary" size="sm" @click="router.push('/register')">
            Start Free →
          </Button>
        </div>

        <!-- Mobile Hamburger -->
        <button
          class="md:hidden w-9 h-9 flex flex-col justify-center items-center gap-1.5 cursor-pointer rounded-lg hover:bg-canvas p-1 transition-colors"
          aria-label="Toggle menu"
          @click="mobileOpen = !mobileOpen"
        >
          <span class="w-5 h-0.5 bg-ink transition-all" :class="mobileOpen ? 'rotate-45 translate-y-[8px]' : ''" />
          <span class="w-5 h-0.5 bg-ink transition-all" :class="mobileOpen ? 'opacity-0' : ''" />
          <span class="w-5 h-0.5 bg-ink transition-all" :class="mobileOpen ? '-rotate-45 -translate-y-[8px]' : ''" />
        </button>
      </div>

      <!-- Mobile Menu Dropdown -->
      <transition name="slide-down">
        <div v-if="mobileOpen" class="md:hidden border-t border-border bg-canvas-raised px-6 py-4 space-y-1 shadow-card">
          <button
            v-for="link in navLinks"
            :key="link.label"
            class="block w-full text-left px-3 py-2.5 rounded-lg text-[0.92rem] font-medium text-ink hover:bg-canvas transition-colors cursor-pointer"
            @click="scrollTo(link.href)"
          >{{ link.label }}</button>
          <div class="pt-3 flex flex-col gap-2 border-t border-border mt-2">
            <a href="/login" class="block text-center px-4 py-2.5 rounded-lg border border-border text-[0.92rem] font-medium text-ink no-underline hover:bg-canvas transition-colors">
              Sign in
            </a>
            <Button variant="primary" @click="router.push('/register')" class="w-full">
              Start Free →
            </Button>
          </div>
        </div>
      </transition>
    </header>

    <!-- ── Page Content ───────────────────────────────────────────── -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- ── Footer ─────────────────────────────────────────────────── -->
    <footer class="border-t border-border bg-canvas-raised pt-16 pb-12">
      <div class="max-w-7xl mx-auto px-6">
        <div class="grid grid-cols-2 md:grid-cols-5 gap-10 mb-12">

          <!-- Brand info -->
          <div class="col-span-2 md:col-span-2">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-7 h-7 rounded-md bg-primary flex items-center justify-center text-white font-display font-bold text-[0.9rem]">
                N
              </div>
              <span class="font-display font-bold text-[1.1rem] text-ink">
                Nutri<span class="text-primary">Plan</span> AI
              </span>
            </div>
            <p class="text-[0.85rem] text-ink-muted leading-relaxed max-w-sm">
              Personalized precision nutrition engine grounded in ICMR-NIN Indian Food Composition science, authentic regional traditions, and wearable telemetry.
            </p>
            <div class="flex items-center gap-3 mt-5">
              <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[0.72rem] font-data bg-primary-soft text-primary font-bold">
                <Icon name="shield-check" :size="13" />
                ICMR-NIN IFCT Grounded
              </span>
              <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[0.72rem] font-data bg-secondary-soft text-ink font-bold">
                <Icon name="wearable" :size="13" />
                Durable Workflows
              </span>
            </div>
          </div>

          <!-- Product -->
          <div>
            <h4 class="text-[0.72rem] font-data font-bold text-ink-muted uppercase tracking-widest mb-4">Product</h4>
            <ul class="space-y-2.5">
              <li v-for="l in [
                { name: '7-Day Palate Tour', href: '#palate-tour' },
                { name: 'Features', href: '#features' },
                { name: 'How it Works', href: '#how-it-works' },
                { name: 'Pricing & Plans', href: '#pricing' },
              ]" :key="l.name">
                <a :href="l.href" class="text-[0.88rem] text-ink-muted hover:text-primary transition-colors no-underline">{{ l.name }}</a>
              </li>
            </ul>
          </div>

          <!-- Portals -->
          <div>
            <h4 class="text-[0.72rem] font-data font-bold text-ink-muted uppercase tracking-widest mb-4">Portals</h4>
            <ul class="space-y-2.5">
              <li><a href="/login" class="text-[0.88rem] text-ink-muted hover:text-primary transition-colors no-underline">Patient Portal</a></li>
              <li><a href="/login" class="text-[0.88rem] text-ink-muted hover:text-primary transition-colors no-underline">Dietitian / Provider Hub</a></li>
              <li><a href="/login" class="text-[0.88rem] text-ink-muted hover:text-primary transition-colors no-underline">Admin & Governance</a></li>
              <li><a href="/corporate" class="text-[0.88rem] text-ink-muted hover:text-primary transition-colors no-underline">Corporate Wellness</a></li>
            </ul>
          </div>

          <!-- Legal -->
          <div>
            <h4 class="text-[0.72rem] font-data font-bold text-ink-muted uppercase tracking-widest mb-4">Legal & Trust</h4>
            <ul class="space-y-2.5">
              <li><a href="/privacy" class="text-[0.88rem] text-ink-muted hover:text-primary transition-colors no-underline">Privacy Policy</a></li>
              <li><a href="/terms" class="text-[0.88rem] text-ink-muted hover:text-primary transition-colors no-underline">Terms of Service</a></li>
              <li><a href="/cookies" class="text-[0.88rem] text-ink-muted hover:text-primary transition-colors no-underline">Cookie Policy</a></li>
              <li><span class="text-[0.88rem] text-ink-muted">GDPR & CCPA Compliant</span></li>
            </ul>
          </div>
        </div>

        <!-- Bottom bar -->
        <div class="border-t border-border pt-8 flex flex-col md:flex-row items-center justify-between gap-4 text-[0.78rem] text-ink-muted">
          <p>© 2026 NutriPlan AI, Inc. All rights reserved.</p>
          <p class="text-center md:text-right max-w-xl">
            NutriPlan AI is an auxiliary dietary intelligence tool and not a substitute for clinical medical advice. Always consult a certified healthcare professional.
          </p>
        </div>
      </div>
    </footer>

  </div>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active {
  transition: all 200ms var(--ease-out);
}
.slide-down-enter-from, .slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>

