"""
Interface para servicios de email.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Attachment:
    """Representa un archivo adjunto para un email."""

    filename: str
    content: bytes
    mime_type: str


class IEmailService(ABC):
    """Interface para servicios de email."""

    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str | None = None,
        attachments: list[Attachment] | None = None,
        cc: str | None = None,
    ) -> bool:
        """
        Envía un email.

        Args:
            to: Email del destinatario
            subject: Asunto del email
            body: Cuerpo del email en texto plano
            html_body: Cuerpo del email en HTML (opcional)
            attachments: Lista de archivos adjuntos (opcional)
            cc: Email con copia (opcional)

        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        pass

