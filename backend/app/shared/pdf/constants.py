"""
PDF feature constants.
Default values and configuration for PDF templates.
"""

# ── Default PDF template colors ─────────────────────────────────
DEFAULT_BG_COLOR = "#ffffff"
DEFAULT_TEXT_COLOR = "#1a1a1a"
DEFAULT_ACCENT_COLOR = "#2563eb"

# ── Default template values (dev-facing, English) ───────────────
PDF_TEMPLATE_DEFAULTS = {
    "logo_url": None,
    "header_text": None,
    "footer_text": None,
    "bg_color": DEFAULT_BG_COLOR,
    "text_color": DEFAULT_TEXT_COLOR,
    "accent_color": DEFAULT_ACCENT_COLOR,
}

# ── Logo upload configuration ──────────────────────────────────
ALLOWED_LOGO_TYPES = {"image/png", "image/jpeg", "image/svg+xml", "image/webp"}
LOGO_UPLOAD_DIR_NAME = "logos"
