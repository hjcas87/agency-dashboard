"""Data-access layer for the Invoice feature."""
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

    def get_by_proposal(self, proposal_id: int) -> Invoice | None:
        """Returns the latest invoice for a given proposal, or None.
        Used to flag proposals as already-invoiced in the billable list."""
        return (
            self.db.query(Invoice)
            .filter(Invoice.proposal_id == proposal_id)
            .order_by(Invoice.id.desc())
            .first()
        )

    def invoiced_proposal_ids(self) -> set[int]:
        """All proposal_ids that already have at least one invoice."""
        rows = (
            self.db.query(Invoice.proposal_id)
            .filter(Invoice.proposal_id.isnot(None))
            .distinct()
            .all()
        )
        return {row[0] for row in rows if row[0] is not None}

    def add(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
