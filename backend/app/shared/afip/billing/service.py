"""WSFEv1 billing orchestrator.

`BillingService.issue(InvoiceRequest)` is the single public entry into
the FECAESolicitar flow. It composes the pure pieces from `request.py`,
`response.py`, `validations.py` and the existing `AuthService` /
`SoapClient` into one transactional path:

    validate -> get last receipt number -> auth -> build -> POST ->
        parse -> persist AfipInvoiceLog -> return InvoiceResult

`AfipInvoiceLog` is persisted in **both** the success and the failure
paths so the operator can correlate ARCA's response (or the absence of
one) with the in-app business entity.

`get_last_authorized` exposes `FECompUltimoAutorizado` directly — the
consumer can call it without issuing if it just needs the number.
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from dataclasses import replace
from xml.etree.ElementTree import Element, SubElement, tostring

from sqlalchemy.orm import Session

from app.shared.afip.auth.ticket import AuthService
from app.shared.afip.billing.request import build_authorize_request
from app.shared.afip.billing.response import parse_authorize_response
from app.shared.afip.billing.validations import raise_on_failures
from app.shared.afip.config import AfipSettings, afip_settings
from app.shared.afip.constants import (
    WSFE_NAMESPACE,
    WSFE_SERVICE_NAME,
    WSFE_SOAP_ACTION_AUTHORIZE,
    WSFE_SOAP_ACTION_LAST_AUTHORIZED,
    wsfe_url,
)
from app.shared.afip.enums import ReceiptType
from app.shared.afip.exceptions import AfipConfigurationError, AfipException, AfipServiceError
from app.shared.afip.messages import ERR_AFIP_NOT_CONFIGURED
from app.shared.afip.models import AfipInvoiceLog
from app.shared.afip.schemas import (
    AfipError,
    InvoiceRequest,
    InvoiceResult,
    LastAuthorizedRequest,
    LastAuthorizedResult,
)
from app.shared.afip.transport.soap import SoapClient

logger = logging.getLogger(__name__)

_SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"


class BillingService:
    """Public orchestrator. All four collaborators come in by DI so the
    whole flow is testable without touching the network or the DB."""

    def __init__(
        self,
        db: Session,
        auth: AuthService,
        soap_client: SoapClient,
        settings: AfipSettings = afip_settings,
    ) -> None:
        self._db = db
        self._auth = auth
        self._soap_client = soap_client
        self._settings = settings

    # ------------------------------------------------------------------ public

    def issue(self, request: InvoiceRequest) -> InvoiceResult:
        """Authorize a receipt via FECAESolicitar. Persists an
        AfipInvoiceLog row in both the success and failure paths."""
        raise_on_failures(request)

        point_of_sale = self._require_point_of_sale()
        issuer_cuit = self._require_cuit()
        last = self.get_last_authorized(
            LastAuthorizedRequest(
                receipt_type=request.receipt_type,
                point_of_sale=point_of_sale,
            )
        )
        receipt_number = last.last_number + 1

        token, sign = self._auth.get_token_and_sign(WSFE_SERVICE_NAME)
        body = build_authorize_request(
            request=request,
            token=token,
            sign=sign,
            issuer_cuit=issuer_cuit,
            point_of_sale=point_of_sale,
            receipt_number=receipt_number,
        )

        url = wsfe_url(self._settings.ENVIRONMENT)
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": WSFE_SOAP_ACTION_AUTHORIZE,
        }

        logger.info(
            "Issuing receipt %s pos=%s number=%s",
            request.receipt_type.name,
            point_of_sale,
            receipt_number,
        )
        try:
            response_xml = self._soap_client.post(url=url, body=body, headers=headers)
        except AfipException as exc:
            return self._persist_failed_call(
                request=request,
                request_xml=body,
                point_of_sale=point_of_sale,
                error=exc,
            )

        result = parse_authorize_response(
            response_xml,
            requested_receipt_type=request.receipt_type,
            requested_point_of_sale=point_of_sale,
        )
        return self._persist_response(
            request=request,
            request_xml=body,
            result=result,
        )

    def get_last_authorized(self, request: LastAuthorizedRequest) -> LastAuthorizedResult:
        """Last authorized receipt number for `(receipt_type, point_of_sale)`.

        Falls back to the configured default point of sale when the
        request leaves it `None`."""
        point_of_sale = request.point_of_sale or self._require_point_of_sale()
        token, sign = self._auth.get_token_and_sign(WSFE_SERVICE_NAME)
        issuer_cuit = self._require_cuit()

        body = _build_last_authorized_request(
            token=token,
            sign=sign,
            issuer_cuit=issuer_cuit,
            point_of_sale=point_of_sale,
            receipt_type=int(request.receipt_type),
        )
        url = wsfe_url(self._settings.ENVIRONMENT)
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": WSFE_SOAP_ACTION_LAST_AUTHORIZED,
        }
        response_xml = self._soap_client.post(url=url, body=body, headers=headers)
        return _parse_last_authorized_response(
            response_xml,
            receipt_type=request.receipt_type,
            point_of_sale=point_of_sale,
        )

    # ------------------------------------------------------------------ helpers

    def _require_point_of_sale(self) -> int:
        if self._settings.POINT_OF_SALE is None:
            raise AfipConfigurationError(ERR_AFIP_NOT_CONFIGURED)
        return self._settings.POINT_OF_SALE

    def _require_cuit(self) -> str:
        if self._settings.CUIT is None:
            raise AfipConfigurationError(ERR_AFIP_NOT_CONFIGURED)
        return self._settings.CUIT

    def _persist_response(
        self,
        *,
        request: InvoiceRequest,
        request_xml: str,
        result: InvoiceResult,
    ) -> InvoiceResult:
        log = AfipInvoiceLog(
            point_of_sale=result.point_of_sale,
            receipt_type=int(request.receipt_type),
            request_xml=request_xml,
            response_xml=result.raw_response,
            success=result.success,
            receipt_number=result.receipt_number,
            cae=result.cae,
            cae_expiration=result.cae_expiration,
            authorized_cbte_tipo=result.authorized_cbte_tipo,
            observations=[{"code": o.code, "message": o.message} for o in result.observations],
            errors=[{"code": e.code, "message": e.message} for e in result.errors],
        )
        self._db.add(log)
        self._db.commit()
        return replace(result, log_id=log.id)

    def _persist_failed_call(
        self,
        *,
        request: InvoiceRequest,
        request_xml: str,
        point_of_sale: int,
        error: AfipException,
    ) -> InvoiceResult:
        """When the SOAP call itself blows up (timeout, fault, etc.),
        we never get an ARCA response. Persist enough to debug, return
        an InvoiceResult with success=False and the error in `errors`."""
        afip_error = AfipError(code=0, message=str(error))
        log = AfipInvoiceLog(
            point_of_sale=point_of_sale,
            receipt_type=int(request.receipt_type),
            request_xml=request_xml,
            response_xml=None,
            success=False,
            receipt_number=None,
            cae=None,
            cae_expiration=None,
            authorized_cbte_tipo=None,
            observations=[],
            errors=[{"code": 0, "message": str(error)}],
        )
        self._db.add(log)
        self._db.commit()
        return InvoiceResult(
            success=False,
            receipt_type=request.receipt_type,
            point_of_sale=point_of_sale,
            receipt_number=None,
            cae=None,
            cae_expiration=None,
            authorized_cbte_tipo=None,
            observations=[],
            errors=[afip_error],
            raw_response=None,
            log_id=log.id,
        )


# ---------------------------------------------------------------------------
# Pure helpers — no IO, no state. Trivial to unit-test.
# ---------------------------------------------------------------------------


def _build_last_authorized_request(
    *,
    token: str,
    sign: str,
    issuer_cuit: str,
    point_of_sale: int,
    receipt_type: int,
) -> str:
    """Build the SOAP body for `FECompUltimoAutorizado`."""
    ET.register_namespace("soapenv", _SOAP_NS)
    ET.register_namespace("ar", WSFE_NAMESPACE)

    envelope = Element(f"{{{_SOAP_NS}}}Envelope")
    SubElement(envelope, f"{{{_SOAP_NS}}}Header")
    body = SubElement(envelope, f"{{{_SOAP_NS}}}Body")
    operation = SubElement(body, f"{{{WSFE_NAMESPACE}}}FECompUltimoAutorizado")

    auth = SubElement(operation, f"{{{WSFE_NAMESPACE}}}Auth")
    SubElement(auth, f"{{{WSFE_NAMESPACE}}}Token").text = token
    SubElement(auth, f"{{{WSFE_NAMESPACE}}}Sign").text = sign
    SubElement(auth, f"{{{WSFE_NAMESPACE}}}Cuit").text = issuer_cuit

    SubElement(operation, f"{{{WSFE_NAMESPACE}}}PtoVta").text = str(point_of_sale)
    SubElement(operation, f"{{{WSFE_NAMESPACE}}}CbteTipo").text = str(receipt_type)

    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(envelope, encoding="unicode")


def _parse_last_authorized_response(
    xml: str,
    *,
    receipt_type: ReceiptType,
    point_of_sale: int,
) -> LastAuthorizedResult:
    """Extract `CbteNro` from `FECompUltimoAutorizadoResponse`. Surfaces
    AFIP `Errors` (auth failed, CUIT not enabled, …) as
    AfipServiceError carrying the structured error list."""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise AfipServiceError(f"Could not parse FECompUltimoAutorizado response: {exc}") from exc

    errors = _collect_errors(root)
    if errors:
        message = "; ".join(f"[{code}] {msg}" for code, msg in errors)
        raise AfipServiceError(message, errors=errors)

    cbte_nro_text = _first_text(root, "CbteNro")
    if cbte_nro_text is None or not cbte_nro_text.strip():
        raise AfipServiceError("FECompUltimoAutorizado response missing CbteNro")
    try:
        cbte_nro = int(cbte_nro_text.strip())
    except ValueError as exc:
        raise AfipServiceError(f"Invalid CbteNro in response: {cbte_nro_text!r}") from exc

    # Receipt_type comes back from the caller (the consumer asked for it).
    return LastAuthorizedResult(
        receipt_type=receipt_type,
        point_of_sale=point_of_sale,
        last_number=cbte_nro,
    )


def _first_text(root: Element, tag: str) -> str | None:
    """Find the first occurrence of `tag` (namespaced or bare) and
    return its text."""
    for path in (f".//{{{WSFE_NAMESPACE}}}{tag}", f".//{tag}"):
        text = root.findtext(path)
        if text is not None:
            return text
    return None


def _collect_errors(root: Element) -> list[tuple[int, str]]:
    """Collect `(code, message)` pairs from any `Err` node — namespaced
    or not. Used for both FECompUltimoAutorizado and as a defensive
    check elsewhere."""
    out: list[tuple[int, str]] = []
    for err in root.iter(f"{{{WSFE_NAMESPACE}}}Err"):
        code, msg = _err_pair(err)
        out.append((code, msg))
    if not out:
        for err in root.iter("Err"):
            code, msg = _err_pair(err)
            out.append((code, msg))
    return out


def _err_pair(node: Element) -> tuple[int, str]:
    code_text = (node.findtext(f"{{{WSFE_NAMESPACE}}}Code") or node.findtext("Code") or "0").strip()
    msg = (node.findtext(f"{{{WSFE_NAMESPACE}}}Msg") or node.findtext("Msg") or "").strip()
    try:
        return int(code_text), msg
    except ValueError:
        return 0, msg


__all__ = ["BillingService"]
