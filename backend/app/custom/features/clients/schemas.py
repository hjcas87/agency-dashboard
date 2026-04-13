"""
Pydantic schemas for the Client feature.
"""
from pydantic import BaseModel, EmailStr


class ClientCreate(BaseModel):
    """Schema for creating a new client."""

    name: str
    company: str | None = None
    email: EmailStr
    phone: str | None = None


class ClientUpdate(BaseModel):
    """Schema for updating an existing client."""

    name: str | None = None
    company: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class ClientResponse(BaseModel):
    """Schema returned for client operations."""

    id: int
    name: str
    company: str | None
    email: str
    phone: str | None

    class Config:
        from_attributes = True
