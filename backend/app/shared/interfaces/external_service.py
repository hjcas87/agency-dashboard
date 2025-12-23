"""
Interface para servicios externos (N8N, APIs, etc.)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IExternalService(ABC):
    """Interface para servicios externos."""

    @abstractmethod
    async def call(
        self,
        endpoint: str,
        method: str = "POST",
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Realiza una llamada al servicio externo.
        
        Args:
            endpoint: Endpoint del servicio
            method: Método HTTP
            payload: Datos a enviar
            headers: Headers HTTP
            
        Returns:
            Respuesta del servicio
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verifica la salud del servicio."""
        pass

