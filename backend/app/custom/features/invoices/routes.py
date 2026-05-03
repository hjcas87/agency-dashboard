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
    afip: AfipService = Depends(afip_dependency),
) -> InvoiceResponse:
    """Anular un comprobante.

    Internal X → soft toggle, returns the same Invoice with
    `cancelled_at` set.

    AFIP-issued → emit a Nota de Crédito linked via CbtesAsoc, persist
    it as a new Invoice row with `cancels_invoice_id` pointing at the
    original, and back-link the original via `cancelled_by_invoice_id`.
    The response is the **NC** Invoice (with its own CAE) so the UI
    can immediately offer to view/print/email it. The frontend follows
    `cancelled_by_invoice_id` to highlight the link in the listing."""
    return service.cancel_invoice(invoice_id, afip)


@router.post("/{invoice_id}/restore", response_model=InvoiceResponse)
def restore_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceResponse:
    """Reverse a soft-cancellation on an internal X comprobante."""
    return service.restore_invoice(invoice_id)
