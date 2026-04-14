"""
PDF generator — reusable class that delegates to specific renderers.

Uses reportlab (pure Python, no system dependencies required).
"""
import logging
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
)

from app.shared.pdf.renderers.base import PdfRenderer
from app.shared.pdf.template import PdfTemplate, PdfTemplateRepository

logger = logging.getLogger(__name__)


class PdfGenerator:
    """
    Reusable PDF generator. Not dependent on specific features.

    Uses reportlab — pure Python, no system libraries required.
    """

    def __init__(self, db, template: PdfTemplate | None = None):
        """
        Initialize PDF generator.

        Args:
            db: Database session
            template: PDF template configuration (loads default if not provided)
        """
        self.db = db
        self.template = template or self._load_default_template()
        self.renderer: PdfRenderer | None = None

    def set_renderer(self, renderer: PdfRenderer) -> None:
        """Set the document-specific renderer."""
        self.renderer = renderer

    def generate(self, data: dict) -> bytes:
        """
        Generate PDF bytes using the configured renderer.

        Args:
            data: Document-specific data dict

        Returns:
            PDF file as bytes

        Raises:
            ValueError: If renderer is not set
        """
        if not self.renderer:
            raise ValueError("Renderer not set. Call set_renderer() first.")

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=25 * mm,
            bottomMargin=25 * mm,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
        )

        story = self.renderer.render(data, self.template)
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def generate_proposal(self, proposal_data: dict) -> bytes:
        """
        Convenience method to generate a proposal PDF.

        Args:
            proposal_data: {proposal, client, tasks, totals}

        Returns:
            PDF file as bytes
        """
        from app.shared.pdf.renderers.proposal import ProposalPdfRenderer

        self.set_renderer(ProposalPdfRenderer())
        return self.generate(proposal_data)

    def _load_default_template(self) -> PdfTemplate:
        """Load default PDF template from database."""
        repo = PdfTemplateRepository(self.db)
        template = repo.get_default()
        if not template:
            template = repo.reset_to_defaults()
        return template
