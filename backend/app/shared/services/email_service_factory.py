"""
Factory para obtener el servicio de email apropiado.
"""
import logging

from app.config import settings
from app.shared.interfaces.email_service import IEmailService
from app.shared.services.email_service import APIEmailService, LoggingEmailService, SMTPEmailService

logger = logging.getLogger(__name__)


def get_email_service() -> IEmailService:
    """
    Obtiene el servicio de email apropiado según la configuración.

    Returns:
        Instancia del servicio de email configurado
    """
    provider = settings.EMAIL_PROVIDER.lower()

    if provider == "smtp":
        # Verificar si SMTP está configurado
        if settings.SMTP_HOST and settings.SMTP_FROM_EMAIL:
            return SMTPEmailService()
        else:
            logger.warning("[yellow]⚠[/yellow] SMTP not fully configured, using logging service")
            return LoggingEmailService()
    elif provider == "api":
        # Verificar si API está configurada
        if settings.EMAIL_API_URL and settings.EMAIL_FROM_EMAIL:
            return APIEmailService()
        else:
            logger.warning(
                "[yellow]⚠[/yellow] Email API not fully configured, using logging service"
            )
            return LoggingEmailService()
    else:
        # Por defecto, usar servicio de logging (desarrollo)
        return LoggingEmailService()
