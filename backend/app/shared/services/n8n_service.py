"""
Wrapper para el servicio N8N.
"""
import logging
from typing import Any

import httpx

from app.config import settings
from app.shared.constants import CONTENT_TYPE_JSON, HEADER_CONTENT_TYPE, N8N_STATUS
from app.shared.interfaces.external_service import IExternalService

logger = logging.getLogger(__name__)


class N8NService(IExternalService):
    """Wrapper para interactuar con N8N."""

    def __init__(self):
        """Inicializa el servicio N8N."""
        # N8N_BASE_URL es la base (ej: http://n8n:5678)
        # Construimos la URL base para webhooks
        self.base_url = settings.N8N_BASE_URL.rstrip("/")
        self.timeout = 30.0
        self.api_key = settings.N8N_API_KEY
        self.api_key_header = settings.N8N_API_KEY_HEADER

    async def call(
        self,
        endpoint: str,
        method: str = "POST",
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Realiza una llamada a N8N.

        Args:
            endpoint: Endpoint de N8N (ej: /workflow-id)
            method: Método HTTP
            payload: Datos a enviar
            headers: Headers HTTP adicionales
        """
        # Construir URL evitando doble barra
        base = self.base_url.rstrip("/")
        endpoint_clean = endpoint.lstrip("/")
        url = f"{base}/{endpoint_clean}" if endpoint_clean else base
        default_headers = {
            HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
        }
        # Agregar API key en header si está configurado (para Header Auth en N8N)
        if self.api_key:
            default_headers[self.api_key_header] = self.api_key
        if headers:
            default_headers.update(headers)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=payload or {},
                    headers=default_headers,
                )
                response.raise_for_status()

                result = {
                    "status": N8N_STATUS["SUCCESS"],
                    "status_code": response.status_code,
                    "data": response.json() if response.content else None,
                }

                logger.info(f"N8N call successful: {endpoint}")
                return result

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if e.response.text else "No error details"
            if e.response.status_code == 404:
                logger.error(
                    f"N8N 404 error: Webhook not found at {url}. "
                    f"Make sure: 1) The workflow is activated in N8N, "
                    f"2) The webhook path matches exactly. Error: {error_detail}"
                )
            else:
                logger.error(f"N8N HTTP error {e.response.status_code}: {error_detail}")
            raise
        except httpx.RequestError as e:
            logger.error(f"N8N request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling N8N: {str(e)}")
            raise

    async def trigger_workflow(
        self,
        webhook_path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Dispara un workflow de N8N vía webhook.

        Args:
            webhook_path: Path del webhook (ej: "my-webhook" o "webhook-test/348b0e40-cbbc-4146-97ad-e21d7b145ea9")
                         Este es el path configurado en el nodo Webhook de N8N, puede incluir
                         paths personalizados como "webhook-test/..." o solo el ID del workflow.
                         NO el workflow ID.
            payload: Datos para el workflow
        """
        # Remover barra inicial si existe
        webhook_path = webhook_path.lstrip("/")
        # Construir endpoint: el webhook_path ya incluye el path completo después del dominio
        # Ejemplo: si webhook_path es "webhook-test/348b0e40-...", la URL será
        # http://n8n:5678/webhook-test/348b0e40-...
        endpoint = f"/{webhook_path}"
        return await self.call(endpoint=endpoint, method="POST", payload=payload)

    def health_check(self) -> bool:
        """Verifica la salud de N8N."""
        try:
            import asyncio

            response = asyncio.run(self.call(endpoint="/healthz", method="GET"))
            return response.get("status") == N8N_STATUS["SUCCESS"]
        except Exception:
            return False
