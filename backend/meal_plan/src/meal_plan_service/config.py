from pydantic_settings import BaseSettings, SettingsConfigDict

class MealPlanSettings(BaseSettings):
    SERVICE_NAME: str = "meal-plan-service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # PostgreSQL — stores relational meal plans
    DATABASE_URL: str = "postgresql+asyncpg://nutriplan:nutriplan@localhost:5432/nutriplan_meal_plan"

    # Services
    RECIPE_SERVICE_URL: str = "http://localhost:8004"
    PROFILE_SERVICE_URL: str = "http://localhost:8003"
    COMPLIANCE_SERVICE_URL: str = "http://localhost:8002"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = MealPlanSettings()
