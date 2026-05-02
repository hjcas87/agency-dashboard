"""
Quote PDF overlay engine.

Generates the 5-page client-facing quote booklet by drawing a
ReportLab-generated transparent layer on top of each base PDF asset
and merging the result with `pypdf`.

Right now only `build_debug()` is wired up — it paints every layout
zone in red so the operator can visually validate the coordinate
system before any text rendering is added.
"""
from io import BytesIO
from pathlib import Path

from pypdf import PageObject, PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from app.core.logging_config import get_logger
from app.custom.features.proposals.quote.layout import (
    A4_HEIGHT_CM,
    ASSET_ORDER,
    ZONES_BY_ASSET,
    LayoutZone,
)

logger = get_logger(__name__)

ASSETS_DIR = Path(__file__).parent / "assets"

# ── Debug palette ───────────────────────────────────────────────
# Container fill is intentionally lighter than field fill so the
# operator can immediately tell apart the "useful area" from a
# concrete one-liner field.
_CONTAINER_FILL = Color(1, 0, 0, alpha=0.15)
_CONTAINER_BORDER = Color(0.85, 0, 0, alpha=1.0)
_INNER_BORDER = Color(0.5, 0, 0, alpha=0.9)
_FIELD_FILL = Color(1, 0, 0, alpha=0.40)
_FIELD_BORDER = Color(0.85, 0, 0, alpha=1.0)

_BORDER_WIDTH_PT = 0.8
_INNER_DASH = (3, 2)


def cm_to_pt(value_cm: float) -> float:
    """Convert centimeters to PDF points (1 cm == 28.3464 pt)."""
    return value_cm * cm


def top_to_y_pt(top_cm: float, height_cm: float) -> float:
    """
    Convert a top-down vertical coordinate (cm from the page's top
    edge) into ReportLab's bottom-up y-axis (points).

    Args:
        top_cm: Distance from the page's top edge to the box's top.
        height_cm: Height of the box.

    Returns:
        y-coordinate in points of the box's lower-left corner.
    """
    return cm_to_pt(A4_HEIGHT_CM - top_cm - height_cm)


class QuoteOverlayBuilder:
    """
    Assembles the client-facing quote PDF on top of the 5 base assets.

    The class is intentionally split between transport (reading
    assets, merging pages, emitting bytes) and content (currently
    only the debug painter, but `_paint_zone` is the seam where the
    real text-rendering layer will plug in next).
    """

    def build_debug(self) -> bytes:
        """
        Build the 5-page booklet with every registered layout zone
        painted in red.

        Pages without registered zones (cover, terms, final) are
        emitted untouched so the operator validates layout in the
        same flow that real users will see.

        Returns:
            PDF file as bytes.
        """
        logger.info("quote.overlay.debug.start", extra={"pages": len(ASSET_ORDER)})
        writer = PdfWriter()

        for asset_name in ASSET_ORDER:
            base_page = self._read_first_page(asset_name)
            zones = ZONES_BY_ASSET.get(asset_name, ())
            if zones:
                overlay_page = self._build_debug_page(zones)
                base_page.merge_page(overlay_page)
            writer.add_page(base_page)

        return self._writer_to_bytes(writer)

    # ── Internal: I/O ──────────────────────────────────────────
    @staticmethod
    def _read_first_page(asset_name: str) -> PageObject:
        path = ASSETS_DIR / asset_name
        reader = PdfReader(str(path))
        return reader.pages[0]

    @staticmethod
    def _writer_to_bytes(writer: PdfWriter) -> bytes:
        buffer = BytesIO()
        writer.write(buffer)
        return buffer.getvalue()

    # ── Internal: drawing ─────────────────────────────────────
    def _build_debug_page(self, zones: tuple[LayoutZone, ...]) -> PageObject:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        for zone in zones:
            self._paint_zone(c, zone)
        c.showPage()
        c.save()
        buffer.seek(0)
        return PdfReader(buffer).pages[0]

    @staticmethod
    def _paint_zone(c: canvas.Canvas, zone: LayoutZone) -> None:
        x = cm_to_pt(zone.left_cm)
        y = top_to_y_pt(zone.top_cm, zone.height_cm)
        w = cm_to_pt(zone.width_cm)
        h = cm_to_pt(zone.height_cm)

        is_container = zone.inner_padding_cm > 0
        c.setFillColor(_CONTAINER_FILL if is_container else _FIELD_FILL)
        c.setStrokeColor(_CONTAINER_BORDER if is_container else _FIELD_BORDER)
        c.setLineWidth(_BORDER_WIDTH_PT)
        c.rect(x, y, w, h, stroke=1, fill=1)

        if is_container:
            QuoteOverlayBuilder._paint_inner_border(c, zone)

    @staticmethod
    def _paint_inner_border(c: canvas.Canvas, zone: LayoutZone) -> None:
        pad = cm_to_pt(zone.inner_padding_cm)
        x = cm_to_pt(zone.left_cm) + pad
        y = top_to_y_pt(zone.top_cm, zone.height_cm) + pad
        w = cm_to_pt(zone.width_cm) - 2 * pad
        h = cm_to_pt(zone.height_cm) - 2 * pad

        c.saveState()
        c.setStrokeColor(_INNER_BORDER)
        c.setDash(*_INNER_DASH)
        c.setLineWidth(_BORDER_WIDTH_PT)
        c.rect(x, y, w, h, stroke=1, fill=0)
        c.restoreState()
