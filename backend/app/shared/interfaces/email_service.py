"""
Interface para servicios de email.
"""
from abc import ABC, abstractmethod


class IEmailService(ABC):
    """Interface para servicios de email."""

    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str | None = None,
    ) -> bool:
        """
        Envía un email.
        
        Args:
            to: Email del destinatario
            subject: Asunto del email
            body: Cuerpo del email en texto plano
            html_body: Cuerpo del email en HTML (opcional)
            
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        pass

