from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))

from .config import settings
from .routes.profile_routes import router as profile_router
from nutriplan_shared.mongodb import init_mongodb
from .models.profile import UserProfile

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize MongoDB Beanie ODM
    try:
        await init_mongodb(document_models=[UserProfile])
        print(f"✅ Profile Service started — Swagger: http://localhost:8003/docs")
    except Exception as e:
        print(f"Profile Service running with fallback (MongoDB offline: {e})")
    yield
    # Shutdown
    print("Profile Service shutting down")

app = FastAPI(
    title="NutriPlan — Profile Service",
    description="Handles user profiles, onboarding data, and pantry inventory.",
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
app.include_router(profile_router)

# Health endpoints
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "profile-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "profile-service"}
