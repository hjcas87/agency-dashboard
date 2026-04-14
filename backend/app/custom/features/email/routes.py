"""
Email feature — API routes.
"""
import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.custom.features.clients.repository import ClientRepository
from app.custom.features.email.messages import ERRORS, LOG_MESSAGES, RESPONSES
from app.custom.features.proposals.repository import ProposalRepository
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
from app.shared.pdf.generator import PdfGenerator
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

        client = None
        if proposal.client_id:
            client = client_repo.get(proposal.client_id)

        total_hours = sum((t.hours for t in proposal.tasks), Decimal("0"))
        subtotal_ars = total_hours * proposal.hourly_rate_ars
        adjustment_amount_ars = subtotal_ars * (proposal.adjustment_percentage / Decimal("100"))
        total_ars = subtotal_ars + adjustment_amount_ars
        total_usd = total_ars / proposal.exchange_rate if proposal.exchange_rate else Decimal("0")

        proposal_data = {
            "proposal": {
                "id": proposal.id,
                "name": proposal.name,
                "status": str(proposal.status),
                "created_at": proposal.created_at.isoformat(),
            },
            "client": {
                "name": client.name,
                "company": client.company,
                "email": client.email,
                "phone": client.phone,
            } if client else None,
            "tasks": [
                {
                    "name": task.name,
                    "description": task.description,
                    "hours": float(task.hours),
                }
                for task in proposal.tasks
            ],
            "totals": {
                "Total Horas": f"{float(total_hours):.2f} hs",
                "Subtotal ARS": f"$ {subtotal_ars:,.2f}",
                f"Ajuste ({float(proposal.adjustment_percentage):.1f}%)": f"$ {adjustment_amount_ars:,.2f}",
                "Total ARS": f"$ {total_ars:,.2f}",
                "Total USD": f"US$ {total_usd:,.2f}",
            },
        }

        try:
            logger.info(LOG_MESSAGES["pdf_attachment_generating"].format(id=proposal.id))
            generator = PdfGenerator(db)
            pdf_bytes = generator.generate_proposal(proposal_data)
            attachments.append(Attachment(
                filename=f"presupuesto_{proposal.id}.pdf",
                content=pdf_bytes,
                mime_type="application/pdf",
            ))
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
