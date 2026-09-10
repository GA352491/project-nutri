from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Any, List

class SubscriptionSettings(BaseSettings):
    SERVICE_NAME: str = "subscription-service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # PostgreSQL — stores subscription states
    DATABASE_URL: str = "postgresql+asyncpg://nutriplan:nutriplan@localhost:5432/nutriplan"

    # CORS
    ALLOWED_ORIGINS: Any = ["http://localhost:5173", "http://localhost:3000"]

    # Mock payment keys for Phase 1
    PAYMENT_GATEWAY_SECRET: str = "sk_test_mock123"

    @model_validator(mode="after")
    def parse_allowed_origins(self) -> "SubscriptionSettings":
        val = self.ALLOWED_ORIGINS
        if isinstance(val, str):
            self.ALLOWED_ORIGINS = [o.strip() for o in val.split(",") if o.strip()]
        return self

    @property
    def allowed_origins_list(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        return [o.strip() for o in str(self.ALLOWED_ORIGINS).split(",") if o.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = SubscriptionSettings()
