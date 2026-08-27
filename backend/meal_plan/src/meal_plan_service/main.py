from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))

from .config import settings
from .routes.meal_plan_routes import router as meal_plan_router
from .services.meal_plan_service import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: auto-create Postgres tables
    try:
        await init_db()
        print(f"✅ Meal Plan Service started — Swagger: http://localhost:8009/docs")
    except Exception as e:
        print(f"Meal Plan Service database note (Postgres offline: {e})")
    yield
    # Shutdown
    print("Meal Plan Service shutting down")

app = FastAPI(
    title="NutriPlan — Meal Plan Service",
    description="Generates and tracks weekly meal plans.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes - AI Temporal Workflow Router mounted first
from .routes.plans import router as plans_ai_router
app.include_router(plans_ai_router, prefix="/api/v1/plan", tags=["AI Plan Workflows"])
app.include_router(meal_plan_router)

# Health endpoints
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "meal-plan-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "meal-plan-service"}
