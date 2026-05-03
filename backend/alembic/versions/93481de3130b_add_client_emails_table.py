"""add client_emails table

Revision ID: 93481de3130b
Revises: d5f0bb953fbe
Create Date: 2026-05-02 12:50:40.555194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93481de3130b'
down_revision = 'd5f0bb953fbe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'client_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_client_emails_id'),
        'client_emails',
        ['id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_client_emails_client_id'),
        'client_emails',
        ['client_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_client_emails_client_id'), table_name='client_emails')
    op.drop_index(op.f('ix_client_emails_id'), table_name='client_emails')
    op.drop_table('client_emails')
