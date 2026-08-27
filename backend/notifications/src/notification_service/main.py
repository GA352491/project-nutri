from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .routes.notification_routes import router as notification_router
from nutriplan_shared.mongodb import init_mongodb
from .models.notification import Notification

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize MongoDB Beanie ODM
    try:
        await init_mongodb(document_models=[Notification])
        print(f"✅ Notification Service started — Swagger: http://localhost:8010/docs")
    except Exception as e:
        print(f"Notification Service running with fallback (MongoDB offline: {e})")
    yield
    # Shutdown
    print("Notification Service shutting down")

app = FastAPI(
    title="NutriPlan — Notification Service",
    description="Manages system notifications, reminders, and alerts.",
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
app.include_router(notification_router)

# Health endpoints
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "notification-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "notification-service"}
