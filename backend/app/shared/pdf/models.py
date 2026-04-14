"""
PDF Template SQLAlchemy model.

Kept in a separate file to avoid importing weasyprint when Alembic loads models.
"""
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class PdfTemplate(Base):
    """PDF template configuration for document generation."""

    __tablename__ = "pdf_templates"

    id = Column(Integer, primary_key=True, index=True)
    logo_url = Column(String(500), nullable=True)
    header_text = Column(Text, nullable=True)
    footer_text = Column(Text, nullable=True)
    bg_color = Column(String(7), nullable=False, server_default="#ffffff")
    text_color = Column(String(7), nullable=False, server_default="#1a1a1a")
    accent_color = Column(String(7), nullable=False, server_default="#2563eb")
    is_default = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<PdfTemplate(id={self.id}, is_default={self.is_default})>"
