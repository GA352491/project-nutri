from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional, Any, List

class BaseServiceSettings(BaseSettings):
    """
    Base configuration for all NutriPlan services.
    Each service should subclass this if they need specific variables.
    Defaults assume a local development environment.

    Domain/URL note:
        Service URLs are NOT stored here — they are assembled at import
        time in nutriplan_shared.service_registry using APP_DOMAIN,
        APP_SCHEME, and APP_PORT_* from the root .env. Import from
        service_registry whenever you need to call another service.
    """
    SERVICE_NAME: str = "nutriplan_service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # Core Datastores
    DATABASE_URL: str = "postgresql+asyncpg://nutriplan:nutriplan@localhost:5432/nutriplan"
    MONGODB_URL: str = "mongodb://localhost:27017/nutriplan"
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # Auth
    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "nutriplan"
    KEYCLOAK_CLIENT_ID: str = "nutriplan-web"

    # CORS — accepts comma-separated string from ALLOWED_ORIGINS env var or list
    # Automatically normalized into list[str] for CORSMiddleware
    ALLOWED_ORIGINS: Any = ["http://localhost:5173", "http://localhost:3000"]

    @model_validator(mode="after")
    def parse_allowed_origins(self) -> "BaseServiceSettings":
        val = self.ALLOWED_ORIGINS
        if isinstance(val, str):
            self.ALLOWED_ORIGINS = [o.strip() for o in val.split(",") if o.strip()]
        return self

    @property
    def allowed_origins_list(self) -> List[str]:
        """Return ALLOWED_ORIGINS as a parsed list for FastAPI CORSMiddleware."""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        return [o.strip() for o in str(self.ALLOWED_ORIGINS).split(",") if o.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

def get_settings() -> BaseServiceSettings:
    return BaseServiceSettings()
