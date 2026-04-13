"""
Application configuration using Pydantic settings.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Obtener la ruta al directorio backend (un nivel arriba desde este archivo)
BACKEND_DIR = Path(__file__).parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    PROJECT_NAME: str = "Automation Warehouse API"
    ENVIRONMENT: str = "DEVELOPMENT"
    API_VERSION: str = "v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "core_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # RabbitMQ (para Celery tasks)
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "admin"
    RABBITMQ_PASSWORD: str = "admin"

    # Celery (usa RabbitMQ como broker para tareas en background)
    CELERY_BROKER_URL: str = "amqp://admin:admin@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "rpc://"

    # N8N
    N8N_BASE_URL: str = "http://localhost:5678"
    N8N_WEBHOOK_URL: str = "http://localhost:5678"
    N8N_API_KEY: str | None = None
    N8N_API_KEY_HEADER: str = "X-API-Key"

    # Email Service
    EMAIL_PROVIDER: str = "smtp"
    EMAIL_FROM_NAME: str = "Equipo"

    # SMTP Configuration
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_USE_TLS: bool = True

    # API Email Configuration (SendGrid, Mailgun, etc.)
    EMAIL_API_URL: str | None = None
    EMAIL_API_KEY: str | None = None
    EMAIL_API_KEY_HEADER: str = "Authorization"
    EMAIL_FROM_EMAIL: str | None = None

    # Frontend URL (para links en emails)
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]


settings = Settings()

