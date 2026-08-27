from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings, SettingsConfigDict
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))

class GrocerySettings(BaseSettings):
    SERVICE_NAME: str = "grocery-service"
    DATABASE_URL: str = "postgresql+asyncpg://nutriplan:nutriplan@localhost:5432/nutriplan_grocery"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = GrocerySettings()

from .routes.grocery_routes import router as grocery_router
from .services.grocery_service import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        print("✅ Grocery Service started — Swagger: http://localhost:8006/docs")
    except Exception as e:
        print(f"Grocery Service database note (Postgres offline: {e})")
    yield

app = FastAPI(
    title="NutriPlan — Grocery Service",
    description="Manages grocery lists generated from meal plans.",
    version="1.0.0", docs_url="/docs", redoc_url="/redoc", lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(grocery_router)

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "grocery-service"}
