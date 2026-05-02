"""SQLAlchemy models persisted by the AFIP/ARCA integration.

Two tables only:

- `afip_token` — cached WSAA TA. Short-lived rows (12 h TTL); a follow-up
  PR adds a Celery beat task to delete expired rows after a small audit
  window. **No business value in keeping history.**
- `afip_invoice_log` — one row per WSFEv1 attempt (success or failure).
  Audit-only. The consuming feature's business `Invoice` entity declares
  a FK pointing here; this side does not know about that.
"""
from sqlalchemy import Boolean, Column, Date, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.database import Base


class AfipToken(Base):
    """Cached WSAA Ticket de Acceso (TA) per service.

    The auth service looks up the most recent non-expired row for a given
    service before requesting a new one. ARCA TAs are valid for ~12 h."""

    __tablename__ = "afip_token"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(64), nullable=False, index=True)
    token = Column(Text, nullable=False)
    sign = Column(Text, nullable=False)
    generation_time = Column(DateTime(timezone=True), nullable=False)
    expiration_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_afip_token_service_expiration", "service", "expiration_time"),)

    def __repr__(self) -> str:
        return (
            f"<AfipToken(id={self.id}, service={self.service!r}, "
            f"expires_at={self.expiration_time.isoformat() if self.expiration_time else None})>"
        )


class AfipInvoiceLog(Base):
    """Audit row for every WSFEv1 authorization attempt.

    Persisted in both the success and the failure path so the operator
    can correlate ARCA's response with the in-app business entity. The
    business `Invoice` of the consuming feature references this table by
    FK; this table itself has no FKs into business tables."""

    __tablename__ = "afip_invoice_log"

    id = Column(Integer, primary_key=True, index=True)

    # Request side
    point_of_sale = Column(Integer, nullable=False)
    receipt_type = Column(Integer, nullable=False)
    request_xml = Column(Text, nullable=False)

    # Response side (nullable until ARCA replies)
    receipt_number = Column(Integer, nullable=True)
    cae = Column(String(32), nullable=True)
    cae_expiration = Column(Date, nullable=True)
    authorized_cbte_tipo = Column(Integer, nullable=True)
    response_xml = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False, server_default="false")
    observations = Column(JSONB, nullable=False, server_default="[]")
    errors = Column(JSONB, nullable=False, server_default="[]")

    issued_at = Column(
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
