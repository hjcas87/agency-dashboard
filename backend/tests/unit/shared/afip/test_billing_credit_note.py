"""Unit tests for CreditNoteService note-specific local rules.

Uses a stubbed BillingService — the wrapper logic is what matters
here, not the orchestration."""
from datetime import date
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.shared.afip.billing.credit_note import CreditNoteService
from app.shared.afip.enums import Concept, DocType, IvaAliquotId, IvaCondition, ReceiptType
from app.shared.afip.exceptions import AfipValidationError
from app.shared.afip.schemas import AssociatedReceipt, InvoiceRequest, IvaBlock

pytestmark = pytest.mark.unit


def _credit_note(**overrides: Any) -> InvoiceRequest:
    base: dict[str, Any] = {
        "receipt_type": ReceiptType.CREDIT_NOTE_B,
        "concept": Concept.PRODUCTS,
        "document_type": DocType.FINAL_CONSUMER,
        "document_number": 0,
        "iva_condition": IvaCondition.CF,
        "issue_date": date(2026, 5, 2),
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
        "associated_receipts": [
            AssociatedReceipt(
                receipt_type=ReceiptType.INVOICE_B,
                point_of_sale=1,
                receipt_number=1,
                issue_date=date(2026, 5, 1),
            )
        ],
    }
    base.update(overrides)
    return InvoiceRequest(**base)


class TestKindMismatch:
    def test_issue_credit_note_with_debit_note_rejected(self):
        billing = MagicMock()
        service = CreditNoteService(billing)
        with pytest.raises(AfipValidationError) as excinfo:
            service.issue_credit_note(_credit_note(receipt_type=ReceiptType.DEBIT_NOTE_B))
        billing.issue.assert_not_called()
        assert "issue_credit_note called with DEBIT_NOTE_B" in str(excinfo.value)

    def test_issue_debit_note_with_credit_note_rejected(self):
        billing = MagicMock()
        service = CreditNoteService(billing)
        with pytest.raises(AfipValidationError):
            service.issue_debit_note(_credit_note())
        billing.issue.assert_not_called()


class TestClassMismatch:
    def test_b_note_to_a_invoice_rejected(self):
        billing = MagicMock()
        service = CreditNoteService(billing)
        request = _credit_note(
            associated_receipts=[
                AssociatedReceipt(
                    receipt_type=ReceiptType.INVOICE_A, point_of_sale=1, receipt_number=1
                )
            ]
        )
        with pytest.raises(AfipValidationError) as excinfo:
            service.issue_credit_note(request)
        # The error list includes 10040.
        assert any(code == 10040 for code, _msg in excinfo.value.errors)


class TestDateOrder:
    def test_note_earlier_than_associated_rejected(self):
        billing = MagicMock()
        service = CreditNoteService(billing)
        request = _credit_note(
            issue_date=date(2026, 4, 30),
            associated_receipts=[
                AssociatedReceipt(
                    receipt_type=ReceiptType.INVOICE_B,
                    point_of_sale=1,
                    receipt_number=1,
                    issue_date=date(2026, 5, 1),
                )
            ],
        )
        with pytest.raises(AfipValidationError) as excinfo:
            service.issue_credit_note(request)
        assert any(code == 10210 for code, _ in excinfo.value.errors)

    def test_associated_without_date_skipped(self):
        # Without an associated date, the rule cannot fire — wrapper just
        # delegates.
        billing = MagicMock()
        billing.issue.return_value = "delegated"
        service = CreditNoteService(billing)
        request = _credit_note(
            associated_receipts=[
                AssociatedReceipt(
                    receipt_type=ReceiptType.INVOICE_B,
                    point_of_sale=1,
                    receipt_number=1,
                )
            ]
        )
        result = service.issue_credit_note(request)
        assert result == "delegated"
        billing.issue.assert_called_once_with(request)


class TestValidPassthrough:
    def test_valid_credit_note_delegates_to_billing(self):
        billing = MagicMock()
        billing.issue.return_value = "delegated"
        service = CreditNoteService(billing)
        result = service.issue_credit_note(_credit_note())
        assert result == "delegated"
        billing.issue.assert_called_once()
