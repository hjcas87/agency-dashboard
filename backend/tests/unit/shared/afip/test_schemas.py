"""Unit tests for shared.afip.schemas Pydantic validators.

Schema-level invariants are the first defense — they reject inputs at
construction time before anything else runs. These tests pin those
invariants so a refactor cannot relax them silently.
"""
from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from app.shared.afip.enums import (
    CancellationFlag,
    Concept,
    DocType,
    IvaAliquotId,
    IvaCondition,
    ReceiptType,
    TransferType,
)
from app.shared.afip.schemas import (
    AssociatedReceipt,
    FceData,
    InvoiceRequest,
    IvaBlock,
    TaxpayerRequest,
)

pytestmark = pytest.mark.unit


def _base_invoice_kwargs(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "receipt_type": ReceiptType.INVOICE_B,
        "concept": Concept.PRODUCTS,
        "document_type": DocType.FINAL_CONSUMER,
        "document_number": 0,
        "iva_condition": IvaCondition.CF,
        "issue_date": date(2026, 5, 1),
        "base_amount": Decimal("100.00"),
        "iva_amount": Decimal("21.00"),
        "total_amount": Decimal("121.00"),
        "iva_blocks": [
            IvaBlock(
                aliquot_id=IvaAliquotId.GENERAL,
                base_amount=Decimal("100"),
                amount=Decimal("21"),
            )
        ],
    }
    base.update(overrides)
    return base


class TestInvoiceRequestHappyPath:
    def test_factura_b_to_cf_constructs(self):
        req = InvoiceRequest(**_base_invoice_kwargs())
        assert req.receipt_type is ReceiptType.INVOICE_B
        assert req.total_amount == Decimal("121.00")


class TestClassCInvariants:
    def test_class_c_rejects_iva_amount(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(
                **_base_invoice_kwargs(
                    receipt_type=ReceiptType.INVOICE_C,
                    iva_amount=Decimal("21"),
                    iva_blocks=[],
                )
            )

    def test_class_c_rejects_non_taxable_amount(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(
                **_base_invoice_kwargs(
                    receipt_type=ReceiptType.INVOICE_C,
                    iva_amount=Decimal("0"),
                    non_taxable_amount=Decimal("10"),
                    iva_blocks=[],
                )
            )

    def test_class_c_rejects_iva_blocks(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(
                **_base_invoice_kwargs(
                    receipt_type=ReceiptType.INVOICE_C,
                    iva_amount=Decimal("0"),
                )
            )

    def test_class_c_clean_passes(self):
        req = InvoiceRequest(
            **_base_invoice_kwargs(
                receipt_type=ReceiptType.INVOICE_C,
                iva_amount=Decimal("0"),
                iva_blocks=[],
                base_amount=Decimal("100"),
                total_amount=Decimal("100"),
            )
        )
        assert req.iva_blocks == []


class TestServiceWindowDates:
    def test_services_concept_requires_dates(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(**_base_invoice_kwargs(concept=Concept.SERVICES))

    def test_services_concept_with_dates_passes(self):
        req = InvoiceRequest(
            **_base_invoice_kwargs(
                concept=Concept.SERVICES,
                service_date_from=date(2026, 4, 1),
                service_date_to=date(2026, 4, 30),
            )
        )
        assert req.service_date_from == date(2026, 4, 1)


class TestNotesNeedAssociations:
    def test_note_without_association_rejected(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(**_base_invoice_kwargs(receipt_type=ReceiptType.CREDIT_NOTE_B))

    def test_note_with_association_passes(self):
        req = InvoiceRequest(
            **_base_invoice_kwargs(
                receipt_type=ReceiptType.CREDIT_NOTE_B,
                associated_receipts=[
                    AssociatedReceipt(
                        receipt_type=ReceiptType.INVOICE_B,
                        point_of_sale=1,
                        receipt_number=1,
                    )
                ],
            )
        )
        assert len(req.associated_receipts) == 1


class TestFceInvariants:
    def test_fce_invoice_requires_fce_block(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(
                **_base_invoice_kwargs(
                    receipt_type=ReceiptType.FCE_INVOICE_B,
                    iva_condition=IvaCondition.RI,
                    document_type=DocType.CUIT,
                    document_number=20431203422,
                )
            )

    def test_non_fce_with_fce_block_rejected(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(
                **_base_invoice_kwargs(
                    fce=FceData(
                        cbu="0123456789012345678901",
                        transfer_type=TransferType.SCA,
                        payment_due_date=date(2026, 6, 1),
                    )
                )
            )

    def test_fce_invoice_requires_cbu_and_transfer(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(
                **_base_invoice_kwargs(
                    receipt_type=ReceiptType.FCE_INVOICE_B,
                    iva_condition=IvaCondition.RI,
                    document_type=DocType.CUIT,
                    document_number=20431203422,
                    fce=FceData(payment_due_date=date(2026, 6, 1)),
                )
            )

    def test_fce_invoice_requires_payment_due_date(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(
                **_base_invoice_kwargs(
                    receipt_type=ReceiptType.FCE_INVOICE_B,
                    iva_condition=IvaCondition.RI,
                    document_type=DocType.CUIT,
                    document_number=20431203422,
                    fce=FceData(cbu="0123456789012345678901", transfer_type=TransferType.SCA),
                )
            )

    def test_fce_note_requires_cancellation(self):
        with pytest.raises(ValidationError):
            InvoiceRequest(
                **_base_invoice_kwargs(
                    receipt_type=ReceiptType.FCE_CREDIT_NOTE_B,
                    iva_condition=IvaCondition.RI,
                    document_type=DocType.CUIT,
                    document_number=20431203422,
                    fce=FceData(),
                    associated_receipts=[
                        AssociatedReceipt(
                            receipt_type=ReceiptType.FCE_INVOICE_B,
                            point_of_sale=1,
                            receipt_number=1,
                        )
                    ],
                )
            )

    def test_fce_note_with_cancellation_passes(self):
        req = InvoiceRequest(
            **_base_invoice_kwargs(
                receipt_type=ReceiptType.FCE_CREDIT_NOTE_B,
                iva_condition=IvaCondition.RI,
                document_type=DocType.CUIT,
                document_number=20431203422,
                fce=FceData(cancellation=CancellationFlag.NO),
                associated_receipts=[
                    AssociatedReceipt(
                        receipt_type=ReceiptType.FCE_INVOICE_B,
                        point_of_sale=1,
                        receipt_number=1,
                    )
                ],
            )
        )
        assert req.fce is not None
        assert req.fce.cancellation is CancellationFlag.NO


class TestCuitNormalization:
    def test_taxpayer_cuit_strips_separators(self):
        assert TaxpayerRequest(cuit="20-12345678-9").cuit == "20123456789"

    def test_taxpayer_cuit_strips_spaces(self):
        assert TaxpayerRequest(cuit="20 12345678 9").cuit == "20123456789"

    def test_taxpayer_cuit_short_rejected(self):
        with pytest.raises(ValidationError):
            TaxpayerRequest(cuit="123")

    def test_associated_receipt_cuit_normalized(self):
        rec = AssociatedReceipt(
            receipt_type=ReceiptType.INVOICE_B,
            point_of_sale=1,
            receipt_number=1,
            issuer_cuit="20-12345678-9",
        )
        assert rec.issuer_cuit == "20123456789"


class TestCbuValidation:
    def test_cbu_rejects_short(self):
        with pytest.raises(ValidationError):
            FceData(cbu="123")

    def test_cbu_rejects_non_digits(self):
        with pytest.raises(ValidationError):
            FceData(cbu="01234567890123456789ab")

    def test_cbu_22_digits_passes(self):
        fce = FceData(cbu="0" * 22)
        assert fce.cbu == "0" * 22
