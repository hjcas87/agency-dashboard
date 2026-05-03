"""add currency, estimated_days, deliverables_summary to proposals

Revision ID: 60feadbb188c
Revises: fb8153bb5132
Create Date: 2026-05-02 20:09:50.471980

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "60feadbb188c"
down_revision = "fb8153bb5132"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres `add_column` does not auto-create the named ENUM type
    # the way `create_table` does — explicit `.create()` is required
    # or the next ALTER fails with "type ... does not exist".
    proposalcurrency = sa.Enum("ARS", "USD", name="proposalcurrency")
    proposalcurrency.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "proposals",
        sa.Column(
            "currency",
            proposalcurrency,
            server_default="ARS",
            nullable=False,
        ),
    )
    op.add_column("proposals", sa.Column("estimated_days", sa.String(length=64), nullable=True))
    op.add_column("proposals", sa.Column("deliverables_summary", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("proposals", "deliverables_summary")
    op.drop_column("proposals", "estimated_days")
    op.drop_column("proposals", "currency")
    op.execute("DROP TYPE proposalcurrency")
