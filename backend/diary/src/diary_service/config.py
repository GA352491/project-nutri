from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Any, List
from nutriplan_shared.service_registry import RECIPE_URL

class DiarySettings(BaseSettings):
    SERVICE_NAME: str = "diary-service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # PostgreSQL — stores daily diary entries and macro aggregations
    DATABASE_URL: str = "postgresql+asyncpg://nutriplan:nutriplan@localhost:5432/nutriplan_diary"

    # Services — derived dynamically from service_registry
    RECIPE_SERVICE_URL: str = RECIPE_URL

    # CORS
    ALLOWED_ORIGINS: Any = ["http://localhost:5173", "http://localhost:3000"]

    @model_validator(mode="after")
    def parse_allowed_origins(self) -> "DiarySettings":
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

settings = DiarySettings()
