"""
PDF feature messages.
User-facing messages in Spanish. Internal/developer messages in English.
"""

# ── Error messages (user-facing, Spanish) ───────────────────────
ERRORS = {
    "template_not_found": "Plantilla PDF no encontrada",
    "update_failed": "Error al actualizar la plantilla PDF",
    "proposal_not_found": "Presupuesto no encontrado",
    "generation_failed": "Error al generar el PDF: {error}",
    "pdf_attachment_failed": "Error al generar el archivo PDF adjunto",
    "logo_invalid": "Tipo de archivo no permitido. Formatos aceptados: PNG, JPG, SVG, WEBP",
}

# ── Success messages (user-facing, Spanish) ─────────────────────
SUCCESS = {
    "template_updated": "Plantilla PDF actualizada exitosamente",
    "template_reset": "Plantilla PDF restaurada a valores por defecto",
    "logo_uploaded": "Logo subido exitosamente",
    "proposal_generated": "Presupuesto PDF generado exitosamente",
}

# ── Log messages (dev-facing, English) ──────────────────────────
LOG_MESSAGES = {
    "template_updated": "PDF template updated successfully: id={id}",
    "template_reset": "PDF template reset to defaults",
    "template_created": "PDF template created: id={id}",
    "logo_uploaded": "Logo uploaded: {filename}",
    "proposal_generating": "Generating PDF for proposal {id}",
    "proposal_generated": "PDF generated successfully for proposal {id}",
    "generation_error": "Error generating PDF for proposal {id}: {error}",
    "logo_upload_error": "Error uploading logo: {error}",
    "template_fetch_error": "Error fetching PDF template: {error}",
    "template_create_error": "Error creating PDF template: {error}",
    "template_update_error": "Error updating PDF template {id}: {error}",
    "template_delete_error": "Error deleting PDF template {id}: {error}",
    "template_reset_error": "Error resetting PDF template to defaults: {error}",
}

# ── Response messages (dev-facing, English) ─────────────────────
RESPONSES = {
    "template_updated": "Template updated",
    "template_reset": "Template reset to defaults",
    "logo_uploaded": "Logo uploaded successfully",
    "proposal_generated": "Proposal PDF generated",
}

# ── Logo upload configuration ──────────────────────────────────
ALLOWED_LOGO_MIME_TYPES = frozenset({
    "image/png",
    "image/jpeg",
    "image/svg+xml",
    "image/webp",
})

ALLOWED_LOGO_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".svg", ".webp"})

LOGO_UPLOAD_DIR_NAME = "logos"

# ── Default PDF template values ─────────────────────────────────
DEFAULT_BG_COLOR = "#ffffff"
DEFAULT_TEXT_COLOR = "#1a1a1a"
DEFAULT_ACCENT_COLOR = "#2563eb"

PDF_TEMPLATE_DEFAULTS = {
    "logo_url": None,
    "header_text": None,
    "footer_text": None,
    "bg_color": DEFAULT_BG_COLOR,
    "text_color": DEFAULT_TEXT_COLOR,
    "accent_color": DEFAULT_ACCENT_COLOR,
}
