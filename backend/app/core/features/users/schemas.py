"""
Schemas para el feature de Users.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Schema base para User."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


class UserCreate(UserBase):
    """Schema para crear un User."""

    pass


class UserUpdate(BaseModel):
    """Schema para actualizar un User."""

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema de respuesta para User."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema de respuesta para lista de Users."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
