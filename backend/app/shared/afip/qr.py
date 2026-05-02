"""ARCA QR code generator for the printed receipt.

ARCA mandates a QR on every electronic invoice that encodes the receipt
identity + CAE so any consumer can verify authenticity at
https://www.afip.gob.ar/fe/qr/. The format is:

    https://www.afip.gob.ar/fe/qr/?p=<base64-urlsafe(json_payload)>

Where `json_payload` is a JSON object with the canonical fields
(`ver`, `fecha`, `cuit`, `ptoVta`, `tipoCmp`, `nroCmp`, `importe`,
`moneda`, `ctz`, `tipoDocRec`, `nroDocRec`, `tipoCodAut`, `codAut`).

This module exposes:
- `build_qr_url(...)`: returns the full ARCA QR URL.
- `render_qr_png(...)`: returns the QR image as PNG bytes — caller
  embeds it in the PDF with a renderer that knows about images.

Both are pure functions; no IO. Lives in `shared/afip` because the
QR spec is part of the ARCA receipt contract, not of any one client's
PDF design.
"""
from __future__ import annotations

import base64
import json
from datetime import date
from decimal import Decimal
from io import BytesIO

import qrcode

# Authorization-code-type values per ARCA's QR spec:
# "E" — CAE (online), "A" — CAEA (offline batch).
QR_AUTH_TYPE_CAE = "E"
QR_AUTH_TYPE_CAEA = "A"

QR_BASE_URL = "https://www.afip.gob.ar/fe/qr/"
QR_VERSION = 1


def build_qr_url(
    *,
    issue_date: date,
    issuer_cuit: str,
    point_of_sale: int,
    receipt_type: int,
    receipt_number: int,
    total_amount: Decimal,
    currency_id: str,
    currency_quote: Decimal,
    receiver_doc_type: int,
    receiver_doc_number: int,
    cae: str,
    auth_type: str = QR_AUTH_TYPE_CAE,
) -> str:
    """Build the ARCA QR URL for a printed receipt.

    Field names use ARCA's exact JSON keys (camelCase). The receiver
    fields default to 0/0 when the receipt is to a Consumidor Final;
    callers should still pass them explicitly so the QR matches what
    was actually sent to ARCA.
    """
    payload = {
        "ver": QR_VERSION,
        "fecha": issue_date.isoformat(),
        "cuit": int(issuer_cuit),
        "ptoVta": point_of_sale,
        "tipoCmp": receipt_type,
        "nroCmp": receipt_number,
        "importe": float(total_amount),
        "moneda": currency_id,
        "ctz": float(currency_quote),
        "tipoDocRec": receiver_doc_type,
        "nroDocRec": receiver_doc_number,
        "tipoCodAut": auth_type,
        "codAut": int(cae),
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return f"{QR_BASE_URL}?p={encoded}"


def render_qr_png(url: str, *, box_size: int = 4, border: int = 1) -> bytes:
    """Render `url` to a PNG image. Defaults are tuned for a ~25–30 mm
    QR on an A4 PDF — sharp at print resolution, small file size."""
    qr = qrcode.QRCode(
        version=None,  # auto-fit by data length
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


__all__ = [
    "QR_AUTH_TYPE_CAE",
    "QR_AUTH_TYPE_CAEA",
    "QR_BASE_URL",
    "QR_VERSION",
    "build_qr_url",
    "render_qr_png",
]
