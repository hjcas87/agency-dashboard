"""
SQLAlchemy models for the Proposal feature.

Uses SQLAlchemy 2.x `Mapped[...]` / `mapped_column(...)` declarations so
attribute access yields plain types instead of `Column[T]`.
"""
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
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


class ProposalCurrency(str, enum.Enum):
    """Currency the proposal is presented in to the client."""

    ARS = "ARS"
    USD = "USD"

    def __str__(self) -> str:
        return self.value


class Proposal(Base):
    """Proposal model representing a commercial quote."""

    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[ProposalStatus] = mapped_column(
        Enum(
            ProposalStatus,
            values_callable=lambda e: [x.value for x in e],
            name="proposalstatus",
        ),
        nullable=False,
        server_default="draft",
    )
    currency: Mapped[ProposalCurrency] = mapped_column(
        Enum(
            ProposalCurrency,
            values_callable=lambda e: [x.value for x in e],
            name="proposalcurrency",
        ),
        nullable=False,
        server_default="ARS",
    )
    hourly_rate_ars: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    adjustment_percentage: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False, server_default="0"
    )
    estimated_days: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deliverables_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tasks: Mapped[list["ProposalTask"]] = relationship(
        "ProposalTask",
        back_populates="proposal",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Proposal(id={self.id}, name='{self.name}', status='{self.status}')>"


class ProposalTask(Base):
    """Individual task/line item within a proposal."""

    __tablename__ = "proposal_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    proposal_id: Mapped[int] = mapped_column(
        ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    hours: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    sort_order: Mapped[int] = mapped_column(nullable=False, server_default="0")

    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<ProposalTask(id={self.id}, name='{self.name}', hours={self.hours})>"
