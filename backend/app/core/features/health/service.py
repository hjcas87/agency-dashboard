"""
Service layer para health checks.
"""
from typing import Any

from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.shared.constants import HEALTH_STATUS
from app.shared.services.n8n_service import N8NService


class HealthFeatureService:
    """Service para health checks."""

    def __init__(
        self,
        n8n_service: N8NService,
    ):
        """
        Inicializa el service.

        Args:
            n8n_service: Instancia del servicio N8N
        """
        self.n8n_service = n8n_service

    def check_health(self, module: str = "core") -> dict[str, Any]:
        """
        Realiza un health check completo.

        Args:
            module: Nombre del módulo

        Returns:
            Estado de salud del sistema
        """
        details = {
            "database": self._check_database(),
            "rabbitmq": self._check_rabbitmq(),
            "n8n": self._check_n8n(),
        }

        all_healthy = all(details.values())

        return {
            "status": HEALTH_STATUS["HEALTHY"] if all_healthy else HEALTH_STATUS["DEGRADED"],
            "module": module,
            "details": details,
        }

    def _check_database(self) -> bool:
        """Verifica la conexión a la base de datos."""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def _check_rabbitmq(self) -> bool:
        """Verifica la conexión a RabbitMQ."""
        try:
            import pika

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    credentials=pika.PlainCredentials(
                        settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD
                    ),
                    connection_attempts=1,
                    socket_timeout=2,
                )
            )
            connection.close()
            return True
        except Exception:
            return False

    def _check_n8n(self) -> bool:
        """Verifica la conexión a N8N."""
        return self.n8n_service.health_check()
