"""End-to-end AFIP homologación smoke test.

Run from the backend directory as a module (no sys.path hacks needed):

    cd backend
    uv run python -m scripts.afip_homo_smoke_test

Walks the full integration top-to-bottom and reports each step as a
PASS / FAIL line. Exits 0 if every step passes, 1 otherwise. Designed
to be the first thing to run when picking up the integration in a new
environment, on a new machine, or after rotating a certificate.

The script imports `app.shared.afip` directly — it is **not** standalone
across projects. Reusing it elsewhere means dropping the whole
`shared/afip/` package over there and wiring `AfipSettings` to that
project's `.env`.
"""
from __future__ import annotations

import sys
import traceback
from collections.abc import Callable
from typing import TypeVar

from app.database import SessionLocal
from app.shared.afip.auth import AuthService
from app.shared.afip.config import afip_settings
from app.shared.afip.constants import PADRON_SERVICE_NAME, WSFE_SERVICE_NAME
from app.shared.afip.enums import AfipEnvironment
from app.shared.afip.models import AfipToken
from app.shared.afip.schemas import TaxpayerInfo, TaxpayerRequest
from app.shared.afip.taxpayer import TaxpayerService
from app.shared.afip.transport import SoapClient
from tests.fixtures.afip_homo_cuits import (
    SAMPLE_MONOTRIBUTO,
    SAMPLE_PERSONA_FISICA,
    SAMPLE_PERSONA_JURIDICA,
)

PASS = "[ \033[32mOK\033[0m  ]"
FAIL = "[\033[31mFAIL\033[0m]"
SKIP = "[SKIP]"

T = TypeVar("T")


def _line(label: str, status: str, detail: str = "") -> None:
    print(f"  {status} {label}" + (f" — {detail}" if detail else ""))


def _step(label: str, fn: Callable[[], T]) -> T | None:
    """Run `fn`, print its outcome, and return the value (or None on failure)."""
    try:
        value = fn()
    except Exception as exc:
        _line(label, FAIL, f"{type(exc).__name__}: {exc}")
        return None
    _line(label, PASS)
    return value


def _check_taxpayer(label: str, cuit: str, taxpayer: TaxpayerService) -> TaxpayerInfo | None:
    return _step(
        f"Padrón A5 — {label} ({cuit})",
        lambda: taxpayer.get(TaxpayerRequest(cuit=cuit)),
    )


def main() -> int:
    print()
    print("AFIP/ARCA homologación smoke test")
    print(f"  environment    : {afip_settings.ENVIRONMENT}")
    print(f"  CUIT (issuer)  : {afip_settings.CUIT or '(unset)'}")
    print(f"  point of sale  : {afip_settings.POINT_OF_SALE}")
    print(f"  cert path      : {afip_settings.CERT_PATH}")
    print(f"  key path       : {afip_settings.KEY_PATH}")
    print()

    if afip_settings.ENVIRONMENT is not AfipEnvironment.HOMO:
        print(
            f"{FAIL} Refusing to run smoke test against {afip_settings.ENVIRONMENT}; "
            f"set AFIP_ENVIRONMENT=homo in .env first."
        )
        return 1

    failures: list[str] = []

    # 1) Configuration sanity ----------------------------------------------
    if not afip_settings.is_configured():
        _line("Configuration loaded", FAIL, "missing required AFIP_* env vars")
        return 1
    _line("Configuration loaded", PASS)

    if not afip_settings.CERT_PATH or not afip_settings.CERT_PATH.exists():
        _line("Certificate readable", FAIL, str(afip_settings.CERT_PATH))
        return 1
    _line("Certificate readable", PASS)

    if not afip_settings.KEY_PATH or not afip_settings.KEY_PATH.exists():
        _line("Private key readable", FAIL, str(afip_settings.KEY_PATH))
        return 1
    _line("Private key readable", PASS)

    # 2) WSAA login (twice — once per service) -----------------------------
    db = SessionLocal()
    client = SoapClient()
    try:
        auth = AuthService(db=db, soap_client=client)

        wsfe_ta = _step(
            f"WSAA loginCms ({WSFE_SERVICE_NAME})",
            lambda: auth.get_token_and_sign(WSFE_SERVICE_NAME),
        )
        if wsfe_ta is None:
            failures.append("WSAA wsfe")

        padron_ta = _step(
            f"WSAA loginCms ({PADRON_SERVICE_NAME})",
            lambda: auth.get_token_and_sign(PADRON_SERVICE_NAME),
        )
        if padron_ta is None:
            failures.append("WSAA padrón")

        # 3) Verify both rows are in afip_token --------------------------
        token_count = db.query(AfipToken).count()
        if token_count >= 2:
            _line(f"AfipToken cache ({token_count} rows)", PASS)
        else:
            _line(f"AfipToken cache ({token_count} rows)", FAIL, "expected ≥ 2")
            failures.append("AfipToken cache")

        # 4) Padrón A5 — try one CUIT per category ------------------------
        if padron_ta is None:
            _line("Padrón A5 lookups", SKIP, "skipping — Padrón TA failed")
        else:
            taxpayer = TaxpayerService(auth=auth, soap_client=client)
            samples = (
                ("Monotributo", SAMPLE_MONOTRIBUTO),
                ("Persona Física", SAMPLE_PERSONA_FISICA),
                ("Persona Jurídica", SAMPLE_PERSONA_JURIDICA),
            )
            for label, cuit in samples:
                info = _check_taxpayer(label, cuit, taxpayer)
                if info is None:
                    failures.append(f"Padrón {label}")
                    continue
                name = info.company_name or " ".join(
                    x for x in (info.first_name, info.last_name) if x
                )
                print(f"        → {name or '(no name)'}, status={info.status}")
    finally:
        client.close()
        db.close()

    print()
    if failures:
        print(f"{FAIL} {len(failures)} step(s) failed: {', '.join(failures)}")
        return 1
    print(f"{PASS} all checks green — AFIP homo connectivity is healthy.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\ninterrupted")
        sys.exit(130)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
