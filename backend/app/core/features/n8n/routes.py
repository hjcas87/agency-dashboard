"""
Routes para el feature de N8N.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.features.n8n.schemas import N8NTriggerRequest, N8NTriggerResponse, TaskStatusResponse
from app.core.features.n8n.service import N8NFeatureService
from app.database import get_db
from app.shared.services.n8n_service import N8NService

router = APIRouter(prefix="/n8n", tags=["Core: N8N"])


def get_n8n_service() -> N8NService:
    """Dependency para obtener el servicio N8N."""
    return N8NService()


def get_n8n_feature_service(
    n8n_service: N8NService = Depends(get_n8n_service),
) -> N8NFeatureService:
    """Dependency para obtener el feature service de N8N."""
    return N8NFeatureService(n8n_service)


@router.post("/trigger", response_model=N8NTriggerResponse)
async def trigger_workflow(
    request: N8NTriggerRequest,
    db: Session = Depends(get_db),
    service: N8NFeatureService = Depends(get_n8n_feature_service),
):
    """
    Dispara un workflow de N8N de forma asíncrona.
    """
    result = await service.trigger_workflow_async(
        webhook_path=request.webhook_path,
        payload=request.payload,
    )
    return N8NTriggerResponse(**result)


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    service: N8NFeatureService = Depends(get_n8n_feature_service),
):
    """
    Obtiene el estado de una tarea Celery.
    """
    result = service.get_task_status(task_id)
    return TaskStatusResponse(**result)
