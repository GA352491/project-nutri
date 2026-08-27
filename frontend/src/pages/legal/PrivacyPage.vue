<script setup lang="ts">
const lastUpdated = 'August 27, 2026'
</script>

<template>
  <div class="max-w-4xl mx-auto px-6 py-20">
    <!-- Header -->
    <div class="mb-12 border-b border-border pb-8">
      <div class="inline-block text-[0.75rem] font-data font-bold uppercase tracking-[0.2em] text-primary mb-3">Legal & Trust Documentation</div>
      <h1 class="font-display font-bold text-[2.4rem] md:text-[3rem] text-ink leading-tight mb-3">
        Privacy Policy
      </h1>
      <p class="text-[0.88rem] text-ink-muted">
        Last updated: {{ lastUpdated }} · Grounded in clinical data protection for NutriPlan AI members
      </p>
    </div>

    <!-- Content -->
    <div class="space-y-8 text-ink leading-relaxed text-[0.95rem]">
      <section class="space-y-3">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">1. Introduction</h2>
        <p class="text-ink-muted">
          NutriPlan AI ("we", "our", or "us") is dedicated to protecting your personal information and your right to privacy. This Privacy Policy governs the processing of data collected through our web applications, mobile services, and API endpoints connected to our precision nutrition engine.
        </p>
      </section>

      <section class="space-y-3">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">2. Information We Collect</h2>
        <p class="text-ink-muted">We collect personal information that you voluntarily provide to us when registering, participating in activities, or requesting nutrition guidance:</p>
        <ul class="list-disc pl-6 space-y-2 text-ink-muted">
          <li><strong class="text-ink">Account Information:</strong> Name, email address, password hash, demographic profile (age, gender, height, current weight, target weight).</li>
          <li><strong class="text-ink">Nutritional &amp; Health Data:</strong> Dietary preferences (vegetarian, vegan, Jain), allergies, medical conditions, caloric targets, and food diary logs.</li>
          <li><strong class="text-ink">Wearable &amp; Sensor Telemetry:</strong> Step counts, active calories burned, resting heart rate, and sleep duration synced via Apple HealthKit, Google Fit, or wearable APIs.</li>
          <li><strong class="text-ink">Payment Data:</strong> Transaction records processed securely by our PCI-DSS compliant partner, Stripe. We never store raw credit card numbers.</li>
        </ul>
      </section>

      <section class="space-y-3">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">3. How We Use Your Information</h2>
        <p class="text-ink-muted">We use personal information collected via our services for purposes including:</p>
        <ul class="list-disc pl-6 space-y-2 text-ink-muted">
          <li>Generating bespoke AI meal recommendations and dynamic macro adjustments.</li>
          <li>Facilitating secure consultations and real-time messaging with certified nutrition experts.</li>
          <li>Providing automated grocery lists and Quick-Commerce cart synchronization.</li>
          <li>Model evaluation and clinical precision tracking with zero personally identifiable disclosures.</li>
        </ul>
      </section>

      <section class="space-y-3">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">4. GDPR &amp; CCPA Compliance (Your Rights)</h2>
        <p class="text-ink-muted">
          Regardless of your jurisdiction, NutriPlan AI guarantees the following data protection rights:
        </p>
        <div class="grid sm:grid-cols-2 gap-4 pt-2">
          <div class="p-5 rounded-xl bg-canvas-raised border border-border shadow-xs">
            <h3 class="font-display font-bold text-ink mb-1">Right to Access &amp; Export</h3>
            <p class="text-[0.85rem] text-ink-muted">Request a full machine-readable JSON copy of all your health metrics and meal logs.</p>
          </div>
          <div class="p-5 rounded-xl bg-canvas-raised border border-border shadow-xs">
            <h3 class="font-display font-bold text-ink mb-1">Right to Erasure (Be Forgotten)</h3>
            <p class="text-[0.85rem] text-ink-muted">Instantly delete your entire profile and historical biometric data permanently from our servers.</p>
          </div>
        </div>
      </section>

      <section class="space-y-3">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">5. Data Security &amp; Storage</h2>
        <p class="text-ink-muted">
          All biometric and dietary records are stored using AES-256 encryption at rest and TLS 1.3 encryption in transit. We enforce role-based access control (RBAC) preventing unauthorized access even among internal staff.
        </p>
      </section>

      <section class="space-y-3">
        <h2 class="font-display font-bold text-[1.3rem] text-ink">6. Contact Our Data Protection Officer</h2>
        <p class="text-ink-muted">
          If you have questions or comments about this policy or wish to exercise your privacy rights, contact our Data Protection Officer at:
        </p>
        <div class="p-4 rounded-xl bg-primary-soft border border-primary/20 text-primary font-data text-[0.88rem]">
          Email: privacy@nutriplan.local · Security Hotline: +91 (80) 4567-8900
        </div>
      </section>
    </div>
  </div>
</template>

