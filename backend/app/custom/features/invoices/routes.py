"""HTTP routes for the Invoice feature."""
from collections.abc import Generator

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.custom.features.invoices.schemas import (
    BillableProposalResponse,
    InvoiceResponse,
    IssueFromProposalRequest,
    IssueManualRequest,
)
from app.custom.features.invoices.service import InvoiceService
from app.database import get_db
from app.shared.afip import AfipService, get_afip_service

router = APIRouter(prefix="/invoices", tags=["Custom: Invoices"])


def get_invoice_service(db: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(db)


def afip_dependency(db: Session = Depends(get_db)) -> Generator[AfipService, None, None]:
    yield from get_afip_service(db)


@router.get("/", response_model=list[InvoiceResponse])
def list_invoices(
    service: InvoiceService = Depends(get_invoice_service),
) -> list[InvoiceResponse]:
    """List every issued invoice."""
    return service.list_invoices()


@router.get("/billable-proposals", response_model=list[BillableProposalResponse])
def list_billable_proposals(
    service: InvoiceService = Depends(get_invoice_service),
) -> list[BillableProposalResponse]:
    """List proposals in ACCEPTED status that don't have an invoice yet."""
    return service.list_billable_proposals()


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceResponse:
    """Detail of a single issued invoice."""
    return service.get_invoice(invoice_id)


@router.post(
    "/from-proposal",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def issue_invoice_from_proposal(
    payload: IssueFromProposalRequest,
    service: InvoiceService = Depends(get_invoice_service),
    afip: AfipService = Depends(afip_dependency),
) -> InvoiceResponse:
    """Issue Factura C against AFIP for an accepted proposal."""
    return service.issue_from_proposal(payload, afip)


@router.post(
    "/manual",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def issue_invoice_manual(
    payload: IssueManualRequest,
    service: InvoiceService = Depends(get_invoice_service),
    afip: AfipService = Depends(afip_dependency),
) -> InvoiceResponse:
    """Issue Factura C against AFIP from a free-form line list."""
    return service.issue_manual(payload, afip)


@router.post("/{invoice_id}/cancel", response_model=InvoiceResponse)
def cancel_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceResponse:
    """Soft-cancel an internal X comprobante. AFIP receipts return 400
    — those need a Nota de Crédito (separate flow, not yet wired up)."""
    return service.cancel_invoice(invoice_id)


@router.post("/{invoice_id}/restore", response_model=InvoiceResponse)
def restore_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceResponse:
    """Reverse a soft-cancellation on an internal X comprobante."""
    return service.restore_invoice(invoice_id)
