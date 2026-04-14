"""
Pydantic schemas for Email Templates.
"""
from pydantic import BaseModel, Field


class EmailTemplateCreate(BaseModel):
    """Schema for creating an email template."""

    name: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    is_default: bool = False


class EmailTemplateUpdate(BaseModel):
    """Schema for updating an email template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    subject: str | None = Field(None, min_length=1, max_length=500)
    body: str | None = Field(None, min_length=1)
    is_default: bool | None = None


class EmailTemplateResponse(BaseModel):
    """Schema returned for an email template."""

    id: int
    name: str
    subject: str
    body: str
    is_default: bool

    class Config:
        from_attributes = True


class EmailSendRequest(BaseModel):
    """Schema for sending an email."""

    to: str = Field(..., min_length=1)
    cc: str | None = None
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    html_body: str | None = None
    attach_proposal_pdf: int | None = None  # Proposal ID para adjuntar PDF


class EmailPreviewRequest(BaseModel):
    """Schema for previewing an email with variables rendered."""

    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    variables: dict[str, str] = Field(default_factory=dict)
