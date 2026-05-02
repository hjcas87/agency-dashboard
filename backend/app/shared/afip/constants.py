"""Static, non-configurable AFIP/ARCA constants.

Endpoint URLs, SOAP namespaces, SOAPAction values, the list of `FEParam*`
operations, and the AFIP error code → friendly message map all live here.
**Nothing in this file comes from environment**: AFIP fixes these. Anything
that varies per deployment lives in `config.AfipSettings`.
"""
from typing import Final

from app.shared.afip.enums import AfipEnvironment

# --- WSAA (authentication) -------------------------------------------------

WSAA_URL_PROD: Final[str] = "https://wsaa.afip.gov.ar/ws/services/LoginCms"
WSAA_URL_HOMO: Final[str] = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"

# WSFEv1 service name used in the LoginTicketRequest.
WSFE_SERVICE_NAME: Final[str] = "wsfe"

# Padrón A5 (taxpayer registry) requires its own LoginTicket for service
# `ws_sr_constancia_inscripcion`. Both legacy modules used the same name.
PADRON_SERVICE_NAME: Final[str] = "ws_sr_constancia_inscripcion"

# WSAA TA validity is 12h. We refresh proactively before this expires.
WSAA_TICKET_TTL_HOURS: Final[int] = 12

# --- WSFEv1 (invoicing) ----------------------------------------------------

WSFE_URL_PROD: Final[str] = "https://servicios1.afip.gov.ar/wsfev1/service.asmx"
WSFE_URL_HOMO: Final[str] = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx"
WSFE_NAMESPACE: Final[str] = "http://ar.gov.afip.dif.FEV1/"

# SOAPAction values per WSFEv1 operation. AFIP routes by these.
WSFE_SOAP_ACTION_AUTHORIZE: Final[str] = WSFE_NAMESPACE + "FECAESolicitar"
WSFE_SOAP_ACTION_LAST_AUTHORIZED: Final[str] = WSFE_NAMESPACE + "FECompUltimoAutorizado"
WSFE_SOAP_ACTION_QUERY_RECEIPT: Final[str] = WSFE_NAMESPACE + "FECompConsultar"
WSFE_SOAP_ACTION_PARAM_GET_PTOS_VENTA: Final[str] = WSFE_NAMESPACE + "FEParamGetPtosVenta"
WSFE_SOAP_ACTION_PARAM_GET_TIPOS_CBTE: Final[str] = WSFE_NAMESPACE + "FEParamGetTiposCbte"
WSFE_SOAP_ACTION_PARAM_GET_TIPOS_DOC: Final[str] = WSFE_NAMESPACE + "FEParamGetTiposDoc"
WSFE_SOAP_ACTION_PARAM_GET_TIPOS_IVA: Final[str] = WSFE_NAMESPACE + "FEParamGetTiposIva"
WSFE_SOAP_ACTION_PARAM_GET_COND_IVA_RECEPTOR: Final[str] = (
    WSFE_NAMESPACE + "FEParamGetCondicionIvaReceptor"
)

# --- WSPADRON A5 (taxpayer registry) ---------------------------------------

WSPADRON_URL_PROD: Final[str] = "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA5"
WSPADRON_URL_HOMO: Final[str] = "https://awshomo.afip.gov.ar/sr-padron/webservices/personaServiceA5"
WSPADRON_NAMESPACE: Final[str] = "http://a5.soap.ws.server.puc.sr/"
WSPADRON_SOAP_ACTION_GET_PERSONA: Final[
    str
] = "http://ar.gov.afip.dif.sr.padron/PersonaServiceA5/getPersona_v2"

# --- Network --------------------------------------------------------------

# AFIP servers still negotiate legacy DH keys; OpenSSL default SECLEVEL=2
# rejects keys smaller than 2048 bits. This level allows DH ≥ 1024 bits
# while still requiring TLS 1.2+. Used by the SoapClient SSL context.
SSL_CIPHERS_AFIP: Final[str] = "DEFAULT:@SECLEVEL=1"

DEFAULT_HTTP_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_HTTP_MAX_RETRIES: Final[int] = 3
DEFAULT_HTTP_RETRY_BACKOFF_SECONDS: Final[float] = 1.0

# --- WSAA SOAP envelopes ---------------------------------------------------

WSAA_NAMESPACE: Final[str] = "http://ar.gov.afip.dif.logincms/"
WSAA_SOAP_ACTION_LOGIN: Final[str] = ""  # WSAA expects an empty SOAPAction.

# --- Endpoint resolver ----------------------------------------------------

_WSAA_URLS: Final[dict[AfipEnvironment, str]] = {
    AfipEnvironment.PROD: WSAA_URL_PROD,
    AfipEnvironment.HOMO: WSAA_URL_HOMO,
}

_WSFE_URLS: Final[dict[AfipEnvironment, str]] = {
    AfipEnvironment.PROD: WSFE_URL_PROD,
    AfipEnvironment.HOMO: WSFE_URL_HOMO,
}

_WSPADRON_URLS: Final[dict[AfipEnvironment, str]] = {
    AfipEnvironment.PROD: WSPADRON_URL_PROD,
    AfipEnvironment.HOMO: WSPADRON_URL_HOMO,
}


def wsaa_url(environment: AfipEnvironment) -> str:
    return _WSAA_URLS[environment]


def wsfe_url(environment: AfipEnvironment) -> str:
    return _WSFE_URLS[environment]


def wspadron_url(environment: AfipEnvironment) -> str:
    return _WSPADRON_URLS[environment]


# --- Optional codes (FCE Opcionales) --------------------------------------

OPCIONAL_ID_CBU: Final[str] = "2101"  # FCE Factura: CBU emisor
OPCIONAL_ID_ALIAS: Final[str] = "2102"  # FCE Factura: ALIAS emisor (optional)
OPCIONAL_ID_TRANSFER_TYPE: Final[str] = "27"  # FCE Factura: SCA / ADC
OPCIONAL_ID_CANCELLATION: Final[str] = "22"  # FCE ND/NC: anulación S / N
OPCIONAL_ID_REFERENCE: Final[str] = "23"  # FCE: referencia comercial

# --- AFIP-defined limits --------------------------------------------------

CBU_LENGTH: Final[int] = 22
CUIT_LENGTH: Final[int] = 11
NO_CATEGORIZADO_CUIT: Final[str] = "23000000000"  # ARCA 10178 / 1475
EXCHANGE_RATE_MIN: Final[float] = 0.0
EXCHANGE_RATE_MAX_DEVIATION: Final[float] = 4.0  # ARCA 10119 (≤ +400%)


# --- Friendly mapping of the most common ARCA error codes -----------------
# Operator-facing strings live in `messages.py`; this map only fixes which
# codes have a friendly translation. The fallback is the raw ARCA message.

CRITICAL_ERROR_CODES: Final[frozenset[int]] = frozenset(
    {
        # Issuer / receiver
        10000,
        10013,
        10015,
        10017,
        10063,
        10067,
        10069,
        10070,
        10071,
        10238,
        # IVA condition (RG 5616)
        10242,
        10243,
        10245,
        10246,
        # Amounts / IVA detail
        10018,
        10023,
        10048,
        10061,
        10119,
        # Class C
        1434,
        1435,
        1436,
        1438,
        1443,
        # Associations (ND/NC)
        10040,
        10041,
        10151,
        10210,
        # FCE-specific
        1474,
        1475,
        1487,
        10153,
        10154,
        10155,
        10156,
        10161,
        10162,
        10163,
        10164,
        10165,
        10166,
        10167,
        10168,
        10169,
        10170,
        10171,
        10172,
        10173,
        10174,
        10175,
        10177,
        10178,
        10180,
        10183,
        10184,
        10194,
        10196,
        10214,
        10215,
        10216,
    }
)


__all__ = [
    "CBU_LENGTH",
    "CRITICAL_ERROR_CODES",
    "CUIT_LENGTH",
    "DEFAULT_HTTP_MAX_RETRIES",
    "DEFAULT_HTTP_RETRY_BACKOFF_SECONDS",
    "DEFAULT_HTTP_TIMEOUT_SECONDS",
    "EXCHANGE_RATE_MAX_DEVIATION",
    "EXCHANGE_RATE_MIN",
    "NO_CATEGORIZADO_CUIT",
    "OPCIONAL_ID_ALIAS",
    "OPCIONAL_ID_CANCELLATION",
    "OPCIONAL_ID_CBU",
    "OPCIONAL_ID_REFERENCE",
    "OPCIONAL_ID_TRANSFER_TYPE",
    "PADRON_SERVICE_NAME",
    "SSL_CIPHERS_AFIP",
    "WSAA_NAMESPACE",
    "WSAA_SOAP_ACTION_LOGIN",
    "WSAA_TICKET_TTL_HOURS",
    "WSAA_URL_HOMO",
    "WSAA_URL_PROD",
    "WSFE_NAMESPACE",
    "WSFE_SERVICE_NAME",
    "WSFE_SOAP_ACTION_AUTHORIZE",
    "WSFE_SOAP_ACTION_LAST_AUTHORIZED",
    "WSFE_SOAP_ACTION_PARAM_GET_COND_IVA_RECEPTOR",
    "WSFE_SOAP_ACTION_PARAM_GET_PTOS_VENTA",
    "WSFE_SOAP_ACTION_PARAM_GET_TIPOS_CBTE",
    "WSFE_SOAP_ACTION_PARAM_GET_TIPOS_DOC",
    "WSFE_SOAP_ACTION_PARAM_GET_TIPOS_IVA",
    "WSFE_SOAP_ACTION_QUERY_RECEIPT",
    "WSFE_URL_HOMO",
    "WSFE_URL_PROD",
    "WSPADRON_NAMESPACE",
    "WSPADRON_SOAP_ACTION_GET_PERSONA",
    "WSPADRON_URL_HOMO",
    "WSPADRON_URL_PROD",
    "wsaa_url",
    "wsfe_url",
    "wspadron_url",
]
