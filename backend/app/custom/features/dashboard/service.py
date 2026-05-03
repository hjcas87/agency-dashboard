"""Service layer for the dashboard summary.

Aggregates invoice, proposal and client tables into the four KPIs
the home dashboard needs:

- `revenue_month`         — facturado del mes calendario actual
                             (Facturas AFIP + Comprobantes X, no
                             anuladas), comparado contra el mes
                             pasado.
- `pending_to_bill`       — saldo restante de cada presupuesto
                             aceptado con `remaining > 0`.
- `avg_ticket_month`      — ticket promedio (sum / count) del mes
                             calendario actual.
- `active_clients_90d`    — clientes distintos con al menos una
                             factura en los últimos 90 días.

Plus 90 daily points for the area chart (AFIP vs internos).
"""
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.custom.features.dashboard.schemas import ChartPoint, DashboardSummary, KpiValue
from app.custom.features.invoices.models import Invoice
from app.custom.features.proposals.models import Proposal, ProposalStatus
from app.custom.features.proposals.service import ProposalService

# How long the "active clients" window stretches back. 90 days is the
# canonical SaaS "active user" definition; for an invoicing context it
# also matches the AFIP threshold for considering a client recurring.
_ACTIVE_WINDOW_DAYS = 90

# Days plotted in the chart. Frontend already filters down to 7/30/90
# client-side via the existing toggle, so we always emit the longest
# window and let the UI slice it.
_CHART_WINDOW_DAYS = 90


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def summary(self) -> DashboardSummary:
        today = datetime.now(tz=UTC).date()
        month_start, month_end = _month_bounds(today)
        prev_month_start, prev_month_end = _month_bounds(month_start - timedelta(days=1))

        revenue_curr = self._sum_invoices_in_range(month_start, month_end)
        revenue_prev = self._sum_invoices_in_range(prev_month_start, prev_month_end)

        avg_curr = self._avg_invoice_in_range(month_start, month_end)
        avg_prev = self._avg_invoice_in_range(prev_month_start, prev_month_end)

        pending_curr = self._pending_to_bill()
        # `pending_to_bill` is a snapshot of "what's currently
        # outstanding". A "previous" snapshot would need a historical
        # backup — for now we show the headline without delta. Schema
        # still expects two Decimals, so we mirror current as previous
        # and emit `None` for the delta.
        pending_prev = pending_curr

        active_curr = self._active_clients(today, _ACTIVE_WINDOW_DAYS)
        active_prev = self._active_clients(
            today - timedelta(days=_ACTIVE_WINDOW_DAYS), _ACTIVE_WINDOW_DAYS
        )

        chart = self._chart_points(today, _CHART_WINDOW_DAYS)

        return DashboardSummary(
            revenue_month=_kpi(revenue_curr, revenue_prev),
            pending_to_bill=KpiValue(current=pending_curr, previous=pending_prev, delta_pct=None),
            avg_ticket_month=_kpi(avg_curr, avg_prev),
            active_clients_90d=_kpi(Decimal(active_curr), Decimal(active_prev)),
            chart=chart,
        )

    # ── Invoice aggregations ─────────────────────────────────────

    def _sum_invoices_in_range(self, start: date, end: date) -> Decimal:
        """Total billed in [start, end] inclusive — both AFIP and X,
        excluding anything cancelled. NCs themselves are filtered out
        by the cancelled_at filter on the original (the NC row carries
        `cancels_invoice_id` but the parent's cancelled_at is set, so
        the parent stops counting; the NC itself is NOT a revenue
        event and we filter it out by `cancels_invoice_id IS NULL`)."""
        result = (
            self.db.query(func.coalesce(func.sum(Invoice.total_amount_ars), 0))
            .filter(
                Invoice.issue_date >= start,
                Invoice.issue_date <= end,
                Invoice.cancelled_at.is_(None),
                Invoice.cancels_invoice_id.is_(None),
            )
            .scalar()
        )
        return Decimal(result or 0)

    def _avg_invoice_in_range(self, start: date, end: date) -> Decimal:
        """Average invoice amount in the same window. Returns 0 when
        there are no invoices (dividing-by-zero is the consumer's
        problem, not the database's)."""
        result = (
            self.db.query(func.avg(Invoice.total_amount_ars))
            .filter(
                Invoice.issue_date >= start,
                Invoice.issue_date <= end,
                Invoice.cancelled_at.is_(None),
                Invoice.cancels_invoice_id.is_(None),
            )
            .scalar()
        )
        return Decimal(result or 0).quantize(Decimal("0.01"))

    def _active_clients(self, anchor: date, window_days: int) -> int:
        """Count of distinct clients with at least one non-cancelled
        invoice in `[anchor - window_days, anchor]`."""
        start = anchor - timedelta(days=window_days)
        result = (
            self.db.query(func.count(func.distinct(Invoice.client_id)))
            .filter(
                Invoice.issue_date >= start,
                Invoice.issue_date <= anchor,
                Invoice.cancelled_at.is_(None),
                Invoice.cancels_invoice_id.is_(None),
                Invoice.client_id.isnot(None),
            )
            .scalar()
        )
        return int(result or 0)

    def _pending_to_bill(self) -> Decimal:
        """Sum of remaining balances across every accepted proposal.
        Mirrors `InvoiceRepository.invoiced_amount_for_proposal` per
        proposal — the per-proposal logic lives there and is the
        canonical "invoiced amount" definition."""
        proposals = self.db.query(Proposal).filter(Proposal.status == ProposalStatus.ACCEPTED).all()
        total = Decimal("0")
        for p in proposals:
            totals = ProposalService.calculate_totals(p, list(p.tasks))
            proposal_total = Decimal(totals["total_ars"])
            invoiced = self._invoiced_amount_for_proposal(p.id)
            remaining = (proposal_total - invoiced).quantize(Decimal("0.01"))
            if remaining > 0:
                total += remaining
        return total

    def _invoiced_amount_for_proposal(self, proposal_id: int) -> Decimal:
        result = (
            self.db.query(func.coalesce(func.sum(Invoice.total_amount_ars), 0))
            .filter(
                Invoice.proposal_id == proposal_id,
                Invoice.cancelled_at.is_(None),
            )
            .scalar()
        )
        return Decimal(result or 0)

    # ── Chart series ─────────────────────────────────────────────

    def _chart_points(self, anchor: date, window_days: int) -> list[ChartPoint]:
        """One point per calendar day in `[anchor - window_days,
        anchor]`. AFIP and X are summed into separate series so the
        existing two-series `<ChartAreaInteractive>` only needs a key
        rename. Days with no activity carry zeros — the chart is
        cleaner with a continuous x-axis."""
        start = anchor - timedelta(days=window_days)

        # Pull both kinds in two grouped queries (cheaper than rebuilding
        # a Python pivot from a single query). The result is a dict
        # `date -> Decimal`.
        afip_rows = (
            self.db.query(
                Invoice.issue_date,
                func.coalesce(func.sum(Invoice.total_amount_ars), 0),
            )
            .filter(
                Invoice.issue_date >= start,
                Invoice.issue_date <= anchor,
                Invoice.cancelled_at.is_(None),
                Invoice.cancels_invoice_id.is_(None),
                Invoice.is_internal.is_(False),
            )
            .group_by(Invoice.issue_date)
            .all()
        )
        internos_rows = (
            self.db.query(
                Invoice.issue_date,
                func.coalesce(func.sum(Invoice.total_amount_ars), 0),
            )
            .filter(
                Invoice.issue_date >= start,
                Invoice.issue_date <= anchor,
                Invoice.cancelled_at.is_(None),
                Invoice.is_internal.is_(True),
            )
            .group_by(Invoice.issue_date)
            .all()
        )
        afip_map = {row[0]: Decimal(row[1] or 0) for row in afip_rows}
        internos_map = {row[0]: Decimal(row[1] or 0) for row in internos_rows}

        points: list[ChartPoint] = []
        cursor = start
        while cursor <= anchor:
            points.append(
                ChartPoint(
                    date=cursor,
                    afip=afip_map.get(cursor, Decimal("0")),
                    internos=internos_map.get(cursor, Decimal("0")),
                )
            )
            cursor += timedelta(days=1)
        return points


# ── Pure helpers ─────────────────────────────────────────────────


def _month_bounds(reference: date) -> tuple[date, date]:
    """First and last calendar day of the month containing `reference`."""
    start = reference.replace(day=1)
    if start.month == 12:
        next_month_first = start.replace(year=start.year + 1, month=1)
    else:
        next_month_first = start.replace(month=start.month + 1)
    end = next_month_first - timedelta(days=1)
    return start, end


def _kpi(current: Decimal, previous: Decimal) -> KpiValue:
    """Build a `KpiValue` with a properly-rounded delta or None when
    the previous period is zero (no division-by-zero allowed; the UI
    interprets `None` as "no comparison available yet")."""
    if previous == 0:
        delta = None
    else:
        delta = ((current - previous) / previous * Decimal("100")).quantize(Decimal("0.01"))
    return KpiValue(current=current, previous=previous, delta_pct=delta)
