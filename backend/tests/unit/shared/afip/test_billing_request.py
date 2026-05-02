"""Unit tests for shared.afip.billing.request — pure XML builder.

The builder is the surface area where bug 12 of the legacy module
lived (f-string XML breaking on hostile chars). These tests pin the
escape behavior, the FCE optional-codes layout, and the FchVtoPago
emission rules.
"""
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from app.shared.afip.billing.request import build_authorize_request
from app.shared.afip.constants import WSFE_NAMESPACE
from app.shared.afip.enums import (
    CancellationFlag,
    Concept,
    DocType,
    IvaAliquotId,
    IvaCondition,
    ReceiptType,
    TransferType,
)
from app.shared.afip.schemas import AssociatedReceipt, FceData, InvoiceRequest, IvaBlock

pytestmark = pytest.mark.unit


def _q(tag: str) -> str:
    return f"{{{WSFE_NAMESPACE}}}{tag}"


def _make_invoice(**overrides: Any) -> InvoiceRequest:
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
    return InvoiceRequest(**base)


def _build(invoice: InvoiceRequest, **kwargs: Any) -> str:
    defaults: dict[str, Any] = {
        "token": "T",
        "sign": "S",
        "issuer_cuit": "20410646243",
        "point_of_sale": 1,
        "receipt_number": 1,
    }
    defaults.update(kwargs)
    return build_authorize_request(request=invoice, **defaults)


class TestFacturaB:
    def test_emits_correct_cbtetipo_and_amounts(self):
        xml = _build(_make_invoice(), receipt_number=42)
        root = ET.fromstring(xml)
        assert root.findtext(f".//{_q('CbteTipo')}") == "6"
        assert root.findtext(f".//{_q('CbteDesde')}") == "42"
        assert root.findtext(f".//{_q('CbteHasta')}") == "42"
        assert root.findtext(f".//{_q('ImpTotal')}") == "121.00"
        assert root.findtext(f".//{_q('ImpIVA')}") == "21.00"

    def test_iva_block_has_general_aliquot(self):
        xml = _build(_make_invoice())
        root = ET.fromstring(xml)
        assert root.findtext(f".//{_q('AlicIva')}/{_q('Id')}") == "5"

    def test_condicion_iva_receptor_is_cf_code(self):
        xml = _build(_make_invoice())
        root = ET.fromstring(xml)
        # CF maps to ARCA code 5.
        assert root.findtext(f".//{_q('CondicionIVAReceptorId')}") == "5"

    def test_products_only_omits_fchvtopago(self):
        xml = _build(_make_invoice())
        assert "FchVtoPago" not in xml


class TestFacturaC:
    def test_omits_iva_block(self):
        xml = _build(
            _make_invoice(
                receipt_type=ReceiptType.INVOICE_C,
                iva_amount=Decimal("0"),
                iva_blocks=[],
                base_amount=Decimal("100"),
                total_amount=Decimal("100"),
            )
        )
        # The Iva container itself must be absent (not just empty).
        assert "<ar:Iva>" not in xml
        # ImpIVA must be 0.
        root = ET.fromstring(xml)
        assert root.findtext(f".//{_q('ImpIVA')}") == "0.00"


class TestFceFactura:
    def test_emits_optional_cbu_and_transfer(self):
        invoice = _make_invoice(
            receipt_type=ReceiptType.FCE_INVOICE_B,
            iva_condition=IvaCondition.RI,
            document_type=DocType.CUIT,
            document_number=30643411861,
            fce=FceData(
                cbu="0" * 22,
                transfer_type=TransferType.SCA,
                payment_due_date=date(2026, 6, 1),
            ),
        )
        xml = _build(invoice)
        root = ET.fromstring(xml)
        opt_ids = [
            opt.findtext(_q("Id"))
            for opt in root.findall(f".//{_q('Opcionales')}/{_q('Opcional')}")
        ]
        assert "2101" in opt_ids
        assert "27" in opt_ids
        assert root.findtext(f".//{_q('FchVtoPago')}") == "20260601"

    def test_fce_credit_note_emits_cancellation_flag(self):
        invoice = _make_invoice(
            receipt_type=ReceiptType.FCE_CREDIT_NOTE_B,
            iva_condition=IvaCondition.RI,
            document_type=DocType.CUIT,
            document_number=30643411861,
            fce=FceData(cancellation=CancellationFlag.NO),
            associated_receipts=[
                AssociatedReceipt(
                    receipt_type=ReceiptType.FCE_INVOICE_B,
                    point_of_sale=1,
                    receipt_number=1,
                )
            ],
        )
        xml = _build(invoice)
        root = ET.fromstring(xml)
        opt_ids = [
            opt.findtext(_q("Id"))
            for opt in root.findall(f".//{_q('Opcionales')}/{_q('Opcional')}")
        ]
        assert opt_ids == ["22"]


class TestAssociatedReceipts:
    def test_credit_note_emits_cbtesasoc(self):
        invoice = _make_invoice(
            receipt_type=ReceiptType.CREDIT_NOTE_B,
            associated_receipts=[
                AssociatedReceipt(
                    receipt_type=ReceiptType.INVOICE_B,
                    point_of_sale=1,
                    receipt_number=42,
                    issue_date=date(2026, 5, 1),
                    issuer_cuit="20410646243",
                )
            ],
        )
        xml = _build(invoice, receipt_number=5)
        root = ET.fromstring(xml)
        asoc = root.find(f".//{_q('CbteAsoc')}")
        assert asoc is not None
        assert asoc.findtext(_q("Tipo")) == "6"
        assert asoc.findtext(_q("Nro")) == "42"
        assert asoc.findtext(_q("CbteFch")) == "20260501"
        assert asoc.findtext(_q("Cuit")) == "20410646243"


class TestServicesConcept:
    def test_emits_service_dates_and_payment_due(self):
        invoice = _make_invoice(
            concept=Concept.SERVICES,
            service_date_from=date(2026, 4, 1),
            service_date_to=date(2026, 4, 30),
            payment_due_date=date(2026, 5, 31),
        )
        xml = _build(invoice)
        root = ET.fromstring(xml)
        assert root.findtext(f".//{_q('FchServDesde')}") == "20260401"
        assert root.findtext(f".//{_q('FchServHasta')}") == "20260430"
        assert root.findtext(f".//{_q('FchVtoPago')}") == "20260531"


class TestXmlEscape:
    @pytest.mark.parametrize("hostile", ["<token>", "tok&en", 'with "quotes"', "amp & spaces"])
    def test_token_escape_round_trips(self, hostile):
        invoice = _make_invoice()
        xml = _build(invoice, token=hostile)
        # Parsing must succeed — that is the actual contract.
        root = ET.fromstring(xml)
        # The literal hostile chars must NOT appear in the raw string.
        assert "<" + hostile not in xml.replace("&lt;", "ESC")
        # And the round-tripped value must equal the input.
        assert root.findtext(f".//{_q('Token')}") == hostile

    def test_commercial_reference_escape(self):
        invoice = _make_invoice(commercial_reference='Ref "with" <tags>')
        xml = _build(invoice)
        root = ET.fromstring(xml)
        opt = root.findall(f".//{_q('Opcional')}")
        assert len(opt) == 1
        assert opt[0].findtext(_q("Valor")) == 'Ref "with" <tags>'
