"""Pydantic schemas for the dashboard summary endpoint."""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class KpiValue(BaseModel):
    """One KPI tile.

    `current` is the headline number. `previous` is the same metric
    over the immediately prior comparable window — last calendar
    month for monthly KPIs, the prior 90-day window for the
    rolling-90 KPIs. `delta_pct` is `(current - previous) / previous *
    100`, rounded to two decimals; `None` when previous is 0 (we
    don't divide by zero, the UI shows just the headline number).
    """

    model_config = ConfigDict(extra="forbid")

    current: Decimal
    previous: Decimal
    delta_pct: Decimal | None


class ChartPoint(BaseModel):
    """One data point on the area chart — a calendar day with the
    breakdown by comprobante kind. The frontend's existing
    `<ChartAreaInteractive>` switches `7d / 30d / 90d` client-side
    over the full series, so we always return the last 90 days.
    """

    model_config = ConfigDict(extra="forbid")

    date: date
    afip: Decimal
    internos: Decimal


class DashboardSummary(BaseModel):
    """Single round-trip payload feeding the home dashboard.

    The frontend is expected to render four KPI cards and an area
    chart from this object — no further fetches per tile."""

    model_config = ConfigDict(extra="forbid")

    revenue_month: KpiValue
    pending_to_bill: KpiValue
    avg_ticket_month: KpiValue
    active_clients_90d: KpiValue
    chart: list[ChartPoint]
