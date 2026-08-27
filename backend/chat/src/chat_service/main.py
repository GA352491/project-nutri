from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings, SettingsConfigDict
from nutriplan_shared.mongodb import init_mongodb

class ChatSettings(BaseSettings):
    SERVICE_NAME: str = "chat-service"
    MONGODB_URL: str = "mongodb://localhost:27017/nutriplan_chat"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = ChatSettings()

from .routes.chat_routes import router as chat_router
from .models.chat import ChatMessage, Conversation

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_mongodb(document_models=[ChatMessage, Conversation])
        print("✅ Chat Service started — Swagger: http://localhost:8012/docs")
    except Exception as e:
        print(f"Chat Service running with fallback (MongoDB offline: {e})")
    yield

app = FastAPI(
    title="NutriPlan — Chat Service",
    description="Manages nutritionist chat conversations. Phase 1 uses canned responses; Phase 2 plugs in Gemini/OpenAI.",
    version="1.0.0", docs_url="/docs", redoc_url="/redoc", lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(chat_router)

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "chat-service"}
