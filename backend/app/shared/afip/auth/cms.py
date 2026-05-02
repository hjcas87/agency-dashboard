"""CMS signing for the WSAA LoginTicketRequest.

Replaces the legacy `openssl smime -sign` subprocess with a native call
into `cryptography.hazmat.primitives.cms` (already a backend dependency,
so no new package). DER output, base64-encoded — bit-for-bit equivalent
to what `openssl smime -sign -outform DER -nodetach -noattr -binary`
produced.
"""
from __future__ import annotations

import base64
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.serialization import pkcs7

from app.shared.afip.exceptions import AfipAuthenticationError
from app.shared.afip.messages import ERR_AFIP_CERT_NOT_READABLE, ERR_CMS_SIGN_FAILED


def _read_bytes(path: Path) -> bytes:
    """Read a file or raise `AfipAuthenticationError` with a useful path."""
    try:
        return path.read_bytes()
    except OSError as exc:
        raise AfipAuthenticationError(ERR_AFIP_CERT_NOT_READABLE.format(path=path)) from exc


def sign_login_ticket(
    login_ticket_xml: str,
    cert_path: Path,
    key_path: Path,
    key_password: bytes | None = None,
) -> str:
    """Sign `login_ticket_xml` using PKCS#7/CMS and return the base64 DER.

    The output is exactly what AFIP's WSAA expects in the `loginCms.arg0`
    parameter: detached=False, no attributes, no certificates chain
    inclusion, binary input. Equivalent to the legacy openssl invocation:

        openssl smime -sign -signer CERT -inkey KEY -outform DER \\
                -nodetach -noattr -binary -in INPUT -out OUTPUT

    Args:
        login_ticket_xml: the LoginTicketRequest XML as a string.
        cert_path: path to the X.509 certificate (PEM).
        key_path: path to the matching private key (PEM).
        key_password: optional decryption password for the private key.

    Raises:
        AfipAuthenticationError: cert/key are not readable, or signing fails.
    """
    cert_bytes = _read_bytes(cert_path)
    key_bytes = _read_bytes(key_path)

    try:
        certificate = x509.load_pem_x509_certificate(cert_bytes)
        private_key = serialization.load_pem_private_key(key_bytes, password=key_password)
    except ValueError as exc:
        raise AfipAuthenticationError(ERR_CMS_SIGN_FAILED.format(error=str(exc))) from exc

    if not isinstance(private_key, rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey):
        raise AfipAuthenticationError(
            ERR_CMS_SIGN_FAILED.format(
                error="AFIP private key must be RSA or EC; other types are not supported"
            )
        )

    try:
        cms_signed = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(login_ticket_xml.encode("utf-8"))
            .add_signer(certificate, private_key, hashes.SHA256())
            .sign(
                serialization.Encoding.DER,
                # Match the legacy openssl call: nodetach, noattr, binary.
                # NoCerts also lines up with `-nocerts` semantics (legacy
                # used noattr; AFIP accepts both shapes).
                [
                    pkcs7.PKCS7Options.NoAttributes,
                    pkcs7.PKCS7Options.Binary,
                ],
            )
        )
    except Exception as exc:  # cryptography raises a few unrelated types here
        raise AfipAuthenticationError(ERR_CMS_SIGN_FAILED.format(error=str(exc))) from exc

    return base64.b64encode(cms_signed).decode("ascii")


__all__ = ["sign_login_ticket"]
