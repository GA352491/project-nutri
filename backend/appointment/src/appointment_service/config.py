from pydantic_settings import BaseSettings, SettingsConfigDict


class AppointmentSettings(BaseSettings):
    SERVICE_NAME: str = "appointment-service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://nutriplan:nutriplan@localhost:5432/nutriplan_appointments"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = AppointmentSettings()
