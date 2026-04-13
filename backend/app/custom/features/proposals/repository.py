"""
Repository for Proposal data access.
"""
from sqlalchemy.orm import Session

from app.custom.features.proposals.models import Proposal, ProposalTask
from app.shared.repositories.base_repository import BaseRepository


class ProposalRepository(BaseRepository[Proposal]):
    """Repository for Proposal CRUD operations."""

    def __init__(self, db: Session):
        super().__init__(Proposal, db)

    def get_with_tasks(self, proposal_id: int) -> Proposal | None:
        """Get a proposal with its tasks eagerly loaded."""
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(Proposal)
            .options(joinedload(Proposal.tasks))
            .filter(Proposal.id == proposal_id)
            .first()
        )

    def get_all_with_relations(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Proposal]:
        """Get all proposals with tasks eagerly loaded."""
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(Proposal)
            .options(joinedload(Proposal.tasks))
            .order_by(Proposal.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class ProposalTaskRepository(BaseRepository[ProposalTask]):
    """Repository for ProposalTask CRUD operations."""

    def __init__(self, db: Session):
        super().__init__(ProposalTask, db)

    def get_by_proposal(self, proposal_id: int) -> list[ProposalTask]:
        """Get all tasks for a specific proposal."""
        return (
            self.db.query(ProposalTask)
            .filter(ProposalTask.proposal_id == proposal_id)
            .order_by(ProposalTask.sort_order)
            .all()
        )

    def delete_by_proposal(self, proposal_id: int) -> None:
        """Delete all tasks for a specific proposal."""
        self.db.query(ProposalTask).filter(
            ProposalTask.proposal_id == proposal_id
        ).delete()
