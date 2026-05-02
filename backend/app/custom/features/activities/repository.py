from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.custom.features.activities.constants import ActivityOrigin
from app.custom.features.activities.models import Activity


def _week_bounds() -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    monday = now.replace(hour=0, minute=0, second=0, microsecond=0)
    monday = monday - timedelta(days=monday.weekday())
    sunday = monday + timedelta(days=7)
    return monday, sunday


class ActivityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return self.db.query(Activity).options(
            joinedload(Activity.assignee),
            joinedload(Activity.created_by),
        )

    def list(
        self,
        assignee_id: int | None = None,
        show_done: bool = False,
        week_current: bool = False,
        origin: ActivityOrigin | None = None,
    ) -> list[Activity]:
        q = self._base_query()

        if assignee_id is not None:
            q = q.filter(Activity.assignee_id == assignee_id)

        if not show_done:
            q = q.filter(Activity.done_at.is_(None))

        if week_current:
            start, end = _week_bounds()
            q = q.filter(
                and_(Activity.due_date >= start.date(), Activity.due_date < end.date())
            )

        if origin is not None:
            q = q.filter(Activity.origin == origin)

        return q.order_by(Activity.sort_order.asc(), Activity.created_at.asc()).all()

    def get(self, activity_id: int) -> Activity | None:
        return self._base_query().filter(Activity.id == activity_id).first()

    def create(self, data: dict) -> Activity:
        activity = Activity(**data)
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return self.get(activity.id)  # type: ignore[return-value]

    def update(self, activity: Activity, data: dict) -> Activity:
        for field, value in data.items():
            setattr(activity, field, value)
        self.db.commit()
        self.db.refresh(activity)
        return self.get(activity.id)  # type: ignore[return-value]

    def delete(self, activity: Activity) -> None:
        self.db.delete(activity)
        self.db.commit()

    def bulk_update_sort_order(self, ids: list[int]) -> None:
        for position, activity_id in enumerate(ids):
            self.db.query(Activity).filter(Activity.id == activity_id).update(
                {"sort_order": position}
            )
        self.db.commit()
