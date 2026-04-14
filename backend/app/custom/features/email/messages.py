"""
Email feature messages.
User-facing messages in Spanish. Internal/developer messages in English.
"""

# ── Error messages (user-facing, Spanish) ───────────────────────
ERRORS = {
    "template_not_found": "Plantilla de email no encontrada",
    "send_failed": "Error al enviar el email",
    "pdf_attachment_failed": "Error al generar el archivo PDF adjunto",
    "proposal_not_found": "Presupuesto no encontrado",
    "preview_failed": "Error al generar la vista previa del email",
}

# ── Success messages (user-facing, Spanish) ─────────────────────
SUCCESS = {
    "email_sent": "Email enviado exitosamente",
    "template_created": "Plantilla de email creada exitosamente",
    "template_updated": "Plantilla de email actualizada exitosamente",
    "template_deleted": "Plantilla de email eliminada",
    "preview_generated": "Vista previa generada exitosamente",
}

# ── Log messages (dev-facing, English) ──────────────────────────
LOG_MESSAGES = {
    "email_sending": "Sending email to {to}",
    "email_sent": "Email sent successfully to {to}",
    "email_send_error": "Error sending email to {to}: {error}",
    "template_created": "Email template created: id={id}",
    "template_updated": "Email template updated: id={id}",
    "template_deleted": "Email template deleted: id={id}",
    "preview_generated": "Email preview generated for template {id}",
    "pdf_attachment_generating": "Generating PDF attachment for proposal {id}",
    "pdf_attachment_generated": "PDF attachment generated for proposal {id}",
    "pdf_attachment_error": "Error generating PDF attachment: {error}",
}

# ── Response messages (dev-facing, English) ─────────────────────
RESPONSES = {
    "email_sent": "Email sent successfully",
    "template_created": "Template created",
    "template_updated": "Template updated",
    "template_deleted": "Template deleted",
    "preview_generated": "Preview generated",
}
