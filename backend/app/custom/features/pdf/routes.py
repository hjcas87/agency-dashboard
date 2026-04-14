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

from app.custom.features.clients.models import Client
from app.custom.features.clients.repository import ClientRepository
from app.custom.features.proposals.models import Proposal
from app.custom.features.proposals.repository import ProposalRepository
from app.database import get_db
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
    """
    Generate and stream a proposal PDF.

    Args:
        proposal_id: ID of the proposal

    Returns:
        PDF file streamed with Content-Disposition: inline
    """
    proposal_repo = ProposalRepository(db)
    client_repo = ClientRepository(db)

    proposal = proposal_repo.get_with_tasks(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=ERRORS["proposal_not_found"])

    client: Client | None = None
    if proposal.client_id:
        client = client_repo.get(proposal.client_id)

    # Build data dict for PDF generator
    proposal_dict = {
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
        "totals": _calculate_totals(proposal),
    }

    try:
        logger.info(LOG_MESSAGES["proposal_generating"].format(id=proposal_id))
        generator = PdfGenerator(db)
        pdf_bytes = generator.generate_proposal(proposal_dict)
        logger.info(LOG_MESSAGES["proposal_generated"].format(id=proposal_id))

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=presupuesto_{proposal_id}.pdf",
            },
        )
    except Exception as e:
        logger.exception(LOG_MESSAGES["generation_error"].format(id=proposal_id, error=str(e)))
        error_detail = ERRORS["generation_failed"].format(error=str(e))
        raise HTTPException(status_code=500, detail=error_detail) from e


def _calculate_totals(proposal: Proposal) -> dict[str, str]:
    """Calculate totals for PDF display."""
    total_hours = sum((t.hours for t in proposal.tasks), Decimal("0"))
    subtotal_ars = total_hours * proposal.hourly_rate_ars
    adjustment_amount_ars = subtotal_ars * (proposal.adjustment_percentage / Decimal("100"))
    total_ars = subtotal_ars + adjustment_amount_ars
    total_usd = total_ars / proposal.exchange_rate if proposal.exchange_rate else Decimal("0")

    return {
        "Total Horas": f"{float(total_hours):.2f} hs",
        "Subtotal ARS": f"$ {subtotal_ars:,.2f}",
        f"Ajuste ({float(proposal.adjustment_percentage):.1f}%)": f"$ {adjustment_amount_ars:,.2f}",
        "Total ARS": f"$ {total_ars:,.2f}",
        "Total USD": f"US$ {total_usd:,.2f}",
    }


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
