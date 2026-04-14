"""
PDF Template repository and CRUD operations.
"""
import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.shared.pdf.messages import LOG_MESSAGES, PDF_TEMPLATE_DEFAULTS
from app.shared.pdf.models import PdfTemplate
from app.shared.pdf.schemas import PdfTemplateCreate, PdfTemplateUpdate

logger = logging.getLogger(__name__)


class PdfTemplateRepository:
    """Repository for PDF template CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_default(self) -> PdfTemplate | None:
        """Get the default PDF template."""
        try:
            return self.db.query(PdfTemplate).filter(PdfTemplate.is_default.is_(True)).first()
        except SQLAlchemyError as e:
            logger.error(LOG_MESSAGES["template_fetch_error"].format(error=str(e)))
            return None

    def get_by_id(self, template_id: int) -> PdfTemplate | None:
        """Get a PDF template by ID."""
        try:
            return self.db.query(PdfTemplate).filter(PdfTemplate.id == template_id).first()
        except SQLAlchemyError as e:
            logger.error(LOG_MESSAGES["template_fetch_error"].format(error=str(e)))
            return None

    def create(self, template_data: PdfTemplateCreate) -> PdfTemplate:
        """Create a new PDF template."""
        try:
            # If is_default is True, unset all other defaults
            if template_data.is_default:
                self.db.query(PdfTemplate).update({PdfTemplate.is_default: False})

            db_template = PdfTemplate(**template_data.model_dump())
            self.db.add(db_template)
            self.db.commit()
            self.db.refresh(db_template)
            logger.info(LOG_MESSAGES["template_created"].format(id=db_template.id))
            return db_template
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(LOG_MESSAGES["template_create_error"].format(error=str(e)))
            raise

    def update(self, template_id: int, update_data: PdfTemplateUpdate) -> PdfTemplate | None:
        """Update an existing PDF template."""
        try:
            db_template = self.get_by_id(template_id)
            if not db_template:
                return None

            update_dict = update_data.model_dump(exclude_unset=True)

            # If setting as default, unset others first
            if update_dict.get("is_default", False):
                self.db.query(PdfTemplate).filter(
                    PdfTemplate.id != template_id,
                    PdfTemplate.is_default.is_(True),
                ).update({PdfTemplate.is_default: False})

            for key, value in update_dict.items():
                setattr(db_template, key, value)

            self.db.commit()
            self.db.refresh(db_template)
            logger.info(LOG_MESSAGES["template_updated"].format(id=template_id))
            return db_template
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(LOG_MESSAGES["template_update_error"].format(id=template_id, error=str(e)))
            raise

    def delete(self, template_id: int) -> bool:
        """Delete a PDF template."""
        try:
            db_template = self.get_by_id(template_id)
            if not db_template:
                return False

            self.db.delete(db_template)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(LOG_MESSAGES["template_delete_error"].format(id=template_id, error=str(e)))
            return False

    def reset_to_defaults(self) -> PdfTemplate:
        """Reset or create default template with standard values."""
        try:
            default_template = self.get_default()
            if default_template:
                # Update existing default
                for key, value in PDF_TEMPLATE_DEFAULTS.items():
                    setattr(default_template, key, value)
                self.db.commit()
                self.db.refresh(default_template)
                logger.info(LOG_MESSAGES["template_reset"])
                return default_template
            else:
                # Create new default
                new_template = PdfTemplate(
                    **PDF_TEMPLATE_DEFAULTS,
                    is_default=True,
                )
                self.db.add(new_template)
                self.db.commit()
                self.db.refresh(new_template)
                logger.info(LOG_MESSAGES["template_reset"])
                return new_template
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(LOG_MESSAGES["template_reset_error"].format(error=str(e)))
            raise
