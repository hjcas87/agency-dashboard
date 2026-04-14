"""
Base PDF renderer interface.
"""
from abc import ABC, abstractmethod

from app.shared.pdf.template import PdfTemplate


class PdfRenderer(ABC):
    """Interface for document-specific PDF renderers."""

    @abstractmethod
    def render(self, data: dict, template: PdfTemplate) -> str:
        """
        Render HTML string ready for PDF conversion.

        Args:
            data: Document-specific data (varies by renderer)
            template: PDF template with styling configuration

        Returns:
            HTML string ready for WeasyPrint conversion
        """
        pass
