from pydantic_settings import BaseSettings, SettingsConfigDict

class ComplianceSettings(BaseSettings):
    SERVICE_NAME: str = "compliance-service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = ComplianceSettings()
