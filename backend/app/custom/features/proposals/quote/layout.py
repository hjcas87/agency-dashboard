"""
Quote PDF layout constants.

All measurements are expressed in centimeters from the TOP-LEFT corner
of an A4 page (29.7 cm tall, 21.0 cm wide). The overlay engine in
`overlay.py` converts this top-down system to ReportLab's bottom-up
y-axis at draw time so the rest of the codebase can keep thinking in
the same units used to design the base PDFs.
"""

from dataclasses import dataclass

# ── Page dimensions (A4) ────────────────────────────────────────
A4_WIDTH_CM = 21.0
A4_HEIGHT_CM = 29.7

# Default text-line height used to size single-line fields when the
# layout doesn't specify one explicitly. Generous enough to stay
# visible during debug overlays without overlapping neighbouring rows.
LINE_HEIGHT_CM = 0.6


@dataclass(frozen=True)
class LayoutZone:
    """
    A rectangular area on a page, expressed top-down in centimeters.

    Attributes:
        name: Stable identifier used for logging and debug overlays.
        top_cm: Distance from the page's top edge to the box's top.
        left_cm: Distance from the page's left edge to the box's left.
        width_cm: Width of the box.
        height_cm: Height of the box.
        inner_padding_cm: Additional padding applied inside the box
            before any content is drawn. ``0`` means the zone is
            treated as a single-line field with no inner area.
    """

    name: str
    top_cm: float
    left_cm: float
    width_cm: float
    height_cm: float
    inner_padding_cm: float = 0.0


# ── Asset filenames (in the order the booklet is assembled) ─────
ASSET_COVER = "cover_page.pdf"
ASSET_QUOTE_BASE = "quote_base.pdf"
ASSET_DELIVERABLES = "deliverables_summary.pdf"
ASSET_TERMS = "terms_conditions.pdf"
ASSET_FINAL = "final_page.pdf"

ASSET_ORDER: tuple[str, ...] = (
    ASSET_COVER,
    ASSET_QUOTE_BASE,
    ASSET_DELIVERABLES,
    ASSET_TERMS,
    ASSET_FINAL,
)

# ── cover_page.pdf ──────────────────────────────────────────────
# Reference code printed in white at the bottom-left of the cover —
# precedes a "#" character at draw time. fs 14.2 pt.
COVER_CODE_FIELD = LayoutZone(
    name="cover.code",
    top_cm=27.2,
    left_cm=2.0,
    width_cm=4.5,
    height_cm=0.8,
)

# Big red issue date stacked across three lines (dd / mm / yy). The
# layout box reserves enough vertical room for the 58.3 pt glyphs at
# leading 60 pt × 3 lines.
COVER_DATE_FIELD = LayoutZone(
    name="cover.date",
    top_cm=16.5,
    left_cm=15.0,
    width_cm=4.5,
    height_cm=6.5,
)

# "PREPARADO PARA:" fixed label, fs 14.2 pt white. Optional pair with
# the recipient name field below.
COVER_RECIPIENT_LABEL_FIELD = LayoutZone(
    name="cover.recipient.label",
    top_cm=25.0,
    left_cm=13.0,
    width_cm=6.5,
    height_cm=0.8,
)

# Recipient line — wraps up to 19.5 cm from the page's left edge so
# longer "Name - Company" combinations don't run off the design.
COVER_RECIPIENT_NAME_FIELD = LayoutZone(
    name="cover.recipient.name",
    top_cm=27.0,
    left_cm=13.0,
    width_cm=6.5,
    height_cm=2.0,
)

# ── quote_base.pdf ──────────────────────────────────────────────
QUOTE_BASE_CONTAINER = LayoutZone(
    name="quote_base.container",
    top_cm=4.9,
    left_cm=1.1,
    width_cm=18.8,
    height_cm=21.2,
    inner_padding_cm=0.5,
)

# ── deliverables_summary.pdf ────────────────────────────────────
# This sheet uses wider margins than the rest of the booklet.
_DELIVERABLES_LATERAL_CM = 2.1
_DELIVERABLES_USEFUL_WIDTH_CM = A4_WIDTH_CM - 2 * _DELIVERABLES_LATERAL_CM  # 16.8

DELIVERABLES_CONTAINER = LayoutZone(
    name="deliverables.container",
    top_cm=5.0,
    left_cm=_DELIVERABLES_LATERAL_CM,
    width_cm=_DELIVERABLES_USEFUL_WIDTH_CM,
    height_cm=11.0,
    inner_padding_cm=0.5,
)

# Total caption ("TOTAL: $X ARS" / "TOTAL: US$ X") is right-aligned and
# dies 2cm before the right edge of the page. The current width is a
# debug placeholder — once real text rendering lands, the box becomes
# right-anchored and its width is computed from the rendered string.
DELIVERABLES_TOTAL_RIGHT_MARGIN_CM = 2.0
DELIVERABLES_TOTAL_FIELD = LayoutZone(
    name="deliverables.total",
    top_cm=18.7,
    left_cm=A4_WIDTH_CM - DELIVERABLES_TOTAL_RIGHT_MARGIN_CM - 2.8,
    width_cm=2.8,
    height_cm=LINE_HEIGHT_CM,
)

# Days caption holds short labels like "5 días hábiles". The right
# margin is intentionally generous — the value never wraps.
DELIVERABLES_DAYS_FIELD = LayoutZone(
    name="deliverables.days",
    top_cm=21.3,
    left_cm=9.5,
    width_cm=A4_WIDTH_CM - 9.7 - _DELIVERABLES_LATERAL_CM,
    height_cm=LINE_HEIGHT_CM,
)

# ── Mapping of zones drawn for each asset (debug + future use) ──
ZONES_BY_ASSET: dict[str, tuple[LayoutZone, ...]] = {
    ASSET_QUOTE_BASE: (QUOTE_BASE_CONTAINER,),
    ASSET_DELIVERABLES: (
        DELIVERABLES_CONTAINER,
        DELIVERABLES_TOTAL_FIELD,
        DELIVERABLES_DAYS_FIELD,
    ),
}
