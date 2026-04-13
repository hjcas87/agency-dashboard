"""
Service layer for the Proposal feature.
"""
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.custom.features.proposals.models import Proposal, ProposalTask, ProposalStatus
from app.custom.features.proposals.repository import ProposalRepository, ProposalTaskRepository
from app.custom.features.proposals.schemas import (
    ProposalCreate,
    ProposalUpdate,
    ProposalStatusUpdate,
    ProposalResponse,
    ProposalTaskCreate,
    ProposalTaskResponse,
)
from app.shared.constants import AUTH_ERRORS


class ProposalService:
    """Service for proposal business logic and calculations."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProposalRepository(db)
        self.task_repository = ProposalTaskRepository(db)

    # ── Calculations ─────────────────────────────────────────────

    @staticmethod
    def calculate_totals(
        proposal: Proposal,
        tasks: list[ProposalTask],
    ) -> dict:
        """Calculate derived values for a proposal."""
        total_hours = sum((t.hours for t in tasks), Decimal("0"))
        subtotal_ars = total_hours * proposal.hourly_rate_ars
        adjustment_amount_ars = subtotal_ars * (proposal.adjustment_percentage / Decimal("100"))
        total_ars = subtotal_ars + adjustment_amount_ars
        total_usd = total_ars / proposal.exchange_rate if proposal.exchange_rate else Decimal("0")

        return {
            "total_hours": total_hours,
            "subtotal_ars": subtotal_ars,
            "adjustment_amount_ars": adjustment_amount_ars,
            "total_ars": total_ars,
            "total_usd": total_usd,
        }

    def _to_response(self, proposal: Proposal) -> ProposalResponse:
        """Convert a Proposal model to a response schema with calculated totals."""
        tasks = proposal.tasks if proposal.tasks else []
        totals = self.calculate_totals(proposal, tasks)

        # Get client name without relying on relationship
        client_name = None
        if proposal.client_id:
            from app.custom.features.clients.models import Client
            client = self.db.query(Client).filter(Client.id == proposal.client_id).first()
            if client:
                client_name = client.name

        return ProposalResponse(
            id=proposal.id,
            name=proposal.name,
            client_id=proposal.client_id,
            client_name=client_name,
            status=proposal.status.value if isinstance(proposal.status, ProposalStatus) else proposal.status,
            hourly_rate_ars=proposal.hourly_rate_ars,
            exchange_rate=proposal.exchange_rate,
            adjustment_percentage=proposal.adjustment_percentage,
            total_hours=totals["total_hours"],
            subtotal_ars=totals["subtotal_ars"],
            adjustment_amount_ars=totals["adjustment_amount_ars"],
            total_ars=totals["total_ars"],
            total_usd=totals["total_usd"],
            created_at=proposal.created_at.isoformat() if proposal.created_at else "",
            updated_at=proposal.updated_at.isoformat() if proposal.updated_at else "",
            tasks=[
                ProposalTaskResponse(
                    id=t.id,
                    proposal_id=t.proposal_id,
                    name=t.name,
                    description=t.description,
                    hours=t.hours,
                    sort_order=t.sort_order,
                )
                for t in tasks
            ],
        )

    # ── CRUD Operations ──────────────────────────────────────────

    def list_proposals(self) -> list[ProposalResponse]:
        """Return all proposals with calculated totals."""
        proposals = self.repository.get_all_with_relations()
        return [self._to_response(p) for p in proposals]

    def get_proposal(self, proposal_id: int) -> ProposalResponse:
        """Return a single proposal by ID with tasks."""
        proposal = self.repository.get_with_tasks(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado",
            )
        return self._to_response(proposal)

    def create_proposal(self, data: ProposalCreate) -> ProposalResponse:
        """Create a new proposal with its tasks."""
        proposal = Proposal(
            name=data.name,
            client_id=data.client_id,
            hourly_rate_ars=data.hourly_rate_ars,
            exchange_rate=data.exchange_rate,
            adjustment_percentage=data.adjustment_percentage,
            status=ProposalStatus.DRAFT,
        )
        self.db.add(proposal)
        self.db.flush()

        # Create tasks
        for i, task_data in enumerate(data.tasks):
            task = ProposalTask(
                proposal_id=proposal.id,
                name=task_data.name,
                description=task_data.description,
                hours=task_data.hours,
                sort_order=task_data.sort_order if task_data.sort_order else i,
            )
            self.db.add(task)

        self.db.commit()
        self.db.refresh(proposal)

        # Reload with tasks
        proposal = self.repository.get_with_tasks(proposal.id)
        return self._to_response(proposal)

    def update_proposal(self, proposal_id: int, data: ProposalUpdate) -> ProposalResponse:
        """Update an existing proposal and replace its tasks."""
        proposal = self.repository.get_with_tasks(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado",
            )

        update_data = data.model_dump(exclude_unset=True)
        tasks_data = update_data.pop("tasks", None)

        for field, value in update_data.items():
            setattr(proposal, field, value)

        # Replace tasks if provided
        if tasks_data is not None:
            self.task_repository.delete_by_proposal(proposal_id)
            for i, task_dict in enumerate(tasks_data):
                task = ProposalTask(
                    proposal_id=proposal_id,
                    name=task_dict["name"],
                    description=task_dict.get("description"),
                    hours=task_dict["hours"],
                    sort_order=task_dict.get("sort_order", i),
                )
                self.db.add(task)

        self.db.commit()
        self.db.refresh(proposal)
        proposal = self.repository.get_with_tasks(proposal_id)
        return self._to_response(proposal)

    def update_status(self, proposal_id: int, data: ProposalStatusUpdate) -> ProposalResponse:
        """Update only the status of a proposal."""
        proposal = self.repository.get_with_tasks(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado",
            )

        try:
            proposal.status = ProposalStatus(data.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Debe ser uno de: {', '.join(s.value for s in ProposalStatus)}",
            )

        self.db.commit()
        self.db.refresh(proposal)
        return self._to_response(proposal)

    def delete_proposal(self, proposal_id: int) -> None:
        """Delete a proposal (tasks are cascade deleted)."""
        proposal = self.repository.get(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado",
            )
        self.repository.delete(proposal_id)
