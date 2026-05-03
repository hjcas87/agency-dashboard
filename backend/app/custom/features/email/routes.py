"""
Email feature — API routes.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.custom.features.clients.repository import ClientRepository
from app.custom.features.email.messages import ERRORS, LOG_MESSAGES, RESPONSES
from app.custom.features.invoices.repository import InvoiceRepository
from app.custom.features.pdf.routes import generate_invoice_pdf
from app.custom.features.proposals.models import ProposalCurrency
from app.custom.features.proposals.quote.overlay import QuoteData, QuoteOverlayBuilder, QuoteTask
from app.custom.features.proposals.quote_formatting import (
    format_email_body,
    format_email_subject,
    format_filename,
    format_recipient_label,
)
from app.custom.features.proposals.repository import ProposalRepository
from app.custom.features.proposals.service import ProposalService
from app.database import get_db
from app.shared.email.schemas import (
    EmailPreviewRequest,
    EmailSendRequest,
    EmailTemplateCreate,
    EmailTemplateResponse,
    EmailTemplateUpdate,
)
from app.shared.email.template import EmailTemplateRepository
from app.shared.interfaces.email_service import Attachment
from app.shared.services.email_service_factory import get_email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["email"])


def get_template_repo(db: Session = Depends(get_db)) -> EmailTemplateRepository:
    return EmailTemplateRepository(db)


@router.post("/send")
async def send_email(
    request: EmailSendRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Send an email with optional PDF attachment.

    Args:
        request: Email details + optional proposal ID for PDF attachment
    """
    email_service = get_email_service()

    attachments = []
    if request.attach_proposal_pdf:
        proposal_repo = ProposalRepository(db)
        client_repo = ClientRepository(db)

        proposal = proposal_repo.get_with_tasks(request.attach_proposal_pdf)
        if not proposal:
            raise HTTPException(status_code=404, detail=ERRORS["proposal_not_found"])

        client = client_repo.get(proposal.client_id) if proposal.client_id else None

        # Reuse the same overlay builder that drives the download
        # endpoint so the email attachment is byte-for-byte identical
        # to the PDF the client would see in the browser.
        totals = ProposalService.calculate_totals(proposal, proposal.tasks)
        currency = (
            proposal.currency.value
            if isinstance(proposal.currency, ProposalCurrency)
            else str(proposal.currency)
        )
        total_amount = totals["total_usd"] if currency == "USD" else totals["total_ars"]
        recipient_label = (
            format_recipient_label(client) if proposal.show_recipient_on_cover else None
        )
        quote_data = QuoteData(
            code=proposal.code,
            issue_date=proposal.issue_date,
            recipient_label=recipient_label,
            tasks=[QuoteTask(name=t.name, description=t.description) for t in proposal.tasks],
            deliverables_summary=proposal.deliverables_summary,
            estimated_days=proposal.estimated_days,
            total_amount=total_amount,
            currency=currency,
        )

        try:
            logger.info(LOG_MESSAGES["pdf_attachment_generating"].format(id=proposal.id))
            pdf_bytes = QuoteOverlayBuilder().build(quote_data)
            attachments.append(
                Attachment(
                    filename=f"{format_filename(proposal, client)}.pdf",
                    content=pdf_bytes,
                    mime_type="application/pdf",
                )
            )
            logger.info(LOG_MESSAGES["pdf_attachment_generated"].format(id=proposal.id))
        except Exception as e:
            logger.error(LOG_MESSAGES["pdf_attachment_error"].format(error=str(e)))
            raise HTTPException(status_code=500, detail=ERRORS["pdf_attachment_failed"]) from e

    logger.info(LOG_MESSAGES["email_sending"].format(to=request.to))
    success = await email_service.send_email(
        to=request.to,
        subject=request.subject,
        body=request.body,
        html_body=request.html_body,
        attachments=attachments if attachments else None,
        cc=request.cc,
    )

    if not success:
        raise HTTPException(status_code=500, detail=ERRORS["send_failed"])

    logger.info(LOG_MESSAGES["email_sent"].format(to=request.to))
    return {"message": RESPONSES["email_sent"]}


@router.post("/proposals/{proposal_id}/send")
async def send_proposal_email(
    proposal_id: int,
    request: EmailSendRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Send a proposal by email with PDF attachment.

    Args:
        proposal_id: ID of the proposal
        request: Email details (to, subject, body, cc)
    """
    request.attach_proposal_pdf = proposal_id
    return await send_email(request, db)


@router.get("/proposals/{proposal_id}/template")
async def get_proposal_email_template(
    proposal_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Return the canonical subject + body the operator should send
    for this proposal. The frontend pre-fills the email dialog with
    these values; the operator can still tweak before sending.
    """
    proposal_repo = ProposalRepository(db)
    proposal = proposal_repo.get_with_tasks(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=ERRORS["proposal_not_found"])

    client = ClientRepository(db).get(proposal.client_id) if proposal.client_id else None
    return {
        "to": (client.email if client and client.email else "") or "",
        "subject": format_email_subject(proposal, client),
        "body": format_email_body(proposal, client),
    }


@router.post("/invoices/{invoice_id}/send")
async def send_invoice_email(
    invoice_id: int,
    request: EmailSendRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Send an invoice (or internal X comprobante) by email with the
    printed PDF attached. Filename adapts to the kind so the recipient
    sees `presupuesto_X-00000001.pdf` for internals and
    `factura_<n>.pdf` for AFIP-issued comprobantes."""
    invoice_repo = InvoiceRepository(db)
    invoice = invoice_repo.get(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    pdf_response = await generate_invoice_pdf(invoice_id, db)
    pdf_bytes = pdf_response.body if hasattr(pdf_response, "body") else b""
    if invoice.is_internal:
        suffix = (
            f"X-{str(invoice.internal_number).zfill(8)}"
            if invoice.internal_number is not None
            else f"X-{invoice_id}"
        )
        filename = f"presupuesto_{suffix}.pdf"
    else:
        filename = f"factura_{invoice_id}.pdf"
    attachments = [
        Attachment(
            filename=filename,
            content=bytes(pdf_bytes),
            mime_type="application/pdf",
        )
    ]

    email_service = get_email_service()
    logger.info(LOG_MESSAGES["email_sending"].format(to=request.to))
    success = await email_service.send_email(
        to=request.to,
        subject=request.subject,
        body=request.body,
        html_body=request.html_body,
        attachments=attachments,
        cc=request.cc,
    )
    if not success:
        raise HTTPException(status_code=500, detail=ERRORS["send_failed"])
    logger.info(LOG_MESSAGES["email_sent"].format(to=request.to))
    return {"message": RESPONSES["email_sent"]}


@router.get("/templates", response_model=list[EmailTemplateResponse])
async def list_templates(
    template_repo: EmailTemplateRepository = Depends(get_template_repo),
) -> list[EmailTemplateResponse]:
    """List all email templates."""
    templates = template_repo.list_all()
    return [EmailTemplateResponse.model_validate(t) for t in templates]


@router.get("/templates/{template_id}", response_model=EmailTemplateResponse)
async def get_template(
    template_id: int,
    template_repo: EmailTemplateRepository = Depends(get_template_repo),
) -> EmailTemplateResponse:
    """Get an email template by ID."""
    template = template_repo.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=ERRORS["template_not_found"])
    return EmailTemplateResponse.model_validate(template)


@router.post("/templates", response_model=EmailTemplateResponse)
async def create_template(
    template_data: EmailTemplateCreate,
    template_repo: EmailTemplateRepository = Depends(get_template_repo),
) -> EmailTemplateResponse:
    """Create a new email template."""
    template = template_repo.create(template_data)
    logger.info(LOG_MESSAGES["template_created"].format(id=template.id))
    return EmailTemplateResponse.model_validate(template)


@router.put("/templates/{template_id}", response_model=EmailTemplateResponse)
async def update_template(
    template_id: int,
    update_data: EmailTemplateUpdate,
    template_repo: EmailTemplateRepository = Depends(get_template_repo),
) -> EmailTemplateResponse:
    """Update an email template."""
    template = template_repo.update(template_id, update_data)
    if not template:
        raise HTTPException(status_code=404, detail=ERRORS["template_not_found"])
    logger.info(LOG_MESSAGES["template_updated"].format(id=template_id))
    return EmailTemplateResponse.model_validate(template)


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: int,
    template_repo: EmailTemplateRepository = Depends(get_template_repo),
) -> None:
    """Delete an email template."""
    success = template_repo.delete(template_id)
    if not success:
        raise HTTPException(status_code=404, detail=ERRORS["template_not_found"])
    logger.info(LOG_MESSAGES["template_deleted"].format(id=template_id))


@router.post("/templates/{template_id}/preview")
async def preview_template(
    template_id: int,
    request: EmailPreviewRequest,
    template_repo: EmailTemplateRepository = Depends(get_template_repo),
) -> dict:
    """
    Preview email with variables rendered.

    Replaces variables like {nombre_cliente} in subject and body with actual values.
    """
    template = template_repo.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=ERRORS["template_not_found"])

    subject = template.subject
    body = template.body

    # Render variables
    for key, value in request.variables.items():
        subject = subject.replace(f"{{{key}}}", value)
        body = body.replace(f"{{{key}}}", value)

    logger.info(LOG_MESSAGES["preview_generated"].format(id=template_id))
    return {
        "subject": subject,
        "body": body,
        "to": request.to if hasattr(request, "to") else "destinatario@ejemplo.com",
    }
