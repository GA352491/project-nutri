# 🚀 NutriPlan — Developer Onboarding & Local Setup Guide

Welcome to the **NutriPlan** engineering team! This guide walks you through setting up your local environment, running the full stack, running test suites, and understanding the development workflow.

---

## 📋 1. Prerequisites & Tooling

Before starting, ensure you have the following installed on your machine:
- **macOS** or **Linux**
- **Python 3.11+** (`python3 --version`)
- **Node.js 20+** & **npm** (`node -v`, `npm -v`)
- **Docker Desktop** (for running PostgreSQL, MongoDB, Redis, and Temporal)
- **Ollama** (optional, for local LLM inference): `brew install ollama`
- **Flutter SDK** (optional, for mobile app development): `flutter --version`

---

## 🛠️ 2. Quickstart (One-Command Boot)

### Step 1: Clone and Configure Environment
```bash
git clone <repository_url> Project-nutri
cd Project-nutri

# Create environment configuration from template
cp .env.example .env
```

### Step 2: Start Infrastructure via Docker Compose
```bash
docker compose up -d
```
This boots up:
- **PostgreSQL 15** on `localhost:5432`
- **MongoDB 6.0** on `localhost:27017`
- **Redis 7** on `localhost:6379`
- **Temporal Server** on `localhost:7233` (Web UI at `http://localhost:8233`)

### Step 3: Install Dependencies
```bash
# Backend shared libraries & core dependencies
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..
```

### Step 4: Start All Services & API Gateway
```bash
bash scripts/start-dev.sh
```
This script launches Redis, Ollama, the FastStream Event Broker, the Temporal Booking Worker, and all **16 microservices** with live auto-reload enabled.

---

## 🌐 3. Key Local URLs & Dashboards

| Service / Interface | Local URL | Description |
|---|---|---|
| **API Gateway & Dashboard** | [http://localhost:8000](http://localhost:8000) | Live service registry and status overview |
| **Unified Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive testing across all 16 microservices |
| **Unified Redoc Portal** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Clean consolidated API reference documentation |
| **Frontend Web App** | [http://localhost:5173](http://localhost:5173) | Vue 3 patient portal, marketplace & admin UI |
| **Temporal Web UI** | [http://localhost:8233](http://localhost:8233) | Real-time saga workflow execution visualizer |

---

## 🧪 4. Testing & Verification

### Running the Live Stack Smoke Test Suite
Validates that all microservices, the API gateway, compliance calculations, marketplace directory, and payment flows are operational:
```bash
bash scripts/smoke-test.sh
```

### Running Backend Pytest Suite
```bash
pytest backend/tests -v
```

### Running Frontend Type-Check & Linter
```bash
cd frontend
npm run type-check
```

### Frontend Bundle Visualizer & Performance Audit
```bash
cd frontend
npm run build:analyze
```

---

## 📂 5. Repository Layout

```text
Project-nutri/
├── .harness/               # Harness CI/CD pipelines & templates
├── backend/                # Microservices Ecosystem
│   ├── shared/             # nutriplan_shared (middleware, HIPAA, database, faststream)
│   ├── gateway/            # API Gateway & OpenAPI aggregator (:8000)
│   ├── auth/               # JWT & role authorization (:8001)
│   ├── compliance/         # ICMR-NIN & USDA DGA rules engine (:8002)
│   ├── profile/            # User onboarding & pantry inventory (:8003)
│   ├── recipe/             # Food database & USDA import (:8004)
│   ├── diary/              # Food logging & atomic macro tracking (:8005)
│   ├── grocery/            # Grocery checklist generator (:8006)
│   ├── subscriptions/      # Billing, referrals & family plans (:8007)
│   ├── meal_plan/          # Pydantic AI & Guardrails AI meal engine (:8009)
│   ├── notifications/      # In-app alerts & push notifications (:8010)
│   ├── chat/               # Nutritionist 1-on-1 chat (:8012)
│   ├── appointment/        # Temporal booking saga & scheduling (:8013)
│   ├── video/              # Jitsi video consultation rooms (:8014)
│   ├── ai_chatbot/         # LangGraph multi-agent clinical triage (:8015)
│   ├── payment/            # Stripe Connect & PaymentIntents (:8016)
│   ├── delivery/           # Quick-commerce basket deep linking (:8017)
│   ├── wearable/           # HealthKit / Health Connect ingestion (:8018)
│   └── marketplace/        # Certified nutritionist directory (:8021)
├── frontend/               # Vue 3, Vite, Tailwind CSS Web Application
├── mobile/                 # Flutter iOS & Android Mobile Application
├── docs/                   # Product & Technical Design Documents
├── scripts/                # Dev startup, health check, seed & import scripts
└── docker-compose.yml      # Local database and infrastructure orchestration
```

---

## 🌿 6. Coding Standards & Git Workflow

1. **Branch Naming**: `feat/T-XXX-short-name`, `fix/issue-description`
2. **Commit Messages**: Follow Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
3. **Database Changes**: Use centralized multi-database Alembic migrations in `backend/migrations/`.
4. **Security**: Never commit raw API keys or credentials. Use `.env` variables and test mocks.
