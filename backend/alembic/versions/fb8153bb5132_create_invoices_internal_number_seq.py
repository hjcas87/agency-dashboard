"""create invoices_internal_number_seq

Revision ID: fb8153bb5132
Revises: 266abc62e3fa
Create Date: 2026-05-02 16:42:38.990262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb8153bb5132'
down_revision = '266abc62e3fa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS invoices_internal_number_seq")
    # Seed from current max so existing X numbers stay contiguous.
    op.execute(
        """
        SELECT setval(
            'invoices_internal_number_seq',
            COALESCE((SELECT MAX(internal_number) FROM invoices WHERE is_internal = true), 0) + 1,
            false
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP SEQUENCE IF EXISTS invoices_internal_number_seq")

