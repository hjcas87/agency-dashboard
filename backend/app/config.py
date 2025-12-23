"""
Application configuration using Pydantic settings.
"""
from pathlib import Path
from pydantic_settings import BaseSettings

# Obtener la ruta al directorio backend (un nivel arriba desde este archivo)
BACKEND_DIR = Path(__file__).parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings."""

    # App
    PROJECT_NAME: str = "Automation Warehouse API"
    ENVIRONMENT: str = "DEVELOPMENT"
    API_VERSION: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # RabbitMQ (para Celery tasks)
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    # Celery (usa RabbitMQ como broker para tareas en background)
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # N8N
    N8N_BASE_URL: str
    N8N_WEBHOOK_URL: str
    N8N_API_KEY: str | None = None  # API key para autenticación Header Auth (opcional)
    N8N_API_KEY_HEADER: str = "X-API-Key"  # Nombre del header para la API key (default: X-API-Key)

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]

    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = True


settings = Settings()

