"""add description to snippets

Revision ID: 3c1a9f2e8b47
Revises: 8754a677eb36
Create Date: 2026-05-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c1a9f2e8b47'
down_revision: Union[str, Sequence[str], None] = '8754a677eb36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('snippets', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('snippets', 'description')
