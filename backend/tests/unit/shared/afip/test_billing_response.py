"""Unit tests for shared.afip.billing.response — pure XML parser."""
from datetime import date

import pytest

from app.shared.afip.billing.response import parse_authorize_response
from app.shared.afip.enums import ReceiptType
from app.shared.afip.exceptions import AfipServiceError

pytestmark = pytest.mark.unit


def _wrap(inner: str) -> str:
    return f"""<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
 <soap:Body>
  <FECAESolicitarResponse xmlns="http://ar.gov.afip.dif.FEV1/">
   <FECAESolicitarResult>{inner}</FECAESolicitarResult>
  </FECAESolicitarResponse>
 </soap:Body>
</soap:Envelope>"""


class TestApprovedResponse:
    def test_parses_cae_and_expiration(self):
        xml = _wrap(
            """
            <FeCabResp>
              <Cuit>20410646243</Cuit>
              <PtoVta>1</PtoVta>
              <CbteTipo>6</CbteTipo>
              <Resultado>A</Resultado>
            </FeCabResp>
            <FeDetResp>
             <FECAEDetResponse>
              <CbteDesde>42</CbteDesde>
              <CbteHasta>42</CbteHasta>
              <Resultado>A</Resultado>
              <CAE>74098765432109</CAE>
              <CAEFchVto>20260511</CAEFchVto>
             </FECAEDetResponse>
            </FeDetResp>
            """
        )
        result = parse_authorize_response(
            xml,
            requested_receipt_type=ReceiptType.INVOICE_B,
            requested_point_of_sale=1,
        )
        assert result.success is True
        assert result.cae == "74098765432109"
        assert result.cae_expiration == date(2026, 5, 11)
        assert result.receipt_number == 42
        assert result.authorized_cbte_tipo == 6
        assert result.errors == []

    def test_authorized_cbte_tipo_falls_back_when_unknown(self):
        # ARCA returns a CbteTipo we don't have in the enum (hypothetical).
        xml = _wrap(
            """
            <FeCabResp>
              <PtoVta>1</PtoVta>
              <CbteTipo>9999</CbteTipo>
              <Resultado>A</Resultado>
            </FeCabResp>
            <FeDetResp>
             <FECAEDetResponse>
              <CbteDesde>1</CbteDesde><CbteHasta>1</CbteHasta>
              <Resultado>A</Resultado>
              <CAE>X</CAE><CAEFchVto>20260511</CAEFchVto>
             </FECAEDetResponse>
            </FeDetResp>
            """
        )
        result = parse_authorize_response(
            xml, requested_receipt_type=ReceiptType.INVOICE_B, requested_point_of_sale=1
        )
        # authorized_cbte_tipo carries the raw int even when unknown
        assert result.authorized_cbte_tipo == 9999
        # receipt_type falls back to the requested one
        assert result.receipt_type is ReceiptType.INVOICE_B


class TestRejectedResponse:
    def test_top_level_errors_make_failure(self):
        xml = _wrap(
            """
            <Errors>
              <Err>
                <Code>10243</Code>
                <Msg>Para Comprobantes A no se permite ese codigo de IVA</Msg>
              </Err>
            </Errors>
            """
        )
        result = parse_authorize_response(
            xml, requested_receipt_type=ReceiptType.INVOICE_A, requested_point_of_sale=1
        )
        assert result.success is False
        assert result.errors[0].code == 10243
        assert result.cae is None

    def test_detail_resultado_r_makes_failure(self):
        # Cabecera says A but detail says R — defensive: must reject.
        xml = _wrap(
            """
            <FeCabResp>
              <PtoVta>1</PtoVta>
              <CbteTipo>6</CbteTipo>
              <Resultado>A</Resultado>
            </FeCabResp>
            <FeDetResp>
             <FECAEDetResponse>
              <CbteDesde>1</CbteDesde><CbteHasta>1</CbteHasta>
              <Resultado>R</Resultado>
              <CAE></CAE><CAEFchVto></CAEFchVto>
              <Observaciones>
               <Obs><Code>10015</Code><Msg>Padron mismatch</Msg></Obs>
              </Observaciones>
             </FECAEDetResponse>
            </FeDetResp>
            """
        )
        result = parse_authorize_response(
            xml, requested_receipt_type=ReceiptType.INVOICE_B, requested_point_of_sale=1
        )
        assert result.success is False
        assert len(result.observations) == 1
        assert result.observations[0].code == 10015


class TestObservationsAreNonBlocking:
    def test_approved_with_observation(self):
        xml = _wrap(
            """
            <FeCabResp>
              <PtoVta>1</PtoVta>
              <CbteTipo>1</CbteTipo>
              <Resultado>A</Resultado>
            </FeCabResp>
            <FeDetResp>
             <FECAEDetResponse>
              <CbteDesde>10</CbteDesde><CbteHasta>10</CbteHasta>
              <Resultado>A</Resultado>
              <CAE>74012345678901</CAE>
              <CAEFchVto>20260511</CAEFchVto>
              <Observaciones>
               <Obs><Code>10217</Code><Msg>Credito fiscal a Monotributista</Msg></Obs>
              </Observaciones>
             </FECAEDetResponse>
            </FeDetResp>
            """
        )
        result = parse_authorize_response(
            xml, requested_receipt_type=ReceiptType.INVOICE_A, requested_point_of_sale=1
        )
        assert result.success is True
        assert result.observations[0].code == 10217


class TestMalformed:
    def test_unparseable_xml_raises(self):
        with pytest.raises(AfipServiceError):
            parse_authorize_response(
                "<not really xml",
                requested_receipt_type=ReceiptType.INVOICE_B,
                requested_point_of_sale=1,
            )

    def test_missing_result_node_raises(self):
        with pytest.raises(AfipServiceError):
            parse_authorize_response(
                "<envelope/>",
                requested_receipt_type=ReceiptType.INVOICE_B,
                requested_point_of_sale=1,
            )
