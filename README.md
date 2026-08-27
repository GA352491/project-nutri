# 🥦 NutriPlan — Clinical-Grade Nutrition & Health Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue 3](https://img.shields.io/badge/Frontend-Vue_3_%2B_Vite-4FC08D.svg?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Temporal](https://img.shields.io/badge/Orchestration-Temporal_Durable_Workflows-000000.svg?logo=temporal&logoColor=white)](https://temporal.io/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_14-4169E1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB_8.3-47A248.svg?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Stripe](https://img.shields.io/badge/Payments-Stripe_Elements-635BFF.svg?logo=stripe&logoColor=white)](https://stripe.com/)
[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)](#)

NutriPlan is a clinical-grade, AI-driven personalized nutrition platform. It orchestrates automated meal planning with clinical guardrails (Diabetes, Keto, Renal, Cardiac), food diary tracking with macro aggregation, 10-minute grocery delivery integrations (Blinkit, Zepto, Instacart), telehealth appointments with certified clinical dietitians, and durable subscription lifecycles powered by **Temporal.io**.

---

## 🌟 Key Architecture & Capabilities

### 1. 🤖 AI Clinical Meal Planning & Guardrails
* Powered by **PydanticAI** and local LLMs (**Llama-3** via Ollama) with structured schema enforcement.
* Real-time physiological safety checks against clinical nutrition rules (glycemic index limits, sodium ceilings, macro ratio validations).

### 2. ⚡ Temporal Durable Execution Hub
Orchestrates long-running, fault-tolerant business workflows:
* `BookingWorkflow` — Telehealth appointment lifecycle, payment hold capture, nutritionist calendar reservation.
* `SubscriptionLifecycleWorkflow` — 14-day free trial schedules, automated dunning, plan tier upgrades/downgrades.
* `MealPlanGenerationWorkflow` — Asynchronous clinical generation, dietitian review triggers.
* `GroceryDeliveryWorkflow` — Cart synchronization & deep-link dispatch.
* `ReminderWorkflow` — Meal and consultation push notifications.

### 3. 💳 PCI-Safe Stripe Integration
* **SetupIntent Pre-Authorization**: 14-day zero-dollar free trials pre-authorized securely via the official Stripe iframe.
* **Stripe Connect**: Express accounts and automatic split payouts (80% expert / 20% platform) for dietitian consultations.
* **Ledger Database**: Idempotent webhook processing and local payment ledger in PostgreSQL.

### 4. 🗄️ Polyglot Database Persistence (Zero Mock Fallbacks)
* **PostgreSQL 14**: Dedicated schemas/databases for `nutriplan_auth`, `nutriplan_diary`, `nutriplan_grocery`, `nutriplan_subscriptions`, `nutriplan_meal_plan`, `nutriplan_appointments`, `nutriplan_payments`.
* **MongoDB Community 8.3**: Structured document storage for comprehensive health profiles and medical histories via Beanie ODM.

---

## 🏗️ Microservices Ecosystem Map

| Service | Port | Database | Primary Responsibility |
|---|---|---|---|
| **API Gateway** | `:8000` | — | Reverse proxy, routing, and aggregated OpenAPI docs |
| **Auth Service** | `:8001` | PostgreSQL (`nutriplan_auth`) | Argon2/bcrypt password hashing, JWT creation & refresh token rotation |
| **Profile Service** | `:8003` | MongoDB (`nutriplan`) | User onboarding, medical intake, allergies, and biometric targets |
| **Recipe Service** | `:8004` | MongoDB / PostgreSQL | Comprehensive recipe repository, macro computation, ingredient breakdown |
| **Diary Service** | `:8005` | PostgreSQL (`nutriplan_diary`) | Food logging, automatic daily macro summation, running totals |
| **Grocery Service** | `:8006` | PostgreSQL (`nutriplan_grocery`) | Dynamic grocery lists, pantry sync, item checkoff state |
| **Subscription Service** | `:8007` | PostgreSQL (`nutriplan_subscriptions`) | Tier management (`free`, `pro`, `family`), referral codes, Temporal billing workflows |
| **Meal Plan Service** | `:8009` | PostgreSQL (`nutriplan_meal_plan`) | PydanticAI meal generation with clinical safety validation |
| **Notification Service** | `:8010` | PostgreSQL | Push & email notifications, reminder dispatch queues |
| **Appointment Service** | `:8013` | PostgreSQL (`nutriplan_appointments`) | Dietitian slot availability, Telehealth scheduling, session state |
| **Video Service** | `:8014` | — | Jitsi Meet room provisioning and authenticated JWT tokens |
| **Payment Service** | `:8016` | PostgreSQL (`nutriplan_payments`) | Stripe Connect, SetupIntents, PaymentIntents, webhook ledger |
| **Delivery Service** | `:8017` | — | Deep-linking for Blinkit, Zepto, and Instacart carts |
| **Wearable Service** | `:8018` | — | HealthKit, Health Connect, and basal/active calorie TDEE calculations |
| **Marketplace Service** | `:8025` | MongoDB | Search, filter, and review certified clinical nutritionists |
| **Temporal Server & UI** | `:7233` / `:8233` | In-Memory / SQLite | Durable orchestration engine and workflow inspection dashboard |
| **Frontend Web App** | `:5173` | — | Vue 3 + Vite + Tailwind CSS + Pinia reactive application |

---

## 🚀 Getting Started

### Prerequisites
* **macOS** (Apple Silicon or Intel) or Linux
* **Python 3.12+**
* **Node.js 20+** & `npm`
* **PostgreSQL 14+** (running on `localhost:5432` with user `nutriplan:nutriplan`)
* **MongoDB Community 8+** (running on `localhost:27017`)
* **Temporal CLI** (`brew install temporal`)

---

### Installation & Environment Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url> Project-nutri
   cd Project-nutri
   ```

2. **Initialize Single Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install Frontend Dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure Environment Variables:**
   Copy the example `.env` file:
   ```bash
   cp .env.example .env
   ```
   *Verify your `STRIPE_SECRET_KEY` and `VITE_STRIPE_PUBLISHABLE_KEY` in `.env` and `frontend/.env`.*

---

## ⚙️ Running the Application

All services, Temporal dev server, worker queues, and the Vite frontend are unified via the root `Makefile` and helper scripts:

### Starting the Ecosystem
```bash
make start
# or
make dev
```

### Checking Service Health
```bash
make status
```

### Stopping All Services
```bash
make stop
```

---

## 🌐 Key URLs & Port Directory

| Application / Dashboard | URL |
|---|---|
| **Frontend Web Application** | [http://localhost:5173](http://localhost:5173) |
| **Temporal Workflow Web UI** | [http://localhost:8233](http://localhost:8233) |
| **Auth API Docs** | [http://localhost:8001/docs](http://localhost:8001/docs) |
| **Profile API Docs** | [http://localhost:8003/docs](http://localhost:8003/docs) |
| **Meal Plan API Docs** | [http://localhost:8009/docs](http://localhost:8009/docs) |
| **Diary API Docs** | [http://localhost:8005/docs](http://localhost:8005/docs) |
| **Grocery API Docs** | [http://localhost:8006/docs](http://localhost:8006/docs) |
| **Payment API Docs** | [http://localhost:8016/docs](http://localhost:8016/docs) |
| **Marketplace API Docs** | [http://localhost:8025/docs](http://localhost:8025/docs) |

---

## 🧪 Testing & Verification

Run the automated backend test suite:
```bash
# Run unit & integration tests
make test

# Run frontend E2E Playwright tests
cd frontend && npm run test:e2e
```

---

## 📁 Repository Structure

```text
Project-nutri/
├── backend/
│   ├── auth/              # JWT authentication & credential verification
│   ├── profile/           # User intake, biometrics & health preferences
│   ├── recipe/            # Recipe database & nutritional indexing
│   ├── diary/             # Daily food logging & running macro aggregations
│   ├── grocery/           # Dynamic shopping list & pantry management
│   ├── subscriptions/     # Plan billing, tiers & referral system
│   ├── meal_plan/         # PydanticAI + Llama-3 clinical meal generator
│   ├── notifications/     # Email & in-app push notification dispatcher
│   ├── appointment/       # Telehealth appointment booking & scheduling
│   ├── video/             # Jitsi Meet consultation room generation
│   ├── payment/           # Stripe Connect & SetupIntent webhook processor
│   ├── delivery/          # Blinkit / Zepto / Instacart deep-link engine
│   ├── wearable/          # Apple HealthKit & Health Connect ingestion
│   ├── marketplace/       # Nutritionist directory & matching algorithm
│   └── shared/            # Shared database pools, security & Temporal hub
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI component library (Design System)
│   │   ├── pages/         # Onboarding, Dashboard, Meal Plan, Diary, Telehealth
│   │   ├── stores/        # Pinia reactive state stores (Auth, Diary, Plan)
│   │   └── router/        # Vue Router with auth navigation guards
│   └── package.json
├── scripts/               # Mac setup, database seeding, smoke test scripts
├── start_all.sh           # Unified ecosystem startup runner
├── stop_all.sh            # Complete process and port shutdown runner
├── Makefile               # CLI target runner (make start, stop, status, test)
└── README.md
```

---

## 🔒 Security, Privacy & HIPAA Compliance

* **Token Security**: Strict JWT signature verification with cryptographic salt per password hash.
* **PCI-DSS Compliance**: Direct card details are processed solely inside Stripe's isolated iframe (`@stripe/stripe-js`); zero sensitive card PAN data touches backend servers.
* **Audit Trail**: Webhook processing is idempotent and saved directly into a permanent PostgreSQL event ledger.



# ##############################
Admin	admin@nutriplan.local	Admin@123	System Administrator
Expert / Nutritionist	expert@nutriplan.local	Expert@123	Dr. Sarah Jenkins
Patient	patient@nutriplan.local	Patient@123	Jane Doe
Test Member	test@test.com	Test@123	Test User
https://app.harness.io/ng/account/P8cvPNQpT2GZZGUBp11mlA/all/orgs/default/projects/nutriplan