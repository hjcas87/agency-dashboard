"""Invoice PDF renderer — matches the canonical AFIP receipt layout.

Receives an entirely data-driven payload (no hardcoded issuer / client /
totals — the consumer feature passes them all). The visual structure
mirrors the AFIP printed receipt:

    +------------------------ ORIGINAL ------------------------+
    |  ISSUER LEGAL NAME       | C  | FACTURA                  |
    |  Razón Social: ...       |011 | Pto. Vta: ... Comp:...   |
    |  Domicilio: ...          |    | Fecha de Venta: ...      |
    |  Cond. IVA: ...          |    | CUIT / Ing. Brutos       |
    |                          |    | Inicio Actividades       |
    +----------------------------------------------------------+
    | Período Facturado: Desde – Hasta | Receiver block        |
    +----------------------------------------------------------+
    | items table                                              |
    +----------------------------------------------------------+
    |                                  Subtotal: ...           |
    |                                  Otros tributos: ...     |
    |                                  IMPORTE TOTAL: ...      |
    +----------------------------------------------------------+
    | [QR] [ARCA] | Comprobante Autorizado |  Pág 1/1 — CAE …  |

The renderer is fully agnostic of the issuer's identity and the
client / project. The hardcoded data lives in the consumer feature
(see `app/custom/features/invoices/issuer.py` for the agency-dashboard
case) and is passed in via the `data["issuer"]` dict.
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle

from app.shared.pdf.renderers.base import PdfRenderer
from app.shared.pdf.template import PdfTemplate

# AFIP receipts use a uniform light-grey for every border and for the
# items-table header background. Keeping it in one constant means the
# whole document re-themes by changing this single value.
BORDER = HexColor("#cccccc")
HEADER_BG = HexColor("#cccccc")

# ARCA receipt-letter mapping — only the codes this renderer knows how
# to label. Receipts outside the table fall back to the raw value.
RECEIPT_LETTER_BY_CODE: dict[int, str] = {
    1: "A",
    2: "A",
    3: "A",
    6: "B",
    7: "B",
    8: "B",
    11: "C",
    12: "C",
    13: "C",
    51: "M",
    52: "M",
    53: "M",
    201: "A",
    202: "A",
    203: "A",
    206: "B",
    207: "B",
    208: "B",
    211: "C",
    212: "C",
    213: "C",
}

# `COD. <nnn>` — the inner code shown under the big letter.
RECEIPT_CODE_BY_TYPE: dict[int, str] = {
    1: "001",
    2: "002",
    3: "003",
    6: "006",
    7: "007",
    8: "008",
    11: "011",
    12: "012",
    13: "013",
    201: "201",
    202: "202",
    203: "203",
    206: "206",
    207: "207",
    208: "208",
    211: "211",
    212: "212",
    213: "213",
}

RECEIPT_NAME_BY_TYPE: dict[int, str] = {
    1: "FACTURA",
    6: "FACTURA",
    11: "FACTURA",
    51: "FACTURA",
    201: "FCE FACTURA",
    206: "FCE FACTURA",
    211: "FCE FACTURA",
    2: "NOTA DE DÉBITO",
    7: "NOTA DE DÉBITO",
    12: "NOTA DE DÉBITO",
    52: "NOTA DE DÉBITO",
    202: "FCE NOTA DE DÉBITO",
    207: "FCE NOTA DE DÉBITO",
    212: "FCE NOTA DE DÉBITO",
    3: "NOTA DE CRÉDITO",
    8: "NOTA DE CRÉDITO",
    13: "NOTA DE CRÉDITO",
    53: "NOTA DE CRÉDITO",
    203: "FCE NOTA DE CRÉDITO",
    208: "FCE NOTA DE CRÉDITO",
    213: "FCE NOTA DE CRÉDITO",
}


class InvoicePdfRenderer(PdfRenderer):
    """Render an AFIP-shaped Factura into a list of reportlab flowables.

    `data` shape:
        {
            "issuer": {legal_name, address, iva_condition_label, cuit,
                       gross_income, activity_start_date, logo_path},
            "customer": {legal_name, doc_label, doc_number,
                         iva_condition_label, address},
            "invoice": {receipt_type, point_of_sale, receipt_number,
                        issue_date, period_from, period_to,
                        due_date, condition_of_sale},
            "items":   [{code, name, quantity, unit, unit_price,
                         discount_pct, discount_amount, subtotal}, ...],
            "totals":  {subtotal, other_taxes, total},
            "afip":    {cae, cae_expiration, qr_png_bytes, page_label}
        }
    """

    # AFIP-style receipts go nearly edge-to-edge — 5mm margin on each side
    # leaves a 200mm-wide content area on A4 (210 - 10 = 200). The bottom
    # margin reserves a fixed strip for the totals + QR/ARCA/CAE block,
    # which is drawn by `make_page_callback` so it always sits at the
    # foot of the page regardless of how tall the items table grows.
    page_margins_mm = (8, 5, 56, 5)

    # Total content width all sub-tables target.
    CONTENT_WIDTH_MM = 200

    # Fixed height for the issuer / receipt-id row. Keeping it fixed lets
    # the C-box's "Y trunk" know exactly how far it must extend down, and
    # avoids the trunk-line being clipped by a row that's too short.
    HEADER_CONTENT_HEIGHT_MM = 42
    LETTER_BOX_HEIGHT_MM = 16

    def render(self, data: dict, template: PdfTemplate) -> list:
        styles = self._build_styles(template)
        story: list[Any] = [
            self._build_main_header(data, styles),
            Spacer(1, 2 * mm),
            self._build_period_and_customer(data, styles),
            Spacer(1, 3 * mm),
            self._build_items_table(data, styles),
        ]
        return story

    def make_page_callback(
        self, data: dict, template: PdfTemplate
    ) -> Callable:
        """Draw totals + QR/ARCA/CAE block pinned to the bottom of every page.

        The items table flows in the normal story above; this block stays
        at a fixed offset from the page bottom so the receipt always
        looks "footer-anchored" like the canonical AFIP printout.
        """
        styles = self._build_styles(template)
        totals = self._build_totals(data, styles)
        footer = self._build_footer(data, styles)
        content_w = self.CONTENT_WIDTH_MM * mm
        left_margin = self.page_margins_mm[3] * mm

        def _on_page(canvas, doc) -> None:
            _, footer_h = footer.wrapOn(canvas, content_w, 60 * mm)
            footer_y = 8 * mm
            footer.drawOn(canvas, left_margin, footer_y)

            totals.wrapOn(canvas, content_w, 30 * mm)
            totals_y = footer_y + footer_h + 4 * mm
            totals.drawOn(canvas, left_margin, totals_y)

        return _on_page

    # ── Styles ────────────────────────────────────────────────────

    def _build_styles(self, template: PdfTemplate) -> dict[str, ParagraphStyle]:
        base = getSampleStyleSheet()
        return {
            "Original": ParagraphStyle(
                "Original",
                parent=base["Normal"],
                fontSize=11,
                fontName="Helvetica-Bold",
                alignment=TA_CENTER,
                leading=13,
            ),
            "IssuerName": ParagraphStyle(
                "IssuerName",
                parent=base["Normal"],
                fontSize=9,
                fontName="Helvetica-Bold",
                alignment=TA_LEFT,
                leading=11,
            ),
            "Label": ParagraphStyle(
                "Label",
                parent=base["Normal"],
                fontSize=7.5,
                fontName="Helvetica-Bold",
                alignment=TA_LEFT,
                leading=10,
            ),
            "LabelRight": ParagraphStyle(
                "LabelRight",
                parent=base["Normal"],
                fontSize=7.5,
                fontName="Helvetica-Bold",
                alignment=TA_LEFT,
                leading=10,
            ),
            "Value": ParagraphStyle(
                "Value",
                parent=base["Normal"],
                fontSize=7.5,
                alignment=TA_LEFT,
                leading=10,
            ),
            "BigLetter": ParagraphStyle(
                "BigLetter",
                parent=base["Normal"],
                fontSize=22,
                fontName="Helvetica-Bold",
                alignment=TA_CENTER,
                leading=22,
            ),
            "ReceiptCode": ParagraphStyle(
                "ReceiptCode",
                parent=base["Normal"],
                fontSize=6,
                fontName="Helvetica-Bold",
                alignment=TA_CENTER,
                leading=7,
            ),
            "ReceiptName": ParagraphStyle(
                "ReceiptName",
                parent=base["Normal"],
                fontSize=15,
                fontName="Helvetica-Bold",
                alignment=TA_LEFT,
                leading=17,
            ),
            "TableHeader": ParagraphStyle(
                "TableHeader",
                parent=base["Normal"],
                fontSize=8,
                fontName="Helvetica-Bold",
                alignment=TA_CENTER,
                textColor=black,
            ),
            "TableCell": ParagraphStyle(
                "TableCell",
                parent=base["Normal"],
                fontSize=8,
                alignment=TA_LEFT,
            ),
            "TableCellRight": ParagraphStyle(
                "TableCellRight",
                parent=base["Normal"],
                fontSize=8,
                alignment=TA_RIGHT,
            ),
            "TotalLabel": ParagraphStyle(
                "TotalLabel",
                parent=base["Normal"],
                fontSize=9,
                alignment=TA_RIGHT,
            ),
            "TotalValue": ParagraphStyle(
                "TotalValue",
                parent=base["Normal"],
                fontSize=9,
                fontName="Helvetica-Bold",
                alignment=TA_RIGHT,
            ),
            "TotalGrand": ParagraphStyle(
                "TotalGrand",
                parent=base["Normal"],
                fontSize=11,
                fontName="Helvetica-Bold",
                alignment=TA_RIGHT,
            ),
            "Footer": ParagraphStyle(
                "Footer",
                parent=base["Normal"],
                fontSize=7,
                alignment=TA_LEFT,
                leading=9,
                textColor=HexColor("#6b7280"),
            ),
            "FooterBold": ParagraphStyle(
                "FooterBold",
                parent=base["Normal"],
                fontSize=8,
                fontName="Helvetica-Bold",
                alignment=TA_RIGHT,
                leading=10,
            ),
        }

    # ── Top header (issuer + center letter + receipt id) ──────────

    def _build_main_header(self, data: dict, styles: dict) -> Table:
        """Single bordered frame matching the AFIP receipt header.

        Layout:

            ┌──────────────────────────────────────────────────────────┐
            │                        ORIGINAL                          │
            ├──────────────────────────┬───────────┬───────────────────┤
            │                          │  ┌─────┐  │                   │
            │  ISSUER NAME             │  │  C  │  │  FACTURA          │
            │                          │  │ 011 │  │                   │
            │  Razón Social: …         │  └──┬──┘  │  Pto Vta · Comp.. │
            │  Domicilio Comercial: …  │     │     │  Fecha de Emisión │
            │  Condición frente al IVA │     │     │  CUIT             │
            │                          │     │     │  Ingresos Brutos  │
            │                          │     │     │  Fecha de Inicio  │
            └──────────────────────────┴─────┴─────┴───────────────────┘

        The C-box is a complete bordered rectangle sitting flush against
        the top of the content row. A single hairline drops from the
        centre of the box's bottom edge down to the bottom of the header,
        forming the "Y trunk" that visually separates the issuer and
        receipt-id columns. There are no other vertical dividers in the
        content row — only the outer perimeter and that single trunk.
        """
        issuer = data.get("issuer", {})
        invoice = data.get("invoice", {})

        receipt_type = int(invoice.get("receipt_type", 0))
        letter = RECEIPT_LETTER_BY_CODE.get(receipt_type, "?")
        code = RECEIPT_CODE_BY_TYPE.get(receipt_type, str(receipt_type).zfill(3))
        name = RECEIPT_NAME_BY_TYPE.get(receipt_type, "COMPROBANTE")

        left_cell = self._build_left_header_cell(issuer, styles)
        c_column = self._build_letter_column(letter, code, styles)
        right_cell = self._build_right_header_cell(invoice, issuer, name, styles)

        outer = Table(
            [
                [Paragraph("ORIGINAL", styles["Original"]), "", ""],
                [left_cell, c_column, right_cell],
            ],
            colWidths=[91 * mm, 18 * mm, 91 * mm],
            rowHeights=[None, self.HEADER_CONTENT_HEIGHT_MM * mm],
        )
        outer.setStyle(
            TableStyle(
                [
                    # ORIGINAL bar: full-width banner with hairline below.
                    ("SPAN", (0, 0), (-1, 0)),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.4, BORDER),
                    ("TOPPADDING", (0, 0), (-1, 0), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                    # Content row: top-aligned. No internal vertical
                    # dividers — the C-column draws its own box and trunk.
                    ("VALIGN", (0, 1), (-1, 1), "TOP"),
                    ("ALIGN", (1, 1), (1, 1), "CENTER"),
                    # Outer perimeter.
                    ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
                    # Padding for issuer / receipt-id columns; zero for
                    # the C-column so its inner box+trunk hug the edges.
                    ("LEFTPADDING", (0, 1), (0, 1), 6),
                    ("RIGHTPADDING", (0, 1), (0, 1), 6),
                    ("TOPPADDING", (0, 1), (0, 1), 6),
                    ("BOTTOMPADDING", (0, 1), (0, 1), 6),
                    ("LEFTPADDING", (1, 1), (1, 1), 0),
                    ("RIGHTPADDING", (1, 1), (1, 1), 0),
                    ("TOPPADDING", (1, 1), (1, 1), 0),
                    ("BOTTOMPADDING", (1, 1), (1, 1), 0),
                    ("LEFTPADDING", (2, 1), (2, 1), 6),
                    ("RIGHTPADDING", (2, 1), (2, 1), 6),
                    ("TOPPADDING", (2, 1), (2, 1), 6),
                    ("BOTTOMPADDING", (2, 1), (2, 1), 6),
                ]
            )
        )
        return outer

    def _build_left_header_cell(self, issuer: dict, styles: dict) -> list:
        logo_flowable: list = []
        logo_path = issuer.get("logo_path")
        if logo_path and Path(str(logo_path)).exists():
            try:
                logo_flowable = [
                    Image(str(logo_path), width=30 * mm, height=12 * mm, kind="proportional"),
                    Spacer(1, 2 * mm),
                ]
            except Exception:  # noqa: BLE001 — a bad logo file shouldn't break the PDF
                logo_flowable = []

        return [
            *logo_flowable,
            Paragraph(issuer.get("legal_name", ""), styles["IssuerName"]),
            Spacer(1, 4 * mm),
            self._labeled("Razón Social: ", issuer.get("legal_name", ""), styles),
            self._labeled("Domicilio Comercial: ", issuer.get("address", ""), styles),
            self._labeled(
                "Condición frente al IVA: ",
                issuer.get("iva_condition_label", ""),
                styles,
            ),
        ]

    def _build_letter_column(self, letter: str, code: str, styles: dict) -> Table:
        """Vertical Y-shape: a complete bordered C-box on top, then a
        single hairline dropping from its bottom-centre to the foot of
        the header content row.

        ::

            ┌────────┐   <- box: 4 borders (BOX), 16mm tall
            │   C    │
            ├────────┤   <- inner divider between letter and "COD. xxx"
            │COD. 011│
            └───┬────┘
                │        <- single centred hairline (the trunk)
                │
        """
        # The box itself: 1 column × 2 rows with all four borders.
        letter_box = Table(
            [
                [Paragraph(letter, styles["BigLetter"])],
                [Paragraph(f"COD. {code}", styles["ReceiptCode"])],
            ],
            colWidths=[18 * mm],
            rowHeights=[12 * mm, 4 * mm],
        )
        letter_box.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.4, BORDER),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        # The trunk: a 2-column row whose internal LINEAFTER on column 0
        # gives a single hairline exactly at the horizontal centre of
        # the 18mm column. Its height fills the gap between the bottom
        # of the C-box and the bottom of the header content row.
        trunk_height = max(self.HEADER_CONTENT_HEIGHT_MM - self.LETTER_BOX_HEIGHT_MM, 1)
        trunk = Table(
            [["", ""]],
            colWidths=[9 * mm, 9 * mm],
            rowHeights=[trunk_height * mm],
        )
        trunk.setStyle(
            TableStyle(
                [
                    ("LINEAFTER", (0, 0), (0, 0), 0.4, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        # Wrap the box and the trunk into a single flowable so the cell
        # in the outer table receives just one element.
        wrapper = Table(
            [[letter_box], [trunk]],
            colWidths=[18 * mm],
            rowHeights=[self.LETTER_BOX_HEIGHT_MM * mm, trunk_height * mm],
        )
        wrapper.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return wrapper

    def _build_right_header_cell(
        self, invoice: dict, issuer: dict, receipt_name: str, styles: dict
    ) -> list:
        pos = int(invoice.get("point_of_sale", 0))
        nro = int(invoice.get("receipt_number", 0))
        pos_comp = Paragraph(
            f"<b>Punto de Venta:</b> {str(pos).zfill(5)}"
            f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Comp. Nro:</b> {str(nro).zfill(8)}",
            styles["Value"],
        )
        return [
            Paragraph(receipt_name, styles["ReceiptName"]),
            Spacer(1, 3 * mm),
            pos_comp,
            self._labeled(
                "Fecha de Emisión: ",
                _fmt_date(invoice.get("issue_date")),
                styles,
            ),
            Spacer(1, 1.5 * mm),
            self._labeled("CUIT: ", issuer.get("cuit", ""), styles),
            self._labeled("Ingresos Brutos: ", issuer.get("gross_income", ""), styles),
            self._labeled(
                "Fecha de Inicio de Actividades: ",
                _fmt_date(issuer.get("activity_start_date")),
                styles,
            ),
        ]

    # ── Period + customer block ──────────────────────────────────

    def _build_period_and_customer(self, data: dict, styles: dict) -> Table:
        invoice = data.get("invoice", {})
        customer = data.get("customer", {})

        period_row = [
            Paragraph(
                f"<b>Período Facturado Desde:</b> {_fmt_date(invoice.get('period_from'))}",
                styles["Value"],
            ),
            Paragraph(
                f"<b>Hasta:</b> {_fmt_date(invoice.get('period_to'))}",
                styles["Value"],
            ),
            Paragraph(
                f"<b>Fecha de Vto. para el pago:</b> {_fmt_date(invoice.get('due_date'))}",
                styles["Value"],
            ),
        ]

        customer_left = [
            self._labeled(
                f"{customer.get('doc_label', 'CUIT')}: ",
                customer.get("doc_number", ""),
                styles,
            ),
            self._labeled(
                "Condición frente al IVA: ",
                customer.get("iva_condition_label", ""),
                styles,
            ),
        ]
        customer_right = [
            self._labeled(
                "Apellido y Nombre / Razón Social: ",
                customer.get("legal_name", ""),
                styles,
            ),
            self._labeled("Domicilio: ", customer.get("address", ""), styles),
            self._labeled(
                "Condición de venta: ",
                invoice.get("condition_of_sale", "Otra"),
                styles,
            ),
        ]

        outer = Table(
            [period_row, [customer_left, "", customer_right]],
            colWidths=[70 * mm, 60 * mm, 70 * mm],
        )
        outer.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("SPAN", (1, 1), (1, 1)),  # placeholder
                    ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.4, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        return outer

    # ── Items table ──────────────────────────────────────────────

    def _build_items_table(self, data: dict, styles: dict) -> Table:
        items = data.get("items", [])

        header = [
            Paragraph("Código", styles["TableHeader"]),
            Paragraph("Producto / Servicio", styles["TableHeader"]),
            Paragraph("Cantidad", styles["TableHeader"]),
            Paragraph("U. Medida", styles["TableHeader"]),
            Paragraph("Precio Unit.", styles["TableHeader"]),
            Paragraph("% Bonif.", styles["TableHeader"]),
            Paragraph("Imp. Bonif.", styles["TableHeader"]),
            Paragraph("Subtotal", styles["TableHeader"]),
        ]
        rows: list[list] = [header]

        for item in items:
            rows.append(
                [
                    Paragraph(str(item.get("code", "")), styles["TableCell"]),
                    Paragraph(str(item.get("name", "")), styles["TableCell"]),
                    Paragraph(_fmt_decimal(item.get("quantity", 1), 2), styles["TableCellRight"]),
                    Paragraph(str(item.get("unit", "unidades")), styles["TableCell"]),
                    Paragraph(_fmt_money(item.get("unit_price", 0)), styles["TableCellRight"]),
                    Paragraph(
                        _fmt_decimal(item.get("discount_pct", 0), 2), styles["TableCellRight"]
                    ),
                    Paragraph(_fmt_money(item.get("discount_amount", 0)), styles["TableCellRight"]),
                    Paragraph(_fmt_money(item.get("subtotal", 0)), styles["TableCellRight"]),
                ]
            )

        col_widths = [
            14 * mm,
            60 * mm,
            18 * mm,
            18 * mm,
            24 * mm,
            14 * mm,
            20 * mm,
            32 * mm,
        ]
        table = Table(rows, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.4, BORDER),
                    ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    # ── Totals (right-aligned) ───────────────────────────────────

    def _build_totals(self, data: dict, styles: dict) -> Table:
        totals = data.get("totals", {})
        rows = [
            [
                Paragraph("Subtotal: $", styles["TotalLabel"]),
                Paragraph(_fmt_money(totals.get("subtotal", 0)), styles["TotalValue"]),
            ],
            [
                Paragraph("Importe Otros Tributos: $", styles["TotalLabel"]),
                Paragraph(_fmt_money(totals.get("other_taxes", 0)), styles["TotalValue"]),
            ],
            [
                Paragraph("Importe Total: $", styles["TotalLabel"]),
                Paragraph(_fmt_money(totals.get("total", 0)), styles["TotalGrand"]),
            ],
        ]
        # Right-aligned by allocating space on the left.
        table = Table(rows, colWidths=[160 * mm, 40 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        return table

    # ── Footer (QR + CAE + page) ─────────────────────────────────

    def _build_footer(self, data: dict, styles: dict) -> Table:
        afip = data.get("afip", {})

        qr_cell: list = []
        qr_bytes = afip.get("qr_png_bytes")
        if qr_bytes:
            qr_cell.append(
                Image(BytesIO(qr_bytes), width=28 * mm, height=28 * mm, kind="proportional")
            )

        center_cell = [
            Paragraph("ARCA", styles["IssuerName"]),
            Paragraph("Comprobante Autorizado", styles["Label"]),
            Paragraph(
                "Esta Administración Federal no se responsabiliza por los datos "
                "ingresados en el detalle de la operación.",
                styles["Footer"],
            ),
        ]
        right_cell = [
            Paragraph(f"Pág. {afip.get('page_label', '1/1')}", styles["FooterBold"]),
            Paragraph(f"CAE Nº: {afip.get('cae', '')}", styles["FooterBold"]),
            Paragraph(
                f"Fecha de Vto. de CAE: {_fmt_date(afip.get('cae_expiration'))}",
                styles["FooterBold"],
            ),
        ]
        return Table(
            [[qr_cell, center_cell, right_cell]],
            colWidths=[40 * mm, 90 * mm, 70 * mm],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            ),
        )

    # ── Helpers ──────────────────────────────────────────────────

    def _labeled(self, label: str, value: str, styles: dict) -> Paragraph:
        return Paragraph(f"<b>{label}</b>{value}", styles["Value"])


# --- Format helpers -------------------------------------------------------


def _fmt_date(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, str):
        # Accept ISO dates or pre-formatted strings.
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.strftime("%d/%m/%Y")
        except ValueError:
            return value
    return str(value)


def _fmt_money(value: Any) -> str:
    if value is None:
        return "0.00"
    decimal_value = _coerce_decimal(value)
    return f"{decimal_value:,.2f}"


def _fmt_decimal(value: Any, places: int = 2) -> str:
    decimal_value = _coerce_decimal(value)
    return f"{decimal_value:.{places}f}"


def _coerce_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int | float):
        return Decimal(str(value))
    if isinstance(value, str):
        try:
            return Decimal(value)
        except Exception:  # noqa: BLE001
            return Decimal("0")
    return Decimal("0")
