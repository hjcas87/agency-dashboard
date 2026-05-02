"""SQLAlchemy models persisted by the AFIP/ARCA integration.

Two tables only:

- `afip_token` — cached WSAA TA. Short-lived rows (12 h TTL); a follow-up
  PR adds a Celery beat task to delete expired rows after a small audit
  window. **No business value in keeping history.**
- `afip_invoice_log` — one row per WSFEv1 attempt (success or failure).
  Audit-only. The consuming feature's business `Invoice` entity declares
  a FK pointing here; this side does not know about that.

Uses SQLAlchemy 2.x `Mapped[...]` / `mapped_column(...)` declarations so
attribute access yields plain types (the legacy `Column(...)` style
yields `Column[T]` to type checkers, which forces casts at every read).
"""
from datetime import date, datetime
from typing import Any

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class AfipToken(Base):
    """Cached WSAA Ticket de Acceso (TA) per service.

    The auth service looks up the most recent non-expired row for a given
    service before requesting a new one. ARCA TAs are valid for ~12 h."""

    __tablename__ = "afip_token"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    sign: Mapped[str] = mapped_column(Text, nullable=False)
    generation_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiration_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_afip_token_service_expiration", "service", "expiration_time"),)

    def __repr__(self) -> str:
        expires = self.expiration_time.isoformat() if self.expiration_time else None
        return f"<AfipToken(id={self.id}, service={self.service!r}, expires_at={expires})>"


class AfipInvoiceLog(Base):
    """Audit row for every WSFEv1 authorization attempt.

    Persisted in both the success and the failure path so the operator
    can correlate ARCA's response with the in-app business entity. The
    business `Invoice` of the consuming feature references this table by
    FK; this table itself has no FKs into business tables."""

    __tablename__ = "afip_invoice_log"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Request side
    point_of_sale: Mapped[int] = mapped_column(nullable=False)
    receipt_type: Mapped[int] = mapped_column(nullable=False)
    request_xml: Mapped[str] = mapped_column(Text, nullable=False)

    # Response side (nullable until ARCA replies)
    receipt_number: Mapped[int | None] = mapped_column(nullable=True)
    cae: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cae_expiration: Mapped[date | None] = mapped_column(nullable=True)
    authorized_cbte_tipo: Mapped[int | None] = mapped_column(nullable=True)
    response_xml: Mapped[str | None] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    observations: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")
    errors: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        # Lookups by (point_of_sale, receipt_type, receipt_number) match how
        # consumers correlate a CAE back to the request — heaviest path.
        Index(
            "ix_afip_invoice_log_pos_type_number",
            "point_of_sale",
            "receipt_type",
            "receipt_number",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AfipInvoiceLog(id={self.id}, type={self.receipt_type}, "
            f"pos={self.point_of_sale}, number={self.receipt_number}, success={self.success})>"
        )
