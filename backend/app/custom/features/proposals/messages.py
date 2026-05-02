"""Operator-facing messages for the Proposal feature.

All Spanish strings the operator can hit live here so the logic files
stay free of inline literals (repo convention)."""

# --- Errors ---------------------------------------------------------------

ERR_NOT_FOUND = "Presupuesto no encontrado"
ERR_INVALID_STATUS_VALUE = (
    "Estado inválido. Debe ser uno de: borrador, enviado, aceptado, rechazado."
)
ERR_TRANSITION_FORBIDDEN = (
    "No se puede pasar de '{from_status}' a '{to_status}'. "
    "Si querés volver a editar un presupuesto cerrado, primero pasalo a 'borrador'."
)


# --- Status labels (for error messages, not for UI — UI usa frontend/lib/messages) ---

STATUS_LABELS = {
    "draft": "borrador",
    "sent": "enviado",
    "accepted": "aceptado",
    "rejected": "rechazado",
}


__all__ = [
    "ERR_INVALID_STATUS_VALUE",
    "ERR_NOT_FOUND",
    "ERR_TRANSITION_FORBIDDEN",
    "STATUS_LABELS",
]
