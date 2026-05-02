"""Pure XML builder for `FECAESolicitar`.

No IO, no state — every function takes its inputs and returns a string
or an `Element`. Trivially unit-testable: feed an `InvoiceRequest` and a
synthetic auth tuple, assert on the resulting XML.

XML construction goes through `ElementTree.SubElement(...).text =
value`, so any string interpolated into the request is escaped
automatically. Closes the f-string-XML hazard from the legacy module
(bug 12) without adding `lxml` as a dependency.

Receipt numbers are decided by the orchestrator (via
`FECompUltimoAutorizado`) and passed in here — the builder does not
talk to the network.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring

from app.shared.afip.constants import (
    OPCIONAL_ID_ALIAS,
    OPCIONAL_ID_CANCELLATION,
    OPCIONAL_ID_CBU,
    OPCIONAL_ID_REFERENCE,
    OPCIONAL_ID_TRANSFER_TYPE,
    WSFE_NAMESPACE,
)
from app.shared.afip.enums import (
    IVA_CONDITION_TO_AFIP_CODE,
    CancellationFlag,
    Concept,
    CurrencyId,
    ReceiptType,
    SameForeignCurrencyMarker,
    is_class_c,
    is_fce,
    is_invoice,
    is_note,
    requires_iva_block,
)
from app.shared.afip.schemas import AssociatedReceipt, FceData, InvoiceRequest, IvaBlock

_SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"

# ARCA expects monetary amounts as decimals with two decimal places, no
# thousands separators, dot as decimal mark. `format(value, '.2f')` is
# locale-independent and matches the pattern.
_AMOUNT_FORMAT = ".2f"


def build_authorize_request(
    *,
    request: InvoiceRequest,
    token: str,
    sign: str,
    issuer_cuit: str,
    point_of_sale: int,
    receipt_number: int,
) -> str:
    """Build the full SOAP envelope for `FECAESolicitar`.

    Args:
        request: validated `InvoiceRequest` from the consumer.
        token, sign: WSAA TA pair from `AuthService`.
        issuer_cuit: emitter CUIT (configured `AFIP_CUIT`).
        point_of_sale: the issuer's `PtoVta` for this receipt.
        receipt_number: the next number per `FECompUltimoAutorizado` + 1.

    Returns:
        XML string ready to POST as the SOAP body.
    """
    ET.register_namespace("soapenv", _SOAP_NS)
    ET.register_namespace("ar", WSFE_NAMESPACE)

    envelope = Element(f"{{{_SOAP_NS}}}Envelope")
    SubElement(envelope, f"{{{_SOAP_NS}}}Header")
    body = SubElement(envelope, f"{{{_SOAP_NS}}}Body")
    operation = SubElement(body, f"{{{WSFE_NAMESPACE}}}FECAESolicitar")

    _build_auth_block(operation, token=token, sign=sign, cuit=issuer_cuit)
    _build_fe_cae_req(
        operation,
        request=request,
        point_of_sale=point_of_sale,
        receipt_number=receipt_number,
    )

    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(envelope, encoding="unicode")


# ---------------------------------------------------------------------------
# Auth and request envelope
# ---------------------------------------------------------------------------


def _build_auth_block(parent: Element, *, token: str, sign: str, cuit: str) -> None:
    auth = SubElement(parent, f"{{{WSFE_NAMESPACE}}}Auth")
    SubElement(auth, f"{{{WSFE_NAMESPACE}}}Token").text = token
    SubElement(auth, f"{{{WSFE_NAMESPACE}}}Sign").text = sign
    SubElement(auth, f"{{{WSFE_NAMESPACE}}}Cuit").text = cuit


def _build_fe_cae_req(
    parent: Element,
    *,
    request: InvoiceRequest,
    point_of_sale: int,
    receipt_number: int,
) -> None:
    fe_cae_req = SubElement(parent, f"{{{WSFE_NAMESPACE}}}FeCAEReq")
    _build_fe_cab_req(
        fe_cae_req,
        receipt_type=int(request.receipt_type),
        point_of_sale=point_of_sale,
    )
    fe_det_req = SubElement(fe_cae_req, f"{{{WSFE_NAMESPACE}}}FeDetReq")
    _build_fecae_det_request(fe_det_req, request=request, receipt_number=receipt_number)


def _build_fe_cab_req(parent: Element, *, receipt_type: int, point_of_sale: int) -> None:
    cab = SubElement(parent, f"{{{WSFE_NAMESPACE}}}FeCabReq")
    # Single-receipt batch — FCE forbids more (ARCA 10003) and the
    # consumer pattern in this project never batches.
    SubElement(cab, f"{{{WSFE_NAMESPACE}}}CantReg").text = "1"
    SubElement(cab, f"{{{WSFE_NAMESPACE}}}PtoVta").text = str(point_of_sale)
    SubElement(cab, f"{{{WSFE_NAMESPACE}}}CbteTipo").text = str(receipt_type)


# ---------------------------------------------------------------------------
# FECAEDetRequest — the per-receipt payload
# ---------------------------------------------------------------------------


def _build_fecae_det_request(
    parent: Element, *, request: InvoiceRequest, receipt_number: int
) -> None:
    detail = SubElement(parent, f"{{{WSFE_NAMESPACE}}}FECAEDetRequest")

    _add_text(detail, "Concepto", str(int(request.concept)))
    _add_text(detail, "DocTipo", str(int(request.document_type)))
    _add_text(detail, "DocNro", str(request.document_number))
    _add_text(detail, "CbteDesde", str(receipt_number))
    _add_text(detail, "CbteHasta", str(receipt_number))
    _add_text(detail, "CbteFch", _format_date(request.issue_date))

    _add_text(detail, "ImpTotal", _format_amount(request.total_amount))
    _add_text(detail, "ImpTotConc", _format_amount(request.non_taxable_amount))
    _add_text(detail, "ImpNeto", _format_amount(request.base_amount))
    _add_text(detail, "ImpOpEx", _format_amount(request.exempt_amount))
    _add_text(detail, "ImpTrib", _format_amount(request.taxes_amount))
    _add_text(detail, "ImpIVA", _format_amount(request.iva_amount))

    if request.concept in (Concept.SERVICES, Concept.PRODUCTS_AND_SERVICES):
        # The schema validator has already enforced both dates are present.
        assert request.service_date_from is not None
        assert request.service_date_to is not None
        _add_text(detail, "FchServDesde", _format_date(request.service_date_from))
        _add_text(detail, "FchServHasta", _format_date(request.service_date_to))

    payment_due_date = _payment_due_date(request)
    if _emits_payment_due_date(request) and payment_due_date is not None:
        _add_text(detail, "FchVtoPago", _format_date(payment_due_date))

    _add_text(detail, "MonId", request.currency.value)
    _add_text(detail, "MonCotiz", _format_amount(request.currency_quote))

    # CanMisMonExt is mandatory for non-PES (ARCA 10239) and forbidden
    # for PES (ARCA 10241). Default to "N" — the operator has to choose
    # explicitly only when foreign currency is in scope (out of scope
    # for the initial port, see README).
    if request.currency is not CurrencyId.PES:
        _add_text(detail, "CanMisMonExt", SameForeignCurrencyMarker.NO.value)

    _add_text(
        detail,
        "CondicionIVAReceptorId",
        str(IVA_CONDITION_TO_AFIP_CODE[request.iva_condition]),
    )

    if request.associated_receipts:
        _build_associated_receipts(detail, request.associated_receipts)
    if requires_iva_block(request.receipt_type) and request.iva_blocks:
        _build_iva_blocks(detail, request.iva_blocks)

    opcionales = _collect_opcionales(request)
    if opcionales:
        _build_opcionales(detail, opcionales)


# ---------------------------------------------------------------------------
# Sub-blocks
# ---------------------------------------------------------------------------


def _build_associated_receipts(parent: Element, receipts: list[AssociatedReceipt]) -> None:
    """Emit the `CbtesAsoc` block. Required for ND/NC (ARCA 10153)."""
    container = SubElement(parent, f"{{{WSFE_NAMESPACE}}}CbtesAsoc")
    for receipt in receipts:
        node = SubElement(container, f"{{{WSFE_NAMESPACE}}}CbteAsoc")
        _add_text(node, "Tipo", str(int(receipt.receipt_type)))
        _add_text(node, "PtoVta", str(receipt.point_of_sale))
        _add_text(node, "Nro", str(receipt.receipt_number))
        if receipt.issuer_cuit is not None:
            _add_text(node, "Cuit", receipt.issuer_cuit)
        if receipt.issue_date is not None:
            _add_text(node, "CbteFch", _format_date(receipt.issue_date))


def _build_iva_blocks(parent: Element, blocks: list[IvaBlock]) -> None:
    """Emit the `Iva` block. Forbidden for class C (ARCA 1443/10071) —
    the model_validator on `InvoiceRequest` already enforces this; this
    function trusts that contract."""
    container = SubElement(parent, f"{{{WSFE_NAMESPACE}}}Iva")
    for block in blocks:
        node = SubElement(container, f"{{{WSFE_NAMESPACE}}}AlicIva")
        _add_text(node, "Id", str(int(block.aliquot_id)))
        _add_text(node, "BaseImp", _format_amount(block.base_amount))
        _add_text(node, "Importe", _format_amount(block.amount))


def _build_opcionales(parent: Element, opcionales: list[tuple[str, str]]) -> None:
    """Emit the `Opcionales` block. Each entry is `(id, value)`."""
    container = SubElement(parent, f"{{{WSFE_NAMESPACE}}}Opcionales")
    for opt_id, value in opcionales:
        node = SubElement(container, f"{{{WSFE_NAMESPACE}}}Opcional")
        _add_text(node, "Id", opt_id)
        _add_text(node, "Valor", value)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _collect_opcionales(request: InvoiceRequest) -> list[tuple[str, str]]:
    """Compose the `Opcionales` list per the FCE rules.

    Non-FCE receipts must NOT include any of the FCE optional ids
    (ARCA 10169) — the schema validator has already rejected such
    requests, so this function operates only on FCE inputs."""
    if not is_fce(request.receipt_type) or request.fce is None:
        return _collect_non_fce_opcionales(request)

    return _collect_fce_opcionales(request.receipt_type, request.fce, request)


def _collect_non_fce_opcionales(request: InvoiceRequest) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if request.commercial_reference:
        out.append((OPCIONAL_ID_REFERENCE, request.commercial_reference))
    return out


def _collect_fce_opcionales(
    receipt_type: ReceiptType, fce: FceData, request: InvoiceRequest
) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    # FCE Factura: CBU (10168) + transfer (10216) + optional alias / reference.
    if is_invoice(receipt_type):
        if fce.cbu is not None:
            out.append((OPCIONAL_ID_CBU, fce.cbu))
        if fce.transfer_type is not None:
            out.append((OPCIONAL_ID_TRANSFER_TYPE, fce.transfer_type.value))
        if fce.alias is not None:
            out.append((OPCIONAL_ID_ALIAS, fce.alias))
    # FCE ND/NC: cancellation flag (10173). CBU/alias/transfer forbidden
    # (ARCA 10172) — the schema rejects them upstream.
    if is_note(receipt_type) and fce.cancellation is not None:
        out.append((OPCIONAL_ID_CANCELLATION, fce.cancellation.value))
    # Commercial reference (id 23) is allowed for both invoices and notes.
    ref = fce.commercial_reference or request.commercial_reference
    if ref:
        out.append((OPCIONAL_ID_REFERENCE, ref))
    return out


def _emits_payment_due_date(request: InvoiceRequest) -> bool:
    """`FchVtoPago` rules:

    - SERVICES / PRODUCTS_AND_SERVICES: required (manual: Concepto 2/3).
    - FCE Factura (any class): required (ARCA 10163).
    - FCE ND/NC of annulment (cancellation == "S"): allowed (ARCA 10175).
    - PRODUCTS-only non-FCE: must NOT include it.
    """
    if request.concept in (Concept.SERVICES, Concept.PRODUCTS_AND_SERVICES):
        return True
    if is_fce(request.receipt_type) and is_invoice(request.receipt_type):
        return True
    if (
        is_fce(request.receipt_type)
        and is_note(request.receipt_type)
        and request.fce is not None
        and request.fce.cancellation is CancellationFlag.YES
    ):
        return True
    return False


def _payment_due_date(request: InvoiceRequest) -> date | None:
    """Resolve `FchVtoPago` from the FCE block (preferred) or from the
    request itself."""
    if request.fce is not None and request.fce.payment_due_date is not None:
        return request.fce.payment_due_date
    return request.payment_due_date


def _format_amount(value: Decimal) -> str:
    """ARCA expects 13.2 — dot as decimal separator, no grouping."""
    return format(value, _AMOUNT_FORMAT)


def _format_date(value: date) -> str:
    """ARCA's `CbteFch` / `FchServDesde` / etc. are `yyyymmdd`."""
    return value.strftime("%Y%m%d")


def _add_text(parent: Element, tag: str, value: str) -> None:
    """Append a namespaced child whose text is `value`. ElementTree
    escapes special chars on `tostring`."""
    SubElement(parent, f"{{{WSFE_NAMESPACE}}}{tag}").text = value


# Class C consistency assertions live in the schema model_validator.
# Surface a small helper for tests / orchestrator pre-checks.
def class_c_amount_consistency(request: InvoiceRequest) -> bool:
    """True if class-C class-specific amount rules hold."""
    if not is_class_c(request.receipt_type):
        return True
    return (
        request.iva_amount == Decimal("0")
        and request.non_taxable_amount == Decimal("0")
        and request.exempt_amount == Decimal("0")
        and not request.iva_blocks
    )


__all__ = [
    "build_authorize_request",
    "class_c_amount_consistency",
]
