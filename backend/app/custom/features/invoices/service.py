"""Service layer for the Invoice feature.

Orchestrates the issuance flow:

    request -> validate proposal/client -> compute totals -> ask
    AfipService.issue_invoice -> persist Invoice referencing the
    AfipInvoiceLog row -> return InvoiceResponse.

This service depends on AfipService for the wire call, the
ProposalRepository / ClientRepository for the business context, and
its own InvoiceRepository for persistence.
"""
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.custom.features.clients.repository import ClientRepository
from app.custom.features.invoices.messages import (
    ERR_AFIP_ISSUE_FAILED,
    ERR_CLIENT_NOT_FOUND,
    ERR_NO_LINE_ITEMS,
    ERR_NOT_FOUND,
    ERR_PROPOSAL_ALREADY_INVOICED,
    ERR_PROPOSAL_NOT_ACCEPTED,
    ERR_PROPOSAL_NOT_FOUND,
)
from app.custom.features.invoices.models import Invoice
from app.custom.features.invoices.repository import InvoiceRepository
from app.custom.features.invoices.schemas import (
    BillableProposalResponse,
    InvoiceLineItem,
    InvoiceResponse,
    IssueFromProposalRequest,
    IssueManualRequest,
)
from app.custom.features.proposals.models import ProposalStatus
from app.custom.features.proposals.repository import ProposalRepository
from app.custom.features.proposals.service import ProposalService
from app.shared.afip import (
    AfipService,
    Concept,
    DocType,
    InvoiceRequest,
    IvaCondition,
    ReceiptType,
)
from app.shared.afip.models import AfipInvoiceLog


class InvoiceService:
    """Public service for the invoice feature."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = InvoiceRepository(db)
        self.proposal_repo = ProposalRepository(db)
        self.client_repo = ClientRepository(db)

    # ── Listings ─────────────────────────────────────────────────

    def list_invoices(self) -> list[InvoiceResponse]:
        invoices = self.repository.list_all()
        return [self._to_response(inv) for inv in invoices]

    def get_invoice(self, invoice_id: int) -> InvoiceResponse:
        invoice = self.repository.get(invoice_id)
        if invoice is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)
        return self._to_response(invoice)

    def list_billable_proposals(self) -> list[BillableProposalResponse]:
        """Proposals in ACCEPTED state without an associated invoice."""
        proposals = self.proposal_repo.get_all_with_relations()
        invoiced = self.repository.invoiced_proposal_ids()
        out: list[BillableProposalResponse] = []
        for p in proposals:
            if p.status is not ProposalStatus.ACCEPTED:
                continue
            if p.id in invoiced:
                continue
            totals = ProposalService.calculate_totals(p, list(p.tasks))
            client_name = None
            if p.client_id:
                client = self.client_repo.get(p.client_id)
                if client:
                    client_name = client.name
            out.append(
                BillableProposalResponse(
                    id=p.id,
                    name=p.name,
                    client_id=p.client_id,
                    client_name=client_name,
                    total_ars=totals["total_ars"],
                    created_at=p.created_at.isoformat() if p.created_at else "",
                )
            )
        return out

    # ── Issuance ──────────────────────────────────────────────────

    def issue_from_proposal(
        self, request: IssueFromProposalRequest, afip: AfipService
    ) -> InvoiceResponse:
        proposal = self.proposal_repo.get_with_tasks(request.proposal_id)
        if proposal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ERR_PROPOSAL_NOT_FOUND
            )

        current_status = (
            proposal.status
            if isinstance(proposal.status, ProposalStatus)
            else ProposalStatus(proposal.status)
        )
        if current_status is not ProposalStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERR_PROPOSAL_NOT_ACCEPTED
            )
        if self.repository.get_by_proposal(proposal.id) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=ERR_PROPOSAL_ALREADY_INVOICED
            )

        if proposal.client_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERR_CLIENT_NOT_FOUND
            )
        client = self.client_repo.get(proposal.client_id)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_CLIENT_NOT_FOUND)

        # Snapshot tasks as line items. Each task's amount is
        # `hours * hourly_rate` adjusted by adjustment_percentage.
        totals = ProposalService.calculate_totals(proposal, list(proposal.tasks))
        adjustment_factor = Decimal("1") + (proposal.adjustment_percentage / Decimal("100"))
        line_items = [
            InvoiceLineItem(
                name=task.name,
                amount=(task.hours * proposal.hourly_rate_ars * adjustment_factor).quantize(
                    Decimal("0.01")
                ),
            )
            for task in proposal.tasks
        ]
        total_ars = totals["total_ars"]

        return self._issue_factura_c(
            client_id=client.id,
            client_cuit=client.cuit,
            proposal_id=proposal.id,
            issue_date=request.issue_date,
            concept=request.concept.value,
            service_date_from=request.service_date_from,
            service_date_to=request.service_date_to,
            total_ars=total_ars,
            line_items=line_items,
            commercial_reference=request.commercial_reference,
            afip=afip,
        )

    def issue_manual(self, request: IssueManualRequest, afip: AfipService) -> InvoiceResponse:
        if not request.line_items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERR_NO_LINE_ITEMS)
        client = self.client_repo.get(request.client_id)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_CLIENT_NOT_FOUND)

        total_ars = sum((line.amount for line in request.line_items), Decimal("0"))
        return self._issue_factura_c(
            client_id=client.id,
            client_cuit=client.cuit,
            proposal_id=None,
            issue_date=request.issue_date,
            concept=request.concept.value,
            service_date_from=request.service_date_from,
            service_date_to=request.service_date_to,
            total_ars=total_ars,
            line_items=list(request.line_items),
            commercial_reference=request.commercial_reference,
            afip=afip,
        )

    # ── Internals ────────────────────────────────────────────────

    def _issue_factura_c(
        self,
        *,
        client_id: int,
        client_cuit: str | None,
        proposal_id: int | None,
        issue_date: date,
        concept: int,
        service_date_from: date | None,
        service_date_to: date | None,
        total_ars: Decimal,
        line_items: list[InvoiceLineItem],
        commercial_reference: str | None,
        afip: AfipService,
    ) -> InvoiceResponse:
        """Build the AFIP request, fire it, persist the local Invoice
        when AFIP returns a CAE."""
        # Factura C accepts any IvaCondition (it's the catch-all class).
        # If the client has no CUIT we fall back to Consumidor Final.
        if client_cuit:
            document_type = int(DocType.CUIT)
            document_number = int(client_cuit)
            iva_condition = IvaCondition.CF  # default; AFIP accepts any for C
        else:
            document_type = int(DocType.FINAL_CONSUMER)
            document_number = 0
            iva_condition = IvaCondition.CF

        afip_request = InvoiceRequest(
            receipt_type=ReceiptType.INVOICE_C,
            concept=Concept(concept),
            document_type=DocType(document_type),
            document_number=document_number,
            iva_condition=iva_condition,
            issue_date=issue_date,
            service_date_from=service_date_from,
            service_date_to=service_date_to,
            base_amount=total_ars,
            iva_amount=Decimal("0"),
            non_taxable_amount=Decimal("0"),
            exempt_amount=Decimal("0"),
            taxes_amount=Decimal("0"),
            total_amount=total_ars,
            iva_blocks=[],  # Class C must not include IVA detail.
            commercial_reference=commercial_reference,
        )

        result = afip.issue_invoice(afip_request)
        if not result.success or result.cae is None or result.log_id is None:
            error_msg = (
                "; ".join(f"[{e.code}] {e.message}" for e in result.errors)
                or "AFIP no devolvió CAE"
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=ERR_AFIP_ISSUE_FAILED.format(error=error_msg),
            )

        invoice = Invoice(
            proposal_id=proposal_id,
            client_id=client_id,
            afip_invoice_log_id=result.log_id,
            receipt_type=int(result.receipt_type),
            concept=concept,
            issue_date=issue_date,
            service_date_from=service_date_from,
            service_date_to=service_date_to,
            total_amount_ars=total_ars,
            document_type=document_type,
            document_number=document_number,
            line_items=[{"name": line.name, "amount": str(line.amount)} for line in line_items],
            commercial_reference=commercial_reference,
        )
        self.repository.add(invoice)
        return self._to_response(invoice)

    def _to_response(self, invoice: Invoice) -> InvoiceResponse:
        """Hydrate an Invoice with the joined AfipInvoiceLog data the
        UI needs (CAE, observations, etc.) and the client's name."""
        log = (
            self.db.query(AfipInvoiceLog)
            .filter(AfipInvoiceLog.id == invoice.afip_invoice_log_id)
            .first()
        )
        client_name: str | None = None
        if invoice.client_id:
            client = self.client_repo.get(invoice.client_id)
            if client:
                client_name = client.name

        line_items = [InvoiceLineItem.model_validate(item) for item in (invoice.line_items or [])]

        return InvoiceResponse(
            id=invoice.id,
            proposal_id=invoice.proposal_id,
            client_id=invoice.client_id,
            client_name=client_name,
            receipt_type=invoice.receipt_type,
            concept=invoice.concept,
            issue_date=invoice.issue_date,
            service_date_from=invoice.service_date_from,
            service_date_to=invoice.service_date_to,
            total_amount_ars=invoice.total_amount_ars,
            document_type=invoice.document_type,
            document_number=invoice.document_number,
            line_items=line_items,
            commercial_reference=invoice.commercial_reference,
            afip_invoice_log_id=invoice.afip_invoice_log_id,
            cae=log.cae if log else None,
            cae_expiration=log.cae_expiration if log else None,
            afip_success=log.success if log else False,
            afip_observations=list(log.observations or []) if log else [],
            afip_errors=list(log.errors or []) if log else [],
            receipt_number=log.receipt_number if log else None,
            point_of_sale=log.point_of_sale if log else None,
            created_at=invoice.created_at.isoformat() if invoice.created_at else "",
            updated_at=invoice.updated_at.isoformat() if invoice.updated_at else "",
        )


def _coerce_line_items(raw: list[Any]) -> list[InvoiceLineItem]:
    """Defensive coercion: JSONB roundtrip returns dicts."""
    out: list[InvoiceLineItem] = []
    for item in raw:
        out.append(InvoiceLineItem.model_validate(item))
    return out
