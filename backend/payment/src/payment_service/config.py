from pydantic_settings import BaseSettings, SettingsConfigDict


class PaymentSettings(BaseSettings):
    SERVICE_NAME: str = "payment-service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # PostgreSQL — source of truth for payment ledger, Connect accounts, webhooks
    DATABASE_URL: str = "postgresql+asyncpg://nutriplan:nutriplan@localhost:5432/nutriplan_payments"

    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = PaymentSettings()
