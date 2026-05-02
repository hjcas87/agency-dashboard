"""
Implementación del servicio de email.
Soporta SMTP y APIs de email (SendGrid, Mailgun, etc).
"""
import asyncio
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

# Implicit-SSL ports — these require smtplib.SMTP_SSL from the start.
# 587 / 25 / 2525 negotiate STARTTLS over a plain SMTP connection instead.
_IMPLICIT_SSL_PORTS = {465}


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
        self.timeout = settings.SMTP_TIMEOUT_SECONDS

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
            True si se envió exitosamente, False en cualquier fallo
            (timeout, autenticación, TLS handshake, etc).
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
            message = self._build_message(
                to=to,
                subject=subject,
                body=body,
                html_body=html_body,
                attachments=attachments,
                cc=cc,
            )
            # smtplib is sync. Running it directly inside an async handler
            # blocks the event loop for the entire SMTP session — and on a
            # broken/unreachable host it would block forever. asyncio.to_thread
            # offloads the call so the loop keeps serving other requests, and
            # the `timeout=` argument on the smtplib constructor caps the
            # blocking time.
            await asyncio.to_thread(self._send_blocking, to, message)
            logger.info(f"[green]✓[/green] Email sent successfully to [cyan]{to}[/cyan] via SMTP")
            return True

        except (TimeoutError, OSError) as exc:
            logger.error(
                f"[red]✗[/red] SMTP connection to [cyan]{self.host}:{self.port}[/cyan] "
                f"timed out or refused: [yellow]{exc}[/yellow]"
            )
            return False
        except smtplib.SMTPAuthenticationError as exc:
            logger.error(f"[red]✗[/red] SMTP authentication failed: [yellow]{exc}[/yellow]")
            return False
        except smtplib.SMTPException as exc:
            logger.error(f"[red]✗[/red] SMTP error: [yellow]{exc}[/yellow]")
            return False
        except Exception as exc:
            # Catch-all kept narrow: log with traceback so unknown failures
            # do not get silently swallowed (legacy behavior).
            logger.exception(f"[red]✗[/red] Unexpected error sending email via SMTP: {exc}")
            return False

    # ------------------------------------------------------------------ helpers

    def _build_message(
        self,
        *,
        to: str,
        subject: str,
        body: str,
        html_body: str | None,
        attachments: list[Attachment] | None,
        cc: str | None,
    ) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to
        if cc:
            msg["Cc"] = cc
        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))
        for attachment in attachments or []:
            part = MIMEApplication(attachment.content, Name=attachment.filename)
            part["Content-Disposition"] = f'attachment; filename="{attachment.filename}"'
            msg.attach(part)
        return msg

    def _send_blocking(self, to: str, message: MIMEMultipart) -> None:
        """Sync SMTP delivery — runs inside `asyncio.to_thread`. Picks
        SMTP_SSL for implicit-SSL ports (465) and plain SMTP+STARTTLS
        for the rest."""
        client_cls = smtplib.SMTP_SSL if self.port in _IMPLICIT_SSL_PORTS else smtplib.SMTP
        with client_cls(self.host, self.port, timeout=self.timeout) as server:
            # STARTTLS only applies to plain-SMTP connections that were
            # created without implicit SSL.
            if self.use_tls and client_cls is smtplib.SMTP:
                server.starttls()
            if self.username and self.password:
                server.login(self.username, self.password)
            server.send_message(message)


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
