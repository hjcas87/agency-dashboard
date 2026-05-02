"""Pure XML parser for `FECAESolicitarResponse`.

No IO, no state. Takes the raw response body string from the SOAP
client and returns a typed `InvoiceResult`. Tolerates partial /
slightly-malformed shapes (missing nodes return `None`); only fails
hard when the document is unparseable XML or the `FECAESolicitarResult`
backbone is absent (which would indicate a transport-level problem
SOAP fault detection should have caught earlier)."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date, datetime
from xml.etree.ElementTree import Element

from app.shared.afip.constants import WSFE_NAMESPACE
from app.shared.afip.enums import AfipResult, ReceiptType
from app.shared.afip.exceptions import AfipServiceError
from app.shared.afip.messages import ERR_AFIP_QUERY_ERROR
from app.shared.afip.schemas import AfipError, AfipObservation, InvoiceResult


def parse_authorize_response(
    xml: str,
    *,
    requested_receipt_type: ReceiptType,
    requested_point_of_sale: int,
) -> InvoiceResult:
    """Map a `FECAESolicitarResponse` to an `InvoiceResult`.

    `requested_*` are echoed into the result for the (rare) case where
    ARCA omits the cabecera response and we still want the consumer to
    know what was asked. ARCA may authorize a different `CbteTipo` than
    requested (e.g. an FCE escalation): that lands in
    `authorized_cbte_tipo`.
    """
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise AfipServiceError(ERR_AFIP_QUERY_ERROR.format(error=str(exc))) from exc

    result_node = _find_result_node(root)
    if result_node is None:
        raise AfipServiceError(
            ERR_AFIP_QUERY_ERROR.format(error="FECAESolicitarResult missing in response")
        )

    cab_resp = _ns_find(result_node, "FeCabResp")
    det_resp = _ns_find(result_node, ".//FECAEDetResponse")

    point_of_sale = _int_or_default(cab_resp, "PtoVta", requested_point_of_sale)
    authorized_cbte_tipo = _int_or_none(cab_resp, "CbteTipo")

    receipt_type = _resolve_receipt_type(authorized_cbte_tipo, requested_receipt_type)
    receipt_number = _int_or_none(det_resp, "CbteHasta")
    cae = _text(det_resp, "CAE")
    cae_expiration = _parse_yyyymmdd(_text(det_resp, "CAEFchVto"))

    observations = _collect_observations(result_node)
    errors = _collect_errors(result_node)

    success = _is_success(cab_resp, det_resp, errors)

    return InvoiceResult(
        success=success,
        receipt_type=receipt_type,
        point_of_sale=point_of_sale,
        receipt_number=receipt_number,
        cae=cae,
        cae_expiration=cae_expiration,
        authorized_cbte_tipo=authorized_cbte_tipo,
        observations=observations,
        errors=errors,
        raw_response=xml,
        log_id=None,  # the orchestrator fills this in after persisting AfipInvoiceLog
    )


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _find_result_node(root: Element) -> Element | None:
    """Locate the `FECAESolicitarResult` node under either the
    namespaced or the bare path."""
    node = root.find(f".//{{{WSFE_NAMESPACE}}}FECAESolicitarResult")
    if node is not None:
        return node
    return root.find(".//FECAESolicitarResult")


def _is_success(
    cab_resp: Element | None,
    det_resp: Element | None,
    errors: list[AfipError],
) -> bool:
    """A response is a success only when the cabecera says APPROVED,
    every detail entry says APPROVED, and there are no top-level
    errors. Defensive — ARCA has historically returned `Resultado=A`
    with embedded `Errors`; reject those."""
    if errors:
        return False
    cab_result = _text(cab_resp, "Resultado")
    if cab_result != AfipResult.APPROVED.value:
        return False
    det_result = _text(det_resp, "Resultado")
    if det_result is not None and det_result != AfipResult.APPROVED.value:
        return False
    return True


def _resolve_receipt_type(authorized: int | None, fallback: ReceiptType) -> ReceiptType:
    """Translate AFIP's authorized `CbteTipo` back into the enum.
    Falls back to the requested type when ARCA omits it from the
    response or returns an unknown int (the latter is logged via the
    `authorized_cbte_tipo` field for the consumer to inspect)."""
    if authorized is None:
        return fallback
    try:
        return ReceiptType(authorized)
    except ValueError:
        return fallback


def _collect_observations(result_node: Element) -> list[AfipObservation]:
    """Find every `Obs` under the result, regardless of nesting."""
    out: list[AfipObservation] = []
    for obs in result_node.iter(f"{{{WSFE_NAMESPACE}}}Obs"):
        out.append(_obs(obs))
    # Tolerate non-namespaced fixtures too.
    if not out:
        for obs in result_node.iter("Obs"):
            out.append(_obs(obs))
    return out


def _collect_errors(result_node: Element) -> list[AfipError]:
    """Find every `Err` under the result, namespaced or not."""
    out: list[AfipError] = []
    for err in result_node.iter(f"{{{WSFE_NAMESPACE}}}Err"):
        out.append(_err(err))
    if not out:
        for err in result_node.iter("Err"):
            out.append(_err(err))
    return out


def _obs(node: Element) -> AfipObservation:
    return AfipObservation(
        code=_int_or_default(node, "Code", 0),
        message=_text(node, "Msg") or "",
    )


def _err(node: Element) -> AfipError:
    return AfipError(
        code=_int_or_default(node, "Code", 0),
        message=_text(node, "Msg") or "",
    )


# ---------------------------------------------------------------------------
# Element-access primitives
# ---------------------------------------------------------------------------


def _ns_find(parent: Element | None, path: str) -> Element | None:
    """Find a child by path tolerating the WSFE namespace prefix.
    Falls back to the bare path so test fixtures (no ns) still work."""
    if parent is None:
        return None
    if path.startswith(".//"):
        bare = path[3:]
        node = parent.find(f".//{{{WSFE_NAMESPACE}}}{bare}")
        return node if node is not None else parent.find(path)
    node = parent.find(f"{{{WSFE_NAMESPACE}}}{path}")
    return node if node is not None else parent.find(path)


def _text(parent: Element | None, tag: str) -> str | None:
    """findtext that probes both namespaced and bare names."""
    if parent is None:
        return None
    value = parent.findtext(f"{{{WSFE_NAMESPACE}}}{tag}")
    if value is not None:
        return value
    return parent.findtext(tag)


def _int_or_none(parent: Element | None, tag: str) -> int | None:
    raw = _text(parent, tag)
    if raw is None or not raw.strip():
        return None
    try:
        return int(raw.strip())
    except ValueError:
        return None


def _int_or_default(parent: Element | None, tag: str, default: int) -> int:
    value = _int_or_none(parent, tag)
    return value if value is not None else default


def _parse_yyyymmdd(raw: str | None) -> date | None:
    if raw is None or not raw.strip():
        return None
    try:
        return datetime.strptime(raw.strip(), "%Y%m%d").date()
    except ValueError:
        return None


__all__ = ["parse_authorize_response"]
