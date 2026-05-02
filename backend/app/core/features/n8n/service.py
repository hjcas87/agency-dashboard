"""
Service layer para el feature de N8N.
"""
import logging
from typing import Any

from app.core.features.n8n.tasks import trigger_n8n_workflow
from app.shared.constants import N8N_MESSAGES, N8N_STATUS, TASK_STATE
from app.shared.services.n8n_service import N8NService

logger = logging.getLogger(__name__)


class N8NFeatureService:
    """Service para manejar workflows de N8N."""

    def __init__(self, n8n_service: N8NService):
        """
        Inicializa el service.

        Args:
            n8n_service: Instancia del servicio N8N
        """
        self.n8n_service = n8n_service

    async def trigger_workflow_async(
        self,
        webhook_path: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Dispara un workflow de N8N de forma asíncrona usando Celery.

        Args:
            webhook_path: Path del webhook configurado en N8N (ej: "my-webhook" o workflow ID si está configurado como path)
            payload: Datos para el workflow

        Returns:
            Información de la tarea creada
        """

        # Encolar tarea en Celery
        task = trigger_n8n_workflow.delay(
            webhook_path=webhook_path,
            payload=payload,
        )

        return {
            "task_id": task.id,
            "status": N8N_STATUS["QUEUED"],
            "message": N8N_MESSAGES["queued"],
        }

    async def trigger_workflow_sync(
        self,
        webhook_path: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Dispara un workflow de N8N de forma síncrona.

        Args:
            webhook_path: Path del webhook configurado en N8N (ej: "my-webhook" o workflow ID si está configurado como path)
            payload: Datos para el workflow

        Returns:
            Respuesta del workflow
        """
        return await self.n8n_service.trigger_workflow(
            webhook_path=webhook_path,
            payload=payload,
        )

    def get_task_status(self, task_id: str) -> dict[str, Any]:
        """
        Obtiene el estado de una tarea Celery.

        Args:
            task_id: ID de la tarea

        Returns:
            Estado de la tarea
        """
        from app.core.tasks.celery_app import celery_app

        task = celery_app.AsyncResult(task_id)

        if task.state == TASK_STATE["PENDING"]:
            return {
                "task_id": task_id,
                "state": task.state,
                "status": N8N_MESSAGES["pending_desc"],
            }
        elif task.state == TASK_STATE["SUCCESS"]:
            return {
                "task_id": task_id,
                "state": task.state,
                "result": task.result,
            }
        else:
            return {
                "task_id": task_id,
                "state": task.state,
                "error": str(task.info) if task.info else N8N_MESSAGES["unknown_error"],
            }
