<script setup lang="ts">
const lastUpdated = 'August 27, 2026'
</script>

<template>
  <div class="max-w-4xl mx-auto px-6 py-20">
    <!-- Header -->
    <div class="mb-12 border-b border-border pb-8">
      <div class="inline-block text-[0.75rem] font-data font-bold uppercase tracking-[0.2em] text-primary mb-3">Legal Documentation</div>
      <h1 class="font-display font-bold text-[2.4rem] md:text-[3rem] text-ink leading-tight mb-3">
        Cookie Policy
      </h1>
      <p class="text-[0.88rem] text-ink-muted">
        Last updated: {{ lastUpdated }} · Learn how we use tracking &amp; authentication technologies
      </p>
    </div>

    <!-- Content -->
    <div class="space-y-8 text-ink leading-relaxed text-[0.95rem]">
      <section class="space-y-3">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">1. What are Cookies?</h2>
        <p class="text-ink-muted">
          Cookies are small text files placed on your computer or mobile device when you browse websites. They are widely used to make web applications function efficiently, preserve authentication sessions, and store user preferences.
        </p>
      </section>

      <section class="space-y-4">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">2. Categories of Cookies We Use</h2>
        
        <div class="space-y-3">
          <div class="p-5 rounded-xl bg-canvas-raised border border-border shadow-xs">
            <h3 class="font-display font-bold text-primary text-[1rem] mb-1">Essential / Strictly Necessary Cookies</h3>
            <p class="text-[0.85rem] text-ink-muted">
              Required for basic application functions such as user authentication tokens (JWT in localStorage/session cookies), secure payment processing via Stripe, and role-based routing. These cannot be disabled.
            </p>
          </div>

          <div class="p-5 rounded-xl bg-canvas-raised border border-border shadow-xs">
            <h3 class="font-display font-bold text-primary text-[1rem] mb-1">Preference &amp; Functionality Cookies</h3>
            <p class="text-[0.85rem] text-ink-muted">
              Used to remember your UI settings, including chosen cuisine preference, selected unit system (metric/imperial), and regional palate tour choices across browser restarts.
            </p>
          </div>

          <div class="p-5 rounded-xl bg-canvas-raised border border-border shadow-xs">
            <h3 class="font-display font-bold text-primary text-[1rem] mb-1">Performance &amp; Telemetry Cookies</h3>
            <p class="text-[0.85rem] text-ink-muted">
              Help us measure page load speed, identify broken client routes, and evaluate model response latencies without tracking individual identities across external sites.
            </p>
          </div>
        </div>
      </section>

      <section class="space-y-3">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">3. Managing and Disabling Cookies</h2>
        <p class="text-ink-muted">
          Most modern web browsers allow you to control cookies through browser settings. You can set your browser to refuse cookies or delete specific cookies. Note that disabling essential cookies will prevent you from signing in to your NutriPlan AI account.
        </p>
      </section>

      <section class="space-y-3">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">4. Updates to this Policy</h2>
        <p class="text-ink-muted">
          We may update our Cookie Policy periodically to reflect technological or regulatory advancements. Significant modifications will be communicated via in-app banners.
        </p>
      </section>
    </div>
  </div>
</template>

