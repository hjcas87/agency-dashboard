"""
Celery tasks para N8N workflow execution.
Usa el wrapper de N8N service para mejor abstracción.
"""
import logging
import asyncio
from typing import Any

import httpx

from app.core.tasks.celery_app import celery_app
from app.shared.services.n8n_service import N8NService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def trigger_n8n_workflow(
    self,
    webhook_path: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Trigger an N8N workflow via webhook en background.
    Usa el N8NService wrapper para mejor abstracción.
    
    La tarea tiene retries automáticos con exponential backoff para garantizar
    que los workflows se ejecuten incluso si hay fallos temporales.
    
    Args:
        webhook_path: Path del webhook configurado en N8N (ej: "my-webhook" o "webhook-test/path")
                     Este es el path configurado en el nodo Webhook de N8N, NO incluye el dominio.
        payload: Data to send to the webhook
        
    Returns:
        Response from N8N webhook
        
    Raises:
        Retry si falla por error temporal (network, timeout, etc)
    """
    if payload is None:
        payload = {}
    
    try:
        logger.info(
            f"Triggering N8N workflow: {webhook_path} (attempt {self.request.retries + 1}/{self.max_retries + 1})"
        )
        
        # Usar el servicio N8N (async call en sync context)
        n8n_service = N8NService()

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            n8n_service.trigger_workflow(
                webhook_path=webhook_path,
                payload=payload,
            )
        )
        
        logger.info(
            f"N8N workflow completed successfully: {webhook_path}, status: {result.get('status', 'unknown')}"
        )
        return result
        
    except (httpx.RequestError, httpx.TimeoutException) as e:
        # Errores de red/timeout - reintentar
        logger.warning(
            f"Network error triggering N8N workflow (attempt {self.request.retries + 1}): {str(e)}"
        )
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
        
    except httpx.HTTPStatusError as e:
        # Errores HTTP (4xx, 5xx) - solo reintentar si es 5xx (error del servidor)
        if e.response.status_code >= 500:
            logger.warning(
                f"Server error triggering N8N workflow (attempt {self.request.retries + 1}): "
                f"{e.response.status_code} - {str(e)}"
            )
            raise self.retry(exc=e, countdown=2 ** self.request.retries)
        else:
            # Errores 4xx (client errors) - no reintentar
            logger.error(
                f"Client error triggering N8N workflow (will not retry): "
                f"{e.response.status_code} - {str(e)}"
            )
            raise
        
    except ValueError as e:
        # Errores de validación - no reintentar
        logger.error(f"Validation error (will not retry): {str(e)}")
        raise
        
    except Exception as e:
        # Otros errores inesperados - reintentar
        logger.error(
            f"Unexpected error triggering N8N workflow (attempt {self.request.retries + 1}): {str(e)}",
            exc_info=True
        )
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
