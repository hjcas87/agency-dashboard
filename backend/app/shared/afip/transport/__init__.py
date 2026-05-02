"""HTTP/SOAP transport for the AFIP/ARCA integration.

Two pieces:

- `SoapClient` — `httpx`-based POST with a custom SSL context (SECLEVEL=1
  required by ARCA's legacy DH keys), retry on 5xx, SOAP-fault detection.
- helpers in `xml` — element builders and parsers that escape correctly
  by construction.
"""
from app.shared.afip.transport.soap import SoapClient

__all__ = ["SoapClient"]
