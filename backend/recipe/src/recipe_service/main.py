from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .routes.recipe_routes import router as recipe_router
from nutriplan_shared.mongodb import init_mongodb
from .models.food_item import FoodItem
from .models.recipe import Recipe

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize MongoDB Beanie ODM
    try:
        await init_mongodb(document_models=[FoodItem, Recipe])
        from .services.recipe_service import seed_regional_recipes_if_empty
        await seed_regional_recipes_if_empty()
        print(f"✅ Recipe Service started with regional seeds — Swagger: http://localhost:8004/docs")
    except Exception as e:
        print(f"Recipe Service running in fast in-memory mode (MongoDB offline: {e})")
    yield
    # Shutdown
    print("Recipe Service shutting down")

app = FastAPI(
    title="NutriPlan — Recipe Service",
    description="Manages food items (IFCT) and curates recipes.",
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
app.include_router(recipe_router)

# Health endpoints
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "recipe-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "recipe-service"}
