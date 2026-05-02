"""SQLAlchemy model for the Invoice feature.

`Invoice` is the agency's persistent business entity for an electronic
invoice. It holds:
- An optional FK to the originating proposal (NULL when issued
  manually without a quote).
- An FK to the client being invoiced.
- An FK to `afip_invoice_log` — the audit row owned by `shared/afip`
  with the raw request/response and the CAE. Lifecycle of that row is
  out of our hands; we just point at it.

The line items are stored as JSONB so the manual-invoice flow can
freely add lines without a separate table. For invoices coming from
a proposal we still snapshot the lines here at the moment of issuance,
so the invoice stays auditable even if the proposal changes later.
"""
from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Invoice(Base):
    """Persistent business invoice — links a proposal (optional) and a
    client to the AFIP audit row that holds the CAE."""

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Business context
    proposal_id: Mapped[int | None] = mapped_column(
        ForeignKey("proposals.id", ondelete="SET NULL"), nullable=True, index=True
    )
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # ARCA audit reference. RESTRICT — never delete the AFIP log if a
    # business invoice points at it. Nullable because internal receipts
    # ("Comprobante interno X") never reach AFIP and therefore have no
    # log row to link.
    afip_invoice_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("afip_invoice_log.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    # Internal receipts are local-only — same flow / table / PDF as a
    # real Factura, but they don't go through AFIP, don't carry CAE,
    # and the printed PDF carries the letter "X" plus a "no válido como
    # factura" disclaimer. Used for non-billable work (internal control,
    # cost-share between partners, etc.). `internal_number` is a global
    # auto-incrementing counter assigned at issuance time.
    is_internal: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    internal_number: Mapped[int | None] = mapped_column(nullable=True, index=True)

    # Snapshot of the receipt that was issued. For internal receipts
    # `receipt_type` is 0 — the renderer keys off `is_internal` and the
    # field is just preserved for forward compatibility.
    receipt_type: Mapped[int] = mapped_column(nullable=False)  # ARCA CbteTipo
    concept: Mapped[int] = mapped_column(nullable=False)  # 1=products, 2=services, 3=both
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    service_date_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    service_date_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_amount_ars: Mapped[Any] = mapped_column(Numeric(13, 2), nullable=False)

    # Receiver document — what was actually sent to AFIP. Both nullable
    # because internal receipts have no AFIP-side identification.
    # `document_number` uses BigInteger because a CUIT is 11 digits
    # (max 99,999,999,999) which overflows a 32-bit INT.
    document_type: Mapped[int | None] = mapped_column(nullable=True)
    document_number: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Snapshot of line items as JSONB. Each entry is
    # `{"name": str, "amount": str}` — Decimal is preserved as str so
    # round-trip JSON does not lose precision.
    line_items: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")

    commercial_reference: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Internal-only soft cancellation. AFIP receipts are NEVER cancelled
    # this way — they require a Nota de Crédito issued through ARCA,
    # tracked as a separate Invoice row. For internal X comprobantes
    # `cancelled_at` flips to "now()" and the row stays visible (struck
    # through in the UI) so the operator keeps the audit trail.
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Invoice(id={self.id}, client_id={self.client_id}, "
            f"receipt_type={self.receipt_type}, total={self.total_amount_ars})>"
        )
