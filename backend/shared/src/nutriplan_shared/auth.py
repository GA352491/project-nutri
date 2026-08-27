"""JWT authentication shared by all NutriPlan HTTP services."""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .exceptions import UnauthorizedException

_bearer = HTTPBearer(auto_error=True)

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "local-dev-secret-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def _decode(token: str) -> Dict[str, Any]:
    try:
        from jose import JWTError, jwt
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except ImportError:
        import jwt as pyjwt
        return pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception as exc:
        raise UnauthorizedException(detail="Invalid authentication credentials") from exc


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Dict[str, Any]:
    payload = _decode(creds.credentials)
    if not payload.get("sub"):
        raise UnauthorizedException(detail="Token missing subject")
    return payload


def user_uuid(user: Dict[str, Any]) -> uuid.UUID:
    try:
        return uuid.UUID(str(user["sub"]))
    except (ValueError, KeyError) as exc:
        raise UnauthorizedException(detail="Token subject is not a user id") from exc
