"""Padrón A5 (`getPersona_v2`) — taxpayer registry lookup.

Sync HTTP call to `ws_sr_padron_a5.getPersona_v2`. The request requires
a TA from WSAA (service `ws_sr_constancia_inscripcion`); the response is
parsed into the `TaxpayerInfo` dataclass tree defined in `schemas.py`.

The orchestrator (`TaxpayerService.get`) is thin: build → sign → post →
parse → return. The XML builder and parsers are pure functions, kept
below the class for unit testing without IO."""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Final
from xml.etree.ElementTree import Element, SubElement, tostring

from app.shared.afip.auth.ticket import AuthService
from app.shared.afip.config import AfipSettings, afip_settings
from app.shared.afip.constants import (
    PADRON_SERVICE_NAME,
    WSPADRON_NAMESPACE,
    WSPADRON_SOAP_ACTION_GET_PERSONA,
    wspadron_url,
)
from app.shared.afip.exceptions import AfipConfigurationError, AfipServiceError
from app.shared.afip.messages import ERR_AFIP_NOT_CONFIGURED, ERR_AFIP_QUERY_ERROR
from app.shared.afip.schemas import (
    FiscalDomicile,
    GeneralRegimeData,
    MonotributoData,
    TaxpayerActivity,
    TaxpayerCategory,
    TaxpayerInfo,
    TaxpayerRequest,
    TaxpayerTax,
)
from app.shared.afip.transport.soap import SoapClient

logger = logging.getLogger(__name__)

_SOAP_NS: Final[str] = "http://schemas.xmlsoap.org/soap/envelope/"


class TaxpayerService:
    """Public entry into Padrón A5. Pure dependency-injected — pass an
    `AuthService` and a `SoapClient` to make the whole call testable
    without the network."""

    def __init__(
        self,
        auth: AuthService,
        soap_client: SoapClient,
        settings: AfipSettings = afip_settings,
    ) -> None:
        self._auth = auth
        self._soap_client = soap_client
        self._settings = settings

    def get(self, request: TaxpayerRequest) -> TaxpayerInfo:
        """Fetch registry info for the given CUIT."""
        issuer_cuit = self._require_issuer_cuit()
        token, sign = self._auth.get_token_and_sign(PADRON_SERVICE_NAME)

        soap_body = _build_get_persona_envelope(
            token=token,
            sign=sign,
            issuer_cuit=issuer_cuit,
            target_cuit=request.cuit,
        )
        url = wspadron_url(self._settings.ENVIRONMENT)
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": WSPADRON_SOAP_ACTION_GET_PERSONA,
        }

        logger.info("Querying Padrón A5 for CUIT %s", request.cuit)
        try:
            response = self._soap_client.post(url=url, body=soap_body, headers=headers)
        except Exception as exc:
            raise AfipServiceError(ERR_AFIP_QUERY_ERROR.format(error=str(exc))) from exc

        return _parse_get_persona_response(response)

    def _require_issuer_cuit(self) -> str:
        cuit = self._settings.CUIT
        if cuit is None:
            raise AfipConfigurationError(ERR_AFIP_NOT_CONFIGURED)
        return cuit


# ---------------------------------------------------------------------------
# Pure helpers — no IO, no state. Trivial to unit-test.
# ---------------------------------------------------------------------------


def _build_get_persona_envelope(
    *, token: str, sign: str, issuer_cuit: str, target_cuit: str
) -> str:
    """Build the SOAP envelope for `getPersona_v2`. ElementTree handles
    escape automatically — kept consistent with `auth/ticket.py`."""
    ET.register_namespace("soapenv", _SOAP_NS)
    ET.register_namespace("a5", WSPADRON_NAMESPACE)
    envelope = Element(f"{{{_SOAP_NS}}}Envelope")
    SubElement(envelope, f"{{{_SOAP_NS}}}Header")
    body = SubElement(envelope, f"{{{_SOAP_NS}}}Body")
    op = SubElement(body, f"{{{WSPADRON_NAMESPACE}}}getPersona_v2")
    SubElement(op, "token").text = token
    SubElement(op, "sign").text = sign
    SubElement(op, "cuitRepresentada").text = issuer_cuit
    SubElement(op, "idPersona").text = target_cuit
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(envelope, encoding="unicode")


def _parse_get_persona_response(xml: str) -> TaxpayerInfo:
    """Map the `personaReturn` payload into a `TaxpayerInfo` dataclass.

    Returns the fully-populated structure even when ARCA omits sections
    (defaults are `None` / empty list). Raises `AfipServiceError` only
    when the structural backbone is missing — partial data is OK."""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise AfipServiceError(ERR_AFIP_QUERY_ERROR.format(error=str(exc))) from exc

    persona = root.find(".//personaReturn")
    if persona is None:
        raise AfipServiceError(ERR_AFIP_QUERY_ERROR.format(error="personaReturn missing"))

    general = persona.find("datosGenerales")
    fiscal_domicile = _parse_fiscal_domicile(general)
    monotributo = _parse_monotributo(persona.find("datosMonotributo"))
    general_regime = _parse_general_regime(persona.find("datosRegimenGeneral"))
    return TaxpayerInfo(
        person_id=_text(general, "idPersona"),
        first_name=_text(general, "nombre"),
        last_name=_text(general, "apellido"),
        company_name=_text(general, "razonSocial"),
        person_type=_text(general, "tipoPersona"),
        key_type=_text(general, "tipoClave"),
        status=_text(general, "estadoClave"),
        closing_month=_text(general, "mesCierre"),
        is_succession=_text(general, "esSucesion"),
        date_social_contract=_text(general, "fechaContratoSocial"),
        fiscal_domicile=fiscal_domicile,
        monotributo=monotributo,
        general_regime=general_regime,
    )


def _parse_fiscal_domicile(general: Element | None) -> FiscalDomicile:
    if general is None:
        return FiscalDomicile(None, None, None, None, None, None)
    domicile = general.find("domicilioFiscal")
    return FiscalDomicile(
        address=_text(domicile, "direccion"),
        locality=_text(domicile, "localidad"),
        province=_text(domicile, "descripcionProvincia"),
        province_id=_text(domicile, "idProvincia"),
        postal_code=_text(domicile, "codPostal"),
        domicile_type=_text(domicile, "tipoDomicilio"),
    )


def _parse_monotributo(node: Element | None) -> MonotributoData:
    if node is None:
        return MonotributoData()
    return MonotributoData(
        activities=[_parse_activity(a) for a in node.findall("actividad")],
        categories=[_parse_category(c) for c in node.findall("categoriaMonotributo")],
        taxes=[_parse_tax(t) for t in node.findall("impuesto")],
    )


def _parse_general_regime(node: Element | None) -> GeneralRegimeData:
    if node is None:
        return GeneralRegimeData()
    return GeneralRegimeData(
        activities=[_parse_activity(a) for a in node.findall("actividad")],
        taxes=[_parse_tax(t) for t in node.findall("impuesto")],
    )


def _parse_activity(node: Element) -> TaxpayerActivity:
    return TaxpayerActivity(
        activity_id=_text(node, "idActividad"),
        description=_text(node, "descripcionActividad"),
        nomenclature=_text(node, "nomenclador"),
        order=_text(node, "orden"),
        period=_text(node, "periodo"),
    )


def _parse_category(node: Element) -> TaxpayerCategory:
    return TaxpayerCategory(
        category_id=_text(node, "idCategoria"),
        tax_id=_text(node, "idImpuesto"),
        period=_text(node, "periodo"),
    )


def _parse_tax(node: Element) -> TaxpayerTax:
    return TaxpayerTax(
        tax_id=_text(node, "idImpuesto"),
        description=_text(node, "descripcionImpuesto"),
        status=_text(node, "estadoImpuesto"),
        reason=_text(node, "motivo"),
        period=_text(node, "periodo"),
    )


def _text(node: Element | None, tag: str) -> str | None:
    """Find a child by tag and return its text — or None."""
    if node is None:
        return None
    return node.findtext(tag)


__all__ = ["TaxpayerService"]
