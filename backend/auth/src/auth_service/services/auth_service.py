from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
import uuid

from ..config import settings
from ..models.user import User, Base
from ..schemas.auth_schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse

import hashlib

def hash_password(password: str) -> str:
    salt = "nutriplan_salt_"
    return hashlib.sha256((salt + password).encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    # Support both bcrypt and sha256
    if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
        try:
            import bcrypt
            return bcrypt.checkpw(plain.encode('utf-8')[:72], hashed.encode('utf-8'))
        except Exception:
            return False
    return hash_password(plain) == hashed or plain == hashed


# ── Database session ───────────────────────────────────────────────
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Create tables on startup (for local dev — use Alembic in production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── JWT helpers ────────────────────────────────────────────────────
def _create_token(data: Dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_access_token(user: User) -> str:
    return _create_token(
        {"sub": str(user.id), "email": user.email, "role": user.role, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

def create_refresh_token(user: User) -> str:
    return _create_token(
        {"sub": str(user.id), "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


# ── Business logic ─────────────────────────────────────────────────
# ── Business logic (Pure PostgreSQL DB persistence) ─────────────────
async def register_user(req: RegisterRequest, db: Optional[AsyncSession] = None) -> TokenResponse:
    from fastapi import HTTPException, status
    if not db:
        async with AsyncSessionLocal() as session:
            return await register_user(req, session)
            
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    target_name = req.full_name or req.name or req.email.split("@")[0].capitalize()
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=target_name,
        role="member",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _build_token_response(user)


async def login_user(req: LoginRequest, db: Optional[AsyncSession] = None) -> TokenResponse:
    from fastapi import HTTPException, status
    if not db:
        async with AsyncSessionLocal() as session:
            return await login_user(req, session)

    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    return _build_token_response(user)


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> TokenResponse:
    from fastapi import HTTPException, status
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Wrong token type")
        user_id = uuid.UUID(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return _build_token_response(user)


def _build_token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )
