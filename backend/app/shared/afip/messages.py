"""Operator-facing strings and ARCA error-code translations.

This is the **only** file in `shared/afip/` where Spanish appears in
strings. Logic files import these constants — never inline a literal.

`translate_afip_error` is the single entrypoint for converting an ARCA
error code into a friendly Spanish message. It always returns a string;
unknown codes fall back to a generic template that includes the code so
the operator can still report it.
"""
from app.shared.afip.enums import IvaCondition

# --- Operator UI ----------------------------------------------------------

MSG_INVOICE_GENERATED_SUCCESS = "Factura {invoice_number} generada exitosamente"
MSG_CREDIT_NOTE_GENERATED_SUCCESS = "Nota de Crédito {note_number} generada exitosamente"
MSG_DEBIT_NOTE_GENERATED_SUCCESS = "Nota de Débito {note_number} generada exitosamente"
MSG_TAXPAYER_QUERY_SUCCESS = "Datos de contribuyente {cuit} obtenidos correctamente"

# --- Pre-AFIP validation errors -------------------------------------------

ERR_INVALID_CUIT = "Formato de CUIT inválido (debe tener 11 dígitos)"
ERR_INVALID_CBU = "Formato de CBU inválido (debe tener 22 dígitos)"
ERR_AFIP_NOT_CONFIGURED = (
    "La integración con AFIP no está configurada. Verificá las variables AFIP_* en .env "
    "(CUIT, POINT_OF_SALE, CERT_PATH, KEY_PATH)."
)
ERR_AFIP_CERT_NOT_READABLE = "No se pudo leer el certificado o la clave privada de AFIP en {path}"
ERR_AFIP_QUERY_ERROR = "Error consultando el padrón de AFIP: {error}"
ERR_INVOICE_TOTAL_MISMATCH = (
    "El importe total no coincide con la suma de los componentes "
    "(neto + IVA + no gravado + exento + tributos)"
)

# --- Authentication / network --------------------------------------------

ERR_WSAA_NO_TOKEN = "AFIP no devolvió un token válido en la respuesta de WSAA"
ERR_WSAA_PARSE_FAILED = "No se pudo parsear la respuesta de WSAA: {error}"
ERR_CMS_SIGN_FAILED = "Error firmando el LoginTicketRequest: {error}"
ERR_NETWORK_TIMEOUT = "Tiempo de espera agotado consultando a AFIP ({timeout}s)"
ERR_NETWORK_CONNECTION = "No se pudo conectar a AFIP: {error}"
ERR_HTTP_NON_OK = "AFIP respondió con HTTP {status}: {body}"
ERR_SOAP_FAULT = "AFIP devolvió un SOAP Fault: [{code}] {message}"

# --- ARCA service-side errors --------------------------------------------

ERR_GENERIC_AFIP = "AFIP rechazó la operación con código {code}: {message}"
ERR_AFIP_VALIDATION_COMBINED = "Validación previa falló: {messages}"

# --- Friendly translations for the ARCA error codes the operator hits the most.
# Source: legacy module + manual_dev.md error tables. Keys are int (ARCA codes).

_AFIP_ERROR_FRIENDLY: dict[int, str] = {
    # Issuer / receiver
    10000: (
        "El CUIT emisor no está registrado o habilitado en AFIP. Verificá la "
        "habilitación del CUIT y los servicios contratados."
    ),
    10013: "Las facturas clase A requieren CUIT (DocTipo=80) en el receptor.",
    10015: (
        "El número de documento del receptor es inválido. Verificá que el CUIT "
        "esté correctamente cargado (11 dígitos, sin guiones)."
    ),
    10017: (
        "El receptor no figura como activo en el padrón de AFIP. La factura puede "
        "haberse autorizado igual con observación."
    ),
    10063: (
        "El receptor no está activo en IVA o Monotributo según el padrón AFIP. "
        "La factura puede haberse autorizado igual con observación."
    ),
    10067: (
        "Para facturar a un cliente No Categorizado debés incluir al menos un "
        "tributo en la factura."
    ),
    10069: "El receptor no puede ser el mismo CUIT que el emisor.",
    10070: "Esta factura debe incluir el detalle de IVA discriminado.",
    10071: "Las facturas tipo C no pueden incluir IVA discriminado.",
    10238: "El CUIT del receptor no existe en los registros de AFIP.",
    # IVA condition (RG 5616)
    10242: (
        "La condición de IVA del receptor no es un valor válido para AFIP. "
        "Verificá que esté correctamente configurada."
    ),
    10243: (
        "No se puede emitir este tipo de factura a este receptor por su condición "
        "de IVA. Sugerencia: {suggestion}"
    ),
    10245: "Es recomendable informar la condición de IVA del receptor.",
    10246: "Es obligatorio informar la condición de IVA del receptor.",
    # Amounts / IVA detail
    10018: ("Si el importe de IVA es 0, el array de IVA solo puede tener una alícuota " "del 0%."),
    10023: "La suma de los importes por alícuota de IVA no coincide con el IVA total.",
    10048: (
        "El importe total no coincide con la suma de neto + IVA + no gravado + "
        "exento + tributos."
    ),
    10061: "La suma de las bases por alícuota de IVA no coincide con el neto declarado.",
    10119: "La cotización informada está fuera del rango aceptado por AFIP (-2%, +400%).",
    # Class C
    1434: "En facturas clase C el importe no gravado debe ser 0.",
    1435: "En facturas clase C el importe exento debe ser 0.",
    1436: "En facturas clase C el neto debe ser igual al subtotal.",
    1438: "En facturas clase C el importe de IVA debe ser 0.",
    1443: "En facturas clase C no se puede informar el array de IVA.",
    # Associated receipts (ND/NC)
    10040: ("El comprobante asociado no es válido para este tipo de Nota de " "Crédito/Débito."),
    10041: (
        "El comprobante asociado declarado no existe en los registros de AFIP. "
        "Verificá tipo, punto de venta y número."
    ),
    10151: "El CUIT informado en el comprobante asociado debe tener 11 dígitos.",
    10210: (
        "El comprobante asociado tiene fecha posterior al que se está autorizando: "
        "ambos deben ser del mismo mes y año."
    ),
    # FCE-specific
    1474: (
        "El receptor no cumple con la condición de IVA requerida para FCE "
        "(activo en IVA/Monotributo/Exento según corresponda)."
    ),
    1475: (
        "FCE no permite facturar a CUIT 23000000000 (No Categorizado). "
        "Cambiá el tipo de comprobante o actualizá los datos del cliente."
    ),
    1487: "FCE solo admite CUIT (DocTipo=80) en el receptor.",
    10153: "Las Notas de Crédito/Débito FCE deben asociar la factura original.",
    10161: "El receptor de la FCE no tiene domicilio fiscal electrónico activo.",
    10163: "Las facturas FCE requieren la fecha de vencimiento de pago.",
    10164: (
        "La fecha de vencimiento de pago de la FCE debe ser posterior o igual a "
        "la fecha del comprobante y a la fecha actual."
    ),
    10165: "El CBU informado para la FCE debe tener 22 dígitos numéricos.",
    10168: "Las facturas FCE requieren informar el CBU del emisor.",
    10169: (
        "Estos códigos opcionales (CBU, alias, anulación, transferencia) solo "
        "aplican a comprobantes FCE."
    ),
    10173: ("Las Notas de Crédito/Débito FCE requieren informar el código de " "anulación (S/N)."),
    10174: (
        "El CBU informado para la FCE debe estar registrado en AFIP, vigente y "
        "pertenecer al emisor."
    ),
    10177: "FCE: el receptor no cumple las condiciones de IVA exigidas.",
    10178: "FCE no permite facturar a CUIT 23000000000 (No Categorizado).",
    10180: (
        "FCE: el receptor debe estar caracterizado como GRANDE u optar por PYME "
        "para recibir comprobantes FCE."
    ),
    10215: "El tipo de transferencia FCE solo puede ser SCA o ADC.",
    10216: "Las facturas FCE requieren informar el tipo de transferencia (SCA/ADC).",
    # Service-name fallback (legacy 708 — taxpayer not found)
    708: (
        "El CUIT consultado no está registrado en AFIP. Verificá que el CUIT "
        "sea correcto y esté activo."
    ),
}


# Suggestions used by code 10243 (incompatible receipt for IVA condition).
_RECEIPT_SUGGESTIONS_BY_IVA: dict[IvaCondition, str] = {
    IvaCondition.RI: "Debe emitirse Factura A a un Responsable Inscripto.",
    IvaCondition.MT: "Debe emitirse Factura A o B a un Monotributista.",
    IvaCondition.EX: "Debe emitirse Factura B a un Sujeto Exento.",
    IvaCondition.NA: "Debe emitirse Factura B (IVA No Alcanzado).",
    IvaCondition.CF: "Debe emitirse Factura B o C a un Consumidor Final.",
    IvaCondition.NC: ("Debe emitirse Factura B a un No Categorizado, incluyendo tributos."),
}

_DEFAULT_SUGGESTION = "Verificá el tipo de factura para el receptor seleccionado."


def receipt_suggestion_for(iva_condition: IvaCondition | None) -> str:
    """Return the textual hint about which receipt fits a given receiver.

    Used to fill the `{suggestion}` slot in code 10243's friendly message.
    Falls back to a generic hint for unknown / unset conditions."""
    if iva_condition is None:
        return _DEFAULT_SUGGESTION
    return _RECEIPT_SUGGESTIONS_BY_IVA.get(iva_condition, _DEFAULT_SUGGESTION)


def translate_afip_error(
    code: int,
    raw_message: str = "",
    iva_condition: IvaCondition | None = None,
) -> str:
    """Translate an ARCA error code to a friendly Spanish message.

    Always returns a string. Unknown codes fall back to
    `ERR_GENERIC_AFIP`, which still carries the raw ARCA message so the
    operator has something to act on. Code 10243 is parameterized with a
    suggestion based on the receiver's IVA condition."""
    template = _AFIP_ERROR_FRIENDLY.get(code)
    if template is None:
        return ERR_GENERIC_AFIP.format(code=code, message=raw_message or "(sin mensaje)")
    if "{suggestion}" in template:
        return template.format(suggestion=receipt_suggestion_for(iva_condition))
    return template


__all__ = [
    "ERR_AFIP_CERT_NOT_READABLE",
    "ERR_AFIP_NOT_CONFIGURED",
    "ERR_AFIP_QUERY_ERROR",
    "ERR_AFIP_VALIDATION_COMBINED",
    "ERR_CMS_SIGN_FAILED",
    "ERR_GENERIC_AFIP",
    "ERR_HTTP_NON_OK",
    "ERR_INVALID_CBU",
    "ERR_INVALID_CUIT",
    "ERR_INVOICE_TOTAL_MISMATCH",
    "ERR_NETWORK_CONNECTION",
    "ERR_NETWORK_TIMEOUT",
    "ERR_SOAP_FAULT",
    "ERR_WSAA_NO_TOKEN",
    "ERR_WSAA_PARSE_FAILED",
    "MSG_CREDIT_NOTE_GENERATED_SUCCESS",
    "MSG_DEBIT_NOTE_GENERATED_SUCCESS",
    "MSG_INVOICE_GENERATED_SUCCESS",
    "MSG_TAXPAYER_QUERY_SUCCESS",
    "receipt_suggestion_for",
    "translate_afip_error",
]
