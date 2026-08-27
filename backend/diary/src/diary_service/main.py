from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))

from .config import settings
from .routes.diary_routes import router as diary_router
from .services.diary_service import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        print("✅ Diary Service started — Swagger: http://localhost:8005/docs")
    except Exception as e:
        print(f"Diary Service database note (Postgres offline: {e})")
    yield
    print("Diary Service shutting down")


app = FastAPI(
    title="NutriPlan — Diary Service",
    description="""
## Food Diary & Logging Service

Handles all food logging events and maintains pre-aggregated daily summaries.

### Key Design Decision
Every `POST /entries` call atomically upserts a `DailySummary` row so the 
Today dashboard can display totals with a single fast query rather than 
aggregating at read-time.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diary_router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "diary-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "diary-service"}
