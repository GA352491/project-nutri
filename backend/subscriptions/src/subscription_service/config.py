from pydantic_settings import BaseSettings, SettingsConfigDict

class SubscriptionSettings(BaseSettings):
    SERVICE_NAME: str = "subscription-service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # PostgreSQL — stores subscription states
    DATABASE_URL: str = "postgresql+asyncpg://nutriplan:nutriplan@localhost:5432/nutriplan_subscriptions"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Mock payment keys for Phase 1
    PAYMENT_GATEWAY_SECRET: str = "sk_test_mock123"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = SubscriptionSettings()
