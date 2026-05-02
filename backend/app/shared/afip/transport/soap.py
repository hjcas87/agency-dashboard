"""SOAP client for AFIP/ARCA.

Migrates from `requests + urllib3` (legacy module) to `httpx` (already a
backend dep), keeping the SECLEVEL=1 SSL context AFIP requires for its
legacy DH keys. Retries on 5xx with exponential backoff. Detects SOAP
faults inside otherwise-200 responses and surfaces them as
`AfipNetworkError`.
"""
from __future__ import annotations

import logging
import ssl
import time
import xml.etree.ElementTree as ET

import httpx

from app.shared.afip.constants import (
    DEFAULT_HTTP_MAX_RETRIES,
    DEFAULT_HTTP_RETRY_BACKOFF_SECONDS,
    DEFAULT_HTTP_TIMEOUT_SECONDS,
    SSL_CIPHERS_AFIP,
)
from app.shared.afip.exceptions import AfipNetworkError
from app.shared.afip.messages import (
    ERR_HTTP_NON_OK,
    ERR_NETWORK_CONNECTION,
    ERR_NETWORK_TIMEOUT,
    ERR_SOAP_FAULT,
)

logger = logging.getLogger(__name__)


_SOAP_ENVELOPE_NS = "http://schemas.xmlsoap.org/soap/envelope/"


def build_afip_ssl_context() -> ssl.SSLContext:
    """SSL context configured for AFIP's legacy DH keys.

    AFIP servers still negotiate Diffie-Hellman keys < 2048 bits which
    OpenSSL 3 rejects at SECLEVEL=2 (its default). SECLEVEL=1 keeps
    TLS 1.2+ but allows DH ≥ 1024 bits. Kept as a function so tests can
    override it without monkeypatching."""
    context = ssl.create_default_context()
    context.set_ciphers(SSL_CIPHERS_AFIP)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context


class SoapClient:
    """Thin synchronous SOAP client. One instance per service is fine —
    httpx handles connection pooling internally."""

    def __init__(
        self,
        timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_HTTP_MAX_RETRIES,
        backoff: float = DEFAULT_HTTP_RETRY_BACKOFF_SECONDS,
        ssl_context: ssl.SSLContext | None = None,
    ) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff = backoff
        self._client = httpx.Client(
            timeout=timeout,
            verify=ssl_context if ssl_context is not None else build_afip_ssl_context(),
            transport=httpx.HTTPTransport(retries=0),  # we handle retries ourselves
        )

    def __enter__(self) -> SoapClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def post(self, url: str, body: str, headers: dict[str, str]) -> str:
        """POST `body` to `url` and return the response body as text.

        Retries on transport-level failures and on 5xx responses **without**
        a SOAP Fault. AFIP commonly returns semantic errors as HTTP 500 +
        SOAP Fault — those are not retryable (the answer won't change),
        and surface immediately as `AfipNetworkError` with the fault
        code/message in the error text."""
        last_error: str | None = None
        for attempt in range(self._max_retries):
            try:
                response = self._client.post(url, content=body.encode("utf-8"), headers=headers)
            except httpx.TimeoutException as exc:
                last_error = ERR_NETWORK_TIMEOUT.format(timeout=self._timeout)
                logger.warning("AFIP request timed out (attempt %s): %s", attempt + 1, exc)
            except httpx.HTTPError as exc:
                last_error = ERR_NETWORK_CONNECTION.format(error=str(exc))
                logger.warning("AFIP transport error (attempt %s): %s", attempt + 1, exc)
            else:
                if response.status_code == 200:
                    _raise_if_soap_fault(response.text)
                    return response.text

                # Non-200: SOAP Fault inside the body short-circuits the
                # retry loop (semantic error — retrying won't change it).
                _raise_if_soap_fault(response.text)

                if 500 <= response.status_code < 600:
                    last_error = ERR_HTTP_NON_OK.format(
                        status=response.status_code, body=response.text[:500]
                    )
                    logger.warning(
                        "AFIP returned %s (attempt %s)", response.status_code, attempt + 1
                    )
                else:
                    raise AfipNetworkError(
                        ERR_HTTP_NON_OK.format(
                            status=response.status_code, body=response.text[:500]
                        )
                    )

            # Exponential backoff before the next attempt.
            time.sleep(self._backoff * (2**attempt))

        raise AfipNetworkError(last_error or "AFIP request failed for unknown reason")


def _raise_if_soap_fault(xml_response: str) -> None:
    """Inspect a 200 response and raise `AfipNetworkError` if it carries
    a SOAP Fault. Parser errors are silently ignored — the caller's
    XML parser will surface them in a more useful place."""
    try:
        root = ET.fromstring(xml_response)
    except ET.ParseError:
        return

    fault = root.find(f".//{{{_SOAP_ENVELOPE_NS}}}Fault")
    if fault is None:
        fault = root.find(".//Fault")
    if fault is None:
        return

    code = fault.findtext("faultcode") or fault.findtext(f"{{{_SOAP_ENVELOPE_NS}}}faultcode") or ""
    message = (
        fault.findtext("faultstring") or fault.findtext(f"{{{_SOAP_ENVELOPE_NS}}}faultstring") or ""
    )
    raise AfipNetworkError(ERR_SOAP_FAULT.format(code=code, message=message))


__all__ = ["SoapClient", "build_afip_ssl_context"]
