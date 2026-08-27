# Harness CI/CD — NutriPlan

All Harness pipeline configs live here. This is a **code-first** setup — Harness syncs automatically from GitHub via **Bi-directional Git Sync**.

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `pipeline.yaml` | Main CI/CD pipeline (4 stages: Lint → Tests → Build → Deploy) |
| `triggers.yaml` | Webhook triggers (push to `main`, all PRs) |
| `ci-template.yaml` | Reusable step template for testing any Python microservice |

---

## Pipeline Stages

```
┌──────────────────┐    ┌──────────────────┐    ┌───────────────────┐    ┌──────────────┐
│  Stage 1: Lint   │───▶│  Stage 2: Tests  │───▶│  Stage 3: Build   │───▶│ Stage 4: CD  │
│                  │    │                  │    │                   │    │  (main only) │
│ vue-tsc          │    │ pytest           │    │ npm run build     │    │ docker pull  │
│ ruff             │    │ Playwright E2E   │    │ Lighthouse CI     │    │ compose up   │
│ mypy             │    │ Alembic dry-run  │    │ Docker push       │    │ health check │
└──────────────────┘    └──────────────────┘    └───────────────────┘    └──────────────┘
  ALL branches             ALL branches            main only               main only
```

---

## Required Connectors (set up once in Harness UI)

| Connector ID | Type | Purpose |
|---|---|---|
| `account.github` | GitHub | Clone `GA352491/project-nutri` |
| `account.docker_hub` | Docker Registry | Pull runner images + push built images |

---

## Required Secrets (add in Harness → Account Settings → Secrets)

| Secret Name | Value |
|---|---|
| `nutriplan_pg_base_url` | PostgreSQL connection URL |
| `nutriplan_mongo_url` | MongoDB connection URL |
| `nutriplan_redis_url` | Redis connection URL |
| `nutriplan_jwt_secret` | JWT signing secret |
| `nutriplan_stripe_secret` | Stripe secret key |

---

## First-time Setup in Harness

1. **Create a free account** → [app.harness.io](https://app.harness.io)
2. **Create a Project** named `nutriplan`
3. **Add GitHub Connector** (`account.github`):
   - Go to *Account Settings → Connectors → New Connector → GitHub*
   - Authenticate via OAuth or PAT
   - Enable **webhook** for triggers
4. **Add Docker Hub Connector** (`account.docker_hub`)
5. **Add Secrets** (see table above)
6. **Enable Git Sync**:
   - Go to *Project Settings → Git Management*
   - Repo: `GA352491/project-nutri`
   - Branch: `main`
   - Root folder: `.harness/`
7. Harness will auto-import `pipeline.yaml`, `triggers.yaml`, and `ci-template.yaml`

---

## Triggering Pipelines

| Event | What fires |
|---|---|
| Push to `main` | Full CI/CD (all 4 stages) |
| Push to `develop` | CI only (Lint + Tests + Build) |
| Pull Request | CI only (Lint + Tests) |
| Manual run | Any stage, any branch |
