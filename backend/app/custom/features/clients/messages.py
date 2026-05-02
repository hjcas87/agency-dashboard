"""Operator-facing messages for the Client feature.

All Spanish strings the operator can hit live here so logic files stay
free of inline literals (repo convention)."""

# --- Errors ---------------------------------------------------------------

ERR_NOT_FOUND = "Cliente no encontrado"
ERR_DUPLICATE_EMAIL = "Ya existe un cliente con ese email"
ERR_DUPLICATE_ADDITIONAL_EMAIL = "Ese email ya está cargado para este cliente"
ERR_INVALID_CUIT = "El CUIT debe tener 11 dígitos."
ERR_AFIP_NOT_CONFIGURED = (
    "La integración con AFIP no está configurada en este servidor. "
    "Contactá al administrador para activarla."
)
ERR_AFIP_LOOKUP_FAILED = "No se pudo consultar el padrón de AFIP: {error}"
ERR_AFIP_LOOKUP_NOT_FOUND = (
    "El CUIT consultado no figura en el padrón de AFIP. "
    "Verificá que sea correcto y que esté activo."
)
