from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, Any
import uuid
from datetime import datetime

class RegisterRequest(BaseModel):
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Valid email address")
    password: str = Field(min_length=8, description="Minimum 8 characters")
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    name: Optional[str] = Field(default=None)

    @model_validator(mode='before')
    @classmethod
    def unify_name(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get('full_name') and data.get('name'):
                data['full_name'] = data['name']
            elif not data.get('name') and data.get('full_name'):
                data['name'] = data['full_name']
        return data


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Valid email address")
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


# ── Response schemas ───────────────────────────────────────────────

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int            # seconds
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
