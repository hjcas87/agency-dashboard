"""
Unit tests for ProposalService.update_status — sent_at behaviour.
"""
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.custom.features.proposals.models import Proposal, ProposalStatus
from app.custom.features.proposals.schemas import ProposalStatusUpdate
from app.custom.features.proposals.service import ProposalService


def _make_proposal_mock(status: ProposalStatus, sent_at: datetime | None = None) -> Proposal:
    proposal = MagicMock(spec=Proposal)
    proposal.id = 1
    proposal.name = "Test Proposal"
    proposal.client_id = None
    proposal.status = status
    proposal.sent_at = sent_at
    proposal.hourly_rate_ars = Decimal("1000.00")
    proposal.exchange_rate = Decimal("1000.00")
    proposal.adjustment_percentage = Decimal("0")
    proposal.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    proposal.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    proposal.tasks = []
    return proposal


def _make_service_with_proposal(proposal: Proposal) -> tuple[ProposalService, MagicMock]:
    db = MagicMock()
    svc = ProposalService(db)
    svc.repository = MagicMock()
    svc.repository.get_with_tasks.return_value = proposal

    def _commit_side_effect():
        pass

    def _refresh_side_effect(obj):
        pass

    db.commit.side_effect = _commit_side_effect
    db.refresh.side_effect = _refresh_side_effect
    db.query.return_value.filter.return_value.first.return_value = None
    return svc, db


@pytest.mark.unit
class TestProposalServiceSentAt:
    def test_draft_to_sent_sets_sent_at(self):
        proposal = _make_proposal_mock(ProposalStatus.DRAFT, sent_at=None)
        svc, _ = _make_service_with_proposal(proposal)

        svc.update_status(1, ProposalStatusUpdate(status="sent"))

        assert proposal.sent_at is not None

    def test_draft_to_accepted_sets_sent_at(self):
        proposal = _make_proposal_mock(ProposalStatus.DRAFT, sent_at=None)
        svc, _ = _make_service_with_proposal(proposal)

        svc.update_status(1, ProposalStatusUpdate(status="accepted"))

        assert proposal.sent_at is not None

    def test_resend_updates_sent_at(self):
        first_ts = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        proposal = _make_proposal_mock(ProposalStatus.DRAFT, sent_at=first_ts)
        svc, _ = _make_service_with_proposal(proposal)

        svc.update_status(1, ProposalStatusUpdate(status="sent"))

        assert proposal.sent_at is not None
        assert proposal.sent_at >= first_ts
