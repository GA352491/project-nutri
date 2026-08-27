from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))

from .config import settings
from .routes.auth_routes import router as auth_router
from .services.auth_service import init_db
from nutriplan_shared.middleware import apply_security_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: auto-create tables for local dev
    try:
        await init_db()
        print(f"✅ Auth Service started — Swagger: http://localhost:8001/docs")
    except Exception as e:
        print(f"Auth Service database connection note (PostgreSQL offline: {e})")
    yield
    print("Auth Service shutting down")


app = FastAPI(
    title="NutriPlan — Auth Service",
    description="""
## Authentication Service

Handles user registration, login, and JWT token management.

### Local Dev Mode
Running in **standalone JWT mode** (no Keycloak required).  
Tokens are HS256 JWTs signed with `JWT_SECRET_KEY` from `.env`.

### Rate Limits
- `POST /api/v1/auth/login`    → **5 requests / minute** per IP
- `POST /api/v1/auth/register` → **3 requests / minute** per IP

### Endpoints
- `POST /api/v1/auth/register` — Create account
- `POST /api/v1/auth/login` — Login
- `POST /api/v1/auth/refresh` — Refresh access token
- `POST /api/v1/auth/logout` — Logout (stateless)
    """,
    version="1.0.0",
    contact={"name": "NutriPlan Engineering"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── Security: CORS + headers + rate limiting + request size limits ────────────
# Returns a Limiter so individual routes can apply @limiter.limit(...)
limiter = apply_security_middleware(app, settings)

# Routes
app.include_router(auth_router)


# ── Health endpoints ──────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "auth-service"}

@app.get("/ready", tags=["Health"])
async def ready():
    return {"status": "ready", "service": "auth-service"}
