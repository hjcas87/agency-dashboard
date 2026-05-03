"""add code, issue_date, show_recipient_on_cover to proposals

Revision ID: f0d0280b9e3a
Revises: 60feadbb188c
Create Date: 2026-05-02 23:08:46.117946

"""
import secrets
import string

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0d0280b9e3a'
down_revision = '60feadbb188c'
branch_labels = None
depends_on = None


def _generate_code() -> str:
    """LLDDLL — mirrors app.custom.features.proposals.code_generator."""
    letters = string.ascii_uppercase
    digits = string.digits
    return (
        secrets.choice(letters)
        + secrets.choice(letters)
        + secrets.choice(digits)
        + secrets.choice(digits)
        + secrets.choice(letters)
        + secrets.choice(letters)
    )


def upgrade() -> None:
    # 1) Add columns. `code` is added nullable so existing rows can be
    #    backfilled before we promote it to NOT NULL.
    op.add_column('proposals', sa.Column('code', sa.String(length=8), nullable=True))
    op.add_column(
        'proposals',
        sa.Column(
            'issue_date',
            sa.Date(),
            server_default=sa.text('CURRENT_DATE'),
            nullable=False,
        ),
    )
    op.add_column(
        'proposals',
        sa.Column(
            'show_recipient_on_cover',
            sa.Boolean(),
            server_default='true',
            nullable=False,
        ),
    )

    # 2) Backfill issue_date from created_at::date for existing rows so
    #    pre-existing proposals show their actual creation day, not
    #    today's date.
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE proposals SET issue_date = created_at::date"))

    # 3) Backfill code with unique LLDDLL values. Retry on collision
    #    against codes already used in this batch.
    rows = conn.execute(sa.text("SELECT id FROM proposals ORDER BY id")).fetchall()
    used: set[str] = set()
    for (row_id,) in rows:
        for _ in range(32):
            candidate = _generate_code()
            if candidate not in used:
                used.add(candidate)
                conn.execute(
                    sa.text("UPDATE proposals SET code = :c WHERE id = :id"),
                    {"c": candidate, "id": row_id},
                )
                break
        else:
            raise RuntimeError(f"could not allocate a unique code for proposal {row_id}")

    # 4) Promote `code` to NOT NULL + unique index.
    op.alter_column('proposals', 'code', nullable=False)
    op.create_index(op.f('ix_proposals_code'), 'proposals', ['code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_proposals_code'), table_name='proposals')
    op.drop_column('proposals', 'show_recipient_on_cover')
    op.drop_column('proposals', 'issue_date')
    op.drop_column('proposals', 'code')
