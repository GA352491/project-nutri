from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class BaseServiceSettings(BaseSettings):
    """
    Base configuration for all NutriPlan services.
    Each service should subclass this if they need specific variables.
    Defaults assume a local development environment.
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
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

def get_settings() -> BaseServiceSettings:
    return BaseServiceSettings()
