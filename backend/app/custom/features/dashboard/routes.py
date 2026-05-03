"""HTTP routes for the dashboard feature."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.custom.features.dashboard.schemas import DashboardSummary
from app.custom.features.dashboard.service import DashboardService
from app.database import get_db

router = APIRouter(prefix="/dashboard", tags=["Custom: Dashboard"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSummary:
    """Single round-trip payload for the home dashboard — KPI cards
    plus the area chart series. Frontend renders directly from this."""
    return service.summary()
