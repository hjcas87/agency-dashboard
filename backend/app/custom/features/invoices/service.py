"""Service layer for the Invoice feature.

Orchestrates two issuance flows:

* `AFIP` — request CAE from ARCA, persist `afip_invoice_log` audit row,
  then persist `Invoice` referencing it.
* `INTERNAL` — local-only "Comprobante interno X". Skips AFIP entirely,
  allocates a global sequential `internal_number`, persists the
  `Invoice` with `is_internal=True` and no `afip_invoice_log_id`.

The choice is driven by `IssueFromProposalRequest.kind` /
`IssueManualRequest.kind`. The receipt_type (Factura A / B / C / FCE)
only matters when `kind == AFIP`.
"""
import logging
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.custom.features.clients.models import Client
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
    InvoiceKind,
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
from app.shared.afip.enums import is_class_c, is_fce
from app.shared.afip.models import AfipInvoiceLog
from app.shared.afip.schemas import InvoiceResult

logger = logging.getLogger(__name__)


def _allows_cf_fallback(receipt_type: ReceiptType) -> bool:
    """Class C receipts (Factura/NC/ND C) can fall back to Consumidor
    Final if the AFIP padrón rejects the client's CUIT. FCE never —
    those always require a CUIT-validated receiver (ARCA 1487)."""
    return is_class_c(receipt_type) and not is_fce(receipt_type)


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

    def cancel_invoice(self, invoice_id: int) -> InvoiceResponse:
        """Mark an invoice as cancelled.

        For internal X comprobantes this is a soft toggle: the row stays
        visible (struck through in the UI) and `cancelled_at` is set to
        now() so the audit trail is preserved.

        For AFIP-issued comprobantes this raises 400 — anulación on
        AFIP requires emitting a Nota de Crédito linked back via
        CbtesAsoc, and that flow is not implemented yet. Re-issuing a
        cancellation row on AFIP without the NC would silently desync
        the local state from ARCA's authorisation, which is worse than
        not supporting it.
        """
        invoice = self.repository.get(invoice_id)
        if invoice is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)
        if not invoice.is_internal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La anulación de comprobantes AFIP requiere emitir una "
                    "Nota de Crédito — flujo aún no disponible. Por ahora "
                    "solo se pueden anular comprobantes internos (X)."
                ),
            )
        if invoice.cancelled_at is not None:
            return self._to_response(invoice)
        invoice.cancelled_at = datetime.now(tz=UTC)
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return self._to_response(invoice)

    def restore_invoice(self, invoice_id: int) -> InvoiceResponse:
        """Undo a soft cancellation on an internal X comprobante.
        Symmetric inverse of `cancel_invoice` — same restrictions."""
        invoice = self.repository.get(invoice_id)
        if invoice is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)
        if not invoice.is_internal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden restaurar comprobantes internos (X).",
            )
        if invoice.cancelled_at is None:
            return self._to_response(invoice)
        invoice.cancelled_at = None
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
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

        return self._issue(
            kind=request.kind,
            receipt_type=request.receipt_type,
            client=client,
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
        return self._issue(
            kind=request.kind,
            receipt_type=request.receipt_type,
            client=client,
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

    def _issue(
        self,
        *,
        kind: InvoiceKind,
        receipt_type: ReceiptType,
        client: Client,
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
        """Dispatch on `kind`: internal receipts skip AFIP entirely;
        AFIP receipts go through the ARCA flow with a Class-C-only CF
        fallback."""
        if kind is InvoiceKind.INTERNAL:
            return self._issue_internal(
                client_id=client.id,
                proposal_id=proposal_id,
                issue_date=issue_date,
                concept=concept,
                service_date_from=service_date_from,
                service_date_to=service_date_to,
                total_ars=total_ars,
                line_items=line_items,
                commercial_reference=commercial_reference,
            )
        return self._issue_afip(
            receipt_type=receipt_type,
            client=client,
            proposal_id=proposal_id,
            issue_date=issue_date,
            concept=concept,
            service_date_from=service_date_from,
            service_date_to=service_date_to,
            total_ars=total_ars,
            line_items=line_items,
            commercial_reference=commercial_reference,
            afip=afip,
        )

    def _issue_internal(
        self,
        *,
        client_id: int,
        proposal_id: int | None,
        issue_date: date,
        concept: int,
        service_date_from: date | None,
        service_date_to: date | None,
        total_ars: Decimal,
        line_items: list[InvoiceLineItem],
        commercial_reference: str | None,
    ) -> InvoiceResponse:
        """Persist a local-only "Comprobante interno X". No AFIP call,
        no CAE, no QR. The number is allocated as `MAX(internal_number)
        + 1` — global sequence across the whole table."""
        next_internal = (
            self.db.query(func.coalesce(func.max(Invoice.internal_number), 0)).scalar() or 0
        )
        invoice = Invoice(
            proposal_id=proposal_id,
            client_id=client_id,
            afip_invoice_log_id=None,
            is_internal=True,
            internal_number=next_internal + 1,
            receipt_type=0,  # not an AFIP receipt — sentinel for "internal"
            concept=concept,
            issue_date=issue_date,
            service_date_from=service_date_from,
            service_date_to=service_date_to,
            total_amount_ars=total_ars,
            document_type=None,
            document_number=None,
            line_items=[{"name": line.name, "amount": str(line.amount)} for line in line_items],
            commercial_reference=commercial_reference,
        )
        self.repository.add(invoice)
        return self._to_response(invoice)

    def _issue_afip(
        self,
        *,
        receipt_type: ReceiptType,
        client: Client,
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
        """Run the AFIP issuance flow. For receipt classes that require
        receiver identification (A, B, FCE-*) the client must have a
        CUIT loaded — we reject upfront with 400, no AFIP round-trip.

        For Class-C receipts (Factura C, NC C, ND C) we first attempt
        with the client's real CUIT/IvaCondition; if AFIP rejects with
        a padrón error (typically obs 10015), we retry as Consumidor
        Final on the same request. The first attempt's audit row stays
        in `afip_invoice_log` for traceability.
        """
        cf_fallback_allowed = _allows_cf_fallback(receipt_type)

        # Hard requirement for A / B / FCE: the receiver must be
        # identified by CUIT before we even talk to AFIP.
        if not cf_fallback_allowed and not client.cuit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"El comprobante {receipt_type.name} requiere CUIT del "
                    "receptor — cargá el CUIT del cliente antes de emitir."
                ),
            )

        # First attempt: identify the receiver if we can. For C without
        # a CUIT, skip straight to the Consumidor Final path.
        primary_result: InvoiceResult | None = None
        if client.cuit:
            primary_request = self._build_afip_request(
                receipt_type=receipt_type,
                concept=concept,
                document_type=DocType.CUIT,
                document_number=int(client.cuit),
                iva_condition=client.iva_condition or IvaCondition.CF,
                issue_date=issue_date,
                service_date_from=service_date_from,
                service_date_to=service_date_to,
                total_ars=total_ars,
                commercial_reference=commercial_reference,
            )
            primary_result = afip.issue_invoice(primary_request)
            if (
                primary_result.success
                and primary_result.cae is not None
                and primary_result.log_id is not None
            ):
                return self._persist_afip_invoice(
                    result=primary_result,
                    client_id=client.id,
                    proposal_id=proposal_id,
                    concept=concept,
                    issue_date=issue_date,
                    service_date_from=service_date_from,
                    service_date_to=service_date_to,
                    total_ars=total_ars,
                    document_type=int(DocType.CUIT),
                    document_number=int(client.cuit),
                    line_items=line_items,
                    commercial_reference=commercial_reference,
                )

            # AFIP rejected the receiver-identified attempt.
            if not cf_fallback_allowed:
                self._raise_afip_error(primary_result)
            logger.warning(
                "Class-C primary attempt rejected by AFIP for client %s, "
                "falling back to Consumidor Final: %s",
                client.id,
                _format_afip_messages(primary_result),
            )

        # Class C only: retry as (or start as) Consumidor Final.
        fallback_request = self._build_afip_request(
            receipt_type=receipt_type,
            concept=concept,
            document_type=DocType.FINAL_CONSUMER,
            document_number=0,
            iva_condition=IvaCondition.CF,
            issue_date=issue_date,
            service_date_from=service_date_from,
            service_date_to=service_date_to,
            total_ars=total_ars,
            commercial_reference=commercial_reference,
        )
        fallback_result = afip.issue_invoice(fallback_request)
        if (
            not fallback_result.success
            or fallback_result.cae is None
            or fallback_result.log_id is None
        ):
            # If the primary attempt also failed, prepend its message so
            # the operator sees the full picture.
            self._raise_afip_error(fallback_result, primary=primary_result)

        return self._persist_afip_invoice(
            result=fallback_result,
            client_id=client.id,
            proposal_id=proposal_id,
            concept=concept,
            issue_date=issue_date,
            service_date_from=service_date_from,
            service_date_to=service_date_to,
            total_ars=total_ars,
            document_type=int(DocType.FINAL_CONSUMER),
            document_number=0,
            line_items=line_items,
            commercial_reference=commercial_reference,
        )

    def _build_afip_request(
        self,
        *,
        receipt_type: ReceiptType,
        concept: int,
        document_type: DocType,
        document_number: int,
        iva_condition: IvaCondition,
        issue_date: date,
        service_date_from: date | None,
        service_date_to: date | None,
        total_ars: Decimal,
        commercial_reference: str | None,
    ) -> InvoiceRequest:
        return InvoiceRequest(
            receipt_type=receipt_type,
            concept=Concept(concept),
            document_type=document_type,
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
            iva_blocks=[],  # Class C must not include IVA detail; A/B add it later.
            commercial_reference=commercial_reference,
        )

    def _persist_afip_invoice(
        self,
        *,
        result: InvoiceResult,
        client_id: int,
        proposal_id: int | None,
        concept: int,
        issue_date: date,
        service_date_from: date | None,
        service_date_to: date | None,
        total_ars: Decimal,
        document_type: int,
        document_number: int,
        line_items: list[InvoiceLineItem],
        commercial_reference: str | None,
    ) -> InvoiceResponse:
        invoice = Invoice(
            proposal_id=proposal_id,
            client_id=client_id,
            afip_invoice_log_id=result.log_id,
            is_internal=False,
            internal_number=None,
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

    @staticmethod
    def _raise_afip_error(
        result: InvoiceResult, primary: InvoiceResult | None = None
    ) -> None:
        """Translate an AFIP rejection into an HTTP 502. When `primary`
        is set, both attempts' messages are joined so the operator can
        see why the CUIT path failed and why the Consumidor-Final path
        also failed."""
        parts: list[str] = []
        if primary is not None:
            parts.append(f"Intento con CUIT: {_format_afip_messages(primary)}")
            parts.append(f"Intento como Consumidor Final: {_format_afip_messages(result)}")
        else:
            parts.append(_format_afip_messages(result))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ERR_AFIP_ISSUE_FAILED.format(error=" | ".join(parts)),
        )

    def _to_response(self, invoice: Invoice) -> InvoiceResponse:
        """Hydrate an Invoice with the joined AfipInvoiceLog data the
        UI needs (CAE, observations, etc.) and the client's name. For
        internal receipts the AFIP-side fields are all null."""
        log: AfipInvoiceLog | None = None
        if invoice.afip_invoice_log_id is not None:
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
            is_internal=invoice.is_internal,
            internal_number=invoice.internal_number,
            afip_invoice_log_id=invoice.afip_invoice_log_id,
            cae=log.cae if log else None,
            cae_expiration=log.cae_expiration if log else None,
            afip_success=log.success if log else False,
            afip_observations=list(log.observations or []) if log else [],
            afip_errors=list(log.errors or []) if log else [],
            receipt_number=log.receipt_number if log else None,
            point_of_sale=log.point_of_sale if log else None,
            cancelled_at=(
                invoice.cancelled_at.isoformat() if invoice.cancelled_at else None
            ),
            created_at=invoice.created_at.isoformat() if invoice.created_at else "",
            updated_at=invoice.updated_at.isoformat() if invoice.updated_at else "",
        )


def _format_afip_messages(result: InvoiceResult) -> str:
    """Flatten an InvoiceResult's errors + observations into a single
    human-readable string for the toast."""
    parts: list[str] = []
    parts.extend(f"[{e.code}] {e.message}" for e in result.errors)
    parts.extend(f"[{o.code}] {o.message}" for o in result.observations)
    return "; ".join(parts) or "AFIP no devolvió CAE"


def _coerce_line_items(raw: list[Any]) -> list[InvoiceLineItem]:
    """Defensive coercion: JSONB roundtrip returns dicts."""
    out: list[InvoiceLineItem] = []
    for item in raw:
        out.append(InvoiceLineItem.model_validate(item))
    return out
