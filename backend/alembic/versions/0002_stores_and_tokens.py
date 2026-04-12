"""add stores and tiendanube tokens tables

Revision ID: 0002_stores_and_tokens
Revises: 0001_initial
Create Date: 2025-04-11 00:00:00.000000

Adds tables for managing Tiendanube store connections:
- stores: connected Tiendanube stores with status tracking
- tiendanube_tokens: encrypted OAuth token storage
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_stores_and_tokens'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create stores and tiendanube_tokens tables."""
    # stores table
    op.create_table(
        'stores',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('tiendanube_store_id', sa.String(50), nullable=False),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('currency', sa.String(10), nullable=True, server_default='ARS'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_stores_id'), 'stores', ['id'], unique=False)
    op.create_index(op.f('ix_stores_tiendanube_store_id'), 'stores', ['tiendanube_store_id'], unique=True)
    op.create_unique_constraint('uq_store_tiendanube_id', 'stores', ['tiendanube_store_id'])

    # tiendanube_tokens table
    op.create_table(
        'tiendanube_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('store_id', sa.Integer(), nullable=False),
        sa.Column('encrypted_access_token', sa.Text(), nullable=False),
        sa.Column('token_type', sa.String(50), nullable=False, server_default='bearer'),
        sa.Column('scope', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_tiendanube_tokens_id'), 'tiendanube_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_tiendanube_tokens_store_id'), 'tiendanube_tokens', ['store_id'], unique=True)


def downgrade() -> None:
    """Drop stores and tiendanube_tokens tables."""
    op.drop_table('tiendanube_tokens')
    op.drop_table('stores')
