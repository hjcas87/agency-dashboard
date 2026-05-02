"""
Service layer for the Proposal feature.
"""
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.custom.features.proposals.constants import PROPOSAL_VALIDITY_DAYS
from app.custom.features.proposals.messages import (
    ERR_INVALID_STATUS_VALUE,
    ERR_NOT_FOUND,
    ERR_TRANSITION_FORBIDDEN,
    STATUS_LABELS,
)
from app.custom.features.proposals.models import (
    Proposal,
    ProposalCurrency,
    ProposalStatus,
    ProposalTask,
)
from app.custom.features.proposals.repository import ProposalRepository, ProposalTaskRepository
from app.custom.features.proposals.schemas import (
    ProposalCreate,
    ProposalResponse,
    ProposalStatusUpdate,
    ProposalTaskResponse,
    ProposalUpdate,
)

# Allowed status transitions, expressed as a dispatch table from the
# current status to the set of legal target statuses. Encodes the rules
# documented in docs/solution_design/user_stories/proposal_status_change.md:
# - DRAFT can move to any other state.
# - SENT can move to ACCEPTED, REJECTED, or back to DRAFT (re-open).
# - Terminal states (ACCEPTED / REJECTED) can only be re-opened to DRAFT;
#   no direct ACCEPTED <-> REJECTED. The operator has to pass through
#   DRAFT explicitly, which is by design — it forces a deliberate pause.
_ALLOWED_TRANSITIONS: dict[ProposalStatus, frozenset[ProposalStatus]] = {
    ProposalStatus.DRAFT: frozenset(
        {ProposalStatus.SENT, ProposalStatus.ACCEPTED, ProposalStatus.REJECTED}
    ),
    ProposalStatus.SENT: frozenset(
        {ProposalStatus.DRAFT, ProposalStatus.ACCEPTED, ProposalStatus.REJECTED}
    ),
    ProposalStatus.ACCEPTED: frozenset({ProposalStatus.DRAFT}),
    ProposalStatus.REJECTED: frozenset({ProposalStatus.DRAFT}),
}


def _can_transition(current: ProposalStatus, target: ProposalStatus) -> bool:
    """True iff `current → target` is in the allowed-transitions table.
    A no-op transition (current == target) returns True — it's a noop."""
    if current is target:
        return True
    return target in _ALLOWED_TRANSITIONS[current]


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

        sent_at = proposal.sent_at
        if sent_at is not None:
            expiry = sent_at + timedelta(days=PROPOSAL_VALIDITY_DAYS)
            days_until_expiry = (expiry - datetime.now(UTC)).days
        else:
            days_until_expiry = None

        return ProposalResponse(
            id=proposal.id,
            name=proposal.name,
            client_id=proposal.client_id,
            client_name=client_name,
            status=proposal.status.value
            if isinstance(proposal.status, ProposalStatus)
            else proposal.status,
            currency=proposal.currency.value
            if isinstance(proposal.currency, ProposalCurrency)
            else proposal.currency,
            hourly_rate_ars=proposal.hourly_rate_ars,
            exchange_rate=proposal.exchange_rate,
            adjustment_percentage=proposal.adjustment_percentage,
            estimated_days=proposal.estimated_days,
            deliverables_summary=proposal.deliverables_summary,
            total_hours=totals["total_hours"],
            subtotal_ars=totals["subtotal_ars"],
            adjustment_amount_ars=totals["adjustment_amount_ars"],
            total_ars=totals["total_ars"],
            total_usd=totals["total_usd"],
            created_at=proposal.created_at.isoformat() if proposal.created_at else "",
            updated_at=proposal.updated_at.isoformat() if proposal.updated_at else "",
            sent_at=sent_at,
            days_until_expiry=days_until_expiry,
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
                detail=ERR_NOT_FOUND,
            )
        return self._to_response(proposal)

    def create_proposal(self, data: ProposalCreate) -> ProposalResponse:
        """Create a new proposal with its tasks."""
        proposal = Proposal(
            name=data.name,
            client_id=data.client_id,
            currency=ProposalCurrency(data.currency),
            hourly_rate_ars=data.hourly_rate_ars,
            exchange_rate=data.exchange_rate,
            adjustment_percentage=data.adjustment_percentage,
            estimated_days=data.estimated_days,
            deliverables_summary=data.deliverables_summary,
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
                detail=ERR_NOT_FOUND,
            )

        update_data = data.model_dump(exclude_unset=True)
        tasks_data = update_data.pop("tasks", None)
        if "currency" in update_data:
            update_data["currency"] = ProposalCurrency(update_data["currency"])

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
        """Update only the status of a proposal, enforcing the allowed-
        transitions matrix. Rejects invalid transitions with HTTP 400 and
        an operator-friendly message that includes the current and target
        labels in Spanish."""
        proposal = self.repository.get_with_tasks(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERR_NOT_FOUND,
            )

        try:
            target = ProposalStatus(data.status)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERR_INVALID_STATUS_VALUE,
            ) from exc

        current = (
            proposal.status
            if isinstance(proposal.status, ProposalStatus)
            else ProposalStatus(proposal.status)
        )

        if not _can_transition(current, target):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERR_TRANSITION_FORBIDDEN.format(
                    from_status=STATUS_LABELS[current.value],
                    to_status=STATUS_LABELS[target.value],
                ),
            )

        proposal.status = target

        if target in (ProposalStatus.SENT, ProposalStatus.ACCEPTED) and proposal.sent_at is None:
            proposal.sent_at = datetime.now(UTC)
        elif target is ProposalStatus.SENT and current is ProposalStatus.DRAFT:
            proposal.sent_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(proposal)
        return self._to_response(proposal)

    def delete_proposal(self, proposal_id: int) -> None:
        """Delete a proposal (tasks are cascade deleted)."""
        proposal = self.repository.get(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERR_NOT_FOUND,
            )
        self.repository.delete(proposal_id)
