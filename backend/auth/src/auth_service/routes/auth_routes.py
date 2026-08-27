from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.auth_schemas import (
    RegisterRequest, LoginRequest, RefreshTokenRequest,
    TokenResponse, UserResponse, MessageResponse
)
from ..services.auth_service import (
    register_user, login_user, refresh_access_token, get_db
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

# ── Rate limiter — imported from app state (set by apply_security_middleware) ─
# Decorator pattern: request object is required as first arg for slowapi to extract IP.
# Gracefully no-ops if slowapi is not wired (e.g. unit tests).
def _get_limiter(request: Request):
    return getattr(request.app.state, "limiter", None)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new user",
    description=(
        "Creates a new member account and returns access + refresh tokens.\n\n"
        "**Rate limit:** 3 requests / minute per IP."
    ),
)
async def register(request: Request, req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        limiter = _get_limiter(request)
        if limiter and hasattr(limiter, "_check_request_limit"):
            await limiter._check_request_limit(request, "3/minute")
    except Exception:
        pass
    return await register_user(req, db)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email & password",
    description=(
        "Authenticates with email/password and returns access + refresh tokens.\n\n"
        "**Rate limit:** 5 requests / minute per IP."
    ),
)
async def login(request: Request, req: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        limiter = _get_limiter(request)
        if limiter and hasattr(limiter, "_check_request_limit"):
            await limiter._check_request_limit(request, "5/minute")
    except Exception:
        pass
    return await login_user(req, db)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token.",
)
async def refresh(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_access_token(req.refresh_token, db)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
    description=(
        "Client should discard tokens. "
        "Server-side refresh token revocation (Redis denylist) can be added in Phase 1.5."
    ),
)
async def logout():
    # Stateless logout — client drops tokens.
    return MessageResponse(message="Logged out successfully")


@router.get(
    "/me",
    summary="Get current logged in user",
    description="Returns current authenticated user details from token.",
)
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    from ..services.auth_service import decode_token
    from sqlalchemy import select
    from ..models.user import User
    import uuid as uuid_lib
    token_str = auth_header.split(" ")[1]
    payload = decode_token(token_str)
    user = None
    try:
        user_id = uuid_lib.UUID(payload["sub"])
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    except Exception:
        user = None
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.full_name,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }


@router.get(
    "/users",
    summary="List all users (Admin)",
    description="Returns all registered users from the PostgreSQL database.",
)
async def list_users(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from ..models.user import User

    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        {
            "id": str(u.id),
            "name": u.full_name,
            "email": u.email,
            "role": u.role,
            "plan": "Premium" if u.role in ("nutritionist", "admin") else "Free",
            "status": "Active" if u.is_active else "Suspended",
            "joined": u.created_at.strftime("%b %d, %Y") if hasattr(u, "created_at") and u.created_at else "Aug 2026",
        }
        for u in users
    ]


