"""
Proposal-specific PDF renderer using reportlab.
"""
from datetime import datetime
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from app.shared.pdf.renderers.base import PdfRenderer
from app.shared.pdf.template import PdfTemplate


class ProposalPdfRenderer(PdfRenderer):
    """Renders proposal data into PDF using reportlab platypus."""

    def render(self, data: dict, template: PdfTemplate) -> list:
        """
        Render proposal as reportlab flowable list.

        Args:
            data: {proposal, client, tasks, totals}
            template: PDF template configuration

        Returns:
            List of reportlab flowables (story)
        """
        proposal = data["proposal"]
        client = data.get("client")
        tasks = data.get("tasks", [])

        styles = self._build_styles(template)
        story: list = []

        # Header
        story.extend(self._build_header(proposal, styles, template))
        story.append(Spacer(1, 12 * mm))

        # Proposal info
        story.append(self._build_proposal_info(proposal, client, styles, template))
        story.append(Spacer(1, 8 * mm))

        # Tasks table
        if tasks:
            story.append(self._build_tasks_table(tasks, styles, template))
            story.append(Spacer(1, 8 * mm))

        # Totals
        totals = data.get("totals", {})
        if totals:
            story.append(self._build_totals(totals, styles, template))

        # Footer
        if template.footer_text:
            story.append(Spacer(1, 12 * mm))
            story.append(Paragraph(template.footer_text, styles["Footer"]))

        return story

    def _build_styles(self, template: PdfTemplate):
        """Build ParagraphStyle objects from template colors."""
        base_styles = getSampleStyleSheet()

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=base_styles["Heading1"],
            fontSize=24,
            textColor=HexColor(template.accent_color),
            spaceAfter=6 * mm,
            alignment=TA_LEFT,
        )

        label_style = ParagraphStyle(
            "CustomLabel",
            parent=base_styles["Normal"],
            fontSize=8,
            textColor=HexColor(template.accent_color),
            fontName="Helvetica-Bold",
            spaceAfter=1 * mm,
            textTransform="uppercase",
        )

        value_style = ParagraphStyle(
            "CustomValue",
            parent=base_styles["Normal"],
            fontSize=11,
            textColor=HexColor(template.text_color),
            spaceAfter=4 * mm,
        )

        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=base_styles["Normal"],
            fontSize=10,
            textColor=white,
            fontName="Helvetica-Bold",
        )

        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=base_styles["Normal"],
            fontSize=9,
            textColor=HexColor(template.text_color),
        )

        total_label_style = ParagraphStyle(
            "TotalLabel",
            parent=base_styles["Normal"],
            fontSize=10,
            textColor=HexColor(template.text_color),
        )

        total_value_style = ParagraphStyle(
            "TotalValue",
            parent=base_styles["Normal"],
            fontSize=10,
            textColor=HexColor(template.text_color),
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT,
        )

        grand_total_style = ParagraphStyle(
            "GrandTotal",
            parent=base_styles["Heading2"],
            fontSize=14,
            textColor=HexColor(template.accent_color),
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT,
        )

        footer_style = ParagraphStyle(
            "CustomFooter",
            parent=base_styles["Normal"],
            fontSize=8,
            textColor=HexColor("#6b7280"),
            alignment=TA_LEFT,
        )

        return {
            "Heading": heading_style,
            "Label": label_style,
            "Value": value_style,
            "TableHeader": table_header_style,
            "TableCell": table_cell_style,
            "TotalLabel": total_label_style,
            "TotalValue": total_value_style,
            "GrandTotal": grand_total_style,
            "Footer": footer_style,
        }

    def _build_header(self, proposal: dict, styles, template: PdfTemplate):
        """Build header section with optional logo."""
        story = []

        # Add logo if available
        if template.logo_url:
            # Resolve logo path: "/uploads/logos/xxx.png" -> backend/uploads/logos/xxx.png
            logo_rel = template.logo_url.lstrip("/")
            # proposal.py is at: backend/app/shared/pdf/renderers/proposal.py
            # Need to go up 5 levels to reach backend/
            backend_root = Path(__file__).parent.parent.parent.parent.parent
            logo_path = backend_root / logo_rel

            if logo_path.exists():
                from reportlab.platypus import Image

                logo_img = Image(str(logo_path), width=40 * mm, height=20 * mm, kind="proportional")
                story.append(logo_img)
                story.append(Spacer(1, 4 * mm))

        story.append(Paragraph("Presupuesto", styles["Heading"]))
        return story

    def _build_proposal_info(
        self, proposal: dict, client: dict | None, styles, template: PdfTemplate
    ):
        """Build proposal info grid."""
        created_at = proposal.get("created_at", "")
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                created_at = dt.strftime("%d/%m/%Y")
            except (ValueError, AttributeError):
                pass

        info_data = [
            [Paragraph("Nombre", styles["Label"]), Paragraph("Fecha de Emisión", styles["Label"])],
            [
                Paragraph(proposal.get("name", "N/A"), styles["Value"]),
                Paragraph(created_at, styles["Value"]),
            ],
        ]

        if client:
            info_data.append(
                [
                    Paragraph("Cliente", styles["Label"]),
                    Paragraph("Empresa", styles["Label"]),
                ]
            )
            info_data.append(
                [
                    Paragraph(client.get("name", "N/A"), styles["Value"]),
                    Paragraph(client.get("company") or "—", styles["Value"]),
                ]
            )

        info_table = Table(info_data, colWidths=[80 * mm, 80 * mm])
        info_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        return info_table

    def _build_tasks_table(self, tasks: list[dict], styles, template: PdfTemplate):
        """Build tasks table."""
        header_style = styles["TableHeader"]
        cell_style = styles["TableCell"]
        accent = HexColor(template.accent_color)

        # Headers
        headers = [
            Paragraph("Tarea", header_style),
            Paragraph("Descripción", header_style),
            Paragraph("Horas", header_style),
        ]

        # Data rows
        rows = [headers]
        for task in tasks:
            description = task.get("description", "") or "—"
            rows.append(
                [
                    Paragraph(task.get("name", "N/A"), cell_style),
                    Paragraph(description, cell_style),
                    Paragraph(f'{task.get("hours", 0):.2f} hs', cell_style),
                ]
            )

        table = Table(rows, colWidths=[50 * mm, 90 * mm, 40 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), accent),
                    ("TEXTCOLOR", (0, 0), (-1, 0), white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e5e7eb")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#f9fafb")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return table

    def _build_totals(self, totals: dict, styles, template: PdfTemplate):
        """Build totals section."""
        data = []
        items = list(totals.items())

        for i, (label, value) in enumerate(items):
            style = styles["TotalLabel"]
            value_style = styles["TotalValue"]

            if i == len(items) - 1:
                style = ParagraphStyle(
                    "GrandTotalLabel",
                    parent=styles["GrandTotal"],
                    alignment=TA_LEFT,
                )
                value_style = styles["GrandTotal"]

            data.append(
                [
                    Paragraph(str(label), style),
                    Paragraph(str(value), value_style),
                ]
            )

        totals_table = Table(data, colWidths=[90 * mm, 90 * mm])
        totals_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.5, HexColor("#e5e7eb")),
                    ("BACKGROUND", (0, 0), (-1, -1), HexColor("#f3f4f6")),
                    ("BOX", (0, 0), (-1, -1), 1, HexColor(template.accent_color)),
                ]
            )
        )
        return totals_table
