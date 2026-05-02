"""
Unit tests for ActivityService covering CRUD, done_at toggle, and reorder.
"""
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.custom.features.activities.constants import ActivityOrigin
from app.custom.features.activities.models import Activity
from app.custom.features.activities.schemas import (
    ActivityCreate,
    ActivityUpdate,
    ReorderRequest,
)
from app.custom.features.activities.service import ActivityService
from app.core.features.users.models import User


def _make_user(user_id: int = 1) -> User:
    user = MagicMock(spec=User)
    user.id = user_id
    user.name = "Test User"
    return user


def _make_activity(
    activity_id: int = 1,
    title: str = "Test Activity",
    origin: ActivityOrigin = ActivityOrigin.MANUAL,
    done_at: datetime | None = None,
) -> Activity:
    activity = MagicMock(spec=Activity)
    activity.id = activity_id
    activity.title = title
    activity.description = None
    activity.due_date = None
    activity.due_at = None
    activity.assignee_id = None
    activity.created_by_id = 1
    activity.done_at = done_at
    activity.sort_order = 0
    activity.origin = origin
    activity.external_id = None
    activity.created_at = datetime(2026, 1, 1, tzinfo=UTC)
    activity.updated_at = datetime(2026, 1, 1, tzinfo=UTC)
    activity.assignee = None
    activity.created_by = None
    return activity


def _make_service(activity: Activity | None = None) -> tuple[ActivityService, MagicMock]:
    db = MagicMock()
    svc = ActivityService(db)
    svc.repository = MagicMock()
    if activity:
        svc.repository.get.return_value = activity
        svc.repository.create.return_value = activity
        svc.repository.update.return_value = activity
    return svc, db


@pytest.mark.unit
class TestActivityService:
    def test_create_activity_sets_created_by(self):
        activity = _make_activity()
        svc, _ = _make_service(activity)
        user = _make_user(user_id=42)

        result = svc.create_activity(
            ActivityCreate(title="Nueva actividad"),
            current_user=user,
        )

        call_args = svc.repository.create.call_args[0][0]
        assert call_args["created_by_id"] == 42

    def test_update_activity_changes_title(self):
        activity = _make_activity(title="Old title")
        svc, _ = _make_service(activity)

        svc.update_activity(1, ActivityUpdate(title="New title"))

        update_data = svc.repository.update.call_args[0][1]
        assert update_data["title"] == "New title"

    def test_mark_done_sets_done_at(self):
        activity = _make_activity(done_at=None)
        svc, _ = _make_service(activity)

        svc.update_activity(1, ActivityUpdate(done_at=datetime.now(UTC)))

        update_data = svc.repository.update.call_args[0][1]
        assert update_data["done_at"] is not None

    def test_delete_calls_repository(self):
        activity = _make_activity()
        svc, _ = _make_service(activity)

        svc.delete_activity(1)

        svc.repository.delete.assert_called_once_with(activity)

    def test_list_show_done_false_by_default(self):
        svc, _ = _make_service()
        svc.repository.list.return_value = []

        svc.list_activities(show_done=False)

        svc.repository.list.assert_called_once()
        kwargs = svc.repository.list.call_args[1]
        assert kwargs["show_done"] is False

    def test_list_show_done_true(self):
        svc, _ = _make_service()
        svc.repository.list.return_value = []

        svc.list_activities(show_done=True)

        kwargs = svc.repository.list.call_args[1]
        assert kwargs["show_done"] is True

    def test_reorder_calls_bulk_update(self):
        svc, _ = _make_service()

        svc.reorder_activities(ReorderRequest(ids=[3, 1, 2]))

        svc.repository.bulk_update_sort_order.assert_called_once_with([3, 1, 2])
