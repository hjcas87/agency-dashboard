"""Unit tests for shared.afip.messages — translation function."""
import pytest

from app.shared.afip.enums import IvaCondition
from app.shared.afip.messages import receipt_suggestion_for, translate_afip_error

pytestmark = pytest.mark.unit


class TestTranslateAfipError:
    def test_known_code_returns_friendly_text(self):
        msg = translate_afip_error(10013)
        assert "CUIT" in msg

    def test_unknown_code_returns_generic_with_code(self):
        msg = translate_afip_error(99999, raw_message="raw")
        assert "99999" in msg
        assert "raw" in msg

    def test_10243_substitutes_iva_condition_suggestion(self):
        msg = translate_afip_error(10243, iva_condition=IvaCondition.CF)
        assert "Consumidor Final" in msg

    def test_10243_without_iva_condition_falls_back_generic(self):
        msg = translate_afip_error(10243)
        assert "Sugerencia" in msg


class TestReceiptSuggestion:
    def test_ri_recommends_factura_a(self):
        assert "Factura A" in receipt_suggestion_for(IvaCondition.RI)

    def test_cf_recommends_factura_b_or_c(self):
        suggestion = receipt_suggestion_for(IvaCondition.CF)
        assert "Factura B" in suggestion or "Factura C" in suggestion

    def test_none_falls_back_to_generic(self):
        assert receipt_suggestion_for(None)
