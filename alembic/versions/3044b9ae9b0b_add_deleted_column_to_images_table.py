"""Add deleted column to images table

Revision ID: 3044b9ae9b0b
Revises: d4f9747da532
Create Date: 2024-02-12 16:53:36.112449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3044b9ae9b0b'
down_revision: Union[str, None] = 'd4f9747da532'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('images', sa.Column('deleted', sa.Boolean(), server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('images', 'deleted')
