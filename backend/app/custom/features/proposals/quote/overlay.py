"""
Quote PDF overlay engine.

Renders the dynamic content layer (task list, deliverables summary,
total amount, estimated days) on top of 5 designer-built base PDF
assets and merges everything into a single 5-page client booklet.

Text style is fixed by the design source: Open Sans Bold, 12 pt, white.
Layout zones live in `layout.py` and every drawing is scoped to those
zones — nothing is drawn outside them.
"""
from dataclasses import dataclass
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PageObject, PdfReader, PdfWriter
from reportlab.lib.colors import white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Frame, Paragraph

from app.core.logging_config import get_logger
from app.custom.features.proposals.quote.layout import (
    A4_HEIGHT_CM,
    A4_WIDTH_CM,
    ASSET_DELIVERABLES,
    ASSET_ORDER,
    ASSET_QUOTE_BASE,
    DELIVERABLES_CONTAINER,
    DELIVERABLES_DAYS_FIELD,
    DELIVERABLES_TOTAL_FIELD,
    DELIVERABLES_TOTAL_RIGHT_MARGIN_CM,
    QUOTE_BASE_CONTAINER,
    LayoutZone,
)

logger = get_logger(__name__)

ASSETS_DIR = Path(__file__).parent / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# ── Typography (mirrors the design source) ──────────────────────
FONT_NAME = "OpenSans-Bold"
FONT_PATH = FONTS_DIR / "OpenSans-Bold.ttf"
FONT_SIZE_PT = 12
LINE_LEADING_PT = 14


def _ensure_font_registered() -> None:
    """Idempotently register Open Sans Bold with ReportLab."""
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


# ── Coordinate helpers ──────────────────────────────────────────
def cm_to_pt(value_cm: float) -> float:
    """Convert centimeters to PDF points (1 cm == 28.3464 pt)."""
    return value_cm * cm


def top_to_y_pt(top_cm: float, height_cm: float) -> float:
    """Convert a top-down vertical coord (cm from page top) to
    ReportLab's bottom-up y-axis (points)."""
    return cm_to_pt(A4_HEIGHT_CM - top_cm - height_cm)


# ── Public data shape ───────────────────────────────────────────
@dataclass(frozen=True)
class QuoteTask:
    """A single task as rendered on the quote_base page."""

    name: str
    description: str | None


@dataclass(frozen=True)
class QuoteData:
    """Everything the overlay needs to render a quote.

    Decoupled from SQLAlchemy models on purpose so the builder is
    testable and independent of the persistence layer.
    """

    tasks: list[QuoteTask]
    deliverables_summary: str | None
    estimated_days: str | None
    total_amount: Decimal
    currency: str


# ── Currency formatting (es-AR) ─────────────────────────────────
def _format_amount_ar(amount: Decimal) -> str:
    """Format a decimal as `1.234.567,89` (AR thousands/decimal)."""
    fmt = f"{amount:,.2f}"
    return fmt.replace(",", "X").replace(".", ",").replace("X", ".")


def format_total_text(amount: Decimal, currency: str) -> str:
    """Build the right-aligned total caption."""
    body = _format_amount_ar(amount)
    if currency == "USD":
        return f"TOTAL: US$ {body}"
    return f"TOTAL: $ {body} ARS"


def _build_text_style() -> ParagraphStyle:
    return ParagraphStyle(
        "QuoteText",
        fontName=FONT_NAME,
        fontSize=FONT_SIZE_PT,
        leading=LINE_LEADING_PT,
        textColor=white,
        alignment=TA_LEFT,
        spaceAfter=0,
    )


class QuoteOverlayBuilder:
    """Assembles the 5-page client-facing quote PDF."""

    def build(self, data: QuoteData) -> bytes:
        """Render the booklet with dynamic content drawn on top of
        each base asset. Returns the merged PDF as raw bytes."""
        _ensure_font_registered()
        logger.info("quote.overlay.build.start", extra={"pages": len(ASSET_ORDER)})
        writer = PdfWriter()

        for asset_name in ASSET_ORDER:
            base_page = self._read_first_page(asset_name)
            overlay_page = self._build_overlay_for_asset(asset_name, data)
            if overlay_page is not None:
                base_page.merge_page(overlay_page)
            writer.add_page(base_page)

        return self._writer_to_bytes(writer)

    # ── I/O ───────────────────────────────────────────────────
    @staticmethod
    def _read_first_page(asset_name: str) -> PageObject:
        path = ASSETS_DIR / asset_name
        return PdfReader(str(path)).pages[0]

    @staticmethod
    def _writer_to_bytes(writer: PdfWriter) -> bytes:
        buffer = BytesIO()
        writer.write(buffer)
        return buffer.getvalue()

    # ── Per-asset overlay dispatcher ─────────────────────────
    def _build_overlay_for_asset(self, asset_name: str, data: QuoteData) -> PageObject | None:
        if asset_name == ASSET_QUOTE_BASE:
            return self._render_overlay(lambda c: self._draw_task_loop(c, data.tasks))
        if asset_name == ASSET_DELIVERABLES:
            return self._render_overlay(lambda c: self._draw_deliverables(c, data))
        return None

    @staticmethod
    def _render_overlay(draw_callback) -> PageObject:
        buffer = BytesIO()
        c = rl_canvas.Canvas(buffer, pagesize=A4)
        draw_callback(c)
        c.showPage()
        c.save()
        buffer.seek(0)
        return PdfReader(buffer).pages[0]

    # ── Drawing: quote_base task loop ────────────────────────
    @staticmethod
    def _draw_task_loop(c: rl_canvas.Canvas, tasks: list[QuoteTask]) -> None:
        if not tasks:
            return
        html = QuoteOverlayBuilder._tasks_to_html(tasks)
        QuoteOverlayBuilder._draw_paragraph_in_zone(
            c, QUOTE_BASE_CONTAINER, html, _build_text_style()
        )

    @staticmethod
    def _tasks_to_html(tasks: list[QuoteTask]) -> str:
        lines: list[str] = []
        for i, task in enumerate(tasks, start=1):
            lines.append(f"{i} - {escape(task.name).upper()}")
            if task.description:
                lines.append(escape(task.description))
            lines.append("")
        while lines and not lines[-1]:
            lines.pop()
        return "<br/>".join(lines)

    # ── Drawing: deliverables page ───────────────────────────
    @staticmethod
    def _draw_deliverables(c: rl_canvas.Canvas, data: QuoteData) -> None:
        if data.deliverables_summary:
            html = escape(data.deliverables_summary).replace("\n", "<br/>")
            QuoteOverlayBuilder._draw_paragraph_in_zone(
                c, DELIVERABLES_CONTAINER, html, _build_text_style()
            )

        QuoteOverlayBuilder._draw_total(c, data.total_amount, data.currency)

        if data.estimated_days:
            QuoteOverlayBuilder._draw_days(c, data.estimated_days)

    @staticmethod
    def _draw_total(c: rl_canvas.Canvas, amount: Decimal, currency: str) -> None:
        text = format_total_text(amount, currency)
        right_x = cm_to_pt(A4_WIDTH_CM - DELIVERABLES_TOTAL_RIGHT_MARGIN_CM)
        zone = DELIVERABLES_TOTAL_FIELD
        # Bias the baseline up by 20% of the rect height so the glyph
        # tops align with the visual centre of the line — descenders
        # land in the bottom 20%.
        y = top_to_y_pt(zone.top_cm, zone.height_cm) + cm_to_pt(zone.height_cm) * 0.2
        c.setFont(FONT_NAME, FONT_SIZE_PT)
        c.setFillColor(white)
        c.drawRightString(right_x, y, text)

    @staticmethod
    def _draw_days(c: rl_canvas.Canvas, days: str) -> None:
        zone = DELIVERABLES_DAYS_FIELD
        x = cm_to_pt(zone.left_cm)
        y = top_to_y_pt(zone.top_cm, zone.height_cm) + cm_to_pt(zone.height_cm) * 0.2
        c.setFont(FONT_NAME, FONT_SIZE_PT)
        c.setFillColor(white)
        c.drawString(x, y, days)

    # ── Shared paragraph layout ──────────────────────────────
    @staticmethod
    def _draw_paragraph_in_zone(
        c: rl_canvas.Canvas, zone: LayoutZone, html: str, style: ParagraphStyle
    ) -> None:
        pad = cm_to_pt(zone.inner_padding_cm)
        x = cm_to_pt(zone.left_cm) + pad
        y = top_to_y_pt(zone.top_cm, zone.height_cm) + pad
        w = cm_to_pt(zone.width_cm) - 2 * pad
        h = cm_to_pt(zone.height_cm) - 2 * pad
        frame = Frame(
            x,
            y,
            w,
            h,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )
        frame.add(Paragraph(html, style), c)
