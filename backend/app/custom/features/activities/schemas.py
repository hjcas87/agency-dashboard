from datetime import date, datetime

from pydantic import BaseModel, Field


class UserMini(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    due_at: datetime | None = None
    assignee_id: int | None = None


class ActivityUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    due_at: datetime | None = None
    assignee_id: int | None = None
    done_at: datetime | None = None


class ActivityResponse(BaseModel):
    id: int
    title: str
    description: str | None
    due_date: date | None
    due_at: datetime | None
    assignee_id: int | None
    created_by_id: int | None
    done_at: datetime | None
    sort_order: int
    origin: str
    external_id: str | None
    created_at: datetime
    updated_at: datetime
    assignee: UserMini | None = None
    created_by: UserMini | None = None

    class Config:
        from_attributes = True


class ReorderRequest(BaseModel):
    ids: list[int] = Field(..., min_length=1)


class SyncResponse(BaseModel):
    synced: int
    created: int
    updated: int
    removed: int
    last_sync_at: datetime
