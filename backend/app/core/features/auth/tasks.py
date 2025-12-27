"""
Celery tasks para el feature de Auth.
Tasks relacionadas con autenticación (envío de emails, etc).
"""
import logging
import asyncio

from app.core.tasks.celery_app import celery_app
from app.shared.services.email_service_factory import get_email_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(
    self,
    to: str,
    subject: str,
    body: str,
    html_body: str | None = None,
) -> dict:
    """
    Envía un email en background usando Celery.
    
    La tarea tiene retries automáticos con exponential backoff para garantizar
    que los emails se envíen incluso si hay fallos temporales.
    
    Args:
        to: Email del destinatario
        subject: Asunto del email
        body: Cuerpo del email en texto plano
        html_body: Cuerpo del email en HTML (opcional)
        
    Returns:
        Dict con el resultado del envío
        
    Raises:
        Retry si falla por error temporal (network, timeout, etc)
    """
    try:
        logger.info(
            f"Sending email to {to} with subject '{subject}' "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1})"
        )
        
        # Obtener servicio de email
        email_service = get_email_service()
        
        # Ejecutar async call en sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                email_service.send_email(
                    to=to,
                    subject=subject,
                    body=body,
                    html_body=html_body,
                )
            )
            
            if result:
                logger.info(f"Email sent successfully to {to}")
                return {"success": True, "to": to, "subject": subject}
            else:
                logger.warning(f"Email sending returned False for {to}")
                # Reintentar si falló
                raise Exception("Email sending returned False")
        except Exception as email_error:
            # Si el servicio de email lanzó una excepción, la propagamos
            # para que Celery pueda hacer retry
            logger.error(f"Email service raised exception: {str(email_error)}")
            raise
            
    except Exception as e:
        # Reintentar en caso de error
        logger.warning(
            f"Error sending email to {to} (attempt {self.request.retries + 1}): {str(e)}"
        )
        
        # Si ya alcanzamos el máximo de reintentos, registrar el error pero no fallar
        if self.request.retries >= self.max_retries:
            logger.error(
                f"Failed to send email to {to} after {self.max_retries + 1} attempts: {str(e)}",
                exc_info=True
            )
            return {"success": False, "to": to, "error": str(e)}
        
        # Reintentar con exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)

