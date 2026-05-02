"""Per-deployment AFIP/ARCA settings, bound to environment variables.

Loaded once at import time and exposed as the module-level `afip_settings`.
The merge with `app.config.settings` happens implicitly via Pydantic
reading the same `.env` file. Keeping `AfipSettings` separate keeps the
core `Settings` class clean of integration-specific fields and lets
non-Argentine forks ship without wiring AFIP env vars.
"""
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.afip.constants import DEFAULT_HTTP_MAX_RETRIES, DEFAULT_HTTP_TIMEOUT_SECONDS
from app.shared.afip.enums import AfipEnvironment, CurrencyId

BACKEND_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BACKEND_DIR / ".env"


class AfipSettings(BaseSettings):
    """All `AFIP_*` env vars. Optional fields default to safe values; the
    five fields without defaults must be present in `.env` for any
    deployment that uses the integration."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_prefix="AFIP_",
        case_sensitive=True,
        extra="ignore",
    )

    ENVIRONMENT: AfipEnvironment = AfipEnvironment.HOMO
    CUIT: str | None = None
    POINT_OF_SALE: int | None = None
    CERT_PATH: Path | None = None
    KEY_PATH: Path | None = None

    CURRENCY_ID: CurrencyId = CurrencyId.PES
    TIMEOUT_SECONDS: int = DEFAULT_HTTP_TIMEOUT_SECONDS
    MAX_RETRIES: int = DEFAULT_HTTP_MAX_RETRIES
    TOKEN_REFRESH_THRESHOLD_MINUTES: int = 30

    # RG 4444 receiver-identification threshold in ARS. ARCA does not
    # expose this via WS — must be updated manually when ARCA publishes
    # changes. `0` disables the local check (operator can issue without
    # locally enforced ID; ARCA still enforces server-side).
    RG4444_THRESHOLD_ARS: float = 0.0

    @field_validator("CUIT")
    @classmethod
    def _strip_separators(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.replace("-", "").replace(" ", "")
        if not cleaned.isdigit() or len(cleaned) != 11:
            raise ValueError("AFIP_CUIT must be 11 digits (with or without separators)")
        return cleaned

    def is_configured(self) -> bool:
        """Return True if all five required fields are present.

        Allows the rest of the app to start even when AFIP is not
        configured (e.g. during local development of unrelated features).
        Services raise `AfipConfigurationError` lazily when they are
        actually used without configuration."""
        return all(
            getattr(self, field) is not None
            for field in ("CUIT", "POINT_OF_SALE", "CERT_PATH", "KEY_PATH")
        )


afip_settings = AfipSettings()
