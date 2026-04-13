"""
Routes for the Proposal feature.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.custom.features.proposals.service import ProposalService
from app.custom.features.proposals.schemas import (
    ProposalCreate,
    ProposalUpdate,
    ProposalStatusUpdate,
    ProposalResponse,
)

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
