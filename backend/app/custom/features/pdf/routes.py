"""
PDF Templates feature — API routes.
"""
import logging
import uuid
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.custom.features.clients.repository import ClientRepository
from app.custom.features.invoices.issuer import ISSUER
from app.custom.features.invoices.repository import InvoiceRepository
from app.custom.features.proposals.models import ProposalCurrency
from app.custom.features.proposals.quote.overlay import QuoteData, QuoteOverlayBuilder, QuoteTask
from app.custom.features.proposals.repository import ProposalRepository
from app.custom.features.proposals.service import ProposalService
from app.database import get_db
from app.shared.afip.enums import iva_condition_label
from app.shared.afip.models import AfipInvoiceLog
from app.shared.afip.qr import build_qr_url, render_qr_png
from app.shared.pdf.generator import PdfGenerator
from app.shared.pdf.messages import (
    ALLOWED_LOGO_MIME_TYPES,
    DEFAULT_ACCENT_COLOR,
    DEFAULT_BG_COLOR,
    DEFAULT_TEXT_COLOR,
    ERRORS,
    LOG_MESSAGES,
    LOGO_UPLOAD_DIR_NAME,
    RESPONSES,
)
from app.shared.pdf.schemas import PdfTemplateCreate, PdfTemplateResponse, PdfTemplateUpdate
from app.shared.pdf.template import PdfTemplateRepository

logger = logging.getLogger(__name__)

# Directory for uploaded logos
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent.parent / "uploads" / LOGO_UPLOAD_DIR_NAME
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/pdf", tags=["pdf"])


def get_template_repo(db: Session = Depends(get_db)) -> PdfTemplateRepository:
    return PdfTemplateRepository(db)


@router.get("/proposals/{proposal_id}")
async def generate_proposal_pdf(
    proposal_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Stream the 5-page client-facing quote PDF for a proposal."""
    proposal_repo = ProposalRepository(db)
    proposal = proposal_repo.get_with_tasks(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=ERRORS["proposal_not_found"])

    totals = ProposalService.calculate_totals(proposal, proposal.tasks)
    currency = (
        proposal.currency.value
        if isinstance(proposal.currency, ProposalCurrency)
        else str(proposal.currency)
    )
    total_amount = totals["total_usd"] if currency == "USD" else totals["total_ars"]

    quote_data = QuoteData(
        tasks=[QuoteTask(name=t.name, description=t.description) for t in proposal.tasks],
        deliverables_summary=proposal.deliverables_summary,
        estimated_days=proposal.estimated_days,
        total_amount=total_amount,
        currency=currency,
    )

    logger.info(LOG_MESSAGES["proposal_generating"].format(id=proposal_id))
    pdf_bytes = QuoteOverlayBuilder().build(quote_data)
    logger.info(LOG_MESSAGES["proposal_generated"].format(id=proposal_id))

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=presupuesto_{proposal_id}.pdf",
        },
    )


@router.get("/invoices/{invoice_id}")
async def generate_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Generate and stream the printed Factura PDF for an issued invoice.

    The renderer in `shared/pdf/renderers/invoice.py` is agnostic — this
    handler is the place that knows about *this* project's issuer
    identity (loaded from `custom/features/invoices/issuer.py`) and
    pulls AFIP audit data from `afip_invoice_log` to assemble the QR
    + CAE block.
    """
    invoice_repo = InvoiceRepository(db)
    client_repo = ClientRepository(db)

    invoice = invoice_repo.get(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    # Internal "X" comprobantes don't have an AFIP log; everything in
    # this branch (QR, CAE, point-of-sale) is skipped for them and the
    # renderer keys off `invoice.is_internal` to draw the X-flavoured
    # header + disclaimer footer.
    log: AfipInvoiceLog | None = None
    if invoice.afip_invoice_log_id is not None:
        log = (
            db.query(AfipInvoiceLog)
            .filter(AfipInvoiceLog.id == invoice.afip_invoice_log_id)
            .first()
        )
    client = client_repo.get(invoice.client_id) if invoice.client_id else None

    qr_url = ""
    qr_png: bytes | None = None
    if (
        log
        and log.cae
        and log.receipt_number is not None
        and log.point_of_sale is not None
        and invoice.document_type is not None
        and invoice.document_number is not None
    ):
        qr_url = build_qr_url(
            issue_date=invoice.issue_date,
            issuer_cuit=ISSUER.cuit,
            point_of_sale=log.point_of_sale,
            receipt_type=invoice.receipt_type,
            receipt_number=log.receipt_number,
            total_amount=invoice.total_amount_ars,
            currency_id="PES",
            currency_quote=Decimal("1"),
            receiver_doc_type=invoice.document_type,
            receiver_doc_number=invoice.document_number,
            cae=log.cae,
        )
        qr_png = render_qr_png(qr_url)

    # The customer block on the printed receipt is sourced ENTIRELY
    # from the Client record — the AFIP request might have used DocType
    # 99 / DocNro 0 (Consumidor Final) for monotributo low-amount cases,
    # but the printed receipt still names the actual buyer with their
    # real CUIT, IVA condition and address. The renderer's
    # `_or_placeholder` helper prints "________" for fields the client
    # hasn't filled in yet — so we always pass the raw client value, no
    # "0" or empty-string fallbacks here.
    customer_legal_name = ""
    customer_cuit = ""
    customer_iva_label = ""
    customer_address = ""
    if client:
        customer_legal_name = client.company or client.name or ""
        customer_cuit = client.cuit or ""
        customer_iva_label = iva_condition_label(client.iva_condition)
        customer_address = client.address or ""

    invoice_data = {
        "issuer": {
            "legal_name": ISSUER.legal_name,
            "address": ISSUER.address,
            "iva_condition_label": ISSUER.iva_condition_label,
            "cuit": ISSUER.cuit,
            "gross_income": ISSUER.gross_income,
            "activity_start_date": ISSUER.activity_start_date,
            "logo_path": str(ISSUER.logo_path) if ISSUER.logo_path else None,
        },
        "customer": {
            "legal_name": customer_legal_name,
            # The label is always "CUIT" — it's the only document type
            # the operator captures on a Client today. If a client has
            # no CUIT loaded, the renderer prints a placeholder under
            # this label.
            "doc_label": "CUIT",
            "doc_number": customer_cuit,
            "iva_condition_label": customer_iva_label,
            "address": customer_address,
        },
        "invoice": {
            "receipt_type": invoice.receipt_type,
            "point_of_sale": log.point_of_sale if log else 0,
            "receipt_number": log.receipt_number if log else 0,
            "issue_date": invoice.issue_date,
            "period_from": invoice.service_date_from or invoice.issue_date,
            "period_to": invoice.service_date_to or invoice.issue_date,
            "due_date": invoice.issue_date,
            "condition_of_sale": "Otra",
            # Internal-mode flags consumed by the renderer to switch the
            # C-box letter to "X", drop the QR/CAE block and print the
            # "no válido como factura" disclaimer.
            "is_internal": invoice.is_internal,
            "internal_number": invoice.internal_number,
        },
        "items": [
            {
                "code": str(idx + 1).zfill(4),
                "name": item.get("name", ""),
                "quantity": Decimal("1"),
                "unit": "unidades",
                "unit_price": item.get("amount", "0"),
                "discount_pct": Decimal("0"),
                "discount_amount": Decimal("0"),
                "subtotal": item.get("amount", "0"),
            }
            for idx, item in enumerate(invoice.line_items or [])
        ],
        "totals": {
            "subtotal": invoice.total_amount_ars,
            "other_taxes": Decimal("0"),
            "total": invoice.total_amount_ars,
        },
        "afip": {
            "cae": log.cae if log else "",
            "cae_expiration": log.cae_expiration if log else None,
            "qr_png_bytes": qr_png,
            "qr_url": qr_url,
            "page_label": "1/1",
        },
    }

    try:
        generator = PdfGenerator(db)
        pdf_bytes = generator.generate_invoice(invoice_data)
        filename = f"factura_{invoice_id}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to render invoice PDF id=%s: %s", invoice_id, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/templates", response_model=PdfTemplateResponse)
async def get_active_template(
    template_repo: PdfTemplateRepository = Depends(get_template_repo),
) -> PdfTemplateResponse:
    """Get the active PDF template."""
    template = template_repo.get_default()
    if not template:
        template = template_repo.reset_to_defaults()

    return PdfTemplateResponse.model_validate(template)


@router.put("/templates", response_model=PdfTemplateResponse)
async def update_template(
    template_data: PdfTemplateUpdate,
    template_repo: PdfTemplateRepository = Depends(get_template_repo),
) -> PdfTemplateResponse:
    """Update the PDF template (creates if doesn't exist, updates if exists)."""
    existing = template_repo.get_default()
    if existing:
        template = template_repo.update(existing.id, template_data)
    else:
        # Create new template with the update data
        create_data = PdfTemplateCreate(
            logo_url=template_data.logo_url,
            header_text=template_data.header_text,
            footer_text=template_data.footer_text,
            bg_color=template_data.bg_color or DEFAULT_BG_COLOR,
            text_color=template_data.text_color or DEFAULT_TEXT_COLOR,
            accent_color=template_data.accent_color or DEFAULT_ACCENT_COLOR,
            is_default=template_data.is_default or False,
        )
        template = template_repo.create(create_data)

    if not template:
        raise HTTPException(status_code=500, detail=ERRORS["update_failed"])

    logger.info(LOG_MESSAGES["template_updated"].format(id=template.id))
    return PdfTemplateResponse.model_validate(template)


@router.post("/templates/reset", response_model=PdfTemplateResponse)
async def reset_template(
    template_repo: PdfTemplateRepository = Depends(get_template_repo),
) -> PdfTemplateResponse:
    """Reset PDF template to default values."""
    template = template_repo.reset_to_defaults()
    logger.info(LOG_MESSAGES["template_reset"])
    return PdfTemplateResponse.model_validate(template)


@router.post("/templates/logo")
async def upload_logo(
    file: UploadFile = File(...),
    template_repo: PdfTemplateRepository = Depends(get_template_repo),
) -> dict:
    """
    Upload a logo image for PDF templates.

    Accepts PNG, JPG, SVG, WEBP. Returns the URL path to access the logo.
    """
    if file.content_type not in ALLOWED_LOGO_MIME_TYPES:
        allowed_list = ", ".join(sorted(ALLOWED_LOGO_MIME_TYPES))
        raise HTTPException(
            status_code=400,
            detail=ERRORS["logo_invalid"],
        )

    # Generate unique filename
    ext = Path(file.filename or "logo").suffix or ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename

    content = await file.read()
    file_path.write_bytes(content)

    # URL path relative to backend static root
    logo_url = f"/uploads/{LOGO_UPLOAD_DIR_NAME}/{filename}"

    logger.info(LOG_MESSAGES["logo_uploaded"].format(filename=filename))
    return {"logo_url": logo_url, "message": RESPONSES["logo_uploaded"]}
