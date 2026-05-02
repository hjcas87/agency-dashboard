"""
Quote PDF overlay engine.

Renders the dynamic content layer (task list, deliverables summary,
total amount, estimated days) on top of designer-built base PDF
assets and merges everything into a single client-facing booklet.

Typography mirrors the design source: Open Sans 12 pt, white. Bold for
the task loop, the total caption and the estimated-days caption;
Regular for the deliverables summary so the long-form paragraph is
visually distinct from the structured list.

When the task loop overflows the quote_base container, additional
quote_base pages are inserted automatically until every task fits.
"""
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Any
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
from reportlab.platypus import Frame, Paragraph, Spacer

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
FONT_BOLD = "OpenSans-Bold"
FONT_REGULAR = "OpenSans-Regular"
FONT_BOLD_PATH = FONTS_DIR / "OpenSans-Bold.ttf"
FONT_REGULAR_PATH = FONTS_DIR / "OpenSans-Regular.ttf"
FONT_SIZE_PT = 12
LINE_LEADING_PT = 14

# Vertical gap between the bold task title and its (regular-weight)
# description — small and intentional, just enough to detach the
# heading visually without breaking the block.
TITLE_TO_DESC_GAP_CM = 0.15

# Vertical gap between consecutive task blocks on the quote_base page.
# Generous on purpose so each task reads as its own item.
TASK_GAP_CM = 1.0


def _ensure_fonts_registered() -> None:
    """Idempotently register Open Sans Bold + Regular with ReportLab."""
    registered = pdfmetrics.getRegisteredFontNames()
    if FONT_BOLD not in registered:
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(FONT_BOLD_PATH)))
    if FONT_REGULAR not in registered:
        pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(FONT_REGULAR_PATH)))


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


def _build_text_style(font_name: str = FONT_BOLD) -> ParagraphStyle:
    return ParagraphStyle(
        f"QuoteText_{font_name}",
        fontName=font_name,
        fontSize=FONT_SIZE_PT,
        leading=LINE_LEADING_PT,
        textColor=white,
        alignment=TA_LEFT,
        spaceAfter=0,
    )


class QuoteOverlayBuilder:
    """Assembles the client-facing quote PDF.

    The booklet has a fixed structure (cover → quote_base → deliverables
    → terms → final), but the quote_base section can grow to N pages
    depending on how many tasks fit per container.
    """

    def build(self, data: QuoteData) -> bytes:
        """Render the booklet with dynamic content drawn on top of
        each base asset. Returns the merged PDF as raw bytes."""
        _ensure_fonts_registered()
        logger.info("quote.overlay.build.start", extra={"tasks": len(data.tasks)})
        writer = PdfWriter()

        for asset_name in ASSET_ORDER:
            if asset_name == ASSET_QUOTE_BASE:
                for page in self._build_quote_base_pages(data.tasks):
                    writer.add_page(page)
                continue

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
        if asset_name == ASSET_DELIVERABLES:
            return self._render_overlay(lambda c: self._draw_deliverables(c, data))
        return None

    @staticmethod
    def _render_overlay(draw_callback: Callable[[rl_canvas.Canvas], None]) -> PageObject:
        buffer = BytesIO()
        c = rl_canvas.Canvas(buffer, pagesize=A4)
        draw_callback(c)
        c.showPage()
        c.save()
        buffer.seek(0)
        return PdfReader(buffer).pages[0]

    # ── Quote base: paginated task loop ──────────────────────
    def _build_quote_base_pages(self, tasks: list[QuoteTask]) -> list[PageObject]:
        """Render the task list across as many quote_base pages as
        needed. Always returns at least one page so the booklet
        structure is preserved when there are no tasks."""
        if not tasks:
            return [self._read_first_page(ASSET_QUOTE_BASE)]

        remaining = self._build_task_flowables(tasks)
        pages: list[PageObject] = []

        while remaining:
            base_page = self._read_first_page(ASSET_QUOTE_BASE)
            consumed, overlay_page = self._render_task_page(remaining)
            base_page.merge_page(overlay_page)
            pages.append(base_page)

            if consumed == 0:
                # Defensive: a single task larger than the container
                # would loop forever. Drop it with a warning so the
                # rest of the booklet can render.
                logger.warning(
                    "quote.overlay.task.too_large",
                    extra={"page": len(pages), "remaining": len(remaining)},
                )
                remaining = remaining[1:]
            else:
                remaining = remaining[consumed:]

        return pages

    def _render_task_page(self, flowables: list[Any]) -> tuple[int, PageObject]:
        """Render as many flowables as fit into a single quote_base
        page. Returns (consumed_count, overlay_page)."""
        buffer = BytesIO()
        c = rl_canvas.Canvas(buffer, pagesize=A4)
        frame = self._make_inner_frame(QUOTE_BASE_CONTAINER)
        consumed = 0
        for fl in flowables:
            if frame.add(fl, c) == 0:
                break
            consumed += 1
        c.showPage()
        c.save()
        buffer.seek(0)
        return consumed, PdfReader(buffer).pages[0]

    @staticmethod
    def _build_task_flowables(tasks: list[QuoteTask]) -> list[Any]:
        """Build the flowable list for the task loop.

        Title and description are emitted as separate paragraphs so the
        paginator can split a long task across pages if it really has
        to — keeping them together via KeepTogether interacts poorly
        with frame.add() outside a full Platypus document. The visible
        gaps (title→desc, task→task) keep the list readable even in
        that edge case.
        """
        title_style = _build_text_style(FONT_BOLD)
        desc_style = _build_text_style(FONT_REGULAR)
        title_to_desc = cm_to_pt(TITLE_TO_DESC_GAP_CM)
        task_gap = cm_to_pt(TASK_GAP_CM)

        flowables: list[Any] = []
        for i, task in enumerate(tasks, start=1):
            flowables.append(Paragraph(f"{i} - {escape(task.name).upper()}", title_style))
            if task.description:
                flowables.append(Spacer(1, title_to_desc))
                flowables.append(Paragraph(escape(task.description), desc_style))
            if i < len(tasks):
                flowables.append(Spacer(1, task_gap))
        return flowables

    # ── Deliverables page ────────────────────────────────────
    @staticmethod
    def _draw_deliverables(c: rl_canvas.Canvas, data: QuoteData) -> None:
        if data.deliverables_summary:
            html = escape(data.deliverables_summary).replace("\n", "<br/>")
            QuoteOverlayBuilder._draw_paragraph_in_zone(
                c, DELIVERABLES_CONTAINER, html, _build_text_style(FONT_REGULAR)
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
        c.setFont(FONT_BOLD, FONT_SIZE_PT)
        c.setFillColor(white)
        c.drawRightString(right_x, y, text)

    @staticmethod
    def _draw_days(c: rl_canvas.Canvas, days: str) -> None:
        zone = DELIVERABLES_DAYS_FIELD
        x = cm_to_pt(zone.left_cm)
        y = top_to_y_pt(zone.top_cm, zone.height_cm) + cm_to_pt(zone.height_cm) * 0.2
        c.setFont(FONT_BOLD, FONT_SIZE_PT)
        c.setFillColor(white)
        c.drawString(x, y, days)

    # ── Shared paragraph layout ──────────────────────────────
    @staticmethod
    def _make_inner_frame(zone: LayoutZone) -> Frame:
        pad = cm_to_pt(zone.inner_padding_cm)
        x = cm_to_pt(zone.left_cm) + pad
        y = top_to_y_pt(zone.top_cm, zone.height_cm) + pad
        w = cm_to_pt(zone.width_cm) - 2 * pad
        h = cm_to_pt(zone.height_cm) - 2 * pad
        return Frame(
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

    @staticmethod
    def _draw_paragraph_in_zone(
        c: rl_canvas.Canvas, zone: LayoutZone, html: str, style: ParagraphStyle
    ) -> None:
        frame = QuoteOverlayBuilder._make_inner_frame(zone)
        frame.add(Paragraph(html, style), c)
