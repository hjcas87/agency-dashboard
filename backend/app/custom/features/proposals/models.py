"""
SQLAlchemy models for the Proposal feature.
"""
import enum
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProposalStatus(str, enum.Enum):
    """Status values for proposals."""

    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return self.value


class Proposal(Base):
    """Proposal model representing a commercial quote."""

    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    status = Column(
        Enum(ProposalStatus, values_callable=lambda e: [x.value for x in e], name='proposalstatus'),
        nullable=False,
        server_default="draft",
    )
    hourly_rate_ars = Column(Numeric(12, 2), nullable=False)
    exchange_rate = Column(Numeric(12, 2), nullable=False)
    adjustment_percentage = Column(Numeric(6, 2), nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tasks = relationship("ProposalTask", back_populates="proposal", cascade="all, delete-orphan", lazy="select")

    def __repr__(self) -> str:
        return f"<Proposal(id={self.id}, name='{self.name}', status='{self.status}')>"


class ProposalTask(Base):
    """Individual task/line item within a proposal."""

    __tablename__ = "proposal_tasks"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    hours = Column(Numeric(8, 2), nullable=False)
    sort_order = Column(Integer, nullable=False, server_default="0")

    proposal = relationship("Proposal", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<ProposalTask(id={self.id}, name='{self.name}', hours={self.hours})>"
