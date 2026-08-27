"""
NutriPlan — Centralised Alembic env.py
Handles PostgreSQL databases in a single migration run using
Alembic's include_schemas / multi-database pattern.

Databases managed:
  nutriplan_auth      → auth service      (users)
  nutriplan_diary     → diary service     (diary_entries, daily_summaries)
  nutriplan_grocery   → grocery service   (grocery_lists, grocery_items)
  nutriplan_meal_plan → meal plan service (meal_plans, meal_plan_items)
  nutriplan_subs      → subscription svc  (subscriptions)
  nutriplan_payments  → payment service   (payments, connect_accounts, webhook_events)
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# ── Add backend services to path ─────────────────────────────────────────────
BACKEND_ROOT = os.path.dirname(os.path.dirname(__file__))
for service in ["shared", "auth", "diary", "grocery", "meal_plan", "subscriptions", "payment"]:
    src = os.path.join(BACKEND_ROOT, service, "src")
    if os.path.isdir(src) and src not in sys.path:
        sys.path.insert(0, src)

# ── Import every SQLAlchemy Base / metadata ───────────────────────────────────
from nutriplan_shared.models.base import Base as SharedBase

from auth_service.models.user import Base as AuthBase, User                         # noqa: F401
from diary_service.models.diary import Base as DiaryBase, DiaryEntry, DailySummary # noqa: F401
from grocery_service.models.grocery import (                                        # noqa: F401
    Base as GroceryBase, GroceryList, GroceryItem
)
from meal_plan_service.models.meal_plan import (                                    # noqa: F401
    Base as MealPlanBase, MealPlan, MealPlanItem
)
from subscription_service.models.subscription import (                              # noqa: F401
    Base as SubBase, Subscription
)
from payment_service.models.payment import (                                        # noqa: F401
    Base as PaymentBase, Payment, ConnectAccount, WebhookEvent
)

# ── Database URL mapping ─────────────────────────────────────────────────────
PG_BASE = os.getenv("PG_BASE_URL", "postgresql://nutriplan:nutriplan@localhost:5432")

DB_CONFIG = {
    "auth":      (f"{PG_BASE}/nutriplan_auth",      AuthBase.metadata),
    "diary":     (f"{PG_BASE}/nutriplan_diary",     DiaryBase.metadata),
    "grocery":   (f"{PG_BASE}/nutriplan_grocery",   GroceryBase.metadata),
    "meal_plan": (f"{PG_BASE}/nutriplan_meal_plan", MealPlanBase.metadata),
    "subs":      (f"{PG_BASE}/nutriplan_subs",      SubBase.metadata),
    "payments":  (f"{PG_BASE}/nutriplan_payments",  PaymentBase.metadata),
}

# ── Alembic Config ────────────────────────────────────────────────────────────
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Generate SQL scripts without a live DB connection (--sql mode)."""
    for name, (url, metadata) in DB_CONFIG.items():
        print(f"\n-- [{name}] offline migration SQL --")
        context.configure(
            url=url,
            target_metadata=metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )
        with context.begin_transaction():
            context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against live databases — one engine per DB."""
    for name, (url, metadata) in DB_CONFIG.items():
        # Use sync engine for Alembic (asyncpg not supported by Alembic directly)
        sync_url = url.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(sync_url, poolclass=pool.NullPool)

        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=metadata,
                include_schemas=True,
                compare_type=True,        # detect column type changes
                compare_server_default=True,
            )
            print(f"  ▶ Running migrations for [{name}] ({sync_url.split('@')[-1]})")
            with context.begin_transaction():
                context.run_migrations()

        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
