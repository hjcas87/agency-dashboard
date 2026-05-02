from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.features.users.models import User
from app.custom.features.activities.constants import (
    ERR_MEETING_READONLY,
    ERR_NOT_FOUND,
    ActivityOrigin,
)
from app.custom.features.activities.repository import ActivityRepository
from app.custom.features.activities.schemas import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    ReorderRequest,
    UserMini,
)

_MEETING_EDITABLE_FIELDS = frozenset({"done_at", "sort_order", "assignee_id"})


def _to_response(activity) -> ActivityResponse:
    assignee = None
    if activity.assignee:
        assignee = UserMini(id=activity.assignee.id, name=activity.assignee.name)

    created_by = None
    if activity.created_by:
        created_by = UserMini(id=activity.created_by.id, name=activity.created_by.name)

    return ActivityResponse(
        id=activity.id,
        title=activity.title,
        description=activity.description,
        due_date=activity.due_date,
        due_at=activity.due_at,
        assignee_id=activity.assignee_id,
        created_by_id=activity.created_by_id,
        done_at=activity.done_at,
        sort_order=activity.sort_order,
        origin=activity.origin.value
        if isinstance(activity.origin, ActivityOrigin)
        else activity.origin,
        external_id=activity.external_id,
        created_at=activity.created_at,
        updated_at=activity.updated_at,
        assignee=assignee,
        created_by=created_by,
    )


class ActivityService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ActivityRepository(db)

    def list_activities(
        self,
        assignee_id: int | None = None,
        show_done: bool = False,
        week_current: bool = False,
        origin: str | None = None,
    ) -> list[ActivityResponse]:
        origin_enum = ActivityOrigin(origin) if origin else None
        activities = self.repository.list(
            assignee_id=assignee_id,
            show_done=show_done,
            week_current=week_current,
            origin=origin_enum,
        )
        return [_to_response(a) for a in activities]

    def create_activity(self, data: ActivityCreate, current_user: User) -> ActivityResponse:
        activity_data = data.model_dump()
        activity_data["created_by_id"] = current_user.id
        activity = self.repository.create(activity_data)
        return _to_response(activity)

    def update_activity(self, activity_id: int, data: ActivityUpdate) -> ActivityResponse:
        activity = self.repository.get(activity_id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)

        update_data = data.model_dump(exclude_unset=True)

        if activity.origin == ActivityOrigin.MEETING:
            forbidden = set(update_data.keys()) - _MEETING_EDITABLE_FIELDS
            if forbidden:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=ERR_MEETING_READONLY
                )

        if "done_at" in update_data:
            if update_data["done_at"] is True:
                update_data["done_at"] = datetime.now(UTC)
            elif update_data["done_at"] is False:
                update_data["done_at"] = None

        updated = self.repository.update(activity, update_data)
        return _to_response(updated)

    def delete_activity(self, activity_id: int) -> None:
        activity = self.repository.get(activity_id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)
        self.repository.delete(activity)

    def reorder_activities(self, data: ReorderRequest) -> None:
        self.repository.bulk_update_sort_order(data.ids)
