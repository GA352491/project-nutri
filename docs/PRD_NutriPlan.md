# PRD — NutriPlan (working name)
AI-driven, subscription-based nutrition platform (Web + Mobile)

## 1. Vision
Give a user a single place to get a compliant, personalized meal plan, log what they eat via photo, talk to a nutritionist, and get groceries sorted — starting in India and the US, open-source stack only.

## 2. Users
- **End user / member** — wants a meal plan that fits their body, budget, pantry, and diet rules.
- **Nutritionist / dietician (partner)** — reviews/approves AI plans, chats, takes appointments.
- **Admin/Ops** — manages food DB, compliance rules, subscriptions, delivery partners.

## 3. Core Features

### 3.1 Onboarding & Profile
- Demographics, height/weight, activity level, goal (loss/gain/maintain/medical e.g. diabetes, PCOS, renal)
- Allergies, cuisine preference, diet type (veg/vegan/jain/keto/halal etc.), budget, region, existing pantry items
- Country selected → drives which compliance/RDA ruleset applies (FSSAI/ICMR-NIN for India, USDA/FDA DRI for US)

### 3.2 Meal Plan Generation (two modes, user-selectable per plan)
1. **Curated mode** — assembled from a vetted recipe/food database, filtered by diet rules + macro/micro targets.
2. **Generative mode** — LLM proposes new recipes constrained by the same nutrient targets, validated programmatically before shown (nutrition math is never left to the LLM alone — see TRD).
- Both modes respect: daily calorie/macro budget, micronutrient targets, allergies, cuisine, pantry items on hand, budget ceiling, and country compliance rules.
- Output: day-wise plan (breakfast/lunch/snacks/dinner), each meal tagged with macros+micros.

### 3.3 Grocery List
- Auto-derived from the week's plan minus pantry items already logged as available.
- Editable, exportable, groupable by store section.

### 3.4 Food Logging via Photo (mobile)
- Camera capture → food identification → macro/micro estimate → user confirms/edits quantity → logs to the correct meal slot (breakfast/lunch/snack/dinner) → rolls up into daily totals vs target.

### 3.5 Nutrition Diary
- Per-meal and per-day macro/micro totals vs targets, trend view over the subscription period.

### 3.6 Nutritionist Connect
- Directory/matching by specialty, language, region
- In-app chat (text) with a nutritionist
- Appointment booking + video consultation
- Nutritionist can view/edit the member's AI-generated plan

### 3.7 AI Chatbot
- General nutrition Q&A, grounded in the member's own profile/logs (RAG), clearly distinguished from medical advice, with escalation to a human nutritionist for anything clinical.

### 3.8 Subscriptions & Payments
- Tiered subscription (e.g., Basic/Plus/Premium) controlling: plan length pre-generated, nutritionist chat/appointment quota, delivery eligibility.
- Payment gateway integration point (see TRD note on open-source constraint).

### 3.9 Delivery (select regions only)
- Optional meal/grocery delivery fulfilled through regional partners; flagged per-region as available/unavailable.

## 4. Compliance
- India: FSSAI labeling/nutrition rules, ICMR-NIN RDA/EAR values, Ayush/dietician licensing awareness for nutritionist-facing features.
- US: FDA nutrition labeling rules, USDA Dietary Reference Intakes (DRI), HIPAA-awareness for anything touching health data if nutritionists give clinical advice.
- Country ruleset is a pluggable module so more countries can be added later without re-architecting.

## 5. Subscription-Driven Plan Cadence (see TRD §6 for engineering detail)
- Plan is **not** generated fully for the whole subscription in one shot. It's generated **rolling weekly**, pre-computed a few days ahead, and only touched intraday when the user's profile/pantry/log actually changes — this is what keeps read latency low no matter how long the subscription is.

## 6. Non-goals (v1)
- Not a medical diagnosis tool. Not a full EHR. Not handling insurance claims. No paid third-party SaaS dependencies (open-source self-hosted only, per constraint).

## 7. Success Metrics
- Plan-to-log adherence rate, weekly active logging %, nutritionist chat response SLA, plan regeneration latency (p95), subscription renewal rate.
