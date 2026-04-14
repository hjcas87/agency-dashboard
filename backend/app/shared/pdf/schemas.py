"""
Pydantic schemas for PDF templates.
"""
from pydantic import BaseModel, Field


class PdfTemplateCreate(BaseModel):
    """Schema for creating a PDF template."""

    logo_url: str | None = None
    header_text: str | None = None
    footer_text: str | None = None
    bg_color: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    text_color: str = Field(default="#1a1a1a", pattern=r"^#[0-9a-fA-F]{6}$")
    accent_color: str = Field(default="#2563eb", pattern=r"^#[0-9a-fA-F]{6}$")
    is_default: bool = False


class PdfTemplateUpdate(BaseModel):
    """Schema for updating a PDF template."""

    logo_url: str | None = None
    header_text: str | None = None
    footer_text: str | None = None
    bg_color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    text_color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    accent_color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    is_default: bool | None = None


class PdfTemplateResponse(BaseModel):
    """Schema returned for a PDF template."""

    id: int
    logo_url: str | None
    header_text: str | None
    footer_text: str | None
    bg_color: str
    text_color: str
    accent_color: str
    is_default: bool

    class Config:
        from_attributes = True
