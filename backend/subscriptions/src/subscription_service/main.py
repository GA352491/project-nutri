from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))

from .config import settings
from .routes.subscription_routes import router as subscription_router
from .services.subscription_service import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: auto-create Postgres tables if DB is reachable
    try:
        await init_db()
        print(f"✅ Subscription Service started — Swagger: http://localhost:8007/docs")
    except Exception as e:
        print(f"Subscription Service database note (Postgres offline: {e})")
    yield
    # Shutdown
    print("Subscription Service shutting down")

app = FastAPI(
    title="NutriPlan — Subscription Service",
    description="Manages user subscriptions, billing, and mock webhooks.",
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

# Routes
app.include_router(subscription_router)

# Health endpoints
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "subscription-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "subscription-service"}
