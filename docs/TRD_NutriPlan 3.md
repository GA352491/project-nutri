# TRD — NutriPlan Architecture
Backend: Python (FastAPI) microservices · Web: Vue 3 · Mobile: Flutter (or React Native — see §1a) · All infra components open-source/self-hostable.

## 1a. Mobile stack decision: Flutter vs React Native
Both are fully open source; either is a legitimate choice over Capacitor for camera-heavy, on-device-inference work (food photo recognition benefits from tighter native camera/ML pipeline access than a WebView wrapper gives you).

| | Flutter | React Native |
|---|---|---|
| Language | Dart | JavaScript/TypeScript |
| Fit with your team | New language to learn | Reuses JS/TS skills your Vue web team already has |
| On-device ML | Good via `google_mlkit`/`tflite_flutter`, camera plugin is mature | Good via `react-native-vision-camera` + `react-native-fast-tflite`; very mature camera pipeline |
| Wearable SDK support | Solid (Health Connect/HealthKit plugins exist, slightly less first-party) | Solid, slightly larger ecosystem of community wearable packages |
| Performance for camera+ML | Excellent (compiled, no JS bridge) | Excellent with the new architecture (JSI, no bridge bottleneck) |
| **Recommendation** | **Pick Flutter if you want one consistent, compiled-performance codebase and don't mind Dart.** **Pick React Native if you want your web (Vue/JS) and mobile devs sharing more mental model/tooling (e.g., shared TypeScript types with the FastAPI OpenAPI client).** Either works — this doc assumes **Flutter** going forward since camera + on-device inference + wearable SDKs are all first-class there, but the service architecture below is frontend-agnostic and works unchanged with React Native. | |

## 1. Style
C4-style container architecture (same pattern as the reference diagram you shared): People → UI containers → API layer → domain microservices → data stores → external/partner systems, connected by labeled JSON/HTTPS, event-stream, and WebSocket flows. See `architecture_diagram.mermaid`.

## 2. Open-source stack choices
| Concern | Choice | Why |
|---|---|---|
| API framework | FastAPI (Python) | async, typed, matches your existing stack knowledge |
| Web frontend | Vue 3 + Vite + Pinia + TanStack Query | |
| Mobile | Flutter (open source, Google) — or React Native if you prefer JS parity with web | native camera + on-device ML performance, no WebView bridge |
| Wearable data | Health Connect (Android, OSS) + Apple HealthKit (iOS, free API) as the on-device aggregators; Fitbit Web API / Google Fit REST API / Garmin Health API as cloud sources | HealthKit/Health Connect are the standard, no-cost way to read steps/HR/calories-burned from *any* band the user already owns (Fitbit, Garmin, Apple Watch, Mi Band, etc.) without integrating each vendor separately |
| Auth/IdP | Keycloak | OSS, OAuth2/OIDC, roles for member/nutritionist/admin |
| Relational DB | PostgreSQL | plans, profiles, subscriptions, appointments |
| Document DB | MongoDB | recipe/food DB (flexible schema per cuisine) |
| Cache | Redis | pre-generated plan cache, session, rate limits |
| Vector DB | pgvector (in Postgres) or Qdrant | RAG for chatbot + recipe similarity |
| Search | Meilisearch or Typesense | recipe/food search |
| Messaging/eventing | RabbitMQ or Redis Streams (Kafka if scale demands) | plan-generation jobs, logging events, notifications |
| Object storage | MinIO | food photos, recipe images |
| Chat (member↔nutritionist) | Self-hosted via Socket.IO/Centrifugo (or Matrix if federation desired) | |
| Video appointments | Jitsi Meet (self-hosted) | fully open source video, avoids paid video SaaS |
| LLM (generative meal plans + chatbot) | Self-hosted via Ollama/vLLM serving an open-weight model (e.g., Llama 3 or Mistral class), swappable | keeps "no paid services" constraint; Bedrock/Claude/GPT can be swapped in later exactly like the reference diagram's "AI Models" box does |
| Food image recognition | Open food-recognition model (e.g., a Food-101/CLIP-based classifier) served via TorchServe/ONNX Runtime | |
| Nutrition reference data | USDA FoodData Central (free/public) for US, Indian Food Composition Tables (IFCT 2017, ICMR-NIN) for India | |
| Payments | **Flagged, not solved in v1** — genuine payment processing requires a licensed gateway (Stripe/Razorpay/PayPal etc.), none of which are open source. Recommendation: build the Payment Service against an abstract interface now (so it's swappable), and only wire a real provider when you're ready to go live/paid. Everything else in the platform stays open source. |
| Workflow orchestration | **Temporal** (self-hosted server, MIT license) | durable execution for multi-step flows: meal-plan generation (LLM call → nutrition validator → cache write), appointment reminders, wearable-driven TDEE→plan adjustment chain — each step retries/resumes on failure without hand-rolled Celery retry logic |
| CI | **Harness CI Community Edition (Drone)**, Apache 2.0 | fully open source, no restrictions |
| CD / GitOps | **ArgoCD**, Apache 2.0 | fully open source. Note: Harness CD Community Edition is free but *source-available* under the Polyform Shield license, not true OSS — ArgoCD avoids that asterisk |
| Container orchestration | Docker Compose (dev) → Kubernetes (prod), all self-hostable |
| Observability | Prometheus + Grafana + Loki (OSS equivalents of the Dynatrace box in your reference) |

## 3. Microservices

1. **API Gateway** — Kong (OSS) or FastAPI-based gateway; auth passthrough to Keycloak, rate limiting, routing.
2. **Auth Service** — wraps Keycloak; issues/validates JWT (mirrors "Validate JWT Token" in your reference diagram).
3. **Profile & Onboarding Service** — stores demographics, goals, allergies, pantry inventory.
4. **Compliance/Reference-Data Service** — country-pluggable RDA/DRI/FSSAI/USDA rule engine; every other service asks *this* service "what are today's targets for this user."
5. **Recipe & Food Database Service** — curated recipes/foods, nutrient values, tagging (cuisine, diet type, allergens).
6. **Meal Plan Generation Service** — the core engine (curated + generative modes, detailed in §5).
7. **Grocery List Service** — diffs plan ingredients against pantry, produces shoppable list.
8. **Food Recognition Service** — image → food label → quantity estimate → macro/micro payload.
8a. **Activity & Wearable Integration Service** — pulls steps/active-energy/heart-rate/workouts from Health Connect, HealthKit, Fitbit/Garmin/Google Fit APIs; normalizes into a common "energy expenditure" event, detailed in §9.
9. **Nutrition Logging Service (Diary)** — per-meal/day logs, rollups, adherence vs target.
10. **Nutritionist Directory & Matching Service** — search/filter nutritionists.
11. **Chat/Messaging Service** — member↔nutritionist and AI-chatbot conversation transport.
12. **AI Chatbot Service** — RAG over the member's own profile/log/plan + nutrition knowledge base, backed by the self-hosted LLM.
13. **Appointment/Scheduling Service** — booking, reminders, calendar holds.
14. **Video Consultation Service** — Jitsi room provisioning/tokens.
15. **Subscription Service** — plan tiers, entitlements (chat quota, delivery eligibility, plan horizon).
16. **Payment Service** — abstracted interface (see stack table).
17. **Delivery/Logistics Service** — region-gated, talks to regional delivery partner APIs.
18. **Notification Service** — push/email/SMS via OSS options (e.g., ntfy, self-hosted SMTP).
19. **Analytics/Reporting Service** — adherence metrics, business metrics.
20. **Admin/CMS Service** — ops manage food DB, compliance rules, nutritionist onboarding.

Each service owns its own schema; cross-service reads go through APIs or async events, never direct DB access — same separation of concerns as the DevCon reference diagram (Automation API / Metadata DB / Cache / Event Store all kept distinct).

## 4. Key data flows (mirrors the reference diagram's event-driven style)
- **Onboarding → Plan**: Profile Service emits `profile.updated` → Meal Plan Service consumes → regenerates only the affected days → writes to Postgres → invalidates Redis cache.
- **Photo log**: Mobile → Food Recognition Service (sync, low-latency inference) → user confirms → Logging Service writes → emits `meal.logged` → Analytics + Plan Service (adjusts remaining-day targets) consume asynchronously.
- **Chatbot**: Chat Service → AI Chatbot Service → pgvector/Qdrant retrieval (member's own data + nutrition KB) → LLM → streamed response (like the "Streamable HTTP" pattern in your reference).
- **Appointment**: Scheduling Service → Notification Service (reminders) → Video Service (room token at start time).

## 5. Meal Plan Generation — Curated vs Generative
- **Curated**: constraint-satisfaction/query over Recipe DB (filter by diet/allergen/cuisine/budget, optimize to hit macro/micro targets within tolerance) — deterministic, fast, cheap.
- **Generative**: LLM proposes a recipe/meal; a **separate deterministic nutrition validator** (not the LLM) computes actual macros/micros from ingredient database and rejects/asks-for-revision if out of tolerance, before it's ever shown to the user. This avoids the classic failure mode of trusting an LLM's own nutrition math.
- User can toggle which mode a given plan/week uses, or mix (e.g., curated on weekdays, generative on weekends).

## 6. Plan generation cadence — how to keep latency low
This is the key engineering decision for subscription UX:

- **Don't generate the whole subscription (e.g., a full month) up front.** Generate a **rolling 7-day window**, pre-computed **2–3 days ahead of when it's needed**, as a background job (Celery/RQ + beat scheduler), not on-demand at page load.
- **Serve reads from Redis cache**, not from a live generation call — the UI always reads a pre-baked plan; generation is decoupled from viewing.
- **Regenerate only on triggers, not on a timer alone**: profile change, allergy change, pantry update, or the user explicitly requesting "swap this meal" — each trigger regenerates just the affected day(s)/meal(s), not the whole window.
- **Nightly batch job** extends the rolling window by one more day for every active subscriber (so there's always ~7 days ready), run in off-peak hours to smooth load.
- **On-demand single-meal swap** is the one truly synchronous, user-facing generation path — keep it fast by scoping it to one meal against already-computed remaining-day targets, not recomputing the whole day.
- Net effect: whether someone is on a 1-month or 6-month subscription, the *live* compute unit is always "one day, occasionally one meal" — subscription length only affects how many days get queued, not response latency.

## 9. Fitness band / wearable integration → dynamic macro/micro adjustment

**Sources**: Apple HealthKit (iOS), Health Connect (Android — the modern successor to Google Fit's old API, now the standard aggregator that Fitbit, Garmin, Samsung Health, etc. all write into), plus direct Fitbit Web API / Garmin Health API / Google Fit REST API for users who want cloud-level sync without opening the phone app. This one integration point covers "any fitness band," matching the same "sync with any device" pattern that MyFitnessPal, Cronometer, and HealthifyMe all lean on for wearable support — none of them integrate every band individually.

**Data pulled**: active energy expenditure (calories burned), step count, workout sessions (type/duration/intensity), resting heart rate (as an adherence/recovery signal, not diagnostic).

**Flow**:
1. Activity & Wearable Integration Service polls/receives a push (`activity.synced` event) once new data lands in HealthKit/Health Connect (near-real-time on most platforms).
2. It computes an updated **Total Daily Energy Expenditure (TDEE)** delta versus the sedentary baseline TDEE that Meal Plan Generation used when it built the day's plan.
3. If the delta crosses a meaningful threshold (e.g., >10–15% swing, configurable), it emits `tdee.updated`.
4. Meal Plan Generation Service consumes this and adjusts **only the remaining, not-yet-eaten meals for that day** (never rewrites meals already logged/eaten) — e.g., a harder-than-usual workout nudges dinner's carbs/protein up within the day's remaining micronutrient budget; a rest day trims it back down.
5. The Compliance/Reference-Data Service's per-country RDA floor is always respected — activity can raise a day's targets but never push a plan below the minimum recommended micronutrient intake.
6. This reuses the same "regenerate only what's affected" cadence from §6 — activity-based adjustment is just another *trigger*, not a new generation path, so it doesn't add latency risk.

**UX**: shown as a simple "Today's target adjusted +180 kcal / +12g protein based on your workout" banner, with the option for the user to accept or keep the original plan — some users specifically don't want their plan to move around, so this is opt-in per profile, not forced.

## 7. Design System (Web + Mobile, shared)
- **Component base**: PrimeVue or shadcn-vue (both OSS, Vue-native) themed together for web and Ionic Vue mobile so components look/behave consistently.
- **Tokens**: semantic color roles (e.g., `--color-success` for "on target," `--color-warning` for "over budget," `--color-info` for chat/AI) rather than raw hex in components; a calm, clinical-but-warm palette (greens/neutrals, one accent for CTAs) fits a health app better than saturated brand colors.
- **Typography**: one readable sans (e.g., Inter/Public Sans, both open license) at accessible sizes; numbers (macros) get a tabular-figure variant for scannable diary tables.
- **Data viz**: macro/micro rings and daily bars as reusable chart components (open-source charting, e.g., Chart.js/ECharts).
- **Accessibility**: WCAG AA minimum — this is a health app, contrast and screen-reader labeling for nutrient values matter.
- **Patterns to reuse across web/mobile**: meal card, macro ring, plan-day timeline, chat bubble, appointment slot picker — build once as a shared component library, consumed by both Vue web and Ionic Vue mobile.

## 8. Country-compliance pluggability
Compliance/Reference-Data Service loads a ruleset module per country (`rules/in.py`, `rules/us.py`, …) exposing a common interface: `get_targets(profile) -> {macros, micros}` and `validate_label(meal) -> ok/violations`. Adding a country is adding a module, not touching other services — same extensibility principle as the reference diagram's pluggable "AI Models" box.
