"""
Email Template repository and CRUD operations.
"""
import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.shared.email.models import EmailTemplate
from app.shared.email.schemas import EmailTemplateCreate, EmailTemplateUpdate

logger = logging.getLogger(__name__)


class EmailTemplateRepository:
    """Repository for Email Template CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_default(self) -> EmailTemplate | None:
        """Get the default email template."""
        try:
            return self.db.query(EmailTemplate).filter(EmailTemplate.is_default == True).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching default email template: {e}")
            return None

    def get_by_id(self, template_id: int) -> EmailTemplate | None:
        """Get an email template by ID."""
        try:
            return self.db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching email template {template_id}: {e}")
            return None

    def list_all(self) -> list[EmailTemplate]:
        """List all email templates."""
        try:
            return self.db.query(EmailTemplate).order_by(EmailTemplate.name).all()
        except SQLAlchemyError as e:
            logger.error(f"Error listing email templates: {e}")
            return []

    def create(self, template_data: EmailTemplateCreate) -> EmailTemplate:
        """Create a new email template."""
        try:
            if template_data.is_default:
                self.db.query(EmailTemplate).update({EmailTemplate.is_default: False})

            db_template = EmailTemplate(**template_data.model_dump())
            self.db.add(db_template)
            self.db.commit()
            self.db.refresh(db_template)
            return db_template
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating email template: {e}")
            raise

    def update(self, template_id: int, update_data: EmailTemplateUpdate) -> EmailTemplate | None:
        """Update an existing email template."""
        try:
            db_template = self.get_by_id(template_id)
            if not db_template:
                return None

            update_dict = update_data.model_dump(exclude_unset=True)

            if update_dict.get("is_default", False):
                self.db.query(EmailTemplate).filter(
                    EmailTemplate.id != template_id,
                    EmailTemplate.is_default == True,
                ).update({EmailTemplate.is_default: False})

            for key, value in update_dict.items():
                setattr(db_template, key, value)

            self.db.commit()
            self.db.refresh(db_template)
            return db_template
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating email template {template_id}: {e}")
            raise

    def delete(self, template_id: int) -> bool:
        """Delete an email template."""
        try:
            db_template = self.get_by_id(template_id)
            if not db_template:
                return False

            self.db.delete(db_template)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting email template {template_id}: {e}")
            return False
