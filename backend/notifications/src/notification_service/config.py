from pydantic_settings import BaseSettings, SettingsConfigDict

class NotificationSettings(BaseSettings):
    SERVICE_NAME: str = "notification-service"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # MongoDB for notifications
    MONGODB_URL: str = "mongodb://localhost:27017/nutriplan_notifications"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = NotificationSettings()
