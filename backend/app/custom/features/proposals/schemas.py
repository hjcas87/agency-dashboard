"""
Pydantic schemas for the Proposal feature.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

# ── ProposalTask schemas ─────────────────────────────────────────


class ProposalTaskCreate(BaseModel):
    """Schema for creating a proposal task."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    hours: Decimal = Field(..., gt=0)
    sort_order: int = 0


class ProposalTaskResponse(BaseModel):
    """Schema returned for a proposal task."""

    id: int
    proposal_id: int
    name: str
    description: str | None
    hours: Decimal
    sort_order: int

    class Config:
        from_attributes = True


class ProposalTaskUpdate(BaseModel):
    """Schema for updating a proposal task."""

    name: str | None = None
    description: str | None = None
    hours: Decimal | None = Field(None, gt=0)
    sort_order: int | None = None


# ── Proposal schemas ─────────────────────────────────────────────


# Empirical fit of the deliverables_summary container measured at
# 12 pt / leading 14 / ~448 pt wide × 283 pt tall: ~1420 chars worst-
# case, ~1469 chars on realistic prose. We cap at 1300 to keep ~9 %
# safety against operator-typed line breaks that consume more vertical
# space than the average word-wrapped line.
DELIVERABLES_SUMMARY_MAX_CHARS = 1300


class ProposalCreate(BaseModel):
    """Schema for creating a proposal."""

    name: str = Field(..., min_length=1, max_length=255)
    client_id: int | None = None
    currency: str = Field(default="ARS", pattern="^(ARS|USD)$")
    hourly_rate_ars: Decimal = Field(..., gt=0)
    exchange_rate: Decimal = Field(..., gt=0)
    adjustment_percentage: Decimal = Field(default=0, ge=-100, le=100)
    estimated_days: str | None = Field(default=None, max_length=64)
    deliverables_summary: str | None = Field(
        default=None, max_length=DELIVERABLES_SUMMARY_MAX_CHARS
    )
    tasks: list[ProposalTaskCreate] = Field(..., min_length=1)


class ProposalUpdate(BaseModel):
    """Schema for updating a proposal."""

    name: str | None = Field(None, min_length=1, max_length=255)
    client_id: int | None = None
    currency: str | None = Field(default=None, pattern="^(ARS|USD)$")
    hourly_rate_ars: Decimal | None = Field(None, gt=0)
    exchange_rate: Decimal | None = Field(None, gt=0)
    adjustment_percentage: Decimal | None = Field(None, ge=-100, le=100)
    estimated_days: str | None = Field(default=None, max_length=64)
    deliverables_summary: str | None = Field(
        default=None, max_length=DELIVERABLES_SUMMARY_MAX_CHARS
    )
    tasks: list[ProposalTaskCreate] | None = None


class ProposalStatusUpdate(BaseModel):
    """Schema for updating only the proposal status."""

    status: str = Field(..., pattern="^(draft|sent|accepted|rejected)$")


class ProposalResponse(BaseModel):
    """Schema returned for a proposal with calculated totals."""

    id: int
    name: str
    client_id: int | None
    client_name: str | None = None
    status: str
    currency: str
    hourly_rate_ars: Decimal
    exchange_rate: Decimal
    adjustment_percentage: Decimal
    estimated_days: str | None = None
    deliverables_summary: str | None = None
    total_hours: Decimal
    subtotal_ars: Decimal
    adjustment_amount_ars: Decimal
    total_ars: Decimal
    total_usd: Decimal
    created_at: str
    updated_at: str
    sent_at: datetime | None = None
    days_until_expiry: int | None = None
    tasks: list[ProposalTaskResponse] = []

    class Config:
        from_attributes = True
