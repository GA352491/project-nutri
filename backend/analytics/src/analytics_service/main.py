from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .routes.analytics_routes import router as analytics_router
from nutriplan_shared.mongodb import init_mongodb
from .models.event import TrackingEvent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize MongoDB Beanie ODM
    await init_mongodb(document_models=[TrackingEvent])
    print(f"✅ Analytics Service started — Swagger: http://localhost:8012/docs")
    yield
    # Shutdown
    print("Analytics Service shutting down")

app = FastAPI(
    title="NutriPlan — Analytics Service",
    description="Tracks user events and forwards them to a data warehouse.",
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
app.include_router(analytics_router)

# Health endpoints
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "analytics-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "analytics-service"}
