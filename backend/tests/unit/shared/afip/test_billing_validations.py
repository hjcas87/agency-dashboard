"""Unit tests for the pre-AFIP validation pipeline."""
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from app.shared.afip.billing.validations import (
    PIPELINE,
    cuit_required_for_class_a,
    cuit_required_for_fce,
    document_number_length,
    fce_no_categorizado,
    no_categorizado_requires_taxes,
    raise_on_failures,
    receipt_iva_compatibility,
    run_pipeline,
)
from app.shared.afip.enums import (
    Concept,
    DocType,
    IvaAliquotId,
    IvaCondition,
    ReceiptType,
    TransferType,
)
from app.shared.afip.exceptions import AfipValidationError
from app.shared.afip.schemas import FceData, InvoiceRequest, IvaBlock

pytestmark = pytest.mark.unit


def _make_invoice(**overrides: Any) -> InvoiceRequest:
    base: dict[str, Any] = {
        "receipt_type": ReceiptType.INVOICE_B,
        "concept": Concept.PRODUCTS,
        "document_type": DocType.FINAL_CONSUMER,
        "document_number": 0,
        "iva_condition": IvaCondition.CF,
        "issue_date": date(2026, 5, 1),
        "base_amount": Decimal("100"),
        "iva_amount": Decimal("21"),
        "total_amount": Decimal("121"),
        "iva_blocks": [
            IvaBlock(
                aliquot_id=IvaAliquotId.GENERAL,
                base_amount=Decimal("100"),
                amount=Decimal("21"),
            )
        ],
    }
    base.update(overrides)
    return InvoiceRequest(**base)


class TestReceiptIvaCompatibility:
    def test_factura_b_to_cf_passes(self):
        assert receipt_iva_compatibility(_make_invoice()) is None

    def test_factura_a_to_monotributo_passes(self):
        # MT (code 6) is in _STANDARD_A_RECEIVERS.
        req = _make_invoice(
            receipt_type=ReceiptType.INVOICE_A,
            iva_condition=IvaCondition.MT,
            document_type=DocType.CUIT,
            document_number=20431203422,
        )
        assert receipt_iva_compatibility(req) is None

    def test_factura_a_to_cf_rejected_with_10243(self):
        req = _make_invoice(
            receipt_type=ReceiptType.INVOICE_A,
            iva_condition=IvaCondition.CF,
            document_type=DocType.CUIT,
            document_number=20431203422,
        )
        err = receipt_iva_compatibility(req)
        assert err is not None
        assert err.code == 10243

    def test_factura_b_to_monotributo_rejected(self):
        # The runtime quirk: B does NOT accept MT (legacy bug 2/3 catch).
        req = _make_invoice(
            iva_condition=IvaCondition.MT,
            document_type=DocType.CUIT,
            document_number=20431203422,
        )
        err = receipt_iva_compatibility(req)
        assert err is not None
        assert err.code == 10243


class TestCuitRequiredForClassA:
    def test_class_a_with_dni_rejected_with_10013(self):
        req = _make_invoice(
            receipt_type=ReceiptType.INVOICE_A,
            iva_condition=IvaCondition.RI,
            document_type=DocType.DNI,
            document_number=12345678,
        )
        err = cuit_required_for_class_a(req)
        assert err is not None
        assert err.code == 10013

    def test_class_b_with_dni_passes(self):
        req = _make_invoice(document_type=DocType.DNI, document_number=12345678)
        assert cuit_required_for_class_a(req) is None


class TestCuitRequiredForFce:
    def test_fce_with_dni_rejected_with_1487(self):
        req = _make_invoice(
            receipt_type=ReceiptType.FCE_INVOICE_B,
            iva_condition=IvaCondition.RI,
            document_type=DocType.DNI,
            document_number=12345678,
            fce=FceData(
                cbu="0" * 22,
                transfer_type=TransferType.SCA,
                payment_due_date=date(2026, 6, 1),
            ),
        )
        err = cuit_required_for_fce(req)
        assert err is not None
        assert err.code == 1487

    def test_non_fce_with_dni_passes_this_validator(self):
        # cuit_required_for_class_a will catch class A; this validator
        # only fires for FCE.
        req = _make_invoice(document_type=DocType.DNI, document_number=12345678)
        assert cuit_required_for_fce(req) is None


class TestFceNoCategorizado:
    def test_fce_with_no_cat_cuit_rejected_with_10178(self):
        req = _make_invoice(
            receipt_type=ReceiptType.FCE_INVOICE_B,
            iva_condition=IvaCondition.RI,
            document_type=DocType.CUIT,
            document_number=23000000000,
            fce=FceData(
                cbu="0" * 22,
                transfer_type=TransferType.SCA,
                payment_due_date=date(2026, 6, 1),
            ),
        )
        err = fce_no_categorizado(req)
        assert err is not None
        assert err.code == 10178


class TestNoCategorizadoRequiresTaxes:
    def test_no_cat_b_without_taxes_rejected_with_10067(self):
        req = _make_invoice(
            iva_condition=IvaCondition.NC,
            document_type=DocType.CUIT,
            document_number=23000000000,
            taxes_amount=Decimal("0"),
        )
        err = no_categorizado_requires_taxes(req)
        assert err is not None
        assert err.code == 10067

    def test_no_cat_b_with_taxes_passes(self):
        req = _make_invoice(
            iva_condition=IvaCondition.NC,
            document_type=DocType.CUIT,
            document_number=23000000000,
            taxes_amount=Decimal("10"),
            total_amount=Decimal("131"),
        )
        assert no_categorizado_requires_taxes(req) is None


class TestDocumentNumberLength:
    def test_cuit_length_11_passes(self):
        req = _make_invoice(document_type=DocType.CUIT, document_number=20431203422)
        assert document_number_length(req) is None

    def test_cuit_length_short_rejected(self):
        # Document_number is int — Pydantic doesn't enforce digit length;
        # the validator does.
        req = _make_invoice(document_type=DocType.CUIT, document_number=123)
        err = document_number_length(req)
        assert err is not None
        assert err.code == 10015

    def test_dni_length_short_rejected(self):
        req = _make_invoice(document_type=DocType.DNI, document_number=123)
        err = document_number_length(req)
        assert err is not None

    def test_final_consumer_skipped(self):
        req = _make_invoice()  # document_type=FINAL_CONSUMER
        assert document_number_length(req) is None


class TestPipeline:
    def test_run_pipeline_collects_all_failures(self):
        # Class A + DNI + CF triggers both 10013 and 10243.
        req = _make_invoice(
            receipt_type=ReceiptType.INVOICE_A,
            document_type=DocType.DNI,
            document_number=12345678,
        )
        failures = run_pipeline(req)
        codes = {f.code for f in failures}
        # 10013 (DocType wrong) AND 10243 (CF receiver for class A) should both fire.
        assert 10013 in codes
        assert 10243 in codes

    def test_raise_on_failures_packs_errors(self):
        req = _make_invoice(receipt_type=ReceiptType.INVOICE_A)
        with pytest.raises(AfipValidationError) as excinfo:
            raise_on_failures(req)
        # AfipValidationError carries the structured errors list.
        assert excinfo.value.errors

    def test_pipeline_order_documented(self):
        # Doc-number first, IVA-compat last — the order matters when
        # surfacing the first-cause error to the operator.
        names = [v.__name__ for v in PIPELINE]
        assert names[0] == "document_number_length"
        assert names[-1] == "receipt_iva_compatibility"
