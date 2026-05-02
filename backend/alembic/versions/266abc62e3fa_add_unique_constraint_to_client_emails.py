"""add unique constraint to client_emails

Revision ID: 266abc62e3fa
Revises: 9cd2ae5ea018
Create Date: 2026-05-02 16:42:19.586177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '266abc62e3fa'
down_revision = '9cd2ae5ea018'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove duplicate additional emails, keeping the oldest row per (client_id, email) pair.
    op.execute(
        """
        DELETE FROM client_emails
        WHERE id NOT IN (
            SELECT MIN(id) FROM client_emails GROUP BY client_id, email
        )
        """
    )
    op.create_unique_constraint(
        "uq_client_emails_client_email", "client_emails", ["client_id", "email"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_client_emails_client_email", "client_emails", type_="unique")

