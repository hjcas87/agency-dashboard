"""
Routes para el feature de health check.
"""
from fastapi import APIRouter, Depends

from app.shared.services.n8n_service import N8NService
from app.core.features.health.service import HealthFeatureService
from app.core.features.health.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


def get_health_service(
    n8n_service: N8NService = Depends(lambda: N8NService()),
) -> HealthFeatureService:
    """Dependency para obtener el health service."""
    return HealthFeatureService(n8n_service)


@router.get("", response_model=HealthResponse)
async def health_check(
    service: HealthFeatureService = Depends(get_health_service),
):
    """
    Health check endpoint.
    """
    result = service.check_health()
    return HealthResponse(**result)

