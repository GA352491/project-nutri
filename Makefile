.PHONY: setup dev start stop status test seed generate-api \
        db-migrate db-rollback db-history db-check ci-health

setup:
	@echo "Setting up local environment via Homebrew..."
	bash scripts/setup-mac.sh

seed:
	@echo "Seeding databases..."
	bash scripts/seed-db.sh

dev: start

start:
	@echo "Starting all NutriPlan services..."
	./start_all.sh

stop:
	@echo "Stopping all NutriPlan services..."
	./stop_all.sh

status:
	./start_all.sh --status

test:
	@echo "Running backend tests..."
	python3 -m pytest backend/tests -v
	@echo "Running frontend E2E tests..."
	cd frontend && npm run test:e2e -- --project=chromium

generate-api:
	@echo "Generating API clients..."
	bash scripts/generate-api-client.sh

# ── Database Migrations (Alembic) ─────────────────────────────────────────────
db-migrate:
	@echo "▶ Running Alembic migrations for all 5 PostgreSQL databases..."
	cd backend/migrations && alembic upgrade head
	@echo "✅ All databases migrated to latest revision."

db-rollback:
	@echo "⚠ Rolling back last migration on all databases..."
	cd backend/migrations && alembic downgrade -1
	@echo "✅ Rollback complete."

db-history:
	@echo "Migration history:"
	cd backend/migrations && alembic history --verbose

db-check:
	@echo "Checking migration status (any pending?)..."
	cd backend/migrations && alembic check

# ── CI Utilities ──────────────────────────────────────────────────────────────
ci-health:
	@echo "Checking all service health endpoints..."
	bash scripts/ci-health-check.sh
