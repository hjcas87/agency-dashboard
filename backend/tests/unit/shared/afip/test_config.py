"""Unit tests for shared.afip.config — AfipSettings validation."""
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.shared.afip.config import AfipSettings
from app.shared.afip.enums import AfipEnvironment, CurrencyId

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Point AfipSettings at a non-existent .env so the tests never see
    the local backend/.env (which carries the operator's real CUIT) and
    strip any AFIP_* vars the host might have set."""
    monkeypatch.setattr("app.shared.afip.config.ENV_FILE", tmp_path / "missing.env")
    for key in (
        "AFIP_ENVIRONMENT",
        "AFIP_CUIT",
        "AFIP_POINT_OF_SALE",
        "AFIP_CERT_PATH",
        "AFIP_KEY_PATH",
        "AFIP_CURRENCY_ID",
        "AFIP_TIMEOUT_SECONDS",
        "AFIP_MAX_RETRIES",
        "AFIP_TOKEN_REFRESH_THRESHOLD_MINUTES",
        "AFIP_RG4444_THRESHOLD_ARS",
    ):
        monkeypatch.delenv(key, raising=False)


class TestCuitValidator:
    def test_strips_dashes(self) -> None:
        assert AfipSettings(CUIT="20-12345678-9").CUIT == "20123456789"

    def test_strips_spaces(self) -> None:
        assert AfipSettings(CUIT="20 12345678 9").CUIT == "20123456789"

    def test_rejects_short(self) -> None:
        with pytest.raises(ValidationError):
            AfipSettings(CUIT="123")

    def test_rejects_non_digits(self) -> None:
        with pytest.raises(ValidationError):
            AfipSettings(CUIT="20abcdefgh9")

    def test_none_passes(self) -> None:
        assert AfipSettings(CUIT=None).CUIT is None


class TestIsConfigured:
    def test_all_required_present(self, tmp_path: Path) -> None:
        s = AfipSettings(
            CUIT="20123456789",
            POINT_OF_SALE=1,
            CERT_PATH=tmp_path / "c.crt",
            KEY_PATH=tmp_path / "k.key",
        )
        assert s.is_configured() is True

    def test_missing_cuit_is_unconfigured(self, tmp_path: Path) -> None:
        s = AfipSettings(
            CUIT=None,
            POINT_OF_SALE=1,
            CERT_PATH=tmp_path / "c.crt",
            KEY_PATH=tmp_path / "k.key",
        )
        assert s.is_configured() is False


class TestDefaults:
    def test_environment_defaults_to_homo(self) -> None:
        assert AfipSettings().ENVIRONMENT is AfipEnvironment.HOMO

    def test_currency_defaults_to_pes(self) -> None:
        assert AfipSettings().CURRENCY_ID is CurrencyId.PES
