<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../../components/ui/Button.vue'
import Icon from '../../components/ui/Icon.vue'
import MacroRing from '../../components/MacroRing.vue'

const router = useRouter()

// FAQ accordion
const openFaq = ref<number | null>(0)
function toggleFaq(i: number) {
  openFaq.value = openFaq.value === i ? null : i
}

const faqs = [
  {
    q: 'How does the ICMR-NIN grounded AI meal planning work?',
    a: 'NutriPlan uses clinical data from the Indian Council of Medical Research (ICMR-NIN) and Indian Food Composition Tables (IFCT). Our solver calculates exact macros, calcium, iron, and fiber across regional cuisines with sub-20ms deterministic precision.'
  },
  {
    q: 'What is the 7-Day Regional Palate Rotation Tour?',
    a: 'Our automated rotation cycles through authentic regional food cultures daily (Mon: Andhra/Telangana, Tue: Punjab, Wed: Kerala, Thu: Maharashtra, Fri: Bengal, Sat: Gujarat, Sun: Pan-India Fusion), keeping nutrition exciting and nutrient-diverse.'
  },
  {
    q: 'Can I order missing grocery items automatically?',
    a: 'Yes! With 1-Click Quick-Commerce Cart Sync, NutriPlan deep links and pushes missing recipe ingredients directly into your Zepto, Blinkit, or Instacart carts powered by Temporal delivery sagas.'
  },
  {
    q: 'How do wearable devices adjust my nutrition plan?',
    a: 'We connect with Apple Health, Google Fit, Fitbit, Garmin, and CGM monitors. Your active calorie burn and daily step count dynamically adjust your caloric baseline and hydration targets.'
  },
  {
    q: 'Is NutriPlan AI a replacement for a certified dietitian?',
    a: 'NutriPlan complements medical nutrition therapy. You can book 1-on-1 consultations with verified nutritionists who review your food diary, co-pilot clinical SOAP notes, and fine-tune your targets.'
  },
  {
    q: 'Can I use NutriPlan with my family or workplace?',
    a: 'Yes! Our Family Plan supports up to 5 individual profiles with merged grocery lists, while our Corporate Wellness tier offers team challenges and engagement analytics.'
  }
]

const testimonials = [
  {
    name: 'Priya Sharma',
    role: 'Software Engineer, Bengaluru',
    avatar: 'PS',
    quote: 'NutriPlan understood my South Indian dietary preferences instantly — no bland salads, just balanced dosas, sambar, and ragi mudde tailored to my 1,800 kcal target.'
  },
  {
    name: 'Arjun Mehta',
    role: 'Fitness Coach, Mumbai',
    avatar: 'AM',
    quote: 'The 1-click Zepto grocery sync and Temporal workflow integration are revolutionary. My clients never drop off because their meal prep is completely frictionless.'
  },
  {
    name: 'Dr. Kavitha Nair',
    role: 'Clinical Dietitian, Chennai',
    avatar: 'KN',
    quote: 'The Provider Hub is state-of-the-art. Real-time patient diary analytics, AI SOAP note co-pilot, and instant prescription dispatch save me hours each week.'
  }
]

const features = [
  {
    icon: 'plan',
    title: '7-Day Regional Palate Tour',
    desc: 'Auto-rotating culinary journeys across Andhra, Punjab, Kerala, Maharashtra, Bengal, and Gujarat with sub-15ms meal swaps.'
  },
  {
    icon: 'diary',
    title: 'Smart Food Diary & Barcode Log',
    desc: 'Log meals with instant macro analysis, photo AI recognition, and automated ICMR-NIN micronutrient deficit alerts.'
  },
  {
    icon: 'grocery',
    title: '1-Click Quick-Commerce Sync',
    desc: 'Push auto-categorized ingredient lists directly to Zepto, Blinkit, and Instacart carts in under 10 minutes.'
  },
  {
    icon: 'wearable',
    title: 'Continuous Telemetry & CGM Sync',
    desc: 'Real-time step counts, active burn, and continuous glucose telemetry calibrate your caloric target adaptively.'
  },
  {
    icon: 'consultation',
    title: '1-on-1 Expert Provider Hub',
    desc: 'Encrypted HD video consultations with licensed dietitians, live clinical SOAP notes, and IDA verification.'
  },
  {
    icon: 'users',
    title: 'Family & Corporate Wellness',
    desc: 'Up to 5 synced family member profiles or corporate B2B team health leagues with private analytics.'
  }
]

const tourDays = [
  { day: 'Mon', region: 'Andhra / Telangana', theme: 'High-protein lentils & sun-dried spices', kcal: 1840 },
  { day: 'Tue', region: 'Punjab & North', theme: 'Whole wheat rotis, paneer & rich dal', kcal: 1850 },
  { day: 'Wed', region: 'Kerala Coastal', theme: 'Red rice, coconut stew & garden greens', kcal: 1820 },
  { day: 'Thu', region: 'Maharashtra', theme: 'Sprouted matki, usal & jowar bhakri', kcal: 1860 },
  { day: 'Fri', region: 'Bengal Delicacies', theme: 'Panch phoron, seasonal saag & lentils', kcal: 1830 },
  { day: 'Sat', region: 'Gujarat & West', theme: 'Steamed dhokla & sweet-tangy kadhi', kcal: 1845 },
  { day: 'Sun', region: 'Pan-India Blend', theme: 'Curated fusion of regional favorites', kcal: 1850 },
]

const plans = [
  {
    name: 'Free Starter',
    price: '₹0',
    period: 'forever',
    highlight: false,
    badge: 'FREE FOREVER',
    features: ['7-Day Regional Palate Tour', 'Daily Food Diary & Macro Ring', 'Standard Grocery List', '3 Meal Swaps / week'],
    cta: 'Start Free',
    variant: 'outline' as const,
  },
  {
    name: 'Pro Precision',
    price: '₹499',
    period: 'per month',
    highlight: true,
    badge: 'MOST POPULAR',
    features: ['Unlimited Regional Meal Swaps', '1-Click Quick-Commerce Sync (Zepto/Blinkit)', 'Wearables & CGM Live Telemetry', '1 Expert Video Consultation / month', 'ICMR-NIN Deficit Auto-Fixer'],
    cta: 'Start 14-Day Free Trial',
    variant: 'primary' as const,
  },
  {
    name: 'Family Health',
    price: '₹899',
    period: 'per month',
    highlight: false,
    badge: 'HOUSEHOLD',
    features: ['Everything in Pro Precision', 'Up to 5 Family Member Profiles', '3 Expert Video Consultations / month', 'Merged Family Grocery Orders', 'Dedicated Priority Care Concierge'],
    cta: 'Get Family Plan',
    variant: 'secondary' as const,
  }
]
</script>

<template>
  <div>

    <!-- ═══════════════════════════════════════════════════════
         HERO SECTION
    ═══════════════════════════════════════════════════════ -->
    <section class="relative pt-32 pb-20 px-6 overflow-hidden bg-gradient-to-b from-canvas via-primary-soft/20 to-canvas">
      <div class="max-w-6xl mx-auto flex flex-col items-center text-center">

        <!-- Trust Badge -->
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-primary-soft border border-primary/25 text-primary text-[0.8rem] font-semibold mb-6 shadow-xs">
          <span class="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span>Grounded in ICMR-NIN Science &amp; Authentic Regional Indian Cuisines</span>
        </div>

        <!-- Headline -->
        <h1 class="font-display font-bold text-[2.8rem] sm:text-[3.8rem] lg:text-[4.6rem] leading-[1.08] text-ink max-w-4xl tracking-tight mb-6">
          Your Personal AI <br class="hidden sm:inline" />
          <span class="text-primary italic">Precision Nutrition</span> Engine.
        </h1>

        <!-- Subheadline -->
        <p class="font-body text-[1.05rem] sm:text-[1.2rem] text-ink-muted max-w-2xl leading-relaxed mb-10">
          Personalized weekly regional meal plans, instant food diary tracking, 1-click Zepto &amp; Blinkit grocery checkout, and certified dietitian co-pilots.
        </p>

        <!-- CTA Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 mb-16">
          <Button variant="primary" size="lg" @click="router.push('/register')" class="shadow-sm">
            Get Started Free — No Card Needed
          </Button>
          <Button variant="outline" size="lg" @click="router.push('/login')">
            Explore Demo Experience →
          </Button>
        </div>

        <!-- Metric Proof Points -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl w-full pt-8 border-t border-border/80">
          <div class="p-4 rounded-xl bg-canvas-raised border border-border shadow-xs">
            <div class="font-display font-bold text-[1.8rem] text-primary">12,000+</div>
            <div class="text-[0.78rem] font-data text-ink-muted mt-0.5 uppercase tracking-wider">Active Members</div>
          </div>
          <div class="p-4 rounded-xl bg-canvas-raised border border-border shadow-xs">
            <div class="font-display font-bold text-[1.8rem] text-primary">&lt;15ms</div>
            <div class="text-[0.78rem] font-data text-ink-muted mt-0.5 uppercase tracking-wider">Meal Swap Solver</div>
          </div>
          <div class="p-4 rounded-xl bg-canvas-raised border border-border shadow-xs">
            <div class="font-display font-bold text-[1.8rem] text-primary">10-Min</div>
            <div class="text-[0.78rem] font-data text-ink-muted mt-0.5 uppercase tracking-wider">Cart Delivery Sync</div>
          </div>
          <div class="p-4 rounded-xl bg-canvas-raised border border-border shadow-xs">
            <div class="font-display font-bold text-[1.8rem] text-primary">100%</div>
            <div class="text-[0.78rem] font-data text-ink-muted mt-0.5 uppercase tracking-wider">ICMR-NIN IFCT Aligned</div>
          </div>
        </div>

        <!-- ── Live Application Interface Preview Card ────────────── -->
        <div class="mt-16 w-full max-w-5xl rounded-2xl bg-canvas-raised border border-border shadow-card overflow-hidden text-left">
          
          <!-- Mock Browser / OS Header -->
          <div class="px-5 py-3.5 bg-canvas border-b border-border flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-danger/60" />
              <div class="w-3 h-3 rounded-full bg-warning/60" />
              <div class="w-3 h-3 rounded-full bg-success/60" />
            </div>
            <div class="px-4 py-1 rounded-md bg-canvas-raised border border-border text-[0.72rem] font-data text-ink-muted">
              https://app.nutriplan.local/plan
            </div>
            <div class="w-12" />
          </div>

          <!-- Inside Interactive UI Preview -->
          <div class="p-6 md:p-8 bg-canvas">
            <div class="grid md:grid-cols-3 gap-6">
              
              <!-- Left Col: Macro Dashboard & Palate Banner -->
              <div class="md:col-span-2 space-y-5">
                
                <!-- Regional Palate Banner -->
                <div class="bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20 rounded-xl p-4 flex items-center justify-between">
                  <div>
                    <span class="text-[0.7rem] font-data font-bold text-primary uppercase tracking-wider">7-Day Palate Tour • Active</span>
                    <h3 class="font-display font-bold text-ink text-[1.1rem]">Andhra &amp; Telangana Heritage</h3>
                    <p class="font-body text-[0.82rem] text-ink-muted">High-protein lentils, gongura &amp; sun-dried spices • 1,847 kcal</p>
                  </div>
                  <span class="px-3 py-1 bg-primary text-white rounded-lg text-xs font-bold shrink-0">
                    Day 1 of 7
                  </span>
                </div>

                <!-- Daily Macro Card -->
                <div class="bg-canvas-raised border border-border rounded-xl p-5 shadow-xs flex items-center justify-between">
                  <div>
                    <div class="text-[0.75rem] font-data text-ink-muted uppercase tracking-wider">Daily Target (ICMR-NIN)</div>
                    <div class="font-display font-bold text-[1.6rem] text-ink">
                      1,800 <span class="text-[0.95rem] font-normal text-ink-muted">kcal</span>
                    </div>
                    <div class="flex gap-2 mt-2">
                      <span class="px-2 py-0.5 rounded-full text-[0.7rem] font-bold bg-primary-soft text-primary">778mg Calcium</span>
                      <span class="px-2 py-0.5 rounded-full text-[0.7rem] font-bold bg-amber-500/15 text-amber-700">19mg Iron</span>
                      <span class="px-2 py-0.5 rounded-full text-[0.7rem] font-bold bg-teal-500/15 text-teal-700">46g Fiber</span>
                    </div>
                  </div>
                  <MacroRing :totalKcal="1240" :targetKcal="1800" />
                </div>

                <!-- Sample Meal Items -->
                <div class="space-y-3">
                  <div class="bg-canvas-raised border border-border rounded-xl p-4 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-lg bg-primary-soft flex items-center justify-center text-primary font-bold text-sm">
                        <Icon name="plan" :size="18" />
                      </div>
                      <div>
                        <div class="font-display font-bold text-ink text-[0.92rem]">Pesarattu with Ginger Allam Chutney</div>
                        <div class="text-[0.78rem] font-data text-ink-muted">Breakfast • 420 kcal • P 18g • C 52g • F 8g</div>
                      </div>
                    </div>
                    <span class="px-2.5 py-1 rounded-md text-[0.72rem] font-bold bg-success-soft text-success">
                      ✓ Logged
                    </span>
                  </div>

                  <div class="bg-canvas-raised border border-border rounded-xl p-4 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-lg bg-secondary-soft flex items-center justify-center text-ink font-bold text-sm">
                        <Icon name="diary" :size="18" />
                      </div>
                      <div>
                        <div class="font-display font-bold text-ink text-[0.92rem]">Hyderabadi Khatti Dal &amp; Brown Rice</div>
                        <div class="text-[0.78rem] font-data text-ink-muted">Lunch • 580 kcal • P 24g • C 78g • F 12g</div>
                      </div>
                    </div>
                    <span class="px-2.5 py-1 rounded-md text-[0.72rem] font-semibold border border-border text-ink-muted">
                      Scheduled
                    </span>
                  </div>
                </div>

              </div>

              <!-- Right Col: 1-Click Quick Commerce & Wearable Card -->
              <div class="space-y-5">
                
                <!-- Quick Commerce Sync -->
                <div class="bg-canvas-raised border border-border rounded-xl p-5 shadow-xs">
                  <div class="flex items-center gap-2 mb-3">
                    <Icon name="grocery" :size="18" class="text-primary" />
                    <h4 class="font-display font-bold text-ink text-[0.95rem]">1-Click Cart Sync</h4>
                  </div>
                  <p class="text-[0.8rem] text-ink-muted mb-4">
                    4 missing ingredients for today's plan ready to order in 10 mins:
                  </p>
                  <div class="space-y-2 mb-4 text-[0.8rem] font-data">
                    <div class="flex justify-between py-1 border-b border-border/50">
                      <span>Whole Moong Dal</span>
                      <span class="text-ink-muted">500g</span>
                    </div>
                    <div class="flex justify-between py-1 border-b border-border/50">
                      <span>Fresh Curry Leaves</span>
                      <span class="text-ink-muted">1 bunch</span>
                    </div>
                    <div class="flex justify-between py-1">
                      <span>Fresh Ginger &amp; Tamarind</span>
                      <span class="text-ink-muted">100g</span>
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <button class="py-2 px-3 rounded-lg bg-[#8E24AA]/10 hover:bg-[#8E24AA]/20 text-[#8E24AA] font-bold text-xs border border-[#8E24AA]/30 transition-colors">
                      Zepto 10m
                    </button>
                    <button class="py-2 px-3 rounded-lg bg-[#F4C430]/20 hover:bg-[#F4C430]/30 text-amber-900 font-bold text-xs border border-amber-400/40 transition-colors">
                      Blinkit
                    </button>
                  </div>
                </div>

                <!-- Wearable CGM Telemetry -->
                <div class="bg-canvas-raised border border-border rounded-xl p-5 shadow-xs">
                  <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                      <Icon name="wearable" :size="18" class="text-primary" />
                      <h4 class="font-display font-bold text-ink text-[0.95rem]">Wearable Sync</h4>
                    </div>
                    <span class="w-2 h-2 rounded-full bg-success animate-pulse" />
                  </div>
                  <div class="grid grid-cols-2 gap-3 text-center">
                    <div class="p-2.5 rounded-lg bg-canvas border border-border">
                      <div class="font-display font-bold text-[1.1rem] text-ink">8,420</div>
                      <div class="text-[0.68rem] font-data text-ink-muted uppercase">Steps Synced</div>
                    </div>
                    <div class="p-2.5 rounded-lg bg-canvas border border-border">
                      <div class="font-display font-bold text-[1.1rem] text-primary">+220</div>
                      <div class="text-[0.68rem] font-data text-ink-muted uppercase">Kcal Calibrated</div>
                    </div>
                  </div>
                </div>

              </div>

            </div>
          </div>
        </div>

      </div>
    </section>


    <!-- ═══════════════════════════════════════════════════════
         7-DAY PALATE TOUR SPOTLIGHT
    ═══════════════════════════════════════════════════════ -->
    <section id="palate-tour" class="py-24 px-6 max-w-7xl mx-auto border-t border-border">
      <div class="text-center mb-16">
        <div class="inline-block text-[0.75rem] font-data font-bold uppercase tracking-[0.2em] text-primary mb-3">
          Culinary Diversity
        </div>
        <h2 class="font-display font-bold text-[2.2rem] md:text-[3rem] text-ink leading-tight">
          Automated 7-Day Regional <span class="text-primary italic">Palate Tour</span>
        </h2>
        <p class="font-body text-ink-muted text-[1.05rem] max-w-2xl mx-auto mt-3">
          Never get bored of healthy eating. Our AI dynamically rotates distinct culinary cultures across India Mon–Sun while adhering to strict ICMR-NIN macro &amp; calorie limits.
        </p>
      </div>

      <div class="grid sm:grid-cols-2 lg:grid-cols-7 gap-3">
        <div
          v-for="d in tourDays"
          :key="d.day"
          class="p-4 rounded-xl bg-canvas-raised border border-border shadow-xs hover:border-primary hover:-translate-y-1 transition-all flex flex-col justify-between"
        >
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="font-data font-bold text-[0.75rem] text-primary">{{ d.day }}</span>
              <span class="text-[0.7rem] font-data text-ink-muted">{{ d.kcal }} kcal</span>
            </div>
            <h4 class="font-display font-bold text-[0.95rem] text-ink mb-1">{{ d.region }}</h4>
            <p class="text-[0.78rem] text-ink-muted leading-snug">{{ d.theme }}</p>
          </div>
          <div class="mt-4 pt-2 border-t border-border/50 text-[0.7rem] font-data text-primary font-semibold">
            ✓ 4 Meals Solved
          </div>
        </div>
      </div>
    </section>


    <!-- ═══════════════════════════════════════════════════════
         CORE FEATURES GRID
    ═══════════════════════════════════════════════════════ -->
    <section id="features" class="py-24 px-6 bg-canvas-raised border-y border-border">
      <div class="max-w-7xl mx-auto">
        <div class="text-center mb-16">
          <div class="inline-block text-[0.75rem] font-data font-bold uppercase tracking-[0.2em] text-primary mb-3">
            Platform Capabilities
          </div>
          <h2 class="font-display font-bold text-[2.2rem] md:text-[3rem] text-ink leading-tight">
            One Platform. Complete <span class="text-primary italic">Nutritional Intelligence</span>.
          </h2>
          <p class="font-body text-ink-muted text-[1.05rem] max-w-xl mx-auto mt-3">
            From algorithmic meal planning to certified clinical video consultations.
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="f in features"
            :key="f.title"
            class="p-7 rounded-2xl bg-canvas border border-border shadow-xs hover:border-primary/50 hover:shadow-card hover:-translate-y-1 transition-all"
          >
            <div class="w-12 h-12 rounded-xl bg-primary-soft flex items-center justify-center text-primary mb-5">
              <Icon :name="f.icon" :size="22" />
            </div>
            <h3 class="font-display font-bold text-[1.15rem] text-ink mb-2">{{ f.title }}</h3>
            <p class="font-body text-[0.88rem] text-ink-muted leading-relaxed">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>


    <!-- ═══════════════════════════════════════════════════════
         HOW IT WORKS
    ═══════════════════════════════════════════════════════ -->
    <section id="how-it-works" class="py-24 px-6 max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <div class="inline-block text-[0.75rem] font-data font-bold uppercase tracking-[0.2em] text-primary mb-3">
          Frictionless Setup
        </div>
        <h2 class="font-display font-bold text-[2.2rem] md:text-[3rem] text-ink leading-tight">
          Up and running in <span class="text-primary italic">3 minutes</span>
        </h2>
      </div>

      <div class="grid md:grid-cols-3 gap-8">
        <div class="p-8 rounded-2xl bg-canvas-raised border border-border shadow-card text-center relative">
          <div class="w-12 h-12 rounded-full bg-primary-soft text-primary font-display font-bold text-[1.3rem] flex items-center justify-center mx-auto mb-5">
            01
          </div>
          <h3 class="font-display font-bold text-[1.15rem] text-ink mb-2">Set Your Health Goals</h3>
          <p class="font-body text-[0.88rem] text-ink-muted leading-relaxed">
            Select your caloric target, dietary restriction (Veg/Jain/Non-veg), and favorite regional cuisines.
          </p>
        </div>

        <div class="p-8 rounded-2xl bg-canvas-raised border border-border shadow-card text-center relative">
          <div class="w-12 h-12 rounded-full bg-secondary-soft text-ink font-display font-bold text-[1.3rem] flex items-center justify-center mx-auto mb-5">
            02
          </div>
          <h3 class="font-display font-bold text-[1.15rem] text-ink mb-2">Receive 7-Day Plan</h3>
          <p class="font-body text-[0.88rem] text-ink-muted leading-relaxed">
            Deterministic solver constructs an authentic regional weekly plan with exact macro &amp; micronutrient compliance.
          </p>
        </div>

        <div class="p-8 rounded-2xl bg-canvas-raised border border-border shadow-card text-center relative">
          <div class="w-12 h-12 rounded-full bg-primary-soft text-primary font-display font-bold text-[1.3rem] flex items-center justify-center mx-auto mb-5">
            03
          </div>
          <h3 class="font-display font-bold text-[1.15rem] text-ink mb-2">Track &amp; Order in 1-Click</h3>
          <p class="font-body text-[0.88rem] text-ink-muted leading-relaxed">
            Log meals in seconds, push grocery items to Zepto/Blinkit, or book video reviews with verified dietitians.
          </p>
        </div>
      </div>
    </section>


    <!-- ═══════════════════════════════════════════════════════
         TESTIMONIALS
    ═══════════════════════════════════════════════════════ -->
    <section class="py-24 px-6 bg-canvas-raised border-y border-border">
      <div class="max-w-7xl mx-auto">
        <div class="text-center mb-16">
          <div class="inline-block text-[0.75rem] font-data font-bold uppercase tracking-[0.2em] text-primary mb-3">
            Real Stories
          </div>
          <h2 class="font-display font-bold text-[2.2rem] md:text-[3rem] text-ink leading-tight">
            Validated by Patients &amp; <span class="text-primary italic">Dietitians</span>
          </h2>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
          <div
            v-for="t in testimonials"
            :key="t.name"
            class="p-8 rounded-2xl bg-canvas border border-border shadow-xs flex flex-col justify-between"
          >
            <p class="font-body text-[0.92rem] text-ink-muted leading-relaxed italic mb-6">
              "{{ t.quote }}"
            </p>
            <div class="flex items-center gap-3 pt-4 border-t border-border/60">
              <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-display font-bold text-sm">
                {{ t.avatar }}
              </div>
              <div>
                <div class="font-display font-bold text-[0.92rem] text-ink">{{ t.name }}</div>
                <div class="text-[0.75rem] font-data text-ink-muted">{{ t.role }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>


    <!-- ═══════════════════════════════════════════════════════
         PRICING SECTION
    ═══════════════════════════════════════════════════════ -->
    <section id="pricing" class="py-24 px-6 max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <div class="inline-block text-[0.75rem] font-data font-bold uppercase tracking-[0.2em] text-primary mb-3">
          Transparent Pricing
        </div>
        <h2 class="font-display font-bold text-[2.2rem] md:text-[3rem] text-ink leading-tight">
          Simple, Transparent <span class="text-primary italic">Memberships</span>
        </h2>
        <p class="font-body text-ink-muted text-[1.05rem] max-w-lg mx-auto mt-3">
          Cancel anytime. 14-day free trial on all paid plans.
        </p>
      </div>

      <div class="grid md:grid-cols-3 gap-6">
        <div
          v-for="p in plans"
          :key="p.name"
          :class="[
            'p-8 rounded-2xl bg-canvas-raised border flex flex-col justify-between transition-all relative',
            p.highlight
              ? 'border-primary shadow-card ring-2 ring-primary/20 scale-[1.03]'
              : 'border-border shadow-xs'
          ]"
        >
          <div v-if="p.highlight" class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-primary text-white text-[0.68rem] font-data font-bold tracking-wider uppercase">
            {{ p.badge }}
          </div>

          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-display font-bold text-[1.2rem] text-ink">{{ p.name }}</h3>
              <span v-if="!p.highlight" class="text-[0.68rem] font-data font-bold px-2 py-0.5 rounded bg-canvas text-ink-muted border border-border">
                {{ p.badge }}
              </span>
            </div>

            <div class="flex items-baseline gap-1.5 mb-6">
              <span class="font-display font-bold text-[2.5rem] text-ink">{{ p.price }}</span>
              <span class="font-body text-[0.85rem] text-ink-muted">{{ p.period }}</span>
            </div>

            <ul class="space-y-3 mb-8">
              <li v-for="f in p.features" :key="f" class="flex items-start gap-2.5 text-[0.85rem] text-ink-muted">
                <span class="text-primary font-bold mt-0.5">✓</span>
                <span>{{ f }}</span>
              </li>
            </ul>
          </div>

          <Button :variant="p.variant" class="w-full" @click="router.push('/register')">
            {{ p.cta }}
          </Button>
        </div>
      </div>
    </section>


    <!-- ═══════════════════════════════════════════════════════
         FAQ ACCORDION
    ═══════════════════════════════════════════════════════ -->
    <section id="faq" class="py-24 px-6 bg-canvas-raised border-t border-border">
      <div class="max-w-3xl mx-auto">
        <div class="text-center mb-16">
          <div class="inline-block text-[0.75rem] font-data font-bold uppercase tracking-[0.2em] text-primary mb-3">
            Common Questions
          </div>
          <h2 class="font-display font-bold text-[2.2rem] md:text-[3rem] text-ink leading-tight">
            Frequently Asked <span class="text-primary italic">Questions</span>
          </h2>
        </div>

        <div class="space-y-3">
          <div
            v-for="(f, i) in faqs"
            :key="i"
            class="rounded-xl border border-border overflow-hidden bg-canvas transition-all"
          >
            <button
              class="w-full text-left px-6 py-5 flex items-center justify-between gap-4 cursor-pointer"
              @click="toggleFaq(i)"
            >
              <span class="font-display font-bold text-[1rem] text-ink">{{ f.q }}</span>
              <span class="text-primary font-bold text-lg transition-transform" :class="openFaq === i ? 'rotate-45' : ''">
                +
              </span>
            </button>
            <div v-if="openFaq === i" class="px-6 pb-5 pt-1 border-t border-border/50 text-[0.9rem] text-ink-muted leading-relaxed font-body">
              {{ f.a }}
            </div>
          </div>
        </div>
      </div>
    </section>


    <!-- ═══════════════════════════════════════════════════════
         BOTTOM CTA BANNER
    ═══════════════════════════════════════════════════════ -->
    <section class="py-24 px-6 max-w-5xl mx-auto text-center">
      <div class="p-12 md:p-16 rounded-3xl bg-primary text-white shadow-card relative overflow-hidden">
        <div class="relative z-10 max-w-2xl mx-auto">
          <h2 class="font-display font-bold text-[2.4rem] md:text-[3.2rem] leading-tight mb-4">
            Start Your Healthiest Year Today.
          </h2>
          <p class="font-body text-white/80 text-[1.05rem] leading-relaxed mb-8">
            Join thousands of users optimizing their daily nutrition with ICMR-NIN science, regional Indian palate tours, and 1-click grocery ordering.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <Button variant="secondary" size="lg" @click="router.push('/register')" class="shadow-sm">
              Create Free Account →
            </Button>
            <Button variant="outline" size="lg" @click="router.push('/login')" class="border-white/40 text-white hover:bg-white/10 hover:text-white">
              Sign In to Account
            </Button>
          </div>
          <p class="text-[0.75rem] text-white/60 mt-6 font-data">
            Free forever tier • No credit card required • Instant onboarding
          </p>
        </div>
      </div>
    </section>

  </div>
</template>

