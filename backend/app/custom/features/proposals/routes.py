"""
Routes for the Proposal feature.
"""
import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.custom.features.proposals.messages import (
    ERR_AI_PARSE_INVALID_JSON,
    ERR_AI_PARSE_INVALID_PAYLOAD,
)
from app.custom.features.proposals.schemas import (
    ProposalAIParseRequest,
    ProposalAIParseResponse,
    ProposalCreate,
    ProposalResponse,
    ProposalStatusUpdate,
    ProposalUpdate,
)
from app.custom.features.proposals.service import ProposalService
from app.database import get_db

router = APIRouter(prefix="/proposals", tags=["Custom: Proposals"])


def get_proposal_service(db: Session = Depends(get_db)) -> ProposalService:
    """Dependency to obtain the proposal service."""
    return ProposalService(db)


@router.get("/", response_model=list[ProposalResponse])
def list_proposals(
    service: ProposalService = Depends(get_proposal_service),
) -> list[ProposalResponse]:
    """Return all proposals with calculated totals."""
    return service.list_proposals()


@router.get("/{proposal_id}", response_model=ProposalResponse)
def get_proposal(
    proposal_id: int,
    service: ProposalService = Depends(get_proposal_service),
) -> ProposalResponse:
    """Return a single proposal by ID with its tasks."""
    return service.get_proposal(proposal_id)


@router.post(
    "/",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal(
    data: ProposalCreate,
    service: ProposalService = Depends(get_proposal_service),
) -> ProposalResponse:
    """Create a new proposal with tasks."""
    return service.create_proposal(data)


@router.put("/{proposal_id}", response_model=ProposalResponse)
def update_proposal(
    proposal_id: int,
    data: ProposalUpdate,
    service: ProposalService = Depends(get_proposal_service),
) -> ProposalResponse:
    """Update an existing proposal."""
    return service.update_proposal(proposal_id, data)


@router.patch("/{proposal_id}/status", response_model=ProposalResponse)
def update_proposal_status(
    proposal_id: int,
    data: ProposalStatusUpdate,
    service: ProposalService = Depends(get_proposal_service),
) -> ProposalResponse:
    """Change the status of a proposal."""
    return service.update_status(proposal_id, data)


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal(
    proposal_id: int,
    service: ProposalService = Depends(get_proposal_service),
) -> None:
    """Delete a proposal."""
    return service.delete_proposal(proposal_id)


@router.post("/parse-ai-input", response_model=ProposalAIParseResponse)
def parse_ai_input(data: ProposalAIParseRequest) -> ProposalAIParseResponse:
    """Parse the JSON payload the operator pasted from the AI prompt
    template and return clean tasks + summary. Pure parsing — does not
    touch the DB. The frontend uses this to pre-populate the form so
    the operator can still review/edit before saving."""
    try:
        # `strict=False` lets through literal control chars (tabs,
        # newlines) inside string values. Operators pasting from the
        # chat clipboard, and many AI models, routinely produce JSON
        # with un-escaped newlines inside long string fields — the
        # tradeoff is harmless since we still hand the parsed dict to
        # Pydantic for the real validation.
        parsed = json.loads(data.raw, strict=False)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ERR_AI_PARSE_INVALID_JSON.format(
                reason=exc.msg, line=exc.lineno, column=exc.colno
            ),
        ) from exc

    try:
        return ProposalAIParseResponse.model_validate(parsed)
    except ValidationError as exc:
        first = exc.errors()[0]
        location = ".".join(str(p) for p in first["loc"]) or "root"
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ERR_AI_PARSE_INVALID_PAYLOAD.format(location=location, reason=first["msg"]),
        ) from exc
