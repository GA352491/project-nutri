from fastapi import FastAPI
from contextlib import asynccontextmanager
import sys
import os

# Add shared module to path for local execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))
from nutriplan_shared.fastapi import add_standard_middleware, add_health_endpoints
from nutriplan_shared.mongodb import init_mongodb

from .models.nutritionist import Nutritionist
from .routes import nutritionists

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize MongoDB Beanie ODM
    try:
        await init_mongodb(document_models=[Nutritionist])
        print("✅ Marketplace Service started — Swagger: http://localhost:8021/docs")
    except Exception as e:
        print(f"Marketplace Service running with in-memory fallback (MongoDB not connected: {e})")
    yield
    print("Marketplace Service shutting down")

app = FastAPI(
    title="NutriPlan — Marketplace Service",
    description="Nutritionist marketplace, verified provider discovery, and self-serve onboarding.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

add_standard_middleware(app)
add_health_endpoints(app, service_name="marketplace-service")

app.include_router(nutritionists.router, prefix="/api/v1/marketplace/nutritionists", tags=["Marketplace"])
