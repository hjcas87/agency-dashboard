"""
Implementación del servicio de email.
Soporta SMTP y APIs de email (SendGrid, Mailgun, etc).
"""
import base64
import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import httpx

from app.config import settings
from app.shared.interfaces.email_service import Attachment, IEmailService

logger = logging.getLogger(__name__)


class SMTPEmailService(IEmailService):
    """Servicio de email usando SMTP."""

    def __init__(self):
        """Inicializa el servicio SMTP."""
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL or settings.EMAIL_FROM_EMAIL
        self.from_name = settings.EMAIL_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS

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
        Envía un email usando SMTP.

        Args:
            to: Email del destinatario
            subject: Asunto del email
            body: Cuerpo del email en texto plano
            html_body: Cuerpo del email en HTML (opcional)
            attachments: Lista de archivos adjuntos (opcional)
            cc: Email con copia (opcional)

        Returns:
            True si se envió exitosamente
        """
        if not self.host or not self.from_email:
            logger.warning(
                "[yellow]SMTP not configured. Logging email instead:[/yellow]\n"
                f"[cyan]To:[/cyan] {to}\n"
                f"[cyan]Subject:[/cyan] {subject}\n"
                f"[cyan]Body:[/cyan] {body}"
            )
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to
            if cc:
                msg["Cc"] = cc

            # Agregar texto plano
            text_part = MIMEText(body, "plain")
            msg.attach(text_part)

            # Agregar HTML si está disponible
            if html_body:
                html_part = MIMEText(html_body, "html")
                msg.attach(html_part)

            # Agregar adjuntos
            if attachments:
                for attachment in attachments:
                    part = MIMEApplication(attachment.content, Name=attachment.filename)
                    part["Content-Disposition"] = f'attachment; filename="{attachment.filename}"'
                    msg.attach(part)

            # Enviar email
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"[green]✓[/green] Email sent successfully to [cyan]{to}[/cyan] via SMTP")
            return True

        except Exception as e:
            logger.error(f"[red]✗[/red] Error sending email via SMTP: [yellow]{str(e)}[/yellow]")
            return False


class APIEmailService(IEmailService):
    """Servicio de email usando API (SendGrid, Mailgun, etc)."""

    def __init__(self):
        """Inicializa el servicio de API de email."""
        self.api_url = settings.EMAIL_API_URL
        self.api_key = settings.EMAIL_API_KEY
        self.api_key_header = settings.EMAIL_API_KEY_HEADER
        self.from_email = settings.EMAIL_FROM_EMAIL
        self.from_name = settings.EMAIL_FROM_NAME
        self.timeout = 30.0

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
        Envía un email usando API.

        Args:
            to: Email del destinatario
            subject: Asunto del email
            body: Cuerpo del email en texto plano
            html_body: Cuerpo del email en HTML (opcional)
            attachments: Lista de archivos adjuntos (opcional)
            cc: Email con copia (opcional)

        Returns:
            True si se envió exitosamente
        """
        if not self.api_url or not self.from_email:
            logger.warning(
                f"Email API not configured. Logging email instead:\n"
                f"To: {to}\nSubject: {subject}\nBody: {body}"
            )
            return True

        try:
            headers = {
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers[self.api_key_header] = self.api_key

            payload: dict[str, Any] = {
                "to": to,
                "from": f"{self.from_name} <{self.from_email}>",
                "subject": subject,
                "text": body,
            }
            if html_body:
                payload["html"] = html_body
            if cc:
                payload["cc"] = cc

            # Adjuntos: codificar en base64 si la API lo soporta
            if attachments:
                payload["attachments"] = [
                    {
                        "filename": att.filename,
                        "content": base64.b64encode(att.content).decode("utf-8"),
                        "mime_type": att.mime_type,
                    }
                    for att in attachments
                ]

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()

            logger.info(f"[green]✓[/green] Email sent successfully to [cyan]{to}[/cyan] via API")
            return True

        except httpx.HTTPStatusError as e:
            logger.error(
                f"[red]✗[/red] Email API HTTP error [yellow]{e.response.status_code}[/yellow]: "
                f"[yellow]{e.response.text}[/yellow]"
            )
            return False
        except Exception as e:
            logger.error(f"[red]✗[/red] Error sending email via API: [yellow]{str(e)}[/yellow]")
            return False


class LoggingEmailService(IEmailService):
    """Servicio de email que solo loguea (para desarrollo)."""

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
        Loguea el email en lugar de enviarlo (para desarrollo).

        Args:
            to: Email del destinatario
            subject: Asunto del email
            body: Cuerpo del email en texto plano
            html_body: Cuerpo del email en HTML (opcional)
            attachments: Lista de archivos adjuntos (opcional)
            cc: Email con copia (opcional)

        Returns:
            Siempre True (simula éxito)
        """
        attachment_info = ""
        if attachments:
            attachment_info = "\n".join(
                f"  [cyan]Attachment:[/cyan] {att.filename} ({len(att.content)} bytes, {att.mime_type})"
                for att in attachments
            )

        cc_info = f"\n[cyan]CC:[/cyan] {cc}" if cc else ""
        logger.info(
            "[dim]Email (logged, not sent):[/dim]\n"
            f"[cyan]To:[/cyan] {to}{cc_info}\n"
            f"[cyan]Subject:[/cyan] {subject}\n"
            f"[cyan]Body:[/cyan] {body}\n"
            f"[cyan]HTML Body:[/cyan] {html_body if html_body else '[dim]N/A[/dim]'}\n"
            f"{attachment_info}"
        )
        return True

