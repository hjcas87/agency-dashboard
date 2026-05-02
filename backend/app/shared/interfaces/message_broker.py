"""
Interface para message brokers (Kafka, RabbitMQ, etc.)
"""
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Optional


class IMessageBroker(ABC):
    """Interface para message brokers."""

    @abstractmethod
    async def publish(
        self,
        topic: str,
        message: dict[str, Any],
        key: Optional[str] = None,
    ) -> bool:
        """
        Publica un mensaje en un topic.

        Args:
            topic: Nombre del topic
            message: Mensaje a publicar
            key: Clave opcional para particionamiento

        Returns:
            True si se publicó exitosamente
        """
        pass

    @abstractmethod
    async def consume(
        self,
        topic: str,
        group_id: str,
        callback: Callable[[dict[str, Any]], Any],
    ) -> None:
        """
        Consume mensajes de un topic.

        Args:
            topic: Nombre del topic
            group_id: ID del grupo de consumidores
            callback: Función a ejecutar por cada mensaje
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verifica la salud del broker."""
        pass
