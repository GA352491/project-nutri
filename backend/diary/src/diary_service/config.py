from pydantic_settings import BaseSettings, SettingsConfigDict

class DiarySettings(BaseSettings):
    SERVICE_NAME: str = "diary-service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # PostgreSQL — stores daily diary entries and macro aggregations
    DATABASE_URL: str = "postgresql+asyncpg://nutriplan:nutriplan@localhost:5432/nutriplan_diary"

    # Services
    RECIPE_SERVICE_URL: str = "http://localhost:8004"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = DiarySettings()
