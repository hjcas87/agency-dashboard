"""WSAA `loginCms` orchestrator + DB cache.

`AuthService.get_token_and_sign(service)` is the single way to obtain a
WSFEv1 / Padrón TA. It returns the cached pair if a non-expired row
exists for the service; otherwise it refreshes (single-flight) and
persists the new TA before returning.

Consumers don't construct `AuthService` directly — `AfipService` does.
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from html import unescape
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from sqlalchemy.orm import Session

from app.shared.afip.auth.cms import sign_login_ticket
from app.shared.afip.auth.locking import lock_for
from app.shared.afip.config import AfipSettings, afip_settings
from app.shared.afip.constants import (
    WSAA_NAMESPACE,
    WSAA_SOAP_ACTION_LOGIN,
    WSAA_TICKET_TTL_HOURS,
    wsaa_url,
)
from app.shared.afip.exceptions import AfipAuthenticationError, AfipConfigurationError
from app.shared.afip.messages import (
    ERR_AFIP_NOT_CONFIGURED,
    ERR_WSAA_NO_TOKEN,
    ERR_WSAA_PARSE_FAILED,
)
from app.shared.afip.models import AfipToken
from app.shared.afip.transport.soap import SoapClient

logger = logging.getLogger(__name__)


# WSAA expects a window slightly in the past for `generationTime` to absorb
# clock skew, and a future `expirationTime` that bounds the request validity
# (not the resulting TA — AFIP issues a TA valid for ~12h regardless).
_GENERATION_BACKDATE_MINUTES = 10
_REQUEST_VALIDITY_HOURS = 2


class AuthService:
    """WSAA TA lifecycle. Pure dependency-injected — testable end to end
    without touching the network if you supply a fake `SoapClient` and a
    sqlalchemy `Session`."""

    def __init__(
        self,
        db: Session,
        soap_client: SoapClient,
        settings: AfipSettings = afip_settings,
    ) -> None:
        self._db = db
        self._soap_client = soap_client
        self._settings = settings

    def get_token_and_sign(self, service: str) -> tuple[str, str]:
        """Return `(token, sign)` for the given AFIP service."""
        cached = self._read_cached(service)
        if cached is not None and self._is_fresh(cached):
            return cached.token, cached.sign

        with lock_for(service):
            cached = self._read_cached(service)
            if cached is not None and self._is_fresh(cached):
                return cached.token, cached.sign
            return self._refresh_and_persist(service)

    # ------------------------------------------------------------------ helpers

    def _read_cached(self, service: str) -> AfipToken | None:
        return (
            self._db.query(AfipToken)
            .filter(AfipToken.service == service)
            .order_by(AfipToken.expiration_time.desc())
            .first()
        )

    def _is_fresh(self, token: AfipToken) -> bool:
        threshold = timedelta(minutes=self._settings.TOKEN_REFRESH_THRESHOLD_MINUTES)
        return datetime.now(UTC) + threshold < token.expiration_time

    def _refresh_and_persist(self, service: str) -> tuple[str, str]:
        cert_path, key_path = self._require_credentials()

        now = datetime.now(UTC)
        login_xml = _build_login_ticket_xml(
            service=service,
            generation_time=now - timedelta(minutes=_GENERATION_BACKDATE_MINUTES),
            expiration_time=now + timedelta(hours=_REQUEST_VALIDITY_HOURS),
            unique_id=int(now.timestamp()),
        )

        cms_b64 = sign_login_ticket(
            login_ticket_xml=login_xml, cert_path=cert_path, key_path=key_path
        )
        soap_envelope = _build_login_soap_envelope(cms_b64)

        url = wsaa_url(self._settings.ENVIRONMENT)
        headers = {
            "Content-Type": "text/xml;charset=UTF-8",
            "SOAPAction": WSAA_SOAP_ACTION_LOGIN,
        }

        logger.info("Requesting new TA from WSAA for service %s", service)
        response = self._soap_client.post(url=url, body=soap_envelope, headers=headers)
        token, sign = _parse_login_response(response)

        record = AfipToken(
            service=service,
            token=token,
            sign=sign,
            generation_time=now,
            expiration_time=now + timedelta(hours=WSAA_TICKET_TTL_HOURS),
        )
        self._db.add(record)
        self._db.commit()

        return token, sign

    def _require_credentials(self) -> tuple[Path, Path]:
        cert = self._settings.CERT_PATH
        key = self._settings.KEY_PATH
        if cert is None or key is None:
            raise AfipConfigurationError(ERR_AFIP_NOT_CONFIGURED)
        return cert, key


# ---------------------------------------------------------------------------
# Pure helpers — no IO, no state. Trivial to unit-test.
# ---------------------------------------------------------------------------

# WSAA insists on this exact UTC format, no fractional seconds.
_WSAA_TIME_FMT = "%Y-%m-%dT%H:%M:%SZ"


def _build_login_ticket_xml(
    *,
    service: str,
    generation_time: datetime,
    expiration_time: datetime,
    unique_id: int,
) -> str:
    """Build the inner LoginTicketRequest XML.

    Uses ElementTree so values are escaped automatically — fixes the
    legacy bug 12 (f-strings would break on `<`/`>`/`&` in inputs)."""
    root = Element("loginTicketRequest", attrib={"version": "1.0"})
    header = SubElement(root, "header")
    SubElement(header, "uniqueId").text = str(unique_id)
    SubElement(header, "generationTime").text = generation_time.strftime(_WSAA_TIME_FMT)
    SubElement(header, "expirationTime").text = expiration_time.strftime(_WSAA_TIME_FMT)
    SubElement(root, "service").text = service
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="unicode")


def _build_login_soap_envelope(cms_b64: str) -> str:
    """Wrap the signed CMS in the WSAA SOAP envelope.

    The CMS is plain ASCII (base64), so safe to interpolate, but we still
    use ElementTree for consistency."""
    soapenv = "http://schemas.xmlsoap.org/soap/envelope/"
    ET.register_namespace("soapenv", soapenv)
    ET.register_namespace("ar", WSAA_NAMESPACE)
    envelope = Element(f"{{{soapenv}}}Envelope")
    SubElement(envelope, f"{{{soapenv}}}Header")
    body = SubElement(envelope, f"{{{soapenv}}}Body")
    login = SubElement(body, f"{{{WSAA_NAMESPACE}}}loginCms")
    SubElement(login, "arg0").text = cms_b64
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(envelope, encoding="unicode")


def _parse_login_response(xml: str) -> tuple[str, str]:
    """Extract `(token, sign)` from a WSAA `loginCmsResponse`.

    The response wraps an inner XML document inside `loginCmsReturn` as
    XML-escaped text — has to be unescaped and re-parsed."""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise AfipAuthenticationError(ERR_WSAA_PARSE_FAILED.format(error=str(exc))) from exc

    inner_text = root.findtext(f".//{{{WSAA_NAMESPACE}}}loginCmsReturn")
    if not inner_text:
        raise AfipAuthenticationError(ERR_WSAA_NO_TOKEN)

    try:
        inner = ET.fromstring(unescape(inner_text))
    except ET.ParseError as exc:
        raise AfipAuthenticationError(ERR_WSAA_PARSE_FAILED.format(error=str(exc))) from exc

    token = inner.findtext(".//token")
    sign = inner.findtext(".//sign")
    if not token or not sign:
        raise AfipAuthenticationError(ERR_WSAA_NO_TOKEN)
    return token, sign


__all__ = ["AuthService"]
