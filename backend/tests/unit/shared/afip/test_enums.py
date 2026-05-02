"""Unit tests for shared.afip.enums dispatch tables and helpers.

These are pure-function tests for the matrix that fixes legacy bugs
1, 2, 3 (NA-code mapping, allowed-receivers per class). Cheap to run,
cover the runtime invariants that the full module relies on.
"""
import pytest

from app.shared.afip.enums import (
    IVA_CONDITION_TO_AFIP_CODE,
    IvaCondition,
    ReceiptLetter,
    ReceiptType,
    allowed_afip_codes_for,
    credit_note_for,
    debit_note_for,
    is_class_c,
    is_credit_note,
    is_debit_note,
    is_fce,
    is_invoice,
    is_note,
    receipt_letter,
    requires_iva_block,
    to_fce,
)

pytestmark = pytest.mark.unit


class TestReceiptClassification:
    def test_invoice_a_is_invoice_class_a(self):
        assert is_invoice(ReceiptType.INVOICE_A)
        assert not is_note(ReceiptType.INVOICE_A)
        assert receipt_letter(ReceiptType.INVOICE_A) is ReceiptLetter.A

    def test_credit_note_b_is_note_class_b(self):
        assert is_credit_note(ReceiptType.CREDIT_NOTE_B)
        assert is_note(ReceiptType.CREDIT_NOTE_B)
        assert not is_invoice(ReceiptType.CREDIT_NOTE_B)
        assert receipt_letter(ReceiptType.CREDIT_NOTE_B) is ReceiptLetter.B

    def test_debit_note_c_is_note_class_c(self):
        assert is_debit_note(ReceiptType.DEBIT_NOTE_C)
        assert is_note(ReceiptType.DEBIT_NOTE_C)
        assert is_class_c(ReceiptType.DEBIT_NOTE_C)
        assert not requires_iva_block(ReceiptType.DEBIT_NOTE_C)

    def test_fce_invoice_a_is_fce(self):
        assert is_fce(ReceiptType.FCE_INVOICE_A)
        assert is_invoice(ReceiptType.FCE_INVOICE_A)

    def test_fce_credit_note_b_is_fce_note(self):
        assert is_fce(ReceiptType.FCE_CREDIT_NOTE_B)
        assert is_note(ReceiptType.FCE_CREDIT_NOTE_B)


class TestIvaConditionMapping:
    """Legacy bug 1: NA used to map to non-existent code 3."""

    def test_na_maps_to_15(self):
        assert IVA_CONDITION_TO_AFIP_CODE[IvaCondition.NA] == 15

    def test_ri_maps_to_1(self):
        assert IVA_CONDITION_TO_AFIP_CODE[IvaCondition.RI] == 1

    def test_mt_maps_to_6(self):
        assert IVA_CONDITION_TO_AFIP_CODE[IvaCondition.MT] == 6

    def test_cf_maps_to_5(self):
        assert IVA_CONDITION_TO_AFIP_CODE[IvaCondition.CF] == 5

    def test_no_iva_condition_maps_to_3(self):
        """Code 3 does not exist in ARCA — reject if any condition lands there."""
        assert 3 not in IVA_CONDITION_TO_AFIP_CODE.values()


class TestAllowedReceivers:
    """Legacy bugs 2 & 3: allowed-receivers matrix per class.

    Source of truth is the ARCA runtime (FEParamGetCondicionIvaReceptor),
    verified Apr 2026. Captures the surprising cases:
    - Factura B does NOT accept Monotributo (6).
    - Factura C accepts every condition (it's the wildcard).
    """

    def test_invoice_a_accepts_only_discriminating(self):
        codes = allowed_afip_codes_for(ReceiptType.INVOICE_A)
        assert codes == frozenset({1, 6, 13, 16})

    def test_invoice_b_does_not_accept_monotributo(self):
        codes = allowed_afip_codes_for(ReceiptType.INVOICE_B)
        assert 6 not in codes  # the surprise — MT goes to A or C, never B
        assert codes == frozenset({4, 5, 7, 8, 9, 10, 15})

    def test_invoice_c_is_wildcard(self):
        codes = allowed_afip_codes_for(ReceiptType.INVOICE_C)
        # All known conditions
        assert codes == frozenset({1, 4, 5, 6, 7, 8, 9, 10, 13, 15, 16})

    def test_fce_invoice_a_only_ri_and_monotributo(self):
        codes = allowed_afip_codes_for(ReceiptType.FCE_INVOICE_A)
        assert codes == frozenset({1, 6})

    def test_fce_invoice_b_adds_exempt(self):
        codes = allowed_afip_codes_for(ReceiptType.FCE_INVOICE_B)
        assert codes == frozenset({1, 4, 6})

    def test_credit_note_inherits_invoice_matrix(self):
        # ND/NC class-A receivers are the same as Factura A.
        assert allowed_afip_codes_for(ReceiptType.CREDIT_NOTE_A) == allowed_afip_codes_for(
            ReceiptType.INVOICE_A
        )


class TestNoteForInvoice:
    @pytest.mark.parametrize(
        ("invoice", "expected_credit", "expected_debit"),
        [
            (ReceiptType.INVOICE_A, ReceiptType.CREDIT_NOTE_A, ReceiptType.DEBIT_NOTE_A),
            (ReceiptType.INVOICE_B, ReceiptType.CREDIT_NOTE_B, ReceiptType.DEBIT_NOTE_B),
            (ReceiptType.INVOICE_C, ReceiptType.CREDIT_NOTE_C, ReceiptType.DEBIT_NOTE_C),
            (
                ReceiptType.FCE_INVOICE_A,
                ReceiptType.FCE_CREDIT_NOTE_A,
                ReceiptType.FCE_DEBIT_NOTE_A,
            ),
        ],
    )
    def test_credit_and_debit_note_for_invoice(self, invoice, expected_credit, expected_debit):
        assert credit_note_for(invoice) is expected_credit
        assert debit_note_for(invoice) is expected_debit

    def test_credit_note_for_non_invoice_raises_keyerror(self):
        with pytest.raises(KeyError):
            credit_note_for(ReceiptType.CREDIT_NOTE_A)


class TestToFce:
    def test_invoice_b_to_fce_invoice_b(self):
        assert to_fce(ReceiptType.INVOICE_B) is ReceiptType.FCE_INVOICE_B

    def test_already_fce_is_unchanged(self):
        assert to_fce(ReceiptType.FCE_INVOICE_A) is ReceiptType.FCE_INVOICE_A

    def test_note_unchanged(self):
        # Notes are not invoices — escalation does not apply.
        assert to_fce(ReceiptType.CREDIT_NOTE_B) is ReceiptType.CREDIT_NOTE_B
