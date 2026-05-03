"""add invoices table

Revision ID: bb2101802a31
Revises: 601e661d3a6f
Create Date: 2026-05-02 00:48:18.146225

NOTE: This migration was originally committed empty (`pass`) because
autogen ran against a dev DB where `Base.metadata.create_all()` had
already created the `invoices` table. The bug only surfaced in prod,
where there's no `create_all()` shortcut, and the next migration in
the chain (`03f232cb12c4`) crashed trying to ALTER a non-existent
table. Re-populated against the model as it stood at the migration's
original commit (9d46a31) so subsequent column-adding migrations
keep applying cleanly on top.
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "bb2101802a31"
down_revision = "601e661d3a6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("proposal_id", sa.Integer(), nullable=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("afip_invoice_log_id", sa.Integer(), nullable=False),
        sa.Column("receipt_type", sa.Integer(), nullable=False),
        sa.Column("concept", sa.Integer(), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("service_date_from", sa.Date(), nullable=True),
        sa.Column("service_date_to", sa.Date(), nullable=True),
        sa.Column("total_amount_ars", sa.Numeric(precision=13, scale=2), nullable=False),
        sa.Column("document_type", sa.Integer(), nullable=False),
        sa.Column("document_number", sa.Integer(), nullable=False),
        sa.Column(
            "line_items",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("commercial_reference", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["afip_invoice_log_id"], ["afip_invoice_log.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["proposal_id"], ["proposals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invoices_id"), "invoices", ["id"], unique=False)
    op.create_index(op.f("ix_invoices_proposal_id"), "invoices", ["proposal_id"], unique=False)
    op.create_index(op.f("ix_invoices_client_id"), "invoices", ["client_id"], unique=False)
    op.create_index(
        op.f("ix_invoices_afip_invoice_log_id"),
        "invoices",
        ["afip_invoice_log_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_invoices_afip_invoice_log_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_client_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_proposal_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_id"), table_name="invoices")
    op.drop_table("invoices")
