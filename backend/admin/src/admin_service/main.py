from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes.admin_routes import router as admin_router

app = FastAPI(
    title="NutriPlan — Admin & CMS Service",
    description="Aggregates data across microservices for internal admin tools.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "admin-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "admin-service"}
