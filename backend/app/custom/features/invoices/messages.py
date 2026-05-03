"""Operator-facing strings for the Invoice feature.

All Spanish strings live here so logic files stay free of inline
literals (repo convention)."""

# --- Errors ---------------------------------------------------------------

ERR_NOT_FOUND = "Factura no encontrada"
ERR_PROPOSAL_NOT_FOUND = "Presupuesto no encontrado"
ERR_PROPOSAL_NOT_ACCEPTED = (
    "Solo se pueden facturar presupuestos en estado 'Aceptado'. "
    "Cambiá el estado del presupuesto antes de facturar."
)
ERR_PROPOSAL_ALREADY_INVOICED = (
    "Este presupuesto ya tiene una factura emitida. "
    "Si necesitás reemitir, contactá al administrador."
)
ERR_CLIENT_NOT_FOUND = "Cliente no encontrado"
ERR_NO_LINE_ITEMS = "Agregá al menos una línea con monto válido."
ERR_AFIP_ISSUE_FAILED = "AFIP rechazó la emisión: {error}"


# --- Success --------------------------------------------------------------

MSG_INVOICE_ISSUED = "Factura {receipt_type} N°{number} emitida — CAE {cae}"
