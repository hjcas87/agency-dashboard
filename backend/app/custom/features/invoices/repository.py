"""Data-access layer for the Invoice feature."""
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.custom.features.invoices.models import Invoice


class InvoiceRepository:
    """Thin wrapper around SQLAlchemy queries for `Invoice`."""

    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Invoice]:
        return self.db.query(Invoice).order_by(Invoice.issue_date.desc(), Invoice.id.desc()).all()

    def get(self, invoice_id: int) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def invoiced_amount_for_proposal(self, proposal_id: int) -> Decimal:
        """Sum of every active (non-cancelled) Invoice tied to a
        proposal. Cancelled invoices drop out automatically (their
        `cancelled_at` is set when an NC is emitted), so anulación
        instantly returns capacity to the proposal. NCs themselves
        don't carry a `proposal_id` — they live in their own row with
        only `cancels_invoice_id` set — so they don't double-count."""
        result = (
            self.db.query(func.coalesce(func.sum(Invoice.total_amount_ars), 0))
            .filter(
                Invoice.proposal_id == proposal_id,
                Invoice.cancelled_at.is_(None),
            )
            .scalar()
        )
        return Decimal(result or 0)

    def add(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
