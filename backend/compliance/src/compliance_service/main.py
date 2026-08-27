from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes.compliance_routes import router as compliance_router

app = FastAPI(
    title="NutriPlan — Compliance Service",
    description="Rules engine for evaluating dietary compliance against medical/national guidelines (ICMR-NIN).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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
app.include_router(compliance_router)

# Health endpoints
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "compliance-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "compliance-service"}
