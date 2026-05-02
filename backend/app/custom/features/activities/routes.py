from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.features.auth.dependencies import get_current_user
from app.core.features.users.models import User
from app.custom.features.activities.schemas import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    ReorderRequest,
)
from app.custom.features.activities.service import ActivityService
from app.database import get_db

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("", response_model=list[ActivityResponse])
def list_activities(
    assignee_id: int | None = None,
    show_done: bool = False,
    week: str | None = None,
    origin: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ActivityResponse]:
    svc = ActivityService(db)
    return svc.list_activities(
        assignee_id=assignee_id,
        show_done=show_done,
        week_current=(week == "current"),
        origin=origin,
    )


@router.post("", response_model=ActivityResponse, status_code=201)
def create_activity(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActivityResponse:
    svc = ActivityService(db)
    return svc.create_activity(data, current_user)


@router.patch("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActivityResponse:
    svc = ActivityService(db)
    return svc.update_activity(activity_id, data)


@router.delete("/{activity_id}", status_code=204)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    svc = ActivityService(db)
    svc.delete_activity(activity_id)


@router.post("/reorder", status_code=204)
def reorder_activities(
    data: ReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    svc = ActivityService(db)
    svc.reorder_activities(data)
