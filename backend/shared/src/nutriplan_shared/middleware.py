"""
NutriPlan Shared Middleware Factory
====================================
Provides a single call — ``apply_security_middleware(app)`` — that wires:

  1. CORS            — configurable allowed origins via env
  2. Rate Limiting   — slowapi / Redis-backed, per-IP for auth, per-user elsewhere
  3. Request Size    — 512 KB for JSON, 10 MB for uploads
  4. Security Headers — X-Content-Type-Options, X-Frame-Options, HSTS (prod)

Usage in any FastAPI service ``main.py``::

    from nutriplan_shared.middleware import apply_security_middleware
    apply_security_middleware(app, settings)
"""
from __future__ import annotations

import os
import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# ── Optional slowapi import (gracefully degrade if not installed) ─────────────
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    _SLOWAPI_AVAILABLE = True
except ImportError:
    _SLOWAPI_AVAILABLE = False
    logger.warning("slowapi not installed — rate limiting disabled. Run: pip install slowapi")


# ─────────────────────────────────────────────────────────────────────────────
# Security Headers Middleware
# ─────────────────────────────────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds OWASP-recommended security headers to every response."""

    def __init__(self, app: FastAPI, environment: str = "local") -> None:
        super().__init__(app)
        self.is_prod = environment.lower() in ("production", "staging")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"]        = "DENY"
        response.headers["X-XSS-Protection"]       = "1; mode=block"
        response.headers["Referrer-Policy"]         = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"]      = "camera=(), microphone=(), geolocation=()"
        if self.is_prod:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        return response


# ─────────────────────────────────────────────────────────────────────────────
# Request Size Limit Middleware
# ─────────────────────────────────────────────────────────────────────────────
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Rejects requests whose body exceeds the configured limit."""

    def __init__(
        self,
        app: FastAPI,
        max_upload_bytes: int = 10 * 1024 * 1024,   # 10 MB  for multipart
        max_json_bytes:   int = 512 * 1024,           # 512 KB for JSON/form
    ) -> None:
        super().__init__(app)
        self.max_upload_bytes = max_upload_bytes
        self.max_json_bytes   = max_json_bytes

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        content_type   = request.headers.get("content-type", "")
        content_length = request.headers.get("content-length")

        if content_length:
            size = int(content_length)
            is_upload = "multipart/form-data" in content_type
            limit     = self.max_upload_bytes if is_upload else self.max_json_bytes

            if size > limit:
                limit_mb = limit / (1024 * 1024)
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": f"Request body too large. Maximum allowed: {limit_mb:.1f} MB"
                    },
                )
        return await call_next(request)


# ─────────────────────────────────────────────────────────────────────────────
# Rate Limiter Factory
# ─────────────────────────────────────────────────────────────────────────────
def create_limiter(redis_url: str | None = None) -> "Limiter | None":
    """
    Create a slowapi Limiter.

    Falls back to in-memory storage if Redis is unavailable or slowapi
    is not installed (e.g. during unit tests).
    """
    if not _SLOWAPI_AVAILABLE:
        return None

    storage_uri = redis_url or os.getenv("REDIS_URL", "memory://")
    # Use memory:// in test environments to avoid Redis dependency
    if os.getenv("TESTING", "0") == "1":
        storage_uri = "memory://"

    return Limiter(
        key_func=get_remote_address,
        storage_uri=storage_uri,
        headers_enabled=True,          # adds X-RateLimit-* headers to responses
        swallow_errors=True,           # don't crash if Redis is temporarily down
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main Public API
# ─────────────────────────────────────────────────────────────────────────────
def apply_security_middleware(app: FastAPI, settings: object) -> "Limiter | None":
    """
    Wire all security middleware onto a FastAPI app.

    Returns the Limiter instance so individual routes can apply
    ``@limiter.limit(...)`` decorators.

    Example::

        limiter = apply_security_middleware(app, settings)

        @app.post("/api/v1/auth/login")
        @limiter.limit("5/minute")
        async def login(request: Request, ...): ...
    """
    environment  = getattr(settings, "ENVIRONMENT", "local")
    redis_url    = getattr(settings, "REDIS_URL",    None)
    raw_origins  = getattr(settings, "ALLOWED_ORIGINS", [])

    # ── 1. CORS ───────────────────────────────────────────────────────────────
    allowed_origins: list[str] = (
        raw_origins if isinstance(raw_origins, list)
        else [o.strip() for o in raw_origins.split(",")]
    )
    # Always allow FRONTEND_URL and all ALLOWED_ORIGINS in non-prod environments
    if environment not in ("production",):
        import os
        _frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        _extra_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
        for origin in ([_frontend_url] + _extra_origins):
            if origin and origin not in allowed_origins:
                allowed_origins.append(origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Correlation-ID"],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "X-Correlation-ID"],
    )
    logger.info("CORS configured for origins: %s", allowed_origins)

    # ── 2. Security headers ───────────────────────────────────────────────────
    app.add_middleware(SecurityHeadersMiddleware, environment=environment)

    # ── 3. Request size limits ────────────────────────────────────────────────
    app.add_middleware(RequestSizeLimitMiddleware)

    # ── 4. Structured request logging (stdout + rotating file under LOG_DIR)
    service_name = getattr(settings, "SERVICE_NAME", None) or getattr(app, "title", "service")
    from .logging_middleware import StructuredLoggingMiddleware, configure_logging
    configure_logging(str(service_name))
    app.add_middleware(StructuredLoggingMiddleware, service_name=str(service_name))

    # ── 4. Rate limiting ──────────────────────────────────────────────────────
    limiter = create_limiter(redis_url)
    if limiter and _SLOWAPI_AVAILABLE:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        logger.info("Rate limiting enabled (storage: %s)", redis_url or "memory://")
    else:
        logger.warning("Rate limiting DISABLED — slowapi not available")

    return limiter

# Alias for backward compatibility
def add_standard_middleware(app: FastAPI, settings: object = None) -> "Limiter | None":
    return apply_security_middleware(app, settings)
